"""
AIRIS Phase 4 — District Identifier Verification (2021-22)
============================================================
Verifies that b1q4_perrv in the 2021-22 PLFS file is the district code
by cross-validating against 2019-20 and 2023-24 district-level sample
size distributions.

Method:
  - Extract per-district record counts for Karnataka from each round
  - Compute Spearman rank correlation between 2021-22 b1q4 vs 2019-20 district_per_rv
  - Compute Spearman rank correlation between 2021-22 b1q4 vs 2023-24 dist_code_perrv
  - If rank correlation > 0.80, b1q4_perrv is confirmed as district code
  - Also verify for Bihar (state=10) and Rajasthan (state=8)

Output: prints verification table, saves to research/district_id_verification.csv
"""

import pandas as pd
import numpy as np
from scipy.stats import spearmanr
import zipfile
import os

DATA_DIR = "data/raw/plfs"
OUT_PATH = "research/district_id_verification.csv"
os.makedirs("research", exist_ok=True)

STATES = {29: "Karnataka", 10: "Bihar", 8: "Rajasthan"}

FILES = {
    "2019": {
        "zip": f"{DATA_DIR}/CSV_PLFS_19_20.zip",
        "inner": "CSV_PLFS_19_20/PERRV_2019-20.csv",
        "state_col": "state_per_rv",
        "dist_col": "district_per_rv",
        "weight_col": "MULT_per_rv",
    },
    "2021": {
        "zip": f"{DATA_DIR}/PLFS_Data_2021-22_CSV.zip",
        "inner": "PLFS_Data_2021-22_CSV/perrv.csv",
        "state_col": "state_perrv",
        "dist_col": "b1q4_perrv",   # <-- candidate to verify
        "weight_col": "mult_perrv",
    },
    "2023": {
        "zip": f"{DATA_DIR}/CSV_data_PLFS_2023_2024.zip",
        "inner": "CSV_data_PLFS_2023_2024/perrv.csv",
        "state_col": "state_perrv",
        "dist_col": "dist_code_perrv",
        "weight_col": "mult_perrv",
    },
}

def get_dist_counts(year_key, state_code):
    """Returns Series: district_code -> n_records for given state."""
    cfg = FILES[year_key]
    with zipfile.ZipFile(cfg["zip"]) as z:
        with z.open(cfg["inner"]) as f:
            df = pd.read_csv(f, low_memory=False,
                             usecols=[cfg["state_col"], cfg["dist_col"], cfg["weight_col"]])
    state_s = pd.to_numeric(df[cfg["state_col"]], errors="coerce")
    df_s = df[state_s == state_code].copy()
    counts = df_s.groupby(cfg["dist_col"]).size().rename("n_records")
    return counts.sort_values(ascending=False)

results = []
print("="*70)
print("DISTRICT IDENTIFIER VERIFICATION — PLFS 2021-22 (b1q4_perrv)")
print("="*70)

for state_code, state_name in STATES.items():
    print(f"\n--- {state_name} (state={state_code}) ---")

    c19 = get_dist_counts("2019", state_code)
    c21 = get_dist_counts("2021", state_code)
    c23 = get_dist_counts("2023", state_code)

    n19, n21, n23 = len(c19), len(c21), len(c23)
    print(f"  2019-20 districts: {n19} | 2021-22 districts: {n21} | 2023-24 districts: {n23}")

    # Align 2021 with 2019 (same district codes expected for same districts)
    merged_1921 = pd.merge(
        c19.reset_index().rename(columns={c19.index.name: "dist_code", "n_records": "n19"}),
        c21.reset_index().rename(columns={c21.index.name: "dist_code", "n_records": "n21"}),
        on="dist_code", how="inner"
    )
    merged_2123 = pd.merge(
        c21.reset_index().rename(columns={c21.index.name: "dist_code", "n_records": "n21"}),
        c23.reset_index().rename(columns={c23.index.name: "dist_code", "n_records": "n23"}),
        on="dist_code", how="inner"
    )

    rho_1921, p_1921 = spearmanr(merged_1921["n19"], merged_1921["n21"]) if len(merged_1921) > 3 else (None, None)
    rho_2123, p_2123 = spearmanr(merged_2123["n21"], merged_2123["n23"]) if len(merged_2123) > 3 else (None, None)

    verdict_1921 = "CONFIRMED ✓" if rho_1921 and rho_1921 > 0.80 else ("PROBABLE (~)" if rho_1921 and rho_1921 > 0.60 else "UNCERTAIN ✗")
    verdict_2123 = "CONFIRMED ✓" if rho_2123 and rho_2123 > 0.80 else ("PROBABLE (~)" if rho_2123 and rho_2123 > 0.60 else "UNCERTAIN ✗")

    print(f"  Rank corr (2019 vs 2021): ρ={rho_1921:.3f} p={p_1921:.4f} → {verdict_1921}")
    print(f"  Rank corr (2021 vs 2023): ρ={rho_2123:.3f} p={p_2123:.4f} → {verdict_2123}")
    print(f"  Districts matched (2019↔2021): {len(merged_1921)}")
    print(f"  Districts matched (2021↔2023): {len(merged_2123)}")

    results.append({
        "state": state_name,
        "state_code": state_code,
        "districts_2019": n19,
        "districts_2021": n21,
        "districts_2023": n23,
        "matched_2019_2021": len(merged_1921),
        "matched_2021_2023": len(merged_2123),
        "spearman_rho_2019_2021": round(rho_1921, 3) if rho_1921 else None,
        "spearman_p_2019_2021": round(p_1921, 4) if p_1921 else None,
        "verdict_2021_col": verdict_1921,
    })

df_out = pd.DataFrame(results)
df_out.to_csv(OUT_PATH, index=False)
print(f"\nSaved: {OUT_PATH}")
print("\nSummary:")
print(df_out[["state","districts_2019","districts_2021","districts_2023",
              "spearman_rho_2019_2021","verdict_2021_col"]].to_string(index=False))
