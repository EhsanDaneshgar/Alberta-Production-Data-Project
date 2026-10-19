"""Compare AER General Well Data formation tops with well intervals.

Inputs: six CSV files from parse_aer_general_well_data.py.
Optional: AER Codecnv.txt for formation/operation names.

This program suggests *candidate* formations only. It does not determine
which intervals are open now or assign Petrinex production to formations.
No third-party Python libraries or SQL Server connection required.
"""

import csv
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# STEP 1: Change this folder ONLY if your aer_parsed folder is elsewhere.
DATA_DIR = Path(__file__).resolve().parent / "aer_parsed"

# If Codecnv.txt is in the same folder as this script, names are included.
CODE_FILE = Path(__file__).resolve().parent / "Codecnv.txt"

OUTPUT_DIR = DATA_DIR / "formation_matching_results"

# AER record 055, PACKER_IND=1. Codes 01-09 describe completion/access
# operations; not all are conventional cased-hole perforations.
ACCESS_CODES = {f"{n:02d}" for n in range(1, 10)}
TREATMENT_CODES = {"11", "12", "21", "22", "23", "24", "31", "32",
                   "41", "42", "43"}
REMEDIAL_CODES = {f"{n:02d}" for n in range(50, 59)}


def load_csv(filename):
    path = DATA_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing input: {path}")
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def to_number(value):
    try:
        number = float(str(value).strip())
        if number != number or number in (float("inf"), float("-inf")):
            return None
        return number
    except (TypeError, ValueError):
        return None


def to_date(value):
    value = str(value or "").strip()
    if not value or value == "00000000":
        return None
    try:
        return datetime.strptime(value, "%Y%m%d").date()
    except ValueError:
        return None


def read_aer_code_names():
    formations, operations = {}, {}
    if not CODE_FILE.is_file():
        print("NOTE: Codecnv.txt not found beside the script; names will be blank.")
        return formations, operations

    with CODE_FILE.open("r", encoding="utf-8-sig", errors="replace") as f:
        for line in f:
            if not line.startswith(("700\t", "840\t")):
                continue
            cells = line.rstrip("\r\n").split("\t")
            if len(cells) < 3:
                continue
            group, code, description = cells[:3]
            if group == "700":
                formations[code.strip()] = description.strip()
            elif group == "840":
                operations[code.strip()] = description.strip()
    return formations, operations


def export_csv(filename, rows, columns):
    path = OUTPUT_DIR / filename
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {filename}: {len(rows)} rows")


def overlap(top_a, base_a, top_b, base_b):
    """Positive overlap only. A missing base_b is an open-ended marker zone."""
    if base_b is None:
        return max(0.0, base_a - max(top_a, top_b))
    return max(0.0, min(base_a, base_b) - max(top_a, top_b))


def operation_group(packer_indicator, code):
    if packer_indicator == "2":
        return "PACKER_ONLY"
    if packer_indicator != "1":
        return "UNKNOWN_PACKER_INDICATOR"
    if code in ACCESS_CODES:
        return "ACCESS_OPENING"
    if code in TREATMENT_CODES:
        return "TREATMENT_ONLY"
    if code in REMEDIAL_CODES:
        return "REMEDIAL_OR_PLUGGING"
    return "OTHER_OPERATION"


def main():
    print(f"Input folder: {DATA_DIR}")
    formation_rows = load_csv("formation_tops.csv")
    perf_rows = load_csv("perforations_treatments.csv")
    completion_rows = load_csv("initial_completion_intervals.csv")
    plug_rows = load_csv("plug_abandonments.csv")
    well_rows = load_csv("well_details.csv")
    status_rows = load_csv("well_status_history.csv")
    formation_names, operation_names = read_aer_code_names()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    wells = {r["AER_CPA_ID"]: r for r in well_rows}
    statuses = defaultdict(list)
    for row in status_rows:
        statuses[row["AER_CPA_ID"]].append(row)
    for rows in statuses.values():
        rows.sort(key=lambda r: r["Status_Date"])

    # Create depth intervals bounded by consecutive MD geological tops.
    # Never compare TVD tops directly with MD perforation values.
    md_by_well = defaultdict(list)
    for row in formation_rows:
        if row["Log_TVD_Code"].strip() != "1":
            continue
        depth = to_number(row["Formation_Depth"])
        if depth is not None and depth >= 0:
            md_by_well[row["AER_CPA_ID"]].append({
                "depth": depth,
                "code": row["Formation_Code"].strip(),
                "revision": row["Geo_Revised_Date"].strip(),
            })

    zones = {}
    multiple_revisions = {}
    duplicate_marker_depths = {}
    for well_id, markers in md_by_well.items():
        revisions = {m["revision"] for m in markers if m["revision"] != "00000000"}
        multiple_revisions[well_id] = len(revisions) > 1
        markers.sort(key=lambda m: (m["depth"], m["code"]))
        depth_groups = defaultdict(list)
        for marker in markers:
            depth_groups[marker["depth"]].append(marker)
        duplicate_marker_depths[well_id] = any(
            len(x) > 1 for x in depth_groups.values()
        )
        depths = sorted(depth_groups)
        zones[well_id] = []
        for idx, depth in enumerate(depths):
            next_top = depths[idx + 1] if idx + 1 < len(depths) else None
            # If two formation codes begin at the same depth, retain BOTH
            # and flag the ambiguity; never arbitrarily select one.
            for marker in depth_groups[depth]:
                zones[well_id].append({
                    "top": depth,
                    "bottom": next_top,
                    "code": marker["code"],
                    "duplicate_top": len(depth_groups[depth]) > 1,
                })

    plugs = defaultdict(list)
    for row in plug_rows:
        top, base = to_number(row["Interval_Top"]), to_number(row["Interval_Base"])
        if top is None or base is None or base <= top:
            continue
        plugs[row["AER_CPA_ID"]].append({
            "top": top, "base": base,
            "date": to_date(row["Operation_Date"]),
            "raw_date": row["Operation_Date"],
            "purpose": row["Plug_Purpose"].strip(),
            "plug_type": row["Plug_Type"].strip(),
        })

    intervals = []
    for row in perf_rows:
        group = operation_group(
            row["Packer_Indicator"].strip(), row["Operation_Code"].strip()
        )
        # Packers are equipment locations, not completion/perforation zones.
        if group == "PACKER_ONLY":
            continue
        intervals.append({
            "well": row["AER_CPA_ID"],
            "source": "055",
            "kind": group,
            "event_date": row["Operation_Date"].strip(),
            "obs": row["Observation_Number"].strip(),
            "code": row["Operation_Code"].strip(),
            "top": to_number(row["Interval_Top"]),
            "base": to_number(row["Interval_Base"]),
        })

    for row in completion_rows:
        intervals.append({
            "well": row["AER_CPA_ID"],
            "source": "075",
            "kind": "INITIAL_COMPLETION_ONLY",
            "event_date": "",  # AER 075 sample has no completion date
            "obs": "",
            "code": "",
            "top": to_number(row["Initial_Completion_Top"]),
            "base": to_number(row["Initial_Completion_Bottom"]),
        })

    matches = []
    plug_review = []
    issues = []
    by_well = defaultdict(Counter)
    by_well_formations = defaultdict(lambda: defaultdict(set))

    for interval in intervals:
        well = interval["well"]
        count = by_well[well]
        count["evaluated_intervals"] += 1
        count[interval["kind"]] += 1
        top, base = interval["top"], interval["base"]
        key = f"{interval['source']}:{interval['obs']}:{interval['event_date']}:{interval['top']}:{interval['base']}"
        observed_date = to_date(interval["event_date"])

        # Flag all *possibly relevant* subsequent plug events without
        # claiming that a plug actually closed a particular interval.
        possible_plugs = []
        if top is not None and base is not None and base > top:
            for plug in plugs.get(well, []):
                if observed_date and plug["date"] and plug["date"] < observed_date:
                    continue  # Plug happened before the dated operation.
                relation = None
                if overlap(top, base, plug["top"], plug["base"]) > 0:
                    relation = "INTERSECTS_INTERVAL"
                elif plug["base"] <= top:
                    relation = "SHALLOWER_POTENTIAL_BARRIER"
                if relation is None:
                    continue
                chronology = (
                    "DATE_UNKNOWN" if not observed_date or not plug["date"]
                    else "SAME_DAY_SEQUENCE_UNKNOWN" if plug["date"] == observed_date
                    else "LATER_THAN_OPERATION"
                )
                possible_plugs.append(relation)
                plug_review.append({
                    "AER_CPA_ID": well,
                    "Interval_Key": key,
                    "Source_Record": interval["source"],
                    "Interval_Type": interval["kind"],
                    "Interval_Top_m": top,
                    "Interval_Base_m": base,
                    "Plug_Date": plug["raw_date"],
                    "Plug_Top_m": plug["top"],
                    "Plug_Base_m": plug["base"],
                    "Plug_Purpose": plug["purpose"],
                    "Plug_Type": plug["plug_type"],
                    "Depth_Relation": relation,
                    "Chronology": chronology,
                    "Interpretation": "Potential barrier only; verify datum, well geometry and operational history",
                })

        flags = []
        if possible_plugs:
            flags.append("POTENTIAL_LATER_PLUG_OR_BARRIER")
        if multiple_revisions.get(well):
            flags.append("MULTIPLE_MD_MARKER_REVISION_DATES")
        if duplicate_marker_depths.get(well):
            flags.append("DUPLICATE_MD_MARKER_DEPTH")
        if interval["source"] == "075":
            flags.append("INITIAL_COMPLETION_NOT_CURRENT_STATUS")
        if interval["kind"] == "REMEDIAL_OR_PLUGGING":
            flags.append("NOT_EVIDENCE_OF_OPEN_PERFORATIONS")
        if interval["kind"] == "TREATMENT_ONLY":
            flags.append("TREATMENT_NOT_PROOF_OF_OPEN_PERFORATIONS")

        candidates = []
        if top is None or base is None or top < 0 or base <= top:
            match_status = "INVALID_INTERVAL_DEPTHS"
        elif well not in zones:
            match_status = "NO_MD_GEOLOGICAL_TOPS"
        else:
            candidates = [
                (z, overlap(top, base, z["top"], z["bottom"]))
                for z in zones[well]
                if overlap(top, base, z["top"], z["bottom"]) > 0
            ]
            match_status = (
                "CANDIDATE_OVERLAP" if candidates
                else "OUTSIDE_RECORDED_MD_TOP_RANGE"
            )

        if not candidates:
            count["unmatched_intervals"] += 1
            issues.append({
                "AER_CPA_ID": well, "Interval_Key": key,
                "Issue": match_status,
            })
            candidates = [(None, None)]
        else:
            count["matched_intervals"] += 1
            if len(candidates) > 1:
                count["multi_formation_intervals"] += 1

        for zone, overlap_length in candidates:
            code = zone["code"] if zone else ""
            name = formation_names.get(code, "")
            if zone:
                by_well_formations[well][interval["kind"]].add(
                    (code, name)
                )
            row_flags = list(flags)
            if zone and zone["bottom"] is None:
                row_flags.append("DEEPEST_MARKER_NO_KNOWN_BASE")
            if zone and zone["duplicate_top"]:
                row_flags.append("MULTIPLE_MARKERS_SHARE_TOP")
            if zone and len(candidates) > 1:
                row_flags.append("SPANS_MULTIPLE_CANDIDATES")
            matches.append({
                "AER_CPA_ID": well,
                "Well_Name": wells.get(well, {}).get("Well_Name", ""),
                "Field_Name": wells.get(well, {}).get("Field_Name", ""),
                "Production_Pool_Name": wells.get(well, {}).get("Production_Pool_Name", ""),
                "Interval_Key": key,
                "Source_Record": interval["source"],
                "Interval_Type": interval["kind"],
                "Operation_Code": interval["code"],
                "Operation_Description": operation_names.get(interval["code"], ""),
                "Operation_Date": interval["event_date"],
                "Interval_Top_m": top,
                "Interval_Base_m": base,
                "Candidate_Formation_Code": code,
                "Candidate_Formation_Name": name,
                "MD_Marker_Top_m": zone["top"] if zone else "",
                "Next_MD_Marker_Top_m": (
                    zone["bottom"] if zone and zone["bottom"] is not None else ""
                ),
                "Overlap_m": (
                    round(overlap_length, 2)
                    if zone and zone["bottom"] is not None else ""
                ),
                "Match_Status": match_status,
                "Depth_Datum_Status": "UNVERIFIED_COMMON_DATUM",
                "Later_Plug_Possibility_Count": len(possible_plugs),
                "Flags": "; ".join(row_flags),
            })

    summary = []
    all_wells = sorted(set(wells) | set(md_by_well) | set(by_well))
    for well in all_wells:
        latest = statuses.get(well, [])[-1] if statuses.get(well) else {}

        def format_codes(group):
            return "; ".join(
                f"{code} {name}".strip()
                for code, name in sorted(by_well_formations[well].get(group, set()))
            )

        summary.append({
            "AER_CPA_ID": well,
            "Well_Name": wells.get(well, {}).get("Well_Name", ""),
            "Field_Name": wells.get(well, {}).get("Field_Name", ""),
            "Production_Pool_Name": wells.get(well, {}).get("Production_Pool_Name", ""),
            "MD_Geological_Marker_Count": len(md_by_well.get(well, [])),
            "Intervals_Checked": by_well[well]["evaluated_intervals"],
            "Candidate_Overlaps_Found": by_well[well]["matched_intervals"],
            "Intervals_With_Multiple_Candidates": by_well[well]["multi_formation_intervals"],
            "Intervals_Without_Matches": by_well[well]["unmatched_intervals"],
            "Access_Opening_Formation_Candidates": format_codes("ACCESS_OPENING"),
            "Initial_Completion_Formation_Candidates": format_codes("INITIAL_COMPLETION_ONLY"),
            "Last_Recorded_Status_Date": latest.get("Status_Date", ""),
            "Last_Recorded_Status_Code": latest.get("Status_Code", ""),
            "Current_Producing_Formation_Confirmed": "NO",
            "Common_Depth_Datum_Verified": "NO",
        })

    print("\nWriting reports:")
    export_csv("interval_formation_candidates.csv", matches, [
        "AER_CPA_ID", "Well_Name", "Field_Name", "Production_Pool_Name",
        "Interval_Key", "Source_Record", "Interval_Type", "Operation_Code",
        "Operation_Description", "Operation_Date", "Interval_Top_m", "Interval_Base_m",
        "Candidate_Formation_Code", "Candidate_Formation_Name", "MD_Marker_Top_m",
        "Next_MD_Marker_Top_m", "Overlap_m", "Match_Status",
        "Depth_Datum_Status", "Later_Plug_Possibility_Count", "Flags",
    ])
    export_csv("potential_plug_impacts.csv", plug_review, [
        "AER_CPA_ID", "Interval_Key", "Source_Record", "Interval_Type",
        "Interval_Top_m", "Interval_Base_m", "Plug_Date", "Plug_Top_m",
        "Plug_Base_m", "Plug_Purpose", "Plug_Type", "Depth_Relation",
        "Chronology", "Interpretation",
    ])
    export_csv("well_formation_summary.csv", summary, [
        "AER_CPA_ID", "Well_Name", "Field_Name", "Production_Pool_Name",
        "MD_Geological_Marker_Count", "Intervals_Checked",
        "Candidate_Overlaps_Found", "Intervals_With_Multiple_Candidates",
        "Intervals_Without_Matches", "Access_Opening_Formation_Candidates",
        "Initial_Completion_Formation_Candidates",
        "Last_Recorded_Status_Date", "Last_Recorded_Status_Code",
        "Current_Producing_Formation_Confirmed", "Common_Depth_Datum_Verified",
    ])
    export_csv("unmatched_or_invalid_intervals.csv", issues, [
        "AER_CPA_ID", "Interval_Key", "Issue",
    ])
    print(f"\nDone. Open: {OUTPUT_DIR}")
    print("IMPORTANT: Matches are geological CANDIDATES, not producing formations.")
    print("Depth datum equivalence and time-specific completion status remain unverified.")


if __name__ == "__main__":
    main()
