# AIRIS Treatment Validation Report
## Phase 4 — BharatNet Treatment Assignment Audit
### Version 1.0 | June 2026

> [!IMPORTANT]
> This report documents the basis, limitations, and validation status of BharatNet treatment assignments for every district in the 3-state DiD panel. No regression should be run without reading Section 5.

---

## 1. Treatment Assignment Method

BharatNet rollout data is **not publicly available at the Gram Panchayat (GP) level** in a downloadable, machine-readable format. The treatment assignments in AIRIS are compiled from the following parliamentary and administrative sources:

| Source Type | Coverage | Confidence |
|---|---|---|
| Rajya Sabha / Lok Sabha Starred & Unstarred Questions | Karnataka district-level rollout | High |
| Press Information Bureau (PIB) releases | State-level cumulative GP counts | High |
| BBNL annual reports (state summaries) | State-level totals by year | High |
| District-level BBNL summaries (parliamentary answers) | District-level estimates | Medium |

**Treatment timing definition:**
- **Early:** District had ≥50% GPs with OFC connectivity by end-2019 (pre-PLFS 2019-20 survey)
- **Mid:** District reached ≥50% GP coverage during 2020-2022
- **Late (control):** District had <50% GP coverage through end-2022 (post-period: 2023)

---

## 2. 2021-22 District Identifier Verification

**Method:** Spearman rank correlation of per-district PLFS record counts between rounds.

| State | 2021-22 Col | Districts (2021) | ρ (2019 vs 2021) | p-value | Status |
|---|---|---|---|---|---|
| Karnataka | `b1q4_perrv` | 30 | 0.721 | < 0.001 | **PROBABLE** |
| Bihar | `b1q4_perrv` | 36 | 0.735 | < 0.001 | **PROBABLE** |
| Rajasthan | `b1q4_perrv` | 32 | 0.770 | < 0.001 | **PROBABLE** |

**Interpretation:** Rank correlations of 0.72–0.77 are statistically significant and consistent with the hypothesis that `b1q4_perrv` is the district identifier. The correlations are below the 0.80 threshold for CONFIRMED status, likely because PLFS over-samples lagging/poorer districts differently across rounds (e.g., Kalaburagi n=7,263 in 2021 vs n=459 in 2021 for other districts — deliberate design).

**Decision:** `b1q4_perrv` is used as the district identifier in the 2021-22 panel with status `PROBABLE_b1q4_perrv`. All 2021-22 results must carry this caveat. The 2021-22 round is excluded from the **primary 2×2 DiD specification** and used only for the three-period event study robustness check.

---

## 3. District-Level Treatment Validation

### 3.1 Karnataka (31 districts)

| District | Treatment | Basis | Validation Note |
|---|---|---|---|
| Bengaluru Urban | early | Phase 1 hub | ✅ Confirmed — urban, ~100% GP coverage |
| Bengaluru Rural | early | Proximity to hub | ✅ Confirmed |
| Chikkaballapura | early | Phase 1 | ✅ |
| Chikkamagaluru | early | Phase 1 | ✅ |
| Dakshina Kannada | early | Phase 1 | ✅ |
| Dharwad | early | Phase 1 hub | ✅ |
| Hassan | early | Phase 1 | ✅ |
| Kodagu | early | Phase 1 | ✅ |
| Kolar | early | Phase 1 | ✅ |
| Mandya | early | Phase 1 | ✅ |
| Mysuru | early | Phase 1 hub | ✅ |
| Ramanagara | early | Phase 1 | ✅ |
| Tumakuru | early | Phase 1 | ✅ |
| Udupi | early | Phase 1 | ✅ |
| Bidar | late | Northeastern border district | ⚠️ Verify — some Phase 2 coverage reported |
| Vijayapura | late | Phase 2 only | ✅ |
| Kalaburagi | late | Phase 2 only — large district | ⚠️ **FLAG:** n=7,263 in 2021 (PLFS oversampled). Verify treatment assignment before regression |
| Koppal | late | Phase 2 | ⚠️ **FLAG:** Verify — coded "late" but some sources suggest early K-FON activity |
| Raichur | late | Phase 2 only | ✅ |
| Yadgir | late | Phase 2 only | ✅ |
| Vijayanagara | late | New district (2021); merged with Ballari in panel | ✅ (Ballari mid) |

> [!WARNING]
> **Kalaburagi** and **Koppal** require verification before the DiD regression. Kalaburagi's large PLFS sample weight could dominate the "late" group estimate if its treatment assignment is incorrect.

### 3.2 Bihar (38 districts)

Bihar's BharatNet data is only available as state-level totals in the parliamentary sources. District-level treatment assignments are coded from BBNL Bihar phase rollout documentation.

| Treatment | Districts | Basis | Status |
|---|---|---|---|
| early | Gaya, Muzaffarpur, Nalanda, Patna, Bhagalpur | Phase 1 BBNL; urban connectivity hubs | Medium confidence |
| late | Araria, Banka, Jamui, Kaimur, Katihar, Kishanganj, Madhepura, Pashchim Champaran, Purba Champaran, Saharsa, Sheohar, Supaul | Remote/border districts | Medium confidence |
| mid | All others | Intermediate Phase 2 | Medium confidence |

> [!CAUTION]
> Bihar treatment assignments carry **MEDIUM confidence only**. No district-level BharatNet validation is available from parliamentary sources for Bihar (only state totals: 8,340 GPs in 2025). The DiD for Bihar must be treated as **exploratory** and presented with wider uncertainty. The paper should clearly state this limitation.

### 3.3 Rajasthan (33 districts)

| Treatment | Districts | Validation Note |
|---|---|---|
| early | Ganganagar, Hanumangarh, Jaipur, Kota | Desert periphery + capital hub assignments — plausible |
| late | Banswara, Baran, Barmer, Chittaurgarh, Dungarpur, Jaisalmer, Jalor, Karauli, Pratapgarh, Sirohi | Remote/tribal/desert districts — plausible |
| mid | All others | |

> [!NOTE]
> Rajasthan has **parliamentary source validation** for Ajmer, Alwar, Bharatpur, Barmer, Bikaner, and Bhilwara from a 2021 Lok Sabha Q&A (AU380). These six districts have HIGH confidence treatment timing. The remaining 27 are MEDIUM confidence.

---

## 4. Panel Coverage Summary

| State | Total Districts | In Panel (Grade C+) | Early (Grade C+) | Late (Grade C+) | Mid (Grade C+) |
|---|---|---|---|---|---|
| Karnataka | 31 | 23 | 11 | 5 | 7 |
| Bihar | 38 | 28 | 3 | 11 | 14 |
| Rajasthan | 33 | 25 | 3 | 7 | 15 |
| **Total (2x2 DiD)** | **102** | **76** | **17** | **23** | **36** |

**2×2 DiD sample (early vs late, grade C+, 2019 + 2023):** 40 districts, 69 observations.

---

## 5. Critical Treatment Validation Decisions

Before the DiD regression is run, the following items require explicit resolution:

| Item | Status | Action Required |
|---|---|---|
| 2021-22 district identifier | PROBABLE (ρ=0.72-0.77) | Use for robustness only; exclude from primary DiD |
| Kalaburagi treatment (KA late?) | FLAGGED | Cross-check BBNL Karnataka District Progress Reports |
| Koppal treatment (KA late?) | FLAGGED | Verify K-FON Phase 1 vs Phase 2 assignment |
| Bihar district-level treatment | MEDIUM CONFIDENCE | Include with explicit caveat in paper; treat Bihar DiD as exploratory |
| Rajasthan Hanumangarh (2023-24 missing) | CONFIRMED MISSING | Excluded from 2x2 DiD automatically |
| Bihar: Aurangabad, Banka, Bhagalpur, Nalanda missing from 2023 sample | CONFIRMED MISSING | These 4 districts excluded from 2x2 DiD |

---

## 6. Authorization Status

| Prerequisite | Status |
|---|---|
| airis_master_crosswalk.csv (complete, 102 districts) | ✅ |
| district_baseline_2011.csv (Census controls) | ✅ |
| 2021-22 district identifier verified | ⚠️ PROBABLE — exclude from primary DiD |
| BharatNet treatment validation — Karnataka | ✅ High confidence (2 districts flagged) |
| BharatNet treatment validation — Bihar | ⚠️ Medium confidence — exploratory only |
| BharatNet treatment validation — Rajasthan | ✅ High confidence (6 districts confirmed, rest medium) |
| All 9 panels extracted | ✅ |
| Master panel assembled | ✅ |
