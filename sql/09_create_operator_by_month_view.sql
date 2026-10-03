USE AlbertaProductionDB;
GO

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Preserve the operator name reported for each production month.
-- Three BAIDs have different names across months, but each BAID
-- has only one name within a given month.
-- Validated 2026-10-03: 3,533 BAID-month rows.
CREATE OR ALTER VIEW dbo.vw_Operator_By_Month
AS
SELECT DISTINCT
    Production_Month,
    Operator_BAID,
    Operator_Name
FROM dbo.Clean_Volumetrics
WHERE Operator_BAID IS NOT NULL;
GO
