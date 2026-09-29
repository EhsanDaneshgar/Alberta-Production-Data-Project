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

* 3,770,327 rows
* January through July 2026
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

Matching results for well-related volumetric rows:

| Match Method            | Row Count |
| ----------------------- | --------: |
| Current Well ID         | 2,476,609 |
| Unique Previous Well ID |        68 |
| Unmatched               |         0 |

The view contains the same number of rows as the clean volumetrics table:

| Object                  | Row Count |
| ----------------------- | --------: |
| Clean volumetrics table | 3,770,327 |
| Well-ID matching view   | 3,770,327 |
| Difference              |         0 |

This confirms that the view did not remove or duplicate volumetric records.

## Important Data Findings

* A well ID is not always unique within the well-infrastructure data.
* Some physical wells have multiple well-event identifiers.
* A previous well ID may sometimes relate to more than one current well-event ID.
* Production records must therefore be matched carefully rather than joined blindly.
* Production activities can be reported from a well to a battery or injection facility.
* Missing values are not automatically data errors; their meaning depends on the activity and product type.

## Current Limitations

The database does not yet contain complete information for:

* Geological formation
* Reservoir
* Completion and perforation intervals
* Hydraulic-fracturing details
* Artificial-lift method
* Injection history
* Working-interest or ownership percentage

The existing well-infrastructure table contains field, area, pool/deposit, recovery mechanism, operator/licensee, and horizontal-drill information, but additional reference datasets are needed for more detailed geological and operational analysis.

## Next Steps

1. Save and organize the SQL scripts used to build the existing tables and view.
2. Create reusable data-quality and validation scripts.
3. Locate a reliable pool, deposit, reservoir, and formation reference dataset.
4. Inspect the reference file before designing any new SQL table.
5. Add geological reference tables when suitable source data is confirmed.
6. Build analytical SQL views for well-level monthly production.
7. Create a Power BI data model and dashboard.
8. Document findings, limitations, and business definitions.

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

The planned repository structure is:

```text
Alberta-Production-Data-Project/
├── README.md
├── sql/
│   ├── table-creation/
│   ├── data-loading/
│   ├── transformations/
│   ├── views/
│   └── validation/
├── docs/
│   ├── data-dictionary.md
│   ├── data-quality-log.md
│   └── project-decisions.md
├── powerbi/
└── screenshots/
```

## Author

Ehsan Daneshgar
Calgary, Alberta
