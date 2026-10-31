# AER/AGS geological datasets — October 31, 2026

Database: `AlbertaProductionDB`

## Imported tables and reported row counts

| Table | Rows |
| --- | ---: |
| `dbo.AGS_Atlas_Upper_Isopachs` | 14,628 |
| `dbo.AGS_Atlas_Lower_Isopachs` | 9,970 |
| `dbo.AGS_Atlas_Structure_Tops` | 16,086 |
| `dbo.AGS_Atlas_Data_Dictionary` | 98 |
| `dbo.AER_SDDE_Commingling` | 14,832 |

These counts were reported in the October 31, 2026 project handoff. They are historical load results, not live GitHub/SQL Server verification.

## Existing SQL Server views

- `dbo.vw_Well_Infrastructure_SortUWI`
- `dbo.vw_AGS_Atlas_Well_Keys`

## Identifier cleanup and matching results

- Trailing `CHAR(13)` was removed from commingling identifiers.
- Following cleanup, 14,831 of 14,832 commingling records matched well infrastructure.
- The one unmatched record was `0575223406020`, SUNDANCE, DE2.
- 9,733 of 14,628 Upper Isopachs records matched well infrastructure via 13-digit `Sort_UWI`. Further matching remains outstanding.

## Import source and method

The prior working session used files named `Atlas_Upper_Isopachs.csv`, `Atlas_Lower_Isopachs.csv`, `Atlas_Structure_Tops.csv`, `Atlas_Data_Dictionary.csv`, and `SdDeWellListExport_for_SQL.csv`. The atlas import used SQL Server `BULK INSERT` with CSV format, header skipped (`FIRSTROW = 2`), UTF-8 code page 65001, and LF row terminator. These are recorded process details, not a complete reconstructed executable script.

## Reproducibility status

The original complete `CREATE TABLE`, `BULK INSERT`, cleaning and view-definition SQL has **not yet been committed** here. Preserve the original SQL from the prior working session rather than inventing column schemas, file paths, or import statements. In particular, the source data files and local bulk-import paths should not be mistaken for committed repository assets.

## Geological interpretation

Atlas geological markers, isopachs and structure tops provide supporting geological evidence, but matching a well identifier does not by itself establish its active producing reservoir. Keep any proposed formation assignment distinct from confirmed completion and production evidence.
