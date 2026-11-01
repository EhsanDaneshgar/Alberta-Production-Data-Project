# Monthly Volumetrics Load Log

**Database:** `AlbertaProductionDB`  
**Source table:** `dbo.Source_Volumetrics_v2`  
**Clean table:** `dbo.Clean_Volumetrics`  
**Period:** January–September 2026  
**Last updated:** October 31, 2026

## 1. Monthly Clean Volumetrics Summary

January–August counts were verified in SSMS on October 2, 2026. September was imported and validated on October 31, 2026.

These figures represent actual records in `dbo.Clean_Volumetrics`, not independent row counts from the original CSV files.

| Production Month | Clean Rows |
| --- | ---: |
| 2026-01 | 550,662 |
| 2026-02 | 544,078 |
| 2026-03 | 548,951 |
| 2026-04 | 534,220 |
| 2026-05 | 534,448 |
| 2026-06 | 526,049 |
| 2026-07 | 531,919 |
| 2026-08 | 529,303 |
| 2026-09 | 529,299 |
| **Total** | **4,828,929** |

**Current coverage:** January–September 2026 (9 months).

## 2. Recorded Import and Cleanup History

The following information is based on recorded SQL Server Import and Export Wizard results, SSMS queries, and previous project conversations.

An imported row count can include an extra blank row. Therefore, imported rows and valid monthly records are reported separately where evidence is available.

| Month | Source CSV | Recorded Import and Cleanup |
| --- | --- | --- |
| January | `Vol_2026-01-AB.CSV` | 550,663 rows imported to `dbo.Source_Volumetrics_v2`; one blank row deleted; 550,662 valid source rows. |
| February | `Vol_2026-02-AB.CSV` | 544,079 rows imported to `dbo.Source_Volumetrics_v2`; one blank row deleted; 544,078 valid source rows. |
| March | `Vol_2026-03-AB.CSV` | 548,952 rows imported to `dbo.Source_Volumetrics_v2`; one blank row deleted; 548,951 valid source rows. |
| April | `Vol_2026-04-AB.CSV` | 534,220 valid rows counted in `dbo.Source_Volumetrics_v2`; import report and blank-row deletion were not recorded in the reviewed conversation. |
| May | `Vol_2026-05-AB.CSV` | Earlier import into `dbo.Source_Volumetrics` transferred 534,449 rows, including one blank-month row; 534,448 valid records. Later `_v2` count was 534,448; the `_v2` import and cleanup steps were not recorded. |
| June | `Vol_2026-06-AB.CSV` | Earlier import into `dbo.Source_Volumetrics` transferred 526,050 rows, including one blank-month row; 526,049 valid records. Later `_v2` count was 526,049; the `_v2` import and cleanup steps were not recorded. |
| July | `Vol_2026-07-AB.CSV` | 531,919 valid source rows counted in `dbo.Source_Volumetrics_v2`; import report and blank-row deletion were not recorded in the reviewed conversation. |
| August | `Vol_2026-08-AB.CSV` | 529,304 rows imported into `dbo.Source_Volumetrics_v2`; one blank row deleted; 529,303 valid rows inserted into `dbo.Clean_Volumetrics`. |
| September | `Vol_2026-09-AB.CSV` | 529,300 rows transferred by SSIS into `dbo.Source_Volumetrics_v2`; one blank row deleted; 529,299 valid rows inserted into `dbo.Clean_Volumetrics`. |

### Historical Load Notes

For January and February, the original conversations document the 30-column SQL transformation from `dbo.Source_Volumetrics_v2` into `dbo.Clean_Volumetrics`.

Both months were checked for matching Source/Clean row counts and `PROD`/`OIL` volume totals:

- January: 12,624,495 m³
- February: 11,502,173 m³

The exact March–July clean-table loading statements were not recorded in the reviewed conversations. However, the October 2 SSMS validation confirmed their presence in `dbo.Clean_Volumetrics`.

An additional June test import into `dbo.Test_Volumetrics_June` transferred 526,050 rows, including one blank row. It identified 15 `Volume` and 2,233 `Hours` values containing `***`.

This was a separate test table, not an additional June load into `dbo.Clean_Volumetrics`.

## 3. August 2026 — Data Quality and Validation

**Source CSV:** `Vol_2026-08-AB.CSV`

| Metric | Result |
| --- | ---: |
| SSIS imported rows | 529,304 |
| Blank rows removed | 1 |
| Valid source rows | 529,303 |
| Clean rows inserted | 529,303 |
| Total Clean rows after August | 4,299,630 |

The August source contained:

- 13 `Volume` values marked `***`
- 2,273 `Hours` values marked `***`

These nonnumeric markers were converted to `NULL` during the typed load.

Checks reported no invalid `SubmissionDate`, `Energy`, `ProrationFactor`, or `Heat` values.

The final validation confirmed that both `dbo.Clean_Volumetrics` and `dbo.vw_Volumetrics_With_Current_Well_ID` contained 4,299,630 rows, with no row-count difference.

The exact original blank-row deletion command is not preserved in the historical record.

## 4. September 2026 — Import and Validation

**Source CSV:** `Vol_2026-09-AB.CSV`  
**Source table:** `dbo.Source_Volumetrics_v2`  
**Destination table:** `dbo.Clean_Volumetrics`  
**Validation date:** October 31, 2026

### 4.1 SSIS Import Results

The SQL Server Import and Export Wizard successfully appended September data to the existing Source table.

| Metric | Result |
| --- | ---: |
| Data rows processed by SSIS | 529,301 |
| Rows transferred to Source | 529,300 |
| Blank rows identified and deleted | 1 |
| Valid September source rows | 529,299 |
| Rows inserted into Clean | 529,299 |
| Total Clean rows, January–September | 4,828,929 |

The SSIS package completed successfully.

A warning about unavailable Data Flow performance counters did not prevent the import.

September was not previously present in `dbo.Clean_Volumetrics`. A duplicate-month check confirmed zero September records before the INSERT operation.

The September load used a transaction, a source row-count check, and a post-INSERT row-count check to prevent an incorrect or duplicate load.

### 4.2 Source and Clean Production Validation

The following values were independently calculated from Source and Clean using:

- `ActivityID = 'PROD'`
- `ProductID IN ('OIL', 'GAS', 'WATER')`

| Product | Source Rows | Clean Rows | Source Volume | Clean Volume |
| --- | ---: | ---: | ---: | ---: |
| GAS | 134,141 | 134,141 | 11,502,196.4 | 11,502,196.4 |
| OIL | 42,757 | 42,757 | 12,547,794.6 | 12,547,794.6 |
| WATER | 62,744 | 62,744 | 53,073,338.1 | 53,073,338.1 |

**Result:** All three products matched exactly for both record counts and total reported volumes.

These records are a subset of the 529,299 September rows. Volume units depend on the Petrinex product and reporting definitions.

### 4.3 Missing and Nonnumeric Values

During the transformation, blank numeric values and `***` markers were converted to SQL `NULL`.

| Column | Blank in Source | `***` in Source | NULL in Clean |
| --- | ---: | ---: | ---: |
| Volume | 22,717 | 13 | 22,730 |
| Hours | 380,868 | 2,320 | 383,188 |

**Result:** The number of `NULL` values in Clean equaled the combined number of blank values and `***` markers in Source for both columns.

### 4.4 Numeric and Date Conversion Validation

All 529,299 September rows were examined for unexpected conversion failures in:

- `Volume`
- `Energy`
- `Hours`
- `ProrationFactor`
- `Heat`
- `SubmissionDate`

| Column | Unexpected Conversion Errors |
| --- | ---: |
| Volume | 0 |
| Energy | 0 |
| Hours | 0 |
| ProrationFactor | 0 |
| Heat | 0 |
| SubmissionDate | 0 |

**Result:** No unexpected conversion errors were detected.

### 4.5 Decimal Precision Validation

The five numeric columns were checked by comparing their conversion to `decimal(38,16)` against `decimal(28,8)`.

| Column | Precision Differences |
| --- | ---: |
| Volume | 0 |
| Energy | 0 |
| Hours | 0 |
| ProrationFactor | 0 |
| Heat | 0 |

**Result:** No precision differences were detected within the tested numeric precision.

### 4.6 Full 30-Column Comparison

A two-way SQL `EXCEPT` comparison was performed between:

1. The transformed September Source data, applying the same conversions used by the loading script.
2. The September records stored in `dbo.Clean_Volumetrics`.

All 30 columns were compared.

| Validation | Differences |
| --- | ---: |
| Source rows missing in Clean | 0 |
| Extra rows in Clean | 0 |

**Result:** No distinct row-value differences were detected across the 30 columns.

**Limitation:** SQL `EXCEPT` compares distinct row values and does not independently validate the multiplicity of completely identical duplicate rows. The overall Source and Clean row counts were equal, but a separate duplicate-multiplicity comparison was not performed.

### 4.7 September Final Status

**September 2026: Loaded and validated against the recorded checks.**

Confirmed:

- Source and Clean row counts matched.
- Oil, gas, and water production totals matched.
- Blank and `***` handling matched expectations.
- Numeric and date conversions had no unexpected failures.
- No numeric precision differences were detected.
- The two-way 30-column comparison reported zero differences.
- No duplicate September load was detected before insertion.

**SQL script:** [`sql/15_load_september_2026_volumetrics.sql`](../sql/15_load_september_2026_volumetrics.sql)

The September INSERT has already been executed successfully in the working database and must not be rerun.

## 5. Current Database Status and Next Steps

As of October 31, 2026:

| Metric | Result |
| --- | ---: |
| Production months loaded | 9 |
| Period covered | January–September 2026 |
| Total Clean Volumetrics rows | 4,828,929 |
| Latest validated production month | September 2026 |

### Remaining Work

1. Verify the multiplicities of completely identical September rows if exact multiset equivalence is required.
2. Revalidate downstream production/well-matching views against the expanded January–September dataset.
3. Continue integrating AER geological and well infrastructure data to support Geological Pool / Reservoir identification.
4. Document subsequent monthly imports using the same source-to-clean validation process.

This log records only work that was confirmed through project conversations, SQL execution results, and documented validation outputs. Missing historical execution details are not reconstructed or assumed.
