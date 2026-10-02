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

## August import notes

The August import reported 529,304 rows, including one blank row. That blank
row was removed from `dbo.Source_Volumetrics_v2` before the 529,303 valid
August records were inserted into `dbo.Clean_Volumetrics`. The August source
included 13 `Volume` values and 2,273 `Hours` values containing `***`; the
typed load converted those markers to `NULL`. These details are the recorded
results of the completed August load. The exact original blank-row deletion
command is not preserved here.

The counts above verify the eight loaded months. They do not establish that
the earlier months used the identical SQL statement as August; their original
import and cleanup commands should be added only when available.
