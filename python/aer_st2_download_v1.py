"""
AER ST2 (Alberta Drilling Progress, weekly) downloader (v1)

Downloads the 15 free ST2 CSV files from the AER Tableau site into a
folder named with today's date, e.g.  ST2\\2026-11-01\\
Run it once a week to build your own history (AER keeps only the current week).

Usage (Windows):
  python aer_st2_download_v1.py
  python aer_st2_download_v1.py --out "C:\\some\\folder"
"""

import argparse
import time
from datetime import date
from pathlib import Path

import requests

BASE = "https://www2.aer.ca/t/Production/views/"
FILES = [
    "PRD_0010_ST2_IMB_Weekly_Status_Changes_CSV_EXT/WeeklyAbandonmentStatusChangesReport",
    "PRD_0010_ST2_IMB_Weekly_Status_Changes_CSV_EXT/WeeklyStatusChangesReport",
    "PRD_0020_ST2_IMB_Weekly_Released_Drilling_Data_CSV_EXT/WeeklyReleasedWellFormationReport",
    "PRD_0020_ST2_IMB_Weekly_Released_Drilling_Data_CSV_EXT/WeeklyReleasedWellInformationReport",
    "PRD_0020_ST2_IMB_Weekly_Released_Drilling_Data_CSV_EXT/WeeklyReleasedWellLogSummaryReport",
    "PRD_0020_ST2_IMB_Weekly_Released_Drilling_Data_CSV_EXT/WeeklyReleasedWellCasingReport",
    "PRD_0020_ST2_IMB_Weekly_Released_Drilling_Data_CSV_EXT/WeeklyReleasedWellPerforationTreatmentReport",
    "PRD_0020_ST2_IMB_Weekly_Released_Drilling_Data_CSV_EXT/WeeklyReleasedWellTourOccurrenceReport",
    "PRD_0025_ST2_IMB_Weekly_Drilling_Report_CSV_EXT/WeeklyDrillingReport",
    "PRD_0025_ST2_IMB_Weekly_Drilling_Report_CSV_EXT/WeeklyDrillingWellPerforationTreatmentReport",
    "PRD_0025_ST2_IMB_Weekly_Drilling_Report_CSV_EXT/WeeklyDrillingWellTourOccurrenceReport",
    "PRD_0025_ST2_IMB_Weekly_Drilling_Report_CSV_EXT/WeeklyDrillingUWIChangesReport",
    "PRD_0025_ST2_IMB_Weekly_Drilling_Report_CSV_EXT/WeeklyDrillingWellCasingReport",
    "PRD_0025_ST2_IMB_Weekly_Drilling_Report_CSV_EXT/WeeklyDrillingWellLicenceAmendmentsReport",
    "PRD_0025_ST2_IMB_Weekly_Drilling_Report_CSV_EXT/WeeklyDrillingWellLogSummaryReport",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent))
    args = ap.parse_args()

    folder = Path(args.out) / date.today().isoformat()
    folder.mkdir(parents=True, exist_ok=True)

    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (personal research; AER ST2 weekly)"
    for path in FILES:
        name = path.split("/")[-1]
        workbook = path.split("/")[0].replace("_CSV_EXT", "_EXT")
        try:
            s.get(BASE + workbook + "/" + name + "?:embed=y", timeout=60)  # guest session
            r = s.get(BASE + path + ".csv", timeout=120)
            if r.status_code == 200 and "csv" in r.headers.get("content-type", ""):
                (folder / f"{name}.csv").write_bytes(r.content)
                rows = max(0, r.content.decode("utf-8-sig").strip().count("\n"))
                print(f"OK    {name}: {rows} rows")
            else:
                print(f"ERROR {name}: HTTP {r.status_code} {r.headers.get('content-type')}")
        except requests.RequestException as e:
            print(f"ERROR {name}: {e}")
        time.sleep(2)
    print(f"Saved in: {folder}")


if __name__ == "__main__":
    main()
