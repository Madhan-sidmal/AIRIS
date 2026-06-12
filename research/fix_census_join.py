"""
Fix Census-to-crosswalk join using name-based matching.
The Census file uses old district names (Belgaum, Bijapur, etc.)
The crosswalk has both canonical names and bharatnet_district_names.

Strategy:
1. Add a census_name_key to the crosswalk (manually mapped for known differences)
2. Join Census controls into crosswalk via name key
3. Rerun build_master_panel.py
"""
import pandas as pd
import numpy as np
from difflib import get_close_matches
import os

cen = pd.read_csv("database/seeds/district_baseline_2011.csv")
xw  = pd.read_csv("database/seeds/airis_master_crosswalk.csv")

print("Building Census name key for crosswalk...")

# Build name lookup: census district_name_census → census_district_code
# Use state-level filtering to avoid cross-state collision
all_rows = []

for state_code, state_name in [(29,"Karnataka"), (10,"Bihar"), (8,"Rajasthan")]:
    cen_s = cen[cen["state_code_census"]==state_code].copy()
    xw_s  = xw[xw["state_code_plfs"]==state_code].copy()

    census_names = cen_s["district_name_census"].str.strip().tolist()
    census_codes = cen_s["census_district_code"].tolist()
    census_liter = cen_s["literacy_rate"].tolist()
    census_lookup = {n.strip().lower(): c for n, c in zip(census_names, census_codes)}

    matched = 0
    for i, row in xw_s.iterrows():
        # Try multiple name variants for matching
        candidates = [
            row["district_name_standard"],
            row["bharatnet_district_name"],
        ]
        found_code = None
        for cand in candidates:
            cand_l = str(cand).strip().lower()
            # Exact match
            if cand_l in census_lookup:
                found_code = census_lookup[cand_l]
                break
            # Fuzzy match
            close = get_close_matches(cand_l, list(census_lookup.keys()), n=1, cutoff=0.7)
            if close:
                found_code = census_lookup[close[0]]
                break

        if found_code:
            matched += 1
        row_d = row.to_dict()
        row_d["census_code_resolved"] = found_code
        all_rows.append(row_d)

    print(f"  {state_name}: {matched}/{len(xw_s)} matched")

xw_resolved = pd.DataFrame(all_rows)

# Merge Census controls using resolved code
census_controls = cen[["census_district_code","population","rural_population",
                        "urban_share","literacy_rate","female_literacy_rate",
                        "sc_share","st_share","worker_participation_rate","agri_worker_share"]].copy()

xw_final = xw_resolved.merge(
    census_controls,
    left_on="census_code_resolved",
    right_on="census_district_code",
    how="left",
    suffixes=("","_cen")
)

print(f"\nFinal crosswalk: {len(xw_final)} rows")
print(f"Census controls matched: {xw_final['literacy_rate'].notna().sum()}")

# Save updated crosswalk with Census controls
out = "database/seeds/airis_master_crosswalk_with_census.csv"
xw_final.to_csv(out, index=False)
print(f"Saved: {out}")

# Quick check
print("\nKarnataka literacy sample:")
ka = xw_final[xw_final["state_code_plfs"]==29][["district_name_standard","literacy_rate"]].dropna()
print(ka.head(8).to_string(index=False))
