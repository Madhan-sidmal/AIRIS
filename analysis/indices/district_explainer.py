"""
AIRIS — District Explainer
============================
Answers: "WHY is this district ranked here?"

For each district, decomposes the AI Equity Index into:
  - Contribution of each sub-index
  - Which specific input drove each sub-index
  - What would have to change to move this district one class up

This is the 'explainability layer' that makes AIRIS a research
tool rather than just a ranking — reviewers and policymakers
need to understand the mechanism, not just the score.
"""

import pandas as pd
import numpy as np
from pathlib import Path


class DistrictExplainer:
    """
    Produces human-readable explanations for each district's AI Equity score.
    """

    FEAT_DIR  = Path("data/features")
    CLEAN_DIR = Path("data/clean")

    # Weight map (must match ai_equity_index.py)
    WEIGHTS = {
        "infrastructure_gap_index": 0.35,
        "adoption_gap_index":       0.30,
        "job_impact_index":         0.35,
    }

    LABELS = {
        "infrastructure_gap_index": "Infrastructure Gap",
        "adoption_gap_index":       "AI Adoption Gap",
        "job_impact_index":         "Job Displacement Risk",
    }

    def load_data(self, quarter="Q3", year=2024):
        idx_path  = self.FEAT_DIR  / f"ai_equity_index_{quarter}_{year}.parquet"
        trai_path = self.CLEAN_DIR / f"trai_broadband_{quarter}_{year}.parquet"
        plfs_path = self.CLEAN_DIR / f"plfs_district_{year}.parquet"

        df_idx  = pd.read_parquet(idx_path)
        df_trai = pd.read_parquet(trai_path)
        df_plfs = pd.read_parquet(plfs_path)
        return df_idx, df_trai, df_plfs

    def explain_district(self, district_name: str,
                          df_idx: pd.DataFrame,
                          df_trai: pd.DataFrame,
                          df_plfs: pd.DataFrame) -> dict:
        """
        Returns the full explanation dictionary for one district.
        """
        row = df_idx[df_idx["district_name"] == district_name]
        if row.empty:
            return {"error": f"District '{district_name}' not found."}
        row = row.iloc[0]

        # ── Sub-index contributions ───────────────────────────────────────────
        contributions = {}
        for col, weight in self.WEIGHTS.items():
            val = row.get(col, 0) or 0
            contributions[self.LABELS[col]] = {
                "sub_index_score": round(val, 2),
                "weight":          weight,
                "contribution":    round(val * weight, 2),
                "pct_of_total":    round(val * weight / row["ai_equity_index"] * 100, 1)
                                   if row["ai_equity_index"] else 0,
            }

        # ── Primary drivers (sorted by contribution) ──────────────────────────
        drivers = sorted(contributions.items(),
                         key=lambda x: x[1]["contribution"], reverse=True)

        # ── Raw inputs ────────────────────────────────────────────────────────
        trai_row = df_trai[df_trai["district_name"] == district_name]
        plfs_row = df_plfs[df_plfs["district_code"] == row["district_code"]]

        raw_inputs = {}
        if not trai_row.empty:
            t = trai_row.iloc[0]
            raw_inputs.update({
                "rural_broadband_pct":     t.get("rural_penetration_pct"),
                "urban_broadband_pct":     t.get("urban_penetration_pct"),
                "broadband_gap_pp":        t.get("broadband_gap_pp"),
                "fiber_penetration_pct":   t.get("fiber_penetration_pct"),
                "avg_speed_mbps":          t.get("avg_speed_mbps"),
                "gap_vs_national_urban":   t.get("gap_vs_national_urban"),
            })
        if not plfs_row.empty:
            p = plfs_row.iloc[0]
            raw_inputs.update({
                "avg_weekly_wage_inr":     p.get("avg_weekly_wage"),
                "unemployment_rate_pct":   p.get("unemployment_rate"),
                "net_displacement_risk":   p.get("net_displacement_risk"),
            })

        # ── What would it take to move up one class? ──────────────────────────
        current_class = row.get("ai_equity_index", 50)
        class_boundaries = {
            "Severely Excluded → Excluded": 75,
            "Excluded → Transitional":      50,
            "Transitional → Included":      25,
        }
        needed_reduction = None
        target_class = None
        for label, boundary in class_boundaries.items():
            if current_class > boundary:
                needed_reduction = round(current_class - boundary + 0.01, 2)
                target_class = label
                break

        # ── Intervention priority ─────────────────────────────────────────────
        top_driver = drivers[0][0]
        intervention_map = {
            "Infrastructure Gap":     "Priority intervention: Expand rural broadband (BharatNet phase 3). "
                                      f"Need to close ~{raw_inputs.get('gap_vs_national_urban', 'N/A'):.1f} pp gap.",
            "AI Adoption Gap":        "Priority intervention: Digital literacy programs + low-cost device access. "
                                      "Broadband alone insufficient — usage gap needs demand-side push.",
            "Job Displacement Risk":  "Priority intervention: Rural re-skilling programs for displaced workers. "
                                      "Focus on manufacturing and retail workers at highest automation risk.",
        }

        return {
            "district_name":     district_name,
            "state_name":        row.get("state_name"),
            "district_class":    row.get("district_class"),
            "ai_equity_index":   row.get("ai_equity_index"),
            "ai_equity_class":   str(row.get("ai_equity_class")),
            "national_rank":     int(row.get("national_rank", 0)),
            "sub_index_contributions": contributions,
            "primary_driver":        drivers[0][0],
            "driver_rank":           [d[0] for d in drivers],
            "raw_inputs":            raw_inputs,
            "to_move_up":            {
                "transition":     target_class,
                "points_needed":  needed_reduction,
                "intervention":   intervention_map.get(top_driver, "See methodology."),
            },
        }

    def print_explanation(self, district_name: str,
                           df_idx: pd.DataFrame,
                           df_trai: pd.DataFrame,
                           df_plfs: pd.DataFrame):
        """Pretty-prints the explanation for a district."""
        exp = self.explain_district(district_name, df_idx, df_trai, df_plfs)
        if "error" in exp:
            print(exp["error"])
            return

        print(f"\n{'='*70}")
        print(f"WHY IS {exp['district_name'].upper()} RANKED #{exp['national_rank']}?")
        print(f"State: {exp['state_name']}  |  Class: {exp['ai_equity_class']}")
        print(f"AI Equity Index: {exp['ai_equity_index']:.2f}/100")
        print(f"{'='*70}")

        print(f"\nSCORE DECOMPOSITION (what is driving the exclusion?)")
        print(f"{'─'*70}")
        max_bar = 40
        for name, data in sorted(exp["sub_index_contributions"].items(),
                                   key=lambda x: x[1]["contribution"], reverse=True):
            bar_len = int(data["contribution"] / exp["ai_equity_index"] * max_bar)
            bar = "|" * bar_len
            marker = " <-- PRIMARY DRIVER" if name == exp["primary_driver"] else ""
            print(f"  {name:<25}: {data['sub_index_score']:5.1f}/100 "
                  f"x {data['weight']:.0%} = +{data['contribution']:5.2f} pts  "
                  f"[{data['pct_of_total']:4.1f}%]  {bar}{marker}")

        print(f"\nRAW INPUT VALUES (what produced each sub-index score?)")
        print(f"{'─'*70}")
        inputs = exp["raw_inputs"]
        nat_urban_bb = 93.0
        nat_rural_bb = 29.3
        print(f"  Broadband (rural):   {inputs.get('rural_broadband_pct', 'N/A'):.1f}%"
              f"  [India rural avg: {nat_rural_bb}%  |  India urban avg: {nat_urban_bb}%]")
        print(f"  Broadband (urban):   {inputs.get('urban_broadband_pct', 'N/A'):.1f}%")
        print(f"  Gap vs urban India:  {inputs.get('gap_vs_national_urban', 'N/A'):.1f} pp")
        print(f"  Fiber penetration:   {inputs.get('fiber_penetration_pct', 'N/A'):.1f}%"
              f"  [India rural avg: 3.8%  |  India urban avg: 15.3%]")
        print(f"  Avg speed:           {inputs.get('avg_speed_mbps', 'N/A'):.1f} Mbps")
        print(f"  Avg weekly wage:     Rs.{inputs.get('avg_weekly_wage_inr', 0):,.0f}"
              f"  [national rural avg: ~Rs.3,500]")
        print(f"  Unemployment rate:   {inputs.get('unemployment_rate_pct', 'N/A'):.1f}%")
        print(f"  Displacement risk:   {inputs.get('net_displacement_risk', 'N/A'):.1f}/100")

        print(f"\nINTERVENTION ANALYSIS")
        print(f"{'─'*70}")
        to_move = exp["to_move_up"]
        if to_move["transition"]:
            print(f"  To achieve: {to_move['transition']}")
            print(f"  Index must fall by: {to_move['points_needed']:.1f} points")
            print(f"  Primary lever: {to_move['intervention']}")

        print(f"\nDRIVER RANKING (most to least influential)")
        print(f"{'─'*70}")
        for i, driver in enumerate(exp["driver_rank"], 1):
            print(f"  {i}. {driver}")
        print(f"{'='*70}\n")

    def explain_all(self, quarter="Q3", year=2024):
        """Runs explanation for all districts and prints a summary comparison."""
        df_idx, df_trai, df_plfs = self.load_data(quarter, year)

        print(f"\n{'='*70}")
        print("AIRIS — DISTRICT EXPLANATION SUMMARY")
        print("What is driving AI exclusion in each district?")
        print(f"{'='*70}")

        summary_rows = []
        for name in df_idx["district_name"].dropna():
            exp = self.explain_district(name, df_idx, df_trai, df_plfs)
            if "error" not in exp:
                summary_rows.append({
                    "rank":           exp["national_rank"],
                    "district":       name,
                    "state":          exp["state_name"],
                    "score":          exp["ai_equity_index"],
                    "class":          exp["ai_equity_class"],
                    "primary_driver": exp["primary_driver"],
                    "infra_contrib":  exp["sub_index_contributions"]["Infrastructure Gap"]["contribution"],
                    "adopt_contrib":  exp["sub_index_contributions"]["AI Adoption Gap"]["contribution"],
                    "job_contrib":    exp["sub_index_contributions"]["Job Displacement Risk"]["contribution"],
                })

        summary = pd.DataFrame(summary_rows).sort_values("rank")
        print(summary.to_string(index=False))

        print(f"\n{'─'*70}")
        print("PRIMARY DRIVER DISTRIBUTION")
        print(f"{'─'*70}")
        driver_counts = summary["primary_driver"].value_counts()
        for driver, count in driver_counts.items():
            print(f"  {driver:<30}: {count} districts")

        print(f"\nPOLICY IMPLICATION:")
        top_driver = driver_counts.index[0]
        if top_driver == "Infrastructure Gap":
            print("  Most districts are excluded primarily because of connectivity.")
            print("  Broadband investment (BharatNet) is the highest-leverage intervention.")
        elif top_driver == "Job Displacement Risk":
            print("  Most districts face exclusion primarily through job displacement.")
            print("  Re-skilling programs matter more than broadband alone.")
        elif top_driver == "AI Adoption Gap":
            print("  Most districts have connectivity but aren't adopting AI.")
            print("  Demand-side interventions (literacy, devices, use cases) are needed.")

        # Deep-dive for #1 ranked district
        if not summary.empty:
            top_district = summary.iloc[0]["district"]
            print(f"\n{'='*70}")
            print(f"DETAILED AUDIT: {top_district} (Rank #1 — Most AI-Excluded)")
            self.print_explanation(top_district, df_idx, df_trai, df_plfs)

        return summary


if __name__ == "__main__":
    explainer = DistrictExplainer()
    explainer.explain_all()
