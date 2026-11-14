%%tsql -artifact <NomDuWarehouse> -type Warehouse -bind dim_df
-- ══════════════════════════════════════════════════════════════════════════════
--  SmartRefresh_DetectChanges · CELLULE 3 / 7 · Dimensions modifiées        [T-SQL]
-- ──────────────────────────────────────────────────────────────────────────────
--  RÔLE       Le nom de chaque dimension ayant au moins une ligne ajoutée ou
--             modifiée dans ]T0 ; T1], T0 étant SON propre marque-page.
--  SORTIE     dim_df (lu par la cellule 5) ; dimension inchangée = absente.
--  À ADAPTER  <NomDuWarehouse>, 'MON_MODELE', et UN BLOC PAR DIMENSION.
--             Ajouter une dimension : copier un bloc « UNION ALL SELECT ... » et
--             changer le nom aux 3 endroits (texte, FROM, D.ObjectName).
--             Voir aussi l'annexe B (marque-page, procédure, DIM_TABLES).
-- ══════════════════════════════════════════════════════════════════════════════
WITH R AS                      -- le passage en cours (borne haute T1)
(
    SELECT TOP 1 T1
    FROM dbo.SmartRefreshRun
    WHERE ModelKey = 'MON_MODELE'                               -- ◄ À ADAPTER : clé du modèle
      AND Status = 'RUNNING'
    ORDER BY RunId DESC
),
D AS                           -- marque-page de chaque dimension
(
    SELECT ObjectName,
           COALESCE(WatermarkUtc, CAST('1900-01-01' AS DATETIME2(6))) AS T0   -- vide = tout est modifié
    FROM dbo.SmartRefreshObjectWatermark
    WHERE ModelKey = 'MON_MODELE'                               -- ◄ À ADAPTER : clé du modèle
      AND ObjectType = 'Dimension'
)
-- ── Un bloc par dimension (EXISTS s'arrête à la 1re ligne trouvée : rapide) ──
SELECT 'DimCustomer' AS TableName                                                 -- ◄ À ADAPTER : dimension 1
WHERE EXISTS (SELECT 1 FROM dbo.DimCustomer X CROSS JOIN R JOIN D ON D.ObjectName = 'DimCustomer'
              WHERE X.LastModificationDate > D.T0 AND X.LastModificationDate <= R.T1)
UNION ALL
SELECT 'DimProduct'                                                               -- ◄ À ADAPTER : dimension 2
WHERE EXISTS (SELECT 1 FROM dbo.DimProduct X CROSS JOIN R JOIN D ON D.ObjectName = 'DimProduct'
              WHERE X.LastModificationDate > D.T0 AND X.LastModificationDate <= R.T1)
UNION ALL
SELECT 'DimStore'                                                                 -- ◄ À ADAPTER : dimension 3
WHERE EXISTS (SELECT 1 FROM dbo.DimStore X CROSS JOIN R JOIN D ON D.ObjectName = 'DimStore'
              WHERE X.LastModificationDate > D.T0 AND X.LastModificationDate <= R.T1);
