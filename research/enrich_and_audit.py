"""
AIRIS Phase 4A — Tasks 2-4
===========================
Task 2: Complete Census enrichment (all controls joined via concordance)
Task 3: Rebuild airis_panel_master.csv with enriched controls
Task 4: Data quality audit (missingness by variable / state / treatment / year)
"""

import pandas as pd
import numpy as np
import os

os.makedirs("research", exist_ok=True)
os.makedirs("data/clean/panel", exist_ok=True)

# ─── Load data assets ────────────────────────────────────────────────────────
print("Loading assets...")
cw_cen = pd.read_csv("database/seeds/airis_master_crosswalk_with_census.csv")
conc   = pd.read_csv("database/seeds/district_name_concordance.csv")
STATE_NAMES = {29: "Karnataka", 10: "Bihar", 8: "Rajasthan"}
PANEL_DIR   = "data/clean/panel"

print(f"  Crosswalk with Census: {len(cw_cen)} rows | literacy notna: {cw_cen['literacy_rate'].notna().sum()}")

# ─── Load all 9 PLFS panels ───────────────────────────────────────────────────
print("Loading PLFS panels...")
panels = []
PANEL_FILES = [
    (29, 2019), (29, 2021), (29, 2023),
    (10, 2019), (10, 2021), (10, 2023),
    ( 8, 2019), ( 8, 2021), ( 8, 2023),
]
for sc, yr in PANEL_FILES:
    fpath = f"{PANEL_DIR}/plfs_panel_state{sc}_{yr}.csv"
    if os.path.exists(fpath):
        df = pd.read_csv(fpath)
        df["state_code_plfs"] = sc
        df["state"] = STATE_NAMES[sc]
        panels.append(df)
        print(f"  {STATE_NAMES[sc]} {yr}: {len(df)} districts")
    else:
        print(f"  MISSING: {fpath}")

plfs_all = pd.concat(panels, ignore_index=True)
print(f"  Total PLFS: {len(plfs_all)} rows")

# ─── Build year-specific crosswalk for join ────────────────────────────────────
# The crosswalk has plfs_2019_code / plfs_2021_code / plfs_2023_code
# We need to join each panel year to the right code column

CENSUS_CONTROLS = [
    "population", "rural_population", "urban_share",
    "literacy_rate", "female_literacy_rate", "sc_share", "st_share",
    "worker_participation_rate", "agri_worker_share"
]
META_COLS = [
    "state_code_plfs", "district_name_standard", "bharatnet_treatment",
    "state_group", "panel_usable_2x2", "panel_usable_3period",
    "data_quality_flag", "boundary_note", "census_code_resolved"
] + CENSUS_CONTROLS

def make_year_xw(cw, code_col, year):
    xw = cw[["state_code_plfs", code_col] + META_COLS[1:]].copy()
    xw = xw.rename(columns={code_col: "district_code"})
    xw["district_code"] = pd.to_numeric(xw["district_code"], errors="coerce")
    xw["join_year"] = year
    return xw.dropna(subset=["district_code"])

xw_2019 = make_year_xw(cw_cen, "plfs_2019_code", 2019)
xw_2021 = make_year_xw(cw_cen, "plfs_2021_code", 2021)
xw_2023 = make_year_xw(cw_cen, "plfs_2023_code", 2023)
xw_long  = pd.concat([xw_2019, xw_2021, xw_2023], ignore_index=True)

plfs_all["district_code_num"] = pd.to_numeric(plfs_all["district_code"], errors="coerce")

panel = plfs_all.merge(
    xw_long,
    left_on =["state_code_plfs", "district_code_num", "survey_year"],
    right_on=["state_code_plfs", "district_code",     "join_year"],
    how="left"
)
print(f"\nPanel after join: {len(panel)} rows")
print(f"  Treatment assigned:       {panel['bharatnet_treatment'].notna().sum()}")
print(f"  Literacy matched:         {panel['literacy_rate'].notna().sum()}")
print(f"  district_name_standard:   {panel['district_name_standard'].notna().sum()}")

# ─── Computed DiD variables ────────────────────────────────────────────────────
panel["post_2023"]      = (panel["survey_year"] == 2023).astype(int)
panel["early_treat"]    = (panel["bharatnet_treatment"] == "early").astype(int)
panel["late_ctrl"]      = (panel["bharatnet_treatment"] == "late").astype(int)
panel["treat_binary"]   = panel["early_treat"]   # 1=treated, 0=control (late only)
panel["post_early_did"] = panel["post_2023"] * panel["early_treat"]

# 2x2 DiD eligible: early or late, grade C+, years 2019 and 2023
panel["did_sample_2x2"] = (
    panel["bharatnet_treatment"].isin(["early", "late"]) &
    panel["panel_usable_2x2"].fillna(False) &
    panel["sample_grade"].isin(["A","B","C"]) &
    panel["survey_year"].isin([2019, 2023])
).astype(int)

# 3-period sample: early or late, grade C+, all 3 years
panel["did_sample_3period"] = (
    panel["bharatnet_treatment"].isin(["early","late"]) &
    panel["panel_usable_3period"].fillna(False) &
    panel["sample_grade"].isin(["A","B","C"])
).astype(int)

# Log population
panel["log_population"] = np.log(pd.to_numeric(panel["population"], errors="coerce"))

# Save
out_path = "data/clean/panel/airis_panel_master.csv"
panel.to_csv(out_path, index=False)
print(f"\nSaved: {out_path}")
print(f"  Rows: {len(panel)} | Columns: {len(panel.columns)}")
print(f"  2x2 DiD eligible rows:      {panel['did_sample_2x2'].sum()}")
print(f"  3-period eligible rows:     {panel['did_sample_3period'].sum()}")
print(f"  Unique districts (2x2 DiD): {panel[panel['did_sample_2x2']==1]['district_name_standard'].nunique()}")

# ─── Task 4: Data Quality Audit ───────────────────────────────────────────────
print("\n" + "="*60)
print("TASK 4 — DATA QUALITY AUDIT")
print("="*60)

KEY_VARS = [
    "unemp_rate_wt", "agri_share_wt", "nonagri_share_wt", "edu_secondary_wt",
    "log_wage_median", "literacy_rate", "urban_share", "sc_share", "st_share",
    "worker_participation_rate", "agri_worker_share", "bharatnet_treatment"
]

# 4.1 Missingness by variable
print("\n4.1 Missingness by variable (all 295 rows):")
miss_rows = []
for var in KEY_VARS:
    if var in panel.columns:
        n_miss  = panel[var].isna().sum()
        pct     = n_miss / len(panel) * 100
        miss_rows.append({"variable": var, "n_missing": n_miss,
                          "pct_missing": round(pct, 1), "n_valid": len(panel)-n_miss})
        print(f"  {var:<30} missing: {n_miss:3d} ({pct:5.1f}%)")
    else:
        print(f"  {var:<30} COLUMN NOT FOUND")

miss_df = pd.DataFrame(miss_rows)
miss_df.to_csv("research/audit_missingness_by_var.csv", index=False)

# 4.2 Missingness by state
print("\n4.2 Missingness by state:")
for state in ["Karnataka", "Bihar", "Rajasthan"]:
    sub = panel[panel["state"] == state]
    lit_miss = sub["literacy_rate"].isna().sum()
    unemp_miss = sub["unemp_rate_wt"].isna().sum()
    print(f"  {state:<12}: {len(sub):3d} rows | literacy missing: {lit_miss} | unemp missing: {unemp_miss}")

# 4.3 Missingness by treatment group
print("\n4.3 Missingness by treatment group (2019-20 only):")
pre = panel[panel["survey_year"] == 2019]
for grp in ["early","mid","late"]:
    sub = pre[pre["bharatnet_treatment"] == grp]
    print(f"  {grp:<6}: {len(sub):3d} districts | literacy: {sub['literacy_rate'].notna().sum()} | unemp: {sub['unemp_rate_wt'].notna().sum()}")

# 4.4 District coverage
print("\n4.4 District coverage by state and year:")
cov = panel.groupby(["state","survey_year","sample_grade"]).size().unstack(fill_value=0)
print(cov.to_string())

# 4.5 Year coverage
print("\n4.5 2x2 DiD sample composition:")
did_2x2 = panel[panel["did_sample_2x2"]==1]
print(did_2x2.groupby(["state","bharatnet_treatment","survey_year"]).size().to_string())

# 4.6 Descriptive statistics for DiD sample
print("\n4.6 DiD sample descriptive statistics (2x2, early+late, 2019+2023):")
desc = did_2x2[["unemp_rate_wt","agri_share_wt","literacy_rate","urban_share"]].describe().round(2)
print(desc.to_string())

# 4.7 Save full audit table
audit_summary = {
    "total_rows": len(panel),
    "total_columns": len(panel.columns),
    "did_2x2_rows": int(panel["did_sample_2x2"].sum()),
    "did_3period_rows": int(panel["did_sample_3period"].sum()),
    "unique_districts_total": panel["district_name_standard"].nunique(),
    "unique_districts_did_2x2": int(panel[panel["did_sample_2x2"]==1]["district_name_standard"].nunique()),
    "states": 3,
    "years_covered": sorted(panel["survey_year"].unique().tolist()),
    "literacy_coverage_pct": round(panel["literacy_rate"].notna().mean()*100, 1),
    "unemp_coverage_pct": round(panel["unemp_rate_wt"].notna().mean()*100, 1),
    "zero_unknown_districts": int((panel["district_name_standard"].isna()).sum()) == 0,
    "zero_null_treatment": int(panel["bharatnet_treatment"].isna().sum()) == 0,
}
pd.DataFrame([audit_summary]).to_csv("research/audit_summary.csv", index=False)
print("\nAudit summary saved: research/audit_summary.csv")
for k,v in audit_summary.items():
    print(f"  {k:<40} {v}")
