# AIRIS Working Paper 1 — §1 Introduction
## Phase 5A Draft | June 2026

---

## 1. Introduction

### 1.1 The AI Diffusion Moment

The release of ChatGPT in November 2022 and the subsequent rapid adoption of large language model (LLM) technologies through 2023 represent one of the most abrupt general-purpose technology transitions in recent economic history. Within twelve months, AI tools capable of performing routine cognitive tasks — drafting, translation, data processing, customer interaction, basic coding — became accessible to anyone with an internet connection at near-zero marginal cost. This accessibility is what distinguishes the current AI diffusion episode from earlier automation waves, which were primarily mediated through capital investment in machinery. Unlike industrial robots or enterprise software, the AI diffusion of 2022–2024 requires no firm-level capital expenditure — only connectivity and a device.

This creates a distinctive challenge for developing countries, and for rural areas within them. The infrastructure prerequisite — reliable broadband — is unevenly distributed. In India, the urban–rural digital divide remains among the widest in the world: rural internet subscriber density in 2024 is approximately one-third that of urban areas (TRAI, 2024). Districts connected to India's national optical fibre network (BharatNet) differ systematically from those not yet connected in their ability to access, utilise, and be disrupted by AI tools. What happens to rural labour markets during AI diffusion depends critically on where in the connectivity distribution a district sits.

### 1.2 The Rural–Urban Connectivity Gap

India's BharatNet programme, launched in 2011 as the National Optical Fibre Network (NOFN) and rebranded in 2016, targets the connection of all 250,000 gram panchayats (village governments) to high-speed broadband. Implementation has been uneven and geographically staged. By 2019, some districts in states such as Karnataka had achieved substantial Gram Panchayat (GP) optical fibre coverage, while others — including districts in Bihar and Rajasthan — remained in early rollout phases. This temporal variation in connectivity is the source of identification in this paper.

The rural–urban development gap that BharatNet is designed to narrow is multi-dimensional. It encompasses income levels, employment quality, education, and access to markets, government services, and economic opportunity. AI diffusion adds a new dimension to this gap: access to productivity-enhancing cognitive tools that may shift labour demand, job structures, and wage-setting. Whether connectivity narrows or widens the development gap under AI diffusion is theoretically ambiguous and empirically unresolved.

### 1.3 The Research Question

This paper asks: **Does pre-existing digital connectivity affect the speed and character of labour market adjustment when AI tools become broadly accessible?**

This is not a question about whether AI causes unemployment. It is a question about whether the availability of AI tools — conditional on connectivity — changes the labour market transition dynamics observed at the district level in rural India. Our identification strategy exploits variation in the timing of BharatNet rollout across districts within the same state, comparing labour market outcomes in early-connected districts (treated) to those in late-connected districts (control) before and after the AI diffusion period (2022–2023).

We use three rounds of the Periodic Labour Force Survey (PLFS) — 2019-20, 2021-22, and 2023-24 — matched to district-level BharatNet connectivity and Census 2011 baseline controls across Karnataka and Rajasthan. Our primary outcome is the rural weighted unemployment rate; secondary outcomes cover sectoral composition (agricultural, non-agricultural, services employment shares) and wages.

### 1.4 This Paper's Contribution

This paper makes four contributions to the literature on technology, infrastructure, and labour markets in developing countries.

**First,** we provide the first district-level, panel DiD analysis of labour market dynamics in rural India during the AI diffusion period. Prior work on AI and employment in India is largely aggregated at the national or state level (Bhandari, 2023; Kelkar, 2022) or focused on urban formal-sector employment (Rajan and Kochhar, 2023). We study rural areas, which account for 65% of India's population and are both most vulnerable to and most neglected in the AI transition literature.

**Second,** we document treatment effect heterogeneity that resolves an empirical puzzle. The aggregate DiD shows significant unemployment divergence (+3.03pp, p=0.040) with null secondary outcomes — a pattern consistent with frictional adjustment. Heterogeneity analysis by literacy and agriculture intensity reveals that the aggregate result conceals two simultaneous and qualitatively different processes: structural transformation in high-literacy districts (where both unemployment and services employment rise simultaneously) and labour market disruption in high-agriculture districts (where unemployment spikes without visible sectoral reallocation).

**Third,** we provide empirical grounding for the policy debate on complementary investments. The finding that human capital — proxied by literacy — is the key moderator of connectivity's labour market effects offers specific guidance: connectivity investment without parallel skills development is associated with disruption, not transformation.

**Fourth,** we contribute to the methodological literature on small-sample causal inference. With G=27 district clusters and N=48 observations, asymptotic clustered standard errors may be unreliable. We implement wild cluster bootstrap inference (Rademacher weights, B=999) throughout, report both asymptotic and bootstrap p-values, and demonstrate that the primary result is robust to five alternative specifications.

### 1.5 Limitations

We note three limitations at the outset. First, our sample covers two of three states analysed in the broader AIRIS research programme — Bihar is excluded from this paper due to unresolved district-level treatment assignment uncertainty. Second, BharatNet connectivity timing is not randomly assigned; early-connected districts are systematically more urban, literate, and less agricultural than late-connected districts. We address this through district fixed effects (which absorb all time-invariant differences) and document the balance formally. Third, the LFPR variable extracted from the 2019-20 PLFS round suffers from a measurement inconsistency (missing age filter) that renders DiD estimates for participation outcomes unreliable; these are presented with explicit caveats.

### 1.6 Paper Structure

The remainder of the paper proceeds as follows. Section 2 reviews the related literature. Section 3 describes the data and institutional context. Section 4 presents the empirical strategy. Section 5 reports results. Section 6 interprets the findings and discusses policy implications. Section 7 presents limitations and directions for future research. Section 8 concludes.

---

*[Draft Note: Citations flagged with (Author, Year) are placeholders pending final bibliography compilation. TRAI 2024, PLFS 2019-24, and Census 2011 are verified primary sources.]*
