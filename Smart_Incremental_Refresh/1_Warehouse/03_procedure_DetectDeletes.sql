-- ══════════════════════════════════════════════════════════════════════════════
--  Warehouse · SCRIPT 3 / 3 · Procédure suppressions            [SQL · Warehouse]
-- ──────────────────────────────────────────────────────────────────────────────
--  RÔLE       Détecter les lignes supprimées, invisibles pour le watermark (une
--             ligne supprimée n'a plus de LastModificationDate).
--  PRINCIPE   dbo.SmartRefreshKeys garde toutes les clés connues du modèle :
--             clé connue mais absente de la source = ligne supprimée.
--               table de faits : clé + date (donne le mois à rafraîchir)
--               dimension      : clé seule (la dimension est rechargée)
--  SORTIE     TableName, DelYear, DelMonth (NULL pour une dimension)
--  À ADAPTER  chaque table suivie apparaît à 2 endroits : étape 1 (un LEFT JOIN
--             + une ligne du WHERE) et étape 3 (un SELECT de l'UNION ALL).
--  NE PAS     modifier les étapes 2 et 4 (génériques).
-- ══════════════════════════════════════════════════════════════════════════════
CREATE OR ALTER PROCEDURE dbo.usp_SmartRefresh_DetectDeletes
    @ModelKey VARCHAR(100),   -- clé du modèle (passée par DetectChanges, cellule 4)
    @RunId    INT = NULL      -- passage en cours ; si absent, la ligne RUNNING du modèle
AS
BEGIN
    SET NOCOUNT ON;

    IF @RunId IS NULL
        SET @RunId = (SELECT MAX(RunId) FROM dbo.SmartRefreshRun
                      WHERE Status = 'RUNNING' AND ModelKey = @ModelKey);

    -- -----------------------------------------------------------------
    -- 1. Marquer les clés disparues de la source
    -- -----------------------------------------------------------------
    UPDATE K
    SET K.DeletedRunId = @RunId, K.DeletedUtc = SYSUTCDATETIME()
    FROM dbo.SmartRefreshKeys AS K
    -- ◄ À ADAPTER : un LEFT JOIN par table suivie (tables de faits ET dimensions)
    --   'NomLogique' = nom écrit dans SmartRefreshKeys.TableName (= nom dans le modèle)
    --   X.Cle        = colonne clé UNIQUE de la table source
    LEFT JOIN dbo.FactSales   AS F1 ON K.TableName = 'FactSales'   AND F1.TransactionId = K.KeyValue
 -- LEFT JOIN dbo.FactReturns AS F2 ON K.TableName = 'FactReturns' AND F2.ReturnId      = K.KeyValue
    LEFT JOIN dbo.DimCustomer AS D1 ON K.TableName = 'DimCustomer' AND D1.CustomerId    = K.KeyValue
    LEFT JOIN dbo.DimProduct  AS D2 ON K.TableName = 'DimProduct'  AND D2.ProductId     = K.KeyValue
    LEFT JOIN dbo.DimStore    AS D3 ON K.TableName = 'DimStore'    AND D3.StoreId       = K.KeyValue
    WHERE K.ModelKey = @ModelKey
      AND K.DeletedRunId IS NULL
      -- ◄ À ADAPTER : une ligne par table, même alias et même clé que dans le LEFT JOIN
      AND (   (K.TableName = 'FactSales'   AND F1.TransactionId IS NULL)
        --   OR (K.TableName = 'FactReturns' AND F2.ReturnId      IS NULL)   -- exemple 2e table de faits
           OR (K.TableName = 'DimCustomer' AND D1.CustomerId    IS NULL)
           OR (K.TableName = 'DimProduct'  AND D2.ProductId     IS NULL)
           OR (K.TableName = 'DimStore'    AND D3.StoreId       IS NULL));

    -- -----------------------------------------------------------------
    -- 2. Reprendre les suppressions d'un passage précédent qui a échoué
    --    (générique : ne pas modifier)
    -- -----------------------------------------------------------------
    UPDATE dbo.SmartRefreshKeys
    SET DeletedRunId = @RunId
    WHERE ModelKey = @ModelKey
      AND DeletedRunId IN (SELECT RunId FROM dbo.SmartRefreshRun
                           WHERE ModelKey = @ModelKey AND RunId < @RunId
                             AND Status NOT IN ('SUCCEEDED', 'NO_CHANGE'));

    -- -----------------------------------------------------------------
    -- 3. Ajouter les nouvelles clés de la source
    --    (le premier appel remplit la table : c'est l'initialisation)
    -- -----------------------------------------------------------------
    INSERT INTO dbo.SmartRefreshKeys (ModelKey, TableName, KeyValue, TransactionDate)

    -- ◄ À ADAPTER (tables de faits) : nom logique, clé unique, colonne de date de la politique IR
    SELECT @ModelKey, 'FactSales', F.TransactionId, F.TransactionDate FROM dbo.FactSales F
    WHERE NOT EXISTS (SELECT 1 FROM dbo.SmartRefreshKeys K
                      WHERE K.ModelKey = @ModelKey AND K.TableName = 'FactSales'
                        AND K.KeyValue = F.TransactionId AND K.DeletedRunId IS NULL)
 -- UNION ALL                                                                    -- exemple 2e table de faits
 -- SELECT @ModelKey, 'FactReturns', F.ReturnId, F.ReturnDate FROM dbo.FactReturns F
 -- WHERE NOT EXISTS (SELECT 1 FROM dbo.SmartRefreshKeys K
 --                   WHERE K.ModelKey = @ModelKey AND K.TableName = 'FactReturns'
 --                     AND K.KeyValue = F.ReturnId AND K.DeletedRunId IS NULL)

    -- ◄ À ADAPTER (dimensions) : un bloc par dimension, date = NULL, CAST en BIGINT si clé INT
    UNION ALL
    SELECT @ModelKey, 'DimCustomer', CAST(D.CustomerId AS BIGINT), NULL FROM dbo.DimCustomer D
    WHERE NOT EXISTS (SELECT 1 FROM dbo.SmartRefreshKeys K
                      WHERE K.ModelKey = @ModelKey AND K.TableName = 'DimCustomer'
                        AND K.KeyValue = D.CustomerId AND K.DeletedRunId IS NULL)
    UNION ALL
    SELECT @ModelKey, 'DimProduct', CAST(D.ProductId AS BIGINT), NULL FROM dbo.DimProduct D
    WHERE NOT EXISTS (SELECT 1 FROM dbo.SmartRefreshKeys K
                      WHERE K.ModelKey = @ModelKey AND K.TableName = 'DimProduct'
                        AND K.KeyValue = D.ProductId AND K.DeletedRunId IS NULL)
    UNION ALL
    SELECT @ModelKey, 'DimStore', CAST(D.StoreId AS BIGINT), NULL FROM dbo.DimStore D
    WHERE NOT EXISTS (SELECT 1 FROM dbo.SmartRefreshKeys K
                      WHERE K.ModelKey = @ModelKey AND K.TableName = 'DimStore'
                        AND K.KeyValue = D.StoreId AND K.DeletedRunId IS NULL);

    -- -----------------------------------------------------------------
    -- 4. Résultat : ce qu'il faut rafraîchir à cause des suppressions
    --    (générique : ne pas modifier)
    --    - table de faits : année et mois de chaque ligne supprimée
    --    - dimension      : son nom (DelYear / DelMonth à NULL)
    -- -----------------------------------------------------------------
    SELECT DISTINCT
        TableName,
        YEAR(TransactionDate)  AS DelYear,
        MONTH(TransactionDate) AS DelMonth
    FROM dbo.SmartRefreshKeys
    WHERE ModelKey = @ModelKey
      AND DeletedRunId = @RunId;
END;
