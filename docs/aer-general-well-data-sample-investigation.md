# AER General Well Data: Sample Extraction and Depth-Code Investigation

**Project:** Alberta Oil & Gas Production Data Platform  
**Investigation:** October 2026  
**Status:** Sample parsing completed; depth codes confirmed; formation assignment is preliminary.  
**Scope:** Free AER sample and official code-reference files only. No province-wide General Well Data file purchased or imported.

## 1. Why we investigated this source

The AER ST103 Field/Production Pool reference cannot uniquely establish the actual producing formation for every well, especially commingled pools. We therefore investigated whether AER General Well Data can supply *well-level* geological tops, perforation/treatment operations, and completion intervals that may improve formation identification.

This investigation is a feasibility test on a small published sample, **not** a verified province-wide well-to-formation mapping.

## 2. Source files reviewed

| File | Role |
| --- | --- |
| `general-well-data-sample-file.txt` | Original AER sample containing tab-delimited records of several types |
| `general-well-data-layout-file.pdf` | AER **General Well Data File – All Alberta**, layout (2026 edition) |
| `Codecnv.txt` | AER Basic Well Code Conversion text data; confirms coded field descriptions |
| `BasicWellCodeConversion_LayoutDocument.pdf` | AER **Basic Well Code Conversion File**, layout document (November 2019) |

Useful official source links:
- [AER General Well Data overview](https://www.aer.ca/data-and-performance-reports/activity-and-data/lists-and-activities/general-well-data)
- [AER General Well Data sample TXT](https://static.aer.ca/prd/data/layouts/general-well-data-sample-file.txt)

The raw AER data files and extracted CSV files have **not** been committed to this repository.

## 3. Sample structure and extraction

The original sample uses **tab-separated fields**; it is not a single ordinary table with one schema. The second field is a three-digit **record type**, so each type must be parsed according to its own layout.

The sample contains **544 lines** and **7 distinct AER well-event identifiers (CPA IDs)**.

A local Python script, `parse_aer_general_well_data.py`, was run in VS Code to export six record types to CSV. The script and exports were tested locally; this does **not** imply that the parser script is already stored in GitHub.

| Record type | Output file | Records | Distinct well-event IDs | Information |
| --- | --- | ---: | ---: | --- |
| `010` | `well_details.csv` | 7 | 7 | Well, field, production pool, elevations |
| `015` | `formation_tops.csv` | 156 | 6 | Geological formation codes, marker depths, MD/TVD indicator |
| `055` | `perforations_treatments.csv` | 149 | 7 | Perforations, treatments, cementing, packer records |
| `065` | `plug_abandonments.csv` | 11 | 5 | Plugging and abandonment records |
| `070` | `well_status_history.csv` | 32 | 7 | Dated well status history |
| `075` | `initial_completion_intervals.csv` | 6 | 6 | Initial completion top and base |
| **Total extracted** | **6 CSV files** | **361** | — | Other record types are retained in the original TXT, but were not exported by this version of the script |

The six CSV extractions were compared with the corresponding records in the original TXT sample; the recorded row counts and field values matched. The 544-line original contains additional record types (for example, well licensing and logs) that were deliberately not part of this first extraction.

### Distinguishing operation types

For record `055`, `Packer_Indicator = 1` identifies a perforation/treatment operation; `Packer_Indicator = 2` identifies packer data. Of the 149 records, **144** have indicator `1` and **5** have indicator `2`. The operation code must be interpreted **together with** the packer indicator.

The current `Codecnv.txt` labels operation code `02` under record type `840` as **Perforation** (the older General Well Data layout's operation appendix uses **Jet Perforation**). The reference source/version should be retained with any standardized description; do not assume the descriptions are identical across code lists.

## 4. Verified MD versus TVD code definitions

The Basic Well Code Conversion layout lists **record type 750 — Log-TVD-Code** (PDF page 18), which supplies code descriptions for the General Well Data `015` field `Log_TVD_Code`.

**Actual entries in `Codecnv.txt`:**

| `Log_TVD_Code` | Official AER description | Abbreviation |
| --- | --- | --- |
| `1` | Measured Depth from Log | `LOG` |
| `2` | True Vertical Depth | `TVD` |

In the sample, **93** formation-top records have code `1` and **63** have code `2`. These represent depth-measurement types, **not** separate formation identities.

Example: AER well-event `0636060501000`, formation code `1660` (BADHEART FM):

| `Log_TVD_Code` | Marker depth |
| --- | ---: |
| `1` (MD from log) | 1,992.46 m |
| `2` (TVD) | 1,898.77 m |

The two values differ by **93.69 m**. They must **not** be treated as interchangeable for a deviated well.

Other independently checked formation code descriptions in `Codecnv.txt` include `5240` = **MONTNEY FM** and `5560` = **BELLOY FM**.

## 5. Depth reference / datum: established facts and gaps

The General Well Data layout describes the `055` perforation/treatment interval fields as **measured depths from the surface**; it does **not explicitly state the exact zero datum for those fields** in that section. Do not silently equate this wording to KB, ground level, tubing hanger, or mean sea level.

Record `010` supplies separate **ground elevation** and **KB elevation** for each well. For example, well-event `0795222014020` has ground elevation **570.50 m** and KB elevation **575.20 m** (difference **4.70 m**).

**Unresolved:** Confirm, using AER's current authoritative drilling/completion submission guidance, that the specific `015` geological-marker depths and `055`/`075` intervals are on compatible datums before automated depth comparisons. The code-conversion file resolves **MD vs TVD**, but does not on its own prove a common vertical reference datum.

## 6. Preliminary sample comparison: NORMANDVILLE / MONTNEY E

**AER well-event:** `0795222014020`  
**Name:** `CNRL NVILLE 14-20-79-22`  
**Field:** NORMANDVILLE  
**Reported Production Pool:** MONTNEY E

| Source record | Observation |
| --- | --- |
| `015` (MD code `1`) | MONTNEY FM top (`5240`): **853.00 m** |
| `015` (MD code `1`) | BELLOY FM top (`5560`): **917.20 m** |
| `055` (packer indicator `1`, operation `02`) | Perforation interval: **866.00–868.00 m** on 2000-01-06 |
| `055` (packer indicator `1`, operation `41`) | Fracture operation: **866.00–868.00 m** on 2000-01-07 |
| `075` | Initial completion interval: **866.00–868.00 m** |

**Preliminary inference:** The recorded perforation and initial completion are between the Montney and Belloy MD marker depths, consistent with the reported MONTNEY E pool. This is **not** proof of a currently open completion, formation-level production in 2026, or identical depth datums; later well operations and well history must be evaluated.

## 7. Well-event identity and historical changes

The sample contains `0636060501000`, `0636060501002`, and `0636060501003` under the same well name (`HUSKY REDROCK 1-5-63-6`). Distinct AER CPA IDs must be retained even when well names, elevations, markers, or historical intervals coincide.

`075` is explicitly an **initial completion interval**, not a definitive interval open in 2026. Later `055` treatment, `065` plugging/abandonment, and `070` status changes must be interpreted before attributing a production month to a formation.

A perforated interval can intersect more than one formation; a treated interval does not independently prove productive contribution. No arbitrary allocation of Petrinex volume across candidate formations is justified.

## 8. Working method and validation gates

1. Preserve the original tab-delimited source rows and their record type / AER CPA ID.
2. Extract type-specific records, retain source field definitions, and use string keys so leading zeros are not lost.
3. Decode formation and operation codes using an explicitly versioned AER code reference.
4. Use **MD** formation tops only when matching **MD** perforation/completion intervals; validate the datum first.
5. For vertical/subvertical wells, evaluate depth interval between consecutive formation tops, including incomplete marker sequences and uncertainty flags.
6. For directional/horizontal wells, evaluate trajectory and depth conversion as needed; do not equate MD with TVD.
7. Reconstruct time-relevant completion status from dated perforations, treatments, plugging, and other supporting records.
8. Establish validated links between AER CPA IDs, Petrinex well IDs, and production months, preserving separate well events.
9. Keep candidate or uncertain formation assignments separate from the production fact table. Validate joins to ensure they **do not multiply production rows or volumes**.
10. Benchmark the method against representative wells and commingled cases before considering province-wide implementation.

## 9. Status and next actions

**Completed:** inspected two AER layouts; obtained machine-readable TXT files; extracted and cross-checked six CSV datasets; confirmed `Log_TVD_Code` definitions; reviewed example formation-marker and completion overlap.

**Not completed:** formal perforation/formation datum confirmation; wellbore trajectory integration; time-specific producing-zone validation; integration with `AlbertaProductionDB`; sample-to-Petrinex match coverage; purchase/import of all-Alberta AER General Well Data.

**Follow-up (Phase 2 completed in October 2026):** A reproducible Python prototype now screens measured-depth geological marker intervals against perforation/treatment and initial-completion intervals, with separate potential plug-impact flags. The sample run produced 189 interval output rows (185 candidate formation overlaps plus 4 unmatched placeholders), 241 potential plug relationships, 7 well-event summaries, and 4 unmatched interval records. These are candidate results only; the common depth datum and 2026 producing-zone status remain unverified.

- [Phase 2 Python script](../python/aer_match_formations.py)
- [Phase 2 validation report and limitations](aer-formation-matching-python-validation.md)

**Next action:** verify the exact depth-reference datums, then refine time-aware completion and plugging interpretation before attempting any production linkage.

---

**Data integrity principle:** Neither geological marker overlap nor a unique code association alone is sufficient evidence for allocating 2026 production volumes to a formation.
