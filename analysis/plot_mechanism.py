"""
AIRIS Phase 4C — Mechanism Visualization
Produces: results/fig_mechanism_panel.png
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os

os.makedirs('results', exist_ok=True)
panel = pd.read_csv('data/clean/panel/airis_panel_master.csv')

r1_3yr = panel[
    panel['state'].isin(['Karnataka','Rajasthan']) &
    panel['bharatnet_treatment'].isin(['early','late']) &
    panel['sample_grade'].isin(['A','B','C'])
].copy()

OUTCOMES = [
    ('unemp_rate_wt',   'Unemployment Rate (%)',         'PRIMARY',   [4,16]),
    ('agri_share_wt',   'Agricultural Employment (%)',   'SECONDARY', [44,60]),
    ('services_share',  'Services Employment (%)',       'SECONDARY', [18,36]),
    ('log_wage_median', 'Log Weekly Wage (median)',      'TERTIARY',  [3.55,4.2]),
]

YEARS   = [2019, 2021, 2023]
COLORS  = {'early': '#4fc3f7', 'late': '#ff8a65'}
LABELS  = {'early': 'Early-connected', 'late': 'Late-connected'}
MARKERS = {'early': 'o', 'late': 's'}

fig = plt.figure(figsize=(14, 10))
fig.patch.set_facecolor('#0f1117')
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.32)

for idx, (var, title, tier, ylim) in enumerate(OUTCOMES):
    ax = fig.add_subplot(gs[idx//2, idx%2])
    ax.set_facecolor('#1a1d27')
    for sp in ax.spines.values(): sp.set_color('#333')
    ax.tick_params(colors='#aaa', labelsize=9)
    ax.xaxis.label.set_color('#bbb')
    ax.yaxis.label.set_color('#bbb')

    for grp in ['early','late']:
        sub   = r1_3yr[r1_3yr['bharatnet_treatment']==grp]
        means = []
        sems  = []
        for yr in YEARS:
            v = pd.to_numeric(sub[sub['survey_year']==yr][var], errors='coerce').dropna()
            means.append(v.mean() if len(v)>0 else np.nan)
            sems.append(v.sem()   if len(v)>1 else np.nan)

        ax.errorbar(YEARS, means,
                    yerr=[1.96*s for s in sems],
                    marker=MARKERS[grp], linewidth=2.2, markersize=7,
                    color=COLORS[grp], label=LABELS[grp],
                    capsize=4, capthick=1.5, elinewidth=1.2)

    ax.axvline(2022.5, color='#ffd54f', linestyle='--', alpha=0.7, linewidth=1.4)
    ax.axvspan(2020, 2022, alpha=0.07, color='#ef5350')
    ax.set_xticks(YEARS)
    ax.set_xticklabels(['2019-20\n(pre)', '2021-22\n(COVID)', '2023-24\n(post)'], fontsize=8)
    ax.set_ylim(ylim)
    ax.grid(alpha=0.13, color='#555', linestyle=':')

    # DiD annotation from results
    did_results = {
        'unemp_rate_wt':   ('+3.03pp', 0.040, True),
        'agri_share_wt':   ('−0.27pp', 0.867, False),
        'services_share':  ('−0.19pp', 0.932, False),
        'log_wage_median': ('+0.010', 0.920, False),
    }
    b3_txt, p_val, sig = did_results.get(var, ('', None, False))
    sig_str = '★ p=0.040' if sig else f'p={p_val:.3f}'
    color_sig = '#ffd54f' if sig else '#888'
    ax.set_title(f'{title}\nβ3={b3_txt}  {sig_str}',
                 fontsize=9.5, color='#ddd', pad=6)
    ax.set_ylabel(title.split('(')[0].strip(), fontsize=8.5, color='#bbb')

    if idx == 0:
        ax.legend(fontsize=8.5, framealpha=0.2, labelcolor='white',
                  loc='upper left', borderpad=0.6)

    # Mechanism tag
    if var == 'unemp_rate_wt':
        ax.text(0.98, 0.05, 'SIGNAL', transform=ax.transAxes,
                ha='right', va='bottom', fontsize=9, color='#ffd54f',
                fontweight='bold', alpha=0.9)
    else:
        ax.text(0.98, 0.05, 'NULL', transform=ax.transAxes,
                ha='right', va='bottom', fontsize=9, color='#888',
                fontweight='bold', alpha=0.8)

fig.suptitle(
    'AIRIS Phase 4C — Mechanism Decomposition\n'
    'Labour Market Outcomes by BharatNet Connectivity (Karnataka + Rajasthan)',
    fontsize=11.5, color='white', y=1.01, fontweight='semibold'
)

# Add footnote
fig.text(0.5, -0.02,
         'Yellow line = AI diffusion shock (ChatGPT, Jan 2023). Red band = COVID period.\n'
         'Error bars = ±1.96 SE. DiD coefficients estimated with district + year FE, wild cluster bootstrap (B=999, G=27).',
         ha='center', fontsize=8, color='#777')

plt.savefig('results/fig_mechanism_panel.png', dpi=150,
            bbox_inches='tight', facecolor='#0f1117')
plt.close()
print("Saved: results/fig_mechanism_panel.png")

# ─── Figure 2: Coefficient strip chart (all outcomes) ─────────────────────────
fig2, ax2 = plt.subplots(figsize=(10, 4))
fig2.patch.set_facecolor('#0f1117')
ax2.set_facecolor('#1a1d27')
for sp in ax2.spines.values(): sp.set_color('#333')
ax2.tick_params(colors='#aaa')

all_results = pd.read_csv('results/AIRIS_R2_MultiOutcome_Table.csv')
labels_map = {
    'unemp_rate_wt':    'Unemployment\nrate (%)',
    'agri_share_wt':    'Agricultural\nemployment (%)',
    'nonagri_share_wt': 'Non-agricultural\nemployment (%)',
    'services_share':   'Services\nemployment (%)',
    'log_wage_median':  'Log weekly\nwage',
}

y_pos = list(range(len(all_results)))
for i, row in all_results.iterrows():
    col = '#ffd54f' if row['p_wildboot'] < 0.05 else '#78909c'
    ax2.barh(i, row['ci_hi_boot'] - row['ci_lo_boot'],
             left=row['ci_lo_boot'], height=0.5, color=col, alpha=0.4)
    ax2.plot(row['beta3'], i, 'D', color=col, markersize=9, zorder=5)
    ax2.text(max(row['ci_hi_boot'], row['beta3']) + 0.1, i,
             f"p={row['p_wildboot']:.3f}", va='center', ha='left',
             fontsize=8, color='#aaa')

ax2.axvline(0, color='#ef5350', linewidth=1.5, alpha=0.8)
ax2.set_yticks(y_pos)
ax2.set_yticklabels([labels_map.get(r['outcome_var'], r['outcome_var'])
                     for _, r in all_results.iterrows()],
                    fontsize=9, color='#ccc')
ax2.set_xlabel('DiD Coefficient β3 (percentage points or log units)', fontsize=10, color='#bbb')
ax2.set_title('All Outcome DiD Coefficients — Bootstrap 95% CI\n'
              'Yellow = significant (p<0.05), Grey = null',
              fontsize=10, color='white')
ax2.grid(alpha=0.13, color='#555', axis='x', linestyle=':')
ax2.set_xlim(-7, 10)

plt.tight_layout()
plt.savefig('results/fig_mechanism_coefs.png', dpi=150,
            bbox_inches='tight', facecolor='#0f1117')
plt.close()
print("Saved: results/fig_mechanism_coefs.png")
