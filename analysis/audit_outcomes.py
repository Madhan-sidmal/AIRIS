"""
AIRIS Phase 4C — Task 1: Outcome Variable Audit
Audits all candidate outcome variables in airis_panel_master.csv.
Produces a full missingness and coverage report for the R1 sample (KA+RJ, early+late, 2019+2023, grade C+).
"""

import pandas as pd
import numpy as np

panel = pd.read_csv('data/clean/panel/airis_panel_master.csv')

# R1 sample definition
r1 = panel[
    panel['state'].isin(['Karnataka','Rajasthan']) &
    panel['bharatnet_treatment'].isin(['early','late']) &
    panel['survey_year'].isin([2019, 2023]) &
    panel['sample_grade'].isin(['A','B','C'])
].copy()

# Extended sample: all 3 years for event study
r1_3yr = panel[
    panel['state'].isin(['Karnataka','Rajasthan']) &
    panel['bharatnet_treatment'].isin(['early','late']) &
    panel['sample_grade'].isin(['A','B','C'])
].copy()

print("=" * 70)
print("AIRIS Outcome Variable Audit")
print(f"R1 sample: {len(r1)} obs, {r1['district_name_standard'].nunique()} districts")
print(f"3yr sample: {len(r1_3yr)} obs, {r1_3yr['district_name_standard'].nunique()} districts")
print("=" * 70)

# All columns
print("\nAll columns in master panel:")
for i, c in enumerate(panel.columns):
    print(f"  {i:2d}. {c}")

# Candidate outcome variables
CANDIDATES = [
    'unemp_rate_wt',
    'agri_share_wt',
    'nonagri_share_wt',
    'services_share',
    'edu_secondary_wt',
    'log_wage_median',
    'wage_n',
    'n_employed',
    'n_rural_persons',
    'employed_weight',
    'worker_participation_rate',
    'agri_worker_share',
]

print("\n" + "=" * 70)
print("Candidate Outcome Variable Coverage — R1 Sample (48 obs)")
print("=" * 70)
print(f"{'Variable':<28} {'Type':<12} {'Valid':>5} {'Miss':>5} {'Cov%':>6} {'Min':>7} {'Mean':>7} {'Max':>7}")
print("-" * 70)
for var in CANDIDATES:
    if var not in r1.columns:
        print(f"  {var:<26} COLUMN NOT FOUND")
        continue
    vals = pd.to_numeric(r1[var], errors='coerce')
    n_valid = vals.notna().sum()
    n_miss  = vals.isna().sum()
    cov     = n_valid / len(r1) * 100
    vtype   = "PLFS" if var in ['unemp_rate_wt','agri_share_wt','nonagri_share_wt',
                                  'services_share','edu_secondary_wt','log_wage_median',
                                  'wage_n','n_employed','n_rural_persons','employed_weight'] else "Census"
    mn  = vals.min()  if n_valid > 0 else np.nan
    avg = vals.mean() if n_valid > 0 else np.nan
    mx  = vals.max()  if n_valid > 0 else np.nan
    print(f"  {var:<26} {vtype:<12} {n_valid:>5} {n_miss:>5} {cov:>5.1f}% {mn:>7.2f} {avg:>7.2f} {mx:>7.2f}")

# By group and year
print("\n" + "=" * 70)
print("Coverage by survey_year and treatment group")
print("=" * 70)
for var in ['unemp_rate_wt','agri_share_wt','nonagri_share_wt','log_wage_median','services_share']:
    if var not in r1.columns:
        continue
    print(f"\n{var}:")
    for yr in [2019, 2023]:
        for grp in ['early','late']:
            sub = r1[(r1['survey_year']==yr) & (r1['bharatnet_treatment']==grp)]
            vals = pd.to_numeric(sub[var], errors='coerce').dropna()
            print(f"  {yr} {grp:<6}: n={len(vals):2d} | mean={vals.mean():.2f} | sd={vals.std():.2f} | "
                  f"min={vals.min():.2f} | max={vals.max():.2f}")

# Wage completeness detail
print("\n" + "=" * 70)
print("Wage variable detail (log_wage_median)")
print("=" * 70)
if 'log_wage_median' in r1.columns:
    for state in ['Karnataka','Rajasthan']:
        sub = r1[r1['state']==state]
        vals = pd.to_numeric(sub['log_wage_median'], errors='coerce')
        n_valid = vals.notna().sum()
        print(f"  {state}: {n_valid}/{len(sub)} obs valid ({n_valid/len(sub)*100:.0f}%)")
        # By year
        for yr in [2019, 2023]:
            sub_yr = sub[sub['survey_year']==yr]
            vals_yr = pd.to_numeric(sub_yr['log_wage_median'], errors='coerce')
            print(f"    {yr}: {vals_yr.notna().sum()}/{len(sub_yr)} valid")

# Check if services_share is meaningful
print("\n" + "=" * 70)
print("services_share vs nonagri_share_wt correlation check")
print("=" * 70)
if 'services_share' in r1.columns and 'nonagri_share_wt' in r1.columns:
    sv = pd.to_numeric(r1['services_share'], errors='coerce')
    na = pd.to_numeric(r1['nonagri_share_wt'], errors='coerce')
    valid = sv.notna() & na.notna()
    if valid.sum() > 3:
        corr = np.corrcoef(sv[valid], na[valid])[0,1]
        print(f"  Correlation: {corr:.3f}")
        print(f"  services_share = 100 - agri_share (approx: {'YES' if abs(corr+1)<0.01 else 'NO, different measure'})")
    # Value ranges
    print(f"  services_share range: {sv.min():.1f} – {sv.max():.1f}")
    print(f"  nonagri_share range:  {na.min():.1f} – {na.max():.1f}")

# Worker participation from PLFS vs Census
print("\n" + "=" * 70)
print("PLFS-derived vs Census worker participation")
print("=" * 70)
print("  worker_participation_rate: CENSUS 2011 (time-invariant — cannot be a DiD outcome)")
print("  agri_worker_share: CENSUS 2011 (time-invariant — cannot be a DiD outcome)")
print("  n_employed / employed_weight: PLFS counts — not rates, size-dependent")
print("  unemp_rate_wt: PLFS 2019/2021/2023 — PRIMARY DiD outcome")
print("  agri_share_wt: PLFS 2019/2021/2023 — SECONDARY DiD outcome")
print("  nonagri_share_wt: PLFS 2019/2021/2023 — SECONDARY DiD outcome (= 100 - agri_share_wt)")
print("  log_wage_median: PLFS 2019/2021/2023 — TERTIARY outcome, 30% missing")
print("  services_share: PLFS-derived — CHECK if meaningful or redundant")
print("  edu_secondary_wt: 100% MISSING — EXCLUDED")
