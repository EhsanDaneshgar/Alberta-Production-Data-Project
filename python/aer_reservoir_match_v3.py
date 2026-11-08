"""
AER reservoir matcher (v3)  -  DRAFT for review, provisional rules

Goal: for each Petrinex production string, evaluate EVERY ST103 candidate
Geological Pool one by one, and separately report the geological unit
(group / formation) that contains the producing interval.

TWO CONCLUSIONS PER STRING
  A. Geological unit: Confirmed / Probable / Unresolved
  B. Each candidate pool: Confirmed / Probable / Candidate / Not Supported /
     Unresolved, with a provisional score and a Leading Candidate flag.
  Production volumes are NOT touched (no split, no duplication).

EVIDENCE USED (AER Tableau sheets from aer_well_extract_v2.py)
  ProductionStrings, CompletionInterval, PerfTreatment,
  GeologicalTopsMarkers, LicenceDetails

DEPTH REFERENCE (see documentation)
  - Perforation/completion depths: MD in mKB (AER Manual 027) - verified doc.
  - Tableau tops: MD log values (checked on 1 deviated well, 21/21 tops) .
  - Datum of tops assumed KB (not stated in AER layout)  -> ASSUMPTION.
  Use --no-depth-assumption to treat depths as not compatible
  (then every pool is Unresolved).

STRATIGRAPHIC POSITION
  - Non-MFP pool code 0FFFFNN: FFFF = AER formation code (checked on
    11,874 of 11,977 ST103 pools).
  - MFP pools (085xxxx): unit from mfp_pool_units_v1.csv (DRAFT).
  - Group/family ranges from unit_families_v1.csv (DRAFT).
  - Order of formation codes is used to place units that were NOT picked
    in the well (basis = INFERRED_CODE_ORDER). Units whose own top was
    picked use basis = DIRECT.

PROVISIONAL RULES (agreed with project owner, to be reviewed)
  Rule 1  TD vs max TVD < 1%: screening only (reported, not used as proof).
  Rule 2  3 m boundary tolerance: units on both sides of a nearby top stay possible.
  Rule 3  Score: +2 pool range contains the most specific unit of the interval
                 +1 licence purpose names a formation inside the pool range
                 -1 Basal pool and interval > 30 m above the group base
          A score never makes a pool Confirmed.

LABEL RULES
  Confirmed     non-commingled (production pool = geological pool), interval
                definitely inside the pool unit in all intervals, it is the only
                possible candidate, both bounding tops Good, depth compatible.
  Probable      definitely inside the pool unit for >= 1 interval and the only
                possible candidate for that interval.
  Candidate     not excluded by picked tops (possible), not definite.
  Not Supported excluded for every interval, beyond tolerance, by the pool's OWN
                picked top (basis DIRECT). Exclusion only by stratigraphic sequence
                (unit not picked) -> Unresolved (owner decision, Nov 1 2026).
  Unresolved    no tops, no unit mapping, or depth not compatible.

Usage:
  python aer_reservoir_match_v3.py --data pilot_output pilot_output_v2
     --st103 "..\\ST103\\FieldPoolList_ST103_2026_SQL_Ready.csv"
     --ref-dir . --wells-geometry pilot_geometry.csv --out match_results_v3
"""

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

TOL = 3.0          # Rule 2 (m)
BASAL_GAP = 30.0   # Rule 3 (m)
TVD_SCREEN = 0.01  # Rule 1 (fraction)
PERF_TYPES = ("PERFORATION", "SLOTTED", "OPEN HOLE", "BAREFOOT", "JET", "BULLET")
CBM_STATUS = ("CBM",)
SUFFIXES = (" FORMATION", " MEMBER", " GROUP", " SANDSTONE", " FM", " MBR", " GRP", " SD", " SS")


# ------------------------------------------------------------------ io
def num(v):
    try:
        return float(str(v).strip())
    except ValueError:
        return None


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_sheet(folders, sheet):
    rows, seen = [], set()
    for folder in folders:
        p = Path(folder) / f"{sheet}.csv"
        if not p.exists():
            continue
        for r in read_csv(p):
            r.setdefault("Requested_UWI", r.get("Query_UWI", ""))
            key = tuple(sorted(r.items()))
            if key not in seen:
                seen.add(key)
                rows.append(r)
    return rows


def petrinex_to_uwi(v):
    m = re.match(r"^(?:ABWI)?1(\d{2})(\d{2})(\d{2})(\d{3})(\d{2})W(\d)(\d{2})$", v.strip().upper())
    if not m:
        return v.strip()
    le, lsd, sec, twp, rng, mer, ev = m.groups()
    return f"{le}/{lsd}-{sec}-{twp}-{rng}W{mer}/{int(ev)}"


# ------------------------------------------------------------------ reference
class Ref:
    def __init__(self, ref_dir):
        d = Path(ref_dir)
        self.fcodes = {}
        for r in read_csv(d / "formation_codes_aer.csv"):
            try:
                self.fcodes[int(r["Formation_Code"])] = r["Formation_Name"].strip()
            except ValueError:
                pass
        self.sorted_codes = sorted(self.fcodes)
        self.families = [(int(r["Start_Code"]), int(r["End_Code"]), r["Unit_Name"].strip())
                         for r in read_csv(d / "unit_families_v2.csv")]
        self.mfp = sorted(((r["MFP_Name_Text"].strip().upper(), int(r["Start_Code"]), int(r["End_Code"]))
                           for r in read_csv(d / "mfp_pool_units_v2.csv")),
                          key=lambda x: -len(x[0]))
        # formation names for licence text matching
        self.name_codes = defaultdict(set)
        for c, n in self.fcodes.items():
            if n.startswith("BASE OF") or c < 100:
                continue
            base = n
            for s in SUFFIXES:
                if base.endswith(s):
                    base = base[: -len(s)]
            if len(base) >= 4:
                self.name_codes[base].add(c)

    def families_containing(self, code):
        return sorted([f for f in self.families if f[0] <= code < f[1]], key=lambda f: f[1] - f[0])

    def pool_range(self, pool_code, pool_name):
        """Return (start, end, source) of the pool's stratigraphic unit, or None."""
        if pool_code.startswith("085"):
            up = pool_name.upper()
            for text, s, e in self.mfp:
                if text in up:
                    return s, e, "MFP_TABLE"
            return None
        try:
            c = int(pool_code[1:5])
        except ValueError:
            return None
        for s, e, _ in self.families:
            if s == c:
                return s, e, "POOL_CODE+FAMILY"
        return c, c + 1, "POOL_CODE"

    def window_range(self, start, end):
        """Range used to place the unit in a well: widen members to their family."""
        if end - start > 1:
            return start, end
        fam = self.families_containing(start)
        return (fam[0][0], fam[0][1]) if fam else (start, end)

    def licence_codes(self, text):
        up = " " + re.sub(r"[^A-Z0-9 ]", " ", (text or "").upper()) + " "
        found = set()
        for base, codes in self.name_codes.items():
            if f" {base} " in up:
                found |= codes
        return found

    def codes_between_inside(self, a, b, rs, re_):
        """True if every AER formation code strictly between a and b lies in [rs, re_)."""
        for c in self.sorted_codes:
            if a < c < b and not (rs <= c < re_) and not self.fcodes[c].startswith("BASE OF"):
                return False
        return True


# ------------------------------------------------------------------ main logic
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--st103", required=True)
    ap.add_argument("--ref-dir", default=".")
    ap.add_argument("--wells-geometry", help="CSV: Well_Identifier,Horizontal_Drill,Final_Total_Depth,Max_True_Vertical_Depth")
    ap.add_argument("--no-depth-assumption", action="store_true")
    ap.add_argument("--out", default="match_results_v3")
    args = ap.parse_args()

    ref = Ref(args.ref_dir)
    depth_ok = not args.no_depth_assumption

    st103 = defaultdict(list)
    for r in read_csv(args.st103):
        g = (r["Geological_Pool_Code"] or "").strip()
        if g:
            st103[(r["Field_Code"].strip(), r["Production_Pool_Code"].strip())].append((g, r["Geological_Pool_Name"].strip()))

    geometry = {}
    if args.wells_geometry:
        for r in read_csv(args.wells_geometry):
            geometry[petrinex_to_uwi(r["Well_Identifier"])] = r

    strings = load_sheet(args.data, "ProductionStrings")
    completions = load_sheet(args.data, "CompletionInterval")
    perfs = load_sheet(args.data, "PerfTreatment")
    tops_rows = load_sheet(args.data, "GeologicalTopsMarkers")
    licences = load_sheet(args.data, "LicenceDetails")

    string_by_uwi = {r["Prod String UWI Formatted"]: r for r in strings}
    tops_by_well = defaultdict(list)
    for r in tops_rows:
        d = num(r["Formation Depth"])
        m = re.match(r"^(\d+)\s+(.*)$", r["Formation"].strip())
        if d is not None and m:
            tops_by_well[r["Query_UWI"]].append(
                {"depth": d, "code": int(m.group(1)), "name": m.group(2).strip(), "quality": r["Quality"].strip()})
    licence_by_well = {r["Query_UWI"]: r.get("Well Licence Purpose", "").strip() for r in licences}

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    summary, pool_rows, interval_rows = [], [], []

    for req in sorted({r["Requested_UWI"] for r in strings if r["Requested_UWI"]}):
        flags = []
        query = next(r["Query_UWI"] for r in strings if r["Requested_UWI"] == req)
        s = string_by_uwi.get(req) or next(r for r in strings if r["Requested_UWI"] == req)
        if req not in string_by_uwi:
            flags.append("REQUESTED_STRING_NOT_FOUND")
        string_uwi = s["Prod String UWI Formatted"]
        field = s["Field Id"].strip().zfill(4) if s["Field Id"].strip() else ""
        ppool = s["Pool ID"].strip().zfill(7) if s["Pool ID"].strip() else ""
        status = " ".join(x for x in (s["Status Fluid"], s["Status Mode"], s["Status Type"]) if x and x != "N/A")
        if any(c in s["Status Fluid"].upper() for c in CBM_STATUS):
            flags.append("CBM_STATUS")

        if ppool:
            candidates = st103.get((field, ppool), [])
        elif s["Deposit ID"].strip():
            candidates = [(s["Deposit ID"].strip().zfill(7), s["Deposit Name"].strip())]
            flags.append("OIL_SANDS_DEPOSIT")
        else:
            candidates = []
        commingled = len(candidates) > 1 or "COMMINGLED" in s["Pool Name"].upper()

        # Rule 1 screening (information only)
        g = geometry.get(query) or geometry.get(req)
        screen = "NO_GEOMETRY_DATA"
        if g:
            td, tvd = num(g.get("Final_Total_Depth")), num(g.get("Max_True_Vertical_Depth"))
            if td and tvd:
                screen = "PASS_<1%" if abs(td - tvd) / td < TVD_SCREEN else f"FAIL_{abs(td - tvd) / td:.1%}"
            else:
                screen = "TVD_MISSING_OR_ZERO"
            screen += f" ({g.get('Horizontal_Drill', '')})"

        # producing intervals of this string
        comp = [(num(r["Gross Completion Interval Top"]), num(r["Gross Completion Interval Base"]))
                for r in completions if r["Prod String UWI Formatted"] == string_uwi]
        comp = [(t, b) for t, b in comp if t is not None and b is not None]
        intervals = []
        for r in perfs:
            if r["Query_UWI"] != query or not any(k in r["Perf Treatment Type"].upper() for k in PERF_TYPES):
                continue
            t, b = num(r["Perf Treatment Top Depth (m)"]), num(r["Perf Treatment Base Depth (m)"])
            if t is None or b is None:
                continue
            if comp and not any(min(b, cb) - max(t, ct) >= 0 for ct, cb in comp):
                continue
            intervals.append({"top": t, "base": b, "src": f"PerfTreatment {r['Perf Treatment Type']} {r['Perf Treatment Date'][:10]}"})
        if not intervals:
            intervals = [{"top": t, "base": b, "src": "CompletionInterval"} for t, b in comp]
        if not comp:
            flags.append("NO_COMPLETION_INTERVAL")
        # merge identical intervals
        uniq = {}
        for iv in intervals:
            uniq.setdefault((iv["top"], iv["base"]), iv)
        intervals = sorted(uniq.values(), key=lambda x: x["top"])

        tops = sorted(tops_by_well.get(query, []), key=lambda x: x["depth"])
        lic_text = licence_by_well.get(query, "")
        lic_codes = ref.licence_codes(lic_text)
        has_tops = bool(tops) and depth_ok
        if not tops:
            flags.append("NO_TOPS")

        # ---------------- A. geological unit per interval
        unit_results = []
        for iv in intervals:
            t, b = iv["top"], iv["base"]
            za = max((x for x in tops if x["depth"] <= t + TOL), key=lambda x: x["depth"], default=None)
            zb = min((x for x in tops if x["depth"] >= b - TOL and (za is None or x["depth"] > za["depth"])),
                     key=lambda x: x["depth"], default=None)
            iv["za"], iv["zb"] = za, zb
            if not has_tops or za is None:
                unit_results.append(("ABOVE FIRST TOP" if tops else "NO TOPS", "Unresolved",
                                     "", "Unresolved", "no picked top above the interval" if tops else "no tops"))
                if tops and za is None:
                    flags.append("INTERVAL_ABOVE_FIRST_TOP")
                continue
            # most specific unit
            boundary = (t - za["depth"] < TOL) or (zb is not None and zb["depth"] - b < TOL)
            if zb is None:
                flags.append("INTERVAL_BELOW_LAST_TOP")
            # group / family: narrowest unit that is proven to contain the interval
            za2 = max((x for x in tops if x["depth"] <= t - TOL), key=lambda x: x["depth"], default=None)
            zb2 = min((x for x in tops if x["depth"] >= b + TOL), key=lambda x: x["depth"], default=None)
            fams = ref.families_containing(za["code"]) or [(za["code"], za["code"] + 1, za["name"])]
            chosen, g_label = None, "Probable"
            for fs, fe, fn in fams:
                if (za2 is not None and zb2 is not None and fs <= za2["code"] < fe and zb2["code"] <= fe
                        and ref.codes_between_inside(za2["code"], zb2["code"], fs, fe)
                        and za2["quality"].startswith("Good") and zb2["quality"].startswith("Good")):
                    chosen, g_label = (fs, fe, fn), "Confirmed"
                    break
            gs, ge, gname = chosen or fams[0]
            g_ev = (f"bounded by {za2['code']} {za2['name']} @ {za2['depth']} m" if za2 else "no top above") + " and " + \
                   (f"{zb2['code']} {zb2['name']} @ {zb2['depth']} m" if zb2 else "no top below") + \
                   f"; unit code range {gs}-{ge}"
            ms_label = "Confirmed" if (g_label == "Confirmed" and za["code"] == gs and not boundary) else "Probable"
            unit_results.append((f"{za['code']} {za['name']}", ms_label, gname, g_label, g_ev))

        # ---------------- B. each candidate pool
        cand_eval = []
        for code, name in candidates:
            rng = ref.pool_range(code, name)
            row = {"code": code, "name": name, "label": "", "basis": "", "score": 0, "reasons": [], "rel": []}
            if rng is None:
                row.update(label="Unresolved", reasons=["no stratigraphic unit mapping for this pool"])
                cand_eval.append(row)
                continue
            rs, re_, rsrc = rng
            ws, we = ref.window_range(rs, re_)
            row["unit"] = f"{rs}-{re_} ({rsrc})"
            if not has_tops or not intervals:
                why = "depth reference not accepted" if not depth_ok else ("no tops in well" if not tops else "no producing interval")
                row.update(label="Unresolved", reasons=[why])
                row["lic"] = any(rs <= c < re_ for c in lic_codes)
                cand_eval.append(row)
                continue
            upper = max((x for x in tops if x["code"] <= ws), key=lambda x: (x["code"], x["depth"]), default=None)
            lower = min((x for x in tops if x["code"] >= we and (upper is None or x["depth"] > upper["depth"])),
                        key=lambda x: x["depth"], default=None)
            direct = any(rs <= x["code"] < re_ for x in tops)
            row["basis"] = "DIRECT" if direct else "INFERRED_CODE_ORDER"
            row["window"] = (f"{upper['depth'] if upper else 'open'} to {lower['depth'] if lower else 'open'} m "
                             f"(tops {upper['code'] if upper else '-'} / {lower['code'] if lower else '-'})")
            for iv in intervals:
                t, b = iv["top"], iv["base"]
                if lower is not None and t > lower["depth"] + TOL:
                    rel = "EXCLUDED"
                elif upper is not None and b < upper["depth"] - TOL:
                    rel = "EXCLUDED"
                elif iv["za"] is None:
                    rel = "POSSIBLE" if upper is None else "UNKNOWN_ABOVE_FIRST_TOP"
                else:
                    za, zb = iv["za"], iv["zb"]
                    definite = (zb is not None and rs <= za["code"] < re_
                                and ref.codes_between_inside(za["code"], zb["code"], rs, re_)
                                and t >= za["depth"] + TOL and b <= zb["depth"] - TOL
                                and za["quality"].startswith("Good") and zb["quality"].startswith("Good"))
                    rel = "DEFINITE" if definite else "POSSIBLE"
                row["rel"].append(rel)
            # score (Rule 3)
            if any(r in ("DEFINITE", "POSSIBLE") and iv["za"] and ws <= iv["za"]["code"] < we
                   for r, iv in zip(row["rel"], intervals)):
                row["score"] += 2
                row["reasons"].append("+2 pool unit contains the most specific unit of the interval")
            if any(rs <= c < re_ for c in lic_codes):
                row["score"] += 1
                row["reasons"].append("+1 licence purpose names a formation in this unit")
            if re.search(r"\bBASAL\b|\bBSL\b", name.upper()) and lower is not None:
                gaps = [lower["depth"] - iv["base"] for r, iv in zip(row["rel"], intervals) if r in ("DEFINITE", "POSSIBLE")]
                if gaps and min(gaps) > BASAL_GAP:
                    row["score"] -= 1
                    row["reasons"].append(f"-1 basal pool, interval {min(gaps):.0f} m above group base ({lower['name']})")
            cand_eval.append(row)

        # labels need all candidates (sole-candidate test)
        for i, iv in enumerate(intervals):
            iv["n_possible"] = sum(1 for c in cand_eval if c.get("rel") and c["rel"][i] in ("DEFINITE", "POSSIBLE"))
        for c in cand_eval:
            if c["label"]:
                continue
            rels = c["rel"]
            sole_def = [rels[i] == "DEFINITE" and intervals[i]["n_possible"] == 1 for i in range(len(rels))]
            if all(r == "EXCLUDED" for r in rels) and c["basis"] == "DIRECT":
                c["label"] = "Not Supported"
            elif all(r == "EXCLUDED" for r in rels):
                c["label"] = "Unresolved"
                c["reasons"].append("outside the interval only by stratigraphic sequence; unit top not picked in this well (owner rule: keep Unresolved)")
            elif all(sole_def) and not commingled and c["code"] == ppool:
                c["label"] = "Confirmed"
            elif any(sole_def):
                c["label"] = "Probable"
            elif any(r in ("DEFINITE", "POSSIBLE") for r in rels):
                c["label"] = "Candidate"
            elif all(r in ("EXCLUDED", "UNKNOWN_ABOVE_FIRST_TOP") for r in rels):
                c["label"] = "Unresolved"
                c["reasons"].append("excluded where tops exist; position unknown above first top")
            else:
                c["label"] = "Unresolved"
                c["reasons"].append("interval position relative to this unit not determined")
        cands = [c for c in cand_eval if c["label"] == "Candidate"]
        if cands:
            best = max(c["score"] for c in cands)
            leaders = [c for c in cands if c["score"] == best]
            if len(leaders) == 1:
                leaders[0]["leading"] = True
        unres = [c for c in cand_eval if c["label"] == "Unresolved" and "lic" in c]
        for c in unres:
            if c.get("lic"):
                c["reasons"].append("licence purpose names a formation in this unit (weak evidence)")

        for i, iv in enumerate(intervals):
            ur = unit_results[i]
            if has_tops and iv.get("n_possible", 0) == 0 and candidates:
                flags.append("INTERVAL_WITH_NO_POSSIBLE_CANDIDATE")
            interval_rows.append({
                "Requested_UWI": req, "Interval_Top_m": iv["top"], "Interval_Base_m": iv["base"],
                "Interval_Source": iv["src"],
                "Top_Above": f"{iv['za']['code']} {iv['za']['name']} @ {iv['za']['depth']} ({iv['za']['quality']})" if iv["za"] else "",
                "Top_Below": f"{iv['zb']['code']} {iv['zb']['name']} @ {iv['zb']['depth']} ({iv['zb']['quality']})" if iv.get("zb") else "",
                "Most_Specific_Unit": ur[0], "Most_Specific_Label": ur[1],
                "Geological_Group": ur[2], "Group_Label": ur[3], "Group_Evidence": ur[4],
                "Possible_Candidates": iv.get("n_possible", "")})

        for c in cand_eval:
            pool_rows.append({
                "Requested_UWI": req, "Field_Code": field, "Production_Pool_Code": ppool,
                "Geological_Pool_Code": c["code"], "Geological_Pool_Name": c["name"],
                "Pool_Unit_Code_Range": c.get("unit", ""), "Label": c["label"],
                "Leading_Candidate": "Y" if c.get("leading") else "",
                "Score": c["score"] if c["label"] in ("Candidate", "Probable", "Confirmed") else "",
                "Score_Reasons": "; ".join(c["reasons"]), "Evidence_Basis": c["basis"],
                "Unit_Depth_Window": c.get("window", ""),
                "Interval_Relations": "; ".join(f"{iv['top']:g}-{iv['base']:g}:{r}" for iv, r in zip(intervals, c["rel"]))})

        groups = sorted({(u[2], u[3]) for u in unit_results if u[2]})
        units = sorted({(u[0], u[1]) for u in unit_results})
        cnt = defaultdict(int)
        for c in cand_eval:
            cnt[c["label"]] += 1
        summary.append({
            "Requested_UWI": req, "Wellbore_UWI": query, "Field_Name": s["Field_Name"],
            "Production_Pool_Code": ppool, "Production_Pool_Name": s["Pool Name"] or s["Deposit Name"],
            "String_Status": status, "Producing_Intervals_m": "; ".join(f"{iv['top']:g}-{iv['base']:g}" for iv in intervals),
            "Geological_Group": "; ".join(f"{g} [{l}]" for g, l in groups) or "Unresolved",
            "Most_Specific_Unit": "; ".join(f"{u} [{l}]" for u, l in units),
            "ST103_Candidates": len(candidates),
            "Confirmed": cnt["Confirmed"], "Probable": cnt["Probable"], "Candidate": cnt["Candidate"],
            "Not_Supported": cnt["Not Supported"], "Unresolved": cnt["Unresolved"],
            "Confirmed_or_Probable_Pools": "; ".join(f"{c['code']} {c['name']} [{c['label']}]" for c in cand_eval if c["label"] in ("Confirmed", "Probable")),
            "Leading_Candidate": "; ".join(f"{c['code']} {c['name']}" for c in cand_eval if c.get("leading")),
            "Depth_Reference": "MD/MD, tops datum KB assumed" if depth_ok else "NOT ACCEPTED",
            "TD_TVD_Screen": screen,
            "Flags": "; ".join(dict.fromkeys(flags)),
            "Licence_Purpose": lic_text})

    def write(name, rows):
        if rows:
            with open(out / name, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)

    write("string_summary_v3.csv", summary)
    write("pool_candidates_v3.csv", pool_rows)
    write("producing_intervals_v3.csv", interval_rows)
    print(f"Strings processed: {len(summary)}   candidate-pool rows: {len(pool_rows)}")
    for lab in ("Confirmed", "Probable", "Candidate", "Not Supported", "Unresolved"):
        print(f"  {lab:14} {sum(r['Label'] == lab for r in pool_rows)}")
    print(f"Output: {out.resolve()}")


if __name__ == "__main__":
    main()
