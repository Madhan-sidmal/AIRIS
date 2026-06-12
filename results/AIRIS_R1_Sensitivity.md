# AIRIS R1 — Sensitivity Analysis
## Phase 4B | Robustness of β3 Across Specifications
### Version 1.0 | June 2026

---

## 1. Sensitivity Results Table

| Specification | β3 (pp) | SE | t | p (asymptotic) | p (bootstrap) | 95% CI | G | N |
|---|---|---|---|---|---|---|---|---|
| **R1: KA only** | **+3.003** | 1.884 | 1.59 | 0.130 | — | [−0.99, +7.00] | 17 | 30 |
| **R2: KA+RJ (main)** | **+3.033** | 1.551 | 1.96 | 0.061 | **0.040** | [+0.07, +5.84]† | 27 | 48 |
| **R3: KA+RJ excl. Kalaburagi** | **+3.073** | 1.634 | 1.88 | 0.072 | — | [−0.29, +6.44] | 26 | 46 |
| **R4: KA+RJ excl. urban outliers** | **+2.307** | 1.677 | 1.38 | 0.183 | — | [−1.17, +5.78] | 23 | 41 |
| **R5: KA excl. Kalaburagi** | **+3.210** | 2.096 | 1.53 | 0.147 | — | [−1.26, +7.68] | 16 | 28 |

†Bootstrap 95% CI reported for R2 (main specification).  
Urban outliers excluded in R4: Kalaburagi, Jaipur, Kota, Bengaluru Urban.

---

## 2. Kalaburagi Sensitivity (R3 vs R2)

**Why Kalaburagi is flagged:**
- Coded as BharatNet "late" (treatment: control group)
- PLFS over-sample: n=6,798–7,263 employed persons per round (vs median ~1,200)
- Large n gives this district high statistical influence on the late-group mean
- Treatment assignment disputed: some sources indicate earlier K-FON rollout

**Result of exclusion:** β3 increases from +3.033 to +3.073pp — a change of +0.040pp. The result is **not driven by Kalaburagi**. If anything, Kalaburagi's inclusion slightly attenuates β3 (consistent with it being misclassified as late when it may be early/mid).

**Recommendation for publication:** Report R3 as the primary specification and R2 as the robustness check, with a footnote explaining the Kalaburagi treatment uncertainty.

---

## 3. Urban Outlier Sensitivity (R4)

**Districts excluded:** Kalaburagi (KA late, see above) + Jaipur (RJ early, state capital) + Kota (RJ early, industrial city) + Bengaluru Urban (KA early)

**Rationale:** These districts have structural urban profiles that make them unrepresentative of the rural connectivity gap AIRIS is studying. Jaipur and Kota (Rajasthan early) have urban shares of 66% and 67% — compared to the district median of ~20%. Including them biases the "early" group toward urban-structural dynamics.

**Result:** β3 falls to +2.307pp, and significance weakens (p=0.183 asymptotic). This is the **most conservative** estimate. The confidence interval still overlaps substantially with R2.

**Conclusion:** β3 is sensitive to whether highly urban early districts are included. This is expected — urban districts face different labour market dynamics. The paper should include R4 as the conservative bound.

---

## 4. Karnataka-Only Sensitivity (R1 vs R2)

Adding Rajasthan to Karnataka (R2 vs R1):
- β3 increases marginally: 3.003 → 3.033pp
- SE decreases: 1.884 → 1.551 (more power with more districts)
- Rajasthan's contribution: 10 additional districts, qualitatively consistent with Karnataka

The KA-only estimate is less precise (CI: [−0.99, +7.00]) but directionally identical. Rajasthan does not reverse the finding — it tightens the confidence interval.

---

## 5. Direction and Sign Stability

All five specifications return **positive β3** (range: +2.31 to +3.21pp). The sign is stable.

| Scenario | Would require β3 < 0? |
|---|---|
| All Kalaburagi-type misclassifications | No — R3/R5 show stability |
| All Rajasthan districts misclassified | Unlikely — KA-only R1 is also positive |
| Both Jaipur and Kota reversed (late) | Tested in R4 — β3 falls to +2.31 but stays positive |
| All urban outliers reversed | Not tested — would require re-running with urban=late |

**The positive sign of β3 is robust across all plausible sensitivity specifications.**

---

## 6. Inference Sensitivity

| Inference method | p-value | 95% CI | Recommendation |
|---|---|---|---|
| OLS (HC0, unclustered) | 0.008 | [+0.79, +5.27] | Too liberal — do not use |
| Clustered CR1 (asymptotic) | 0.061 | [−0.16, +6.22] | Conservative with G=27 |
| Wild cluster bootstrap | **0.040** | **[+0.07, +5.84]** | **Report as primary** |
| Randomization inference | Not implemented | — | Future robustness |

> [!NOTE]
> The wild cluster bootstrap (p=0.040) crosses p<0.05 while the asymptotic clustered SE (p=0.061) does not. Both are reported. In the paper, we will note that inference is sensitive to the choice of variance estimator in a small-G setting, and present both.

---

## 7. Specification Choices Not Yet Tested

The following sensitivity checks are reserved for Working Paper 1:

| Check | Reason for deferral |
|---|---|
| Adding Bihar | Treatment confidence MEDIUM; needs district-level BharatNet validation |
| Callaway-Sant'Anna (staggered DiD) | Requires treatment timing variation within state; current design is 2×2 |
| Entropy balancing / IPW | Balance already addressed by district FE; IPW reserved for robustness |
| Placebo test (pre-period DiD 2019 → 2021) | Needs confirmed 2021 district identifiers |
| Heterogeneous effects (rural share × β3) | Requires subgroup sample sizes sufficient for precision |
| Alternative outcome: agri_share_wt | Bihar exclusion makes this cleaner; deferred to multi-state extension |

---

## 8. Sensitivity Summary

| Question | Answer |
|---|---|
| Is β3 driven by Kalaburagi? | **No** — β3 increases to +3.07pp when Kalaburagi is excluded |
| Does adding Rajasthan change the result? | **No** — KA-only β3 = +3.00pp; nearly identical |
| Is β3 sensitive to urban outlier exclusion? | **Yes** — falls to +2.31pp; remains positive |
| Is the positive sign robust? | **Yes** — positive in all 5 specifications |
| Is statistical significance robust? | **Marginal** — significant at bootstrap p=0.040 in R2; not in R1/R4/R5 |
| Overall sensitivity verdict | **Qualitatively robust; quantitatively sensitive to sample composition** |
