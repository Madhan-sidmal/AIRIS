# AIRIS Phase 4B — Publication Readiness Assessment
## First DiD Results: β3 = +3.03pp (p=0.040, wild cluster bootstrap)
### Version 1.0 | June 2026

---

## 1. Result Summary

> Early-connected districts experienced **3.03 percentage points higher unemployment growth** (95% CI: [+0.07, +5.84], wild bootstrap p=0.040) relative to late-connected districts between 2019-20 and 2023-24, after absorbing district and year fixed effects.

The convergence of unemployment rates between early and late districts (gap narrowing from 4.0pp to 1.6pp) is statistically detectable and qualitatively stable across 5 specifications.

---

## 2. What Is Ready

### Data ✅
- 295-row panel, 47 columns, 0 unknowns, 0 null treatments
- Census 2011 controls matched 102/102 districts
- District name concordance across 4 naming systems

### Estimation ✅
- Within-estimator correctly handles unbalanced T=2 panel
- Small-sample clustered SE (CR1) + wild bootstrap (B=999, G=27)
- 5 sensitivity specifications all return positive β3

### Interpretation ✅
- β3 explicitly labelled as "differential labour-market adjustment," NOT AI causation
- Two-tier language maintained (Tier 1: observed gap convergence; Tier 2: structural mechanism)
- No composite scores or indices presented as causal

---

## 3. What Is NOT Ready

### BLOCKER — Bihar missing from primary specification
Bihar (38 districts) is excluded due to medium-confidence treatment assignment. Including Bihar would increase G from 27 to ~60 and substantially improve power. The primary result rests on 27 districts across 2 states — defensible but not definitive.

**Resolution:** District-level BharatNet Bihar validation (RTI or BBNL portal). This is the single highest-priority action before Working Paper 1.

### CONCERN — p-value straddling 0.05
The asymptotic clustered p-value (0.061) does not cross 0.05. The bootstrap p-value (0.040) does. A referee could focus on the 0.061 figure. This is an honest limitation of G=27 — the result should be presented as "marginally significant" with full disclosure of both inference methods.

### LIMITATION — No time-varying controls
The model includes district FE (absorbing time-invariant Census variables) and year FE (absorbing common trends) but no time-varying district-level controls. Post-2019 variation in MGNREGS, agricultural prices, or state-specific policies could confound β3. These are unlikely to be correlated specifically with BharatNet timing but cannot be ruled out.

### LIMITATION — Single outcome
Results exist only for `unemp_rate_wt`. Agriculture share, non-agriculture share, and wage outcomes have not been estimated. A complete labour-market picture requires all three.

---

## 4. Publication-Readiness Score

| Dimension | Status | Score |
|---|---|---|
| Data quality and provenance | Clean, documented, reproducible | 9/10 |
| Identification strategy | DiD with district FE; well-motivated | 7/10 |
| Statistical validity | Bootstrap p=0.040; G=27; marginal | 6/10 |
| Interpretation discipline | Strict; no overclaiming | 9/10 |
| Sensitivity analysis | 5 specs; sign stable | 7/10 |
| Multi-outcome coverage | Unemployment only (WP1 incomplete) | 5/10 |
| Geographic scope | 2 states; Bihar missing | 6/10 |
| **Overall** | | **7/10 — Working paper / preprint stage** |

**Target journal stage:** Working paper / preprint. Not ready for journal submission without Bihar, additional outcomes, and time-varying controls.

---

## 5. Recommended Next Steps (Priority Order)

| Priority | Task | Effort |
|---|---|---|
| **1** | Validate Bihar district-level BharatNet treatment | External dependency |
| **2** | Add Bihar to specification once treatment confirmed | 1 session |
| **3** | Estimate for secondary outcomes (agri_share_wt, nonagri_share_wt) | 1 session |
| **4** | Add time-varying controls (MGNREGS expenditure, rainfall anomaly) | Data collection |
| **5** | Run Callaway-Sant'Anna staggered DiD (3-state) | 1 session |
| **6** | Write Working Paper 1 draft | 2-3 sessions |

---

## 6. Draft Abstract

> We study whether pre-existing digital infrastructure affects district-level labour-market adjustment during periods of rapid AI diffusion. Using a difference-in-differences design with district and year fixed effects, we compare unemployment trajectories in districts with early versus late BharatNet optical fibre connectivity across Karnataka and Rajasthan (India) between 2019-20 and 2023-24 — spanning the ChatGPT-era AI diffusion shock. Early-connected districts experienced 3.03 percentage points higher unemployment growth relative to late-connected districts (95% CI: [0.07, 5.84]; wild cluster bootstrap p=0.040). This convergence — from a 4.0pp pre-period gap to a 1.6pp post-period gap — is consistent with accelerated structural adjustment in digitally connected labour markets during AI diffusion, though we cannot identify the specific mechanism. Results are stable across five sensitivity specifications. Our findings suggest that connectivity, while necessary for AI-era development, does not insulate districts from near-term labour-market disruption.
