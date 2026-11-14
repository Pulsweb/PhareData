# ══════════════════════════════════════════════════════════════════════════════
#  SmartRefresh_DetectChanges · CELLULE 0b / 7 · Garde-fou                 [Python]
# ──────────────────────────────────────────────────────────────────────────────
#  RÔLE       Empêcher le lancement de ce notebook seul. Lancé seul, il s'arrête
#             ici, AVANT la cellule 1 : aucun verrou RUNNING n'est posé.
#  À ADAPTER  rien
#  NE PAS     fusionner avec la cellule 0 (la valeur reçue arrive APRÈS elle).
# ══════════════════════════════════════════════════════════════════════════════
if CALLER != "SmartRefresh_ExecuteRefresh":   # ◄ NE PAS MODIFIER : même texte que dans ExecuteRefresh
    raise RuntimeError(
        "Ne pas lancer SmartRefresh_DetectChanges seul : "
        "lancez SmartRefresh_ExecuteRefresh."
    )
