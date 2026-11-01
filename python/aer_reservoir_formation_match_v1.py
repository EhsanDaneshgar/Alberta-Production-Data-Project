"""
AER reservoir + formation matcher (v1)

For each requested well (production string), this script estimates:
  1. the PRODUCING FORMATION(S)  - from completion/perforation depth vs. tops
  2. the GEOLOGICAL POOL(S)      - by matching those formations to the
                                   AER ST103 candidate pools of the well's
                                   Field + Production Pool

INPUTS
  --data      one or more folders created by aer_well_extract_v1/v2.py
  --st103     FieldPoolList_ST103_2026_SQL_Ready.csv
  --mapping   formation_to_pool_keywords_v1.csv (editable lookup table)
OUTPUTS (in --out folder)
  reservoir_formation_results_v1.csv   one row per requested well
  reservoir_formation_intervals_v1.csv one row per perforation interval

METHOD (per requested production string)
  a. Find the string in ProductionStrings -> Field, Production Pool, status.
  b. Use that string's Completion Interval. Keep perforations/liners/
     open-hole intervals that overlap it (old plugged zones are dropped).
  c. Build formation zones from Geological Tops: zone = top .. next top.
     Each perforation interval gets the zone(s) it overlaps.
  d. If no tops: read formation names from the Licence Purpose text
     (weak evidence).
  e. Map formations to ST103 candidate pool names with the keyword table.

CONFIDENCE
  STRONG          tops evidence, each formation matches one pool
                  (or the well has a single ST103 candidate that matches)
  PROBABLE        unique match, but evidence is licence-only, or the
                  interval sits in a group-level zone (e.g. BELLY RIVER GRP)
  FORMATION_ONLY  formation known, several candidate pools in it
                  (pool letter is set by map area, not by depth)
  UNRESOLVED      no usable evidence or no candidate matches

LIMITS: tops and perforation depths are assumed to share the same
depth reference (not verified). Results are evidence-based estimates,
not AER-confirmed assignments. No database changes are made.

Usage:
  python aer_reservoir_formation_match_v1.py --data pilot_output pilot_output_v2
         --st103 "..\\ST103\\FieldPoolList_ST103_2026_SQL_Ready.csv"
         --mapping formation_to_pool_keywords_v1.csv --out match_results
"""

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

PERF_TYPES = ("PERFORATION", "SLOTTED", "OPEN HOLE", "BAREFOOT", "JET", "BULLET")
CBM_STATUS = ("CBM", "CBMOT", "CBMSH")


# ---------------------------------------------------------------- helpers
def num(value):
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def overlap(a_top, a_base, b_top, b_base):
    return max(0.0, min(a_base, b_base) - max(a_top, b_top))


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_sheet(folders, sheet):
    """Merge one report sheet from several extract folders (deduplicated)."""
    rows, seen = [], set()
    for folder in folders:
        path = Path(folder) / f"{sheet}.csv"
        if not path.exists():
            continue
        for r in read_csv(path):
            r.setdefault("Requested_UWI", r.get("Query_UWI", ""))
            key = tuple(sorted(r.items()))
            if key not in seen:
                seen.add(key)
                rows.append(r)
    return rows


def load_mapping(path):
    rules = []
    for r in read_csv(path):
        rules.append({
            "formation": r["Formation_Keyword"].strip().upper(),
            "pools": [k.strip().upper() for k in r["Pool_Keywords"].split("|") if k.strip()],
            "exclude": [k.strip().upper() for k in r["Exclude_Keywords"].split("|") if k.strip()],
        })
    return rules


def rule_for(formation_name, rules):
    """First mapping rule whose keyword appears in the formation name."""
    name = formation_name.upper()
    for rule in rules:
        if rule["formation"] in name:
            return rule
    return None


def match_pools(formation_name, candidates, rules):
    """Candidate pools whose names fit this formation."""
    rule = rule_for(formation_name, rules)
    if rule is None:
        return [], "NO_MAPPING_RULE"
    hits = []
    for code, name in candidates:
        up = name.upper()
        if any(k in up for k in rule["pools"]) and not any(x in up for x in rule["exclude"]):
            hits.append((code, name))
    return hits, rule["formation"]


def licence_formations(text, rules):
    """Formation keywords mentioned in the licence purpose (weak evidence)."""
    up = (text or "").upper()
    found = []
    for rule in rules:
        if re.search(r"\b" + re.escape(rule["formation"]) + r"\b", up):
            # skip generic MANNVILLE if a member was already found
            if rule["formation"] == "MANNVILLE" and found:
                continue
            found.append(rule["formation"])
    return found


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--st103", required=True)
    ap.add_argument("--mapping", required=True)
    ap.add_argument("--out", default="match_results")
    args = ap.parse_args()

    rules = load_mapping(args.mapping)

    # ST103 candidates per (Field_Code, Production_Pool_Code)
    st103 = defaultdict(list)
    for r in read_csv(args.st103):
        code = (r["Geological_Pool_Code"] or "").strip()
        if code:
            st103[(r["Field_Code"].strip(), r["Production_Pool_Code"].strip())].append(
                (code, r["Geological_Pool_Name"].strip()))

    strings = load_sheet(args.data, "ProductionStrings")
    completions = load_sheet(args.data, "CompletionInterval")
    perfs = load_sheet(args.data, "PerfTreatment")
    tops = load_sheet(args.data, "GeologicalTopsMarkers")
    licences = load_sheet(args.data, "LicenceDetails")

    # index by wellbore (Query_UWI) and by string UWI
    string_by_uwi = {r["Prod String UWI Formatted"]: r for r in strings}
    tops_by_well = defaultdict(list)
    for r in tops:
        d = num(r["Formation Depth"])
        if d is not None and r["Formation"].strip():
            tops_by_well[r["Query_UWI"]].append((d, r["Formation"].strip(), r["Quality"].strip()))
    licence_by_well = {r["Query_UWI"]: r for r in licences}

    requested = sorted({r["Requested_UWI"] for r in strings if r["Requested_UWI"]})

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    results, interval_rows = [], []

    for req in requested:
        flags = ["DEPTH_DATUM_UNVERIFIED"]
        s = string_by_uwi.get(req)
        query = next((r["Query_UWI"] for r in strings if r["Requested_UWI"] == req), req)
        if s is None:
            # requested event not listed as its own string: use first string of the well
            s = next(r for r in strings if r["Requested_UWI"] == req)
            flags.append("REQUESTED_STRING_NOT_FOUND")
        string_uwi = s["Prod String UWI Formatted"]
        field_code = s["Field Id"].strip().zfill(4) if s["Field Id"].strip() else ""
        pool_code = s["Pool ID"].strip().zfill(7) if s["Pool ID"].strip() else ""
        pool_name = s["Pool Name"].strip()
        status = " ".join(x for x in (s["Status Fluid"], s["Status Mode"], s["Status Type"]) if x and x != "N/A")
        if any(c in s["Status Fluid"].upper() for c in CBM_STATUS):
            flags.append("CBM_STATUS")

        # candidate pools: ST103, or the oil sands deposit if no pool
        if pool_code:
            candidates = st103.get((field_code, pool_code), [])
            if not candidates:
                flags.append("NO_ST103_CANDIDATES")
        elif s["Deposit Name"].strip():
            candidates = [(s["Deposit ID"].strip(), s["Deposit Name"].strip())]
            flags.append("OIL_SANDS_DEPOSIT")
        else:
            candidates = []

        # b. completion interval of this string, then overlapping perforations
        comp = [(num(r["Gross Completion Interval Top"]), num(r["Gross Completion Interval Base"]))
                for r in completions if r["Prod String UWI Formatted"] == string_uwi]
        comp = [(t, b) for t, b in comp if t is not None and b is not None]
        well_perfs = []
        for r in perfs:
            if r["Query_UWI"] != query:
                continue
            if not any(k in r["Perf Treatment Type"].upper() for k in PERF_TYPES):
                continue
            t, b = num(r["Perf Treatment Top Depth (m)"]), num(r["Perf Treatment Base Depth (m)"])
            if t is None or b is None:
                continue
            if comp and not any(overlap(t, b, ct, cb) > 0 or (ct <= t <= cb) for ct, cb in comp):
                continue
            well_perfs.append((t, b, r["Perf Treatment Type"], r["Perf Treatment Date"]))
        if not comp:
            flags.append("NO_COMPLETION_INTERVAL")
        if not well_perfs and comp:
            well_perfs = [(t, b, "Completion interval", "") for t, b in comp]

        # c. formation zones from tops
        zones = sorted(tops_by_well.get(query, []))
        formations, source = [], ""
        if zones:
            source = "TOPS"
            for t, b, ptype, pdate in well_perfs:
                hit = []
                for i, (ztop, zname, zq) in enumerate(zones):
                    zbase = zones[i + 1][0] if i + 1 < len(zones) else float("inf")
                    if overlap(t, b, ztop, zbase) > 0 or (ztop <= t < zbase):
                        hit.append(zname)
                        if zbase == float("inf"):
                            flags.append("BELOW_LAST_TOP")
                if t < zones[0][0]:
                    hit.insert(0, "ABOVE FIRST TOP (unknown)")
                    flags.append("ABOVE_FIRST_TOP")
                for h in hit:
                    if h not in formations:
                        formations.append(h)
                interval_rows.append({
                    "Requested_UWI": req, "Interval_Top_m": t, "Interval_Base_m": b,
                    "Interval_Type": ptype, "Interval_Date": pdate,
                    "Formations": "; ".join(hit)})
        else:
            lic = licence_by_well.get(query, {}).get("Well Licence Purpose", "")
            formations = licence_formations(lic, rules)
            if formations:
                source = "LICENCE_ONLY"
                flags.append("NO_TOPS_LICENCE_ONLY")

        # e. formations -> candidate pools
        matched, group_level, multi = [], False, False
        known = [f for f in formations if not f.startswith("ABOVE FIRST TOP")]
        for f in known:
            hits, _ = match_pools(f, candidates, rules)
            if " GRP" in f.upper() or f.upper().endswith("GROUP"):
                group_level = True
            if len(hits) > 1:
                multi = True
            for h in hits:
                if h not in matched:
                    matched.append(h)
        # if specific members gave nothing, try generic group names (e.g. MANNVILLE GRP)
        if not matched and known:
            flags.append("NO_POOL_NAME_MATCH")

        # confidence
        if not known:
            conf = "UNRESOLVED"
        elif not matched:
            conf = "FORMATION_ONLY"
        elif multi:
            conf = "FORMATION_ONLY"
        elif len(candidates) == 1 and source == "TOPS":
            conf = "STRONG"
        elif source == "LICENCE_ONLY" or group_level:
            conf = "PROBABLE"
        else:
            conf = "STRONG"

        results.append({
            "Requested_UWI": req,
            "Wellbore_UWI": query,
            "Field_Code": field_code,
            "Field_Name": s["Field_Name"],
            "Production_Pool_Code": pool_code,
            "Production_Pool_Name": pool_name or s["Deposit Name"],
            "String_Status": status,
            "Completion_Interval_m": "; ".join(f"{t:g}-{b:g}" for t, b in comp),
            "Producing_Formations": "; ".join(formations),
            "Formation_Source": source or "NONE",
            "ST103_Candidate_Count": len(candidates),
            "Matched_Geological_Pools": "; ".join(f"{c} {n}" for c, n in matched),
            "Confidence": conf,
            "Flags": "; ".join(dict.fromkeys(flags)),
            "Licence_Purpose": licence_by_well.get(query, {}).get("Well Licence Purpose", "").strip(),
        })

    with open(out / "reservoir_formation_results_v1.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0]))
        w.writeheader()
        w.writerows(results)
    if interval_rows:
        with open(out / "reservoir_formation_intervals_v1.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(interval_rows[0]))
            w.writeheader()
            w.writerows(interval_rows)

    print(f"Wells processed: {len(results)}")
    for c in ("STRONG", "PROBABLE", "FORMATION_ONLY", "UNRESOLVED"):
        print(f"  {c:15} {sum(r['Confidence'] == c for r in results)}")
    print(f"Output: {out.resolve()}")


if __name__ == "__main__":
    main()
