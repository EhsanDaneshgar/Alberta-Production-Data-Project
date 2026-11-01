"""
AER General Well Data extractor (v2)

v2 changes: (1) AER reports are keyed by the wellbore UWI (event /0).
   The script now queries the /0 event first; if ProductionStrings is
   empty it falls back to the original event. Requested_UWI is kept.
(2) WellInformation removed (it only returned today's date).

Downloads well-level reports from the free AER Tableau site as CSV.
It uses Tableau's built-in ".csv" export of each report sheet
(no screen scraping of JavaScript).

Reports (sheets) downloaded per well:
  ProductionStrings, LicenceDetails, CompletionInterval, PerfTreatment,
  GeologicalTopsMarkers, StatusHistory, WellInformation, PlugbackAbandonment

INPUT : a text or CSV file with one well per line, either
        - Petrinex 16-char Well_Identifier   e.g. 102080207706W402
        - AER formatted UWI                  e.g. 02/08-02-077-06W4/2
        (if CSV, the first column is used; a header line is skipped)
OUTPUT: one CSV per sheet in the output folder (all wells appended,
        with a Query_UWI column), plus extract_log.csv.
        Re-running skips (well, sheet) pairs already logged as OK.

Usage (Windows):
  python aer_well_extract_v2.py wells.txt --out aer_extract --delay 2

Be polite: keep --delay >= 2 seconds. Test with 5-10 wells first.
AER terms: free reuse with attribution; commercial redistribution
needs AER written permission (media@aer.ca).
"""

import argparse
import csv
import io
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests

BASE = "https://www2.aer.ca/t/Production/views/PRD_0100_Well_Summary_Report_View/"
PARAM = "Enter Well Identifier (UWI)"
SHEETS = [
    "ProductionStrings",
    "LicenceDetails",
    "CompletionInterval",
    "PerfTreatment",
    "GeologicalTopsMarkers",
    "StatusHistory",
    "PlugbackAbandonment",
]

AER_UWI = re.compile(r"^\d{2}/\d{2}-\d{2}-\d{3}-\d{2}W\d/\d$")
PETRINEX_ID = re.compile(r"^1(\d{2})(\d{2})(\d{2})(\d{3})(\d{2})W(\d)(\d{2})$")


def to_aer_uwi(value):
    """Return AER formatted UWI, or None if the value is not valid."""
    v = value.strip().upper()
    if v.startswith("ABWI"):
        v = v[4:]
    if AER_UWI.match(v):
        return v
    m = PETRINEX_ID.match(v)
    if not m:
        return None
    le, lsd, sec, twp, rng, mer, ev = m.groups()
    return f"{le}/{lsd}-{sec}-{twp}-{rng}W{mer}/{int(ev)}"


def base_uwi(uwi):
    """Same well, event sequence 0 (the AER report key)."""
    return uwi[:-1] + "0"


def fetch_csv(s, sheet, uwi):
    url = f"{BASE}{sheet}.csv?{quote(PARAM)}={quote(uwi, safe='')}"
    r = s.get(url, timeout=90)
    ctype = r.headers.get("content-type", "")
    if r.status_code == 200 and "csv" in ctype:
        return r.content.decode("utf-8-sig"), ""
    return None, f"HTTP {r.status_code} {ctype}"


def count_rows(csv_text):
    rows = list(csv.reader(io.StringIO(csv_text)))
    return sum(1 for r in rows[1:] if any(c.strip() for c in r))


def read_wells(path):
    wells, bad = [], []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            if not row or not row[0].strip():
                continue
            uwi = to_aer_uwi(row[0])
            if uwi:
                if uwi not in wells:
                    wells.append(uwi)
            else:
                bad.append(row[0].strip())
    # first invalid line is usually a header
    return wells, bad


def load_done(log_path):
    done = set()
    if log_path.exists():
        with open(log_path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["Status"] == "OK":
                    done.add((r["Requested_UWI"], r["Sheet"]))
    return done


def append_rows(out_file, requested_uwi, query_uwi, csv_text):
    rows = list(csv.reader(io.StringIO(csv_text)))
    if len(rows) <= 1:
        return 0
    header, data = rows[0], [r for r in rows[1:] if any(c.strip() for c in r)]
    new_file = not out_file.exists()
    with open(out_file, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["Requested_UWI", "Query_UWI"] + header)
        for r in data:
            w.writerow([requested_uwi, query_uwi] + r)
    return len(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="file with one well per line")
    ap.add_argument("--out", default="aer_extract", help="output folder")
    ap.add_argument("--delay", type=float, default=2.0, help="seconds between requests")
    ap.add_argument("--sheets", default=",".join(SHEETS), help="comma list of sheets")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    log_path = out / "extract_log.csv"
    sheets = [s.strip() for s in args.sheets.split(",") if s.strip()]

    wells, bad = read_wells(args.input)
    print(f"Valid wells: {len(wells)}   Invalid lines skipped: {len(bad)}")
    if bad:
        print("  first invalid values:", bad[:5])

    done = load_done(log_path)
    new_log = not log_path.exists()
    log_f = open(log_path, "a", newline="", encoding="utf-8")
    log = csv.writer(log_f)
    if new_log:
        log.writerow(["Requested_UWI", "Query_UWI", "Sheet", "Status", "Rows", "Message", "Time"])

    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (personal research; AER well data)"
    # Open one view first so the server gives a guest session cookie.
    try:
        s.get(BASE + sheets[0] + "?:embed=y", timeout=60)
    except requests.RequestException as e:
        print("Cannot reach AER site:", e)
        sys.exit(1)

    for i, uwi in enumerate(wells, 1):
        # Decide which UWI the AER reports use for this well.
        query_uwi = base_uwi(uwi)
        try:
            text, _ = fetch_csv(s, "ProductionStrings", query_uwi)
            time.sleep(args.delay)
            if (text is None or count_rows(text) == 0) and query_uwi != uwi:
                query_uwi = uwi
        except requests.RequestException:
            query_uwi = uwi

        for sheet in sheets:
            if (uwi, sheet) in done:
                continue
            status, n, msg = "ERROR", 0, ""
            try:
                text, msg = fetch_csv(s, sheet, query_uwi)
                if text is not None:
                    n = append_rows(out / f"{sheet}.csv", uwi, query_uwi, text)
                    status = "OK"
            except requests.RequestException as e:
                msg = str(e)[:200]
            log.writerow([uwi, query_uwi, sheet, status, n, msg,
                          time.strftime("%Y-%m-%d %H:%M:%S")])
            log_f.flush()
            time.sleep(args.delay)
        print(f"[{i}/{len(wells)}] {uwi} -> {query_uwi} done")

    log_f.close()
    print(f"Finished. Output folder: {out.resolve()}")


if __name__ == "__main__":
    main()
