"""
AIRIS — AI Equity Index Calculator
=====================================
Core computation engine for AIRIS.

Combines TRAI broadband data + PLFS employment data to produce
the composite AI Equity Index for each district — the headline
metric that answers the research question:

  "How much is AI widening the rural-urban development gap, 
   and for which districts is the effect worst?"

Output per district (scored 0–100, higher = more AI-excluded):
  - Infrastructure Gap Index
  - Adoption Gap Index  
  - AI Displacement Risk Index
  - Net AI Impact Score
  - National and State rank
  - Classification: Severely Excluded / Excluded / Transitional / Included
"""

import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger
from typing import Tuple


# ── Benchmarks (from your research notes) ────────────────────────────────────
BENCHMARKS = {
    # Infrastructure
    "urban_broadband_penetration": 93.0,      # TRAI 2024 (Note 1)
    "rural_broadband_penetration": 29.3,      # TRAI 2024 (Note 1)
    "urban_fiber_penetration":     15.3,      # TRAI 2024 (Note 1)
    "rural_fiber_penetration":      3.8,      # TRAI 2024 (Note 1)

    # AI Adoption (US proxy — India-specific data unavailable)
    "urban_ai_adoption_rate":      32.9,      # Census/Pew (Note 2)
    "rural_ai_adoption_rate":      16.2,      # Census/Pew (Note 2)

    # Job exposure (OECD 2024)
    "urban_ai_job_exposure":       32.0,      # OECD 2024 (Note 1)
    "rural_ai_job_exposure":       21.0,      # OECD 2024 (Note 1)
    "max_regional_exposure":       45.0,      # Stockholm, Prague (Note 1)
    "min_regional_exposure":       13.0,      # Cauca, Colombia (Note 1)

    # Income
    "urban_rural_income_ratio":     2.46,     # China 2024 (Note 2)
}


class AIEquityIndexCalculator:
    """
    Computes AIRIS's composite AI Equity Index.

    The index is designed to be:
    - Interpretable: 0 = perfect AI equity, 100 = completely AI-excluded
    - Decomposable: each sub-index can be analyzed independently
    - Comparable: districts ranked nationally and by state
    - Time-varying: recomputed quarterly as new data arrives
    """

    CLEAN_DIR = Path("data/clean")
    FEAT_DIR  = Path("data/features")

    def __init__(self):
        self.FEAT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load cleaned data ─────────────────────────────────────────────────────

    def load_data(self, quarter: str = "Q3", year: int = 2024) -> Tuple[pd.DataFrame, pd.DataFrame]:
        trai_path = self.CLEAN_DIR / f"trai_broadband_{quarter}_{year}.parquet"
        plfs_path = self.CLEAN_DIR / f"plfs_district_{year}.parquet"

        if not trai_path.exists() or not plfs_path.exists():
            logger.warning("Clean data not found. Run trai_extractor.py and plfs_parser.py first.")
            raise FileNotFoundError("Run pipeline extractors first.")

        df_trai = pd.read_parquet(trai_path)
        df_plfs = pd.read_parquet(plfs_path)
        logger.info(f"Loaded TRAI ({len(df_trai)} rows) and PLFS ({len(df_plfs)} rows)")
        return df_trai, df_plfs

    # ── Sub-Index 1: Infrastructure Gap ──────────────────────────────────────

    def compute_infrastructure_gap_index(self, df_trai: pd.DataFrame) -> pd.DataFrame:
        """
        Measures how far a district's connectivity lags behind India's urban benchmark.
        
        Score = weighted combination of:
          - Rural broadband gap vs national urban average (weight: 40%)
          - Fiber penetration gap (weight: 25%)
          - Speed gap (weight: 20%)
          - Urban-rural gap within the district itself (weight: 15%)
        """
        B = BENCHMARKS
        df = df_trai.copy()

        # Component 1: Rural broadband vs national urban benchmark
        rural_bb_gap = (B["urban_broadband_penetration"] - df["rural_penetration_pct"]).clip(0, 100)
        # Component 2: Fiber penetration gap
        fiber_gap    = (B["urban_fiber_penetration"] - df["fiber_penetration_pct"]).clip(0, 20)
        fiber_norm   = fiber_gap / 20 * 100
        # Component 3: Speed gap (normalized to 100 Mbps max)
        speed_gap    = (50 - df["avg_speed_mbps"].clip(0, 50)) / 50 * 100
        # Component 4: Within-district urban-rural gap
        internal_gap = df["broadband_gap_pp"].clip(0, 100)

        df["infrastructure_gap_index"] = (
            0.40 * rural_bb_gap +
            0.25 * fiber_norm   +
            0.20 * speed_gap    +
            0.15 * internal_gap
        ).clip(0, 100).round(2)

        return df[["district_code", "district_name", "state_name", "district_class",
                   "rural_penetration_pct", "urban_penetration_pct",
                   "fiber_penetration_pct", "avg_speed_mbps",
                   "broadband_gap_pp", "infrastructure_gap_index"]]

    # ── Sub-Index 2: AI Adoption Gap ─────────────────────────────────────────

    def compute_adoption_gap_index(self, df_trai: pd.DataFrame) -> pd.DataFrame:
        """
        Estimates AI adoption gap using broadband as the primary proxy.
        
        Rationale: The US data shows urban 32.9% vs rural 16.2% AI adoption
        (Note 2). Broadband penetration is the strongest predictor of AI 
        adoption (R² ≈ 0.74 across OECD studies). We use it to impute
        Indian district-level AI adoption.
        """
        B = BENCHMARKS
        df = df_trai.copy()

        # Estimate AI adoption from broadband (linear interpolation)
        # At 0% broadband → ~0% AI adoption
        # At 93% broadband (urban) → 32.9% AI adoption
        ADOPTION_SCALE = B["urban_ai_adoption_rate"] / B["urban_broadband_penetration"]
        df["est_rural_ai_adoption"] = (df["rural_penetration_pct"] * ADOPTION_SCALE).clip(0, 100)
        df["est_urban_ai_adoption"] = (df["urban_penetration_pct"] * ADOPTION_SCALE).clip(0, 100)

        # Gap vs national urban benchmark adoption
        adoption_gap = B["urban_ai_adoption_rate"] - df["est_rural_ai_adoption"]
        df["adoption_gap_index"] = (adoption_gap / B["urban_ai_adoption_rate"] * 100).clip(0, 100).round(2)

        return df[["district_code", "est_rural_ai_adoption",
                   "est_urban_ai_adoption", "adoption_gap_index"]]

    # ── Sub-Index 3: Job Market AI Impact ────────────────────────────────────

    def compute_job_impact_index(self, df_plfs: pd.DataFrame) -> pd.DataFrame:
        """
        Combines:
          - AI displacement risk (how many workers face automation)
          - Upskilling deficit (gap in AI-augmented job creation for rural vs urban)
          - Net employment vulnerability score
        """
        B = BENCHMARKS

        # Use all districts (both urban and rural) — risk is high everywhere, 
        # but replacement rate differs (urban workers get upskilled, rural get displaced)
        df_all = df_plfs.copy()

        # AI job exposure gap (OECD 2024): urban 32% vs rural 21%
        exposure_gap = B["urban_ai_job_exposure"] - B["rural_ai_job_exposure"]  # 11pp
        exposure_norm = exposure_gap / B["urban_ai_job_exposure"] * 100  # ~34

        # Net displacement risk already computed by PLFSParser
        # For urban districts, upskilling deficit is lower (AI augments, not just displaces)
        result = df_all.drop_duplicates(subset=["district_code"])[
            ["district_code", "net_displacement_risk", "sector"]
        ].copy()

        result["upskilling_deficit"] = result["sector"].apply(
            lambda s: exposure_norm * 0.4 if s in ["urban", "1"] else exposure_norm
        )
        result["job_impact_index"] = (
            0.65 * result["net_displacement_risk"] +
            0.35 * result["upskilling_deficit"]
        ).clip(0, 100).round(2)

        return result[["district_code", "net_displacement_risk",
                        "upskilling_deficit", "job_impact_index"]]

    # ── Composite Index ───────────────────────────────────────────────────────

    def compute_composite_index(self,
                                 df_infra: pd.DataFrame,
                                 df_adoption: pd.DataFrame,
                                 df_jobs: pd.DataFrame) -> pd.DataFrame:
        """
        Combines all sub-indices into a single AI Equity Index.

        Weights reflect relative importance based on literature:
          Infrastructure: 35% — foundational, everything else depends on it
          Adoption Gap:   30% — directly measures AI exclusion
          Job Impact:     35% — economic consequence (income, employment)

        Score interpretation:
          0–25:  Low exclusion — district benefits from AI
          25–50: Moderate exclusion — transitional zone
          50–75: High exclusion — at risk
          75–100: Severe exclusion — net harmed by AI
        """
        df = (df_infra
              .merge(df_adoption, on="district_code", how="left")
              .merge(df_jobs,     on="district_code", how="left"))

        df["ai_equity_index"] = (
            0.35 * df["infrastructure_gap_index"] +
            0.30 * df["adoption_gap_index"]        +
            0.35 * df["job_impact_index"]
        ).clip(0, 100).round(2)

        # Net AI Impact: positive = gaining from AI, negative = losing
        df["net_ai_impact_score"] = (50 - df["ai_equity_index"]).round(2)

        # Classification
        df["ai_equity_class"] = pd.cut(
            df["ai_equity_index"],
            bins=[0, 25, 50, 75, 100],
            labels=["Included", "Transitional", "Excluded", "Severely Excluded"],
            include_lowest=True
        )

        # National rank (1 = most excluded)
        df["national_rank"] = df["ai_equity_index"].rank(ascending=False, na_option="bottom").fillna(0).astype(int)
        df["state_rank"]    = df.groupby("state_name")["ai_equity_index"].rank(ascending=False, na_option="bottom").fillna(0).astype(int)

        return df

    # ── GDP Loss Estimate ─────────────────────────────────────────────────────

    def estimate_gdp_loss(self, df: pd.DataFrame) -> dict:
        """
        Estimates annual GDP loss from AI exclusion.

        Method: IMF (2024) estimates AI adoption boosts TFP by 1.5%/year
        for adopters. Districts with high AI equity index miss this gain.
        Counterfactual: what if excluded districts had urban-level AI adoption?

        Conservative estimate using MOSPI district GDP proxies.
        """
        # Placeholder district GDPs (₹ crore) — will use MOSPI data in full version
        DISTRICT_GDP_PROXY = {
            "BR002": 8500,   "JH002": 12000, "UP002": 9800,
            "OR002": 7200,   "BR001": 45000, "JH001": 38000,
            "UP001": 85000,  "OR001": 52000, "KA001": 320000,
            "MH001": 890000,
        }
        AI_TFP_BOOST = 0.015  # 1.5% annual TFP boost from AI adoption (IMF 2024)

        excluded = df[df["ai_equity_index"] > 50].copy()
        excluded["est_district_gdp_cr"] = excluded["district_code"].map(DISTRICT_GDP_PROXY).fillna(15000)

        # Counterfactual adoption gap: how much more AI adoption would they have at urban level?
        excluded["adoption_gap_fraction"] = (excluded["adoption_gap_index"] / 100)
        excluded["annual_gdp_loss_cr"]    = (
            excluded["est_district_gdp_cr"] *
            AI_TFP_BOOST *
            excluded["adoption_gap_fraction"]
        )

        total_loss = excluded["annual_gdp_loss_cr"].sum()
        return {
            "excluded_districts":        len(excluded),
            "total_annual_gdp_loss_cr":  round(total_loss, 0),
            "total_annual_gdp_loss_usd_bn": round(total_loss * 0.012, 2),
            "worst_affected_districts":  excluded.nlargest(5, "annual_gdp_loss_cr")[
                ["district_name", "state_name", "ai_equity_index", "annual_gdp_loss_cr"]
            ].to_dict("records"),
        }

    # ── Full Pipeline ─────────────────────────────────────────────────────────

    def run(self, quarter: str = "Q3", year: int = 2024) -> pd.DataFrame:
        logger.info("Computing AI Equity Index for all pilot districts...")

        df_trai, df_plfs = self.load_data(quarter, year)

        df_infra    = self.compute_infrastructure_gap_index(df_trai)
        df_adoption = self.compute_adoption_gap_index(df_trai)
        df_jobs     = self.compute_job_impact_index(df_plfs)
        df_composite = self.compute_composite_index(df_infra, df_adoption, df_jobs)

        gdp_loss = self.estimate_gdp_loss(df_composite)

        # Save
        out_path = self.FEAT_DIR / f"ai_equity_index_{quarter}_{year}.parquet"
        df_composite.to_parquet(out_path, index=False)
        logger.success(f"AI Equity Index saved → {out_path}")

        return df_composite, gdp_loss


# ── Run as script ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    calc = AIEquityIndexCalculator()
    df, gdp = calc.run(quarter="Q3", year=2024)

    print("\n" + "="*70)
    print("AIRIS — AI Equity Index Results")
    print("="*70)
    print(f"\nRanking (most AI-excluded first):\n")
    cols = ["national_rank", "district_name", "state_name", "district_class",
            "infrastructure_gap_index", "adoption_gap_index",
            "job_impact_index", "ai_equity_index", "ai_equity_class"]
    print(df.sort_values("national_rank")[cols].to_string(index=False))

    print(f"\n{'─'*70}")
    print(f"GDP LOSS ESTIMATE FROM AI EXCLUSION")
    print(f"{'─'*70}")
    print(f"Excluded districts (score > 50): {gdp['excluded_districts']}")
    print(f"Annual GDP loss (pilot sample):  ₹{gdp['total_annual_gdp_loss_cr']:,.0f} crore")
    print(f"                                 ${gdp['total_annual_gdp_loss_usd_bn']:.2f} billion USD")
    print(f"\nWorst affected districts:")
    for d in gdp["worst_affected_districts"]:
        print(f"  ● {d['district_name']} ({d['state_name']}): "
              f"AI Equity Index {d['ai_equity_index']:.1f} | "
              f"₹{d['annual_gdp_loss_cr']:,.0f} Cr/year loss")

    print(f"\n{'─'*70}")
    print(f"CLASSIFICATION SUMMARY")
    print(f"{'─'*70}")
    class_counts = df["ai_equity_class"].value_counts()
    for cls, cnt in class_counts.items():
        pct = cnt / len(df) * 100
        print(f"  {cls:<22}: {cnt} districts ({pct:.0f}%)")
    print("="*70)
