# AIRIS Outcome Selection
## Phase 4C | Selecting Secondary Outcomes for Mechanism Estimation
### Version 1.0 | June 2026

---

## 1. Selection Criteria

Four criteria determine which variables are selected as secondary DiD outcomes:

| Criterion | Requirement |
|---|---|
| **Coverage** | ≥90% complete in R1 sample (48 obs) |
| **Time-variation** | Must differ across 2019-20 and 2023-24 (i.e., not Census controls) |
| **Interpretability** | Must have a clear economic meaning relevant to labour market structure |
| **Mission relevance** | Must contribute to understanding AI-era structural change in rural India |

---

## 2. Variable Evaluation

| Variable | Coverage | Time-Varying | Interpretable | Mission-Relevant | **Selected** |
|---|---|---|---|---|---|
| `unemp_rate_wt` | 100% ✅ | Yes ✅ | Yes ✅ | Yes ✅ | ✅ **PRIMARY** (already estimated) |
| `agri_share_wt` | 100% ✅ | Yes ✅ | Yes ✅ | Yes ✅ | ✅ **SECONDARY — Selected** |
| `nonagri_share_wt` | 100% ✅ | Yes ✅ | Partial ⚠️ | Yes ✅ | ✅ **SECONDARY — Selected (mirror of agri)** |
| `services_share` | 100% ✅ | Yes ✅ | Yes ✅ | Yes ✅ | ✅ **SECONDARY — Selected** |
| `log_wage_median` | 95.8% ✅ | Yes ✅ | Yes ✅ | Yes ✅ | ✅ **TERTIARY — Selected** |
| `edu_secondary_wt` | 0% ❌ | Yes | Yes | Yes | ❌ **EXCLUDED — 100% missing** |
| `n_employed` | 100% | Yes | No ❌ | Partial | ❌ **EXCLUDED — size-dependent count** |
| `worker_participation_rate` | 100% | No ❌ | Yes | Yes | ❌ **EXCLUDED — Census 2011, time-invariant** |
| `agri_worker_share` | 100% | No ❌ | Yes | Yes | ❌ **EXCLUDED — Census 2011, time-invariant** |

---

## 3. Selected Outcomes and Their Role in Mechanism Testing

### 3.1 `agri_share_wt` — Agricultural Employment Share

**Coverage:** 100% (48/48)  
**Range:** 37.7% – 63.4%  
**Why it matters:** The primary mechanism through which AI-era structural change affects rural India is sectoral reallocation — workers moving between agriculture and non-agriculture. If early-connected districts had AI-driven displacement, we would expect agricultural employment to *rise* (displaced workers retreating to subsistence farming) or non-agricultural employment to *fall*. If early-connected districts are experiencing a healthy AI-driven transition, non-agricultural employment should *rise*.

**What β3 from agri_share_wt tells us:**
- β3 > 0 (more agri in early): Consistent with displacement — workers retreating to agriculture
- β3 < 0 (less agri in early): Consistent with structural transformation — workers moving into non-farm jobs
- β3 ≈ 0: Sector composition unchanged; unemployment change is from within-sector dynamics

### 3.2 `services_share` — Services Sector Employment Share

**Coverage:** 100% (48/48)  
**Range:** 15.0% – 38.2%  
**Why it matters:** This is the most AI-exposed sector. If AI diffusion is displacing service-sector workers, services_share should decline in early-connected districts. If it is enabling new service jobs (the optimistic view), it should rise.

**What β3 from services_share tells us:**
- β3 < 0 (less services in early): Displacement signal — service jobs lost in connected districts
- β3 > 0 (more services in early): Expansion signal — new digital service jobs created
- β3 ≈ 0: No differential services sector shift

### 3.3 `nonagri_share_wt` — Non-Agricultural Employment Share

**Note:** By construction, nonagri_share_wt = 100 − agri_share_wt. The β3 for this variable is the exact negative of agri_share_wt's β3. It is included for completeness and to confirm internal consistency, not for independent information.

### 3.4 `log_wage_median` — Median Log Weekly Wage

**Coverage:** 95.8% (46/48; 2 missing are structural zeros in rural wage employment)  
**Range:** 3.45 – 4.13 (exp: ~315–620 Rs/week)  
**Why it matters:** Wages tell us about worker quality and bargaining power — not just quantity of employment. If AI adoption is occurring, wages in early-connected districts should show one of two patterns:
- **Rising wages:** AI is complementing workers, raising their productivity and pay (positive)
- **Falling or flat wages:** AI is substituting for workers, depressing wages (negative)
- **Flat wages + rising unemployment:** Displacement without wage recovery — worst-case scenario

**This is the most policy-relevant outcome after unemployment.**

---

## 4. Mechanism Hypothesis Matrix

| Mechanism | Expected unemp β3 | Expected agri β3 | Expected services β3 | Expected wage β3 |
|---|---|---|---|---|
| **A. Structural Transformation** | Positive (transitional) | Negative | Positive | Positive |
| **B. Labour Displacement** | Positive | Positive | Negative | Negative/Flat |
| **C. Healthy Digital Transition** | Negative | Negative | Positive | Positive |
| **D. No Clear Mechanism** | Any | ≈ 0 | ≈ 0 | ≈ 0 |

This matrix is tested against the actual β3 estimates.
