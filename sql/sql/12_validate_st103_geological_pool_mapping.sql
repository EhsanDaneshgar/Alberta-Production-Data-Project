
USE AlbertaProductionDB;
GO

/*
PROJECT: Alberta Oil & Gas Production Data Platform

FILE: 12_validate_st103_geological_pool_mapping.sql

PURPOSE:
Validate AER ST103 reference data and investigate
Geological Pool mapping coverage for Alberta wells.

DATA SOURCES:
- dbo.Ref_FieldPool_ST103
- dbo.Source_Well_Infrastructure
- dbo.vw_Well_Production_Records

PERIOD: January–August 2026

IMPORTANT:
- All queries are read-only.
- No tables or records are modified.
- Multiple candidate Geological Pools do not prove
  that a well produces from all of those pools.
*/


-- =====================================================
-- 1. VALIDATE ST103 IMPORT
-- =====================================================

SELECT
    COUNT(*) AS Total_Rows,
    COUNT(DISTINCT Field_Code) AS Distinct_Fields,
    COUNT(DISTINCT Geological_Pool_Code)
        AS Distinct_Geological_Pools,
    SUM(
        CASE
            WHEN Geological_Pool_Code IS NULL
              OR TRIM(Geological_Pool_Code) = ''
            THEN 1 ELSE 0
        END
    ) AS Missing_Geological_Pool_Codes
FROM dbo.Ref_FieldPool_ST103;

-- Confirmed results:
-- Total_Rows:                    68,515
-- Distinct_Fields:                  899
-- Distinct_Geological_Pools:     12,057
-- Missing_Geological_Pool_Codes:    985


-- =====================================================
-- 2. ANALYZE ST103 MAPPING CARDINALITY
-- =====================================================

WITH PoolMappings AS
(
    SELECT
        Field_Code,
        Production_Pool_Code,
        COUNT(
            DISTINCT NULLIF(TRIM(Geological_Pool_Code), '')
        ) AS Geological_Pool_Count
    FROM dbo.Ref_FieldPool_ST103
    GROUP BY
        Field_Code,
        Production_Pool_Code
)
SELECT
    COUNT(*) AS Total_Field_Production_Pool_Pairs,
    SUM(
        CASE WHEN Geological_Pool_Count = 1
        THEN 1 ELSE 0 END
    ) AS Pairs_With_One_Geological_Pool,
    SUM(
        CASE WHEN Geological_Pool_Count > 1
        THEN 1 ELSE 0 END
    ) AS Pairs_With_Multiple_Geological_Pools,
    SUM(
        CASE WHEN Geological_Pool_Count = 0
        THEN 1 ELSE 0 END
    ) AS Pairs_With_No_Geological_Pool
FROM PoolMappings;

-- Confirmed results:
-- Total pairs:            55,288
-- One Geological Pool:    49,845
-- Multiple Pools:          4,458
-- No Geological Pool:        985


-- =====================================================
-- 3. CHECK WELL INFRASTRUCTURE CONSISTENCY
-- =====================================================

WITH WellCounts AS
(
    SELECT
        Well_ID,
        COUNT(
            DISTINCT NULLIF(TRIM(Field_Code), '')
        ) AS Field_Count,
        COUNT(
            DISTINCT NULLIF(TRIM(Pool_Deposit_Code), '')
        ) AS Pool_Count
    FROM dbo.Source_Well_Infrastructure
    WHERE Well_ID IS NOT NULL
    GROUP BY Well_ID
)
SELECT
    COUNT(*) AS Total_Wells,
    SUM(
        CASE WHEN Field_Count > 1
        THEN 1 ELSE 0 END
    ) AS Wells_With_Multiple_Fields,
    SUM(
        CASE WHEN Pool_Count > 1
        THEN 1 ELSE 0 END
    ) AS Wells_With_Multiple_Production_Pools
FROM WellCounts;

-- Confirmed results:
-- Total_Wells:                         665,307
-- Wells_With_Multiple_Fields:                0
-- Wells_With_Multiple_Production_Pools:      0


-- =====================================================
-- 4. MEASURE WELL-LEVEL GEOLOGICAL POOL COVERAGE
-- =====================================================

WITH Wells AS
(
    SELECT
        Well_ID,
        MAX(NULLIF(TRIM(Field_Code), ''))
            AS Field_Code,
        MAX(NULLIF(TRIM(Pool_Deposit_Code), ''))
            AS Production_Pool_Code
    FROM dbo.Source_Well_Infrastructure
    WHERE Well_ID IS NOT NULL
    GROUP BY Well_ID
),
PoolMappings AS
(
    SELECT
        Field_Code,
        Production_Pool_Code,
        COUNT(
            DISTINCT NULLIF(TRIM(Geological_Pool_Code), '')
        ) AS Geological_Pool_Count
    FROM dbo.Ref_FieldPool_ST103
    GROUP BY
        Field_Code,
        Production_Pool_Code
)
SELECT
    COUNT(*) AS Total_Wells,

    SUM(
        CASE
            WHEN w.Field_Code IS NULL
              OR w.Production_Pool_Code IS NULL
            THEN 1 ELSE 0
        END
    ) AS Wells_Missing_Field_Or_Pool,

    SUM(
        CASE
            WHEN w.Field_Code IS NOT NULL
             AND w.Production_Pool_Code IS NOT NULL
             AND p.Geological_Pool_Count = 1
            THEN 1 ELSE 0
        END
    ) AS Wells_With_One_Geological_Pool,

    SUM(
        CASE WHEN p.Geological_Pool_Count > 1
        THEN 1 ELSE 0 END
    ) AS Wells_With_Multiple_Geological_Pools,

    SUM(
        CASE
            WHEN w.Field_Code IS NOT NULL
             AND w.Production_Pool_Code IS NOT NULL
             AND p.Geological_Pool_Count = 0
            THEN 1 ELSE 0
        END
    ) AS Wells_With_No_Geological_Pool_In_ST103,

    SUM(
        CASE
            WHEN w.Field_Code IS NOT NULL
             AND w.Production_Pool_Code IS NOT NULL
             AND p.Field_Code IS NULL
            THEN 1 ELSE 0
        END
    ) AS Wells_With_No_ST103_Match

FROM Wells w
LEFT JOIN PoolMappings p
    ON w.Field_Code = p.Field_Code
   AND w.Production_Pool_Code = p.Production_Pool_Code;

-- Confirmed results:
-- Total Wells:                          665,307
-- Missing Field or Pool:                322,694
-- One Geological Pool:                  138,512
-- Multiple Geological Pools:            192,909
-- No Geological Pool Code in ST103:       8,222
-- No ST103 Match:                          2,970


-- =====================================================
-- 5. IDENTIFY LARGEST AMBIGUOUS PRODUCTION POOLS
-- =====================================================

WITH Wells AS
(
    SELECT
        Well_ID,
        MAX(NULLIF(TRIM(Field_Code), ''))
            AS Field_Code,
        MAX(NULLIF(TRIM(Pool_Deposit_Code), ''))
            AS Production_Pool_Code,
        MAX(NULLIF(TRIM(Pool_Deposit_Name), ''))
            AS Production_Pool_Name
    FROM dbo.Source_Well_Infrastructure
    WHERE Well_ID IS NOT NULL
    GROUP BY Well_ID
),
PoolMappings AS
(
    SELECT
        Field_Code,
        Production_Pool_Code,
        COUNT(
            DISTINCT NULLIF(TRIM(Geological_Pool_Code), '')
        ) AS Geological_Pool_Count
    FROM dbo.Ref_FieldPool_ST103
    GROUP BY
        Field_Code,
        Production_Pool_Code
)
SELECT TOP (20)
    w.Production_Pool_Code,
    w.Production_Pool_Name,
    COUNT(DISTINCT w.Field_Code) AS Number_Of_Fields,
    COUNT(*) AS Number_Of_Wells
FROM Wells w
JOIN PoolMappings p
    ON w.Field_Code = p.Field_Code
   AND w.Production_Pool_Code = p.Production_Pool_Code
WHERE p.Geological_Pool_Count > 1
GROUP BY
    w.Production_Pool_Code,
    w.Production_Pool_Name
ORDER BY Number_Of_Wells DESC;

-- Largest group:
-- 0950160 | COMMINGLED MFP9501 | 99,369 wells


-- =====================================================
-- 6. IDENTIFY AMBIGUOUS WELLS WITH 2026 PRODUCTION
-- =====================================================

WITH ActiveWells AS
(
    SELECT DISTINCT
        Current_Well_ID
    FROM dbo.vw_Well_Production_Records
    WHERE Current_Well_ID IS NOT NULL
      AND Production_Month >= '2026-01-01'
      AND Production_Month < '2026-09-01'
),
Wells AS
(
    SELECT
        Well_ID,
        MAX(NULLIF(TRIM(Field_Code), ''))
            AS Field_Code,
        MAX(NULLIF(TRIM(Pool_Deposit_Code), ''))
            AS Production_Pool_Code
    FROM dbo.Source_Well_Infrastructure
    WHERE Well_ID IS NOT NULL
    GROUP BY Well_ID
),
PoolMappings AS
(
    SELECT
        Field_Code,
        Production_Pool_Code,
        COUNT(
            DISTINCT NULLIF(TRIM(Geological_Pool_Code), '')
        ) AS Geological_Pool_Count
    FROM dbo.Ref_FieldPool_ST103
    GROUP BY
        Field_Code,
        Production_Pool_Code
)
SELECT
    COUNT(*) AS Total_Ambiguous_Wells,
    SUM(
        CASE WHEN a.Current_Well_ID IS NOT NULL
        THEN 1 ELSE 0 END
    ) AS Wells_With_2026_Production,
    SUM(
        CASE WHEN a.Current_Well_ID IS NULL
        THEN 1 ELSE 0 END
    ) AS Wells_Without_2026_Production
FROM Wells w
JOIN PoolMappings p
    ON w.Field_Code = p.Field_Code
   AND w.Production_Pool_Code = p.Production_Pool_Code
LEFT JOIN ActiveWells a
    ON w.Well_ID = a.Current_Well_ID
WHERE p.Geological_Pool_Count > 1;

-- Confirmed results:
-- Total Ambiguous Wells:         192,909
-- With 2026 Production:           80,266
-- Without 2026 Production:       112,643
--
-- "Without production" means no matching records
-- in the analyzed view and date range, not
-- necessarily that the well is inactive.


-- =====================================================
-- 7. TOP 10 AMBIGUOUS POOLS WITH RECORDED PRODUCTION
-- =====================================================

WITH ActiveWells AS
(
    SELECT DISTINCT
        Current_Well_ID
    FROM dbo.vw_Well_Production_Records
    WHERE Current_Well_ID IS NOT NULL
      AND Production_Month >= '2026-01-01'
      AND Production_Month < '2026-09-01'
),
Wells AS
(
    SELECT
        Well_ID,
        MAX(NULLIF(TRIM(Field_Code), ''))
            AS Field_Code,
        MAX(NULLIF(TRIM(Pool_Deposit_Code), ''))
            AS Production_Pool_Code,
        MAX(NULLIF(TRIM(Pool_Deposit_Name), ''))
            AS Production_Pool_Name
    FROM dbo.Source_Well_Infrastructure
    WHERE Well_ID IS NOT NULL
    GROUP BY Well_ID
),
PoolMappings AS
(
    SELECT
        Field_Code,
        Production_Pool_Code,
        COUNT(
            DISTINCT NULLIF(TRIM(Geological_Pool_Code), '')
        ) AS Geological_Pool_Count
    FROM dbo.Ref_FieldPool_ST103
    GROUP BY
        Field_Code,
        Production_Pool_Code
)
SELECT TOP (10)
    w.Production_Pool_Code,
    w.Production_Pool_Name,
    COUNT(*) AS Producing_Wells
FROM Wells w
JOIN ActiveWells a
    ON w.Well_ID = a.Current_Well_ID
JOIN PoolMappings p
    ON w.Field_Code = p.Field_Code
   AND w.Production_Pool_Code = p.Production_Pool_Code
WHERE p.Geological_Pool_Count > 1
GROUP BY
    w.Production_Pool_Code,
    w.Production_Pool_Name
ORDER BY Producing_Wells DESC;

-- Confirmed result:
-- MFP9501: 51,326 wells
-- Top 10 combined: 69,760 wells


-- =====================================================
-- END OF VALIDATION SCRIPT
-- =====================================================

-- All expected results above were recorded during
-- the October 2026 investigation.
-- Future executions may differ if source data changes.
