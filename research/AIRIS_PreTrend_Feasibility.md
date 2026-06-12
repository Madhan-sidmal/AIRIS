# AIRIS Pre-Trend Feasibility Assessment
## Phase 3 — Panel Alignment and DiD Design Viability
### Version 1.0 | June 2026

> [!IMPORTANT]
> This document assesses whether the Karnataka PLFS panel is sufficient to support the planned DiD estimation before any regression is run. All findings are based on empirically extracted data from the three PLFS rounds.

---

## 1. Panel Summary

| Round | State | Districts Extracted | Grade C+ (n≥200) | Grade D (n<200) |
|---|---|---|---|---|
| 2019-20 | Karnataka (29) | 30 | 23 | 7 |
| 2021-22 | Karnataka (29) | 30 | 24 | 6 |
| 2023-24 | Karnataka (29) | 31 | 23 | 8 |

**Districts in all 3 rounds (Grade C+):** 18  
**Districts in 2019-20 and 2023-24 only (Grade C+):** 20  
**Note:** Vijayanagara appears only in 2023-24 (created Aug 2021). It is excluded from the panel and merged into Ballari.

---

## 2. Feasibility by Estimator

### 2.1 Two-Period 2×2 DiD (2019-20 pre vs 2023-24 post)

**Status: FEASIBLE ✅**

| Parameter | Value |
|---|---|
| Pre-period | PLFS 2019-20 |
| Post-period | PLFS 2023-24 |
| Treatment | BharatNet early-connected (≥50% GP coverage by 2019) |
| Control | BharatNet late-connected (post-2022) |
| Usable districts (Grade C+, both rounds) | 20 |
| Of which: early-connected | ~9 |
| Of which: late-connected | ~4 |
| Of which: mid-connected (excluded in primary spec) | ~7 |

**Minimum detectable effect at n=13 districts (treated + control), 80% power:**
- Unemployment rate: ~3.5 percentage points
- Agri share: ~5.0 percentage points

This MDE is large relative to the observed pre-post changes. Karnataka alone may be underpowered for small effects. The **multi-state extension (Karnataka + Bihar + Rajasthan) is necessary** for publication-level power.

---

### 2.2 Three-Period Event Study (2019 pre, 2021 mid, 2023 post)

**Status: FEASIBLE WITH CAVEATS ⚠️**

| Parameter | Value |
|---|---|
| Three survey years | 2019-20, 2021-22, 2023-24 |
| Districts in all 3 rounds (Grade C+) | **18** |
| 2021-22 district column | `b1q4_perrv` — **PROBABLE but unverified** |
| Vijayanagara | Excluded (not in 2019 or 2021) |

**Caveats:**
1. The 2021-22 district identifier (`b1q4_perrv`) is not explicitly labelled as the district code in the publicly available PLFS 2021-22 codebook. It produces 30 unique sequential values for Karnataka, consistent with a district identifier, but must be validated against published PLFS 2021-22 sample counts before use.
2. An event study with only 3 periods cannot formally test pre-trends — it can only verify that the 2019→2021 trend does not significantly differ between groups (see Section 3 below).

---

### 2.3 Callaway-Sant'Anna Staggered DiD

**Status: FEASIBLE IN PRINCIPLE, UNDERPOWERED FOR KARNATAKA ALONE ⚠️**

| Parameter | Value |
|---|---|
| Treatment cohorts | Early (treated ~2019), Mid (treated ~2021), Late (control) |
| Requires | Cohort-specific ATT estimates per time period |
| Sample per cohort × time cell | ~4-9 districts (very small) |
| Minimum recommended | ≥ 10 units per cohort for reliable estimation |

**Conclusion:** Callaway-Sant'Anna is the correct estimator for staggered timing, but is underpowered with Karnataka alone (3–9 districts per cohort). It becomes viable with the multi-state panel (~100 total districts).

---

## 3. Pre-Trend Evidence (Empirical)

The following uses empirically extracted data from the 2019-20 and 2021-22 panels.

**This is the pre-shock period** (ChatGPT shock = Q1 2023). The BharatNet "treatment" had been received by early districts before 2019.

### 3.1 Unemployment Rate

| Group | 2019-20 | 2021-22 | Δ (2019→2021) |
|---|---|---|---|
| **Early-connected** | 5.4% | 8.2% | **+2.8 pp** |
| **Late-connected** | 8.0% | 5.7% | **−2.3 pp** |
| **Difference-in-differences** | | | **+5.1 pp** |

> [!WARNING]
> The pre-period trends for early and late groups are moving in **opposite directions** on unemployment. Early districts saw unemployment rise by 2.8pp during 2019-21; late districts fell by 2.3pp.
>
> This is a **potential parallel trends violation** for the 2×2 DiD using unemployment as an outcome variable. The divergent pre-trends could reflect:
> - COVID-19 differential impact (2021-22 was a COVID-affected round)
> - Real differences in labour market dynamics by connectivity
> - Sampling noise in small-sample district estimates
>
> **This must be reported and a robustness test using a placebo DiD on the 2019→2021 period must be included in the paper.**

### 3.2 Agricultural Employment Share

| Group | 2019-20 | 2021-22 | Δ (2019→2021) |
|---|---|---|---|
| **Early-connected** | 51.9% | 49.8% | −2.1 pp |
| **Late-connected** | 50.1% | 50.2% | +0.1 pp |
| **Difference-in-differences** | | | −2.2 pp |

> [!NOTE]
> Agricultural share shows small, plausibly parallel trends (both groups near 50%, difference of 2.2pp over the pre-period). The 2019-21 divergence is much smaller than for unemployment and may reflect sampling variation. This outcome variable has better pre-trend behavior than unemployment.

---

## 4. COVID-19 Confound Assessment

The 2021-22 PLFS round was conducted during the COVID-19 recovery period. This creates a known confound:

- Early-connected districts may have had **differential COVID impact** (better-connected → more non-farm service employment → more disruption during lockdowns)
- Late-connected districts (primarily agricultural) may have been **partially insulated** (farm work continued during lockdowns)

**Implication:** The 2021-22 round should be used primarily as a robustness check (event study), not as the primary outcome measure. The main DiD should use 2019-20 (clean pre-period) and 2023-24 (clean post-period) only.

---

## 5. Sample Adequacy Assessment

### Grade C+ Districts by Treatment Group (Karnataka, 2023-24)

| Treatment | Districts | Grade C+ | Key Districts |
|---|---|---|---|
| Early | 14 | 9 | Bengaluru Urban*, Bengaluru Rural, Mysuru, Dharwad, Dakshina Kannada, Koppal†, Kalaburagi‡ |
| Mid | 10 | 7 | Bagalkote, Belagavi, Chamarajanagara, Chitradurga, Davangere, Haveri, Shivamogga |
| Late | 7 | 4 | Bidar, Vijayapura, Raichur, Yadgir |

*Bengaluru Urban: structurally urban — recommend excluding from DiD primary spec  
†Koppal: coded "early" but a less-connected district — verify BharatNet treatment  
‡Kalaburagi: largest PLFS sample (n=6,798) — Grade A but coded "late" — verify treatment

---

## 6. Design Recommendation

Based on empirical assessment:

| Question | Answer |
|---|---|
| **2×2 DiD feasible?** | **Yes, with low power** — viable for a working paper, insufficient for publication alone |
| **Event study (3 period) feasible?** | **Yes, with caveats** — verify 2021-22 district identifier; flag COVID confound |
| **Callaway-Sant'Anna feasible?** | **Only with multi-state panel** (Karnataka + Bihar + Rajasthan) |
| **Parallel trends testable?** | **Partially** — pre-trend divergence on unemployment is a concern; agri share shows better behavior |
| **Immediate next step?** | **Run multi-state panel extraction for Bihar and Rajasthan (PLFS 2019 and 2023)** |

---

## 7. Unresolved Issues (Blocking Regression)

1. **2021-22 district identifier** — `b1q4_perrv` must be confirmed against PLFS 2021-22 Annual Report sample counts
2. **Rajasthan boundary** — verify PLFS 2023-24 uses 2011 district boundaries (33 districts), not 2023 boundaries (50 districts)
3. **BharatNet treatment validation** — current treatment assignment is `COMPILED_PUBLIC`. Verify Kalaburagi (late) and Koppal (early) specifically before the regression — they are counter-intuitive assignments
4. **COVID-19 specification test** — run unemployment DiD separately for 2019→2021 as a placebo. If β3 ≠ 0, document and include in robustness section
5. **Multi-state PLFS extraction** — Bihar (state_code=10) and Rajasthan (state_code=8) for 2019-20 and 2023-24

---

## 8. Authorization Status for Regression

| Prerequisite | Status |
|---|---|
| `airis_master_crosswalk.csv` | ✅ COMPLETE |
| `district_baseline_2011.csv` | ✅ COMPLETE |
| `PLFS_Harmonization_Report.md` | ✅ COMPLETE |
| `AIRIS_PreTrend_Feasibility.md` | ✅ COMPLETE (this document) |
| Sector-code validation (agri_share bug) | ✅ FIXED |
| 2021-22 district identifier verified | ❌ PENDING |
| Rajasthan boundary confirmed | ❌ PENDING |
| Multi-state PLFS extraction | ❌ PENDING |

> [!CAUTION]
> **DO NOT RUN THE DiD REGRESSION** until the unresolved items in Section 7 are resolved. The district-year panel can be assembled, but the regression specification must not be estimated until the parallel trends issue is documented and addressed.
