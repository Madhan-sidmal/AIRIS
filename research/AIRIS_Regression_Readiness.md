# AIRIS Regression Readiness Assessment
## Phase 4A — Final Pre-Regression Checklist
### Version 1.0 | June 2026

> [!IMPORTANT]
> This document is the authoritative gate before any DiD regression is estimated. Every item in Section 2 must have a resolution before `β3` is computed.

---

## 1. Deliverables Status

| Deliverable | Status | Location |
|---|---|---|
| `district_name_concordance.csv` | ✅ COMPLETE | `database/seeds/` |
| `airis_panel_master.csv` (enriched) | ✅ COMPLETE | `data/clean/panel/` |
| `AIRIS_Treatment_Validation_Report.md` | ✅ COMPLETE | `research/` |
| `AIRIS_Balance_Table.md` (v2.0) | ✅ COMPLETE | `research/` |
| `AIRIS_Parallel_Trends_Report.md` | ✅ COMPLETE | `research/` |

**Panel facts:** 295 rows × 47 columns | 3 states | 3 years | 101 unique districts  
**2×2 DiD eligible:** 69 rows, 40 unique districts, 0 unknowns, 0 null treatments

---

## 2. Remaining Methodological Blockers

### BLOCKER 1 — Structural Selection Bias (CRITICAL)
**Finding:** Early-connected districts are systemically more literate, more urban, and less agricultural than late-connected districts **within every state**, not just across states.

| State | Literacy Δ̄ | Urban Δ̄ | Agri Worker Δ̄ |
|---|---|---|---|
| Karnataka | +2.26 (IMBALANCED) | +0.51 (IMBALANCED) | −1.21 (IMBALANCED) |
| Bihar | +2.08 (IMBALANCED) | +2.40 (IMBALANCED) | −2.68 (IMBALANCED) |
| Rajasthan | +3.79 (IMBALANCED) | +2.59 (IMBALANCED) | −2.79 (IMBALANCED) |

**Implication:** BharatNet treatment assignment is **not quasi-random** — it is correlated with pre-existing district development levels. An uncontrolled DiD will attribute the structural advantage of early districts to BharatNet connectivity.

**Resolution required before regression:**
- Include all Census 2011 controls as covariates (literacy, urban share, agri worker share, ST share, population)
- Report both controlled and uncontrolled specifications
- Consider entropy balancing or inverse propensity score weighting as robustness checks

---

### BLOCKER 2 — Bihar Treatment Confidence (HIGH PRIORITY)
**Finding:** Bihar treatment assignments are MEDIUM confidence only (state-level parliamentary sources, no district-level validation).

**Impact:** If Bihar's 3 "early" districts (Gaya, Muzaffarpur, Patna) are actually "late", the DiD estimate for Bihar is sign-reversed.

**Resolution options:**
1. Exclude Bihar from primary specification; treat as exploratory
2. Obtain district-level BBNL Bihar data via RTI application
3. Run sensitivity analysis with Bihar included vs excluded

---

### BLOCKER 3 — 2021-22 District Identifier (MODERATE)
**Finding:** `b1q4_perrv` classified as PROBABLE district identifier (ρ=0.72–0.77, not confirmed).

**Impact:** 3-period event study uses possibly mislabelled districts in 2021. Not critical for the primary 2×2 DiD.

**Resolution:** Exclude 2021-22 from the primary specification. Use only for robustness event study with a caveat.

---

### BLOCKER 4 — `edu_secondary_wt` Missing (LOW PRIORITY)
**Finding:** Education share variable is 100% missing — not extracted from PLFS microdata.

**Impact:** Cannot use education as a time-varying control in the DiD. Use Census literacy instead (time-invariant).

**Resolution:** Acceptable to proceed without — Census literacy is the correct pre-treatment control anyway.

---

### BLOCKER 5 — Kalaburagi / Koppal Treatment Flags (LOW PRIORITY)
**Finding:** Kalaburagi (large n=7,263; coded "late") and Koppal (coded "late") require verification.

**Impact:** Kalaburagi's over-sampling could dominate the "late" group estimate.

**Resolution:** Run leave-one-out sensitivity dropping Kalaburagi before accepting the main result.

---

## 3. Data Quality Summary

| Check | Result |
|---|---|
| Total rows | 295 ✅ |
| Unknown districts | 0 ✅ |
| Null treatment assignments | 0 ✅ |
| `unemp_rate_wt` coverage | 100% ✅ |
| `agri_share_wt` coverage | 100% ✅ |
| Census controls coverage | 100% ✅ |
| `log_wage_median` coverage | 69.8% ⚠️ |
| `edu_secondary_wt` coverage | 0% ❌ (excluded) |
| 2×2 DiD eligible rows | 69 ✅ |
| 2×2 DiD unique districts | 40 ✅ |
| 3-period event study rows | 105 ⚠️ (2021 col PROBABLE) |

---

## 4. Confidence Assessment

| Dimension | Confidence | Basis |
|---|---|---|
| **Data integrity** | **High** | 0 unknowns, 0 null treatments, 100% coverage on primary outcomes |
| **District mapping** | **High** | 101/102 exact concordance across 4 name systems |
| **Karnataka treatment** | **High** | Parliamentary source validation; 2 districts flagged (Kalaburagi, Koppal) |
| **Rajasthan treatment** | **Medium-High** | 6 districts confirmed; 27 medium confidence |
| **Bihar treatment** | **Medium** | State-level only; no district-level confirmation |
| **Pre-treatment balance** | **Low** | Systematic selection imbalance on all Census controls (within-state) |
| **Parallel trends (pooled)** | **Medium** | Pooled pre-trend DiD < ±1pp; within-state moderate concern |
| **Overall regression readiness** | **Medium** | Can proceed with controls; cannot proceed without them |

---

## 5. Recommended Next Step Before First DiD Run

**Do not run bare/uncontrolled DiD.**

The structural selection finding means the coefficient β3 from a bare DiD will absorb the pre-existing development advantage of early-connected districts. This is not a data quality failure — it is the fundamental methodological challenge that makes this project publishable if handled correctly.

### Recommended specification before running:

```python
# Preferred specification
Y_it = α_i + λ_t + β3·(Post2023_t × Early_i) + X_i·γ + ε_it

# Where:
# α_i = district fixed effects (absorbs all time-invariant district characteristics)
# λ_t = year fixed effects (absorbs common time trends)
# X_i = Census 2011 controls (literacy, urban_share, agri_worker_share, st_share, log_pop)
# β3  = coefficient of interest
# Early_i = 1 if early-connected, 0 if late-connected
# Post2023_t = 1 if survey_year == 2023
```

> [!IMPORTANT]
> District fixed effects (α_i) ABSORB the structural selection bias identified in the balance table. The DiD with district FE does not require balance on time-invariant covariates — it controls for them by construction. The Census controls (X_i) remain useful as efficiency controls (reducing residual variance) but are not required for identification when district FE are included.

### This means:

1. **The structural imbalance is NOT a blocker for the FE-DiD** — district fixed effects absorb it
2. **Bihar remains a blocker** — the treatment assignment uncertainty is not fixed by adding FE
3. **The recommended first regression** is a pooled 2×2 DiD with district + year FE, on the primary outcome (unemp_rate_wt), excluding Bihar

### Proposed first regression sequence:

| Reg | Sample | FE | Controls | Outcome |
|---|---|---|---|---|
| R1 | KA only, early+late, 2019+2023 | District+Year | None | unemp_rate_wt |
| R2 | KA only, early+late, 2019+2023 | District+Year | Census controls | unemp_rate_wt |
| R3 | KA+RJ, early+late, 2019+2023 | District+Year+State×Year | Census controls | unemp_rate_wt |
| R4 | All 3 states, early+late, 2019+2023 | District+Year+State×Year | Census controls | unemp_rate_wt |
| R5 | All 3 states, all groups, 2019+2021+2023 | District+Year | Census controls | unemp_rate_wt |
| Robustness | R4 but excl. Kalaburagi, Jaipur, Kota, Patna | — | — | unemp_rate_wt |

---

## 6. Authorization to Run Regression

**Condition to unlock regression:**

☐ Researcher confirms they understand district FE absorb the structural selection imbalance  
☐ Bihar exploratory-only status is accepted  
☐ Kalaburagi leave-one-out sensitivity is planned  
☐ 2021-22 robustness check is labelled as using PROBABLE district identifier  

Once these four conditions are explicitly acknowledged, R1 through R4 can be estimated.
