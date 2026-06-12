"""
AIRIS Phase 4 — Master Panel Assembly + Validation Reports
============================================================
Produces:
  1. airis_panel_master.csv                     (regression-ready dataset)
  2. research/AIRIS_Treatment_Validation_Report.md
  3. research/AIRIS_Balance_Table.md
  4. research/AIRIS_Parallel_Trends_Report.md

Run AFTER all 9 panels have been extracted via plfs_panel_builder.py
"""

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind, mannwhitneyu
import os
import warnings
warnings.filterwarnings('ignore')

os.makedirs("research", exist_ok=True)
os.makedirs("data/clean/panel", exist_ok=True)

# ─── 1. Load crosswalk and Census controls ────────────────────────────────────
print("Loading crosswalk and Census controls...")
xw  = pd.read_csv("database/seeds/airis_master_crosswalk.csv")
cen = pd.read_csv("database/seeds/district_baseline_2011.csv")

# Merge Census controls into crosswalk
# Census uses numeric state code + sequential district code
# Join on census_district_code (format "STATE-DISTCODE")
merged_xw = xw.merge(
    cen[["census_district_code","population","rural_population","urban_share",
         "literacy_rate","female_literacy_rate","sc_share","st_share",
         "worker_participation_rate","agri_worker_share"]],
    on="census_district_code", how="left"
)
print(f"  Crosswalk rows: {len(xw)} | After Census merge: {len(merged_xw)}")
print(f"  Census controls matched: {merged_xw['literacy_rate'].notna().sum()}")

# ─── 2. Load all 9 PLFS panels ───────────────────────────────────────────────
print("\nLoading PLFS panels...")
PANEL_FILES = {
    (29, 2019): "data/clean/panel/plfs_panel_state29_2019.csv",
    (29, 2021): "data/clean/panel/plfs_panel_state29_2021.csv",
    (29, 2023): "data/clean/panel/plfs_panel_state29_2023.csv",
    (10, 2019): "data/clean/panel/plfs_panel_state10_2019.csv",
    (10, 2021): "data/clean/panel/plfs_panel_state10_2021.csv",
    (10, 2023): "data/clean/panel/plfs_panel_state10_2023.csv",
    ( 8, 2019): "data/clean/panel/plfs_panel_state8_2019.csv",
    ( 8, 2021): "data/clean/panel/plfs_panel_state8_2021.csv",
    ( 8, 2023): "data/clean/panel/plfs_panel_state8_2023.csv",
}
STATE_NAMES = {29: "Karnataka", 10: "Bihar", 8: "Rajasthan"}

panels = []
for (sc, yr), fpath in PANEL_FILES.items():
    if os.path.exists(fpath):
        df = pd.read_csv(fpath)
        df["state_code_plfs"] = sc
        df["state"] = STATE_NAMES[sc]
        panels.append(df)
        print(f"  Loaded {STATE_NAMES[sc]} {yr}: {len(df)} districts")
    else:
        print(f"  MISSING: {fpath}")

plfs_all = pd.concat(panels, ignore_index=True)
print(f"  Total PLFS records: {len(plfs_all)}")

# ─── 3. Join PLFS panels with crosswalk ──────────────────────────────────────
print("\nJoining PLFS with crosswalk...")

# The crosswalk has plfs_2019_code which is the sequential district code
# For 2021, use plfs_2021_code (same sequential scheme, PROBABLE)
# For 2023, use plfs_2023_code

# Melt crosswalk for year-specific joining
xw_2019 = merged_xw.rename(columns={"plfs_2019_code": "district_code"})[
    ["state_code_plfs","district_code","district_name_standard","bharatnet_treatment",
     "state_group","panel_usable_2x2","panel_usable_3period","data_quality_flag",
     "boundary_note","population","rural_population","urban_share",
     "literacy_rate","female_literacy_rate","sc_share","st_share",
     "worker_participation_rate","agri_worker_share"]
].copy()
xw_2019["join_year"] = 2019

xw_2021 = merged_xw.rename(columns={"plfs_2021_code": "district_code"})[
    ["state_code_plfs","district_code","district_name_standard","bharatnet_treatment",
     "state_group","panel_usable_2x2","panel_usable_3period","data_quality_flag",
     "boundary_note","population","rural_population","urban_share",
     "literacy_rate","female_literacy_rate","sc_share","st_share",
     "worker_participation_rate","agri_worker_share"]
].copy()
xw_2021["join_year"] = 2021

xw_2023 = merged_xw.rename(columns={"plfs_2023_code": "district_code"})[
    ["state_code_plfs","district_code","district_name_standard","bharatnet_treatment",
     "state_group","panel_usable_2x2","panel_usable_3period","data_quality_flag",
     "boundary_note","population","rural_population","urban_share",
     "literacy_rate","female_literacy_rate","sc_share","st_share",
     "worker_participation_rate","agri_worker_share"]
].copy()
xw_2023["join_year"] = 2023

xw_long = pd.concat([xw_2019, xw_2021, xw_2023], ignore_index=True)
xw_long["district_code"] = pd.to_numeric(xw_long["district_code"], errors="coerce")

# Join PLFS to crosswalk
panel = plfs_all.merge(
    xw_long,
    left_on=["state_code_plfs","district_code","survey_year"],
    right_on=["state_code_plfs","district_code","join_year"],
    how="left"
)

print(f"  Panel after join: {len(panel)} rows")
print(f"  Treatment assigned: {panel['bharatnet_treatment'].notna().sum()}")
print(f"  Unknown districts: {(panel['district_name_standard'].isna()).sum()}")

# Create standard variables for DiD
panel["post_2023"]   = (panel["survey_year"] == 2023).astype(int)
panel["early_treat"] = (panel["bharatnet_treatment"] == "early").astype(int)
panel["late_ctrl"]   = (panel["bharatnet_treatment"] == "late").astype(int)
panel["year_fe"]     = panel["survey_year"].astype(str)
panel["did_sample"]  = (
    panel["bharatnet_treatment"].isin(["early","late"]) &
    panel["panel_usable_2x2"].fillna(False) &
    (panel["sample_grade"].isin(["A","B","C"])) &
    (panel["survey_year"].isin([2019, 2023]))
).astype(int)

# Save master panel
out_path = "data/clean/panel/airis_panel_master.csv"
panel.to_csv(out_path, index=False)
print(f"\nSaved: {out_path}")
print(f"  Total rows: {len(panel)}")
print(f"  DiD-eligible rows (2x2, early+late, grade C+): {panel['did_sample'].sum()}")
print(f"  Districts in DiD sample: {panel[panel['did_sample']==1]['district_name_standard'].nunique()}")

# ─── 4. Compute statistics for reports ────────────────────────────────────────
# 2x2 DiD sample: early vs late, 2019 and 2023 only, grade C+
did = panel[panel["did_sample"] == 1].copy()

def grp_stats(df, grp_col, metrics):
    rows = []
    for grp, sub in df.groupby(grp_col):
        row = {"group": grp, "n": len(sub)}
        for m in metrics:
            vals = pd.to_numeric(sub[m], errors="coerce").dropna()
            row[f"{m}_mean"] = vals.mean()
            row[f"{m}_sd"]   = vals.std()
            row[f"{m}_p50"]  = vals.median()
        rows.append(row)
    return pd.DataFrame(rows)

OUTCOMES = ["unemp_rate_wt", "agri_share_wt", "nonagri_share_wt"]
CONTROLS = ["literacy_rate", "female_literacy_rate", "sc_share", "st_share",
            "urban_share", "worker_participation_rate", "agri_worker_share"]

# ─── Balance table ────────────────────────────────────────────────────────────
pre = panel[(panel["survey_year"] == 2019) & panel["bharatnet_treatment"].isin(["early","late"])
            & panel["sample_grade"].isin(["A","B","C"])].copy()

bal_rows = []
for var in CONTROLS + OUTCOMES:
    early_v = pd.to_numeric(pre[pre["bharatnet_treatment"]=="early"][var], errors="coerce").dropna()
    late_v  = pd.to_numeric(pre[pre["bharatnet_treatment"]=="late"][var], errors="coerce").dropna()
    if len(early_v) < 3 or len(late_v) < 3:
        continue
    diff = early_v.mean() - late_v.mean()
    # Normalized difference (Imbens-Rubin)
    pooled_sd = np.sqrt((early_v.var() + late_v.var()) / 2)
    norm_diff = diff / pooled_sd if pooled_sd > 0 else np.nan
    _, p_t = ttest_ind(early_v, late_v, equal_var=False)
    bal_rows.append({
        "variable": var,
        "early_mean": round(early_v.mean(), 2),
        "early_sd": round(early_v.std(), 2),
        "early_n": len(early_v),
        "late_mean": round(late_v.mean(), 2),
        "late_sd": round(late_v.std(), 2),
        "late_n": len(late_v),
        "diff": round(diff, 2),
        "norm_diff": round(norm_diff, 3),
        "p_ttest": round(p_t, 3),
        "balanced": "YES" if abs(norm_diff) < 0.25 else "CONCERN",
    })
balance_df = pd.DataFrame(bal_rows)

# ─── Parallel trends ─────────────────────────────────────────────────────────
pt_rows = []
for state in ["Karnataka", "Bihar", "Rajasthan", "ALL"]:
    for outcome in OUTCOMES:
        for grp in ["early", "late"]:
            sub = panel[
                (panel["bharatnet_treatment"] == grp) &
                (panel["sample_grade"].isin(["A","B","C"])) &
                (panel["survey_year"].isin([2019, 2021, 2023]))
            ]
            if state != "ALL":
                sub = sub[sub["state"] == state]
            for yr in [2019, 2021, 2023]:
                vals = pd.to_numeric(sub[sub["survey_year"]==yr][outcome], errors="coerce").dropna()
                if len(vals) >= 3:
                    pt_rows.append({
                        "state": state, "treatment_group": grp,
                        "outcome": outcome, "year": yr,
                        "mean": round(vals.mean(), 3),
                        "sd": round(vals.std(), 3),
                        "n": len(vals),
                    })

pt_df = pd.DataFrame(pt_rows)

# Pre-trend difference in differences (2019-2021)
pre_did_rows = []
for state in ["Karnataka", "Bihar", "Rajasthan", "ALL"]:
    for outcome in OUTCOMES:
        sub = panel[
            panel["sample_grade"].isin(["A","B","C"]) &
            panel["survey_year"].isin([2019, 2021]) &
            panel["bharatnet_treatment"].isin(["early","late"])
        ]
        if state != "ALL":
            sub = sub[sub["state"] == state]

        for grp in ["early", "late"]:
            g = sub[sub["bharatnet_treatment"] == grp]
            v19 = pd.to_numeric(g[g["survey_year"]==2019][outcome], errors="coerce").dropna().mean()
            v21 = pd.to_numeric(g[g["survey_year"]==2021][outcome], errors="coerce").dropna().mean()
            delta = v21 - v19 if not (pd.isna(v19) or pd.isna(v21)) else np.nan
            pre_did_rows.append({
                "state": state, "outcome": outcome, "group": grp,
                "val_2019": round(v19, 2) if not pd.isna(v19) else None,
                "val_2021": round(v21, 2) if not pd.isna(v21) else None,
                "delta_2019_2021": round(delta, 2) if not pd.isna(delta) else None,
            })

pre_did_df = pd.DataFrame(pre_did_rows)

# DiD pre-trend: early - late
pt_did_rows = []
for state in ["Karnataka", "Bihar", "Rajasthan", "ALL"]:
    for outcome in OUTCOMES:
        e = pre_did_df[(pre_did_df["state"]==state) & (pre_did_df["outcome"]==outcome) & (pre_did_df["group"]=="early")]
        l = pre_did_df[(pre_did_df["state"]==state) & (pre_did_df["outcome"]==outcome) & (pre_did_df["group"]=="late")]
        if len(e) and len(l):
            e_delta = e["delta_2019_2021"].values[0]
            l_delta = l["delta_2019_2021"].values[0]
            did_pre = (e_delta - l_delta) if not (pd.isna(e_delta) or pd.isna(l_delta)) else np.nan
            pt_did_rows.append({
                "state": state, "outcome": outcome,
                "early_delta": e_delta, "late_delta": l_delta,
                "pre_trend_did": round(did_pre, 3) if not pd.isna(did_pre) else None,
                "concern_level": "HIGH" if abs(did_pre) > 5 else "MODERATE" if abs(did_pre) > 2 else "LOW"
                if not pd.isna(did_pre) else "NA",
            })

pt_did_final = pd.DataFrame(pt_did_rows)

print("\n=== Pre-trend DiD Summary (2019→2021) ===")
print(pt_did_final.to_string(index=False))

# ─── Save CSVs ────────────────────────────────────────────────────────────────
balance_df.to_csv("research/airis_balance_table.csv", index=False)
pt_df.to_csv("research/airis_parallel_trends_data.csv", index=False)
pt_did_final.to_csv("research/airis_pretrend_did.csv", index=False)
print("\nSaved analysis CSVs to research/")

# ─── Summary for treatment validation ─────────────────────────────────────────
print("\n=== Treatment Group Summary (2x2 DiD eligible, Grade C+) ===")
did_summary = panel[
    (panel["survey_year"]==2019) &
    panel["sample_grade"].isin(["A","B","C"])
].groupby(["state","bharatnet_treatment"]).agg(
    n_districts=("district_name_standard","count"),
    mean_unemp=("unemp_rate_wt","mean"),
    mean_agri=("agri_share_wt","mean"),
    mean_literacy=("literacy_rate","mean"),
).round(2)
print(did_summary.to_string())

print("\nDone. Ready to write Markdown reports.")
print(f"\nDiD sample stats:")
print(f"  Total district-year obs: {len(panel)}")
print(f"  2x2 DiD eligible obs:    {panel['did_sample'].sum()}")
print(f"  Unique districts in DiD: {panel[panel['did_sample']==1]['district_name_standard'].nunique()}")
print(f"  Balance table rows:      {len(balance_df)}")
