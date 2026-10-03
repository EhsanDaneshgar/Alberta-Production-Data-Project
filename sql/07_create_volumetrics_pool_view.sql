USE AlbertaProductionDB;
GO

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Keep one row per Well_ID so the join does not duplicate production rows.
-- Validation found no Well_ID with conflicting nonblank pool codes or names.
CREATE OR ALTER VIEW dbo.vw_Volumetrics_With_Pool
AS
WITH Pool_By_Well AS
(
    SELECT
        Well_ID,
        MAX(NULLIF(TRIM(Pool_Deposit_Code), '')) AS Pool_Deposit_Code,
        MAX(NULLIF(TRIM(Pool_Deposit_Name), '')) AS Pool_Deposit_Name
    FROM dbo.Source_Well_Infrastructure
    GROUP BY Well_ID
)
SELECT
    v.*,
    p.Pool_Deposit_Code,
    p.Pool_Deposit_Name
FROM dbo.vw_Volumetrics_With_Current_Well_ID AS v
LEFT JOIN Pool_By_Well AS p
    ON v.Current_Well_ID = p.Well_ID;
GO
