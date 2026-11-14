# ══════════════════════════════════════════════════════════════════════════════
#  SmartRefresh_ExecuteRefresh · CELLULE 5 / 5 · Analyse + refresh + clôture [Python]
# ──────────────────────────────────────────────────────────────────────────────
#  RÔLE       Pour CHAQUE table de FACT_TABLES :
#               A. lire sa politique d'incremental refresh (IR) dans le modèle ;
#               B. trier ses mois modifiés : fenêtre IR (phase 1) ou historique
#                  (phase 2). Une table SANS politique est rechargée entière.
#             Puis, toutes tables ensemble :
#               C. PHASE 1 : tables de faits avec politique + dimensions modifiées
#               D. PHASE 2 : partitions historiques touchées (un seul appel)
#               E. CLÔTURE : marque-page à T1 des seuls objets traités + journal
#  À ADAPTER  (rarement) wait_if_refresh_running : temps d'attente maximum
#                        rolling_needed            : au JOUR si politique IR au jour
#                        resolve_partition         : si partitions renommées
#  NE PAS     changer apply_refresh_policy (True en phase 1, False en phase 2).
# ══════════════════════════════════════════════════════════════════════════════
import time
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from sempy.fabric.semantic_model import refresh_semantic_model, list_refresh_requests


# ── Fonctions ─────────────────────────────────────────────────────────────────

def finish_run(status, phase1_tables, phase2_labels, done_facts):
    """Clôture d'un passage réussi (SUCCEEDED ou NO_CHANGE).
    - Marque-page avancé à T1 UNIQUEMENT pour les objets traités : tables
      rechargées en phase 1 + tables de faits dont tous les mois historiques
      sont passés en phase 2 (ou ignorés car hors période stockée).
      Un objet non traité garde son marque-page : il sera revérifié.
    - La ligne du passage est complétée dans le journal dbo.SmartRefreshRun."""
    refreshed = sorted(set(phase1_tables) | set(done_facts))

    if refreshed:
        names = ", ".join(f"'{q(t)}'" for t in refreshed)
        run_sql(f"""
            UPDATE dbo.SmartRefreshObjectWatermark
            SET WatermarkUtc = CAST('{T1}' AS DATETIME2(6))
            WHERE ModelKey = '{MODEL_KEY}' AND ObjectName IN ({names});
        """)

    periods = ", ".join(f"{p['table']} {int(p['year'])}.{int(p['month']):02d}" for p in CHANGED_PERIODS)
    run_sql(f"""
        UPDATE dbo.SmartRefreshRun
        SET Status = '{status}',
            ChangedPeriods = '{q(periods)}',
            ChangedDims = '{q(", ".join(CHANGED_DIMS))}',
            Phase1Tables = '{q(", ".join(phase1_tables))}',
            Phase2Partitions = '{q(", ".join(phase2_labels))}',
            EndedUtc = SYSUTCDATETIME(),
            DurationS = DATEDIFF(SECOND, StartedUtc, SYSUTCDATETIME())
        WHERE RunId = {RUN_ID};
    """)
    print(f"Passage n°{RUN_ID} -> {status} | marque-page T1={T1} pour : {refreshed or 'aucun objet'}")


def wait_if_refresh_running(max_wait_s=900, step_s=30):   # ◄ À ADAPTER : attente max / pas (s)
    """Un modèle n'accepte qu'un refresh à la fois : on attend la fin
    d'un refresh déjà en cours avant de lancer le nôtre."""
    waited = 0
    while True:
        last = list_refresh_requests(dataset=SEMANTIC_MODEL_ID, workspace=WORKSPACE_ID, top_n=1)
        status_cols = [c for c in last.columns if "status" in c.lower()]
        running = (
            not last.empty
            and any(str(last.iloc[0][c]) in ("Unknown", "NotStarted", "InProgress") for c in status_cols)
        )
        if not running:
            return
        if waited >= max_wait_s:
            raise RuntimeError("Un refresh est toujours en cours sur le modèle.")
        print(f"Refresh en cours, attente {step_s} s…")
        time.sleep(step_s)
        waited += step_s


def read_policies():
    """Politique IR de chaque table de faits, lue directement dans le modèle (TOM).
    Renvoie {table: (granularité, nb_périodes)}, ou {table: None} sans politique.
    Une politique modifiée dans Power BI Desktop est prise en compte toute seule."""
    server = fabric.create_tom_server(readonly=True, workspace=WORKSPACE_ID)
    name = fabric.resolve_dataset_name(SEMANTIC_MODEL_ID, workspace=WORKSPACE_ID)
    model = server.Databases.GetByName(name).Model
    policies = {}
    for t in FACT_TABLES:
        if model.Tables.Find(t) is None:
            raise RuntimeError(f"Table de faits {t} absente du modèle sémantique.")
        pol = model.Tables[t].RefreshPolicy
        policies[t] = None if pol is None else (str(pol.IncrementalGranularity), int(pol.IncrementalPeriods))
    return policies


def months_covered_by_ir(t1_dt, granularity, n):
    """Ensemble des (année, mois) rafraîchis par la politique à la date T1."""
    d = t1_dt.date()
    if granularity == "Day":
        start = d - timedelta(days=n - 1)
    elif granularity == "Month":
        start = d.replace(day=1) - relativedelta(months=n - 1)
    elif granularity == "Quarter":
        start = date(d.year, 3 * ((d.month - 1) // 3) + 1, 1) - relativedelta(months=3 * (n - 1))
    else:  # Year
        start = date(d.year - n + 1, 1, 1)
    covered, cur = set(), start.replace(day=1)
    while cur <= d:
        covered.add((cur.year, cur.month))
        cur += relativedelta(months=1)
    return covered


def resolve_partition(year, month, existing_names):
    """Partition qui contient un mois, d'après les noms natifs Power BI :
    mois « 2025Q103 », sinon trimestre « 2025Q1 », sinon année « 2025 ».
    ◄ À ADAPTER uniquement si vos partitions ont été renommées."""
    q_ = (month - 1) // 3 + 1
    for candidate in (f"{year}Q{q_}{month:02d}", f"{year}Q{q_}", f"{year}"):
        if candidate in existing_names:
            return candidate
    return None


# ── Traitement ────────────────────────────────────────────────────────────────
start = time.time()
try:
    t1_dt = datetime.fromisoformat(T1)

    # ── A-B. Analyse, table de faits par table de faits ──────────────────────
    policies = read_policies()
    phase1_facts = []      # tables de faits à recharger en phase 1
    historical = {}        # {table: [(année, mois), ...]} pour la phase 2

    for t in FACT_TABLES:
        months = sorted({(int(p["year"]), int(p["month"])) for p in CHANGED_PERIODS if p["table"] == t})
        pol = policies[t]

        if pol is None:
            # Table de faits sans politique : rechargée entière si elle a changé
            print(f"{t} : pas de politique IR | mois modifiés : {months}")
            if months:
                phase1_facts.append(t)
            continue

        granularity, n = pol
        covered = months_covered_by_ir(t1_dt, granularity, n)
        in_window = any(m in covered for m in months)     # au moins un mois dans la fenêtre IR
        hist = [m for m in months if m not in covered]     # mois plus anciens que la fenêtre

        # Glissement : un nouveau mois a commencé depuis le dernier rechargement
        # de CETTE table → la politique doit créer / fusionner / supprimer des partitions.
        t0_dt = datetime.fromisoformat(FACT_T0[t])
        # ◄ À ADAPTER si politique IR au JOUR : remplacer par  t1_dt.date() != t0_dt.date()
        rolling_needed = (t1_dt.year, t1_dt.month) != (t0_dt.year, t0_dt.month)

        print(f"{t} : politique {n} x {granularity} | fenêtre IR : {in_window} | "
              f"glissement : {rolling_needed} | historique : {hist}")

        if in_window or rolling_needed:
            phase1_facts.append(t)
        if hist:
            historical[t] = hist

    print("Dimensions modifiées :", CHANGED_DIMS)

    if not phase1_facts and not historical and not CHANGED_DIMS:
        print("AUCUN CHANGEMENT : aucun refresh lancé")
        finish_run("NO_CHANGE", [], [], [])
    else:
        # ── C. PHASE 1 : tables de faits AVEC la politique + dimensions modifiées
        phase1_tables = phase1_facts + CHANGED_DIMS
        print("PHASE 1 - TABLES :", phase1_tables)

        if phase1_tables:
            wait_if_refresh_running()
            refresh_semantic_model(
                dataset=SEMANTIC_MODEL_ID,
                workspace=WORKSPACE_ID,
                tables=phase1_tables,
                refresh_type="full",
                apply_refresh_policy=True,     # ◄ NE PAS MODIFIER : Power BI gère les partitions
                effective_date=t1_dt.date(),   # date de référence de la politique = T1
                commit_mode="transactional",   # tout ou rien
                retry_count=0,
                visualize=False,
                verbose=1,
            )
            print("PHASE 1 OK")

        # ── D. PHASE 2 : partitions historiques touchées, SANS la politique,
        #       toutes tables de faits confondues, en un seul appel.
        #       Liste des partitions relue APRÈS la phase 1 (qui a pu en fusionner).
        phase2 = []            # [(table, partition), ...]
        done_facts = []        # tables de faits dont tous les mois historiques sont traités
        if historical:
            fabric.refresh_tom_cache(workspace=WORKSPACE_ID)
            partitions = fabric.list_partitions(dataset=SEMANTIC_MODEL_ID, workspace=WORKSPACE_ID)
            for t, hist in historical.items():
                existing = set(partitions.loc[partitions["Table Name"] == t, "Partition Name"].astype(str))
                for y, m in hist:
                    part = resolve_partition(y, m, existing)
                    if part is None:
                        print(f"{t} {y}-{m:02d} -> aucune partition (hors période stockée), ignoré")
                        continue
                    if (t, part) not in phase2:
                        phase2.append((t, part))
                    print(f"{t} {y}-{m:02d} -> {part} -> PHASE 2")
                done_facts.append(t)

        phase2_labels = [f"{t}[{p}]" for t, p in phase2]
        print("PHASE 2 PARTITIONS :", phase2_labels)

        if phase2:
            wait_if_refresh_running()
            refresh_semantic_model(
                dataset=SEMANTIC_MODEL_ID,
                workspace=WORKSPACE_ID,
                partitions=[f"'{t}'[{p}]" for t, p in phase2],
                refresh_type="full",
                apply_refresh_policy=False,    # ◄ NE PAS MODIFIER : obligatoire pour cibler une partition
                commit_mode="transactional",
                retry_count=0,
                visualize=False,
                verbose=1,
            )
            print("PHASE 2 OK")

        # ── E. CLÔTURE : marque-pages des objets traités + journal ──────────
        finish_run("SUCCEEDED", phase1_tables, phase2_labels, done_facts)

    print(f"DURÉE SMART REFRESH : {time.time() - start:.0f} s")

except Exception as e:
    # Toute erreur : passage FAILED, marque-pages inchangés (rien n'est perdu)
    mark_failed(f"Exécution : {e}")
    raise
