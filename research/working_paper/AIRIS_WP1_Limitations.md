# AIRIS Working Paper 1 — §7 Limitations & Future Work
## Phase 5A Draft | June 2026

---

## 7. Limitations and Future Work

We organise the limitations of this study into four categories: sample scope, identification assumptions, measurement, and estimation power.

### 7.1 Sample Scope

**Geographic coverage.** This paper covers Karnataka and Rajasthan only. The broader AIRIS research programme includes Bihar, which has 38 districts in the three-state panel. Bihar is excluded from this paper because district-level BharatNet treatment assignments for Bihar are classified at medium confidence only — based on state-level parliamentary sources rather than district-level BBNL data. Including Bihar with potentially misclassified treatment assignments would introduce classical measurement error into the treatment indicator, biasing β3 toward zero. Bihar is slated for inclusion in a working paper extension (Phase 5B) following district-level treatment validation.

The exclusion of Bihar is consequential: Bihar has lower literacy rates and higher agricultural employment shares than Karnataka or Rajasthan, and therefore represents the district type where the disruption mechanism (rather than transformation mechanism) is most likely to operate. The heterogeneity estimates for high-agriculture, low-literacy districts would be substantially sharpened by Bihar's inclusion.

**Sample size.** With N=48 observations and G=27 clusters, this paper is underpowered to detect effects smaller than approximately 3 percentage points in the primary outcome, and substantially underpowered for secondary outcomes where true effects may be in the 1–2pp range. The heterogeneity subgroup estimates (G=10–17) are particularly imprecise. Bihar's inclusion would increase G to approximately 60 and N to approximately 90, raising power substantially.

**Time coverage.** We use two periods (2019-20 and 2023-24). The intermediate 2021-22 round is used for parallel trends diagnostics but excluded from the primary 2×2 DiD because it falls within the COVID-19 disruption period and because the 2021-22 district identifier is classified as PROBABLE rather than confirmed. Future analysis should revisit 2021-22 when district identifier confirmation is available.

### 7.2 Identification Assumptions

**Parallel trends.** The parallel trends assumption requires that early- and late-connected districts would have followed parallel labour market trajectories in the absence of differential connectivity. We provide supporting evidence through the 2019→2021 pre-trend analysis, which shows pooled pre-trend DiD below 1pp for the primary outcome. However, the COVID-19 period (2020-22) differentially affected districts by connectivity and sector structure in ways that cannot be fully controlled. Our assessment is that the 2019-24 window brackets the COVID period and that the dominant source of variation in 2023-24 outcomes is post-COVID recovery combined with AI diffusion, not the COVID disruption itself.

**Exclusion of time-varying confounders.** The district + year FE specification absorbs all time-invariant district heterogeneity and common annual shocks. It does not control for time-varying, district-specific shocks occurring between 2019 and 2023. Relevant potential confounders include: state-specific policy changes (Karnataka state elections 2023, Rajasthan state elections 2023), differential MGNREGS expenditure growth, district-level drought or flood events, and other infrastructure investments correlated with BharatNet timing. We cannot rule out these confounders empirically without additional data sources (rainfall anomalies, MGNREGS district expenditure — neither currently in the AIRIS dataset).

**Non-random treatment.** BharatNet rollout timing is not random. Early districts are more urban, literate, and less agricultural — a structural selection pattern documented formally in the AIRIS Balance Table. District fixed effects absorb this selection on time-invariant characteristics. However, if early-connected districts were also on steeper pre-trend trajectories for unobservable reasons related to the same administrative capacity that enabled faster BharatNet deployment, the FE design does not eliminate this confound. The monotonic event study pattern (0 → +1.56pp → +2.38pp) does not show the pre-trend divergence pattern that would signal this problem, but the 2021-22 estimate carries the COVID caveat described above.

**Treatment spillovers.** If BharatNet connectivity in early districts affects economic activity in neighbouring late districts (through market integration, migration, or information diffusion), the SUTVA assumption underlying the DiD estimate is violated. We do not address spatial spillovers in this paper. Future work using spatial econometric methods (Conley spatial standard errors, spatial lag models) would strengthen the identification claim.

### 7.3 Measurement

**LFPR and WPR.** The 2019-20 PLFS PERRV file did not contain a recognisable age column in our extraction pipeline, resulting in LFPR and WPR estimates for 2019-20 being computed over all persons rather than working-age (15+) individuals. DiD estimates for these participation outcomes are unreliable and presented with explicit caveats only. This issue will be resolved in a future extraction pass with the correct 2019-20 age column alias identified.

**Education.** The `edu_secondary_wt` variable — share of employed persons with secondary education — is 100% missing from the panel. This variable was not successfully extracted from the PLFS microdata. Consequently, we cannot use education as a time-varying control and rely on Census 2011 literacy rate (time-invariant) as the human capital proxy. The heterogeneity analysis by literacy uses the time-invariant Census measure, which may not capture changes in educational attainment between 2011 and 2023.

**AI diffusion measurement.** This paper uses the period indicator (Post2023_t) as a proxy for AI diffusion exposure. This is a coarse measure: it treats all post-2022 district-years as equally exposed to AI diffusion, when in reality the intensity of AI tool adoption may vary by connectivity quality (beyond the binary early/late classification), device penetration, and digital literacy. A more precise measure — such as Google Trends data for AI-related search terms at district level — would sharpen the identification but is not currently incorporated.

**Kalaburagi district.** The treatment classification of Kalaburagi (Karnataka, coded "late") is uncertain — some sources suggest earlier K-FON (Karnataka Fiber Net) rollout. This district is flagged in the sensitivity analysis; excluding it marginally increases β3 from +3.033 to +3.073, confirming that the result does not depend on Kalaburagi's classification.

### 7.4 Inference

**Small cluster count.** With G=27 in the main specification and G=10–17 in subgroups, even wild cluster bootstrap inference may not fully resolve finite-sample distortions. Randomisation inference (permutation tests) would provide additional robustness for the smallest subgroups (G=10, Rajasthan). This is a methodological improvement reserved for the revised paper.

**Multiple comparisons.** The heterogeneity analysis estimates DiD for 4 outcomes across 6 subgroups = 24 tests. We do not apply multiple comparison corrections (Bonferroni, Benjamini-Hochberg) to the heterogeneity results. The two strongest findings — high-literacy unemployment p=0.000 and services p=0.000 — would survive any reasonable correction. The agriculture heterogeneity (p=0.003 vs p=0.935 contrast) is a comparison of estimates rather than a formal interaction test; a formal Wald test for the interaction between treatment and agriculture quartile is not yet computed.

### 7.5 Future Extensions

| Extension | Value | Feasibility |
|---|---|---|
| Bihar integration | Sharpens heterogeneity, raises G to ~60 | Pending treatment validation |
| LFPR age column fix | Adds reliable participation outcome | One extraction session |
| Callaway-Sant'Anna staggered DiD | Handles treatment timing heterogeneity correctly | Pending 3-state confirmed timing |
| Spatial spillover analysis | Tests SUTVA validity | Requires spatial weights matrix |
| Time-varying controls | MGNREGS, rainfall anomaly | Requires additional data pipeline |
| Google Trends AI exposure index | Sharpens treatment proxy | Partially available (Karnataka) |
| 2025-26 PLFS (when available) | Adds second post-period for event study | Availability ~2027 |
