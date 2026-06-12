"""
AIRIS Phase 4C — Secondary Outcome DiD Estimation
===================================================
Same specification as R1:
  Y_it = alpha_i + lambda_t + beta3*(Post2023 × Early_i) + epsilon_it
  District + Year FE | Clustered SE (CR1) | Wild bootstrap (B=999)

Outcomes:
  1. agri_share_wt      (agricultural employment share, %)
  2. nonagri_share_wt   (non-agricultural employment share, %)
  3. services_share     (services employment share, %) — distinct from agri/nonagri
  4. log_wage_median    (log weekly wage, median)

Identical sample: KA+RJ | early+late | 2019+2023 | Grade C+
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import warnings, os

warnings.filterwarnings('ignore')
os.makedirs('results', exist_ok=True)
np.random.seed(42)

panel = pd.read_csv('data/clean/panel/airis_panel_master.csv')

# ─── Sample builder ────────────────────────────────────────────────────────────
def make_r1_sample(df, outcome=None):
    """R1 sample: KA+RJ, early+late, 2019+2023, grade C+. Drops rows missing outcome."""
    mask = (
        df['state'].isin(['Karnataka','Rajasthan']) &
        df['bharatnet_treatment'].isin(['early','late']) &
        df['survey_year'].isin([2019, 2023]) &
        df['sample_grade'].isin(['A','B','C'])
    )
    s = df[mask].copy()
    s['post']  = (s['survey_year'] == 2023).astype(int)
    s['early'] = (s['bharatnet_treatment'] == 'early').astype(int)
    s['did']   = s['post'] * s['early']
    if outcome:
        s[outcome] = pd.to_numeric(s[outcome], errors='coerce')
        s = s.dropna(subset=[outcome])
    return s.sort_values(['district_name_standard','survey_year']).reset_index(drop=True)

# ─── Within-estimator ─────────────────────────────────────────────────────────
def within_transform(df, var, dist_col='district_name_standard', yr_col='survey_year'):
    grand = df[var].mean()
    dm    = df.groupby(dist_col)[var].transform('mean')
    ym    = df.groupby(yr_col)[var].transform('mean')
    df[f'{var}_w'] = df[var] - dm - ym + grand
    return df

def did_fe(df, outcome, cluster_col='district_name_standard', B_boot=999, seed=42):
    """Full DiD with district+year FE, clustered SE, and wild bootstrap."""
    df = df.copy()
    for v in [outcome, 'did', 'post', 'early']:
        df = within_transform(df, v)

    Y  = df[f'{outcome}_w'].values
    X  = sm.add_constant(df['did_w'].values)
    c  = df[cluster_col].values
    uc = np.unique(c)
    G  = len(uc);  N = len(Y);  K = X.shape[1]

    # OLS
    m   = sm.OLS(Y, X).fit()
    e   = m.resid
    b3  = m.params[1]

    # Clustered SE (CR1)
    meat = np.zeros((K,K))
    for ci in uc:
        idx = c == ci
        s   = X[idx].T @ e[idx]
        meat += np.outer(s, s)
    corr  = (G/(G-1)) * ((N-1)/(N-K))
    bread = np.linalg.inv(X.T @ X)
    cov_c = corr * bread @ meat @ bread
    se3   = np.sqrt(cov_c[1,1])
    t3    = b3 / se3
    p_asy = 2 * stats.t.sf(abs(t3), df=G-1)
    ci_lo = b3 - stats.t.ppf(0.975, df=G-1)*se3
    ci_hi = b3 + stats.t.ppf(0.975, df=G-1)*se3

    # Wild cluster bootstrap
    rng   = np.random.default_rng(seed)
    boots = np.zeros(B_boot)
    for b in range(B_boot):
        w_g    = {ci2: rng.choice([-1,1]) for ci2 in uc}
        e_boot = np.array([e[i]*w_g[c[i]] for i in range(N)])
        Y_boot = X @ m.params + e_boot
        boots[b] = sm.OLS(Y_boot, X).fit().params[1]

    p_boot    = np.mean(np.abs(boots - boots.mean()) >= abs(b3))
    boot_lo   = np.percentile(boots, 2.5)
    boot_hi   = np.percentile(boots, 97.5)

    # 2x2 decomposition (simple means)
    gm = df.groupby(['early','post'])[outcome].mean()
    e_pre  = gm.get((1,0), np.nan); e_post = gm.get((1,1), np.nan)
    l_pre  = gm.get((0,0), np.nan); l_post = gm.get((0,1), np.nan)
    d_e = e_post - e_pre
    d_l = l_post - l_pre
    naive_did = d_e - d_l

    return {
        'outcome':    outcome,
        'beta3':      b3,      'se':      se3,
        't':          t3,      'p_asy':   p_asy,
        'ci_lo':      ci_lo,   'ci_hi':   ci_hi,
        'p_boot':     p_boot,  'boot_lo': boot_lo,  'boot_hi': boot_hi,
        'G':          G,       'N':       N,
        'r2_within':  m.rsquared,
        'naive_did':  naive_did,
        'early_pre':  e_pre,   'early_post': e_post, 'delta_early': d_e,
        'late_pre':   l_pre,   'late_post':  l_post, 'delta_late':  d_l,
        'boot_dist':  boots,
    }

# ─── Run all outcome DiDs ─────────────────────────────────────────────────────
OUTCOMES = [
    ('unemp_rate_wt',    'Unemployment rate (%)', 'PRIMARY'),
    ('agri_share_wt',    'Agricultural employment share (%)', 'SECONDARY'),
    ('nonagri_share_wt', 'Non-agricultural employment share (%)', 'SECONDARY'),
    ('services_share',   'Services employment share (%)', 'SECONDARY'),
    ('log_wage_median',  'Log weekly wage (median)', 'TERTIARY'),
]

results = {}
print("Estimating DiD for all outcomes...\n")
print(f"{'Outcome':<28} {'β3':>8} {'SE':>6} {'p(asy)':>8} {'p(boot)':>8} {'BootCI':>20} {'G':>4} {'N':>4}")
print("-"*90)

for varname, label, tier in OUTCOMES:
    df_out = make_r1_sample(panel, outcome=varname)
    res    = did_fe(df_out, outcome=varname)
    results[varname] = res
    print(f"  {varname:<26} {res['beta3']:>+8.3f} {res['se']:>6.3f} "
          f"{res['p_asy']:>8.3f} {res['p_boot']:>8.3f} "
          f"[{res['boot_lo']:+.2f}, {res['boot_hi']:+.2f}] "
          f"{res['G']:>4d} {res['N']:>4d}")

# ─── 2×2 decomposition table ──────────────────────────────────────────────────
print("\n" + "="*90)
print("2×2 DiD Decomposition (simple group means)")
print("="*90)
print(f"{'Outcome':<28} {'E-pre':>7} {'E-post':>7} {'ΔE':>7} {'L-pre':>7} {'L-post':>7} {'ΔL':>7} {'DiD':>7}")
print("-"*90)
for varname, label, tier in OUTCOMES:
    r = results[varname]
    print(f"  {varname:<26} {r['early_pre']:>7.2f} {r['early_post']:>7.2f} {r['delta_early']:>+7.2f}"
          f" {r['late_pre']:>7.2f} {r['late_post']:>7.2f} {r['delta_late']:>+7.2f} {r['naive_did']:>+7.3f}")

# ─── Event study (3-period) for all outcomes ──────────────────────────────────
print("\n" + "="*90)
print("Event Study (2019→2021→2023): Early vs Late group mean trajectories")
print("="*90)
r1_3yr = panel[
    panel['state'].isin(['Karnataka','Rajasthan']) &
    panel['bharatnet_treatment'].isin(['early','late']) &
    panel['sample_grade'].isin(['A','B','C'])
].copy()

for varname, label, tier in OUTCOMES:
    print(f"\n{label} ({varname}):")
    for grp in ['early','late']:
        sub = r1_3yr[r1_3yr['bharatnet_treatment']==grp]
        vals = []
        for yr in [2019, 2021, 2023]:
            v = pd.to_numeric(sub[sub['survey_year']==yr][varname], errors='coerce').dropna()
            vals.append(f"{v.mean():.2f}" if len(v)>0 else "N/A")
        print(f"  {grp:<6}: 2019={vals[0]} | 2021={vals[1]} | 2023={vals[2]}")

# ─── Save results ─────────────────────────────────────────────────────────────
rows = []
for varname, label, tier in OUTCOMES:
    r = results[varname]
    rows.append({
        'tier':            tier,
        'outcome_var':     varname,
        'outcome_label':   label,
        'beta3':           round(r['beta3'], 4),
        'se_clustered':    round(r['se'], 4),
        't_stat':          round(r['t'], 3),
        'p_asymptotic':    round(r['p_asy'], 4),
        'p_wildboot':      round(r['p_boot'], 4),
        'ci_lo_asy':       round(r['ci_lo'], 4),
        'ci_hi_asy':       round(r['ci_hi'], 4),
        'ci_lo_boot':      round(r['boot_lo'], 4),
        'ci_hi_boot':      round(r['boot_hi'], 4),
        'n_clusters':      r['G'],
        'n_obs':           r['N'],
        'r2_within':       round(r['r2_within'], 4),
        'early_pre':       round(r['early_pre'], 3),
        'early_post':      round(r['early_post'], 3),
        'delta_early':     round(r['delta_early'], 3),
        'late_pre':        round(r['late_pre'], 3),
        'late_post':       round(r['late_post'], 3),
        'delta_late':      round(r['delta_late'], 3),
        'naive_did':       round(r['naive_did'], 3),
    })

out_df = pd.DataFrame(rows)
out_df.to_csv('results/AIRIS_R2_MultiOutcome_Table.csv', index=False)
print(f"\nSaved: results/AIRIS_R2_MultiOutcome_Table.csv")

# Save bootstrap distributions
for varname, _, _ in OUTCOMES:
    np.save(f"results/boot_{varname}.npy", results[varname]['boot_dist'])

print("All estimations complete.")
