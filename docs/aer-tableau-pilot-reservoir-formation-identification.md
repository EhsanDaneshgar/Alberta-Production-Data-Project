> **SUPERSEDED (November 8, 2026).** This October 31 version used the labels STRONG / PROBABLE / FORMATION_ONLY and over-stated some results. See aer-tableau-pilot-reservoir-formation-identification_v4.md. Kept for history.

# AER Tableau Pilot: Reservoir and Formation Identification

**Project:** Alberta Oil & Gas Production Data Platform
**Date:** October 31, 2026
**Status:** Pilot completed on 10 conventional wells. Results are evidence-based estimates, not AER-confirmed assignments. No SQL Server tables were changed.

## 1. Goal

For each producing well, identify:

1. the **producing Geological Pool(s) / Reservoir(s)**, and
2. the **producing Formation(s)**.

ST103 only gives *candidate* Geological Pools for a Field + Production Pool. Commingled pools can have many candidates (for example, HERRONTON / COMMINGLED MFP9501 has 44). Well-specific evidence is needed to choose among them.

## 2. Data source: AER General Well Data (Tableau, free)

The public AER report [General Well Identifier Search](https://www2.aer.ca/t/Production/views/PRD_0100_General_Well_Identifier_Search/WellIdentifierSearch) links to per-well report sheets in the workbook `PRD_0100_Well_Summary_Report_View`.

Each sheet can be downloaded as CSV using Tableau's standard `.csv` view export:

```text
https://www2.aer.ca/t/Production/views/PRD_0100_Well_Summary_Report_View/<Sheet>.csv?Enter Well Identifier (UWI)=<UWI>
```

Sheets used:

| Sheet | Used for |
| --- | --- |
| `ProductionStrings` | Field, Production Pool, oil sands deposit, status of each production string |
| `CompletionInterval` | Gross completion interval of each string |
| `PerfTreatment` | Perforations, liners, open-hole, fractures, acid, plugs |
| `GeologicalTopsMarkers` | Formation tops (depth, quality) |
| `LicenceDetails` | Licensee and licence purpose (target formation text) |
| `StatusHistory` | Status history |
| `PlugbackAbandonment` | Plugback and abandonment records |

**Important finding:** the reports are keyed by the **wellbore UWI (event `/0`)**. Querying a later event (for example `/2`) returns empty sheets. The `/0` query returns all strings of the well, including `/2`, `/3` and `/4`.

**Terms:** AER content may be reused with attribution. Commercial redistribution requires AER written permission ([AER copyright](https://www.aer.ca/node/2584)).

## 3. Scripts

| File | Purpose |
| --- | --- |
| [`python/aer_well_extract_v2.py`](../python/aer_well_extract_v2.py) | Downloads the report sheets for a list of wells (Petrinex 16-character IDs or AER UWIs). Queries `/0` first, resumes after interruption, logs every request. Default delay: 2 seconds between requests. |
| [`python/aer_reservoir_formation_match_v1.py`](../python/aer_reservoir_formation_match_v1.py) | Estimates producing formation(s) and Geological Pool(s) per well, with confidence and flags. |
| [`reference/formation_to_pool_keywords_v1.csv`](../reference/formation_to_pool_keywords_v1.csv) | Editable lookup from formation names to pool-name keywords (for example Glauconitic → Upper Mannville). **Draft; to be reviewed and extended.** |
| [`sql/16_select_pilot_wells_and_st103_candidates.sql`](../sql/16_select_pilot_wells_and_st103_candidates.sql) | Read-only pilot well selection and ST103 candidate listing. |

Speed observed: about 6–10 seconds per sheet, about 1 minute per well.

## 4. Matching method

For each requested production string:

1. Find the string in `ProductionStrings` (Field, Production Pool, status).
2. Use **that string's completion interval**. Keep only perforation/liner/open-hole intervals that overlap it. Older plugged zones are excluded.
3. Build formation zones from tops (zone = top to next top). Assign each interval to the zone(s) it overlaps → **producing formation(s)**.
4. If there are no tops, use formation names in the licence purpose text (weak evidence).
5. Match formations to ST103 candidate pool names using the keyword lookup → **Geological Pool(s)**.

Confidence levels:

| Level | Meaning |
| --- | --- |
| STRONG | Tops evidence; each formation matches one pool (or the single ST103 candidate matches) |
| PROBABLE | Unique match, but licence-only evidence or a group-level zone (for example BELLY RIVER GRP) |
| FORMATION_ONLY | Formation known; several candidate pools in the same formation |
| UNRESOLVED | No usable evidence or no pool-name match |

## 5. Pilot results (10 conventional wells)

| Field | Production Pool | ST103 candidates | Producing formation(s) | Geological Pool(s) | Confidence |
| --- | --- | ---: | --- | --- | --- |
| BLACK | KEG RIVER C | 1 | Keg River Fm | KEG RIVER C | STRONG |
| SADDLE HILLS | BELLOY A | 1 | Belloy Fm | BELLOY A | STRONG |
| ELIZA | COLORADO A | 1 | Colorado Grp | COLORADO A | STRONG |
| HUXLEY | COMMINGLED POOL 007 | 2 | Glauconitic SS + Ellerslie Mbr | UPPER MANNVILLE U + LOWER MANNVILLE V | STRONG |
| GARTLEY | COMMINGLED MFP9501 | 2 | Basal Belly River Sd | MFP8540 BSL BELLY RIV | STRONG |
| HERRONTON | COMMINGLED MFP9501 | 44 | Belly River Grp | MFP8506 BELLY RIVER | PROBABLE |
| WINDFALL | COMMINGLED POOL 006 | 2 | Gething (licence only) | GETHING PP | PROBABLE |
| CHIGWELL | COMMINGLED MFP9504 | 2 | Belly River Grp + zone above first top | MFP8509 BELLY RIVER | PROBABLE, flagged CBM |
| FAIRYDELL-BON ACCORD | COMMINGLED MFP9508 | 4 | Viking Sandstone | Upper/Middle Viking (4 candidates) | FORMATION_ONLY |
| ADEN | COMMINGLED POOL 001 | 4 | Bow Island Sd | BOW ISLAND A/B/C/D | FORMATION_ONLY |

Summary:

- **Producing formation identified: 10 of 10 wells.**
- **Geological Pool narrowed to a specific pool: 8 of 10 wells.** HERRONTON went from 44 candidates to 1.
- The script output matched the manual analysis for all 10 wells.
- Full output: [`pilot-reservoir-formation-results-2026-10-31.csv`](pilot-reservoir-formation-results-2026-10-31.csv) (also includes 5 oil sands SAGD wells from the first test; their reservoir is the oil sands deposit WABISKAW-MCMURRAY).

## 6. Lessons learned

1. **Use the current string's interval, not all perforations.** Many wells have older zones that were plugged and abandoned.
2. **Licence purpose can be wrong or outdated.** HERRONTON's licence names Medicine Hat Sd, but the producing string is completed in the Belly River Grp. Licence text is weak evidence only.
3. **Tops are often missing.** Licence 0524255 (PROGRESS) and WINDFALL had no tops.
4. **Depth cannot separate pools within the same formation.** Bow Island A–D and Upper/Middle Viking pools are defined by map area. These need a spatial method (pool boundaries or nearby wells).
5. **Coalbed methane wells exist in commingled pools.** CHIGWELL has status CBMOT and perforations in shallow coal zones that have no ST103 conventional pool.
6. **Oil sands wells use Deposit, not Pool** (for example 306200 WABISKAW-MCMURRAY).

## 7. Limitations

- Tops and completion depths are assumed to use the same depth reference (measured depth). This is **not verified**. Horizontal wells need extra care.
- The formation-to-pool keyword table is a first draft.
- Group-level tops (for example BELLY RIVER GRP) give lower precision than member tops.
- The pilot is small (10 conventional wells) and not a random sample.

## 8. Next steps

1. Extend and review the formation-to-pool keyword table.
2. Run a larger test (about 100 wells across the main ambiguous pools, including MFP9501).
3. Add a spatial method for FORMATION_ONLY cases (pool letter by location).
4. Design a SQL table for well-to-Geological-Pool and well-to-Formation results (many-to-many, with evidence, confidence and source date). To be approved before creation.
5. Check depth reference (MD vs TVD) for horizontal wells.
6. Plan the extraction volume: about 1 minute per well. Prioritize wells with current production.
