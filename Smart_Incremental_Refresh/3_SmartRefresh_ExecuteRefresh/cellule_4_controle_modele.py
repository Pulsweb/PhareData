# ══════════════════════════════════════════════════════════════════════════════
#  SmartRefresh_ExecuteRefresh · CELLULE 4 / 5 · Contrôle du modèle        [Python]
# ──────────────────────────────────────────────────────────────────────────────
#  RÔLE       Vérifier les identifiants de la cellule 1 : doit afficher le nom
#             de votre modèle sémantique. En cas d'erreur, le passage est
#             clôturé en FAILED.
#  À ADAPTER  rien (les GUID se règlent dans la cellule 1)
# ══════════════════════════════════════════════════════════════════════════════
import sempy.fabric as fabric

try:
    print("Modèle :", fabric.resolve_dataset_name(SEMANTIC_MODEL_ID, workspace=WORKSPACE_ID))
except Exception as e:
    mark_failed(f"Identifiants : {e}")
    raise
