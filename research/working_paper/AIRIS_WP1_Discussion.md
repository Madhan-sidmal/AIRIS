# AIRIS Working Paper 1 — §6 Discussion
## Phase 5A Draft | June 2026

---

## 6. Discussion

### 6.1 What the Results Establish

Before interpretation, we restate precisely what the empirical evidence establishes and what it does not.

**Established (Tier 1 — directly observed):**
1. Early-connected rural districts in Karnataka and Rajasthan experienced 3.03 percentage points higher unemployment growth relative to late-connected districts between 2019-20 and 2023-24 (p=0.040, district+year FE, G=27)
2. In high-literacy early-connected districts, both unemployment (+4.41pp, p=0.000) and services employment (+3.42pp, p=0.000) increased relative to their high-literacy late-connected counterparts
3. The unemployment effect is concentrated in high-agriculture districts (+4.90pp, p=0.003) and absent in low-agriculture districts (−0.26pp, p=0.935)
4. In low-literacy districts, agricultural employment fell (−3.96pp, p=0.046) without measurable unemployment increase
5. These results are stable across five sensitivity specifications; the sign never reverses

**Not established (Tier 2 — inferred, not observed):**
1. That AI adoption caused these labour market changes — AI adoption at the district level is not directly measured
2. That BharatNet connectivity is the sole mechanism — connectivity is correlated with other district characteristics that we control for through FE but cannot fully isolate
3. That the unemployment increase is permanent — we observe one post-period snapshot (2023-24) and cannot determine whether the disruption is transitional or structural

This separation of evidence from interpretation is maintained throughout the discussion.

### 6.2 Two Adjustment Processes

The heterogeneity analysis reveals that the aggregate unemployment coefficient (+3.03pp) is a population-weighted average of two qualitatively different adjustment dynamics.

**Process 1 — Structural Transformation in High-Literacy Districts**

In districts above the state-median literacy rate, early connectivity is associated with simultaneous expansion in both services employment and unemployment. The joint pattern — services up, unemployment up, wages stable — is the empirical fingerprint of **structural transformation in progress**. Workers are rotating toward service-sector employment, but the transition is not instantaneous. The gap between the rate of job creation (services sector absorption) and the rate of workers leaving their previous employment generates frictional unemployment: workers who are actively searching for work in the growing services sector but have not yet been placed.

This pattern is theoretically consistent with models of sectoral reallocation under skill-biased technological change (Acemoglu and Autor, 2011) applied to a rural connectivity context. The literacy heterogeneity identifies the human capital channel: higher-literacy workers in connected districts are better positioned to access and benefit from AI-enabled service jobs, creating a demand pull that draws workers toward the services sector. The imperfect absorption generates temporary unemployment rather than a permanent displacement equilibrium.

**Process 2 — Disruption in High-Agriculture Districts**

In districts above the state-median agricultural employment share, early connectivity is associated with a sharp unemployment spike (+4.90pp, p=0.003) without visible sectoral reallocation (both agri and services employment shares are stable at 95% confidence). This pattern is consistent with **demand-side disruption** to rural non-farm employment: the types of rural non-agricultural work that were previously available — rural trade, agri-input supply, rural financial services — may have been disrupted by AI-enabled substitutes that became accessible through connectivity, without generating equivalent new employment in observable sectors.

An alternative explanation for the high-agriculture disruption pattern involves **information effects**: connectivity enables rural workers in high-agriculture districts to learn about labour market conditions (including that their informal sector wages are below alternatives), which triggers active job search (registering as unemployed) rather than passive underemployment. Under this interpretation, the unemployment spike reflects a survey response change rather than a true employment loss. We cannot distinguish these two explanations with the available data.

### 6.3 The Role of Human Capital

The literacy heterogeneity finding is the paper's central policy-relevant result. It implies that connectivity and human capital are **complementary inputs** in the labour market adjustment process: connectivity without human capital generates disruption, while connectivity with human capital enables transformation.

This complementarity has a precise interpretation in the context of AI diffusion. AI tools require literacy, digital familiarity, and the ability to direct tool outputs toward productive tasks. In districts where these capabilities are scarce, connectivity provides access to AI tools that the local workforce cannot utilise effectively as a production complement — but the connectivity itself may displace the human labour that previously performed tasks now automated by AI in connected markets. In high-literacy districts, connectivity enables direct labour-AI complementarity: workers can use AI tools to enhance their own productivity and access service-sector employment that rewards these capabilities.

This interpretation is consistent with the SBTC literature (Section 2.3) but adds a developing-country rural dimension: the skill threshold that determines whether technology is complementary or substitutive is lower in rural India than in OECD contexts (because the counterfactual is subsistence agriculture rather than routine manufacturing), but the threshold is non-zero — basic literacy is the minimum condition.

### 6.4 The Agricultural Channel

The finding that the unemployment effect is concentrated in high-agriculture districts requires explanation beyond the human capital channel. Even controlling for literacy (which is correlated with agriculture share), high-agriculture early-connected districts show sharper disruption. Two mechanisms are consistent with this:

**Agricultural-adjacent employment exposure:** The rural non-farm employment that is most abundant in agricultural districts — agri-input dealers, rural credit agents, rural traders, rural extension workers — may be precisely the employment most exposed to AI-enabled substitution. Connectivity enables platform-based or automated versions of these functions (digital credit scoring, online agri-market platforms, AI-assisted agricultural advisory services) that reduce demand for human labour in these roles.

**Reduced informal information rent:** Before connectivity, workers in agricultural districts may have enjoyed informal information rents — charging above-market prices for services or labour due to buyers' imperfect information and high search costs. Connectivity reduces these information asymmetries (consistent with Jensen's 2007 fishermen finding), potentially eroding the informal income that prevented workers from entering the measured unemployment count.

### 6.5 Connection to AIRIS Mission

The AIRIS research programme exists to answer one question: *How is AI adoption affecting the rural–urban development gap, and what interventions can reduce AI-driven exclusion?*

This paper's findings contribute to that mission in two ways:

**First,** they establish that the rural–urban digital divide mediates how AI-era disruption propagates. Districts that are better-connected — and therefore more exposed to AI-era tools — experience more labour market disruption in the short run, not less. Connectivity accelerates both the benefits and the disruption of AI diffusion; which effect dominates depends on human capital.

**Second,** they identify an intervention target: the literacy threshold that determines whether connectivity enables transformation or merely disruption. Programmes that combine infrastructure investment (BharatNet) with skills investment (adult literacy, digital literacy, vocational training) are predicted by this evidence to produce better labour market outcomes than infrastructure investment alone. This is a testable and actionable conclusion.

### 6.6 Policy Implications

**For BharatNet programme design:** The finding that connectivity effects are heterogeneous by literacy suggests that complementary skills programmes should be bundled with — or immediately follow — infrastructure rollout. Areas with below-median literacy receiving new BharatNet connections may benefit from targeted digital literacy and vocational training programmes to convert connectivity from a disruption vector into a transformation enabler.

**For rural employment policy:** The concentration of disruption in high-agriculture districts suggests that MGNREGS (the rural employment guarantee scheme) and similar rural safety net programmes may face higher demand in BharatNet-connected, agricultural-intensive districts during the AI transition period. Programme capacity planning should account for this geographic pattern.

**For AI regulation and access policy:** The findings do not support restricting connectivity as a protective measure — late-connected districts are not better off; they are merely less exposed to both the benefits and risks of AI diffusion. The policy goal should be accelerating the complementarity conditions (literacy, skills) rather than slowing the technology exposure.
