# Alberta Production Data Project

A SQL Server data engineering and analytics portfolio project using Alberta Petrinex production data, well infrastructure information, and AER/AGS geological reference datasets.

**Last updated:** October 31, 2026

## Project Goal

The goal is to build a reliable database that can be used to analyze Alberta oil and gas production by:

- Well
- Production month
- Product type
- Operator
- Reporting facility
- Field and geographical area
- Production Pool and Geological Pool (Reservoir)
- Geological formation
- Completion and perforation intervals
- Recovery mechanism
- Well configuration

A major ongoing objective is to identify the **actual producing Geological Pool or Reservoir associated with each well**, distinguishing confirmed production evidence from potential geological associations.

The database is intended to support SQL analysis, Python-based data integration, and Power BI reporting.

## Data Sources

The project currently uses:

1. **Petrinex** — Alberta monthly conventional volumetric CSV files.
2. **Alberta Well Infrastructure** — Well identification, location, licence, and operational information.
3. **AER ST103** — Field, Production Pool, and Geological Pool reference relationships (`FieldPoolList.xlsx`).
4. **Alberta Geological Survey (AGS)** — Atlas Structure Tops, Upper Isopachs, and Lower Isopachs.
5. **AER DE/SD Commingling List** — Well and production-string commingling information.

AER General Well Data is also being investigated as a source for licence details, production strings, completion/perforation records, and geological information.

The raw source files are not stored in this repository because of their size and source-management requirements. This repository contains SQL scripts, Python code, documentation, and validation methods.

## Technology

- Microsoft SQL Server
- SQL Server Management Studio (SSMS)
- T-SQL
- Python
- Power BI
- GitHub

## Database

**Database name:** `AlbertaProductionDB`

## Current Database Objects

### 1. Clean Volumetrics

**Table:** `dbo.Clean_Volumetrics`

This table contains cleaned and typed monthly volumetric records.

**Current status:**

- **4,828,929 records**
- **January–September 2026**
- Nine production months
- Production month converted to SQL `date`
- Numeric values converted to appropriate numeric types
- Duplicate-month checks applied before inserting monthly data

Monthly CSV files are imported into `dbo.Source_Volumetrics_v2` before being transferred to `dbo.Clean_Volumetrics`.

The latest completed load was **September 2026**, validated on October 31, 2026.

| Metric | September 2026 |
| --- | ---: |
| Rows imported through SSIS | 529,300 |
| Blank rows removed | 1 |
| Valid source rows | 529,299 |
| Clean rows inserted | 529,299 |
| Total Clean rows after September | 4,828,929 |

September validation included:

- Source/Clean row-count reconciliation
- Oil, gas, and water volume comparisons
- Blank and `***` handling
- Numeric and date conversion checks
- Decimal precision checks
- Two-way comparison of all 30 columns using SQL `EXCEPT`

All completed checks passed. Duplicate-row multiplicities were not independently verified.

**Documentation:**

- [Monthly volumetrics load log](docs/monthly-volumetrics-load-log.md)
- [September 2026 load script](sql/15_load_september_2026_volumetrics.sql)

### 2. Well Infrastructure Staging

**Table:** `dbo.Staging_Well_Infrastructure`

This table was used to import the original well-infrastructure data as text before conversion and validation.

### 3. Well Infrastructure

**Table:** `dbo.Source_Well_Infrastructure`

Previously validated status:

- 678,922 rows
- 72 columns
- 665,307 distinct Well IDs

Available attributes include:

- Current and previous Well IDs
- Well name
- Licence number
- Licensee
- Field and area
- Pool or deposit
- Well status
- Spud and drilling dates
- Final total depth
- Maximum true vertical depth
- Horizontal-drill indicator
- Recovery mechanism
- Licence status
- Orphan-well indicator

### 4. Well ID Matching

**View:** `dbo.vw_Volumetrics_With_Current_Well_ID`

This view:

- Preserves the original volumetric records
- Matches current Well IDs where possible
- Uses previous Well IDs when a unique relationship is available
- Provides a standardized current Well ID
- Identifies how each record was matched

The October 2, 2026 validation confirmed:

| Object | Rows |
| --- | ---: |
| `dbo.Clean_Volumetrics` | 4,299,630 |
| `dbo.vw_Volumetrics_With_Current_Well_ID` | 4,299,630 |
| Difference | 0 |

These results cover January–August 2026.

**Pending:** Revalidate the matching view after adding September 2026.

Well-ID matching is not guaranteed for every record. Some volumetric records describe facilities rather than individual wells, and some well-event relationships require additional investigation.

### 5. AER ST103 Geological Pool Reference

**Table:** `dbo.Ref_FieldPool_ST103`

The AER ST103 `FieldPoolList.xlsx` reference was imported on October 18, 2026.

**Imported rows:** 68,515

Previously validated reference statistics:

- 899 distinct Field Codes
- 12,057 distinct nonblank Geological Pool Codes
- 55,288 Field + Production Pool combinations
- 49,845 combinations with one Geological Pool
- 4,458 combinations with multiple Geological Pools
- 985 combinations without a Geological Pool Code

The initial mapping against 665,307 distinct Well IDs produced:

| Geological Pool Mapping Result | Wells |
| --- | ---: |
| Unique Geological Pool candidate | 138,512 |
| Multiple Geological Pool candidates | 192,909 |
| Missing Field or Production Pool | 322,694 |
| ST103 match without Geological Pool Code | 8,222 |
| No matching ST103 combination | 2,970 |
| **Total** | **665,307** |

Of the 192,909 wells with ambiguous reference mappings, 80,266 had January–August production records in `dbo.vw_Well_Production_Records`.

The largest commingled reporting group, `COMMINGLED MFP9501`, accounted for 51,326 of these wells.

**Important interpretation limitation:**

A unique ST103 reference mapping does not independently establish the well's actual producing reservoir.

Likewise, multiple Geological Pool candidates must not be treated as confirmed simultaneous production from multiple reservoirs.

Directly joining multiple candidates to production rows could duplicate reported volumes.

**Related documentation:**

- [ST103 geological pool mapping findings](docs/st103-geological-pool-mapping.md)
- [Create ST103 reference table](sql/11_create_ref_fieldpool_st103.sql)
- [ST103 validation SQL](sql/12_validate_st103_geological_pool_mapping.sql)

### 6. AER/AGS Geological Reference Tables

Five additional tables were created and populated in October 2026.

| Table | Rows |
| --- | ---: |
| `dbo.AGS_Atlas_Upper_Isopachs` | 14,628 |
| `dbo.AGS_Atlas_Lower_Isopachs` | 9,970 |
| `dbo.AGS_Atlas_Structure_Tops` | 16,086 |
| `dbo.AGS_Atlas_Data_Dictionary` | 98 |
| `dbo.AER_SDDE_Commingling` | 14,832 |
| **Total** | **55,614** |

The original AGS datasets were:

- `RISO1.hxd` — Upper Isopachs
- `RISO2.hxd` — Lower Isopachs
- `RSTRC.hxd` — Structure Tops

These files were prepared as SQL-compatible CSV datasets before import.

Two additional views were created:

- `dbo.vw_Well_Infrastructure_SortUWI`
- `dbo.vw_AGS_Atlas_Well_Keys`

#### Commingling Identifier Matching

A trailing `CHAR(13)` character was discovered in the `Sort_UWI` column following CSV import.

After removing the character:

| Result | Records |
| --- | ---: |
| Total Commingling records | 14,832 |
| Matched to well infrastructure | 14,831 |
| Unmatched | 1 |

**Matching rate:** approximately 99.993%.

The one unmatched identifier was:

`0575223406020` — SUNDANCE, DE2

Other well events were found at the same general location, but no exact match was confirmed. The record remains unmatched.

#### AGS Atlas Identifier Matching

The first matching test used 13-digit `Sort_UWI` identifiers.

For Upper Isopachs:

| Result | Records |
| --- | ---: |
| Total rows | 14,628 |
| Matched rows | 9,733 |
| Not matched by this method | 4,895 |

Alternative identifier formats and the matching results for the remaining Atlas datasets require further investigation.

**Related files:**

- [Create AER/AGS reference tables and views](sql/13_create_aer_ags_reference_tables.sql)
- [Import, cleanup and validation SQL](sql/14_import_aer_ags_reference_data.sql)
- [AER/AGS loading and matching findings](docs/aer-ags-five-table-load-and-matching.md)

## AER General Well Data Investigation

The AER General Well Data Tableau report was used to investigate selected wells.

[Open AER General Well Identifier Search](https://www2.aer.ca/t/Production/views/PRD_0100_General_Well_Identifier_Search/WellIdentifierSearch)

The report supports investigation of:

- Well identifiers and licence information
- Licence purpose and target formation
- Production Strings
- Production Pools
- Completion and perforation/treatment information
- Available geological information

### Representative Commingled Well

**Licence Number:** `0524255`

**Field:** PROGRESS

**Production Pool:** `0800860` — COMMINGLED POOL 008

The ST103 reference identifies two Geological Pool candidates:

| Geological Pool | Code |
| --- | --- |
| CHARLIE LAKE AA | 0508027 |
| HALFWAY B | 0516002 |

The licence purpose references production from **Charlie Lake Formation**.

The General Well Data investigation also identified completion and treatment information, but the Geological Tops & Markers section was empty.

The available evidence supports Charlie Lake as a candidate target formation. However, the actual producing Geological Pool or Pools remain unconfirmed.

## Python Geological Investigation

An initial Python workflow was developed to parse AER General Well Data sample records and investigate potential overlaps between geological formation markers and completion/perforation intervals.

**Existing script:**

- [aer_match_formations.py](python/aer_match_formations.py)

**Technical documentation:**

- [AER General Well Data sample investigation](docs/aer-general-well-data-sample-investigation.md)
- [Python formation-matching validation](docs/aer-formation-matching-python-validation.md)

## AER Tableau Pilot: Reservoir and Formation Identification

In October 2026 a pilot extracted well-level data from the free AER General Well Data Tableau reports and matched it to ST103 candidate Geological Pools.

The per-well report sheets (production strings, completion intervals, perforations/treatments, geological tops, licence details, status history, plugbacks) are downloaded as CSV using Tableau's standard `.csv` view export. The reports are keyed by the wellbore UWI (event `/0`).

**Method:** use the current production string's completion interval, find the formation tops it falls in (producing formation), then match those formations to ST103 candidate pool names (Geological Pool).

**Pilot results (10 conventional wells):**

- Producing formation identified for 10 of 10 wells.
- Geological Pool narrowed to a specific pool for 8 of 10 wells (HERRONTON / MFP9501: 44 candidates → 1).
- 2 wells remain formation-only, because their candidate pools are in the same formation and are separated by map area, not depth.
- Licence purpose text was misleading for one well, so it is treated as weak evidence.

Results are evidence-based estimates with a confidence level (STRONG, PROBABLE, FORMATION_ONLY, UNRESOLVED), not AER-confirmed assignments. Depth reference compatibility (MD/TVD) is not yet verified.

**Scripts and files:**

- [aer_well_extract_v2.py](python/aer_well_extract_v2.py): download AER report sheets for a list of wells
- [aer_reservoir_formation_match_v1.py](python/aer_reservoir_formation_match_v1.py): estimate producing formation(s) and Geological Pool(s)
- [formation_to_pool_keywords_v1.csv](reference/formation_to_pool_keywords_v1.csv): draft formation-to-pool-name lookup
- [Pilot well selection SQL](sql/16_select_pilot_wells_and_st103_candidates.sql)
- [Pilot documentation](docs/aer-tableau-pilot-reservoir-formation-identification.md)
- [Pilot results CSV](docs/pilot-reservoir-formation-results-2026-10-31.csv)

AER content may be reused with attribution; commercial redistribution requires AER written permission.

## Data Quality Principles

The project follows these principles:

- Preserve original source information.
- Maintain typed, validated analytical tables.
- Prevent duplicate monthly data loads.
- Verify row counts and numerical transformations.
- Investigate anomalous records rather than deleting them automatically.
- Preserve leading zeros in field, pool, and well identifiers.
- Distinguish physical wells, well events, and production strings.
- Treat Geological Pool mappings as candidates until supported by well-specific evidence.
- Preserve reported production volumes when joining geological data.
- Document assumptions, uncertainty, and source provenance.

## Current Limitations

- Many wells do not have a confirmed producing Geological Pool assignment.
- Some Production Pools map to many potential Geological Pools.
- Some well records lack sufficient Field/Pool information.
- AGS Atlas data covers only a subset of the infrastructure dataset.
- Completion, perforation, and geological-top information has been tested on a 10-well pilot only.
- AER Tableau extraction is automated but slow (about 1 minute per well).
- Geological tops are missing for some wells; depth reference (MD/TVD) is not yet verified.
- Pools in the same formation (for example Bow Island A–D) cannot be separated by depth alone.
- The well matching view has not yet been revalidated for January–September 2026.
- Detailed artificial-lift, injection, and working-interest information is not yet comprehensively modeled.

## Next Steps

1. **Formation-to-pool lookup:** review and extend the keyword table.
2. **Larger test:** run extraction and matching on about 100 wells across the main ambiguous pools, including MFP9501.
3. **Spatial method:** resolve formation-only cases (pool letter by location).
4. **SQL design:** propose well-to-Geological-Pool and well-to-Formation result tables (many-to-many, with evidence and confidence). To be approved before creation.
5. **Depth reference:** check MD vs TVD, especially for horizontal wells.
6. **Production validation:** revalidate downstream well-matching views after the September 2026 load.
7. **Power BI:** develop validated production analytics and dashboards.
8. **Future monthly updates:** continue importing and validating Petrinex production data.

## Planned Analysis

The final analytical model should support questions such as:

- How much oil, gas, and water does each well produce by month?
- Which operators are responsible for specific wells?
- Which Field and Production Pool are associated with reported volumes?
- Which Geological Pool or Reservoir is supported by well-specific evidence?
- Which wells are horizontal?
- How do production rates and water cuts evolve?
- Which wells or operators contribute the largest share of production?
- How do production characteristics vary by location, formation, and reservoir?

## Repository Structure

```text
Alberta-Production-Data-Project/
├── README.md
├── docs/
│   ├── monthly-volumetrics-load-log.md
│   ├── st103-geological-pool-mapping.md
│   ├── aer-ags-five-table-load-and-matching.md
│   ├── aer-general-well-data-sample-investigation.md
│   ├── aer-formation-matching-python-validation.md
│   ├── aer-tableau-pilot-reservoir-formation-identification.md
│   └── pilot-reservoir-formation-results-2026-10-31.csv
├── python/
│   ├── aer_match_formations.py
│   ├── aer_well_extract_v2.py
│   └── aer_reservoir_formation_match_v1.py
├── reference/
│   └── formation_to_pool_keywords_v1.csv
└── sql/
    ├── README.md
    ├── 01_create_clean_volumetrics_table.sql
    ├── ... existing SQL files 02 through 10
    ├── 11_create_ref_fieldpool_st103.sql
    ├── 12_validate_st103_geological_pool_mapping.sql
    ├── 13_create_aer_ags_reference_tables.sql
    ├── 14_import_aer_ags_reference_data.sql
    ├── 15_load_september_2026_volumetrics.sql
    └── 16_select_pilot_wells_and_st103_candidates.sql
```

The original AER/Petrinex and AGS source datasets are not stored in this GitHub repository. The Python scripts write CSV files only and do not modify the working SQL Server database.

## Author

Ehsan Daneshgar  
Calgary, Alberta, Canada
