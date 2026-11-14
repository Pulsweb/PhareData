%%tsql -artifact <NomDuWarehouse> -type Warehouse -bind detection_df
-- ══════════════════════════════════════════════════════════════════════════════
--  SmartRefresh_DetectChanges · CELLULE 2 / 7 · Mois modifiés des faits    [T-SQL]
-- ──────────────────────────────────────────────────────────────────────────────
--  RÔLE       Pour CHAQUE table de faits : les (année, mois) dont au moins une
--             ligne a été ajoutée ou modifiée dans ]T0 ; T1], T0 étant SON
--             propre marque-page.
--  SORTIE     detection_df (lu par la cellule 5) : au moins une ligne par table
--             de faits ; ChangeYear / ChangeMonth à NULL si elle n'a pas changé.
--  À ADAPTER  <NomDuWarehouse>, 'MON_MODELE', et UN BLOC PAR TABLE DE FAITS
--             dans « Changes » : nom (= modèle), table source, colonne de date
--             de la politique IR, colonne de modification (UTC).
--  NE PAS     changer les noms de colonnes renvoyées (lues par la cellule 5).
-- ══════════════════════════════════════════════════════════════════════════════
WITH R AS                      -- le passage en cours, créé par la cellule 1
(
    SELECT TOP 1 RunId, T1
    FROM dbo.SmartRefreshRun
    WHERE ModelKey = 'MON_MODELE'                               -- ◄ À ADAPTER : clé du modèle
      AND Status = 'RUNNING'
    ORDER BY RunId DESC
),
W AS                           -- marque-page (T0) de chaque table de faits
(
    SELECT ObjectName, WatermarkUtc AS T0
    FROM dbo.SmartRefreshObjectWatermark
    WHERE ModelKey = 'MON_MODELE'                               -- ◄ À ADAPTER : clé du modèle
      AND ObjectType = 'Fact'
),
Changes AS                     -- mois touchés, table par table, dans ]T0 ; T1]
(
    -- ── Bloc table de faits n°1 ──────────────────────────────────────────────
    SELECT DISTINCT
        'FactSales'              AS TableName,                  -- ◄ À ADAPTER : nom (= modèle + marque-page)
        YEAR(F.TransactionDate)  AS ChangeYear,                 -- ◄ À ADAPTER : colonne de date IR
        MONTH(F.TransactionDate) AS ChangeMonth                 -- ◄ À ADAPTER : idem
    FROM dbo.FactSales AS F                                     -- ◄ À ADAPTER : table source
    JOIN W ON W.ObjectName = 'FactSales'                        -- ◄ À ADAPTER : même nom
    CROSS JOIN R
    WHERE F.LastModificationDate >  W.T0                        -- ◄ À ADAPTER : colonne de modification
      AND F.LastModificationDate <= R.T1                        --   ]T0 ; T1] : fenêtres collées, sans trou

    -- ── Bloc table de faits n°2 (exemple) : décommenter et adapter ─────────
    -- UNION ALL
    -- SELECT DISTINCT 'FactReturns', YEAR(F.ReturnDate), MONTH(F.ReturnDate)
    -- FROM dbo.FactReturns AS F
    -- JOIN W ON W.ObjectName = 'FactReturns'
    -- CROSS JOIN R
    -- WHERE F.LastModificationDate > W.T0 AND F.LastModificationDate <= R.T1
)
SELECT
    R.RunId,
    CONVERT(VARCHAR(33), R.T1, 126) AS T1,                      -- dates au format ISO pour Python
    W.ObjectName                    AS TableName,
    CONVERT(VARCHAR(33), W.T0, 126) AS T0,
    C.ChangeYear,
    C.ChangeMonth
FROM R
CROSS JOIN W
LEFT JOIN Changes AS C ON C.TableName = W.ObjectName            -- 1 ligne par table, même sans changement
ORDER BY W.ObjectName, C.ChangeYear, C.ChangeMonth;
