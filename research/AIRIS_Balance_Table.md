# AIRIS Balance Table — Enriched
## Phase 4A — Pre-Treatment Covariate Balance
### Version 2.0 | June 2026 (Updated with Census 2011 controls)

> [!IMPORTANT]
> This table supersedes v1.0. All Census 2011 controls are now correctly joined via fuzzy name matching (102/102 districts matched). The balance assessment uses normalized differences (Imbens-Rubin, 2015). |Δ̄| < 0.25 = Balanced, 0.25–0.50 = Marginal, > 0.50 = Imbalanced.

---

## 1. Balance Assessment Method

- **Pre-treatment sample:** PLFS 2019-20 | Early-connected vs Late-connected districts | Grade C+ only (n ≥ 200 employed persons)
- **Census controls:** 2011 Census PCA, district level — time-invariant baseline covariates
- **Pooled sample:** 17 early districts, 23 late districts across Karnataka, Bihar, Rajasthan
- **Normalized difference:** Δ̄ = (μ_early − μ_late) / √[(σ²_early + σ²_late)/2]

---

## 2. Pooled Balance (All Three States, Early vs Late)

| Variable | Early n | Early Mean | Early SD | Late n | Late Mean | Late SD | Diff | Norm. Diff | p-value | Balance |
|---|---|---|---|---|---|---|---|---|---|---|
| Literacy rate (Census 2011, %) | 17 | 74.27 | 6.92 | 23 | 59.38 | 5.66 | +14.89 | +2.357 | 0.0 | ❌ Imbalanced |
| Female literacy rate (Census 2011, %) | 17 | 66.29 | 8.56 | 23 | 47.54 | 6.39 | +18.75 | +2.481 | 0.0 | ❌ Imbalanced |
| Scheduled Caste share (Census 2011, %) | 17 | 19.71 | 7.01 | 23 | 16.11 | 5.54 | +3.60 | +0.569 | 0.09 | ❌ Imbalanced |
| Scheduled Tribe share (Census 2011, %) | 17 | 5.15 | 4.12 | 23 | 13.15 | 20.57 | -8.00 | -0.540 | 0.081 | ❌ Imbalanced |
| Urban population share (Census 2011, %) | 17 | 29.74 | 15.87 | 23 | 12.26 | 8.51 | +17.48 | +1.373 | 0.0 | ❌ Imbalanced |
| Worker participation rate (Census 2011, %) | 17 | 44.51 | 6.01 | 23 | 41.19 | 6.08 | +3.33 | +0.550 | 0.094 | ❌ Imbalanced |
| Agricultural worker share (Census 2011, %) | 17 | 49.93 | 18.81 | 23 | 73.94 | 9.54 | -24.01 | -1.610 | 0.0 | ❌ Imbalanced |
| Unemployment rate (PLFS 2019-20, %) | 17 | 7.0 | 4.25 | 23 | 8.75 | 5.36 | -1.75 | -0.363 | 0.255 | ⚠️ Marginal |
| Agricultural employment share (PLFS 2019-20, %) | 17 | 51.65 | 2.74 | 23 | 51.67 | 4.18 | -0.02 | -0.006 | 0.984 | ✅ Balanced |
| Non-agricultural employment share (PLFS 2019-20, %) | 17 | 48.35 | 2.74 | 23 | 48.33 | 4.18 | +0.02 | +0.006 | 0.984 | ✅ Balanced |
| Median log weekly wage (PLFS 2019-20) | 16 | 3.75 | 0.31 | 15 | 3.83 | 0.17 | -0.08 | -0.314 | 0.388 | ⚠️ Marginal |


**Summary:** 2 balanced | 2 marginal | 7 imbalanced

---

## 3.1 Karnataka (Early n=11, Late n=5)

| Variable | Early n | Early Mean | Early SD | Late n | Late Mean | Late SD | Diff | Norm. Diff | p-value | Balance |
|---|---|---|---|---|---|---|---|---|---|---|
| Literacy rate (Census 2011, %) | 11 | 77.21 | 5.62 | 5 | 66.03 | 4.15 | +11.17 | +2.263 | 0.001 | ❌ Imbalanced |
| Female literacy rate (Census 2011, %) | 11 | 70.57 | 6.68 | 5 | 55.93 | 4.67 | +14.64 | +2.539 | 0.0 | ❌ Imbalanced |
| Scheduled Caste share (Census 2011, %) | 11 | 17.76 | 5.53 | 5 | 21.7 | 2.65 | -3.94 | -0.908 | 0.075 | ❌ Imbalanced |
| Scheduled Tribe share (Census 2011, %) | 11 | 6.29 | 3.66 | 5 | 9.81 | 7.45 | -3.52 | -0.600 | 0.363 | ❌ Imbalanced |
| Urban population share (Census 2011, %) | 11 | 29.69 | 13.11 | 5 | 24.57 | 5.64 | +5.12 | +0.507 | 0.293 | ❌ Imbalanced |
| Worker participation rate (Census 2011, %) | 11 | 48.03 | 2.94 | 5 | 44.03 | 2.73 | +4.00 | +1.409 | 0.028 | ❌ Imbalanced |
| Agricultural worker share (Census 2011, %) | 11 | 46.64 | 19.9 | 5 | 64.17 | 4.74 | -17.54 | -1.213 | 0.017 | ❌ Imbalanced |
| Unemployment rate (PLFS 2019-20, %) | 11 | 6.41 | 4.48 | 5 | 7.82 | 3.55 | -1.41 | -0.348 | 0.515 | ⚠️ Marginal |
| Agricultural employment share (PLFS 2019-20, %) | 11 | 51.65 | 2.46 | 5 | 49.11 | 6.67 | +2.54 | +0.505 | 0.45 | ❌ Imbalanced |
| Non-agricultural employment share (PLFS 2019-20, %) | 11 | 48.35 | 2.46 | 5 | 50.89 | 6.67 | -2.54 | -0.505 | 0.45 | ❌ Imbalanced |
| Median log weekly wage (PLFS 2019-20) | 10 | 3.85 | 0.06 | 5 | 3.85 | 0.2 | -0.00 | -0.000 | 1.0 | ✅ Balanced |

**Summary:** Imbalanced: 9 | Marginal: 1

---

## 3.2 Bihar (Early n=3, Late n=11)

| Variable | Early n | Early Mean | Early SD | Late n | Late Mean | Late SD | Diff | Norm. Diff | p-value | Balance |
|---|---|---|---|---|---|---|---|---|---|---|
| Literacy rate (Census 2011, %) | 3 | 63.84 | 0.52 | 11 | 56.79 | 4.76 | +7.05 | +2.084 | 0.001 | ❌ Imbalanced |
| Female literacy rate (Census 2011, %) | 3 | 53.7 | 0.85 | 11 | 46.12 | 4.52 | +7.59 | +2.333 | 0.0 | ❌ Imbalanced |
| Scheduled Caste share (Census 2011, %) | 3 | 22.39 | 7.45 | 11 | 14.89 | 3.97 | +7.50 | +1.257 | 0.217 | ❌ Imbalanced |
| Scheduled Tribe share (Census 2011, %) | 3 | 0.08 | 0.04 | 11 | 2.34 | 2.23 | -2.26 | -1.430 | 0.007 | ❌ Imbalanced |
| Urban population share (Census 2011, %) | 3 | 13.0 | 3.03 | 11 | 6.44 | 2.39 | +6.56 | +2.404 | 0.047 | ❌ Imbalanced |
| Worker participation rate (Census 2011, %) | 3 | 35.48 | 2.92 | 11 | 36.09 | 3.42 | -0.61 | -0.192 | 0.774 | ✅ Balanced |
| Agricultural worker share (Census 2011, %) | 3 | 69.65 | 2.45 | 11 | 80.95 | 5.43 | -11.30 | -2.683 | 0.001 | ❌ Imbalanced |
| Unemployment rate (PLFS 2019-20, %) | 3 | 5.46 | 3.09 | 11 | 5.94 | 4.22 | -0.49 | -0.131 | 0.835 | ✅ Balanced |
| Agricultural employment share (PLFS 2019-20, %) | 3 | 50.09 | 4.3 | 11 | 52.7 | 3.69 | -2.62 | -0.653 | 0.41 | ❌ Imbalanced |
| Non-agricultural employment share (PLFS 2019-20, %) | 3 | 49.91 | 4.3 | 11 | 47.3 | 3.69 | +2.62 | +0.653 | 0.41 | ❌ Imbalanced |
| Median log weekly wage (PLFS 2019-20) | 3 | 3.45 | 0.7 | 4 | 3.86 | 0.02 | -0.41 | -0.837 | 0.413 | ❌ Imbalanced |

**Summary:** Imbalanced: 9 | Marginal: 0

---

## 3.3 Rajasthan (Early n=3, Late n=7)

| Variable | Early n | Early Mean | Early SD | Late n | Late Mean | Late SD | Diff | Norm. Diff | p-value | Balance |
|---|---|---|---|---|---|---|---|---|---|---|
| Literacy rate (Census 2011, %) | 3 | 73.9 | 3.73 | 7 | 58.69 | 4.28 | +15.22 | +3.790 | 0.004 | ❌ Imbalanced |
| Female literacy rate (Census 2011, %) | 3 | 63.2 | 3.17 | 7 | 43.79 | 4.75 | +19.41 | +4.810 | 0.0 | ❌ Imbalanced |
| Scheduled Caste share (Census 2011, %) | 3 | 24.17 | 11.11 | 7 | 14.04 | 6.9 | +10.13 | +1.095 | 0.25 | ❌ Imbalanced |
| Scheduled Tribe share (Census 2011, %) | 3 | 6.02 | 4.68 | 7 | 32.52 | 29.06 | -26.50 | -1.273 | 0.053 | ❌ Imbalanced |
| Urban population share (Census 2011, %) | 3 | 46.63 | 17.3 | 7 | 12.59 | 6.8 | +34.04 | +2.590 | 0.068 | ❌ Imbalanced |
| Worker participation rate (Census 2011, %) | 3 | 40.64 | 4.98 | 7 | 47.15 | 3.9 | -6.51 | -1.456 | 0.134 | ❌ Imbalanced |
| Agricultural worker share (Census 2011, %) | 3 | 42.31 | 10.7 | 7 | 69.92 | 9.02 | -27.60 | -2.789 | 0.025 | ❌ Imbalanced |
| Unemployment rate (PLFS 2019-20, %) | 3 | 10.7 | 2.86 | 7 | 13.84 | 4.66 | -3.14 | -0.812 | 0.239 | ❌ Imbalanced |
| Agricultural employment share (PLFS 2019-20, %) | 3 | 53.23 | 1.95 | 7 | 51.89 | 2.08 | +1.34 | +0.667 | 0.382 | ❌ Imbalanced |
| Non-agricultural employment share (PLFS 2019-20, %) | 3 | 46.77 | 1.95 | 7 | 48.11 | 2.08 | -1.34 | -0.667 | 0.382 | ❌ Imbalanced |
| Median log weekly wage (PLFS 2019-20) | 3 | 3.72 | 0.23 | 6 | 3.79 | 0.21 | -0.07 | -0.317 | 0.682 | ⚠️ Marginal |

**Summary:** Imbalanced: 10 | Marginal: 1

---

## 4. Imbalance Flags and Required Controls

| State | Variable | Status | Action |
|---|---|---|---|
| Karnataka | Literacy rate (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Karnataka | Female literacy rate (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Karnataka | Scheduled Caste share (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Karnataka | Scheduled Tribe share (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Karnataka | Urban population share (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Karnataka | Worker participation rate (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Karnataka | Agricultural worker share (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Karnataka | Unemployment rate (PLFS 2019-20, %) | ⚠️ Marginal | Include as covariate in DiD |
| Karnataka | Agricultural employment share (PLFS 2019-20, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Karnataka | Non-agricultural employment share (PLFS 2019-20, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Bihar | Literacy rate (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Bihar | Female literacy rate (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Bihar | Scheduled Caste share (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Bihar | Scheduled Tribe share (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Bihar | Urban population share (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Bihar | Agricultural worker share (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Bihar | Agricultural employment share (PLFS 2019-20, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Bihar | Non-agricultural employment share (PLFS 2019-20, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Bihar | Median log weekly wage (PLFS 2019-20) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Rajasthan | Literacy rate (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Rajasthan | Female literacy rate (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Rajasthan | Scheduled Caste share (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Rajasthan | Scheduled Tribe share (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Rajasthan | Urban population share (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Rajasthan | Worker participation rate (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Rajasthan | Agricultural worker share (Census 2011, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Rajasthan | Unemployment rate (PLFS 2019-20, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Rajasthan | Agricultural employment share (PLFS 2019-20, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Rajasthan | Non-agricultural employment share (PLFS 2019-20, %) | ❌ Imbalanced | Do not interpret causally; include as control + run sensitivity |
| Rajasthan | Median log weekly wage (PLFS 2019-20) | ⚠️ Marginal | Include as covariate in DiD |

---

## 5. Required Regression Controls

Based on the balance diagnostics, all DiD regressions must include:

| Control Variable | Source | Justification |
|---|---|---|
| `urban_share` | Census 2011 | Controls structural urban composition difference |
| `agri_worker_share` | Census 2011 | Controls baseline agricultural sector size |
| `literacy_rate` | Census 2011 | Controls human capital endowment |
| `st_share` | Census 2011 | Controls for tribal district characteristics (Rajasthan/Bihar) |
| `log_population` | Census 2011 | Controls district size |
| State fixed effects | — | Absorbs state-level time-invariant confounders |
| Year fixed effects | — | Absorbs common time trends |

---

## 6. Missing Data Summary

| Variable | Total Missing | Coverage |
|---|---|---|
| `unemp_rate_wt` (primary outcome) | 0 / 295 | **100%** |
| `agri_share_wt` (secondary outcome) | 0 / 295 | **100%** |
| `literacy_rate` (Census control) | 0 / 295 | **100%** |
| `urban_share` (Census control) | 0 / 295 | **100%** |
| `sc_share` / `st_share` | 0 / 295 | **100%** |
| `log_wage_median` | 89 / 295 | 69.8% |
| `edu_secondary_wt` | 295 / 295 | **0% — EXCLUDED** |

> [!CAUTION]
> `edu_secondary_wt` (PLFS secondary education share) is 100% missing — the column was not populated from the raw microdata. This variable must be reconstructed from the PLFS `b2q7` education column before regression if used as a control. It is not required for the primary DiD specification.
