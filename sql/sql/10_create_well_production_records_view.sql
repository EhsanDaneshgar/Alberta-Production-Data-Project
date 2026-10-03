USE AlbertaProductionDB;
GO

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Select reported well production for oil, gas, and water.
-- Preserve records even when a current well ID cannot be matched.
-- Validated 2026-10-03: 1,905,498 rows;
-- 31 rows without a matched Current_Well_ID.
CREATE OR ALTER VIEW dbo.vw_Well_Production_Records
AS
SELECT *
FROM dbo.vw_Volumetrics_With_Field_And_Pool
WHERE Activity_ID = 'PROD'
  AND From_To_ID_Type = 'WI'
  AND Product_ID IN ('OIL', 'GAS', 'WATER')
  AND Volume IS NOT NULL;
GO
