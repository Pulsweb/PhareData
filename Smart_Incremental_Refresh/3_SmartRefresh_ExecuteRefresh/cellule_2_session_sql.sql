%%tsql -artifact <NomDuWarehouse> -type Warehouse -session
-- ══════════════════════════════════════════════════════════════════════════════
--  SmartRefresh_ExecuteRefresh · CELLULE 2 / 5 · Session SQL                [T-SQL]
-- ──────────────────────────────────────────────────────────────────────────────
--  RÔLE       Ouvrir une connexion au Warehouse qui reste active pour la suite
--             du notebook (option -session). run_sql() (cellule 1) l'utilise
--             pour écrire le journal et les marque-pages.
--  À ADAPTER  <NomDuWarehouse> = le Warehouse qui contient les tables SmartRefresh*
--  NE PAS     supprimer cette cellule ni l'option -session : sans elle, toutes
--             les écritures SQL des cellules 3 et 5 échouent.
-- ══════════════════════════════════════════════════════════════════════════════
SELECT 1 AS ok;   -- requête neutre : sert uniquement à ouvrir la session
