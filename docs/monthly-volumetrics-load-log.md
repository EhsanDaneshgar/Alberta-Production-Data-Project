# Monthly volumetrics load log

Database: `AlbertaProductionDB`  
Table checked: `dbo.Clean_Volumetrics`  
Period: January–August 2026

The following counts were verified in SSMS on October 2, 2026 by grouping
`dbo.Clean_Volumetrics.Production_Month`. These are counts in the cleaned table,
not independent row counts from the original CSV files.

| Production month | Clean rows |
| --- | ---: |
| 2026-01 | 550,662 |
| 2026-02 | 544,078 |
| 2026-03 | 548,951 |
| 2026-04 | 534,220 |
| 2026-05 | 534,448 |
| 2026-06 | 526,049 |
| 2026-07 | 531,919 |
| 2026-08 | 529,303 |
| **Total** | **4,299,630** |

## Recorded import and cleanup history

The older conversations document the following steps. An imported row count
can include an extra blank row, so it is kept separate from the valid source
and clean-table counts above.

| Month | Recorded CSV | Recorded import and cleanup |
| --- | --- | --- |
| January | `Vol_2026-01-AB.CSV` | 550,663 rows imported to `dbo.Source_Volumetrics_v2`; one blank row deleted; 550,662 valid source rows. |
| February | `Vol_2026-02-AB.CSV` | 544,079 rows imported to `dbo.Source_Volumetrics_v2`; one blank row deleted; 544,078 valid source rows. |
| March | `Vol_2026-03-AB.CSV` | 548,952 rows imported to `dbo.Source_Volumetrics_v2`; one blank row deleted; 548,951 valid source rows. |
| April | `Vol_2026-04-AB.CSV` | 534,220 valid rows were counted in `dbo.Source_Volumetrics_v2`; the import report and blank-row deletion were not recorded in the reviewed room. |
| May | `Vol_2026-05-AB.CSV` | An earlier import into `dbo.Source_Volumetrics` wrote 534,449 rows, including one extra blank-month row; 534,448 valid May rows were counted. The later `dbo.Source_Volumetrics_v2` count was 534,448; the import and deletion steps for `_v2` were not recorded in the reviewed room. |
| June | `Vol_2026-06-AB.CSV` | An earlier import into `dbo.Source_Volumetrics` wrote 526,050 rows, including one extra blank-month row; 526,049 valid June rows were counted. The later `dbo.Source_Volumetrics_v2` count was 526,049; the import and deletion steps for `_v2` were not recorded in the reviewed room. |
| July | `Vol_2026-07-AB.CSV` | 531,919 valid rows were counted in `dbo.Source_Volumetrics_v2`; the import report and blank-row deletion were not recorded in the reviewed room. |
| August | `Vol_2026-08-AB.CSV` | 529,304 rows imported to `dbo.Source_Volumetrics_v2`; one blank row deleted; 529,303 valid rows inserted into `dbo.Clean_Volumetrics`. |

For January and February, the conversations record the 30-column SQL load
from `dbo.Source_Volumetrics_v2` to `dbo.Clean_Volumetrics`. Both months were
checked for matching source and clean row counts and matching `PROD`/`OIL`
volume sums: January 12,624,495 m³; February 11,502,173 m³. The March–July
clean-table load statements were not recorded in the reviewed rooms. The
October 2 SSMS check above confirms their final presence in the clean table;
it does not reconstruct the earlier SQL statements.

An additional June test import into `dbo.Test_Volumetrics_June` transferred
526,050 rows, with 526,049 valid month rows. That test found 15 `Volume`
and 2,233 `Hours` values containing `***`. This was a separate test table,
not a distinct June load into `dbo.Clean_Volumetrics`.

## August data quality and final checks

The August source had 13 `Volume` and 2,273 `Hours` values containing `***`;
the typed load converted them to `NULL`. Checks reported no invalid
`SubmissionDate`, `Energy`, `ProrationFactor`, or `Heat` values. The final
August clean count was 529,303, and both the clean table and
`dbo.vw_Volumetrics_With_Current_Well_ID` contained 4,299,630 rows, with
no row-count difference. The exact original blank-row deletion command
is not preserved here.
