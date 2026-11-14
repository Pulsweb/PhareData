# ══════════════════════════════════════════════════════════════════════════════
#  SmartRefresh_DetectChanges · CELLULE 5 / 7 · Sortie JSON                [Python]
# ──────────────────────────────────────────────────────────────────────────────
#  RÔLE       Réunir detection_df (cellule 2), dim_df (cellule 3) et deleted_df
#             (cellule 4), puis renvoyer le tout à SmartRefresh_ExecuteRefresh.
#  SORTIE     JSON : runId, t1, factT0 {table: marque-page},
#             changedPeriods [{"table", "year", "month"}], changedDims [...]
#  À ADAPTER  'MON_MODELE' (clé du modèle) uniquement
#  NE PAS     lancer seule : hors d'un passage complet, detection_df n'existe pas
#             (erreur NameError normale).
# ══════════════════════════════════════════════════════════════════════════════
import json
import pandas as pd
import notebookutils


def to_pandas(name):
    """DataFrame lié par une cellule %%tsql -bind (None s'il n'existe pas)."""
    d = globals().get(name)
    if d is not None and hasattr(d, "toPandas"):   # selon le moteur, -bind peut renvoyer un DataFrame Spark
        d = d.toPandas()
    return d


# ── 1. Cellule 2 : tables de faits, marque-pages et mois modifiés ────────────
df = to_pandas("detection_df")
if df is None or df.empty:
    raise ValueError("La détection n'a retourné aucune ligne (aucun passage RUNNING ?).")

run_id = int(df["RunId"].iloc[0])    # même valeur sur toutes les lignes
t1 = str(df["T1"].iloc[0])           # borne haute du passage

# Marque-page de chaque table de faits (une entrée par table, même sans changement)
fact_t0 = {str(r["TableName"]): str(r["T0"]) for _, r in df.drop_duplicates("TableName").iterrows()}

changed_periods = [                  # lignes NULL (= table sans changement) ignorées
    {"table": str(r["TableName"]), "year": int(r["ChangeYear"]), "month": int(r["ChangeMonth"])}
    for _, r in df.dropna(subset=["ChangeYear", "ChangeMonth"]).iterrows()
]

# ── 2. Cellule 3 : dimensions modifiées ───────────────────────────────────────
ddf = to_pandas("dim_df")
changed_dims = [] if ddf is None or ddf.empty else ddf["TableName"].astype(str).tolist()

# ── 3. Cellule 4 : lignes supprimées (ajoutées aux deux listes, sans doublon) ─
#      table de faits → le mois de la ligne supprimée
#      dimension      → son nom (elle sera rechargée en entier)
xdf = to_pandas("deleted_df")
if xdf is not None and not xdf.empty:
    for _, r in xdf.iterrows():
        name = str(r["TableName"])
        if name in fact_t0:                                   # table de faits
            if pd.notna(r["DelYear"]):                        # date absente : ignorée
                p = {"table": name, "year": int(r["DelYear"]), "month": int(r["DelMonth"])}
                if p not in changed_periods:
                    changed_periods.append(p)
        elif name not in changed_dims:                        # dimension
            changed_dims.append(name)

print(f"Suppressions : {0 if xdf is None else len(xdf)} objet(s) touché(s)")

# ── 4. JSON renvoyé à SmartRefresh_ExecuteRefresh ─────────────────────────────
result = {
    "modelKey": "MON_MODELE",                    # ◄ À ADAPTER : clé du modèle
    "runId": run_id,
    "t1": t1,
    "factT0": fact_t0,
    "changedPeriods": changed_periods,
    "changedDims": changed_dims,
}

print(json.dumps(result, indent=2))              # visible dans l'instantané de l'exécution
notebookutils.notebook.exit(json.dumps(result))  # ◄ NE PAS MODIFIER : valeur reçue par ExecuteRefresh
