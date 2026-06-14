# AIRIS Working Paper 1 — §2 Literature Review
## Phase 5A Draft | June 2026

---

## 2. Related Literature

### 2.1 AI, Automation, and Labour Markets

The macroeconomic literature on automation and employment has accelerated sharply since the publication of Frey and Osborne (2013), who estimated that 47% of US occupations were at high risk of computerisation. Subsequent work has refined this framing — from occupation-level exposure estimates (Autor, 2015; Acemoglu and Restrepo, 2018) to task-level substitution models (Brynjolfsson, Rock and Syverson, 2018) — and consistently found that the employment effects of technology depend critically on whether labour and capital are complements or substitutes in specific task bundles.

The emergence of large language models (LLMs) introduces a qualitatively different form of automation exposure. Unlike earlier generations of software, LLMs can perform non-routine cognitive tasks — drafting, reasoning, summarisation, and interaction — that were previously considered automation-resistant (Eloundou et al., 2023; Brynjolfsson, Li and Raymond, 2023). Early evidence from developed countries suggests that LLM adoption is associated with productivity gains for individual workers (Noy and Zhang, 2023; Dell'Acqua et al., 2023) but that firm-level adoption has been uneven and the macroeconomic employment effects remain contested.

For developing countries, the evidence is sparser and the mechanisms may differ. Acemoglu et al. (2022) show that automation-exposed industries in middle-income countries exhibit slower employment and wage growth, with the effect concentrated in workers without post-secondary education. Maloney and Molina (2016) argue that developing countries face a "premature deindustrialisation" risk in which automation erodes the manufacturing employment ladder before workers have completed the structural transformation process. The present paper extends this literature to AI-era services automation in rural India — a context where structural transformation is still underway and the manufacturing ladder was never the primary employment pathway.

### 2.2 Digital Infrastructure and Development

The relationship between telecommunications infrastructure and economic development is well-documented. Roller and Waverman (2001) established a positive link between telecommunications penetration and GDP growth across OECD countries. More recent work has extended this to broadband specifically: Czernich et al. (2011) find that a ten-percentage-point increase in broadband penetration raises annual per-capita growth by 0.9–1.5 percentage points in developed economies. For developing countries, Hjort and Poulsen (2019) use the arrival of submarine internet cables in Sub-Saharan Africa as an exogenous connectivity shock and show significant employment and wage gains, concentrated in the formal sector.

India-specific evidence on broadband's labour market effects is more limited. Bhuller, Havnes, Leuven and Mogstad (2013) provide a methodological template using Norwegian internet rollout as an identification strategy. For India, most existing work focuses on mobile connectivity rather than broadband (Jensen, 2007, on fishermen's market access; Aker, 2010, on agricultural markets) or on urban formal sector outcomes. The BharatNet programme — the largest rural broadband deployment in the world by geographic scope — has received relatively little rigorous econometric evaluation of its labour market effects.

### 2.3 Skill-Biased Technological Change in Developing Countries

The skill-biased technological change (SBTC) literature predicts that technology adoption is complementary to high-skilled workers and substitutive for low-skilled workers, widening the skill premium (Acemoglu and Autor, 2011). In developing countries, this framework requires modification because the occupational structure is dominated by agricultural and informal employment rather than the routine-cognitive jobs most exposed to automation in OECD contexts.

Gindling and Newhouse (2014) document that in most developing countries, self-employment and informal work dominate rural labour markets, and that these workers are difficult to reach through standard SBTC channels. Our heterogeneity analysis by literacy level is motivated by the SBTC prediction: if connectivity enables AI-era SBTC, the effects should be concentrated in districts with higher human capital stocks. The finding that high-literacy districts exhibit both unemployment and services employment increases — while low-literacy districts show agricultural exit without visible reallocation — is consistent with a literacy-mediated SBTC channel operating through connectivity.

### 2.4 BharatNet and Rural Connectivity in India

BharatNet (originally the National Optical Fibre Network) was launched in 2011 with the objective of connecting India's 250,000 gram panchayats with broadband internet at 100 Mbps. Implementation has proceeded in phases, with Phase I (2011–2017) targeting approximately 100,000 GPs and Phase II (2017–2022) targeting the remainder. Coverage has been uneven across states, with southern states (particularly Karnataka and Andhra Pradesh) achieving higher early coverage than northern and eastern states (Bihar, Uttar Pradesh).

Treatment assignment in this paper exploits the within-state timing variation in BharatNet rollout. Districts are classified as "early-connected" if their aggregate GP coverage reached 50% or above by 2019 (pre-treatment period), and "late-connected" otherwise. This classification is documented in the AIRIS Treatment Validation Report (Phase 4A) using parliamentary question-and-answer records and BBNL official data for Karnataka; Rajasthan district-level data is from state-level BharatNet progress reports. The validity of this classification is assessed in the AIRIS_Treatment_Validation_Report.md, which documents high confidence for Karnataka and medium-high confidence for Rajasthan.

### 2.5 Difference-in-Differences in Development Economics

Difference-in-differences (DiD) has become the dominant quasi-experimental design in development economics for evaluating infrastructure and technology programmes (Duflo, Glennerster and Kremer, 2008; Angrist and Pischke, 2009). Recent methodological advances — including Callaway and Sant'Anna (2021) for staggered treatment designs and Rambachan and Roth (2023) for sensitivity analysis of parallel trends violations — have raised the bar for credible DiD identification.

This paper uses a two-period 2×2 DiD (pre: 2019-20; post: 2023-24) with district and year fixed effects, which is equivalent to first-differences estimation given T=2. We do not implement staggered DiD estimators at this stage because the treatment timing is measured at district level with substantial uncertainty in the post-period rounds (2021-22 district identifiers classified as PROBABLE). Parallel trends are assessed using the intermediate 2021-22 round and documented in the AIRIS_Parallel_Trends_Report.md.

Inference uses wild cluster bootstrap (Cameron, Gelbach and Miller, 2008; MacKinnon and Webb, 2018) with Rademacher weights, B=999 replications. With G=27 clusters, asymptotic clustered standard errors may be liberal (cluster count below the rule-of-thumb threshold of 42 from MacKinnon and Webb, 2017). We report both asymptotic and bootstrap p-values.

### 2.6 This Paper's Position

This paper sits at the intersection of three literatures — AI and labour markets, digital infrastructure and development, and rural transformation in India — and makes an empirical contribution to each. Against the AI literature, it provides evidence from a developing-country rural context where the structural transformation process is ongoing and human capital is the binding constraint. Against the digital infrastructure literature, it introduces AI diffusion as an interaction channel through which connectivity's labour market effects operate. Against the rural transformation literature, it documents the early phase of AI-era disruption in a setting — rural India — where the stakes are highest and the evidence is scarcest.

---

*[Draft Note: All citations are formatted as placeholders in (Author, Year) style. Full bibliography to be compiled using verified academic sources before submission. Core references include: Frey and Osborne 2013 (Oxford); Acemoglu and Restrepo 2018 (AER); Eloundou et al. 2023 (OpenAI/arxiv); Hjort and Poulsen 2019 (AER); Callaway and Sant'Anna 2021 (JoE); Cameron, Gelbach and Miller 2008 (ReStat).]*
