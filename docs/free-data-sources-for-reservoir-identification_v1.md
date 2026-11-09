# Data Sources for Reservoir and Formation Identification (v1)

**Project:** Alberta Oil & Gas Production Data Platform
**Date:** November 8, 2026
**Status:** Source review. Items marked "estimate" or "assumed" are not verified. No data was purchased.

## 1. What we need

To judge each ST103 candidate pool of a well (see the pilot documentation, section 5), we need for each well:

1. the **perforation / completion intervals** of the current production string (measured depth),
2. the **formation tops** picked in the well,
3. the **well location**, for pools defined by map area,
4. **commingling approvals**, which can support Not Supported.

## 2. Summary

| Source | Cost | Gives | Does not give | Status in the project |
| --- | --- | --- | --- | --- |
| AER ST103 (`FieldPoolList`) | Free | Candidate Geological Pools for a Field + Production Pool | The actual producing pool of a well | Imported (68,515 rows) |
| AER General Well Data, Tableau reports | Free | Per-well production strings, perforations, tops, licence details | A bulk download. One well at a time. | 10 pilot wells downloaded |
| AER ST2 weekly reports | Free | Weekly drilling data, perforation data for about 460 wells (1 week checked) | History. AER keeps only the current week. | Weekly download scheduled |
| AER ST37 (monthly list of wells) | Free | Surface and bottom-hole location, KB, TD, max TVD, production string with Field / Pool / Deposit | Tops and perforations | Reviewed |
| AER DE/SD commingling list | Free | Which wells have commingling approvals | The approved intervals inside the approval text | Imported (14,832 rows) |
| AER MU orders (per-field PDFs) | Free | Commingling approval text by field | A downloadable index | Reviewed, not used yet |
| AER pool order shapefile | Free | Pool boundaries for area-based pools | Depth information | Not used yet |
| AGS Table of Formations (2019) | Free | Formation names and order | Well-specific data | Used to check the draft unit tables |
| AGS Atlas tables | Free | Isopachs and structure tops for a subset of wells | Coverage of all wells | Imported (4 tables, including the data dictionary) |
| Alberta Energy Maps (GeoView) | Free | Well points and well paths, Crown agreements, non-Crown mineral lands | Tops and perforations | 3 of 4 layers exported |
| AER General Well Data bulk file | Paid | Bulk well data | | **Not purchased** |
| Commercial well databases | Paid | Tops and perforations in bulk | | Access not confirmed |

## 3. Details by source

### AER General Well Data (Tableau)
- Each report sheet downloads as CSV. Reports are keyed by the wellbore UWI (event `/0`).
- Speed: about 1 minute per well (pilot estimate). For all 665,307 wells that is about 460 days (derived estimate).
- This is the only free source with tops and perforations for any chosen well, but it is too slow for all wells.
- AER content may be reused with attribution. Commercial redistribution requires AER written permission.

### AER ST2 weekly reports
- 15 CSV files from the AER Tableau site. AER keeps only the current week.
- The script `aer_st2_download_v1.py` saves them into a dated folder every Monday (Windows scheduled task). This builds our own history.
- In the one week checked, about 460 wells had perforation data. If this held every week, it would be up to about 24,000 wells per year (460 x 52, derived estimate; weekly counts will vary).
- ST2 does not replace the Tableau reports for wells already drilled.

### AER ST37
- Free monthly list of wells.
- Useful for location, KB, TD, max TVD and the production string with Field / Pool / Deposit.
- It has no tops and no perforations.

### Commingling orders (DE, MU)
- DE1 covers the zone from the top of the Edmonton Grp to the base of the Belly River Grp. DE2 covers the Smoky Grp to the Nikanassin.
- MU orders are published as one PDF per field (`static.aer.ca/prd/data/muorders/<FIELD>_MU<number>.pdf`). No downloadable index was found.
- DE1 order evidence may be used for Not Supported. It is not coded in matcher v3 yet.

### AER pool order shapefile
- Needed for pools defined by map area (for example Bow Island A to D), which depth cannot separate.
- Not used yet.

### Alberta Energy Maps (GeoView)
Exported with `ab_energy_maps_export_v1.py`:

| Layer | Records saved | Use |
| --- | --- | --- |
| `wells` | 667,586 | Well points, operator, status |
| `well_paths` | 226,675 | KB, TD, max TVD, surface and bottom-hole location |
| `non_crown_png` | 269,348 | Lands where minerals are not owned by the Crown |
| `png_agreements` | not saved | Crown rights holders, % interest, zone. The server service was not started on November 7 and 8, 2026. Retry later. |

- Alberta only. Agreements cover Crown land only. Freehold mineral owners are not in the free bulk data.
- The terms of use of these layers have not been checked for redistribution.

## 4. The gap

No free source gives tops and perforations for all wells in bulk. Options being considered:

1. Download more wells from Tableau in controlled batches, with approval (see the pilot documentation, next steps).
2. Accumulate ST2 weekly files.
3. Obtain access to a commercial database or a data sponsor (not confirmed).

The AER bulk General Well Data file is paid and was not purchased.
