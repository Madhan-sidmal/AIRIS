"""
AIRIS Phase 4D — LFPR / WPR Extractor
========================================
Extracts Labour Force Participation Rate (LFPR) and Worker Population Ratio (WPR)
from PLFS microdata for all 9 rounds (3 states × 3 years).

LFPR = Labour Force (employed + unemployed) / Working-Age Population (15+)
WPR  = Employed Workers / Working-Age Population (15+)

These are computed at district level, weighted by PLFS multiplier.

Output: data/clean/panel/plfs_lfpr_{state}_{year}.csv
         data/clean/panel/airis_lfpr_wpr_all.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import zipfile
import sys
import os

sys.path.insert(0, '.')
# Re-use config from panel_builder
from pipelines.transformers.plfs_panel_builder import (
    load_plfs_rural, normalise_columns, COLUMN_ALIASES,
    EMPLOYED_CODES_OLD, EMPLOYED_CODES_NEW,
    UNEMP_CODES_OLD, UNEMP_CODES_NEW,
    LABOUR_FORCE_OLD, LABOUR_FORCE_NEW,
)

DATA_DIR = Path("data/raw/plfs")
OUT_DIR  = Path("data/clean/panel")
os.makedirs(str(OUT_DIR), exist_ok=True)

CROSSWALK = pd.read_csv("database/seeds/airis_master_crosswalk_with_census.csv")
STATE_NAMES = {29: "Karnataka", 10: "Bihar", 8: "Rajasthan"}

RUNS = [
    (29, 2019), (29, 2021), (29, 2023),
    (10, 2019), (10, 2021), (10, 2023),
    ( 8, 2019), ( 8, 2021), ( 8, 2023),
]

def find_zip(year):
    short = str(year)[2:]
    next_short = str(year + 1)[2:]
    candidates = (
        list(DATA_DIR.glob(f"*{year}*.zip")) +
        list(DATA_DIR.glob(f"*{short}_{next_short}*.zip")) +
        list(DATA_DIR.glob(f"*{year}-{year+1}*.zip")) +
        list(DATA_DIR.glob(f"*{year}-{next_short}*.zip"))
    )
    return candidates[0] if candidates else None

def extract_lfpr(state_code, year):
    """Extract LFPR and WPR for one state-year."""
    zip_path = find_zip(year)
    if zip_path is None:
        print(f"  SKIP: No ZIP for {year}")
        return pd.DataFrame()

    print(f"\n  {STATE_NAMES[state_code]} {year}: loading {zip_path.name}")
    df = load_plfs_rural(zip_path, year)
    df = normalise_columns(df, year)

    # ── Filter to state ──────────────────────────────────────────────────────
    state_col = next((c for c in df.columns
                      if c in ["state_code_col", "state_perrv", "State", "state"]), None)
    if state_col:
        df = df[pd.to_numeric(df[state_col], errors='coerce') == state_code].copy()
    print(f"  State records: {len(df):,}")

    if len(df) == 0:
        return pd.DataFrame()

    # ── Detect coding scheme ─────────────────────────────────────────────────
    act_col = next((c for c in df.columns
                    if c in ["activity_status", "b4q4_perrv", "B_019", "B_020"]), None)
    if act_col is None:
        print(f"  ERROR: no activity column found")
        return pd.DataFrame()

    act_vals = set(pd.to_numeric(df[act_col], errors='coerce').dropna().unique())
    is_new   = max(act_vals) <= 9
    emp_codes = EMPLOYED_CODES_NEW if is_new else EMPLOYED_CODES_OLD
    lf_codes  = LABOUR_FORCE_NEW   if is_new else LABOUR_FORCE_OLD
    print(f"  Coding: {'2023-24 (1-digit)' if is_new else '2019-20 (2-digit)'}")

    # ── Age column ───────────────────────────────────────────────────────────
    age_col = next((c for c in df.columns
                    if c in ["age", "b2q3_perrv", "b2q3_per_rv", "B_005", "B_004"]), None)
    if age_col is None:
        # Try to find any column likely to be age
        age_col = next((c for c in df.columns if "age" in c.lower()), None)

    if age_col:
        df["age_num"] = pd.to_numeric(df[age_col], errors='coerce')
        df_wa = df[df["age_num"] >= 15].copy()  # Working age: 15+
        print(f"  Working-age (15+): {len(df_wa):,} / {len(df):,} total")
    else:
        print(f"  WARNING: no age column found — using all persons (LFPR approximate)")
        df_wa = df.copy()

    if "weight" not in df_wa.columns:
        # Try to find weight
        for wc in ["mult_perrv", "MULT_PERRV", "mult_per_rv", "MULT_per_rv", "wt", "MULT"]:
            if wc in df_wa.columns:
                df_wa["weight"] = pd.to_numeric(df_wa[wc], errors='coerce').fillna(0)
                break

    df_wa["weight"] = pd.to_numeric(df_wa.get("weight", 0), errors='coerce').fillna(0)
    df_wa["act_num"] = pd.to_numeric(df_wa[act_col], errors='coerce')
    df_wa["is_lf"]   = df_wa["act_num"].isin(lf_codes)
    df_wa["is_emp"]  = df_wa["act_num"].isin(emp_codes)

    # ── Crosswalk for state ──────────────────────────────────────────────────
    cw_state = CROSSWALK[CROSSWALK["state_code_plfs"] == state_code].copy()
    code_col = "plfs_2019_code" if year in [2019, 2021] else "plfs_2023_code"
    if year == 2021:
        code_col = "plfs_2021_code"
    cw_lookup = {}
    for _, row in cw_state.iterrows():
        code = row.get(code_col)
        if pd.notna(code):
            try:
                cw_lookup[int(float(code))] = row["district_name_standard"]
            except:
                pass

    # ── Compute district-level LFPR and WPR ─────────────────────────────────
    results = []
    for dist_code, grp in df_wa.groupby("district_code"):
        try:
            dc = int(float(dist_code))
        except:
            continue

        pop_w  = grp["weight"].sum()
        lf_w   = grp[grp["is_lf"]]["weight"].sum()
        emp_w  = grp[grp["is_emp"]]["weight"].sum()

        if pop_w == 0:
            continue

        lfpr = lf_w  / pop_w * 100
        wpr  = emp_w / pop_w * 100
        nilf_share = (pop_w - lf_w) / pop_w * 100

        dist_name = cw_lookup.get(dc, f"UNKNOWN_{dc}")

        results.append({
            "district_code":         dc,
            "district_name_standard": dist_name,
            "state_code_plfs":       state_code,
            "state":                 STATE_NAMES[state_code],
            "survey_year":           year,
            "lfpr_wt":               round(lfpr, 3),
            "wpr_wt":                round(wpr, 3),
            "nilf_share_wt":         round(nilf_share, 3),
            "n_persons_wa":          len(grp),
            "pop_weight_sum":        round(pop_w, 0),
            "lf_weight_sum":         round(lf_w, 0),
            "emp_weight_sum":        round(emp_w, 0),
            "age_filter_applied":    age_col is not None,
            "coding_scheme":         "2023-24" if is_new else "2019-20",
        })

    out_df = pd.DataFrame(results)
    n_valid = len(out_df[~out_df["district_name_standard"].str.startswith("UNKNOWN", na=False)])
    print(f"  Districts extracted: {len(out_df)} | Named: {n_valid}")
    print(f"  LFPR range: {out_df['lfpr_wt'].min():.1f}% – {out_df['lfpr_wt'].max():.1f}%")
    print(f"  WPR range:  {out_df['wpr_wt'].min():.1f}% – {out_df['wpr_wt'].max():.1f}%")

    # Save individual panel
    out_path = OUT_DIR / f"plfs_lfpr_state{state_code}_{year}.csv"
    out_df.to_csv(out_path, index=False)
    return out_df


# ── Run all 9 ─────────────────────────────────────────────────────────────────
print("=" * 65)
print("AIRIS Phase 4D — LFPR/WPR Extraction (all 9 rounds)")
print("=" * 65)

all_frames = []
for sc, yr in RUNS:
    frame = extract_lfpr(sc, yr)
    if len(frame) > 0:
        all_frames.append(frame)

lfpr_all = pd.concat(all_frames, ignore_index=True)

# Save combined
out_combined = OUT_DIR / "airis_lfpr_wpr_all.csv"
lfpr_all.to_csv(out_combined, index=False)

print("\n" + "=" * 65)
print(f"Combined LFPR/WPR panel: {len(lfpr_all)} rows")
print("=" * 65)
print("\nSummary by state and year:")
print(lfpr_all.groupby(["state","survey_year"])[["lfpr_wt","wpr_wt"]].mean().round(1).to_string())

print("\nMissing district names (UNKNOWN):")
unk = lfpr_all[lfpr_all["district_name_standard"].str.startswith("UNKNOWN", na=False)]
print(f"  {len(unk)} rows ({len(lfpr_all)} total)")

print(f"\nSaved: {out_combined}")
