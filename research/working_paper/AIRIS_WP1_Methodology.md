# AIRIS Working Paper 1 — §§3–4 Data, Context & Methodology
## Phase 5A Draft | June 2026

---

## 3. Data and Institutional Context

### 3.1 BharatNet Programme and Treatment Assignment

BharatNet is India's national rural broadband infrastructure programme, operated by the Bharat Broadband Network Limited (BBNL) under the Department of Telecommunications. Its objective is to connect all 250,000 gram panchayats (the lowest tier of rural local government) with optical fibre broadband at speeds of 100 Mbps or above. The programme was conceived as the infrastructure backbone for digital public services, e-commerce, and digital financial inclusion in rural India.

Implementation has been geographically staged, creating a natural experiment: districts in which technical and administrative conditions allowed faster fibre deployment achieved GP-level coverage years before districts where terrain, land acquisition, or administrative capacity created delays. Critically for this study, the timing variation is **within-state** — districts within Karnataka and Rajasthan reached 50% GP coverage at different points between 2014 and 2022, driven by logistical rather than selection-on-outcomes factors.

**Treatment classification:** We classify districts as "early-connected" if at least 50% of their gram panchayats had operational optical fibre connections by 2019-20 (the pre-treatment survey round), and "late-connected" otherwise. This classification is validated in the AIRIS Treatment Validation Report using parliamentary question-and-answer records (Lok Sabha starred and unstarred questions, 2018–2022) and BBNL official state reports. Confidence levels: Karnataka — high; Rajasthan — medium-high. Two Karnataka districts (Kalaburagi, Koppal) are flagged for sensitivity analysis due to treatment assignment uncertainty.

### 3.2 Periodic Labour Force Survey (PLFS)

The Periodic Labour Force Survey (PLFS) is conducted annually by India's National Sample Survey Office (NSSO) with a rotating panel design covering approximately 100,000 households per round. It replaced the earlier quinquennial Employment-Unemployment Surveys in 2017-18, providing annual district-level estimates of employment and labour force status.

**Rounds used in this paper:**
- **2019-20:** Pre-treatment baseline (pre-COVID, pre-AI diffusion)
- **2021-22:** Intermediate period (COVID-affected; used for parallel trends diagnostics, excluded from primary 2×2 DiD)
- **2023-24:** Post-treatment outcome period (post-ChatGPT launch, 2022)

**Sample restriction:** We restrict to rural persons only (PLFS PERRV file — "rural persons"). For each district-year cell, we impose a minimum sample size threshold (`n_employed ≥ 200`) classified as "Grade C or above" and exclude district-year observations with fewer employed persons from the primary DiD. This threshold ensures sufficient precision for district-level rate estimation.

**Key variables extracted from PLFS microdata:**
- `unemp_rate_wt`: Weighted unemployment rate among rural labour force participants (%)
- `agri_share_wt`: Weighted share of employed workers in agriculture (PLFS broad sector code 1: agriculture, forestry, fishing)
- `nonagri_share_wt`: Weighted non-agricultural employment share (= 100 − agri_share_wt)
- `services_share`: Weighted services sub-sector employment share (NIC-2 digit codes ≥ 45)
- `log_wage_median`: Median log real weekly wage among regular/casual wage employees

Activity status classification follows PLFS coding conventions. Employed persons are defined as those with current weekly status codes indicating work during the reference week (codes 11–51 in the 2-digit scheme used in 2019-20; codes 1–5 in the 1-digit scheme used in 2021-22 and 2023-24). Labour force participants additionally include those seeking work (codes 61–71 and 6, respectively).

### 3.3 Census 2011 Controls

District-level baseline controls are drawn from the Primary Census Abstract (PCA) of the 2011 Census of India, the most recent census with district-level socioeconomic detail available for this panel. We use:

| Variable | Description |
|---|---|
| `literacy_rate` | Population aged 7+ that is literate (%) |
| `female_literacy_rate` | Female literacy rate (%) |
| `sc_share` | Scheduled Caste population share (%) |
| `st_share` | Scheduled Tribe population share (%) |
| `urban_share` | Urban population as share of total (%) |
| `agri_worker_share` | Main agricultural workers as share of total workers (%) |
| `log_population` | Log of district population |

These variables are time-invariant by construction (measured once, in 2011) and are fully absorbed by district fixed effects in the DiD specification. They are included in robustness specifications as efficiency controls and used as conditioning variables in the heterogeneity analysis.

### 3.4 Panel Construction

The master panel (`airis_panel_master.csv`) is constructed by:

1. Extracting district-level summary statistics from each PLFS round for Karnataka, Bihar, and Rajasthan
2. Applying a standardised district name concordance (102 districts, 4 naming systems, 101/102 exact matches) to align PLFS district codes with Census 2011 codes
3. Merging PLFS outcomes with BharatNet treatment assignments and Census 2011 controls
4. Imposing quality filters (grade C+, known districts only, confirmed treatment assignments)

**Panel dimensions:**
- Total rows: 295 (101 districts × 3 survey years, minus attrition)
- States: Karnataka (30 districts), Bihar (38 districts), Rajasthan (33 districts)
- Primary DiD sample (this paper): 48 observations, 27 districts, Karnataka + Rajasthan, early + late groups, 2019 + 2023

**[TABLE 0: Pre-treatment Summary Statistics — [PLACEHOLDER: compute from master panel]]**

*[Draft note: Table 0 will be computed from airis_panel_master.csv filtered to 2019-20, early + late groups, KA+RJ. Variables: unemp_rate_wt, agri_share_wt, services_share, log_wage_median, literacy_rate, urban_share, agri_worker_share. Columns: Early mean, Early SD, Late mean, Late SD, Normalised difference.]*

---

## 4. Empirical Strategy

### 4.1 Identification Strategy

Our core identifying assumption is that **within-state timing variation in BharatNet rollout is uncorrelated with trends in labour market outcomes** in the absence of differential connectivity. More precisely, we require that in the counterfactual where both early and late districts had remained equally connected throughout the sample period, their unemployment trajectories would have followed parallel trends from 2019 to 2023.

This assumption is not trivially satisfied. BharatNet rollout timing is correlated with pre-existing district characteristics — early districts tend to be more urban, more literate, and less agricultural (documented in the AIRIS Balance Table, Phase 4A). However, district fixed effects absorb all such time-invariant differences by construction, leaving identification to rest on whether the differential change in labour market outcomes between early and late districts — after removing all time-invariant heterogeneity and common trends — is attributable to differential connectivity exposure.

The key threat to identification is **differential time-varying confounders**: factors that changed differently for early and late districts between 2019 and 2023 for reasons unrelated to BharatNet. We assess this threat through:
1. Parallel trends diagnostics using the 2021-22 intermediate round (Phase 4A: AIRIS_Parallel_Trends_Report.md)
2. Sensitivity analysis across five specifications, including urban outlier exclusion
3. The treatment effect heterogeneity patterns, which are consistent with plausible mechanisms and not with obvious confounders

### 4.2 The DiD Estimator

The primary specification is:

$$Y_{it} = \alpha_i + \lambda_t + \beta_3 \cdot (Post2023_t \times Early_i) + \varepsilon_{it}$$

where:
- $Y_{it}$ is the outcome for district $i$ in survey year $t$
- $\alpha_i$ are district fixed effects
- $\lambda_t$ are year fixed effects
- $Post2023_t = 1$ if $t = 2023\text{-}24$, $= 0$ if $t = 2019\text{-}20$
- $Early_i = 1$ if district $i$ is BharatNet early-connected, $= 0$ if late-connected
- $\beta_3$ is the DiD coefficient — the estimand of interest
- $\varepsilon_{it}$ is an idiosyncratic error term

The coefficient $\beta_3$ identifies the differential change in outcome $Y$ between 2019-20 and 2023-24 for early-connected districts relative to late-connected districts, after absorbing all time-invariant district heterogeneity (through $\alpha_i$) and common time trends (through $\lambda_t$).

**Interpretation constraint:** We interpret $\beta_3$ as the differential labour market adjustment experienced by early-connected districts during the period of AI diffusion. This is **not** an estimate of AI adoption's causal effect — we do not observe AI adoption directly. The timing of the post-period (2023-24) is chosen to coincide with the AI diffusion shock, but alternative explanations for $\beta_3 \neq 0$ cannot be ruled out on identification alone.

### 4.3 Estimation

We implement the DiD using the within (demeaned) estimator, which is algebraically equivalent to the least squares dummy variable (LSDV) estimator with district and year dummies. For T=2, this is equivalent to the first-differences estimator. The within transformation removes district means and year means:

$$\tilde{Y}_{it} = Y_{it} - \bar{Y}_i - \bar{Y}_t + \bar{Y}$$

and similarly for the interaction term $\widetilde{(Post \times Early)}_{it}$. OLS applied to the within-transformed data yields $\hat{\beta}_3$.

The panel is **unbalanced**: some districts drop from the estimation sample in 2023-24 due to falling below the Grade C+ threshold. The within estimator handles this correctly under standard assumptions; the naive group-mean 2×2 DiD (which uses simple averages) cannot. We report both estimators in Section 5 to document the composition effect.

### 4.4 Inference

Standard errors are clustered at the district level (27 clusters in the primary specification), with a small-sample correction factor of $(G/(G-1)) \times ((N-1)/(N-K))$ applied to the meat of the sandwich estimator (CR1 correction; Cameron and Miller, 2015).

With G=27 clusters, asymptotic clustered standard errors may over-reject the null hypothesis relative to the true finite-sample distribution (MacKinnon and Webb, 2017). We therefore implement wild cluster bootstrap inference (Cameron, Gelbach and Miller, 2008) with Rademacher weights ($w_g \in \{-1, +1\}$ with equal probability), B=999 bootstrap replications, and two-sided p-values computed as $\hat{p} = \hat{P}(|\hat{\beta}_3^* - \bar{\beta}_3^*| \geq |\hat{\beta}_3|)$.

**Preferred inference:** Wild cluster bootstrap. We report both asymptotic clustered and bootstrap p-values throughout.

### 4.5 Parallel Trends Assessment

The parallel trends assumption is assessed using the 2021-22 PLFS round, which falls within the pre-shock period (ChatGPT launched November 2022; the 2023-24 survey begins post-launch). We estimate a pre-period DiD using 2019-20 as baseline and 2021-22 as the test period. This test is imperfect for two reasons: (a) 2021-22 coincides with the COVID-19 pandemic, which differentially affected district labour markets in ways correlated with connectivity; and (b) the 2021-22 district identifier (`b1q4_perrv`) is classified as PROBABLE rather than confirmed.

Results from the parallel trends analysis (AIRIS_Parallel_Trends_Report.md) show:
- Pooled pre-trend DiD < ±1pp for unemployment across the three-state sample
- Within-state pre-trend divergences are moderate (KA: +2.98pp in 2019→2021, attributed to COVID differential impact)
- The primary 2×2 DiD skips the COVID period, using only 2019-20 and 2023-24

### 4.6 Sensitivity Specifications

Five sensitivity specifications are estimated to assess robustness (detailed in AIRIS_R1_Sensitivity.md):

| Specification | Sample | N | G |
|---|---|---|---|
| R1: KA only | Karnataka | 30 | 17 |
| R2: KA+RJ (main) | Karnataka + Rajasthan | 48 | 27 |
| R3: KA+RJ excl. Kalaburagi | Excluding disputed district | 46 | 26 |
| R4: KA+RJ excl. urban outliers | Excl. Jaipur, Kota, Kalaburagi, Bengaluru Urban | 41 | 23 |
| R5: KA excl. Kalaburagi | Karnataka without disputed district | 28 | 16 |

All specifications return positive $\hat{\beta}_3$ (range: +2.31 to +3.21pp). The sign and approximate magnitude are stable across all specifications.
