-- ══════════════════════════════════════════════════════════════════════════════
--  Warehouse · SCRIPT 2 / 3 · Initialisation des marque-pages   [SQL · Warehouse]
-- ──────────────────────────────────────────────────────────────────────────────
--  RÔLE       Créer une ligne de marque-page par table suivie, UNE FOIS, juste
--             après le premier refresh complet du modèle sémantique.
--  À ADAPTER  @Init = heure UTC de ce refresh complet (tout ce qui a été modifié
--             avant est déjà dans le modèle) ; 'MON_MODELE' ; une ligne par table.
--             ObjectType : 'Fact' pour CHAQUE table de faits, 'Dimension' sinon.
--  ASTUCE     heure du refresh : SSMS > connexion XMLA au workspace > modèle >
--             table > Partitions > « Dernier traitement » (à convertir en UTC).
-- ══════════════════════════════════════════════════════════════════════════════
DECLARE @Init DATETIME2(6) = '2026-01-01T00:00:00';   -- ◄ À ADAPTER : heure UTC du dernier refresh complet

INSERT INTO dbo.SmartRefreshObjectWatermark (ModelKey, ObjectName, ObjectType, WatermarkUtc)
SELECT 'MON_MODELE', 'FactSales',   'Fact',      @Init      -- ◄ À ADAPTER : une ligne par table de faits
UNION ALL
SELECT 'MON_MODELE', 'DimCustomer', 'Dimension', @Init      -- ◄ À ADAPTER : une ligne par dimension suivie
UNION ALL
SELECT 'MON_MODELE', 'DimProduct',  'Dimension', @Init
UNION ALL
SELECT 'MON_MODELE', 'DimStore',    'Dimension', @Init;

-- Contrôle
SELECT * FROM dbo.SmartRefreshObjectWatermark WHERE ModelKey = 'MON_MODELE';
