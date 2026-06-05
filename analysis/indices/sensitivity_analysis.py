"""
AIRIS — Sensitivity Analysis
==============================
Tests whether the AI Equity Index rankings are stable when
index weights and benchmark assumptions are varied.

A publishable index must be robust: rankings should not
completely invert when reasonable alternative weights are used.

Outputs:
  - Spearman rank correlation across all weight scenarios
  - Maximum rank change per district across scenarios
  - Stability classification per district
  - Recommended weight range where rankings are stable
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
from itertools import product
from loguru import logger


class SensitivityAnalyzer:
    """
    Tests AIRIS index stability under:
    1. Weight perturbation — vary sub-index weights
    2. Benchmark perturbation — vary urban benchmark values
    3. Scenario extremes — test the 'corner cases'
    """

    FEAT_DIR = Path("data/features")

    # ── Weight scenarios ──────────────────────────────────────────────────────
    # Each scenario is (infrastructure_weight, adoption_weight, job_weight)
    # Must sum to 1.0
    WEIGHT_SCENARIOS = {
        "Baseline (equal-ish, literature-derived)":
            (0.35, 0.30, 0.35),

        "Infrastructure-heavy (OECD digital divide framework)":
            (0.50, 0.25, 0.25),

        "Jobs-heavy (labour economics emphasis)":
            (0.25, 0.25, 0.50),

        "Adoption-heavy (AI policy emphasis)":
            (0.20, 0.50, 0.30),

        "Equal weights (naive baseline)":
            (0.333, 0.333, 0.334),

        "Infrastructure-light (critics: broadband not AI-specific)":
            (0.20, 0.40, 0.40),

        "World Bank digital inclusion weights":
            (0.45, 0.30, 0.25),
    }

    # ── Benchmark scenarios ───────────────────────────────────────────────────
    # Tests sensitivity to the urban benchmark assumption
    BENCHMARK_SCENARIOS = {
        "Baseline (TRAI Q3 2024: 93%)":       93.0,
        "Conservative (TRAI Q4 2023: 90%)":   90.0,
        "Aspirational (target: 98%)":          98.0,
        "Global urban avg (ITU 2025: 85%)":    85.0,
    }

    def load_index_data(self, quarter: str = "Q3", year: int = 2024) -> pd.DataFrame:
        path = self.FEAT_DIR / f"ai_equity_index_{quarter}_{year}.parquet"
        if not path.exists():
            raise FileNotFoundError(f"Run run_pipeline.py first to generate index data.")
        return pd.read_parquet(path)

    # ── Weight sensitivity ────────────────────────────────────────────────────

    def run_weight_sensitivity(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recomputes the composite index under each weight scenario.
        Returns a DataFrame with ranks under each scenario.
        """
        required = ["district_code", "district_name",
                    "infrastructure_gap_index", "adoption_gap_index", "job_impact_index"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        results = df[["district_code", "district_name", "state_name",
                       "infrastructure_gap_index", "adoption_gap_index",
                       "job_impact_index"]].copy()

        for scenario_name, (w_infra, w_adopt, w_job) in self.WEIGHT_SCENARIOS.items():
            score_col = f"score_{scenario_name[:20].replace(' ', '_')}"
            rank_col  = f"rank_{scenario_name[:20].replace(' ', '_')}"

            results[score_col] = (
                w_infra * df["infrastructure_gap_index"].fillna(df["infrastructure_gap_index"].mean()) +
                w_adopt * df["adoption_gap_index"].fillna(df["adoption_gap_index"].mean()) +
                w_job   * df["job_impact_index"].fillna(df["job_impact_index"].mean())
            ).clip(0, 100).round(2)

            results[rank_col] = results[score_col].rank(ascending=False).astype(int)

        return results

    def compute_rank_stability(self, sensitivity_df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes stability metrics across all weight scenarios:
        - Spearman correlation between baseline and each scenario
        - Max rank change per district
        - Stability label
        """
        rank_cols = [c for c in sensitivity_df.columns if c.startswith("rank_")]
        baseline_col = rank_cols[0]

        stability = sensitivity_df[["district_code", "district_name", "state_name"]].copy()

        # Max rank change across all scenarios
        ranks = sensitivity_df[rank_cols]
        stability["min_rank"]        = ranks.min(axis=1)
        stability["max_rank"]        = ranks.max(axis=1)
        stability["rank_range"]      = ranks.max(axis=1) - ranks.min(axis=1)
        stability["baseline_rank"]   = sensitivity_df[baseline_col]

        # Average Spearman correlation with baseline across scenarios
        corrs = []
        for col in rank_cols[1:]:
            rho, _ = stats.spearmanr(
                sensitivity_df[baseline_col],
                sensitivity_df[col]
            )
            corrs.append(rho)
        stability["avg_spearman_with_baseline"] = np.mean(corrs)

        # Overall index stability (across all pairs)
        all_corrs = []
        for i, col1 in enumerate(rank_cols):
            for col2 in rank_cols[i+1:]:
                rho, _ = stats.spearmanr(
                    sensitivity_df[col1], sensitivity_df[col2]
                )
                all_corrs.append(rho)
        overall_stability = np.mean(all_corrs)

        # District-level stability label
        n = len(sensitivity_df)
        stability["stability_class"] = stability["rank_range"].apply(
            lambda r: "Stable"         if r <= max(1, n * 0.15) else
                      "Mostly Stable"  if r <= max(2, n * 0.30) else
                      "Sensitive"      if r <= max(3, n * 0.50) else
                      "Unstable"
        )

        # Publishability flag: unstable districts need method note in paper
        stability["publishable_as_ranked"] = stability["stability_class"].isin(
            ["Stable", "Mostly Stable"]
        )

        return stability, overall_stability, corrs

    # ── Benchmark sensitivity ─────────────────────────────────────────────────

    def run_benchmark_sensitivity(self, df_trai: pd.DataFrame) -> pd.DataFrame:
        """
        Tests how sensitive infrastructure gap scores are to
        the choice of urban benchmark (93% vs alternatives).
        """
        results = df_trai[["district_code", "district_name",
                            "rural_penetration_pct"]].copy()

        for scenario_name, benchmark in self.BENCHMARK_SCENARIOS.items():
            col = f"infra_gap_{scenario_name[:20].replace(' ','_')}"
            results[col] = (
                (benchmark - df_trai["rural_penetration_pct"]) / benchmark * 100
            ).clip(0, 100).round(2)

        return results

    # ── Monte Carlo Rank Stability ────────────────────────────────────────────

    def run_monte_carlo_stability(self, df: pd.DataFrame,
                                   n_simulations: int = 1000,
                                   perturbation: float = 0.20) -> pd.DataFrame:
        """
        Addresses the rho=1.000 concern: are rankings genuinely stable,
        or is it a synthetic data artefact?

        Method:
          For each simulation:
            1. Add random noise N(0, perturbation * value) to each sub-index
            2. Recompute composite index with baseline weights
            3. Record the rank of each district

          Output:
            - Mean rank per district (should match baseline)
            - Rank std dev (low = stable, high = sensitive)
            - 95th percentile rank range per district

        Interpretation:
          Std dev < 1.0 : Stable — publishable as ranked
          Std dev 1–2   : Mostly stable — note uncertainty in paper
          Std dev > 2   : Sensitive — do not present point ranks
        """
        required = ["district_name", "infrastructure_gap_index",
                    "adoption_gap_index", "job_impact_index"]
        for col in required:
            if col not in df.columns:
                logger.warning(f"Missing column for Monte Carlo: {col}")
                return pd.DataFrame()

        # Baseline weights
        W_INFRA, W_ADOPT, W_JOB = 0.35, 0.30, 0.35

        rank_matrix = np.zeros((len(df), n_simulations))
        np.random.seed(42)

        for sim in range(n_simulations):
            # Add multiplicative noise to each sub-index
            noise = lambda col: df[col].fillna(df[col].mean()) * (
                1 + np.random.uniform(-perturbation, perturbation, size=len(df))
            )
            infra_n = noise("infrastructure_gap_index").clip(0, 100)
            adopt_n = noise("adoption_gap_index").clip(0, 100)
            job_n   = noise("job_impact_index").clip(0, 100)

            score = (W_INFRA * infra_n + W_ADOPT * adopt_n + W_JOB * job_n).clip(0, 100)
            rank_matrix[:, sim] = score.rank(ascending=False).values

        # Summary statistics
        result = df[["district_name", "state_name"]].copy()
        result["baseline_rank"]  = df["ai_equity_index"].rank(ascending=False).astype(int)
        result["mc_mean_rank"]   = rank_matrix.mean(axis=1).round(1)
        result["mc_rank_std"]    = rank_matrix.std(axis=1).round(2)
        result["mc_rank_p05"]    = np.percentile(rank_matrix, 5,  axis=1).astype(int)
        result["mc_rank_p95"]    = np.percentile(rank_matrix, 95, axis=1).astype(int)
        result["mc_rank_range"]  = result["mc_rank_p95"] - result["mc_rank_p05"]

        result["mc_stability"] = result["mc_rank_std"].apply(
            lambda s: "Stable"       if s < 1.0 else
                      "Mostly Stable" if s < 2.0 else
                      "Sensitive"
        )

        # Diagnose whether rho=1.000 was an artefact
        mean_std = result["mc_rank_std"].mean()
        if mean_std < 0.5:
            diagnosis = (
                "ARTEFACT CONFIRMED: Near-zero rank std dev indicates synthetic data "
                "monotonic ordering. Rankings will show real variance with actual TRAI/PLFS data."
            )
        elif mean_std < 1.5:
            diagnosis = (
                "GENUINE STABILITY: Rankings are stable even under random perturbation. "
                "rho=1.000 reflects real separation between district categories."
            )
        else:
            diagnosis = (
                "PARTIAL STABILITY: Some districts are weight-sensitive. "
                "Report rank ranges, not point estimates, for 'Sensitive' districts."
            )
        result["mc_diagnosis"] = diagnosis

        return result

    # ── GDP Loss Sensitivity ──────────────────────────────────────────────────

    def run_gdp_sensitivity(self, df_index: pd.DataFrame) -> dict:
        """
        Tests GDP loss estimate under different assumptions.
        Shows which assumption drives the estimate most.
        """
        # District GDP proxies (in ₹ crore)
        DISTRICT_GDP = {
            "BR002": 8500, "JH002": 12000, "UP002": 9800, "OR002": 7200,
            "BR001": 45000, "JH001": 38000, "UP001": 85000, "OR001": 52000,
            "KA001": 320000, "MH001": 890000,
        }

        excluded = df_index[df_index["ai_equity_index"] > 50].copy()
        excluded["district_gdp_cr"] = excluded["district_code"].map(DISTRICT_GDP).fillna(15000)

        scenarios = {
            "Conservative (IMF lower: 0.8% TFP boost)":    0.008,
            "Baseline (IMF central: 1.5% TFP boost)":      0.015,
            "Optimistic (IMF upper: 2.5% TFP boost)":      0.025,
            "Literature high (NBER 2024: 4% TFP boost)":   0.040,
        }

        results = {}
        for name, tfp_rate in scenarios.items():
            excluded["adoption_gap_fraction"] = excluded["adoption_gap_index"] / 100
            loss = (excluded["district_gdp_cr"] * tfp_rate * excluded["adoption_gap_fraction"]).sum()
            results[name] = {
                "tfp_assumption":       f"{tfp_rate*100:.1f}%",
                "annual_loss_cr":       round(loss, 0),
                "annual_loss_usd_bn":   round(loss * 0.012, 2),
                "label":               "EXPLORATORY ESTIMATE"
            }

        return results

    # ── Full Report ───────────────────────────────────────────────────────────

    def run(self, quarter: str = "Q3", year: int = 2024):
        logger.info("Running sensitivity analysis...")
        df = self.load_index_data(quarter, year)

        # Weight sensitivity
        sens_df = self.run_weight_sensitivity(df)
        stability_df, overall_rho, corrs = self.compute_rank_stability(sens_df)

        # Monte Carlo stability test (the real robustness check)
        mc_df = self.run_monte_carlo_stability(df, n_simulations=1000, perturbation=0.20)

        # GDP sensitivity
        gdp_scenarios = self.run_gdp_sensitivity(df)

        # Print report
        print("\n" + "="*70)
        print("AIRIS SENSITIVITY ANALYSIS REPORT")
        print("="*70)

        print(f"\n[1] WEIGHT SCENARIO SENSITIVITY")
        print(f"    Overall Spearman rank correlation across scenarios: {overall_rho:.3f}")
        if overall_rho >= 0.90:
            verdict = "STABLE across weight scenarios."
        elif overall_rho >= 0.75:
            verdict = "MOSTLY STABLE — minor reordering in middle ranks."
        else:
            verdict = "SENSITIVE — revisit index design before publishing."
        print(f"    Verdict: {verdict}\n")

        print("    Per-scenario correlation with baseline:")
        for scenario_name, rho in zip(list(self.WEIGHT_SCENARIOS.keys())[1:], corrs):
            bar = "#" * int(rho * 20)
            print(f"      {rho:.3f} {bar}  {scenario_name}")

        print(f"\n    District-level weight stability:")
        print(stability_df[["district_name", "baseline_rank", "min_rank",
                              "max_rank", "rank_range", "stability_class"]].to_string(index=False))

        # ── Monte Carlo Section ───────────────────────────────────────────────
        print(f"\n[2] MONTE CARLO RANK STABILITY (1,000 simulations, +-20% feature perturbation)")
        print(f"    This directly tests the rho=1.000 concern.")
        print(f"    {'─'*60}")
        if not mc_df.empty:
            mean_std = mc_df["mc_rank_std"].mean()
            print(f"    Mean rank std dev across all districts: {mean_std:.3f}")
            print(f"    Diagnosis: {mc_df['mc_diagnosis'].iloc[0]}\n")
            print(f"    Per-district Monte Carlo stability:")
            print(mc_df[["district_name", "baseline_rank", "mc_mean_rank",
                          "mc_rank_std", "mc_rank_p05", "mc_rank_p95",
                          "mc_rank_range", "mc_stability"]].to_string(index=False))
            print(f"\n    Interpretation:")
            print(f"    - If mc_rank_std < 0.5: artefact of synthetic data — expected to grow with real data")
            print(f"    - If mc_rank_std 0.5-1.5: genuine stability under noise")
            print(f"    - If mc_rank_std > 2.0: point ranks unreliable — report ranges only")

        print(f"\n[3] GDP LOSS SENSITIVITY (Range of Estimates)")
        print(f"    {'─'*60}")
        for name, result in gdp_scenarios.items():
            print(f"    {name}")
            print(f"      TFP assumption:  {result['tfp_assumption']}")
            print(f"      Annual loss:     Rs.{result['annual_loss_cr']:,.0f} crore "
                  f"/ ${result['annual_loss_usd_bn']:.2f}B USD")
            print(f"      Label:           [{result['label']}]")
            print()

        print(f"    Key finding: GDP loss estimate varies {min(r['annual_loss_cr'] for r in gdp_scenarios.values()):,.0f}--"
              f"{max(r['annual_loss_cr'] for r in gdp_scenarios.values()):,.0f} crore")
        print(f"    depending on TFP assumption. Must be presented as range, not point estimate.")

        print(f"\n[4] RECOMMENDATIONS FOR PUBLICATION")
        print(f"    1. Report baseline weights AND weight scenario table in appendix")
        print(f"    2. Report Monte Carlo rank range [p05, p95] alongside point rank")
        print(f"    3. Flag rho=1.000 as expected artefact of synthetic pilot data")
        print(f"    4. All GDP figures: label as 'exploratory model estimate'")
        print(f"    5. Add footnote: 'Results based on Q3 2024 data. Pending real TRAI/PLFS integration.'")
        print("="*70)

        return stability_df, mc_df, gdp_scenarios


if __name__ == "__main__":
    analyzer = SensitivityAnalyzer()
    stability_df, mc_df, gdp = analyzer.run()

