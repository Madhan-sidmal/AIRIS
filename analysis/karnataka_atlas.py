"""
AIRIS — Karnataka AI Equity Atlas
===================================
Narrowed scope: 12 Karnataka districts, all socioeconomic classes.

Why Karnataka first:
  - Contains both India's AI capital (Bengaluru Urban)
    and some of its lowest HDI districts (Raichur, Kalaburagi)
  - Within-state variation is higher than most states — ideal for comparison
  - Karnataka IT policy team tracks AI adoption — potential collaboration
  - IISc, IIMs in Bengaluru for academic co-authorship

The core narrative:
  "Within one state — Karnataka — AI is creating a gap of X index points
   between Bengaluru Urban and Raichur. That gap is widening."

That single sentence, backed by real TRAI + PLFS data, is publishable.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger


# ── Karnataka Districts (all 31, pilot with 12 key districts) ────────────────
KARNATAKA_DISTRICTS = {
    # Urban / tech hub
    "KA001": {
        "name": "Bengaluru Urban",    "class": "urban_tech",
        "latitude": 12.97,  "longitude": 77.59,
        "population": 11_440_000,
        "primary_sector": "IT/services",
        "hdI_rank_karnataka": 1,
        "notes": "India AI capital. BharatNet not the constraint here."
    },
    # Peri-urban / high contrast
    "KA002": {
        "name": "Bengaluru Rural",    "class": "peri_urban",
        "latitude": 13.20,  "longitude": 77.52,
        "population": 990_000,
        "primary_sector": "agriculture/IT_satellite",
        "hdI_rank_karnataka": 5,
        "notes": "Same metro, rural periphery. Tests hyper-local gap."
    },
    # Tier-2 cities
    "KA003": {
        "name": "Mysuru",             "class": "tier2_city",
        "latitude": 12.30,  "longitude": 76.65,
        "population": 3_000_000,
        "primary_sector": "tourism/manufacturing",
        "hdI_rank_karnataka": 3,
        "notes": "Second-largest city. Strong silk/manufacturing base."
    },
    "KA004": {
        "name": "Belagavi",           "class": "tier2_city",
        "latitude": 15.85,  "longitude": 74.50,
        "population": 4_780_000,
        "primary_sector": "manufacturing/agriculture",
        "hdI_rank_karnataka": 8,
        "notes": "Border district. Different telecom infrastructure pattern."
    },
    "KA005": {
        "name": "Shivamogga",         "class": "transitional",
        "latitude": 13.93,  "longitude": 75.56,
        "population": 1_760_000,
        "primary_sector": "agriculture/education",
        "hdI_rank_karnataka": 7,
        "notes": "Emerging digital hub in central Karnataka."
    },
    "KA006": {
        "name": "Dakshina Kannada",   "class": "transitional",
        "latitude": 12.87,  "longitude": 75.24,
        "population": 2_090_000,
        "primary_sector": "banking/fisheries",
        "hdI_rank_karnataka": 2,
        "notes": "Coastal. High literacy, banking presence. Good broadband."
    },
    # High-exclusion districts (Northern dry zone)
    "KA007": {
        "name": "Kalaburagi",         "class": "rural_excluded",
        "latitude": 17.33,  "longitude": 76.82,
        "population": 2_564_000,
        "primary_sector": "agriculture/pulses",
        "hdI_rank_karnataka": 27,
        "notes": "Northern dry zone. Among lowest HDI in Karnataka. Key finding district."
    },
    "KA008": {
        "name": "Vijayapura",         "class": "rural_excluded",
        "latitude": 16.83,  "longitude": 75.72,
        "population": 2_178_000,
        "primary_sector": "agriculture/sugarcane",
        "hdI_rank_karnataka": 25,
        "notes": "Semi-arid. High drought exposure. High AI displacement risk."
    },
    "KA009": {
        "name": "Raichur",            "class": "rural_severely_excluded",
        "latitude": 16.20,  "longitude": 77.36,
        "population": 1_924_000,
        "primary_sector": "agriculture/rice",
        "hdI_rank_karnataka": 30,
        "notes": "Lowest HDI in Karnataka. Crucial anchor for 'severely excluded' class."
    },
    # Sector-specific districts
    "KA010": {
        "name": "Ballari",            "class": "rural_excluded",
        "latitude": 15.14,  "longitude": 76.92,
        "population": 2_532_000,
        "primary_sector": "mining/agriculture",
        "hdI_rank_karnataka": 22,
        "notes": "Mining economy. AI disruption pattern different from farm districts."
    },
    "KA011": {
        "name": "Chitradurga",        "class": "rural_excluded",
        "latitude": 14.23,  "longitude": 76.40,
        "population": 1_660_000,
        "primary_sector": "agriculture",
        "hdI_rank_karnataka": 18,
        "notes": "Representative interior rural Karnataka."
    },
    "KA012": {
        "name": "Kodagu",             "class": "transitional",
        "latitude": 12.42,  "longitude": 75.74,
        "population": 554_000,
        "primary_sector": "coffee/tourism",
        "hdI_rank_karnataka": 4,
        "notes": "Agriculture + tourism. Interesting AI adoption vs. displacement story."
    },
}


class KarnatakaAtlas:
    """
    Generates synthetic pilot data for the Karnataka AI Equity Atlas.
    Designed to be replaced with real TRAI state report + PLFS Karnataka sample.

    The Karnataka state telecom report is published separately:
    https://www.trai.gov.in/release-publication/reports/performance-indicators-reports
    (look for state-wise breakdown tables)
    """

    CLEAN_DIR = Path("data/clean/karnataka")
    FEAT_DIR  = Path("data/features/karnataka")

    def __init__(self):
        self.CLEAN_DIR.mkdir(parents=True, exist_ok=True)
        self.FEAT_DIR.mkdir(parents=True, exist_ok=True)

    def generate_karnataka_trai(self) -> pd.DataFrame:
        """
        Generates Karnataka district broadband data.
        Uses class-based distributions reflecting Karnataka's specific profile:
          - Karnataka urban: higher than national urban (tech investment)
          - Karnataka rural: slightly below national rural (northern dryzone drag)
        """
        np.random.seed(77)  # KA state code
        records = []

        for code, info in KARNATAKA_DISTRICTS.items():
            cls = info["class"]

            if cls == "urban_tech":
                rural_bb  = np.random.uniform(55, 70)   # Bengaluru Urban rural pockets
                urban_bb  = np.random.uniform(92, 98)   # Near-saturation
                fiber     = np.random.uniform(20, 30)   # Above national avg — tech infrastructure
                speed     = np.random.uniform(50, 120)  # Mbps — fiber-heavy
            elif cls == "peri_urban":
                rural_bb  = np.random.uniform(35, 55)
                urban_bb  = np.random.uniform(70, 85)
                fiber     = np.random.uniform(8, 15)
                speed     = np.random.uniform(25, 50)
            elif cls in ("tier2_city", "transitional"):
                rural_bb  = np.random.uniform(25, 42)
                urban_bb  = np.random.uniform(65, 85)
                fiber     = np.random.uniform(5, 12)
                speed     = np.random.uniform(18, 40)
            elif cls == "rural_excluded":
                rural_bb  = np.random.uniform(12, 28)   # Below Karnataka rural avg
                urban_bb  = np.random.uniform(45, 65)   # Small town connectivity
                fiber     = np.random.uniform(1, 5)
                speed     = np.random.uniform(6, 18)
            else:  # rural_severely_excluded (Raichur)
                rural_bb  = np.random.uniform(8, 18)    # Well below national rural avg (29.3%)
                urban_bb  = np.random.uniform(35, 55)
                fiber     = np.random.uniform(0.5, 3)
                speed     = np.random.uniform(4, 12)

            records.append({
                "district_code":            code,
                "district_name":            info["name"],
                "state_name":               "Karnataka",
                "district_class":           cls,
                "hdi_rank_karnataka":       info["hdI_rank_karnataka"],
                "primary_sector":           info["primary_sector"],
                "latitude":                 info["latitude"],
                "longitude":                info["longitude"],
                "population":               info["population"],
                "rural_penetration_pct":    round(rural_bb, 2),
                "urban_penetration_pct":    round(urban_bb, 2),
                "fiber_penetration_pct":    round(fiber, 2),
                "avg_speed_mbps":           round(speed, 1),
                "broadband_gap_pp":         round(urban_bb - rural_bb, 2),
                "gap_vs_national_urban":    round(93.0 - rural_bb, 2),
                "data_source":              "synthetic_Karnataka_pilot",
                "data_status":              "SYNTHETIC",
            })

        df = pd.DataFrame(records)
        # Compute infrastructure gap index (same formula as national pipeline)
        df["infrastructure_gap_index"] = (
            0.40 * (93.0 - df["rural_penetration_pct"]).clip(0, 100) +
            0.25 * ((15.3 - df["fiber_penetration_pct"]) / 15.3 * 100).clip(0, 100) +
            0.20 * ((50 - df["avg_speed_mbps"]) / 50 * 100).clip(0, 100) +
            0.15 * df["broadband_gap_pp"].clip(0, 100)
        ).clip(0, 100).round(2)

        path = self.CLEAN_DIR / "karnataka_trai_Q3_2024.parquet"
        df.to_parquet(path, index=False)
        logger.success(f"Karnataka TRAI data saved -> {path}")
        return df

    def generate_karnataka_plfs(self) -> pd.DataFrame:
        """
        Karnataka-specific occupation mix reflecting sectoral reality.
        Raichur/Kalaburagi: heavy agriculture + manual labour
        Bengaluru: heavy IT + services
        """
        np.random.seed(88)
        records = []

        for code, info in KARNATAKA_DISTRICTS.items():
            cls = info["class"]

            if cls == "urban_tech":
                base_wage = 18000  # IT salaries
                unemp_rate = 4.2
                displacement_risk = 22.0  # Low — AI augments
            elif cls == "peri_urban":
                base_wage = 9000
                unemp_rate = 6.5
                displacement_risk = 31.0
            elif cls in ("tier2_city", "transitional"):
                base_wage = 6500
                unemp_rate = 7.8
                displacement_risk = 36.0
            elif cls == "rural_excluded":
                base_wage = 3200
                unemp_rate = 11.2
                displacement_risk = 44.0  # High — agriculture + retail
            else:  # severely_excluded
                base_wage = 2400  # Raichur — lowest in Karnataka
                unemp_rate = 14.1
                displacement_risk = 51.0  # Very high — manual farm labour dominant

            records.append({
                "district_code":       code,
                "sector":              "rural" if "rural" in cls or "excluded" in cls else "urban",
                "avg_weekly_wage":     round(max(800, np.random.normal(base_wage, base_wage * 0.2)), 0),
                "unemployment_rate":   round(max(2, np.random.normal(unemp_rate, 1.5)), 2),
                "net_displacement_risk": round(max(5, np.random.normal(displacement_risk, 5)), 2),
                "upskilling_deficit":  round(displacement_risk * 0.6, 2),
                "job_impact_index":    round((0.65 * displacement_risk + 0.35 * displacement_risk * 0.6), 2),
            })

        df = pd.DataFrame(records)
        path = self.CLEAN_DIR / "karnataka_plfs_2024.parquet"
        df.to_parquet(path, index=False)
        logger.success(f"Karnataka PLFS data saved -> {path}")
        return df

    def compute_karnataka_index(self, df_trai: pd.DataFrame,
                                  df_plfs: pd.DataFrame) -> pd.DataFrame:
        """Computes AI Equity Index for Karnataka districts."""
        ADOPTION_SCALE = 32.9 / 93.0

        df = df_trai.merge(df_plfs, on="district_code", how="left")

        df["est_rural_ai_adoption"] = (df["rural_penetration_pct"] * ADOPTION_SCALE).clip(0, 100)
        df["adoption_gap_index"]    = ((32.9 - df["est_rural_ai_adoption"]) / 32.9 * 100).clip(0, 100).round(2)

        df["ai_equity_index"] = (
            0.35 * df["infrastructure_gap_index"] +
            0.30 * df["adoption_gap_index"] +
            0.35 * df["job_impact_index"]
        ).clip(0, 100).round(2)

        df["net_ai_impact_score"] = (50 - df["ai_equity_index"]).round(2)

        df["ai_equity_class"] = pd.cut(
            df["ai_equity_index"],
            bins=[0, 25, 50, 75, 100],
            labels=["Included", "Transitional", "Excluded", "Severely Excluded"],
            include_lowest=True
        )

        df["karnataka_rank"] = df["ai_equity_index"].rank(ascending=False).astype(int)

        path = self.FEAT_DIR / "karnataka_ai_equity_Q3_2024.parquet"
        df.to_parquet(path, index=False)
        logger.success(f"Karnataka AI Equity Index saved -> {path}")
        return df

    def print_karnataka_atlas(self, df: pd.DataFrame):
        print("\n" + "="*70)
        print("KARNATAKA AI EQUITY ATLAS — Q3 2024")
        print("12 Districts | From Bengaluru Urban to Raichur")
        print("="*70)

        cols = ["karnataka_rank", "district_name", "primary_sector",
                "rural_penetration_pct", "avg_weekly_wage",
                "ai_equity_index", "ai_equity_class"]
        print(df.sort_values("karnataka_rank")[cols].to_string(index=False))

        # The headline number
        top = df.loc[df["karnataka_rank"].idxmax()]
        bot = df.loc[df["karnataka_rank"].idxmin()]
        gap = bot["ai_equity_index"] - top["ai_equity_index"]

        print(f"\nKARNATAKA GAP STORY:")
        print(f"  Most included:     {bot['district_name']} (score: {bot['ai_equity_index']:.1f})")
        print(f"  Most excluded:     {top['district_name']} (score: {top['ai_equity_index']:.1f})")
        print(f"  Within-state gap:  {gap:.1f} index points")
        print(f"  Rural BB gap:      {bot['rural_penetration_pct']:.1f}% vs {top['rural_penetration_pct']:.1f}%")
        print(f"  Wage gap:          Rs.{bot['avg_weekly_wage']:,.0f} vs Rs.{top['avg_weekly_wage']:,.0f} /week")

        print(f"\nPAPER HEADLINE (after real data):")
        print(f"  'Karnataka's AI Divide: A {gap:.0f}-Point Gap Between Bengaluru and Raichur'")
        print("="*70)

    def run(self) -> pd.DataFrame:
        logger.info("Generating Karnataka AI Equity Atlas...")
        df_trai = self.generate_karnataka_trai()
        df_plfs = self.generate_karnataka_plfs()
        df_idx  = self.compute_karnataka_index(df_trai, df_plfs)
        self.print_karnataka_atlas(df_idx)
        return df_idx


if __name__ == "__main__":
    atlas = KarnatakaAtlas()
    df = atlas.run()
