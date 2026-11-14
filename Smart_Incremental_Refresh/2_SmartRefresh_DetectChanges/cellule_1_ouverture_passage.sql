%%tsql -artifact <NomDuWarehouse> -type Warehouse
-- ══════════════════════════════════════════════════════════════════════════════
--  SmartRefresh_DetectChanges · CELLULE 1 / 7 · Ouverture du passage       [T-SQL]
-- ──────────────────────────────────────────────────────────────────────────────
--  RÔLE       1. vérifier que chaque table de faits a un marque-page
--             2. libérer un passage resté RUNNING plus de 5 h (filet de sécurité)
--             3. refuser de démarrer si un passage est déjà en cours (verrou)
--             4. créer la ligne RUNNING du passage, avec sa borne haute T1
--  SORTIE     une ligne RUNNING dans dbo.SmartRefreshRun (lue par les cellules 2 à 4)
--  À ADAPTER  <NomDuWarehouse> (1re ligne) et 'MON_MODELE' (clé du modèle)
--  NE PAS     modifier le texte « déjà en cours » (reconnu par ExecuteRefresh)
-- ══════════════════════════════════════════════════════════════════════════════

-- 1) Chaque table de faits (ObjectType = 'Fact') doit avoir un marque-page renseigné
IF NOT EXISTS (SELECT 1 FROM dbo.SmartRefreshObjectWatermark
               WHERE ModelKey = 'MON_MODELE' AND ObjectType = 'Fact')     -- ◄ À ADAPTER : clé du modèle
   OR EXISTS (SELECT 1 FROM dbo.SmartRefreshObjectWatermark
              WHERE ModelKey = 'MON_MODELE' AND ObjectType = 'Fact'      -- ◄ À ADAPTER : clé du modèle
                AND WatermarkUtc IS NULL)
    THROW 50001, 'Marque-page de table de faits absent ou vide', 1;

-- 2) Filet de sécurité : un passage resté RUNNING plus de 5 h est libéré
--    (ExecuteRefresh libère déjà les verrous morts au bout de 30 min)
UPDATE dbo.SmartRefreshRun
SET Status = 'FAILED', ErrorMessage = 'Passage abandonné (resté RUNNING plus de 5 h)'
WHERE ModelKey = 'MON_MODELE'                                  -- ◄ À ADAPTER : clé du modèle
  AND Status = 'RUNNING'
  AND StartedUtc <= DATEADD(HOUR, -5, SYSUTCDATETIME());       -- 5 h = refresh max Fabric (2 h en Pro)

-- 3) Un seul passage à la fois par modèle
IF EXISTS (SELECT 1 FROM dbo.SmartRefreshRun
           WHERE ModelKey = 'MON_MODELE'                        -- ◄ À ADAPTER : clé du modèle
             AND Status = 'RUNNING')
    THROW 50002, 'Un passage Smart Refresh est déjà en cours', 1;   -- ◄ NE PAS MODIFIER : texte testé

-- 4) Création du passage : T1 = borne haute de détection = maintenant (UTC)
DECLARE @Now DATETIME2(6) = SYSUTCDATETIME();

INSERT INTO dbo.SmartRefreshRun (RunId, ModelKey, StartedUtc, T1, Status)
SELECT COALESCE(MAX(RunId), 0) + 1,                             -- numéro de passage suivant
       'MON_MODELE',                                            -- ◄ À ADAPTER : clé du modèle
       @Now,                                                    -- StartedUtc
       @Now,                                                    -- T1
       'RUNNING'
FROM dbo.SmartRefreshRun;
