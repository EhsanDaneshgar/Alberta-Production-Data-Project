"""
Alberta Energy Maps (GeoView) bulk export (v1)

Downloads public layers from the Government of Alberta GeoView map services
(ArcGIS REST, gis.energy.gov.ab.ca) page by page and saves them as files.
Alberta only.

Layers exported
  wells          ERCB_Ext_PROD/2   all wells: UWI, operator, status, lat/long  (CSV)
  well_paths     ERCB_Ext_PROD/9   KB, TD, max TVD, surface + bottom-hole lat/long (CSV)
  png_agreements Mineral_Agreements_Ext_PROD/31  Crown PNG agreements: rights holders
                 with % interest, zone of rights, status  (CSV + GeoJSON polygons)
  non_crown_png  Mineral_Ownership_Ext_PROD/5  lands where PNG minerals are NOT
                 owned by the Alberta Crown (GeoJSON polygons)

Output: ab_energy_maps\\YYYY-MM-DD\\<layer>.csv / .geojson

Usage (Windows):
  python ab_energy_maps_export_v1.py                 (all layers)
  python ab_energy_maps_export_v1.py --layers wells png_agreements
Run time: roughly 10-30 minutes in total (estimate, not measured).
"""

import argparse
import csv
import json
import time
from datetime import date
from pathlib import Path

import requests

BASE = "https://gis.energy.gov.ab.ca/arcgis/rest/services/Geoview/"
LAYERS = {
    "wells":          {"path": "ERCB_Ext_PROD/MapServer/2", "page": 50000, "geojson": False, "point": True},
    "well_paths":     {"path": "ERCB_Ext_PROD/MapServer/9", "page": 50000, "geojson": False, "point": False},
    "png_agreements": {"path": "Mineral_Agreements_Ext_PROD/MapServer/31", "page": 1000, "geojson": True, "point": False},
    "non_crown_png":  {"path": "Mineral_Ownership_Ext_PROD/MapServer/5", "page": 1000, "geojson": True, "point": False},
}


def get_json(session, url, params, tries=4):
    for i in range(tries):
        try:
            r = session.get(url, params=params, timeout=180)
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                raise RuntimeError(data["error"])
            return data
        except Exception as e:  # network or server error: wait and retry
            if i == tries - 1:
                raise
            print(f"   retry {i + 1} after error: {e}")
            time.sleep(10 * (i + 1))


def export_layer(session, name, cfg, folder, delay):
    url = BASE + cfg["path"] + "/query"
    total = get_json(session, url, {"f": "json", "where": "1=1", "returnCountOnly": "true"})["count"]
    print(f"{name}: {total} records")

    csv_path = folder / f"{name}.csv"
    geo_path = folder / f"{name}.geojson"
    csv_file = open(csv_path, "w", newline="", encoding="utf-8")
    writer = None
    geo_file = open(geo_path, "w", encoding="utf-8") if cfg["geojson"] else None
    if geo_file:
        geo_file.write('{"type":"FeatureCollection","features":[\n')
    first_feature = True

    offset, done = 0, 0
    while offset < total:
        want_geom = cfg["point"] or cfg["geojson"]
        params = {
            "where": "1=1", "outFields": "*", "orderByFields": "OBJECTID" if name in ("wells", "well_paths") else "ObjectId",
            "resultOffset": offset, "resultRecordCount": cfg["page"],
            "returnGeometry": "true" if want_geom else "false", "outSR": "4326",
            "f": "geojson" if cfg["geojson"] else "json",
        }
        data = get_json(session, url, params)
        feats = data.get("features", [])
        if not feats:
            break
        for ft in feats:
            attrs = dict(ft.get("properties") or ft.get("attributes") or {})
            if cfg["point"]:
                g = ft.get("geometry") or {}
                pts = g.get("points") or ([[g["x"], g["y"]]] if "x" in g else [])
                attrs["Longitude"], attrs["Latitude"] = (pts[0] if pts else (None, None))
            attrs.pop("SHAPE", None)
            if writer is None:
                writer = csv.DictWriter(csv_file, fieldnames=list(attrs), extrasaction="ignore")
                writer.writeheader()
            writer.writerow(attrs)
            if geo_file:
                geo_file.write(("" if first_feature else ",\n") + json.dumps(ft))
                first_feature = False
        done += len(feats)
        offset += len(feats)
        print(f"   {done}/{total}")
        time.sleep(delay)

    csv_file.close()
    if geo_file:
        geo_file.write("\n]}\n")
        geo_file.close()
    status = "OK" if done == total else f"INCOMPLETE ({done} of {total})"
    print(f"   {status} -> {csv_path.name}" + (f", {geo_path.name}" if geo_file else ""))
    return name, total, done, status


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layers", nargs="+", default=list(LAYERS), choices=list(LAYERS))
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "ab_energy_maps"))
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    args = ap.parse_args()

    folder = Path(args.out) / date.today().isoformat()
    folder.mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (personal research; Alberta GeoView export)"

    log = []
    for name in args.layers:
        try:
            log.append(export_layer(s, name, LAYERS[name], folder, args.delay))
        except Exception as e:
            print(f"{name}: FAILED {e}")
            log.append((name, "", "", f"FAILED {e}"))
    with open(folder / "export_log.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Layer", "Records_On_Server", "Records_Saved", "Status"])
        w.writerows(log)
    print(f"Saved in: {folder}")


if __name__ == "__main__":
    main()
