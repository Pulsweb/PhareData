-- ══════════════════════════════════════════════════════════════════════════════
--  Warehouse · SCRIPT 1 / 3 · Tables de suivi                   [SQL · Warehouse]
-- ──────────────────────────────────────────────────────────────────────────────
--  RÔLE       Créer les 3 tables du framework, UNE SEULE FOIS par Warehouse.
--             Plusieurs modèles sémantiques peuvent les partager : chaque ligne
--             porte la clé de son modèle (ModelKey).
--  À ADAPTER  rien
--  NE PAS     renommer tables ou colonnes (utilisées par les notebooks).
--             Fabric Warehouse : pas de NVARCHAR, utiliser VARCHAR.
-- ══════════════════════════════════════════════════════════════════════════════

-- 1) Marque-pages : une ligne par table suivie du modèle sémantique
CREATE TABLE dbo.SmartRefreshObjectWatermark
(
    ModelKey      VARCHAR(100)  NOT NULL,   -- clé du modèle (= MODEL_KEY des notebooks)
    ObjectName    VARCHAR(200)  NOT NULL,   -- nom de la table, IDENTIQUE au modèle sémantique
    ObjectType    VARCHAR(20)   NOT NULL,   -- 'Fact' (table de faits) ou 'Dimension'
    WatermarkUtc  DATETIME2(6)  NULL        -- tout ce qui a été modifié en source jusqu'à
                                            -- cette heure (UTC) est déjà dans le modèle
);

-- 2) Journal : une ligne par passage (et verrou : un seul passage RUNNING par modèle)
CREATE TABLE dbo.SmartRefreshRun
(
    RunId            INT            NOT NULL,   -- numéro du passage
    ModelKey         VARCHAR(100)   NOT NULL,
    StartedUtc       DATETIME2(6)   NOT NULL,
    T1               DATETIME2(6)   NOT NULL,   -- borne haute de détection du passage
    EndedUtc         DATETIME2(6)   NULL,
    DurationS        INT            NULL,
    Status           VARCHAR(20)    NOT NULL,   -- RUNNING, SUCCEEDED, NO_CHANGE, FAILED
    ChangedPeriods   VARCHAR(4000)  NULL,       -- mois modifiés par table de faits
    ChangedDims      VARCHAR(4000)  NULL,       -- dimensions modifiées
    Phase1Tables     VARCHAR(4000)  NULL,       -- tables rechargées en phase 1
    Phase2Partitions VARCHAR(4000)  NULL,       -- partitions rechargées en phase 2
    ErrorMessage     VARCHAR(4000)  NULL
);

-- 3) Clés connues : sert UNIQUEMENT à détecter les suppressions physiques
CREATE TABLE dbo.SmartRefreshKeys
(
    ModelKey        VARCHAR(100) NOT NULL,   -- clé du modèle
    TableName       VARCHAR(100) NOT NULL,   -- table de faits ou dimension
    KeyValue        BIGINT       NOT NULL,   -- clé unique de la ligne
    TransactionDate DATE         NULL,       -- tables de faits seulement : date de la ligne
                                             -- (colonne de la politique IR), donne le mois
    DeletedRunId    INT          NULL,       -- NULL = ligne présente ; sinon passage qui a vu la suppression
    DeletedUtc      DATETIME2(6) NULL        -- heure de détection de la suppression
);
