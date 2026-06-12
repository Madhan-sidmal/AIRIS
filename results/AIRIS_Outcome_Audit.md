# AIRIS Outcome Variable Audit
## Phase 4C | Available Outcomes in airis_panel_master.csv
### Version 1.0 | June 2026

---

## 1. Panel Overview

| Property | Value |
|---|---|
| Total rows | 295 |
| Total columns | 47 |
| States | Karnataka, Bihar, Rajasthan |
| Survey years | 2019-20, 2021-22, 2023-24 |
| R1 sample (KA+RJ, early+late, 2019+2023, grade C+) | **48 observations, 27 districts** |

---

## 2. Complete Outcome Variable Inventory

### 2.1 PLFS-Derived Outcome Variables (Time-Varying — DiD Eligible)

| Variable | Coverage (R1) | Missing | Range | Description |
|---|---|---|---|---|
| `unemp_rate_wt` | **100%** (48/48) | 0 | 1.1 – 20.4% | Weighted unemployment rate among rural workers |
| `agri_share_wt` | **100%** (48/48) | 0 | 37.7 – 63.4% | Share of employed workers in agriculture (PLFS broad sector B4Q5=1) |
| `nonagri_share_wt` | **100%** (48/48) | 0 | 36.6 – 62.3% | Non-agricultural employment share (= 100 − agri_share_wt) |
| `services_share` | **100%** (48/48) | 0 | 15.0 – 38.2% | Services-sector employment share — **distinct from nonagri** (corr=0.45) |
| `log_wage_median` | **95.8%** (46/46) | 2 | 3.45 – 4.13 | Median log weekly wages among wage employees (Karnataka 97%, Rajasthan 94%) |
| `edu_secondary_wt` | **0%** (0/48) | 48 | — | Secondary education share — **100% MISSING, column never populated** |

> [!CAUTION]
> `edu_secondary_wt` is entirely missing — the PLFS education variable (`b2q7`) was not extracted from microdata. This variable is **excluded from all analysis**. It cannot serve as a DiD outcome or control variable without re-running the panel builder.

### 2.2 PLFS Count Variables (Size-Dependent — Not Suitable as DiD Outcomes)

| Variable | Coverage | Note |
|---|---|---|
| `n_employed` | 100% | Raw count of employed workers; reflects sample design, not district rates |
| `n_rural_persons` | 100% | Raw count; size-dependent |
| `employed_weight` | 100% | Survey weight sum; scale varies 10⁸ to 10¹⁰; not interpretable as a rate |
| `wage_n` | 100% | Number of wage employees observed; ranges 5–524; reflects sample size |

These are **not suitable DiD outcomes** because they depend on the district's sample size assignment in PLFS, which varies across rounds for design reasons (not district-level change).

### 2.3 Census 2011 Controls (Time-Invariant — NOT DiD Outcomes)

| Variable | Coverage | Note |
|---|---|---|
| `literacy_rate` | 100% | Census 2011 — does not vary across PLFS rounds |
| `female_literacy_rate` | 100% | Census 2011 — time-invariant |
| `sc_share` | 100% | Scheduled Caste share — time-invariant |
| `st_share` | 100% | Scheduled Tribe share — time-invariant |
| `urban_share` | 100% | Urban population share — time-invariant |
| `worker_participation_rate` | 100% | Census 2011 WPR — **time-invariant, not a DiD outcome** |
| `agri_worker_share` | 100% | Census 2011 agricultural worker share — **time-invariant** |

> [!WARNING]
> `worker_participation_rate` and `agri_worker_share` from Census 2011 appear in every panel row but **do not change across survey years** — they are baseline controls. Estimating DiD on these variables will always return β3 ≈ 0 by construction.

---

## 3. Critical Note: `services_share` vs `nonagri_share_wt`

These are **not the same variable** and are not mirror images:

| Property | `nonagri_share_wt` | `services_share` |
|---|---|---|
| Range | 36.6 – 62.3% | 15.0 – 38.2% |
| Correlation | 1.0 (with each other: −1 because nonagri = 100−agri) | 0.45 with nonagri |
| Definition | All non-farm employment | Services-sector employment only |
| Covers | Manufacturing + Construction + Services + Other | Tertiary sector only |

`services_share` captures a subset of `nonagri_share_wt`. The difference (nonagri − services ≈ 21pp) reflects manufacturing and construction employment. Both are PLFS-derived and time-varying, making both eligible for DiD estimation.

---

## 4. Missingness Summary for DiD-Eligible Outcomes

| Outcome | R1 Valid | R1 Missing | 2019 Valid | 2023 Valid | Early Valid | Late Valid |
|---|---|---|---|---|---|---|
| `unemp_rate_wt` | 48 | 0 | 26 | 22 | 26 | 22 |
| `agri_share_wt` | 48 | 0 | 26 | 22 | 26 | 22 |
| `nonagri_share_wt` | 48 | 0 | 26 | 22 | 26 | 22 |
| `services_share` | 48 | 0 | 26 | 22 | 26 | 22 |
| `log_wage_median` | 46 | 2 | 24 | 22 | 25 | 21 |
| `edu_secondary_wt` | 0 | 48 | — | — | — | — |

The two missing `log_wage_median` observations are in the 2019-20 Karnataka early group (districts where no regular wage workers were sampled in the rural areas — genuine structural zero, not data error).
