USE AlbertaProductionDB;
GO

/*
PROJECT: Alberta Oil & Gas Production Data Platform
FILE:    16_select_pilot_wells_and_st103_candidates.sql
DATE:    October 31, 2026

PURPOSE:
1. Select 10 pilot wells for the AER Tableau extraction and
   reservoir/formation matching test.
2. List the ST103 candidate Geological Pools for the pilot wells.

READ-ONLY: no tables or records are modified.

Groups:
  A_ONE_CANDIDATE   3 wells, ST103 gives exactly 1 geological pool
  B_MFP9501         2 wells, COMMINGLED MFP9501 (largest ambiguous group)
  C_MULTI_CANDIDATE 5 wells, other pools with 2+ geological pools
Only wells with production records in 2026. One well per field per group.
*/


-- =====================================================
-- 1. SELECT PILOT WELLS
-- =====================================================

WITH ActiveWells AS
(
    SELECT DISTINCT Current_Well_ID
    FROM dbo.vw_Well_Production_Records
    WHERE Current_Well_ID IS NOT NULL
      AND Production_Month >= '2026-01-01'
),
Wells AS
(
    SELECT
        Well_ID,
        MAX(Well_Identifier)                     AS Well_Identifier,
        MAX(NULLIF(TRIM(Field_Code), ''))        AS Field_Code,
        MAX(NULLIF(TRIM(Field_Name), ''))        AS Field_Name,
        MAX(NULLIF(TRIM(Pool_Deposit_Code), '')) AS Production_Pool_Code,
        MAX(NULLIF(TRIM(Pool_Deposit_Name), '')) AS Production_Pool_Name,
        MAX(Licensee_Name)                       AS Licensee_Name
    FROM dbo.Source_Well_Infrastructure
    WHERE Well_ID IS NOT NULL
    GROUP BY Well_ID
),
PoolMappings AS
(
    SELECT
        Field_Code,
        Production_Pool_Code,
        COUNT(DISTINCT NULLIF(TRIM(Geological_Pool_Code), '')) AS Geo_Pool_Count
    FROM dbo.Ref_FieldPool_ST103
    GROUP BY Field_Code, Production_Pool_Code
),
Candidates AS
(
    SELECT
        CASE
            WHEN p.Geo_Pool_Count = 1               THEN 'A_ONE_CANDIDATE'
            WHEN w.Production_Pool_Code = '0950160' THEN 'B_MFP9501'
            WHEN p.Geo_Pool_Count > 1               THEN 'C_MULTI_CANDIDATE'
        END AS Test_Group,
        w.*,
        p.Geo_Pool_Count
    FROM Wells w
    JOIN ActiveWells a
        ON w.Well_ID = a.Current_Well_ID
    JOIN PoolMappings p
        ON w.Field_Code = p.Field_Code
       AND w.Production_Pool_Code = p.Production_Pool_Code
    WHERE p.Geo_Pool_Count >= 1
),
OnePerField AS
(
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY Test_Group, Field_Code
                           ORDER BY CHECKSUM(Well_ID)) AS rn_field
    FROM Candidates
),
Ranked AS
(
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY Test_Group
                           ORDER BY CHECKSUM(Field_Code, Well_ID)) AS rn_group
    FROM OnePerField
    WHERE rn_field = 1
)
SELECT
    Test_Group,
    Well_Identifier,
    Field_Name,
    Production_Pool_Code,
    Production_Pool_Name,
    Geo_Pool_Count,
    Licensee_Name
FROM Ranked
WHERE (Test_Group = 'A_ONE_CANDIDATE'   AND rn_group <= 3)
   OR (Test_Group = 'B_MFP9501'         AND rn_group <= 2)
   OR (Test_Group = 'C_MULTI_CANDIDATE' AND rn_group <= 5)
ORDER BY Test_Group, Field_Name;

-- Result (October 31, 2026): 10 wells
-- A: BLACK (KEG RIVER C), ELIZA (COLORADO A), SADDLE HILLS (BELLOY A)
-- B: GARTLEY, HERRONTON (COMMINGLED MFP9501)
-- C: ADEN (POOL 001), CHIGWELL (MFP9504), FAIRYDELL-BON ACCORD (MFP9508),
--    HUXLEY (POOL 007), WINDFALL (POOL 006)


-- =====================================================
-- 2. ST103 CANDIDATE GEOLOGICAL POOLS FOR THE PILOT WELLS
-- =====================================================

SELECT
    Field_Code, Field_Name,
    Production_Pool_Code, Production_Pool_Name,
    Geological_Pool_Code, Geological_Pool_Name
FROM dbo.Ref_FieldPool_ST103
WHERE (Field_Code = '0144' AND Production_Pool_Code = '0772103')
   OR (Field_Code = '0812' AND Production_Pool_Code = '0556001')
   OR (Field_Code = '0327' AND Production_Pool_Code = '0160001')
   OR (Field_Code = '0398' AND Production_Pool_Code = '0950160')
   OR (Field_Code = '0467' AND Production_Pool_Code = '0950160')
   OR (Field_Code = '0014' AND Production_Pool_Code = '0800160')
   OR (Field_Code = '0214' AND Production_Pool_Code = '0950460')
   OR (Field_Code = '0367' AND Production_Pool_Code = '0950860')
   OR (Field_Code = '0488' AND Production_Pool_Code = '0800760')
   OR (Field_Code = '0979' AND Production_Pool_Code = '0800660')
ORDER BY Field_Code, Geological_Pool_Code;

-- Candidate counts: BLACK 1, SADDLE HILLS 1, ELIZA 1, GARTLEY 2,
-- HERRONTON 44, ADEN 4, CHIGWELL 2, FAIRYDELL 4, HUXLEY 2, WINDFALL 2
