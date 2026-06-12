"""
AIRIS Census 2011 Baseline Extractor
======================================
Reads DDW_PCA0000_2011_Indiastatedist.xlsx and extracts
district-level control variables for Karnataka, Bihar, Rajasthan.

Outputs: database/seeds/district_baseline_2011.csv

Variables extracted:
  population, rural_population, urban_population, urban_share
  literacy_rate, male_literacy_rate, female_literacy_rate
  sc_share, st_share
  worker_participation_rate, main_worker_share
  agri_worker_share (CL + AL), other_worker_share (HH + OT)

Level filter: TRU="Total" at district level (Subdistt=0, Town/Village=0, Ward=0, EB=0)
"""

import pandas as pd
import numpy as np
import os

CENSUS_FILE  = "database/seeds/DDW_PCA0000_2011_Indiastatedist.xlsx"
CROSSWALK    = "database/seeds/airis_master_crosswalk.csv"
OUT_FILE     = "database/seeds/district_baseline_2011.csv"

# State codes in Census 2011 — stored as zero-padded strings e.g. "08", "10", "29"
TARGET_STATES = {8: "Rajasthan", 10: "Bihar", 29: "Karnataka"}
TARGET_STATE_STR = {f"{k:02d}": v for k, v in TARGET_STATES.items()}  # {'08':..,'10':..,'29':..}

print("Loading Census 2011...")
df = pd.read_excel(CENSUS_FILE, sheet_name="Sheet1", dtype=str)

# Convert numeric columns — keep State, District, Level, Name, TRU as strings
num_cols = [c for c in df.columns if c not in ["Level", "Name", "TRU", "State", "District"]]
for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

print(f"  Total rows: {len(df)}")
print(f"  Levels available: {df['Level'].unique()}")
print(f"  TRU values: {df['TRU'].unique()}")

# Filter: district level = "DISTRICT", Total (not rural/urban breakdown)
# Level hierarchy in Census: INDIA > STATE > DISTRICT > SUBDIST > TOWN/VILLAGE
dist_df = df[
    (df["Level"] == "DISTRICT") &
    (df["TRU"] == "Total") &
    (df["State"].isin(TARGET_STATE_STR.keys()))
].copy()

print(f"  District-Total rows for target states: {len(dist_df)}")

# Also get rural/urban rows for rural_pop / urban_pop split
rural_df = df[
    (df["Level"] == "DISTRICT") &
    (df["TRU"] == "Rural") &
    (df["State"].isin(TARGET_STATE_STR.keys()))
].copy()

urban_df = df[
    (df["Level"] == "DISTRICT") &
    (df["TRU"] == "Urban") &
    (df["State"].isin(TARGET_STATE_STR.keys()))
].copy()

rows = []
for _, row in dist_df.iterrows():
    state_str   = row["State"]
    state_code  = int(state_str)
    dist_code   = int(row["District"])
    state_name  = TARGET_STATE_STR.get(state_str, "Unknown")
    dist_name   = row["Name"]

    tot_pop     = row["TOT_P"]
    tot_m       = row["TOT_M"]
    tot_f       = row["TOT_F"]

    # Rural/urban split — match from rural_df / urban_df
    r_match = rural_df[(rural_df["State"] == row["State"]) & (rural_df["District"] == row["District"])]
    u_match = urban_df[(urban_df["State"] == row["State"]) & (urban_df["District"] == row["District"])]
    rural_pop = r_match["TOT_P"].values[0] if len(r_match) else np.nan
    urban_pop = u_match["TOT_P"].values[0] if len(u_match) else np.nan
    urban_share = (urban_pop / tot_pop * 100) if tot_pop else np.nan

    # Literacy rate (persons aged 7+ who are literate)
    lit_p   = row["P_LIT"]
    lit_m   = row["M_LIT"]
    lit_f   = row["F_LIT"]
    # Total population minus 0-6 age group = eligible population
    pop_7plus = tot_pop - row["P_06"]
    pop_7plus_m = tot_m - row["M_06"]
    pop_7plus_f = tot_f - row["F_06"]
    lit_rate   = (lit_p / pop_7plus * 100) if pop_7plus else np.nan
    lit_rate_m = (lit_m / pop_7plus_m * 100) if pop_7plus_m else np.nan
    lit_rate_f = (lit_f / pop_7plus_f * 100) if pop_7plus_f else np.nan

    # SC/ST shares
    sc_share = (row["P_SC"] / tot_pop * 100) if tot_pop else np.nan
    st_share = (row["P_ST"] / tot_pop * 100) if tot_pop else np.nan

    # Worker participation: total workers / total population
    tot_workers = row["TOT_WORK_P"]
    wpr = (tot_workers / tot_pop * 100) if tot_pop else np.nan

    # Main worker share = main workers / total workers
    main_workers = row["MAINWORK_P"]
    main_share = (main_workers / tot_workers * 100) if tot_workers else np.nan

    # Agricultural worker share = (CL + AL) / total workers
    # CL = Cultivators, AL = Agricultural Labourers
    # Main + Marginal workers in CL/AL
    agri_main = (row.get("MAIN_CL_P", 0) or 0) + (row.get("MAIN_AL_P", 0) or 0)
    agri_marg = (row.get("MARG_CL_P", 0) or 0) + (row.get("MARG_AL_P", 0) or 0)
    agri_workers = agri_main + agri_marg
    agri_share_wk = (agri_workers / tot_workers * 100) if tot_workers else np.nan

    # Other workers (HH = Household Industry, OT = Other)
    other_main = (row.get("MAIN_HH_P", 0) or 0) + (row.get("MAIN_OT_P", 0) or 0)
    other_marg = (row.get("MARG_HH_P", 0) or 0) + (row.get("MARG_OT_P", 0) or 0)
    other_workers = other_main + other_marg
    other_share_wk = (other_workers / tot_workers * 100) if tot_workers else np.nan

    # Census district code in standard format matching crosswalk (e.g. "29-201")
    census_code = f"{state_code}-{dist_code}"

    rows.append({
        "state":                  state_name,
        "state_code_census":      state_code,
        "census_district_code":   census_code,
        "district_name_census":   dist_name,
        "population":             int(tot_pop) if not pd.isna(tot_pop) else None,
        "rural_population":       int(rural_pop) if not pd.isna(rural_pop) else None,
        "urban_population":       int(urban_pop) if not pd.isna(urban_pop) else None,
        "urban_share":            round(urban_share, 2) if not pd.isna(urban_share) else None,
        "literacy_rate":          round(lit_rate, 2)   if not pd.isna(lit_rate) else None,
        "male_literacy_rate":     round(lit_rate_m, 2) if not pd.isna(lit_rate_m) else None,
        "female_literacy_rate":   round(lit_rate_f, 2) if not pd.isna(lit_rate_f) else None,
        "sc_share":               round(sc_share, 2) if not pd.isna(sc_share) else None,
        "st_share":               round(st_share, 2) if not pd.isna(st_share) else None,
        "worker_participation_rate": round(wpr, 2) if not pd.isna(wpr) else None,
        "main_worker_share":      round(main_share, 2) if not pd.isna(main_share) else None,
        "agri_worker_share":      round(agri_share_wk, 2) if not pd.isna(agri_share_wk) else None,
        "other_worker_share":     round(other_share_wk, 2) if not pd.isna(other_share_wk) else None,
        "data_year":              2011,
        "source":                 "Census 2011 PCA District-level (DDW_PCA0000_2011_Indiastatedist.xlsx)",
    })

result = pd.DataFrame(rows)
result.to_csv(OUT_FILE, index=False)

print(f"\nSaved: {OUT_FILE}")
print(f"Districts extracted: {len(result)}")
print(f"\nBy state:")
print(result.groupby("state").agg(
    districts=("district_name_census", "count"),
    avg_pop=("population", "mean"),
    avg_literacy=("literacy_rate", "mean"),
    avg_agri_share=("agri_worker_share", "mean"),
).round(1).to_string())

print(f"\nSample rows:")
print(result[result["state"]=="Karnataka"][
    ["district_name_census","population","urban_share","literacy_rate","agri_worker_share"]
].head(8).to_string(index=False))
