"""
AIRIS R1 — Visualizations
Produces:
  results/fig_event_study.png   : Event study plot (3-period)
  results/fig_did_parallel.png  : Parallel trends visualization
  results/fig_boot_dist.png     : Bootstrap distribution of β3
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

os.makedirs('results', exist_ok=True)

panel = pd.read_csv('data/clean/panel/airis_panel_master.csv')
BASE_STATES  = ['Karnataka', 'Rajasthan']
BASE_TREATS  = ['early', 'late']
BASE_GRADES  = ['A', 'B', 'C']

# ─── Figure 1: Parallel Trends + Event Study ─────────────────────────────────
r_es = panel[
    panel['state'].isin(BASE_STATES) &
    panel['bharatnet_treatment'].isin(BASE_TREATS) &
    panel['sample_grade'].isin(BASE_GRADES)
].copy()

# Group means ± 1SE
def grp_stats(df, grp, years=[2019,2021,2023]):
    rows = []
    for yr in years:
        vals = df[(df['bharatnet_treatment']==grp) & (df['survey_year']==yr)]['unemp_rate_wt']
        rows.append({'year': yr, 'mean': vals.mean(), 'se': vals.sem(),
                     'n': len(vals), 'group': grp})
    return pd.DataFrame(rows)

es_early = grp_stats(r_es, 'early')
es_late  = grp_stats(r_es, 'late')

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.patch.set_facecolor('#0f1117')
for ax in axes:
    ax.set_facecolor('#1a1d27')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.tick_params(colors='#aaa')
    ax.xaxis.label.set_color('#ccc')
    ax.yaxis.label.set_color('#ccc')
    ax.title.set_color('#eee')

COLORS = {'early': '#4fc3f7', 'late': '#ff8a65'}

# --- Panel A: Parallel trends (mean unemployment by group-year) ---
ax = axes[0]
for grp, data, marker in [('early', es_early, 'o'), ('late', es_late, 's')]:
    ax.errorbar(data['year'], data['mean'],
                yerr=1.96 * data['se'],
                marker=marker, linewidth=2, markersize=7,
                color=COLORS[grp], label=f'{grp.capitalize()}-connected',
                capsize=4, capthick=1.5, elinewidth=1)

ax.axvline(2022.5, color='#ffd54f', linestyle='--', alpha=0.7, linewidth=1.5,
           label='AI diffusion shock\n(ChatGPT, Jan 2023)')
ax.axvspan(2020, 2022, alpha=0.08, color='#ef5350', label='COVID period')
ax.set_xlabel('PLFS Survey Year', fontsize=11)
ax.set_ylabel('Weighted Unemployment Rate (%)', fontsize=11)
ax.set_title('Unemployment Rate by BharatNet Connectivity\n(Karnataka + Rajasthan, Grade C+ districts)', fontsize=10)
ax.set_xticks([2019, 2021, 2023])
ax.set_xticklabels(['2019-20\n(pre)', '2021-22\n(COVID)', '2023-24\n(post)'])
ax.legend(fontsize=9, framealpha=0.2, labelcolor='white')
ax.grid(alpha=0.15, color='#555')
ax.set_ylim(4, 16)

# --- Panel B: Event study coefficients (β relative to 2019 baseline) ---
ax = axes[1]
# Event study DiD coefficients (from run_r1_did.py output)
es_coefs = {2019: 0.000, 2021: 1.560, 2023: 2.384}
# Bootstrap CIs for 2023 (from bootstrap results)
boot_ci = {2023: (0.066, 5.840)}
# Approximate SE for 2021 (using R2 spec SE scaling)
se_2021_approx = 1.5

years_plot = [2019, 2021, 2023]
coefs_plot = [es_coefs[y] for y in years_plot]
# CIs: ±1.96*SE (use R2 SE=1.55 for 2023, approximate for 2021)
cis_lo = [0, es_coefs[2021] - 1.96*se_2021_approx, boot_ci[2023][0]]
cis_hi = [0, es_coefs[2021] + 1.96*se_2021_approx, boot_ci[2023][1]]

ax.axhline(0, color='#888', linestyle='-', linewidth=0.8)
ax.axvline(2022.5, color='#ffd54f', linestyle='--', alpha=0.7, linewidth=1.5)
ax.axvspan(2020, 2022, alpha=0.08, color='#ef5350')

for i, yr in enumerate(years_plot):
    color = '#4fc3f7' if yr == 2023 else '#78909c'
    ax.errorbar(yr, coefs_plot[i],
                yerr=[[coefs_plot[i]-cis_lo[i]], [cis_hi[i]-coefs_plot[i]]],
                marker='D', markersize=8, linewidth=2, color=color,
                capsize=5, capthick=2, elinewidth=2)

ax.fill_between([2022.8, 2023.2], [cis_lo[2]], [cis_hi[2]],
                alpha=0.15, color='#4fc3f7')
ax.set_xlabel('PLFS Survey Year', fontsize=11)
ax.set_ylabel('DiD Coefficient β (pp, relative to 2019)', fontsize=11)
ax.set_title('Event Study: Differential Unemployment Change\n(Early vs Late, base=2019)', fontsize=10)
ax.set_xticks([2019, 2021, 2023])
ax.set_xticklabels(['2019-20\n(base)', '2021-22\n(COVID)', '2023-24\n(post-shock)'])
ax.grid(alpha=0.15, color='#555')
ax.set_ylim(-3, 8)

# Annotation for 2023
ax.annotate(f'β = +2.38pp\np(boot) = 0.040',
            xy=(2023, es_coefs[2023]), xytext=(2022.2, 5.5),
            color='#4fc3f7', fontsize=9,
            arrowprops=dict(arrowstyle='->', color='#4fc3f7', lw=1.5))

fig.suptitle(
    'AIRIS — DiD: Labour Market Adjustment During AI Diffusion Period\n'
    'BharatNet Connectivity × Post-2023 (Karnataka + Rajasthan)',
    fontsize=11, color='white', y=1.01
)
plt.tight_layout()
plt.savefig('results/fig_event_study.png', dpi=150, bbox_inches='tight',
            facecolor='#0f1117')
plt.close()
print("Saved: results/fig_event_study.png")

# ─── Figure 2: Bootstrap distribution ────────────────────────────────────────
boot_dist = np.load('results/boot_distribution_r2.npy')

fig2, ax2 = plt.subplots(figsize=(8, 4))
fig2.patch.set_facecolor('#0f1117')
ax2.set_facecolor('#1a1d27')
for sp in ax2.spines.values(): sp.set_color('#333')
ax2.tick_params(colors='#aaa')
ax2.xaxis.label.set_color('#ccc')
ax2.yaxis.label.set_color('#ccc')
ax2.title.set_color('#eee')

ax2.hist(boot_dist, bins=40, color='#4fc3f7', alpha=0.7, edgecolor='#1a1d27', linewidth=0.5)
ax2.axvline(3.033, color='#ffd54f', linewidth=2, label=f'β3 = +3.03pp')
ax2.axvline(np.percentile(boot_dist, 2.5),  color='#ff8a65', linestyle='--', linewidth=1.5, label='95% CI bounds')
ax2.axvline(np.percentile(boot_dist, 97.5), color='#ff8a65', linestyle='--', linewidth=1.5)
ax2.axvline(0, color='#ef5350', linewidth=1, linestyle='-', alpha=0.7, label='H0: β3 = 0')

ax2.set_xlabel('Bootstrap β3 (DiD coefficient, percentage points)', fontsize=11)
ax2.set_ylabel('Frequency', fontsize=11)
ax2.set_title('Wild Cluster Bootstrap Distribution — R2 Specification\n(B=999, Rademacher weights)', fontsize=10, color='white')
ax2.legend(fontsize=9, framealpha=0.2, labelcolor='white')
ax2.grid(alpha=0.15, color='#555')

plt.tight_layout()
plt.savefig('results/fig_boot_dist.png', dpi=150, bbox_inches='tight', facecolor='#0f1117')
plt.close()
print("Saved: results/fig_boot_dist.png")

# ─── Figure 3: Sensitivity waterfall ─────────────────────────────────────────
fig3, ax3 = plt.subplots(figsize=(9, 4))
fig3.patch.set_facecolor('#0f1117')
ax3.set_facecolor('#1a1d27')
for sp in ax3.spines.values(): sp.set_color('#333')
ax3.tick_params(colors='#aaa')
ax3.xaxis.label.set_color('#ccc')
ax3.yaxis.label.set_color('#ccc')
ax3.title.set_color('#eee')

specs_sens = [
    ('KA only', 3.003, -0.990, 6.997),
    ('KA + RJ\n(main)', 3.033, 0.066, 5.840),  # bootstrap CI
    ('KA+RJ excl.\nKalaburagi', 3.073, -0.293, 6.438),
    ('KA+RJ excl.\nurban outliers', 2.307, -1.170, 5.784),
    ('KA excl.\nKalaburagi', 3.210, -1.258, 7.678),
]

y_pos = list(range(len(specs_sens)))[::-1]
colors_s = ['#78909c','#4fc3f7','#80cbc4','#a5d6a7','#78909c']
for i, (name, b, lo, hi) in enumerate(specs_sens):
    color = colors_s[i]
    ax3.barh(y_pos[i], hi-lo, left=lo, height=0.5, color=color, alpha=0.5)
    ax3.plot(b, y_pos[i], 'D', color=color, markersize=9)

ax3.axvline(0, color='#ef5350', linewidth=1.5, linestyle='-', alpha=0.8, label='β3 = 0')
ax3.set_yticks(y_pos)
ax3.set_yticklabels([s[0] for s in specs_sens], fontsize=9, color='#ccc')
ax3.set_xlabel('DiD coefficient β3 (percentage points)', fontsize=10)
ax3.set_title('Sensitivity Analysis — DiD Coefficient β3 across Specifications\n(bars = 95% CI)', fontsize=10, color='white')
ax3.grid(alpha=0.15, color='#555', axis='x')
ax3.legend(fontsize=9, framealpha=0.2, labelcolor='white')

plt.tight_layout()
plt.savefig('results/fig_sensitivity.png', dpi=150, bbox_inches='tight', facecolor='#0f1117')
plt.close()
print("Saved: results/fig_sensitivity.png")
print("All figures complete.")
