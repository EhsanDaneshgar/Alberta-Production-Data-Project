# AER General Well Data: Candidate Formation Matching (Python Phase 2)

**Project:** Alberta Oil & Gas Production Data Platform  
**Date:** October 2026  
**Scope:** AER free sample, *not* all Alberta wells  
**Status:** Phase 2 Python outputs reproduced and validated against the four user-generated sample CSV reports. Formation assignments remain **candidates only**; no SQL Server changes have been made.

## 1. Purpose

The previous investigation extracted six tab-delimited General Well Data record types into CSV. This second phase tests whether measured-depth (MD) geological tops can be used to identify *candidate* formations intersected by the sample's perforation/treatment and initial completion intervals, with separate flags for potentially relevant historical plugs.

This is a **screening algorithm**, not a reconstruction of confirmed producing completions, production allocation, or reservoir activity in 2026.

### Related files

- **Python source:** [`python/aer_match_formations.py`](../python/aer_match_formations.py)
- **Phase 1 investigation and MD/TVD reference:** [`docs/aer-general-well-data-sample-investigation.md`](aer-general-well-data-sample-investigation.md)
- **AER source sample:** [General Well Data TXT sample](https://static.aer.ca/prd/data/layouts/general-well-data-sample-file.txt)
- **AER code descriptions:** locally downloaded `Codecnv.txt`; see the AER Basic Well Code Conversion layout for record types `700` (formations), `750` (Log-TVD-Code), and `840` (perforation treatment).

Neither the source data files nor the derived CSV outputs are stored in GitHub at this stage.

## 2. Inputs and setup

The script uses standard-library Python modules only: `csv`, `collections`, `datetime`, and `pathlib`.

All six CSV files are produced by the *first* parser, `parse_aer_general_well_data.py` (run locally; its source is not yet committed here).

| Input CSV | AER record | Use in Phase 2 |
| --- | --- | --- |
| `formation_tops.csv` | `015` | Geological tops, formation code, `Log_TVD_Code` |
| `perforations_treatments.csv` | `055` | Perforation/treatment and packer records, dates, depth intervals |
| `initial_completion_intervals.csv` | `075` | Initial completed interval, not a current completion |
| `plug_abandonments.csv` | `065` | Historical plug intervals and recorded dates |
| `well_details.csv` | `010` | AER well-event ID, names, Field/Production Pool |
| `well_status_history.csv` | `070` | Most recent recorded status for context |

Recommended local structure:

```text
local_working_folder/
├── aer_match_formations.py
├── Codecnv.txt                        # optional but recommended for names
└── aer_parsed/
    ├── formation_tops.csv
    ├── perforations_treatments.csv
    ├── initial_completion_intervals.csv
    ├── plug_abandonments.csv
    ├── well_details.csv
    └── well_status_history.csv
```

If the CSV folder or `Codecnv.txt` is elsewhere, adjust `DATA_DIR` and `CODE_FILE` at the start of the Python script; on Windows, use raw path literals such as `Path(r"C:\path\to\aer_parsed")`.

Run with `python aer_match_formations.py` from VS Code's integrated terminal, or use VS Code's **Run Python File** action. Results are written to `DATA_DIR / "formation_matching_results"`.

## 3. Implemented logic

1. Read input CSV files with UTF-8 BOM support and **retain all AER CPA IDs as strings**, so identifier zeros and distinct events are not lost.
2. Select **`Log_TVD_Code = 1`**, confirmed by AER code record `750` as **Measured Depth from Log**. Do not combine these with `Log_TVD_Code = 2` (True Vertical Depth) markers.
3. Sort a well-event's MD formation tops by depth. Assign a *candidate depth span* from each marker to the next marker; keep multiple codes at the same marker depth rather than choosing one.
4. Classify `055` records by `Packer_Indicator` and `Operation_Code`: exclude packer-only records; distinguish access/opening, treatment, remedial/plugging, and other operations. These groups are **preliminary script-defined categories**, not proof of wellbore accessibility or a complete regulatory operation ontology.
5. Add `075` initial completion intervals as historical evidence.
6. For valid interval depths, compute positive depth overlap with each candidate MD marker span. An interval can produce **multiple candidate rows** if it spans more than one geological marker zone.
7. Compare `065` plug records against interval depths and available dates. Flag intersecting plugs and **shallower potential barriers**; keep their events as review candidates, not verified isolations.
8. Include latest `070` status fields in each well-event's summary for context; status codes are not treated as conclusive interval-level evidence.
9. Export candidate matches, plug review relationships, summaries, and unmatched intervals. All outputs preserve uncertainty flags.

**Critical restriction:** Common reference datum of geological tops versus treatment/completion depths has **not** been verified by this script. It marks all candidate records `Depth_Datum_Status = UNVERIFIED_COMMON_DATUM`.

## 4. Reproduced and validated sample outputs

A fresh run of `aer_match_formations.py` using the same AER sample-derived CSV inputs and local `Codecnv.txt` reproduced the user's latest four uploaded CSV reports **byte for byte**.

| Output CSV | Verified data rows | What rows mean |
| --- | ---: | --- |
| `interval_formation_candidates.csv` | **189** | **185** rows with candidate formation overlaps plus **4** unmatched-interval placeholder rows |
| `potential_plug_impacts.csv` | **241** | Interval-to-plug *potential relationships*; not 241 plugs or 241 closed zones |
| `well_formation_summary.csv` | **7** | One summary for each AER CPA well-event ID |
| `unmatched_or_invalid_intervals.csv` | **4** | All four report `NO_MD_GEOLOGICAL_TOPS` for the same SUFFIELD well-event |

### Count reconciliation

- `055` input: **149** records, including **144** non-packer operations and **5** packer-only records excluded from interval comparison.
- `075` input: **6** initial completion intervals.
- **150 intervals evaluated** = 144 non-packer `055` records + 6 `075` records.
- **146 intervals have at least one candidate overlap**; **4** lack MD geological tops.
- **185 candidate overlap rows** are produced from the 146 overlapping intervals because some intervals intersect multiple formation-marker spans.
- **189 exported interval rows** = 185 matched candidate rows + 4 unmatched placeholders.
- Decoding `Codecnv.txt` fills **185 candidate formation names**. Operation descriptions are blank where no operation code exists (e.g., `075`) or no lookup applies.
- The first run without a correctly located `Codecnv.txt` had blank description columns. After correcting the local path, rerunning preserved the matching counts and populated names.

These figures describe **sample algorithm behavior**, not the number of confirmed productive formations.

## 5. Example findings and unresolved cases

| AER CPA ID | Well | Result from MD interval screening |
| --- | --- | --- |
| `0795222014020` | CNRL NVILLE 14-20-79-22 | `MONTNEY FM` candidate for access-opening and initial completion intervals |
| `0756111401000` | CNRL VALHALLA 1-14-75-11 | `MONTNEY FM` candidate |
| `0866102103000` | BIRCHCLIFF SIPHON 3-21-86-10 | `GETHING FM` candidate |
| `0204072016030` | RIDGEBACK SUFFIELD 16-20-20-7 | **No MD geological tops**; four intervals cannot be matched |
| `0636060501000`, `0636060501002`, `0636060501003` | HUSKY REDROCK 1-5-63-6 | Multiple candidate formations across historical activities; the three distinct CPA IDs must remain separate |

The `REDROCK` initial completion intervals span many consecutive marker zones. Reporting all intersected markers is expected from the algorithm and **is not a claim that all formations were opened or produced**.

## 6. Limitations / required improvements

- **Depth datum unresolved:** MD vs TVD code meanings are established, but the particular geological-top and perforation/completion *zero references* need official confirmation of compatibility.
- **Well trajectory:** MD depth-marker comparison does not replace a directional survey or wellbore path, especially in deviated/horizontal wells.
- **Geological intervals:** Consecutive observed markers provide provisional zones, not guaranteed complete stratigraphy, active pay, or validated geological boundaries. Deepest observed marker has no independently recorded base.
- **Historical status:** `075` is *initial* completion only; `055` treatments, `065` plug operations, and `070` recorded statuses alone do not determine an interval's current ability to flow.
- **Plug logic:** The **241** potential plug relationships include a heuristic for shallower barriers and unknown/same-day chronology; these cannot be used as confirmed plugging outcomes.
- **Operation categories:** Treatment/plug code groupings are preliminary and must be reconciled with the official AER codes and full operations semantics for production use.
- **Distinct event IDs:** Separate CPA IDs can describe events associated with the same physical well. Do not collapse them just because the well name matches.
- **Allocation:** No link to `AlbertaProductionDB`, no validated producing-zone inference for 2026, and **no multiplication or assignment of Petrinex volumes**.
- **Scale:** Seven sample well-event IDs do not demonstrate completeness or representativeness for Alberta.

In the exported summaries, every well deliberately has:

- `Current_Producing_Formation_Confirmed = NO`
- `Common_Depth_Datum_Verified = NO`

## 7. Next technical steps

1. Confirm exact datum definitions for AER geological tops (`015`), perforation/treatments (`055`), and initial completions (`075`) in applicable official records/submission guidance.
2. Review operation-code classifications, with particular attention to completion openings versus fracture treatments and cement/remedial work.
3. Test date-aware interval accessibility against more complete AER completion and abandonment history.
4. Assess directional well geometry and ambiguous/missing geological markers.
5. Design validated AER CPA / Petrinex well-event matching and preserve the original production fact-table grain.
6. Only then evaluate a wider sample or bulk acquisition.

**Decision:** Phase 2 is reproducible as a *candidate matching prototype*; it is **not approved for reservoir-level production allocation or inference of current producing formations**.
