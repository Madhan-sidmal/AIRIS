# AIRIS Working Paper 1 — §5 Results Structure
## Phase 5A Draft | June 2026

> [!IMPORTANT]
> This document contains the full results narrative with all coefficient values from Phase 4B–4D estimation. All numbers are from `AIRIS_R1_Table1.csv`, `AIRIS_R2_MultiOutcome_Table.csv`, `AIRIS_R3_Results_Table.csv`, and the heterogeneity analysis in `AIRIS_R3_LabourMarketAdjustment.md`. No new estimates are introduced.

---

## 5. Results

### 5.1 Primary Outcome: Unemployment

**Table 1** presents DiD estimates for the primary outcome — the weighted rural unemployment rate — across all five specifications.

**[TABLE 1 — Final formatting required]**

| Specification | β3 (pp) | Clustered SE | p (asymp.) | p (boot) | Boot 95% CI | N | G |
|---|---|---|---|---|---|---|---|
| R1: KA only | +3.003 | 1.884 | 0.130 | 0.077 | [−0.37, +6.21] | 30 | 17 |
| **R2: KA+RJ (main)** | **+3.033** | **1.551** | **0.061** | **0.040** | **[+0.07, +5.84]** | **48** | **27** |
| R3: KA+RJ excl. Kalaburagi | +3.073 | 1.634 | 0.072 | — | [−0.29, +6.44] | 46 | 26 |
| R4: KA+RJ excl. urban outliers | +2.307 | 1.677 | 0.183 | — | [−1.17, +5.78] | 41 | 23 |
| R5: KA excl. Kalaburagi | +3.210 | 2.096 | 0.147 | — | [−1.26, +7.68] | 28 | 16 |

*Notes: Outcome = weighted rural unemployment rate (%). Specification: district + year fixed effects (within estimator). Standard errors clustered at district level with CR1 small-sample correction. Wild cluster bootstrap: B=999, Rademacher weights, two-sided p-value reported for R2 (main specification). All other specifications report asymptotic clustered p-values. Bootstrap CI reported for R2 only.*

**Interpretation:** The main specification (R2) produces a coefficient of $\hat{\beta}_3 = +3.033$ percentage points. This implies that early-connected districts experienced 3.03 percentage points higher unemployment growth between 2019-20 and 2023-24 relative to late-connected districts, after absorbing district and year fixed effects. The wild cluster bootstrap p-value is 0.040. The asymptotic clustered p-value (0.061) does not cross the conventional 0.05 threshold — both are reported.

The 2×2 DiD decomposition reveals the underlying arithmetic: early districts' unemployment rose by +0.74pp (from 7.33% to 8.07%), while late districts' unemployment fell by −1.64pp (from 11.33% to 9.68%). The gap between the two groups narrowed from 4.0pp to 1.6pp. The within-estimator yields a slightly larger β3 (+3.03pp vs +2.38pp from naive group means) because it correctly accounts for the unbalanced panel — districts that dropped out of the Grade C+ sample in 2023-24 differ systematically from those that remained.

The sign and approximate magnitude are stable across all five sensitivity specifications (range: +2.31 to +3.21pp), all returning positive β3. Excluding Kalaburagi — the most disputed treatment assignment — marginally increases β3 from +3.033 to +3.073, confirming that Kalaburagi's inclusion slightly attenuates rather than drives the result. Excluding urban outliers (Jaipur, Kota, Bengaluru Urban, and Kalaburagi) reduces β3 to +2.307pp, indicating that structurally urban districts in the early group contribute to the effect but are not its sole source.

**Figure 1** plots the parallel trends (group means by year) and event study coefficients (β relative to 2019 baseline) using the 3-period panel including 2021-22.

### 5.2 Secondary Outcomes: Sector Composition and Wages

**Table 2** presents DiD estimates for secondary outcomes under the R2 specification.

**[TABLE 2 — Final formatting required]**

| Tier | Outcome | β3 | SE | p (asy.) | p (boot) | Boot 95% CI |
|---|---|---|---|---|---|---|
| PRIMARY | Unemployment (%) | **+3.033** | 1.551 | 0.061 | **0.040** | [+0.07, +5.84] |
| SECONDARY | Agricultural employment (%) | −0.268 | 1.526 | 0.862 | 0.867 | [−3.06, +2.62] |
| SECONDARY | Non-agri employment (%) | +0.268 | 1.526 | 0.862 | 0.867 | [−2.62, +3.06] |
| SECONDARY | Services employment (%) | −0.187 | 2.649 | 0.944 | 0.932 | [−5.63, +4.71] |
| TERTIARY | Log weekly wage | +0.010 | 0.077 | 0.895 | 0.920 | [−0.13, +0.14] |

*Notes: Same specification and sample as primary outcome (R2). N=48 for all except log wage (N=46, 2 missing due to no rural wage workers observed). All p-values from wild cluster bootstrap unless noted.*

**Interpretation:** None of the secondary outcomes reach conventional significance thresholds. Agricultural employment share did not change differentially between early and late districts (β3=−0.27pp, p=0.867). Services employment did not change differentially (β3=−0.19pp, p=0.932). Wages showed no differential change (β3=+0.010 log points, p=0.920).

The event study trajectories reveal that both early and late groups experienced broadly parallel trends in sector composition across 2019-21-2023, with services employment rising in both groups (+1.52pp for early, +1.98pp for late). The DiD in services employment is near-zero at the aggregate level (−0.46pp naive), confirming the absence of a differential compositional shift. This aggregate null on secondary outcomes is revisited in Section 5.4, where heterogeneity by literacy resolves the puzzle.

**Figure 2** presents all outcome DiD coefficients and bootstrap 95% CIs in a single coefficient chart.

### 5.3 Heterogeneity — State

**Table 3A** reports state-level heterogeneity.

| State | Outcome | β3 (pp) | p (boot) | Boot 95% CI | G | N |
|---|---|---|---|---|---|---|
| Karnataka | Unemployment | +3.003 | 0.077 | [−0.37, +6.21] | 17 | 30 |
| Karnataka | Agricultural employment | −2.225 | 0.235 | [−5.63, +1.04] | 17 | 30 |
| Karnataka | Services employment | +2.004 | 0.546 | [−3.78, +7.62] | 17 | 30 |
| **Rajasthan** | **Unemployment** | **+5.844** | **0.005** | **[+1.22, +10.01]** | **10** | **18** |
| Rajasthan | Agricultural employment | +0.379 | 0.770 | [−2.51, +3.31] | 10 | 18 |
| Rajasthan | Services employment | −5.403 | 0.263 | [−13.55, +2.69] | 10 | 18 |

The main pooled effect (β3=+3.03pp) is substantially driven by Rajasthan, where the unemployment coefficient is +5.84pp (p=0.005). Karnataka alone produces β3=+3.00pp (p=0.077). The directional consistency across both states is reassuring, though the Rajasthan point estimate should be interpreted cautiously given that two early-connected Rajasthan districts (Jaipur: 66% urban, Kota: 67% urban) are structurally urban and may not represent the rural connectivity dynamics the paper targets.

### 5.4 Heterogeneity — Human Capital (Literacy)

**Table 3B** reports heterogeneity by within-state median literacy (Census 2011). This is the paper's primary heterogeneity analysis.

**[TABLE 3 — Final formatting required]**

| Subgroup | Outcome | β3 (pp) | SE | p (boot) | Boot 95% CI | G | N |
|---|---|---|---|---|---|---|---|
| **High literacy** | **Unemployment (%)** | **+4.405** | — | **0.000** | **[+1.75, +7.12]** | 13 | 23 |
| **High literacy** | **Services employment (%)** | **+3.417** | — | **0.000** | **[+1.45, +5.49]** | 13 | 23 |
| High literacy | Agricultural employment (%) | +2.454 | — | 0.166 | [−0.76, +5.57] | 13 | 23 |
| Low literacy | Unemployment (%) | −0.884 | — | 0.615 | [−4.29, +2.47] | 14 | 25 |
| **Low literacy** | **Agricultural employment (%)** | **−3.958** | — | **0.046** | **[−7.78, −0.10]** | 14 | 25 |
| Low literacy | Services employment (%) | −4.214 | — | 0.336 | [−12.00, +3.58] | 14 | 25 |

*Notes: Districts classified as high (low) literacy if Census 2011 literacy rate ≥ (<) within-state median literacy rate. Bootstrap p-values from B=999 replications.*

This table contains **the paper's headline finding.** In high-literacy early-connected districts, unemployment increased by +4.41pp (p=0.000) while services employment simultaneously expanded by +3.42pp (p=0.000). These two significant effects from the same subsample, estimated with the same conservative bootstrap inference, are the strongest empirical results in the AIRIS analysis.

The joint pattern — unemployment rising and services employment rising together — is not consistent with labour displacement (which would require services employment to fall). It is consistent with **structural transformation in progress**: workers are rotating toward service-sector employment, but the rate of job creation in services is insufficient to fully absorb the workers who have left or are leaving their previous employment. The labour market is in transition; the transition generates frictional unemployment.

In low-literacy early-connected districts, neither unemployment nor services employment changes significantly. However, agricultural employment declines by −3.96pp (p=0.046). Workers in low-literacy connected districts are exiting agriculture — but without moving into services and without registering as unemployed. The destination is not observable in the PLFS cross-sections; possibilities include informal self-employment, inter-state migration, and NILF transitions.

### 5.5 Heterogeneity — Sector Structure (Agriculture Intensity)

**Table 4** reports heterogeneity by within-state median agricultural employment share in 2019-20.

**[TABLE 4 — Final formatting required]**

| Subgroup | Outcome | β3 (pp) | p (boot) | Boot 95% CI | G | N |
|---|---|---|---|---|---|---|
| **High agriculture** | **Unemployment (%)** | **+4.903** | **0.003** | **[+1.16, +8.46]** | 15 | 29 |
| High agriculture | Services employment (%) | −2.791 | 0.417 | [−9.41, +3.57] | 15 | 29 |
| High agriculture | Agricultural employment (%) | −0.731 | 0.761 | [−4.51, +2.52] | 15 | 29 |
| Low agriculture | Unemployment (%) | −0.262 | 0.935 | [−4.02, +3.53] | 12 | 19 |
| Low agriculture | Services employment (%) | +4.294 | 0.144 | [−1.40, +9.92] | 12 | 19 |

The unemployment effect is entirely concentrated in high-agriculture districts: β3=+4.90pp (p=0.003) versus −0.26pp (p=0.935) in low-agriculture districts. This contrast is stark and represents a clean splitting of the aggregate effect by pre-existing sector structure. Districts that were more dependent on agricultural employment in 2019-20 experienced sharper unemployment increases in early-connected areas by 2023-24.

In low-agriculture districts, there is a directional (though imprecise) pattern of services employment expansion (+4.29pp, p=0.144), consistent with transformation in districts that already have a more diversified employment base. These districts do not experience unemployment increases, suggesting a smoother absorption of workers into service jobs.

### 5.6 Event Study and Figures

**Figure 1** plots group-mean unemployment rates by year (2019, 2021, 2023) for early and late districts, with 95% standard error bars. The two groups follow parallel trajectories from 2019 to 2021, with the gap widening in 2023-24. The event study coefficients (right panel) show a monotonic pattern: 0 (base), +1.56pp (2021), +2.38pp (2023), consistent with a trend that strengthens rather than pre-exists the post-period.

**Figure 2** presents all secondary outcome coefficients with bootstrap 95% CIs in a single strip chart. The unemployment coefficient stands alone in reaching significance; all others overlap zero.

**Figure 3** presents the full multi-outcome coefficient chart from R3, including LFPR and WPR (with caveats noted in the figure legend).
