%%tsql -artifact <NomDuWarehouse> -type Warehouse -bind deleted_df
-- ══════════════════════════════════════════════════════════════════════════════
--  SmartRefresh_DetectChanges · CELLULE 4 / 7 · Lignes supprimées           [T-SQL]
-- ──────────────────────────────────────────────────────────────────────────────
--  RÔLE       Retrouver les lignes supprimées (faits et dimensions), invisibles
--             pour le watermark. Toute la logique est dans la procédure
--             dbo.usp_SmartRefresh_DetectDeletes.
--  SORTIE     deleted_df (lu par la cellule 5) : TableName, DelYear, DelMonth
--             (année / mois : tables de faits seulement). Le premier passage
--             initialise dbo.SmartRefreshKeys et ne renvoie rien.
--  À ADAPTER  <NomDuWarehouse> et 'MON_MODELE'. Les tables suivies se règlent
--             dans la procédure, pas ici.
-- ══════════════════════════════════════════════════════════════════════════════
EXEC dbo.usp_SmartRefresh_DetectDeletes @ModelKey = 'MON_MODELE';   -- ◄ À ADAPTER : clé du modèle
