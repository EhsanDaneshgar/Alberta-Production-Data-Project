# AER ST103 — Geological Pool Mapping and Reservoir Identification

**Project:** Alberta Oil & Gas Production Data Platform  
**Database:** `AlbertaProductionDB`  
**Source:** Alberta Energy Regulator (AER) — ST103  
**Documentation date:** October 18, 2026  
**Status:** Reference data imported and initial mapping analysis completed. Well-level reservoir identification remains incomplete.

---

## 1. Objective

The objective is to enhance Alberta's monthly oil and gas production dataset by associating producing and injecting wells with their geological reservoirs (Geological Pools) and, eventually, their actual producing or injecting formations.

The existing SQL Server database already contains:

- Monthly Petrinex volumetric records (January–August 2026).
- Well infrastructure and identification information.
- Field codes and names.
- Production Pool/Deposit codes and names.
- Operator and reporting facility information.

However, Production Pool information does not always identify the individual geological reservoir from which a well produces.

This phase investigates whether AER ST103 reference data can bridge that information gap.

## 2. Important Geological Definitions

| Concept | Definition |
|---|---|
| Field | A geographically defined area associated with oil or gas accumulations |
| Formation | A recognizable and mappable geological rock unit |
| Geological Pool | A distinct natural hydrocarbon accumulation, generally corresponding to a reservoir |
| Production Pool | A designation used for regulatory production reporting, potentially associated with one or multiple Geological Pools |

A single Formation may contain multiple Geological Pools. A Geological Pool may also involve more than one Formation.

Production Pools and Geological Pools do not necessarily have a one-to-one relationship.

For commingled production, multiple geological reservoirs may be associated with the same Production Pool designation.

## 3. Data Sources

### 3.1 AER ST103

Six ST103 reference workbooks were obtained:

1. `FieldPoolList.xlsx`
2. `CommingledPoolList.xlsx`
3. `MultiFieldPools.xlsx`
4. `FieldList.xlsx`
5. `FormationCodes_AlphaSort.xlsx`
6. `FormationCodes_NumericSort.xlsx`

The primary source used in this phase was `FieldPoolList.xlsx`.

### 3.2 FieldPoolList structure

The workbook contains seven columns:

| Column | Description |
|---|---|
| Field Name | AER field name |
| Production Pool Name | Regulatory Production Pool name |
| Field Code | Field identifier |
| Production Pool Code | Production Pool identifier |
| Geological Pool Code | Geological Pool identifier |
| Geological Pool Name | Geological Pool name |
| Confidential | Source confidentiality indicator |

The updated file contained **68,515 data records**.

A SQL-ready CSV was prepared to preserve the original identifier structure, including leading zeros.

## 4. SQL Server Implementation

### 4.1 Reference table

A new reference table was created:

`dbo.Ref_FieldPool_ST103`

The table contains:

- `Field_Name` — NVARCHAR(100)
- `Production_Pool_Name` — NVARCHAR(100)
- `Field_Code` — NVARCHAR(4)
- `Production_Pool_Code` — NVARCHAR(7)
- `Geological_Pool_Code` — NVARCHAR(7)
- `Geological_Pool_Name` — NVARCHAR(100)
- `Confidential` — NVARCHAR(20)

All fields were defined as nullable. No primary key was imposed because the source supports multiple Geological Pool records for a Field + Production Pool combination.

### 4.2 Import process

The SQL Server Import and Export Wizard was used to import the prepared CSV into the existing reference table.

**Import date:** October 18, 2026

**Result:** 68,515 rows successfully transferred.

The import execution report confirmed successful completion and final commit.

No existing volumetric or well infrastructure tables were modified.

### 4.3 Import validation

The following results were obtained from SQL Server:

| Validation metric | Result |
|---|---:|
| Total imported rows | 68,515 |
| Distinct Field Codes | 899 |
| Distinct Geological Pool Codes | 12,057 |
| Records with missing Geological Pool Codes | 985 |

The imported row count matched the expected source data count.

## 5. ST103 Mapping Analysis

The mapping was evaluated using the combination of:

`Field_Code + Production_Pool_Code`

This composite identifier is important because the same Production Pool Code can appear in different fields with different associated Geological Pools.

### 5.1 Mapping cardinality

| Mapping classification | Combinations | Percentage |
|---|---:|---:|
| One Geological Pool | 49,845 | 90.16% |
| Multiple Geological Pools | 4,458 | 8.06% |
| No Geological Pool Code | 985 | 1.78% |
| **Total** | **55,288** | **100%** |

These percentages describe the reference-table combinations, not the percentage of wells that can be assigned to a Geological Pool.

Although most ST103 Field + Production Pool combinations have one Geological Pool Code, this does not establish that most wells in the production database have a unique reservoir assignment.

## 6. Mapping to Well Infrastructure

The existing table:

`dbo.Source_Well_Infrastructure`

was evaluated using the following columns:

- `Well_ID`
- `Field_Code`
- `Pool_Deposit_Code`
- `Pool_Deposit_Name`

For this investigation, `Pool_Deposit_Code` was matched against the ST103 `Production_Pool_Code`.

### 6.1 Well infrastructure consistency

| Metric | Result |
|---|---:|
| Distinct Well IDs | 665,307 |
| Wells with multiple distinct nonblank Field Codes | 0 |
| Wells with multiple distinct nonblank Production Pool Codes | 0 |

Therefore, each well had at most one distinct nonblank Field Code and one distinct nonblank Production Pool Code in the current infrastructure data.

This supported the use of a one-row-per-well intermediate dataset to avoid duplicate joins.

### 6.2 Geological Pool mapping coverage

| Classification | Wells | Percentage of all wells |
|---|---:|---:|
| One Geological Pool mapping | 138,512 | 20.82% |
| Multiple Geological Pool mappings | 192,909 | 29.00% |
| Missing Field or Production Pool information | 322,694 | 48.50% |
| Matching ST103 combination without Geological Pool Code | 8,222 | 1.24% |
| No matching ST103 combination | 2,970 | 0.45% |
| **Total** | **665,307** | **100%** |

Only 138,512 wells could be associated with a single Geological Pool Code through the available ST103 mapping.

This is a unique *reference mapping*, not independent verification of the well's actual producing or injecting reservoir.

The 192,909 wells with multiple mappings require additional well-level geological or completion information.

## 7. Investigation of Ambiguous Geological Pool Mappings

The next analysis investigated the 192,909 wells associated with multiple Geological Pool Codes.

### 7.1 Major commingled Production Pools

| Production Pool Code | Production Pool Name | Ambiguous Wells |
|---|---|---:|
| 0950160 | COMMINGLED MFP9501 | 99,369 |
| 0800160 | COMMINGLED POOL 001 | 17,407 |
| 0952960 | COMMINGLED MFP9529 | 10,354 |
| 0800260 | COMMINGLED POOL 002 | 7,072 |
| 0951560 | COMMINGLED MFP9515 | 6,795 |

The 20 largest Production Pool reporting groups accounted for 173,712 ambiguous wells, approximately 90% of the total ambiguous population.

The largest group, MFP9501, accounted for approximately 51.5%.

This finding demonstrates that ambiguous mappings are heavily concentrated in commingled Production Pool reporting groups.

### 7.2 Example: MFP9501

The same Production Pool Code, `0950160`, occurs across multiple fields.

Examples:

| Field Code | Candidate Geological Pools | Wells |
|---|---:|---:|
| 0601 | 54 | 16,289 |
| 0877 | 23 | 11,595 |
| 0259 | 682 | 9,989 |

These values describe the number of Geological Pool Codes associated with the Field + Production Pool combination in ST103.

They do not demonstrate that an individual well produces from every listed Geological Pool.

## 8. Prioritizing Wells with Recorded Production

The investigation was refined using:

`dbo.vw_Well_Production_Records`

The previously created view identifies well-related volumetric production records for OIL, GAS and WATER.

The analysis covered January–August 2026.

### 8.1 Results

| Classification | Wells |
|---|---:|
| Total wells with ambiguous mappings | 192,909 |
| Wells with recorded 2026 production | 80,266 |
| Wells without matching 2026 production records | 112,643 |

Approximately 41.6% of the ambiguous wells had matching production records during the study period.

Wells without matching production records should not automatically be classified as inactive. They may be shut-in, injecting, abandoned, or outside the available reporting scope.

### 8.2 Largest ambiguous groups among producing wells

| Production Pool | Producing Wells |
|---|---:|
| COMMINGLED MFP9501 | 51,326 |
| COMMINGLED MFP9529 | 4,893 |
| COMMINGLED POOL 001 | 4,214 |
| COMMINGLED MFP9515 | 2,201 |
| COMMINGLED POOL 002 | 1,920 |
| COMMINGLED POOL 003 | 1,199 |
| COMMINGLED POOL 005 | 1,165 |
| COMMINGLED MFP9504 | 1,141 |
| COMMINGLED POOL 007 | 970 |
| COMMINGLED MFP9513 | 731 |

The ten largest groups contain 69,760 wells, approximately 86.9% of the 80,266 producing wells with ambiguous mappings.

MFP9501 alone accounts for 51,326 wells, approximately 63.9% of the ambiguous producing-well population.

This concentration is useful for prioritizing additional geological data research.

## 9. Important Limitations

The ST103 reference table provides relationships between Production Pools and Geological Pools. It does not necessarily establish the actual producing or injecting reservoir for each well.

Several limitations remain:

1. **Commingled production:** Multiple Geological Pools can correspond to one Production Pool.
2. **Missing infrastructure information:** 322,694 wells lacked the required field/pool information for the matching analysis.
3. **Time dependency:** A well's historical completion or producing zone may differ from the intervals active during 2026.
4. **Formation identification:** Geological Pool Codes must not automatically be interpreted as Formation Codes.
5. **Production allocation:** Monthly production volumes cannot be assigned to multiple candidate Geological Pools without supporting allocation evidence.
6. **Injection:** The current production-focused analysis does not fully evaluate injection wells.
7. **Reservoir confirmation:** A unique reference mapping is not proof of reservoir continuity or an independently verified producing interval.

### Critical data integrity rule

Joining ST103 directly to monthly volumetric records may multiply rows when one Production Pool has multiple Geological Pool mappings.

Future integration must preserve the original production-record grain and reported volumes.

Any one-to-many geological relationships should be handled separately from the production fact table until the appropriate well-level reservoir assignments are established.

## 10. Preliminary Research into Additional AER Sources

Because ST103 cannot uniquely identify reservoirs for many producing wells, additional AER data sources were identified for investigation.

### 10.1 General Well Data

Potentially useful information includes:

- Well identification.
- Geological tops and markers.
- Perforation and treatment intervals.
- Well completion intervals.
- Well history.

These records may help associate completion intervals with geological formations.

### 10.2 IGDS Well File

Potentially useful information includes:

- Well identifiers.
- Formation and zone information.
- Zone top and base depths.
- Reservoir evaluation properties.

However, potentially productive zones must not automatically be treated as actually producing zones.

### 10.3 Investigation status

The available AER product descriptions and layouts have been reviewed at a preliminary level.

No province-wide General Well Data or IGDS file has been purchased or imported as part of this investigation.

Their actual well-matching coverage, completeness and ability to resolve ambiguous ST103 mappings have not yet been established.

## 11. Next Steps

The next phase will focus on finding a scalable and defensible method for identifying actual reservoirs and formations.

Planned activities:

1. Inspect available AER General Well Data sample records and layouts.
2. Identify usable well identifiers and compare them with Petrinex Well IDs.
3. Evaluate completion intervals, perforations and geological tops.
4. Investigate whether these records identify the Geological Pools associated with individual commingled wells.
5. Assess formation identification for wells with missing Production Pool data.
6. Test the method on a representative batch of wells before any province-wide integration.
7. Evaluate injection wells separately.
8. Preserve geological source provenance and unresolved mapping cases.
9. Validate that geological joins do not change original production volumes or record counts.
10. Develop reservoir- and formation-level analytical views only when sufficient evidence is available.

## 12. Conclusion

The AER ST103 integration is an important milestone in the Alberta Oil & Gas Production Data Platform.

**Completed:**

- Created the ST103 SQL reference table.
- Successfully imported 68,515 records.
- Validated reference data counts.
- Analyzed 55,288 Field + Production Pool combinations.
- Evaluated Geological Pool mapping coverage for 665,307 wells.
- Identified 138,512 wells with unique reference mappings.
- Identified 192,909 wells with ambiguous mappings.
- Narrowed the recorded-producing ambiguous population to 80,266 wells.
- Identified the principal commingled Production Pools responsible for the ambiguity.

**Not yet completed:**

- Definitive reservoir identification for ambiguous wells.
- Well-level producing/injecting formation identification.
- Integration of bulk completion and geological-top datasets.
- Reservoir-level production allocation.

The investigation demonstrates both the value and limitations of ST103 and establishes a data-driven direction for the next phase of the project.

The long-term objective remains to build a reliable Alberta production analytics platform capable of supporting field, reservoir, formation, well, and production-performance analysis.
