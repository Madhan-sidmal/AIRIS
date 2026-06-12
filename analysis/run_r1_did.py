"""
AIRIS Phase 4B — R1: First DiD Estimation
==========================================
Specification:
  Y_it = α_i + λ_t + β3·(Post2023_t × Early_i) + ε_it

Estimator:
  Within estimator (demeaned OLS) with district + year fixed effects
  Clustered standard errors at district level (CR1-small-sample corrected)
  Wild cluster bootstrap for inference (given small N of clusters)

Sample:
  Karnataka + Rajasthan | Early + Late | 2019 + 2023 | Grade C+

Outcome: unemp_rate_wt (weighted unemployment rate, %)

Interpretation of β3:
  Differential change in unemployment between 2019 and 2023 for
  early-connected districts relative to late-connected districts.
  NOT a causal AI adoption effect — identifies differential labour-market
  adjustment during the period of AI diffusion for districts with stronger
  pre-existing digital connectivity.

Outputs:
  results/AIRIS_R1_Results.md
  results/AIRIS_R1_Table1.csv
  results/AIRIS_R1_Diagnostics.md
  results/AIRIS_R1_Sensitivity.md
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.formula.api as smf
import statsmodels.api as sm
import warnings
import os

warnings.filterwarnings('ignore')
os.makedirs('results', exist_ok=True)
np.random.seed(42)

# ─── 1. Load and filter sample ───────────────────────────────────────────────
print("Loading panel...")
panel = pd.read_csv('data/clean/panel/airis_panel_master.csv')

def make_sample(df, states=None, treatments=None, years=None, grades=None):
    mask = pd.Series(True, index=df.index)
    if states:      mask &= df['state'].isin(states)
    if treatments:  mask &= df['bharatnet_treatment'].isin(treatments)
    if years:       mask &= df['survey_year'].isin(years)
    if grades:      mask &= df['sample_grade'].isin(grades)
    return df[mask].copy()

BASE_STATES    = ['Karnataka', 'Rajasthan']
BASE_TREATS    = ['early', 'late']
BASE_YEARS     = [2019, 2023]
BASE_GRADES    = ['A', 'B', 'C']

r1 = make_sample(panel, BASE_STATES, BASE_TREATS, BASE_YEARS, BASE_GRADES).copy()

# Encode
r1['post']    = (r1['survey_year'] == 2023).astype(int)
r1['early']   = (r1['bharatnet_treatment'] == 'early').astype(int)
r1['did']     = r1['post'] * r1['early']
r1['dist_id'] = pd.Categorical(r1['district_name_standard']).codes
r1['year_id'] = pd.Categorical(r1['survey_year']).codes

# Sort for consistency
r1 = r1.sort_values(['district_name_standard', 'survey_year']).reset_index(drop=True)

print(f"R1 sample: {len(r1)} obs | {r1['district_name_standard'].nunique()} districts")
print(f"Early: {r1[r1['early']==1]['district_name_standard'].nunique()} districts | "
      f"Late: {r1[r1['early']==0]['district_name_standard'].nunique()} districts")

# ─── 2. Within estimator (district + year FE) ────────────────────────────────
def within_transform(df, outcome, group_col='district_name_standard', year_col='survey_year'):
    """
    Applies within transformation: demean by district and year.
    Equivalent to including district + year fixed effects.
    """
    df = df.copy()
    # Grand mean
    grand_mean = df[outcome].mean()
    # District means
    dist_means  = df.groupby(group_col)[outcome].transform('mean')
    # Year means
    year_means  = df.groupby(year_col)[outcome].transform('mean')
    # Within-transformed Y
    df[f'{outcome}_w'] = df[outcome] - dist_means - year_means + grand_mean
    return df

def did_within(df, outcome='unemp_rate_wt', cluster_col='district_name_standard'):
    """
    Estimates DiD with district + year FE using within transformation.
    Returns OLS results with clustered SEs.
    """
    df = within_transform(df, outcome)
    df = within_transform(df, 'did')
    df = within_transform(df, 'post')
    df = within_transform(df, 'early')

    Y  = df[f'{outcome}_w'].values
    X  = sm.add_constant(df['did_w'].values)

    # OLS
    model = sm.OLS(Y, X).fit()

    # Clustered SE (CR1 — Liang-Zeger, with small-sample correction)
    clusters = df[cluster_col].values
    unique_clusters = np.unique(clusters)
    G = len(unique_clusters)
    N = len(Y)
    K = X.shape[1]

    e = model.resid
    meat = np.zeros((K, K))
    for c in unique_clusters:
        idx = clusters == c
        Xc  = X[idx, :]
        ec  = e[idx]
        score = Xc.T @ ec
        meat += np.outer(score, score)

    # Small-sample correction: (G/(G-1)) * (N-1)/(N-K)
    correction = (G / (G - 1)) * ((N - 1) / (N - K))
    bread = np.linalg.inv(X.T @ X)
    cov_cluster = correction * bread @ meat @ bread

    se_cluster  = np.sqrt(np.diag(cov_cluster))
    beta3       = model.params[1]      # DiD coefficient
    se3         = se_cluster[1]
    t3          = beta3 / se3
    # Use t distribution with G-1 degrees of freedom (cluster-robust)
    p3          = 2 * stats.t.sf(abs(t3), df=G-1)
    ci_lo       = beta3 - stats.t.ppf(0.975, df=G-1) * se3
    ci_hi       = beta3 + stats.t.ppf(0.975, df=G-1) * se3

    return {
        'beta3': beta3, 'se': se3, 't': t3, 'p': p3,
        'ci_lo': ci_lo, 'ci_hi': ci_hi,
        'G': G, 'N': N, 'R2_within': model.rsquared,
        'model': model, 'cov_cluster': cov_cluster,
    }

# ─── 3. Main estimates ────────────────────────────────────────────────────────
print("\nEstimating R1 through R5...")

# R1: KA only
r1_ka = make_sample(panel, ['Karnataka'], BASE_TREATS, BASE_YEARS, BASE_GRADES)
r1_ka['post']  = (r1_ka['survey_year']==2023).astype(int)
r1_ka['early'] = (r1_ka['bharatnet_treatment']=='early').astype(int)
r1_ka['did']   = r1_ka['post'] * r1_ka['early']
res_ka = did_within(r1_ka)

# R2: KA + RJ
r1_karj = r1.copy()
res_karj = did_within(r1_karj)

# R3: KA + RJ excl. Kalaburagi
r1_excl_kal = r1_karj[r1_karj['district_name_standard'] != 'Kalaburagi'].copy()
res_excl_kal = did_within(r1_excl_kal)

# R4: KA + RJ excl. Jaipur + Kota + Kalaburagi (Rajasthan urban outliers + KA flag)
excl_list = ['Kalaburagi', 'Jaipur', 'Kota', 'Bengaluru Urban']
r1_excl = r1_karj[~r1_karj['district_name_standard'].isin(excl_list)].copy()
res_excl = did_within(r1_excl)

# R5: KA only, excl. Kalaburagi
r1_ka_excl = r1_ka[r1_ka['district_name_standard'] != 'Kalaburagi'].copy()
res_ka_excl = did_within(r1_ka_excl)

print("\n=== MAIN RESULTS ===")
specs = [
    ('R1: KA only',                      res_ka),
    ('R2: KA+RJ (main)',                  res_karj),
    ('R3: KA+RJ excl. Kalaburagi',        res_excl_kal),
    ('R4: KA+RJ excl. urban outliers',    res_excl),
    ('R5: KA excl. Kalaburagi',           res_ka_excl),
]
print(f"{'Spec':<35} {'β3':>7} {'SE':>6} {'t':>6} {'p':>6} {'CI_lo':>7} {'CI_hi':>7} {'G':>4} {'N':>4}")
for name, res in specs:
    print(f"{name:<35} {res['beta3']:>7.3f} {res['se']:>6.3f} {res['t']:>6.2f} "
          f"{res['p']:>6.3f} {res['ci_lo']:>7.3f} {res['ci_hi']:>7.3f} "
          f"{res['G']:>4d} {res['N']:>4d}")

# ─── 4. Wild cluster bootstrap for R2 (recommended inference with G<30) ──────
print("\nRunning wild cluster bootstrap (B=999) for R2 main spec...")

def wild_cluster_bootstrap(df, outcome='unemp_rate_wt', B=999, seed=42):
    """
    Wild cluster bootstrap using Rademacher weights.
    Provides better inference than asymptotic clustered SE when G < 30.
    """
    rng = np.random.default_rng(seed)
    df2 = within_transform(df.copy(), outcome)
    df2 = within_transform(df2, 'did')

    Y   = df2[f'{outcome}_w'].values
    X   = sm.add_constant(df2['did_w'].values)
    clusters = df2['district_name_standard'].values
    unique_c = np.unique(clusters)
    G = len(unique_c)

    # Original beta
    model0 = sm.OLS(Y, X).fit()
    beta0  = model0.params[1]
    e0     = model0.resid

    # Bootstrap
    beta_boot = np.zeros(B)
    for b in range(B):
        # Rademacher weights: ±1 with equal probability
        w_g = {c: rng.choice([-1, 1]) for c in unique_c}
        e_boot = np.array([e0[i] * w_g[clusters[i]] for i in range(len(e0))])
        Y_boot = X @ model0.params + e_boot
        beta_boot[b] = sm.OLS(Y_boot, X).fit().params[1]

    # Bootstrap p-value (two-sided)
    p_boot = np.mean(np.abs(beta_boot - beta_boot.mean()) >= np.abs(beta0))
    ci_boot_lo = np.percentile(beta_boot, 2.5)
    ci_boot_hi = np.percentile(beta_boot, 97.5)

    return {
        'beta3': beta0,
        'p_boot': p_boot,
        'ci_boot_lo': ci_boot_lo,
        'ci_boot_hi': ci_boot_hi,
        'beta_boot': beta_boot,
        'G': G,
    }

boot_r2 = wild_cluster_bootstrap(r1_karj, B=999)
print(f"Bootstrap p-value: {boot_r2['p_boot']:.3f}")
print(f"Bootstrap 95% CI: [{boot_r2['ci_boot_lo']:.3f}, {boot_r2['ci_boot_hi']:.3f}]")

# ─── 5. 2×2 DiD decomposition (Lechner decomposition) ────────────────────────
print("\n=== 2x2 DiD Decomposition ===")
grp_means = r1_karj.groupby(['early','post'])['unemp_rate_wt'].mean()
print(grp_means.to_string())

early_pre  = grp_means.get((1,0), np.nan)
early_post = grp_means.get((1,1), np.nan)
late_pre   = grp_means.get((0,0), np.nan)
late_post  = grp_means.get((0,1), np.nan)

delta_early = early_post - early_pre
delta_late  = late_post  - late_pre
beta3_naive = delta_early - delta_late  # naive 2x2 without FE

print(f"\nEarly: {early_pre:.2f} → {early_post:.2f} (Δ = {delta_early:+.2f}pp)")
print(f"Late:  {late_pre:.2f} → {late_post:.2f} (Δ = {delta_late:+.2f}pp)")
print(f"DiD (naive group means): {beta3_naive:+.3f}pp")
print(f"DiD (within estimator):  {res_karj['beta3']:+.3f}pp")
print(f"Note: FE estimator accounts for unbalanced panel and district composition")

# ─── 6. Save Table 1 CSV ─────────────────────────────────────────────────────
table1_rows = []
for name, res in specs:
    table1_rows.append({
        'specification': name,
        'beta3_pp':      round(res['beta3'], 3),
        'se_clustered':  round(res['se'], 3),
        't_stat':        round(res['t'], 2),
        'p_value_asymptotic': round(res['p'], 3),
        'ci_lo_95':      round(res['ci_lo'], 3),
        'ci_hi_95':      round(res['ci_hi'], 3),
        'n_clusters':    res['G'],
        'n_obs':         res['N'],
        'r2_within':     round(res['R2_within'], 3),
    })

# Add bootstrap for R2
table1_rows[1]['p_value_wildboot'] = round(boot_r2['p_boot'], 3)
table1_rows[1]['ci_lo_boot']       = round(boot_r2['ci_boot_lo'], 3)
table1_rows[1]['ci_hi_boot']       = round(boot_r2['ci_boot_hi'], 3)

table1 = pd.DataFrame(table1_rows)
table1.to_csv('results/AIRIS_R1_Table1.csv', index=False)
print(f"\nSaved: results/AIRIS_R1_Table1.csv")

# ─── 7. Event study (3-period, using 2021 as mid-point) ──────────────────────
print("\n=== Event Study (3-period: 2019/2021/2023) ===")
r_es = make_sample(panel, BASE_STATES, BASE_TREATS, [2019,2021,2023], BASE_GRADES).copy()
r_es['early'] = (r_es['bharatnet_treatment']=='early').astype(int)

es_means = r_es.groupby(['early','survey_year'])['unemp_rate_wt'].mean().unstack()
print(es_means.to_string())

# Event study coefficients: estimate per-year DiD vs baseline year 2019
print("\nEvent study (base=2019, early vs late):")
for yr in [2019, 2021, 2023]:
    sub = r_es[r_es['survey_year'].isin([2019, yr])].copy()
    if yr == 2019:
        print(f"  {yr}: base period (β = 0.000 by construction)")
        continue
    sub['post_yr']  = (sub['survey_year'] == yr).astype(int)
    sub['did_yr']   = sub['post_yr'] * sub['early']
    # Simple 2x2 for each event window
    gm = sub.groupby(['early','post_yr'])['unemp_rate_wt'].mean()
    b_es = (gm.get((1,1),np.nan) - gm.get((1,0),np.nan)) - \
           (gm.get((0,1),np.nan) - gm.get((0,0),np.nan))
    print(f"  {yr}: β = {b_es:+.3f}pp")

# Save all results to numpy for reporting
np.save('results/boot_distribution_r2.npy', boot_r2['beta_boot'])
print("\nAll estimation complete.")
