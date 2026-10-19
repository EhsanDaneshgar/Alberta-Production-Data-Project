# Alberta Production Data Project

A SQL Server data engineering and analytics portfolio project using Alberta Petrinex data to integrate monthly volumetric records with well infrastructure information.

## Project Goal

The goal is to build a reliable database that can be used to analyze Alberta oil and gas production by:

* Well
* Production month
* Product type
* Operator
* Reporting facility
* Field and geographical area
* Pool or deposit
* Recovery mechanism
* Well configuration

The final database will support SQL analysis and Power BI reporting. Additional geological and operational datasets may later be added for formation, reservoir, completion, artificial-lift, injection, and ownership analysis.

## Data Sources

The project currently uses:

* Petrinex monthly volumetric CSV files
* Alberta Well Infrastructure CSV file
* AER ST103 Field/Production Pool/Geological Pool reference data (`FieldPoolList.xlsx`)

The raw CSV files are not stored in this repository because of their size. This repository will contain the SQL scripts, documentation, validation queries, and reporting materials used in the project.

## Technology

* Microsoft SQL Server
* SQL Server Management Studio
* T-SQL
* Power BI
* GitHub

## Database

Database name:

`AlbertaProductionDB`

## Current Database Objects

### Clean Volumetrics Table

`dbo.Clean_Volumetrics`

This table contains cleaned and typed monthly volumetric records.

Current status:

* **4,299,630 rows** (verified October 2, 2026)
* **January through August 2026**
* Numeric values converted to appropriate numeric data types
* Production month converted to a date data type
* Duplicate-month checks used before inserting new data

Examples of available information include:

* Production month
* Operator
* Reporting facility
* Activity type
* Product
* Volume
* Energy
* Hours
* From and To facility identifiers

The [monthly volumetrics load log](docs/monthly-volumetrics-load-log.md) records verified monthly counts, import history, and known gaps in the original execution records.

### Well Infrastructure Staging Table

`dbo.Staging_Well_Infrastructure`

This table was used to import the original well-infrastructure CSV data as text before conversion and validation.

### Well Infrastructure Table

`dbo.Source_Well_Infrastructure`

This table contains cleaned and typed well-infrastructure information.

Current status:

* 678,922 rows
* 72 columns

Examples of available information include:

* Current well ID
* Previous well ID
* Well name
* Licence number
* Licensee name
* Linked facility
* Field
* Area
* Pool or deposit
* Well status
* Spud date
* Finished drilling date
* Final total depth
* Maximum true vertical depth
* Horizontal-drill indicator
* Recovery mechanism
* Licence status
* Orphan-well indicator

## Data Quality Work

The following validation work has been completed:

* Checked numeric columns before conversion
* Checked date columns before conversion
* Checked required fields for missing values
* Allowed `Spud_Date` to contain null values because some source records do not provide a spud date
* Investigated duplicate well IDs
* Investigated suspicious date values
* Reviewed records where maximum true vertical depth exceeded final total depth
* Checked monthly volumetric data before inserting additional months

No source values were automatically deleted simply because they appeared unusual. Suspicious values were investigated before deciding how they should be handled.

## Well ID Matching

Volumetric records use well identifiers that may represent either a current well ID or a previous well ID.

To support analysis, the following view was created:

`dbo.vw_Volumetrics_With_Current_Well_ID`

The view:

* Preserves the original volumetric records
* Matches the volumetric well ID directly to the current well ID when possible
* Uses the previous well ID when a unique current-ID match is available
* Adds a standardized current well ID
* Identifies the method used for each match

The October 2, 2026 validation confirmed that the matching view preserved the overall source row count:

| Object | Row Count |
| --- | ---: |
| `dbo.Clean_Volumetrics` | 4,299,630 |
| `dbo.vw_Volumetrics_With_Current_Well_ID` | 4,299,630 |
| Difference | 0 |

Well-ID matching is not guaranteed for every record. Some rows are not well-level reporting records, while other well-related rows require further matching checks. The older July-only matching breakdown has been removed because it did not describe the current January–August dataset.

### AER ST103 Geological Pool Reference

`dbo.Ref_FieldPool_ST103` was created and populated using the updated AER ST103 `FieldPoolList.xlsx` reference data. The SQL Server Import and Export Wizard transferred **68,515 data rows** on October 18, 2026.

Validation confirmed 899 distinct Field Codes and 12,057 distinct nonblank Geological Pool Codes. The reference contains **55,288 Field + Production Pool combinations**, of which 49,845 map to one Geological Pool, 4,458 map to multiple Geological Pools, and 985 have no Geological Pool Code.

Mapping this reference to the **665,307 distinct Well IDs** in the infrastructure data produced:

| Well-level reference mapping result | Wells |
| --- | ---: |
| Unique Geological Pool Code | 138,512 |
| Multiple candidate Geological Pools | 192,909 |
| Missing Field or Production Pool | 322,694 |
| Matched ST103 combination without a Geological Pool Code | 8,222 |
| No matching ST103 combination | 2,970 |
| **Total** | **665,307** |

Of the 192,909 wells with ambiguous reference mappings, **80,266** had corresponding January–August 2026 production records in `dbo.vw_Well_Production_Records`. The largest commingled reporting group, `COMMINGLED MFP9501`, accounted for **51,326** of these wells.

**Interpretation limit:** A unique ST103 reference mapping does not independently confirm a well's actual producing or injecting reservoir. Multiple candidate Geological Pools must not be treated as multiple confirmed producing pools, and joining them directly to production records would risk duplicating volumes.

Read more:
- [ST103 geological pool mapping findings](docs/st103-geological-pool-mapping.md)
- [Create ST103 reference table](sql/11_create_ref_fieldpool_st103.sql)
- [ST103 validation SQL](sql/12_validate_st103_geological_pool_mapping.sql)
- [AER General Well Data sample investigation and MD/TVD findings](docs/aer-general-well-data-sample-investigation.md)

## Important Data Findings

* A well ID is not always unique within the well-infrastructure data.
* Some physical wells have multiple well-event identifiers.
* A previous well ID may sometimes relate to more than one current well-event ID.
* Production records must therefore be matched carefully rather than joined blindly.
* Production activities can be reported from a well to a battery or injection facility.
* Missing values are not automatically data errors; their meaning depends on the activity and product type.

## Current Limitations

- ST103 provides *reference associations*, not confirmed well-level producing or injecting formations.
- Commingled reporting pools may have many candidate Geological Pools; the original production-record grain and reported volumes must be preserved.
- Many wells lack a Field or Production Pool Code needed for the current mapping.
- Completion and perforation intervals, geological tops, and formation assignments are not yet integrated at scale.
- AER General Well Data and IGDS have been identified as potential additional sources, but their well-level coverage and suitability are not yet validated.
- Hydraulic-fracturing details, artificial-lift method, detailed injection history, and working-interest data are not yet comprehensively modeled.

## Next Steps

1. Review the free AER General Well Data samples and record layouts before acquiring bulk files.
2. Assess programmatic matching of well identifiers and alignment of geological tops with completion and perforation intervals.
3. Test formation and reservoir identification on representative wells, including commingled cases, with provenance and uncertainty recorded.
4. Investigate injection wells separately and preserve source reporting volumes throughout any future geological joins.
5. Maintain reusable SQL validation queries and monthly data-loading documentation.
6. Build tested production analytics views and a Power BI reporting model.

## Planned Analysis

The completed model should support questions such as:

* How much oil, gas, and water did each well produce by month?
* Which operator is responsible for each well?
* Which field, area, pool, reservoir, or formation is associated with production?
* Which wells are horizontal?
* What recovery mechanism is recorded for each well?
* What are the production and water-cut trends?
* Which wells or operators contribute the largest share of production?
* How does production vary by geography, facility, field, and pool?

## Repository Structure

The repository currently contains a flat, numbered set of SQL scripts and project documentation:

```text
Alberta-Production-Data-Project/
├── README.md
├── docs/
│   ├── monthly-volumetrics-load-log.md
│   └── st103-geological-pool-mapping.md
└── sql/
    ├── README.md
    ├── 01_create_clean_volumetrics_table.sql
    ├── ... (other existing scripts, 02 through 10)
    ├── 11_create_ref_fieldpool_st103.sql
    └── 12_validate_st103_geological_pool_mapping.sql
```

The source CSV/XLSX datasets are not stored in this repository. SQL files document the schema and analysis logic; the live database and its data remain in SQL Server.

## Author

Ehsan Daneshgar
Calgary, Alberta
