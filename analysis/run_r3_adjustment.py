"""
AIRIS Phase 4D — R3: Labour Market Adjustment DiD + Heterogeneity Analysis
============================================================================
Builds unified outcome framework (unemployment + LFPR + WPR + sector + wages)
and estimates DiD for all outcomes using the R1 specification.

Also runs heterogeneity analysis:
  1. Karnataka vs Rajasthan
  2. High vs Low literacy districts (split at state median)
  3. High vs Low agriculture districts (split at state median)

All specifications: district + year FE, clustered SE (CR1), wild bootstrap (B=999)
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings, os

warnings.filterwarnings('ignore')
os.makedirs('results', exist_ok=True)
np.random.seed(42)

# ─── 1. Load master panel ─────────────────────────────────────────────────────
panel   = pd.read_csv('data/clean/panel/airis_panel_master.csv')
lfpr_df = pd.read_csv('data/clean/panel/airis_lfpr_wpr_all.csv')

print(f"Master panel: {len(panel)} rows")
print(f"LFPR/WPR panel: {len(lfpr_df)} rows")

# ─── 2. Merge LFPR/WPR into master panel ─────────────────────────────────────
lfpr_merge = lfpr_df[[
    "district_code","state_code_plfs","survey_year","lfpr_wt","wpr_wt","nilf_share_wt"
]].copy()
lfpr_merge["district_code"] = pd.to_numeric(lfpr_merge["district_code"], errors='coerce')

panel_full = panel.merge(
    lfpr_merge,
    left_on=["district_code_num","state_code_plfs","survey_year"],
    right_on=["district_code","state_code_plfs","survey_year"],
    how="left"
)
print(f"After LFPR merge: {len(panel_full)} rows")
print(f"LFPR matched: {panel_full['lfpr_wt'].notna().sum()}")
print(f"WPR matched: {panel_full['wpr_wt'].notna().sum()}")

# Save enriched panel
panel_full.to_csv('data/clean/panel/airis_panel_master.csv', index=False)
print("Updated airis_panel_master.csv with LFPR/WPR")

# ─── 3. R1 Sample helper ──────────────────────────────────────────────────────
def make_sample(df, states=None, treats=None, years=None, grades=None,
                extra_filter=None, outcome=None):
    mask = pd.Series(True, index=df.index)
    if states:   mask &= df['state'].isin(states)
    if treats:   mask &= df['bharatnet_treatment'].isin(treats)
    if years:    mask &= df['survey_year'].isin(years)
    if grades:   mask &= df['sample_grade'].isin(grades)
    if extra_filter is not None:
        mask &= extra_filter
    s = df[mask].copy()
    s['post']  = (s['survey_year'] == 2023).astype(int)
    s['early'] = (s['bharatnet_treatment'] == 'early').astype(int)
    s['did']   = s['post'] * s['early']
    if outcome:
        s[outcome] = pd.to_numeric(s[outcome], errors='coerce')
        s = s.dropna(subset=[outcome])
    return s.sort_values(['district_name_standard','survey_year']).reset_index(drop=True)

BASE = dict(states=['Karnataka','Rajasthan'], treats=['early','late'],
            years=[2019,2023], grades=['A','B','C'])

# ─── 4. Within-estimator ──────────────────────────────────────────────────────
def wt(df, v, dc='district_name_standard', yc='survey_year'):
    grand = df[v].mean()
    dm    = df.groupby(dc)[v].transform('mean')
    ym    = df.groupby(yc)[v].transform('mean')
    df[f'{v}_w'] = df[v] - dm - ym + grand
    return df

def did_fe(df, outcome, B=999, seed=42, cluster_col='district_name_standard'):
    df = df.copy()
    for v in [outcome, 'did']:
        df = wt(df, v)
    Y  = df[f'{outcome}_w'].values
    X  = sm.add_constant(df['did_w'].values)
    c  = df[cluster_col].values
    uc = np.unique(c); G = len(uc); N = len(Y); K = X.shape[1]
    m  = sm.OLS(Y, X).fit()
    e  = m.resid; b3 = m.params[1]
    meat = np.zeros((K,K))
    for ci in uc:
        idx = c==ci; s = X[idx].T@e[idx]; meat += np.outer(s,s)
    corr  = (G/(G-1))*((N-1)/(N-K))
    bread = np.linalg.inv(X.T@X)
    cov_c = corr * bread @ meat @ bread
    se3   = np.sqrt(cov_c[1,1])
    t3    = b3/se3
    p_asy = 2*stats.t.sf(abs(t3), df=G-1)
    ci_lo = b3 - stats.t.ppf(0.975, df=G-1)*se3
    ci_hi = b3 + stats.t.ppf(0.975, df=G-1)*se3
    rng  = np.random.default_rng(seed)
    boots = np.zeros(B)
    for b in range(B):
        w_g  = {ci2: rng.choice([-1,1]) for ci2 in uc}
        eb   = np.array([e[i]*w_g[c[i]] for i in range(N)])
        boots[b] = sm.OLS(X@m.params+eb, X).fit().params[1]
    p_boot  = np.mean(np.abs(boots-boots.mean()) >= abs(b3))
    blo, bhi = np.percentile(boots, [2.5, 97.5])
    gm = df.groupby(['early','post'])[outcome].mean()
    ep,lp = gm.get((1,0),np.nan), gm.get((0,0),np.nan)
    epo,lpo = gm.get((1,1),np.nan), gm.get((0,1),np.nan)
    return dict(b3=b3, se=se3, t=t3, p_asy=p_asy, ci_lo=ci_lo, ci_hi=ci_hi,
                p_boot=p_boot, blo=blo, bhi=bhi, G=G, N=N, r2=m.rsquared,
                de=epo-ep, dl=lpo-lp, naive=((epo-ep)-(lpo-lp)),
                ep=ep, epo=epo, lp=lp, lpo=lpo)

# ─── 5. Full outcome suite ────────────────────────────────────────────────────
ALL_OUTCOMES = [
    ('unemp_rate_wt',    'Unemployment rate (%)'),
    ('lfpr_wt',          'LFPR — Labour Force Participation Rate (%)'),
    ('wpr_wt',           'WPR — Worker Population Ratio (%)'),
    ('nilf_share_wt',    'NILF — Not in Labour Force (%)'),
    ('agri_share_wt',    'Agricultural employment share (%)'),
    ('nonagri_share_wt', 'Non-agricultural employment share (%)'),
    ('services_share',   'Services employment share (%)'),
    ('log_wage_median',  'Median log weekly wage'),
]

print("\n" + "="*90)
print("R3 — Full Labour Market Adjustment DiD (KA+RJ, early vs late, 2019+2023)")
print("="*90)
print(f"{'Outcome':<28} {'β3':>8} {'SE':>6} {'p(asy)':>8} {'p(boot)':>8} {'BootCI':>20} {'G':>4} {'N':>4}")
print("-"*90)

results_main = {}
for var, label in ALL_OUTCOMES:
    samp = make_sample(panel_full, **BASE, outcome=var)
    if len(samp) < 10:
        print(f"  {var:<26} INSUFFICIENT DATA (n={len(samp)})")
        continue
    res = did_fe(samp, var)
    results_main[var] = res
    sig = '★' if res['p_boot'] < 0.05 else ' '
    print(f"  {sig}{var:<26} {res['b3']:>+8.3f} {res['se']:>6.3f} "
          f"{res['p_asy']:>8.3f} {res['p_boot']:>8.3f} "
          f"[{res['blo']:+.2f},{res['bhi']:+.2f}] "
          f"{res['G']:>4d} {res['N']:>4d}")

# ─── 6. 2×2 Decomposition ─────────────────────────────────────────────────────
print("\n2×2 Decomposition:")
print(f"{'Outcome':<28} {'E_2019':>7} {'E_2023':>7} {'ΔEarly':>8} {'L_2019':>7} {'L_2023':>7} {'ΔLate':>8} {'DiD':>8}")
for var, label in ALL_OUTCOMES:
    if var not in results_main: continue
    r = results_main[var]
    print(f"  {var:<26} {r['ep']:>7.2f} {r['epo']:>7.2f} {r['de']:>+8.3f}"
          f" {r['lp']:>7.2f} {r['lpo']:>7.2f} {r['dl']:>+8.3f} {r['naive']:>+8.3f}")

# ─── 7. Heterogeneity — by State ─────────────────────────────────────────────
print("\n" + "="*90)
print("Heterogeneity Analysis — By State")
print("="*90)

hetero_state = {}
for state in ['Karnataka', 'Rajasthan']:
    print(f"\n{state}:")
    hetero_state[state] = {}
    for var, label in [('unemp_rate_wt','Unemployment'),
                        ('lfpr_wt','LFPR'),
                        ('wpr_wt','WPR'),
                        ('agri_share_wt','Agri share'),
                        ('services_share','Services share')]:
        samp = make_sample(panel_full, states=[state],
                           treats=['early','late'], years=[2019,2023],
                           grades=['A','B','C'], outcome=var)
        if len(samp) < 8:
            continue
        res = did_fe(samp, var)
        hetero_state[state][var] = res
        sig = '★' if res['p_boot'] < 0.05 else ' '
        print(f"  {sig}{var:<24} β3={res['b3']:>+7.3f} p(boot)={res['p_boot']:.3f}"
              f"  [{res['blo']:+.2f},{res['bhi']:+.2f}]  G={res['G']} N={res['N']}")

# ─── 8. Heterogeneity — by Literacy ──────────────────────────────────────────
print("\n" + "="*90)
print("Heterogeneity Analysis — High vs Low Literacy (within-state median split)")
print("="*90)

# Compute state-level literacy median from 2019 baseline
panel_full['lit_median_state'] = panel_full.groupby('state')['literacy_rate'].transform('median')
panel_full['high_lit'] = (panel_full['literacy_rate'] >= panel_full['lit_median_state'])

hetero_lit = {}
for lit_grp, lit_label in [(True,'High literacy'), (False,'Low literacy')]:
    print(f"\n{lit_label}:")
    hetero_lit[lit_label] = {}
    filt = panel_full['high_lit'] == lit_grp
    for var, label in [('unemp_rate_wt','Unemployment'),('lfpr_wt','LFPR'),
                        ('agri_share_wt','Agri share'),('services_share','Services')]:
        samp = make_sample(panel_full, **BASE,
                           extra_filter=filt, outcome=var)
        if len(samp) < 8:
            continue
        res = did_fe(samp, var)
        hetero_lit[lit_label][var] = res
        sig = '★' if res['p_boot'] < 0.05 else ' '
        print(f"  {sig}{var:<24} β3={res['b3']:>+7.3f} p(boot)={res['p_boot']:.3f}"
              f"  [{res['blo']:+.2f},{res['bhi']:+.2f}]  G={res['G']} N={res['N']}")

# ─── 9. Heterogeneity — by Agriculture share ──────────────────────────────────
print("\n" + "="*90)
print("Heterogeneity Analysis — High vs Low Agriculture (2019 baseline, state median)")
print("="*90)

# Use 2019 agri_share_wt as baseline agriculture intensity
agri_baseline = panel_full[panel_full['survey_year']==2019][
    ['district_name_standard','state','agri_share_wt']
].rename(columns={'agri_share_wt':'agri_base_2019'}).copy()
agri_baseline['agri_median_state'] = agri_baseline.groupby('state')['agri_base_2019'].transform('median')
agri_baseline['high_agri'] = agri_baseline['agri_base_2019'] >= agri_baseline['agri_median_state']
panel_full = panel_full.merge(
    agri_baseline[['district_name_standard','state','high_agri']].drop_duplicates(),
    on=['district_name_standard','state'], how='left'
)

hetero_agri = {}
for agri_grp, agri_label in [(True,'High agriculture'), (False,'Low agriculture')]:
    print(f"\n{agri_label}:")
    hetero_agri[agri_label] = {}
    filt = panel_full['high_agri'] == agri_grp
    for var, label in [('unemp_rate_wt','Unemployment'),('lfpr_wt','LFPR'),
                        ('agri_share_wt','Agri share'),('services_share','Services')]:
        samp = make_sample(panel_full, **BASE,
                           extra_filter=filt, outcome=var)
        if len(samp) < 8:
            continue
        res = did_fe(samp, var)
        hetero_agri[agri_label][var] = res
        sig = '★' if res['p_boot'] < 0.05 else ' '
        print(f"  {sig}{var:<24} β3={res['b3']:>+7.3f} p(boot)={res['p_boot']:.3f}"
              f"  [{res['blo']:+.2f},{res['bhi']:+.2f}]  G={res['G']} N={res['N']}")

# ─── 10. Save results CSV ─────────────────────────────────────────────────────
rows = []
for var, label in ALL_OUTCOMES:
    if var not in results_main: continue
    r = results_main[var]
    rows.append({'spec': 'Main (KA+RJ)', 'outcome': var, 'label': label,
                 'beta3': round(r['b3'],4), 'se': round(r['se'],4),
                 'p_asy': round(r['p_asy'],4), 'p_boot': round(r['p_boot'],4),
                 'ci_lo_boot': round(r['blo'],4), 'ci_hi_boot': round(r['bhi'],4),
                 'G': r['G'], 'N': r['N'], 'r2_within': round(r['r2'],4)})

pd.DataFrame(rows).to_csv('results/AIRIS_R3_Results_Table.csv', index=False)
print("\nSaved: results/AIRIS_R3_Results_Table.csv")

# ─── 11. Visualization ────────────────────────────────────────────────────────
print("Generating figures...")

# Coefficient chart for all outcomes
fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor('#0f1117')
ax.set_facecolor('#1a1d27')
for sp in ax.spines.values(): sp.set_color('#333')
ax.tick_params(colors='#aaa')

labels_short = {
    'unemp_rate_wt': 'Unemployment\nrate (%)',
    'lfpr_wt':       'LFPR (%)',
    'wpr_wt':        'WPR (%)',
    'nilf_share_wt': 'NILF share (%)',
    'agri_share_wt': 'Agri\nemployment (%)',
    'nonagri_share_wt': 'Non-agri\nemployment (%)',
    'services_share': 'Services\nemployment (%)',
    'log_wage_median': 'Log wage\n(median)',
}

ordered_vars = [v for v,_ in ALL_OUTCOMES if v in results_main]
for i, var in enumerate(ordered_vars):
    r = results_main[var]
    col = '#ffd54f' if r['p_boot'] < 0.05 else ('#80cbc4' if r['p_boot'] < 0.10 else '#78909c')
    ax.barh(i, r['bhi']-r['blo'], left=r['blo'], height=0.55, color=col, alpha=0.4)
    ax.plot(r['b3'], i, 'D', color=col, markersize=9, zorder=5)
    p_txt = f"p={r['p_boot']:.3f}"
    if r['p_boot'] < 0.05: p_txt += ' ★'
    ax.text(max(r['bhi'],r['b3'])+0.05, i, p_txt,
            va='center', ha='left', fontsize=8, color='#aaa')

ax.axvline(0, color='#ef5350', linewidth=1.5, alpha=0.8)
ax.set_yticks(range(len(ordered_vars)))
ax.set_yticklabels([labels_short.get(v, v) for v in ordered_vars], fontsize=9, color='#ccc')
ax.set_xlabel('DiD Coefficient β3 (wild bootstrap 95% CI)', fontsize=10, color='#bbb')
ax.set_title('AIRIS R3 — Full Labour Market Adjustment\nAll outcomes: KA+RJ, early vs late, 2019 vs 2023, district+year FE',
             fontsize=10, color='white')
ax.grid(alpha=0.13, color='#555', axis='x', linestyle=':')
ax.set_xlim(-12, 14)
plt.tight_layout()
plt.savefig('results/fig_r3_all_outcomes.png', dpi=150,
            bbox_inches='tight', facecolor='#0f1117')
plt.close()
print("Saved: results/fig_r3_all_outcomes.png")

# LFPR/WPR event study
lfpr_3yr = panel_full[
    panel_full['state'].isin(['Karnataka','Rajasthan']) &
    panel_full['bharatnet_treatment'].isin(['early','late']) &
    panel_full['sample_grade'].isin(['A','B','C']) &
    panel_full['lfpr_wt'].notna()
].copy()

fig2, axes = plt.subplots(1, 3, figsize=(13, 4))
fig2.patch.set_facecolor('#0f1117')
COLORS = {'early':'#4fc3f7','late':'#ff8a65'}
TITLES = {'lfpr_wt':'LFPR (%)','wpr_wt':'WPR (%)','nilf_share_wt':'NILF Share (%)'}
YLIMS  = {'lfpr_wt':[35,65],'wpr_wt':[30,65],'nilf_share_wt':[30,65]}

for ax, (var,ylim) in zip(axes, [(v,YLIMS[v]) for v in ['lfpr_wt','wpr_wt','nilf_share_wt']]):
    ax.set_facecolor('#1a1d27')
    for sp in ax.spines.values(): sp.set_color('#333')
    ax.tick_params(colors='#aaa', labelsize=8)
    for grp in ['early','late']:
        sub = lfpr_3yr[lfpr_3yr['bharatnet_treatment']==grp]
        means,sems=[],[]
        for yr in [2019,2021,2023]:
            v = pd.to_numeric(sub[sub['survey_year']==yr][var],errors='coerce').dropna()
            means.append(v.mean() if len(v)>0 else np.nan)
            sems.append(v.sem()   if len(v)>1 else np.nan)
        ax.errorbar([2019,2021,2023], means,
                    yerr=[1.96*s for s in sems],
                    marker='o' if grp=='early' else 's',
                    linewidth=2, markersize=6, color=COLORS[grp],
                    label=grp.capitalize(), capsize=4, capthick=1.5, elinewidth=1)
    ax.axvline(2022.5, color='#ffd54f', linestyle='--', alpha=0.7, linewidth=1.2)
    ax.axvspan(2020,2022,alpha=0.07,color='#ef5350')
    ax.set_xticks([2019,2021,2023])
    ax.set_xticklabels(['2019','2021','2023'], fontsize=8)
    ax.set_ylim(ylim)
    ax.set_title(TITLES[var], fontsize=9.5, color='#ddd')
    ax.grid(alpha=0.13, color='#555', linestyle=':')
    if var=='lfpr_wt': ax.legend(fontsize=8,framealpha=0.2,labelcolor='white')

fig2.suptitle('LFPR, WPR and NILF — Early vs Late Districts (KA+RJ)\nYellow=AI shock | Red=COVID',
              fontsize=10, color='white')
plt.tight_layout()
plt.savefig('results/fig_r3_lfpr_event.png', dpi=150,
            bbox_inches='tight', facecolor='#0f1117')
plt.close()
print("Saved: results/fig_r3_lfpr_event.png")
print("\nAll R3 analyses complete.")
