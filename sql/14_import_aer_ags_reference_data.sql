
/*
Alberta Oil & Gas Production Data Platform

Script 14: Import AER/AGS Reference Data
Database: AlbertaProductionDB

Purpose:
- Import five AER/AGS reference datasets.
- Remove trailing CHAR(13) from Commingling Sort_UWI.
- Validate imported row counts.

Historical import results: October 2026

Upper Isopachs:       14,628 rows
Lower Isopachs:        9,970 rows
Structure Tops:       16,086 rows
Atlas Data Dictionary:    98 rows
AER SDDE Commingling: 14,832 rows

IMPORTANT:
These datasets have already been imported into the
working database. This script is retained for
documentation and future database reconstruction.

Do not rerun the imports against populated tables.
*/

USE AlbertaProductionDB;
GO


/* =================================================
   1. AGS Atlas Upper Isopachs
   ================================================= */

IF NOT EXISTS (
    SELECT 1 FROM dbo.AGS_Atlas_Upper_Isopachs
)
BEGIN
    BULK INSERT dbo.AGS_Atlas_Upper_Isopachs
    FROM 'C:\Folder D\Data Projects\Alberta Production Data_2026\Alberta Energy Regulator\AGS\Atlas_Upper_Isopachs_ready.csv'
    WITH (
        FORMAT = 'CSV',
        FIRSTROW = 2,
        FIELDQUOTE = '"',
        CODEPAGE = '65001',
        ROWTERMINATOR = '0x0a',
        TABLOCK
    );
END;
GO


/* =================================================
   2. AGS Atlas Lower Isopachs
   ================================================= */

IF NOT EXISTS (
    SELECT 1 FROM dbo.AGS_Atlas_Lower_Isopachs
)
BEGIN
    BULK INSERT dbo.AGS_Atlas_Lower_Isopachs
    FROM 'C:\Folder D\Data Projects\Alberta Production Data_2026\Alberta Energy Regulator\AGS\Atlas_Lower_Isopachs_ready.csv'
    WITH (
        FORMAT = 'CSV',
        FIRSTROW = 2,
        FIELDQUOTE = '"',
        CODEPAGE = '65001',
        ROWTERMINATOR = '0x0a',
        TABLOCK
    );
END;
GO


/* =================================================
   3. AGS Atlas Structure Tops
   ================================================= */

IF NOT EXISTS (
    SELECT 1 FROM dbo.AGS_Atlas_Structure_Tops
)
BEGIN
    BULK INSERT dbo.AGS_Atlas_Structure_Tops
    FROM 'C:\Folder D\Data Projects\Alberta Production Data_2026\Alberta Energy Regulator\AGS\AGS_Structure_Tops_Import.csv'
    WITH (
        FORMAT = 'CSV',
        FIRSTROW = 2,
        FIELDQUOTE = '"',
        CODEPAGE = '65001',
        ROWTERMINATOR = '0x0a',
        TABLOCK
    );
END;
GO


/* =================================================
   4. AGS Atlas Data Dictionary
   ================================================= */

IF NOT EXISTS (
    SELECT 1 FROM dbo.AGS_Atlas_Data_Dictionary
)
BEGIN
    BULK INSERT dbo.AGS_Atlas_Data_Dictionary
    FROM 'C:\Folder D\Data Projects\Alberta Production Data_2026\Alberta Energy Regulator\AGS\Atlas_Data_Dictionary.csv'
    WITH (
        FORMAT = 'CSV',
        FIRSTROW = 2,
        FIELDQUOTE = '"',
        CODEPAGE = '65001',
        ROWTERMINATOR = '0x0a',
        TABLOCK
    );
END;
GO


/* =================================================
   5. AER SDDE Commingling
   ================================================= */

IF NOT EXISTS (
    SELECT 1 FROM dbo.AER_SDDE_Commingling
)
BEGIN
    BULK INSERT dbo.AER_SDDE_Commingling
    FROM 'C:\Folder D\Data Projects\Alberta Production Data_2026\Alberta Energy Regulator\AGS\SdDeWellListExport_for_SQL.csv'
    WITH (
        FORMAT = 'CSV',
        FIRSTROW = 2,
        FIELDQUOTE = '"',
        CODEPAGE = '65001',
        ROWTERMINATOR = '0x0a',
        TABLOCK
    );
END;
GO


/* =================================================
   6. Clean Commingling Well Identifiers

   The CSV import introduced trailing CHAR(13)
   into the Sort_UWI column.

   Historical correction: 14,832 rows.
   ================================================= */

UPDATE dbo.AER_SDDE_Commingling
SET Sort_UWI = REPLACE(Sort_UWI, CHAR(13), '')
WHERE CHARINDEX(CHAR(13), Sort_UWI) > 0;
GO


/* =================================================
   7. Validate Imported Row Counts
   ================================================= */

SELECT
    'AGS_Atlas_Upper_Isopachs' AS Table_Name,
    COUNT(*) AS Row_Count
FROM dbo.AGS_Atlas_Upper_Isopachs

UNION ALL

SELECT 'AGS_Atlas_Lower_Isopachs', COUNT(*)
FROM dbo.AGS_Atlas_Lower_Isopachs

UNION ALL

SELECT 'AGS_Atlas_Structure_Tops', COUNT(*)
FROM dbo.AGS_Atlas_Structure_Tops

UNION ALL

SELECT 'AGS_Atlas_Data_Dictionary', COUNT(*)
FROM dbo.AGS_Atlas_Data_Dictionary

UNION ALL

SELECT 'AER_SDDE_Commingling', COUNT(*)
FROM dbo.AER_SDDE_Commingling;
GO


/* =================================================
   8. Validate Commingling Well Matching

   Historical result:
   Total rows:     14,832
   Matched rows:   14,831
   Unmatched rows:      1

   Unmatched Sort_UWI: 0575223406020
   ================================================= */

WITH WellKeys AS
(
    SELECT DISTINCT Sort_UWI
    FROM dbo.vw_Well_Infrastructure_SortUWI
    WHERE Sort_UWI IS NOT NULL
)
SELECT
    COUNT(*) AS Total_Commingling_Rows,
    COUNT(W.Sort_UWI) AS Matched_Rows,
    COUNT(*) - COUNT(W.Sort_UWI) AS Unmatched_Rows
FROM dbo.AER_SDDE_Commingling AS C
LEFT JOIN WellKeys AS W
    ON C.Sort_UWI = W.Sort_UWI;
GO
