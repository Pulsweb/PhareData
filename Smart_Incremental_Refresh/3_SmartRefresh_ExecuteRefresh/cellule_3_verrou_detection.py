# ══════════════════════════════════════════════════════════════════════════════
#  SmartRefresh_ExecuteRefresh · CELLULE 3 / 5 · Verrou + détection        [Python]
# ──────────────────────────────────────────────────────────────────────────────
#  RÔLE       1. libérer un verrou mort (passage RUNNING abandonné) ;
#             2. lancer SmartRefresh_DetectChanges et lire son JSON ;
#             3. vérifier que chaque table de FACT_TABLES a bien été détectée.
#  SORTIES    RUN_ID, T1, FACT_T0, CHANGED_PERIODS, CHANGED_DIMS (pour la cellule 5)
#  À ADAPTER  rien en général (délai max de la détection : 1800 s)
#  NE PAS     modifier le paramètre CALLER ni le test « déjà en cours ».
# ══════════════════════════════════════════════════════════════════════════════
import notebookutils
from datetime import datetime, timezone, timedelta
from sempy.fabric.semantic_model import list_refresh_requests


def model_refresh_in_progress():
    """True si un refresh tourne sur le modèle (planifié, manuel ou Smart Refresh)."""
    last = list_refresh_requests(dataset=SEMANTIC_MODEL_ID, workspace=WORKSPACE_ID, top_n=1)
    status_cols = [c for c in last.columns if "status" in c.lower()]
    return (
        not last.empty
        and any(str(last.iloc[0][c]) in ("Unknown", "NotStarted", "InProgress") for c in status_cols)
    )


# ── 1. Verrou mort ────────────────────────────────────────────────────────────
#  Mort = RUNNING depuis plus de LOCK_TIMEOUT_MIN minutes ET aucun refresh en
#  cours sur le modèle. Un passage en plein refresh n'est jamais libéré.
if FORCE_UNLOCK:
    age_min = 0
    print("FORCE_UNLOCK : libération de tout passage RUNNING")
elif model_refresh_in_progress():
    age_min = None
    print("Refresh en cours sur le modèle : aucun verrou libéré")
else:
    age_min = LOCK_TIMEOUT_MIN

if age_min is not None:
    # Écrit SANS signe moins : %tsql lirait « -30 » comme une option
    run_sql(f"""
        UPDATE dbo.SmartRefreshRun
        SET Status = 'FAILED',
            EndedUtc = SYSUTCDATETIME(),
            ErrorMessage = 'Verrou libere automatiquement (passage abandonne)'
        WHERE ModelKey = '{MODEL_KEY}'
          AND Status = 'RUNNING'
          AND DATEADD(MINUTE, {age_min}, StartedUtc) <= SYSUTCDATETIME();
    """)

# ── 2. Détection (notebook SmartRefresh_DetectChanges) ───────────────────────
RUN_ID = None
RUN_START_UTC = (datetime.now(timezone.utc) - timedelta(seconds=5)).strftime("%Y-%m-%d %H:%M:%S")

try:
    detection = json.loads(
        notebookutils.notebook.run(
            DETECT_NOTEBOOK, 1800,                      # ◄ À ADAPTER si besoin : délai max (s)
            {"CALLER": "SmartRefresh_ExecuteRefresh"}   # ◄ NE PAS MODIFIER : ouvre le garde-fou (cellule 0b)
        ) or "{}"
    )
    for key in ["runId", "t1", "factT0", "changedPeriods"]:
        if key not in detection:
            raise ValueError(f"Clé manquante dans la détection : {key}")

    RUN_ID = int(detection["runId"])           # numéro du passage
    T1 = detection["t1"]                       # borne haute du passage

    # ── 3. Contrôle : chaque table de FACT_TABLES doit avoir été détectée
    #       (marque-page + bloc dans DetectChanges cellule 2), sinon ses
    #       changements seraient ignorés sans bruit.
    missing = [t for t in FACT_TABLES if t not in detection["factT0"]]
    if missing:
        raise ValueError(f"Tables de faits sans marque-page ou sans bloc de détection : {missing}")
    ignored = [t for t in detection["factT0"] if t not in FACT_TABLES]
    if ignored:
        print(f"⚠ Tables de faits détectées mais absentes de FACT_TABLES (ignorées) : {ignored}")

    FACT_T0 = {t: detection["factT0"][t] for t in FACT_TABLES}                    # marque-page par table
    CHANGED_PERIODS = [p for p in detection["changedPeriods"] if p["table"] in FACT_TABLES]
    CHANGED_DIMS = [d for d in detection.get("changedDims", []) if d in DIM_TABLES]  # dims déclarées

except Exception as e:
    if "déjà en cours" in str(e):              # ◄ NE PAS MODIFIER : texte du THROW 50002
        # Un autre lancement tourne : on ne touche pas à son passage
        print("Un autre passage Smart Refresh est en cours : ce lancement s'arrête sans rien modifier.")
    else:
        mark_failed(f"Détection : {e}")
    raise

# ── Résumé affiché ────────────────────────────────────────────────────────────
print("============================================")
print("PASSAGE n°", RUN_ID, "| T1 :", T1)
for t in FACT_TABLES:
    months = [f"{p['year']}-{p['month']:02d}" for p in CHANGED_PERIODS if p["table"] == t]
    print(f"{t:<20} T0 : {FACT_T0[t]} | mois modifiés : {months}")
print("Dims modifiées  :", CHANGED_DIMS)
print("============================================")
