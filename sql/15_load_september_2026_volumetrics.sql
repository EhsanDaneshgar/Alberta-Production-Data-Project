
/*
Alberta Oil & Gas Production Data Platform

Script 15: September 2026 Volumetrics Load
Database: AlbertaProductionDB

Source CSV:
    Vol_2026-09-AB.CSV

Source table:
    dbo.Source_Volumetrics_v2

Destination table:
    dbo.Clean_Volumetrics

HISTORICAL RESULTS — OCTOBER 2026

SSIS imported rows:            529,300
Blank row removed:                  1
Valid September source rows:   529,299
Rows inserted into Clean:      529,299
Total Clean rows Jan-Sep:     4,828,929

Validation completed:
- Source/Clean row counts matched.
- Oil, gas and water PROD counts and volumes matched.
- Blank and *** values converted to NULL.
- Numeric and date conversion errors: zero.
- Decimal precision differences: zero.
- Two-way 30-column EXCEPT differences: zero.

IMPORTANT:
September 2026 has ALREADY been loaded.
Do not execute this INSERT again against the working database.

The duplicate guard prevents a repeated load.
*/

USE AlbertaProductionDB;
GO

SET NOCOUNT ON;
SET XACT_ABORT ON;

BEGIN TRY
    BEGIN TRANSACTION;

    /* 1. Prevent duplicate September import */

    IF EXISTS (
        SELECT 1
        FROM dbo.Clean_Volumetrics WITH (UPDLOCK, HOLDLOCK)
        WHERE Production_Month = '2026-09-01'
    )
    BEGIN
        THROW 50001,
            'September already exists in Clean_Volumetrics.', 1;
    END;

    /* 2. Validate September source count */

    DECLARE @Source_Rows INT;

    SELECT @Source_Rows = COUNT(*)
    FROM dbo.Source_Volumetrics_v2
    WHERE TRIM(ProductionMonth) = '2026-09';

    IF @Source_Rows <> 529299
    BEGIN
        THROW 50002,
            'Unexpected September source row count.', 1;
    END;

    /* 3. Insert typed September data */

    INSERT INTO dbo.Clean_Volumetrics
    (
        Production_Month,
        Operator_BAID,
        Operator_Name,
        Reporting_Facility_ID,
        Reporting_Facility_Province_State,
        Reporting_Facility_Type,
        Reporting_Facility_Identifier,
        Reporting_Facility_Name,
        Reporting_Facility_Sub_Type,
        Reporting_Facility_Sub_Type_Desc,
        Reporting_Facility_Location,
        Facility_Legal_Subdivision,
        Facility_Section,
        Facility_Township,
        Facility_Range,
        Facility_Meridian,
        Submission_Date,
        Activity_ID,
        Product_ID,
        From_To_ID,
        From_To_ID_Province_State,
        From_To_ID_Type,
        From_To_ID_Identifier,
        Volume,
        Energy,
        Hours,
        CCI_Code,
        Proration_Product,
        Proration_Factor,
        Heat
    )
    SELECT
        TRY_CONVERT(date, TRIM(ProductionMonth) + '-01'),
        NULLIF(TRIM(OperatorBAID), ''),
        NULLIF(TRIM(OperatorName), ''),
        NULLIF(TRIM(ReportingFacilityID), ''),
        NULLIF(TRIM(ReportingFacilityProvinceState), ''),
        NULLIF(TRIM(ReportingFacilityType), ''),
        NULLIF(TRIM(ReportingFacilityIdentifier), ''),
        NULLIF(TRIM(ReportingFacilityName), ''),
        NULLIF(TRIM(ReportingFacilitySubType), ''),
        NULLIF(TRIM(ReportingFacilitySubTypeDesc), ''),
        NULLIF(TRIM(ReportingFacilityLocation), ''),
        NULLIF(TRIM(FacilityLegalSubdivision), ''),
        NULLIF(TRIM(FacilitySection), ''),
        NULLIF(TRIM(FacilityTownship), ''),
        NULLIF(TRIM(FacilityRange), ''),
        NULLIF(TRIM(FacilityMeridian), ''),
        TRY_CONVERT(
            datetime2(7),
            NULLIF(TRIM(SubmissionDate), '')
        ),
        NULLIF(TRIM(ActivityID), ''),
        NULLIF(TRIM(ProductID), ''),
        NULLIF(TRIM(FromToID), ''),
        NULLIF(TRIM(FromToIDProvinceState), ''),
        NULLIF(TRIM(FromToIDType), ''),
        NULLIF(TRIM(FromToIDIdentifier), ''),
        TRY_CONVERT(
            decimal(28,8),
            NULLIF(NULLIF(TRIM(Volume), ''), '***')
        ),
        TRY_CONVERT(
            decimal(28,8),
            NULLIF(NULLIF(TRIM(Energy), ''), '***')
        ),
        TRY_CONVERT(
            decimal(28,8),
            NULLIF(NULLIF(TRIM(Hours), ''), '***')
        ),
        NULLIF(TRIM(CCICode), ''),
        NULLIF(TRIM(ProrationProduct), ''),
        TRY_CONVERT(
            decimal(28,8),
            NULLIF(NULLIF(TRIM(ProrationFactor), ''), '***')
        ),
        TRY_CONVERT(
            decimal(28,8),
            NULLIF(NULLIF(TRIM(Heat), ''), '***')
        )
    FROM dbo.Source_Volumetrics_v2
    WHERE TRIM(ProductionMonth) = '2026-09';

    /* 4. Verify inserted row count */

    DECLARE @Inserted_Rows INT = @@ROWCOUNT;

    IF @Inserted_Rows <> 529299
    BEGIN
        THROW 50003,
            'Unexpected inserted row count. Rolling back.', 1;
    END;

    COMMIT TRANSACTION;

    SELECT
        @Source_Rows AS Source_Rows,
        @Inserted_Rows AS Inserted_Rows;

END TRY
BEGIN CATCH

    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    THROW;

END CATCH;
GO


/* 5. Validate September row count */

SELECT
    COUNT(*) AS September_Clean_Rows
FROM dbo.Clean_Volumetrics
WHERE Production_Month = '2026-09-01';
GO


/* 6. Validate total Clean row count */

SELECT
    COUNT(*) AS Total_Clean_Rows
FROM dbo.Clean_Volumetrics;
GO


/* 7. Compare oil, gas and water volumes */

SELECT
    'Source' AS Table_Name,
    ProductID AS Product,
    COUNT(*) AS Row_Count,
    SUM(TRY_CONVERT(decimal(28,8), Volume))
        AS Total_Volume
FROM dbo.Source_Volumetrics_v2
WHERE ProductionMonth = '2026-09'
  AND ActivityID = 'PROD'
  AND ProductID IN ('OIL', 'GAS', 'WATER')
GROUP BY ProductID

UNION ALL

SELECT
    'Clean',
    Product_ID,
    COUNT(*),
    SUM(Volume)
FROM dbo.Clean_Volumetrics
WHERE Production_Month = '2026-09-01'
  AND Activity_ID = 'PROD'
  AND Product_ID IN ('OIL', 'GAS', 'WATER')
GROUP BY Product_ID

ORDER BY Product, Table_Name;
GO


/* 8. Expected validated production results

GAS:
    134,141 rows
    11,502,196.4 volume

OIL:
    42,757 rows
    12,547,794.6 volume

WATER:
    62,744 rows
    53,073,338.1 volume

Source and Clean results were identical.

Volume:
    22,717 blank values
    13 *** markers
    22,730 Clean NULL values

Hours:
    380,868 blank values
    2,320 *** markers
    383,188 Clean NULL values

All five numeric columns:
    Zero unexpected conversion errors.
    Zero precision differences.

All 30 columns:
    Zero differences in both EXCEPT directions.
    Duplicate multiplicities were not separately checked.
*/
