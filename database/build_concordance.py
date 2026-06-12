"""
AIRIS Phase 4A — Task 1: District Name Concordance Table
=========================================================
Produces: database/seeds/district_name_concordance.csv

Columns:
  state                 : State name
  state_code_plfs       : PLFS state code
  plfs_2019_code        : Sequential district code in 2019-20
  plfs_2021_code        : Sequential district code in 2021-22 (PROBABLE)
  plfs_2023_code        : Sequential district code in 2023-24
  district_name_plfs_2019  : Name as it appears in PLFS 2019-20 panel output
  district_name_plfs_2021  : Name as it appears in PLFS 2021-22 panel output
  district_name_plfs_2023  : Name as it appears in PLFS 2023-24 panel output
  district_name_standard   : AIRIS canonical name (from master crosswalk)
  district_name_census     : Name as in Census 2011 DDW file
  district_name_bharatnet  : Name used in BharatNet dataset
  census_code_resolved     : Census district code (DDW format) used for merge
  bharatnet_treatment      : BharatNet timing group
  concordance_status       : EXACT / SPELLING / RENAMED / MISSING
"""

import pandas as pd
import os

PANEL_DIR = "data/clean/panel"
os.makedirs("database/seeds", exist_ok=True)

# Load crosswalk (already has Census info)
cw = pd.read_csv("database/seeds/airis_master_crosswalk_with_census.csv")

# Load Census DDW for district_name_census
cen_raw = pd.read_excel(
    "database/seeds/DDW_PCA0000_2011_Indiastatedist.xlsx",
    sheet_name="Sheet1", dtype=str
)
cen_names = cen_raw[
    (cen_raw["Level"] == "DISTRICT") & (cen_raw["TRU"] == "Total")
][["State", "District", "Name"]].copy()
cen_names["Name"] = cen_names["Name"].str.strip()

# Build state-district name lookup from Census
def census_name_for(state_int, dist_code_str):
    s = str(state_int).zfill(2)
    matches = cen_names[
        (cen_names["State"] == s) | (cen_names["State"] == str(state_int))
    ]
    # dist_code is last 3 chars of census_code_resolved after hyphen
    return None

# Load each PLFS panel to extract actual district names as output by builder
def load_panel_names(state_code, year):
    path = f"{PANEL_DIR}/plfs_panel_state{state_code}_{year}.csv"
    if not os.path.exists(path):
        return {}
    df = pd.read_csv(path)
    # Returns {district_code: district_name}
    return dict(zip(
        df["district_code"].astype(str),
        df["district_name"].str.strip()
    ))

STATE_CODES = {"Karnataka": 29, "Bihar": 10, "Rajasthan": 8}
YEARS = [2019, 2021, 2023]

# Load all panel name lookups
panel_names = {}
for state_name, sc in STATE_CODES.items():
    panel_names[sc] = {}
    for yr in YEARS:
        panel_names[sc][yr] = load_panel_names(sc, yr)

# Load Census name lookup keyed by resolved code
cen_lookup = {}
if "census_code_resolved" in cw.columns:
    for _, row in cw.iterrows():
        cen_lookup[row["census_code_resolved"]] = None  # filled below

cen_dist_file = pd.read_csv("database/seeds/district_baseline_2011.csv")
cen_name_by_code = dict(zip(
    cen_dist_file["census_district_code"].astype(str),
    cen_dist_file["district_name_census"].str.strip()
))

rows = []
for _, cw_row in cw.iterrows():
    sc   = int(cw_row["state_code_plfs"])
    c19  = str(cw_row["plfs_2019_code"]) if pd.notna(cw_row["plfs_2019_code"]) else None
    c21  = str(cw_row["plfs_2021_code"]) if pd.notna(cw_row["plfs_2021_code"]) else None
    c23  = str(cw_row["plfs_2023_code"]) if pd.notna(cw_row["plfs_2023_code"]) else None

    # Fix: integer codes like 1.0 → "1"
    for code_var, attr in [("plfs_2019_code","plfs_2019_code"),
                           ("plfs_2021_code","plfs_2021_code"),
                           ("plfs_2023_code","plfs_2023_code")]:
        val = cw_row[attr]
        if pd.notna(val):
            try:
                val = str(int(float(val)))
            except:
                val = str(val)
        else:
            val = None
        if attr == "plfs_2019_code": c19 = val
        if attr == "plfs_2021_code": c21 = val
        if attr == "plfs_2023_code": c23 = val

    n19 = panel_names[sc][2019].get(c19, "MISSING") if c19 else "NO_CODE"
    n21 = panel_names[sc][2021].get(c21, "MISSING") if c21 else "NO_CODE"
    n23 = panel_names[sc][2023].get(c23, "MISSING") if c23 else "NO_CODE"
    n_std = str(cw_row["district_name_standard"]).strip()
    n_bn  = str(cw_row["bharatnet_district_name"]).strip()
    n_cen = cen_name_by_code.get(str(cw_row.get("census_code_resolved", "")), "")

    # Concordance status
    names_seen = {n for n in [n19, n21, n23] if n not in ("MISSING", "NO_CODE")}
    if all(n == n_std for n in names_seen) and n_std == n_bn:
        status = "EXACT"
    elif names_seen and any(n.lower() == n_std.lower() for n in names_seen):
        status = "EXACT"
    elif names_seen:
        status = "SPELLING"
    else:
        status = "MISSING"

    rows.append({
        "state":                   cw_row["state"],
        "state_code_plfs":         sc,
        "plfs_2019_code":          c19,
        "plfs_2021_code":          c21,
        "plfs_2023_code":          c23,
        "district_name_plfs_2019": n19,
        "district_name_plfs_2021": n21,
        "district_name_plfs_2023": n23,
        "district_name_standard":  n_std,
        "district_name_census":    n_cen,
        "district_name_bharatnet": n_bn,
        "census_code_resolved":    cw_row.get("census_code_resolved", ""),
        "bharatnet_treatment":     cw_row["bharatnet_treatment"],
        "concordance_status":      status,
        "plfs_2021_col_status":    cw_row.get("plfs_2021_code_status", ""),
    })

df_conc = pd.DataFrame(rows)
out = "database/seeds/district_name_concordance.csv"
df_conc.to_csv(out, index=False)
print(f"Saved: {out}")
print(f"Rows: {len(df_conc)}")
print()
print("Concordance status breakdown:")
print(df_conc["concordance_status"].value_counts().to_string())
print()
print("SPELLING differences (sample):")
sp = df_conc[df_conc["concordance_status"] == "SPELLING"][
    ["state","district_name_standard","district_name_plfs_2019",
     "district_name_plfs_2023","district_name_census","district_name_bharatnet"]
]
print(sp.head(20).to_string(index=False))
print()
print("MISSING districts:")
ms = df_conc[df_conc["concordance_status"] == "MISSING"]
print(ms[["state","district_name_standard","plfs_2019_code","plfs_2023_code"]].to_string(index=False))
