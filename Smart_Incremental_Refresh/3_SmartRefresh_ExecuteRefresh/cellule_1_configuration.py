# ══════════════════════════════════════════════════════════════════════════════
#  SmartRefresh_ExecuteRefresh · CELLULE 1 / 5 · Configuration             [Python]
# ──────────────────────────────────────────────────────────────────────────────
#  RÔLE       Tous les réglages du framework + 3 fonctions SQL utilitaires.
#             C'est la SEULE cellule de ce notebook à adapter à chaque projet.
#  À ADAPTER  le bloc « RÉGLAGES » ci-dessous. Les noms de tables doivent être
#             EXACTEMENT ceux du modèle sémantique ET ceux de la colonne
#             ObjectName de dbo.SmartRefreshObjectWatermark.
#  NE PAS     modifier les fonctions run_sql, q et mark_failed.
# ══════════════════════════════════════════════════════════════════════════════
import json
import re

# ── RÉGLAGES ──────────────────────────────────────────────────────────────────
MODEL_KEY = "MON_MODELE"                                # ◄ À ADAPTER : clé du modèle (= ModelKey des tables)
FACT_TABLES = ["FactSales"]                             # ◄ À ADAPTER : tables de faits suivies
                                                        #   ex. ["FactSales", "FactReturns"]
DIM_TABLES = ["DimCustomer", "DimProduct", "DimStore"]  # ◄ À ADAPTER : dimensions suivies
DETECT_NOTEBOOK = "SmartRefresh_DetectChanges"          # ◄ À ADAPTER : seulement si le notebook est renommé

WORKSPACE_ID = "<WORKSPACE_ID>"                         # ◄ À ADAPTER : GUID du workspace
SEMANTIC_MODEL_ID = "<SEMANTIC_MODEL_ID>"               # ◄ À ADAPTER : GUID du modèle sémantique
#   Les deux GUID se lisent dans l'URL du modèle dans Fabric :
#   .../groups/<WORKSPACE_ID>/datasets/<SEMANTIC_MODEL_ID>/...

LOCK_TIMEOUT_MIN = 30    # ◄ À ADAPTER : minutes avant libération d'un verrou mort
FORCE_UNLOCK = False     # ◄ True = débloquer tout de suite ; REMETTRE À False juste après

# ── État du passage : rempli par la cellule 3 ─────────────────────────────────
RUN_ID = None            # ◄ NE PAS MODIFIER : numéro du passage (connu après la détection)
RUN_START_UTC = None     # ◄ NE PAS MODIFIER : heure de lancement du passage


# ── Fonctions utilitaires ─────────────────────────────────────────────────────

def run_sql(sql):
    """Exécute du T-SQL dans la session ouverte par la cellule 2.
    ⚠ Le SQL est envoyé sur UNE SEULE ligne à la commande %tsql, donc :
      - pas de commentaire « -- » dans le SQL (il couperait la suite) ;
      - aucun mot ne doit commencer par « - » (%tsql le prendrait pour une option) :
        écrire DATEADD(MINUTE, 30, x) <= y plutôt que x <= DATEADD(MINUTE, -30, y)."""
    get_ipython().run_line_magic("tsql", " ".join(sql.split()))   # ◄ NE PAS MODIFIER


def q(value):
    """Nettoie un texte avant de l'écrire en SQL : ne garde que lettres, chiffres,
    espaces et ponctuation simple. Apostrophes, guillemets et tirets sont retirés
    (un message d'erreur qui en contenait cassait l'écriture du journal)."""
    return re.sub(r"[^0-9A-Za-zÀ-ÿ .,:;_()/\[\]]", " ", str(value))[:3900]   # ◄ NE PAS MODIFIER


def mark_failed(message):
    """Passe NOTRE passage en FAILED, jamais celui d'un autre lancement :
      - RUN_ID connu (détection terminée)  → ce passage-là ;
      - sinon                              → le passage RUNNING créé depuis RUN_START_UTC.
    Les marque-pages ne bougent pas : le passage suivant revérifiera tout."""
    if RUN_ID is not None:
        target = f"RunId = {int(RUN_ID)}"
    elif RUN_START_UTC is not None:
        target = f"StartedUtc >= CAST('{RUN_START_UTC}' AS DATETIME2(6))"
    else:
        print("Aucun passage à clôturer")
        return
    run_sql(f"""
        UPDATE dbo.SmartRefreshRun
        SET Status = 'FAILED',
            EndedUtc = SYSUTCDATETIME(),
            DurationS = DATEDIFF(SECOND, StartedUtc, SYSUTCDATETIME()),
            ErrorMessage = '{q(message)}'
        WHERE ModelKey = '{MODEL_KEY}' AND Status = 'RUNNING' AND {target};
    """)
    print("Passage -> FAILED")
