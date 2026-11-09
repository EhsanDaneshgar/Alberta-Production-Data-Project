# AER Tableau Pilot: Reservoir and Formation Identification (v4)

**Project:** Alberta Oil & Gas Production Data Platform
**Version:** v4, November 8, 2026 (replaces the October 31, 2026 version, which used the labels STRONG / PROBABLE / FORMATION_ONLY and over-stated some results)
**Status:** Pilot on 10 conventional wells, using matcher v3. Results are evidence-based labels, not AER-confirmed assignments. No SQL Server tables were changed. Production volumes are never split or duplicated between pools.

## 1. Goal

For each producing well, identify:

1. the **producing Geological Pool(s)** (reservoir), and
2. the **producing Formation(s)** or geological group.

ST103 only gives *candidate* Geological Pools for a Field + Production Pool. Commingled pools can have many candidates (HERRONTON / COMMINGLED MFP9501 has 44). Well-specific evidence is needed to judge each candidate.

**Design principle.** The goal is defensible assignments while preserving the ST103 mapping. It is not to reduce the number of Confirmed wells. The ST103 candidate list stays visible for every well. The evidence labels are added on top of it and never replace or delete it. Each label has a stated evidence rule (section 5).

## 2. Terms

| Term | Meaning |
| --- | --- |
| Formation | A rock unit (for example Belly River Grp) |
| Geological Pool | A reservoir (AER legal definition) |
| Production Pool | The unit Petrinex reports volumes for. It is either one geological pool or several commingled pools. |

The geological **group or formation** and the **pool** are reported separately. The group can be Confirmed from the tops; the pool is judged one candidate at a time.

## 3. Data source: AER General Well Data (Tableau, free)

The public AER report [General Well Identifier Search](https://www2.aer.ca/t/Production/views/PRD_0100_General_Well_Identifier_Search/WellIdentifierSearch) links to per-well report sheets in the workbook `PRD_0100_Well_Summary_Report_View`. Each sheet can be downloaded as CSV with Tableau's standard `.csv` view export.

Sheets used: `ProductionStrings`, `CompletionInterval`, `PerfTreatment`, `GeologicalTopsMarkers`, `LicenceDetails`, `StatusHistory`, `PlugbackAbandonment`.

**Important finding:** the reports are keyed by the wellbore UWI (event `/0`). A query for a later event (for example `/2`) returns empty sheets. The `/0` query returns all strings of the well.

**Terms:** AER content may be reused with attribution. Commercial redistribution requires AER written permission ([AER copyright](https://www.aer.ca/node/2584)).

Speed observed: about 1 minute per well (pilot estimate).

## 4. Scripts and reference files

| File | Purpose |
| --- | --- |
| `python/aer_well_extract_v2.py` | Downloads the report sheets for a list of wells. Queries `/0` first, resumes after interruption, logs every request. |
| `python/aer_reservoir_match_v3.py` | **Current matcher.** Reads the downloaded CSV files, ST103 candidates and the reference tables, and writes the labels. |
| `python/aer_reservoir_formation_match_v1.py` | Old keyword matcher. **Superseded.** Kept for history. |
| `reference/unit_families_v2.csv` | DRAFT depth-code ranges of geological units |
| `reference/mfp_pool_units_v2.csv` | DRAFT depth-code ranges of multi-field pools (MFP) |
| `reference/formation_codes_aer.csv` | AER formation code list |
| `sql/16_select_pilot_wells_and_st103_candidates.sql` | Read-only pilot well selection and ST103 candidate listing |

## 5. Evidence behind the five labels

Each ST103 candidate pool of each well gets one label. Every candidate is judged on its own, using only this well's evidence: the perforation / open-hole intervals of the current string (measured depth) and the formation tops picked in the well. A candidate pool is first converted into a depth-code range (section 6). Then each interval is compared with that range.

For each interval the matcher decides one of four relations:

| Relation | Meaning |
| --- | --- |
| DEFINITE | The interval lies inside the pool's unit. The tops above and below are picked, both have quality "Good", and the interval is at least 3 m away from both. |
| POSSIBLE | The interval may lie inside the pool's unit, but the tops do not prove it. |
| EXCLUDED | The interval lies outside the pool's unit, more than 3 m beyond its boundary. |
| UNKNOWN | The interval is above the first top picked in the well, so its position is not known. |

The label comes from these relations:

| Label | Evidence required | What it does **not** mean |
| --- | --- | --- |
| **Confirmed** | All 4 conditions are true: (1) the production pool and the geological pool are the same pool (not commingled); (2) every interval is DEFINITE inside the pool's unit; (3) this pool is the only possible candidate for those intervals; (4) the tops are Good and the depth reference is compatible. | It is not AER-confirmed. It is still subject to geological validation. |
| **Probable** | At least one interval is DEFINITE inside the pool's unit, and this pool is the only possible candidate for that interval. | Other intervals may be unexplained. |
| **Candidate** | The tops do not exclude the pool (POSSIBLE), but they do not prove it. Several candidates can be Candidate at the same time. | It is not a finding that the well produces from this pool. |
| **Not Supported** | Every interval is EXCLUDED, and the exclusion is made by the pool's **own** top picked in this well (basis DIRECT). | It does not mean the pool is impossible for the well. It means this well's own tops do not support it. |
| **Unresolved** | The evidence is not enough: no tops in the well, no depth-code range for the pool, the interval is above the first top, the depth reference is not compatible, **or** the pool is outside the interval only by stratigraphic order (its own top is not picked in this well). | It is not a negative result. The pool can still be real. |

**Leading candidate.** Among the pools labelled Candidate, the matcher marks one as the leading candidate only if it has the single highest provisional score. The score is +2 if the pool's unit contains the most specific unit of the interval, +1 if the licence purpose names a formation in the pool's unit, and -1 for a basal pool whose interval is more than 30 m above the group base. The score is provisional. A leading candidate is **not** Confirmed, and a high score never means Confirmed.

General rules:

- A single ST103 candidate is not automatically Confirmed. It is only a candidate until this well's evidence supports it.
- A well can produce from more than one pool.
- Candidates are never dismissed because the well is in ST103 category 3, 4 or 5.
- Production volumes are never split or duplicated between pools.
- The geological group or formation is reported separately from the pool.

## 6. Matching method (matcher v3)

1. Take the current production string and its perforation / open-hole intervals.
2. Place each interval between the formation tops of the well. This gives the geological group and the most specific unit. A 3 m tolerance is used at boundaries (provisional).
3. Convert each ST103 candidate pool to a depth-code range (from the formation code in the pool code, the unit families table, or the MFP table).
4. Compare each candidate pool with the interval and give it one label. The score (+2 / +1 / -1) is only a helper and is provisional.

## 7. Depth reference

| Item | Status |
| --- | --- |
| Perforation depths are measured depth (MD), mKB | Verified (AER Manual 027) |
| Tableau tops are MD | Verified for 1 deviated well (21 of 21 tops matched) |
| Tops datum is KB | **Assumed** |
| TD vs max TVD check | Screen only, not proof. Several directional wells fail it (WINDFALL 3.1%, HUXLEY 2.4%, BLACK 4.2%). |

## 8. Pilot results (matcher v3, 10 conventional wells)

63 candidate pools were judged: **1 Confirmed, 2 Probable, 16 Candidate, 5 Not Supported, 39 Unresolved.**

**Summary.** Matcher v3 identified a Confirmed or Probable pool, or a leading candidate, for 6 of the 10 pilot wells (ELIZA, CHIGWELL, HUXLEY, HERRONTON, SADDLE HILLS and BLACK). The other 4 wells (GARTLEY, FAIRYDELL-BON ACCORD, ADEN and WINDFALL) have several equally possible candidates or no tops. All results remain subject to geological validation.

The geological group or formation was placed for **9 of 10 wells**. WINDFALL has no tops, so it stays Unresolved.

| Field | Production Pool | ST103 candidates | Geological group / unit | Pool labels |
| --- | --- | ---: | --- | --- |
| FAIRYDELL-BON ACCORD | COMMINGLED MFP9508 | 4 | Viking Fm [Probable] | 4 Candidate |
| GARTLEY | COMMINGLED MFP9501 | 2 | Belly River Grp [Confirmed]; Basal Belly River Sd [Probable] | 2 Candidate |
| ELIZA | COLORADO A | 1 | Colorado Grp [Confirmed] | 1 Confirmed |
| WINDFALL | COMMINGLED POOL 006 | 2 | No tops [Unresolved] | 2 Unresolved |
| HERRONTON | COMMINGLED MFP9501 | 44 | Belly River Grp [Confirmed] | 3 Candidate, 4 Not Supported, 37 Unresolved |
| ADEN | COMMINGLED POOL 001 | 4 | Colorado Grp [Confirmed]; Bow Island Sd [Probable] | 4 Candidate |
| CHIGWELL | COMMINGLED MFP9504 | 2 | Belly River Grp [Confirmed] | 1 Probable, 1 Not Supported |
| SADDLE HILLS | BELLOY A | 1 | Belloy Fm [Probable] | 1 Candidate |
| BLACK | KEG RIVER C | 1 | Keg River Fm [Probable] | 1 Candidate |
| HUXLEY | COMMINGLED POOL 007 | 2 | Lower Mannville Fm and Mannville Grp [Confirmed]; Glauconitic Ss and Ellerslie Mbr [Probable] | 1 Probable, 1 Candidate |

**HERRONTON:** 44 ST103 Geological Pool candidates were evaluated. MFP8506 BELLY RIVER is the leading candidate, pending further validation.

Details:

- 4 pools are Not Supported by the well's own tops: MILK RIVER B, MILK RIVER C, MEDICINE HAT C and MFP8502 MED HAT.
- 3 pools are Candidates: BASAL BELLY RIVER NN, MFP8506 BELLY RIVER and MFP8543 BSL BELLY RIV.
- **MFP8506 BELLY RIVER is the leading candidate. It is not confirmed.**
- 37 pools are Unresolved. Most are Edmonton pools. They lie above or below the interval only by stratigraphic order (their own tops are not picked in this well).
- Open question: whether MFP8506 includes the basal Belly River sand (MFP8506 vs MFP8543) is still unresolved.

**CHIGWELL** is a coalbed methane (CBM) well, flagged in the output.

**Why single-candidate wells are mostly Candidate, not Confirmed:** SADDLE HILLS (BELLOY A) and BLACK (KEG RIVER C) have one ST103 candidate, and the pool's own top is picked just above the interval. But the lower boundary of the unit is not picked. If the lower boundary is not picked, it may lie at or above the top of the perforation, so the perforated interval may be partly or fully below the formation. The upper top alone is therefore not enough to upgrade the pool from Candidate to Probable. (Decision of the project owner, November 8, 2026.)

ELIZA is Confirmed because the tops above and below the interval are picked, are Good, and bound the interval inside the Colorado Grp.

## 9. Lessons learned

1. **Use the current string's interval, not all perforations.** Many wells have older plugged zones.
2. **Licence purpose can be wrong or outdated.** HERRONTON's licence names Medicine Hat Sd, but the string is completed in the Belly River Grp. Licence text is weak evidence.
3. **Tops are often missing** (WINDFALL, and licence 0524255 in the earlier investigation).
4. **Depth cannot separate pools in the same formation.** Bow Island A to D and the Viking pools are defined by map area. A spatial method is needed.
5. **Coalbed methane wells** can have intervals with no ST103 conventional pool (CHIGWELL).
6. **Oil sands wells** use Deposit, not Pool.
7. **One candidate is not one answer.** v1 called single-candidate wells STRONG. Under the evidence rules they are Candidate unless the evidence supports more.

## 10. Remaining geological uncertainties

**Depth and tops**

1. The tops datum (KB) is **assumed**. Tops were verified as measured depth on 1 deviated well (21 of 21 tops) only.
2. The TD vs max TVD check is a screen, not proof. TVD is missing or zero for many wells, and three directional wells fail the screen (WINDFALL 3.1%, HUXLEY 2.4%, BLACK 4.2%).
3. Some wells have no tops (WINDFALL), an interval below the last top (FAIRYDELL-BON ACCORD, SADDLE HILLS, BLACK) or above the first top (CHIGWELL). In these cases the tops cannot prove the position.

**Pool definitions**

4. The unit family and MFP tables are **drafts**. A wrong range would change labels.
5. **MFP8506 or MFP8543:** whether MFP8506 BELLY RIVER includes the basal Belly River sand is unresolved. HERRONTON's leading candidate depends on this.
6. The leading candidate of HERRONTON depends on provisional scoring: the -1 for basal pools (more than 30 m above the group base) and the licence-purpose text, which is weak evidence.
7. Unit order for units whose own top is not picked is inferred from formation codes. Codes of some units interleave (Viking and Bow Island), so that order is only a guide. This is why such pools stay Unresolved.
8. Pools in the same formation (Bow Island A to D, the Viking pools) are defined by map area. Depth cannot separate them.
9. The 3 m boundary tolerance and the score weights are provisional.

**Evidence not yet used**

10. Commingling orders (DE1, MU orders) can support Not Supported. They are not coded yet.
11. Pool boundaries (AER pool order shapefile) and well coordinates are not used yet.

**Sample**

12. The pilot has 10 wells, is not random, and covers only conventional wells.
13. Only the current string is analysed. Older zones are excluded.

## 11. Next steps

1. Review the draft unit and MFP reference tables.
2. Add commingling order evidence (DE1, MU orders) and the AER pool-order shapefile.
3. Run a larger test (about 100 wells) before any large extraction.
4. Add a spatial method for pools defined by map area.
5. Design SQL tables for well-to-pool and well-to-formation results (draft only; to be approved before creation).
6. Find a bulk source of tops and perforations. Tableau at about 1 minute per well is too slow for all wells.
