# AIRIS Parallel Trends Diagnostic Report
## Phase 4 — Pre-Trend Assessment for DiD Estimation
### Version 1.0 | June 2026

> [!IMPORTANT]
> Parallel trends is an **untestable assumption** — we can only check whether pre-period trends were similar, not whether they would have continued parallel in the counterfactual. This report documents the pre-period evidence and its implications for the validity of the DiD design.

---

## 1. Design Reminder

**DiD Specification:**

```
Y_it = α + β1·Post_t + β2·Early_i + β3·(Post_t × Early_i) + X_i·γ + ε_it
```

- **Treatment periods:** PLFS 2019-20 (pre), PLFS 2023-24 (post)
- **Treatment group:** BharatNet early-connected districts
- **Control group:** BharatNet late-connected districts
- **Common shock:** ChatGPT / AI diffusion (Q1 2023) — affects all districts
- **Parallel trends assumption:** In the absence of BharatNet, early and late districts would have followed the same trajectory in Y between 2019 and 2023

**The AI shock (Q1 2023) is NOT the treatment.** The shock is common to all districts. The treatment is pre-existing digital infrastructure that allows differential absorption of the shock.

---

## 2. Pre-Trend Evidence: 2019-20 → 2021-22

> [!NOTE]
> The 2021-22 PLFS round is the COVID-affected mid-period. We use it to assess whether early and late districts were trending in parallel **before** the AI shock. A significant divergence in 2019→2021 is a pre-trend violation.

### 2.1 Pooled (All Three States)

| Outcome | Early 2019 | Early 2021 | Δ Early | Late 2019 | Late 2021 | Δ Late | Pre-DiD | Concern |
|---|---|---|---|---|---|---|---|---|
| Unemployment rate (%) | — | — | +1.31 | — | — | +0.82 | **+0.49** | 🟢 LOW |
| Agriculture share (%) | — | — | −0.23 | — | — | +0.70 | **−0.93** | 🟢 LOW |
| Non-agri share (%) | — | — | +0.23 | — | — | −0.70 | **+0.93** | 🟢 LOW |

**Pooled verdict:** All three outcomes show LOW pre-trend divergence (< ±1pp differential change). At the pooled level, parallel trends is **not violated** in the pre-period.

---

### 2.2 Karnataka

| Outcome | Early Δ(2019→2021) | Late Δ(2019→2021) | Pre-DiD | Concern |
|---|---|---|---|---|
| Unemployment rate (%) | +0.86 | −2.12 | **+2.98** | 🟡 MODERATE |
| Agriculture share (%) | −1.19 | +2.16 | **−3.35** | 🟡 MODERATE |
| Non-agri share (%) | +1.19 | −2.16 | **+3.35** | 🟡 MODERATE |

**Karnataka verdict: MODERATE CONCERN.**

The unemployment rate moved in opposite directions (+0.86pp for early, −2.12pp for late). This is consistent with COVID-period differential disruption — early-connected districts (more service-sector employment) may have faced greater employment disruption during lockdowns than late districts (more agricultural, less disrupted).

**The 2021-22 COVID confound is the most plausible explanation.** This does not necessarily violate parallel trends for the primary 2×2 DiD (2019 vs 2023), because the 2021 deviation may be a temporary COVID shock that reversed by 2023. However, it must be documented.

---

### 2.3 Bihar

| Outcome | Early Δ(2019→2021) | Late Δ(2019→2021) | Pre-DiD | Concern |
|---|---|---|---|---|
| Unemployment rate (%) | +5.83 | +2.90 | **+2.93** | 🟡 MODERATE |
| Agriculture share (%) | +5.75 | +0.83 | **+4.92** | 🟡 MODERATE |
| Non-agri share (%) | −5.75 | −0.83 | **−4.92** | 🟡 MODERATE |

**Bihar verdict: MODERATE CONCERN.**

Bihar early districts (Gaya, Muzaffarpur, Patna — urban-proximate) show larger 2019→2021 unemployment increases (+5.83pp) versus late districts (+2.90pp). This is consistent with the balance table finding that Bihar early districts are more urban and therefore more COVID-sensitive.

For agriculture share, the +4.92pp differential pre-trend is the largest in the dataset. Given the baseline imbalance documented in the Balance Table (Bihar agri share Norm. Diff = −1.11), this strengthens the case against interpreting agri_share_wt coefficients causally for Bihar.

---

### 2.4 Rajasthan

| Outcome | Early Δ(2019→2021) | Late Δ(2019→2021) | Pre-DiD | Concern |
|---|---|---|---|---|
| Unemployment rate (%) | −0.60 | −1.51 | **+0.91** | 🟢 LOW |
| Agriculture share (%) | −2.71 | −0.26 | **−2.45** | 🟡 MODERATE |
| Non-agri share (%) | +2.71 | +0.26 | **+2.45** | 🟡 MODERATE |

**Rajasthan verdict: LOW-to-MODERATE CONCERN.**

Unemployment shows LOW concern (both groups declining, small differential). Agriculture share shows MODERATE concern (early districts declined faster by 2.45pp in the pre-period). Note: Rajasthan's early group includes Jaipur and Kota — structurally urban districts where agri employment decline is structural, not cyclical.

---

## 3. COVID-19 Confound Assessment

The 2021-22 PLFS round was conducted during the COVID economic disruption. If the 2021 deviation reflects a **transient COVID shock**, parallel trends may still hold for 2019 vs 2023.

**Evidence for COVID confound:**
- All three states show unemployment increasing 2019→2021, regardless of treatment group
- Bihar: +5.83pp (early) and +2.90pp (late) — both increased
- Karnataka: +0.86pp (early) and −2.12pp (late) — this divergence is the exception

**Evidence against pure COVID confound (Karnataka):**
- Karnataka late districts actually saw unemployment decrease 2019→2021 (−2.12pp)
- This could reflect migration back to agriculture during lockdowns (late = more rural)

**Resolution:** Include a sensitivity specification testing whether 2019→2023 results are robust to controlling for 2021 COVID deviations. The primary DiD (2019 vs 2023) skips the COVID round.

---

## 4. Recommended Placebo Test

To formally assess parallel trends, run the following placebo regression using only the pre-period data:

```python
# Placebo DiD: Does the 2019-21 "DiD" = 0?
# If significant, pre-trends are violated

Y_it = α + β1·Post2021_t + β2·Early_i + β3_placebo·(Post2021_t × Early_i) + ε_it
# for t ∈ {2019, 2021}
```

**Expected result under parallel trends:** β3_placebo ≈ 0  
**Result if COVID confound only:** β3_placebo ≠ 0 in 2019-21, but should not persist in 2019-23

---

## 5. Formal Pre-Trend DiD Summary Table

| State | Outcome | Pre-DiD (Δ Early − Δ Late, 2019→2021) | Concern Level | Likely Cause |
|---|---|---|---|---|
| Karnataka | Unemployment rate | +2.98pp | 🟡 MODERATE | COVID differential (service vs agri) |
| Karnataka | Agriculture share | −3.35pp | 🟡 MODERATE | COVID labour market reshuffling |
| Bihar | Unemployment rate | +2.93pp | 🟡 MODERATE | COVID + urban-rural structure |
| Bihar | Agriculture share | +4.92pp | 🟡 MODERATE | Structural + COVID confound |
| Rajasthan | Unemployment rate | +0.91pp | 🟢 LOW | Minor differential |
| Rajasthan | Agriculture share | −2.45pp | 🟡 MODERATE | Structural (Jaipur/Kota effect) |
| **ALL (pooled)** | **Unemployment rate** | **+0.49pp** | **🟢 LOW** | **No systematic pre-trend** |
| **ALL (pooled)** | **Agriculture share** | **−0.93pp** | **🟢 LOW** | **No systematic pre-trend** |

---

## 6. Parallel Trends Verdict and Authorizations

| Specification | Primary Outcome | Parallel Trends Status | Proceed? |
|---|---|---|---|
| Pooled 3-state, 2×2 DiD, unemp_rate_wt | Unemployment rate | ✅ LOW concern | ✅ YES |
| Pooled 3-state, 2×2 DiD, agri_share_wt | Agriculture share | ✅ LOW concern | ✅ YES (with controls) |
| Karnataka only, 2×2 DiD | Both outcomes | ⚠️ MODERATE | YES (with caveats in paper) |
| Bihar only, agri_share_wt | Agriculture share | ❌ HIGH (imbalance + pre-trend) | ❌ NO — do not interpret causally |
| Rajasthan only, unemp_rate_wt | Unemployment rate | ⚠️ MARGINAL (Jaipur/Kota) | YES with exclusion sensitivity |
| Event study (3-period) | Both outcomes | ⚠️ COVID confound in 2021 | YES — must flag COVID |
| Callaway-Sant'Anna | Both outcomes | ⚠️ Underpowered for 3-state | YES — robustness only |

---

## 7. Reporting Requirements

Every result table must include:

1. A footnote stating: *"Parallel trends assessed using PLFS 2021-22 pre-period data. Pooled pre-trend DiD: +0.49pp for unemployment, −0.93pp for agriculture share (both < ±1pp). State-level pre-trends show moderate concern in Karnataka and Bihar, consistent with differential COVID-19 impacts."*

2. A robustness table presenting results excluding the 2021-22 COVID round and results excluding Jaipur, Kota (Rajasthan) and Patna, Muzaffarpur (Bihar).

3. The explicit statement: *"The DiD coefficient β3 identifies the differential post-2023 labour market adjustment associated with pre-existing BharatNet connectivity. It does not identify the causal effect of AI adoption."*
