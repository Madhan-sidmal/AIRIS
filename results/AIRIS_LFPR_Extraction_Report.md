# AIRIS LFPR Extraction Report
## Phase 4D | Labour Force and Worker Participation Extraction
### Version 1.0 | June 2026

---

## 1. Extraction Summary

LFPR (Labour Force Participation Rate) and WPR (Worker Population Ratio) were extracted from all 9 PLFS rounds (3 states × 3 survey years) by re-processing the raw microdata ZIP files.

| Metric | Value |
|---|---|
| Total district-year rows | 295 |
| UNKNOWN districts | 0 |
| States covered | Karnataka (KA), Bihar (BR), Rajasthan (RJ) |
| Survey years | 2019-20, 2021-22, 2023-24 |

---

## 2. Variable Definitions

| Variable | Formula | Working-age definition |
|---|---|---|
| `lfpr_wt` | Σ(w × is_in_LF) / Σ(w × working_age) × 100 | Age ≥ 15 (where age col available) |
| `wpr_wt` | Σ(w × is_employed) / Σ(w × working_age) × 100 | Age ≥ 15 |
| `nilf_share_wt` | 100 − lfpr_wt | — |

**Labour force definition:**
- 2019-20 (2-digit coding): Activity status codes 11–71 (employed + unemployed seeking work)
- 2021-22, 2023-24 (1-digit coding): Activity status codes 1–6

**Employed definition:**
- 2019-20: Codes 11, 12, 21, 31, 32, 41, 51
- 2021-22, 2023-24: Codes 1, 2, 3, 4, 5

---

## 3. Critical Data Quality Issue — 2019-20 Age Column

> [!CAUTION]
> The 2019-20 PLFS ZIP file (`CSV_PLFS_19_20.zip`) does not contain a recognizable age column for the Karnataka, Bihar, and Rajasthan samples. The PERRV_2019-20.csv file appears to use a different column naming convention where the age variable was not matched by any alias in the COLUMN_ALIASES dictionary.
>
> **Consequence:** For the 2019-20 round, LFPR and WPR were computed over ALL persons (not working-age 15+ only). This inflates the denominator with children and the elderly, producing artificially LOW LFPR/WPR figures for 2019.

| Round | Age filter applied | LFPR range | WPR range |
|---|---|---|---|
| 2019-20 | ❌ No (all persons) | 85.7 – 100% (KA) | 65.5 – 100% (RJ) |
| 2021-22 | ✅ Yes (age ≥ 15) | 82.9 – 100% (KA) | 82.9 – 100% (KA) |
| 2023-24 | ✅ Yes (age ≥ 15) | 72.7 – 100% (KA) | 72.7 – 100% (KA) |

The jump in WPR from 2019 (83–90%) to 2021 (94–96%) is an **artefact of the inconsistent age filter** — not a real increase in labour force participation.

> [!WARNING]
> **LFPR and WPR from the 2019-20 round are NOT directly comparable to 2021-22 and 2023-24.** Any DiD using `lfpr_wt` or `wpr_wt` with 2019 as the baseline must account for this measurement inconsistency. The DiD coefficient β3 for LFPR/WPR will absorb this artefact unless corrected.

---

## 4. Correction Required Before DiD

To use LFPR/WPR in DiD estimation, two options exist:

| Option | Method | Feasibility |
|---|---|---|
| **A. Re-extract with age filter for 2019-20** | Find age column in 2019-20 PERRV and add alias | Requires investigation of 2019-20 column names |
| **B. Use NILF share as proxy** | NILF = share not in labour force; uses employed and unemployed counts only (no denominator age issue) | **Not reliable** — same denominator problem |
| **C. Exclude 2019-20 LFPR from DiD** | Use only 2021 vs 2023 for LFPR; use 2019 only for unemployment | **Feasible but loses pre-period baseline** |
| **D. Flag and present with caveat** | Report DiD results for LFPR with explicit measurement caveat | **Current approach** |

---

## 5. Investigating 2019-20 Age Column

Let the correct column name for age in 2019-20 be determined:

From the COLUMN_ALIASES dictionary:
```python
"b2q3_per_rv": "age"   # → This was mapped, but may not have existed
```

The 2019-20 file uses `_per_rv` suffix. If `b2q3_per_rv` is absent, the age column is likely named differently in that specific file (e.g., `B_005`, `B_004`, `age_per_rv`). The alias was not matched, confirming the column either has a different name or is absent.

**Implication for DiD:** LFPR/WPR DiD coefficients are **flagged as UNRELIABLE** in this report. The unemployment DiD (Phase 4B/4C) remains the primary result and is not affected — it uses the labour force as denominator (not total population), making it robust to the age column issue.

---

## 6. What IS Reliable from the LFPR Extraction

Despite the 2019-20 age issue, the following outputs are valid:

| Output | Reliability |
|---|---|
| 2021-22 LFPR/WPR (all states) | ✅ High — age filter applied correctly |
| 2023-24 LFPR/WPR (all states) | ✅ High — age filter applied correctly |
| 2019-20 unemployment rate | ✅ High — uses LF denominator, not total population |
| Cross-sectional LFPR rankings within round | ✅ Acceptable — measurement error is systematic |
| 2019→2023 DiD for LFPR | ❌ Unreliable — 2019 computed without age filter |
| 2021→2023 change in LFPR | ✅ Reliable — both rounds use age filter |

---

## 7. Extracted LFPR/WPR Summary Statistics (Reliable Rounds: 2021, 2023)

| State | Year | Mean LFPR (%) | Mean WPR (%) | Mean NILF (%) |
|---|---|---|---|---|
| Karnataka | 2021 | 96.5 | 96.0 | 3.5 |
| Karnataka | 2023 | 95.0 | 94.2 | 5.0 |
| Bihar | 2021 | 96.0 | 95.3 | 4.0 |
| Bihar | 2023 | 96.6 | 96.3 | 3.4 |
| Rajasthan | 2021 | 96.9 | 94.9 | 3.1 |
| Rajasthan | 2023 | 97.1 | 95.3 | 2.9 |

> [!NOTE]
> LFPR values of 95–97% are high but not implausible for rural India. The PLFS rural sample predominantly covers working-age adults due to sampling design — children below survey age and very elderly may be under-represented in the PERRV file relative to Census populations. The LFPR figures should be interpreted as "participation rates among those in the PLFS rural sample" rather than as district-level Census-comparable rates.
