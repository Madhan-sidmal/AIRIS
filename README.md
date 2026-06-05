# AIRIS: Artificial Intelligence Rural Inclusion System

![AIRIS Banner](https://img.shields.io/badge/Project-AIRIS-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Phase_3_Active-green?style=for-the-badge)
![Data](https://img.shields.io/badge/Data-PLFS_|_TRAI_|_ASER-orange?style=for-the-badge)

**AIRIS** is an empirical research platform dedicated to understanding how digital infrastructure and local capabilities influence economic opportunity during the period of AI-driven structural change across rural and urban India.

Rather than relying on synthetic scores, AIRIS leverages hard, unit-level data from the Periodic Labour Force Survey (PLFS), Telecom Regulatory Authority of India (TRAI), ASER, and Google Trends to quantify actual rural-urban inequalities and measure the heterogeneous impacts of technological diffusion.

---

## 🎯 Mission

1. **Measure AI Adoption & Diffusion:** Track digital prerequisites (internet access, smartphone ownership) and early awareness markers.
2. **Measure Structural Impact:** Quantify automation risk exposure and monitor observable shifts in employment and wages.
3. **Identify AI Exclusion Risk:** Pinpoint districts most vulnerable to being structurally bypassed by AI-driven growth.
4. **Recommend Evidence-Based Interventions:** Use quasi-experimental causal inference (Difference-in-Differences) to test whether specific interventions (like BharatNet broadband access) materially alter labour market adaptation.

---

## 🔬 Current Status: Phase 3 (Causal Analysis)

AIRIS has advanced beyond vulnerability mapping (Phase 1 & 2) and has now entered Phase 3, prioritizing formal **causal evidence** over composite indexing.

### Key Empirical Findings So Far
- **Automation Exposure:** Between 11.6% and 16.2% of the employed rural workforce in Karnataka face significant automation exposure (PLFS 2023-24).
- **The True Agricultural Baseline:** The actual rural agricultural employment share in Karnataka is 77.8% (weighted), contradicting raw count artefacts.
- **The Connectivity Gulf:** Karnataka possesses a massive 117.45 percentage point tele-density gap between urban and rural areas—significantly worse than the national average. Rural internet penetration sits at only 60.75%.
- **The AI Shock:** Google Trends analysis shows that the "ChatGPT" search index jumped from near zero to almost 50 points in a single quarter (Q1 2023) within connected populations, while remaining entirely invisible to the ~40% unconnected rural households.

---

## 📊 Core Data Architecture

AIRIS utilizes automated, reproducible pipelines to ingest and harmonize disparate Indian government datasets into a unified district-year panel.

| Dataset | Granularity | Objective | Status in AIRIS |
|---------|-------------|-----------|-----------------|
| **PLFS (2019-20, 2023-24)** | District | Measure labour market impact & exclusion risk | 2023-24 Extracted. 2019-20 pending MoSPI acquisition. |
| **TRAI QPIR (Q4 2025)** | State (LSA) | Benchmark infrastructure capacity | Fully integrated |
| **Google Trends** | State | Proxy for AI awareness and diffusion timeline | Fully integrated (2020-2025) |
| **BharatNet GP Status** | District | Treatment variable for causal inference | Compiled and coded |
| **ASER 2024** | District | Measure rural digital capability & device access | State integrated, district PDF parsing active |

---

## 🧠 Methodology: The DiD Approach

To evaluate the true impact of digital infrastructure on AI-era economic adaptation, AIRIS utilizes a **Difference-in-Differences (DiD)** design anchored around the staggered rollout of the BharatNet rural broadband initiative.

**The Design:**
*   **Common Shock:** The sudden global proliferation of generative AI tools in Q1 2023.
*   **Treatment:** District-level service readiness of high-speed optical fibre (BharatNet).
*   **Outcome Variables:** Non-agricultural employment share, rural median wages, and unemployment rates.

*Hypothesis: Districts connected to high-speed broadband prior to the AI shock demonstrated higher labour-market resilience and faster adaptation (increased non-agri employment, higher wage growth) than those connected later.*

---

## 📂 Repository Structure

```text
AIRIS/
├── analysis/               # Core analytical scripts (Risk Atlases, ROI models, Indices)
│   ├── indices/            # Explainability trackers and sensitivity analysis
│   └── causal/             # Difference-in-differences (DiD) regression models
├── dashboard/              # Streamlit web application for interactive data visualization
├── data/                   # Data storage layer
│   ├── raw/                # Unaltered source files (PDFs, ZIPs, CSVs)
│   ├── clean/              # Harmonized, cleaned data formats (Parquet, CSV)
│   └── features/           # Derived features ready for causal modeling
├── database/               # Relational crosswalks (e.g., standardizing district codes)
│   └── seeds/              # Base mapping CSVs
├── pipelines/              # Automated ETL pipelines
│   ├── extractors/         # Scraping and parsing scripts (PLFS, TRAI, ASER)
│   └── transformers/       # Panel builders and standardizers
├── docker-compose.yml      # Infrastructure setup (PostgreSQL, MinIO, Airflow)
└── requirements.txt        # Python dependency manifest
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL (if running the full index database)
- Optional: Docker & Docker Compose for isolated execution

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Madhan-sidmal/AIRIS.git
   cd AIRIS
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the `.env` file (see `.env.template` for required variables).

### Running the Pipelines
Extract and standardize the latest PLFS panel:
```bash
python pipelines/transformers/plfs_panel_builder.py --year 2023 --state_code 29
```

Run the Google Trends awareness proxy extractor:
```bash
python pipelines/extractors/google_trends_ai.py
```

---

## 📜 Causal Design Documentation
For an in-depth look at our formal pre-analysis plan, including identification strategies, outcome variable definitions, and power analysis, please refer to the `AIRIS_Causal_Design_Report.md` (located in the project tracking artifacts).

## 🤝 Contributing
AIRIS adheres strictly to a three-tier claims hierarchy:
1. **Tier 1:** Observed evidence (statistically significant, directly measured).
2. **Tier 2:** Inferred mechanism (consistent with evidence, clearly labeled).
3. **Tier 3:** Unsupported claims (strictly prohibited).

When contributing, ensure all data transformations retain complete, auditable provenance.

---
*Built to ensure the next wave of technological advancement includes those historically left behind.*
