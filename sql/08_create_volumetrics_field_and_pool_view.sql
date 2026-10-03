USE AlbertaProductionDB;
GO

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- One row per Well_ID prevents duplicate production rows.
-- Validation found no conflicting nonblank field codes or names
-- for the same Well_ID.
-- Validation on 2026-10-03:
-- 4,299,630 View rows; 2,823,495 with a field;
-- 2,232,850 with a pool.
CREATE OR ALTER VIEW dbo.vw_Volumetrics_With_Field_And_Pool
AS
WITH Field_By_Well AS
(
    SELECT
        Well_ID,
        MAX(NULLIF(TRIM(Field_Code), '')) AS Field_Code,
        MAX(NULLIF(TRIM(Field_Name), '')) AS Field_Name
    FROM dbo.Source_Well_Infrastructure
    GROUP BY Well_ID
)
SELECT
    p.*,
    f.Field_Code,
    f.Field_Name
FROM dbo.vw_Volumetrics_With_Pool AS p
LEFT JOIN Field_By_Well AS f
    ON p.Current_Well_ID = f.Well_ID;
GO
