"""
AIRIS — PLFS Employment Data Parser
=====================================
Parses Periodic Labour Force Survey (PLFS) microdata to extract
district-level employment, wages, and AI exposure by occupation.

What this produces:
  - Employment counts by sector and occupation per district
  - Average wages (urban vs rural) per district
  - AI displacement risk score based on occupation mix
  - Unemployment rate per district

Data source:
  MOSPI PLFS Annual Reports — https://mospi.gov.in/web/plfs
  Format: Fixed-width text files (.txt) with codebook
"""

import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger
from typing import Optional


# ── AI Displacement Risk by Occupation (NIC-2008 codes) ─────────────────────
# Sources: OECD 2024, FAO, McKinsey Global Institute
# These are the numbers from your research notes, operationalized
AI_DISPLACEMENT_RISK = {
    # NIC Code: (occupation_label, displacement_risk_0_to_1)
    "4700": ("retail_cashiers_trade",         0.65),  # 65% at risk — your Note 1
    "3100": ("manufacturing_operatives",       0.45),  # 45% at risk — your Note 1
    "0100": ("agricultural_labour",            0.25),  # 25% at risk — FAO, your Note 1
    "4900": ("transport_logistics",            0.40),
    "4100": ("clerical_support",               0.55),
    "4200": ("customer_service_clerks",        0.60),
    "4300": ("numerical_clerks",               0.65),
    "5800": ("food_service_hospitality",       0.35),
    "6200": ("software_IT",                    0.08),  # Low — AI augments, doesn't displace
    "8500": ("machine_operators",              0.50),
    "9100": ("elementary_cleaning",            0.30),
    "9200": ("agricultural_elementary",        0.22),
    "2600": ("professional_technical",         0.12),
    "2400": ("business_finance_professionals", 0.18),
}

# Sectors dominating rural economies (from OECD 2024 data in Note 2)
RURAL_DOMINANT_SECTORS = {
    "agriculture":    {"share": 0.42, "ai_adoption_rural": 0.04, "ai_adoption_urban": 0.18},
    "manufacturing":  {"share": 0.15, "ai_adoption_rural": 0.12, "ai_adoption_urban": 0.31},
    "retail":         {"share": 0.12, "ai_adoption_rural": 0.08, "ai_adoption_urban": 0.27},
    "construction":   {"share": 0.11, "ai_adoption_rural": 0.031,"ai_adoption_urban": 0.072},
    "hospitality":    {"share": 0.08, "ai_adoption_rural": 0.04, "ai_adoption_urban": 0.078},
    "healthcare":     {"share": 0.05, "ai_adoption_rural": 0.06, "ai_adoption_urban": 0.22},
    "transport":      {"share": 0.07, "ai_adoption_rural": 0.05, "ai_adoption_urban": 0.092},
}


class PLFSParser:
    """
    Parses PLFS microdata to produce district-level employment and
    AI displacement risk profiles.

    PLFS data is released as fixed-width text files with a separate
    codebook defining column positions. This parser handles the
    standard PLFS Annual Report format.
    """

    RAW_DIR   = Path("data/raw/plfs")
    CLEAN_DIR = Path("data/clean")

    # PLFS fixed-width column specification (Annual Report format)
    # Positions are 1-indexed as per PLFS codebook
    PLFS_COLUMNS = {
        "state_code":       (1, 2),
        "district_code":    (3, 5),
        "sector":           (6, 6),    # 1=urban, 2=rural
        "household_id":     (7, 12),
        "person_id":        (13, 14),
        "age":              (15, 16),
        "sex":              (17, 17),
        "education_level":  (18, 19),
        "nic_2digit":       (20, 21),  # Industry of work
        "nco_code":         (22, 24),  # Occupation code
        "employment_status":(25, 25),
        "weekly_wage":      (26, 32),
        "usual_activity":   (33, 34),
        "multiplier":       (35, 42),  # Sample weight
    }

    def __init__(self):
        self.RAW_DIR.mkdir(parents=True, exist_ok=True)
        self.CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    # ── Parse ─────────────────────────────────────────────────────────────────

    def parse_plfs_file(self, filepath: Optional[Path]) -> pd.DataFrame:
        """
        Parses PLFS fixed-width text file into a DataFrame.
        Falls back to synthetic data for development.
        """
        if filepath is None or not filepath.exists():
            logger.warning("PLFS file not found. Generating synthetic data for development.")
            return self._generate_synthetic_plfs()

        logger.info(f"Parsing PLFS file: {filepath}")
        try:
            colspecs = [(v[0]-1, v[1]) for v in self.PLFS_COLUMNS.values()]
            names    = list(self.PLFS_COLUMNS.keys())
            df = pd.read_fwf(filepath, colspecs=colspecs, names=names,
                             dtype=str, encoding="latin-1")
            df = self._clean_plfs(df)
            logger.success(f"Parsed {len(df):,} PLFS records")
            return df
        except Exception as e:
            logger.error(f"PLFS parse failed: {e}. Using synthetic data.")
            return self._generate_synthetic_plfs()

    def _clean_plfs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Converts data types and applies PLFS coding standards."""
        df["sector_label"] = df["sector"].map({"1": "urban", "2": "rural"})
        df["sex_label"]    = df["sex"].map({"1": "male", "2": "female"})
        df["weekly_wage"]  = pd.to_numeric(df["weekly_wage"], errors="coerce")
        df["age"]          = pd.to_numeric(df["age"], errors="coerce")
        df["multiplier"]   = pd.to_numeric(df["multiplier"], errors="coerce").fillna(1)
        return df.dropna(subset=["district_code", "sector"])

    # ── Aggregate to District Level ───────────────────────────────────────────

    def aggregate_to_district(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregates person-level PLFS data to district-level summary.
        Produces weighted estimates using PLFS multipliers.
        """
        logger.info("Aggregating PLFS data to district level...")

        records = []
        for (district_code, sector), group in df.groupby(["district_code", "sector_label"]):
            total_workers  = (group["multiplier"]).sum()
            employed       = group[group["employment_status"].isin(["1", "2"])]
            unemployed     = group[group["employment_status"] == "5"]

            records.append({
                "district_code":      district_code,
                "sector":             sector,
                "total_workers":      int(total_workers),
                "employed_count":     int(employed["multiplier"].sum()),
                "unemployed_count":   int(unemployed["multiplier"].sum()),
                "unemployment_rate":  float(unemployed["multiplier"].sum() /
                                           total_workers * 100) if total_workers > 0 else np.nan,
                "avg_weekly_wage":    float((employed["weekly_wage"] *
                                            employed["multiplier"]).sum() /
                                           employed["multiplier"].sum())
                                       if len(employed) > 0 else np.nan,
                "median_weekly_wage": float(employed["weekly_wage"].median())
                                       if len(employed) > 0 else np.nan,
            })

        return pd.DataFrame(records)

    # ── Compute AI Displacement Risk ──────────────────────────────────────────

    def compute_ai_displacement_risk(self, df: pd.DataFrame,
                                     district_sector_df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes district-level AI displacement risk based on occupation mix.

        Formula:
          Risk = Σ (occupation_share × AI_displacement_probability)
          Net risk = Risk × (1 - rural_replacement_rate)

        The replacement rate is low for rural areas because new AI-created jobs
        cluster in cities — the core finding of your research notes.
        """
        logger.info("Computing AI displacement risk by district...")

        # Occupation distribution per district
        occ_dist = (df.groupby(["district_code", "nic_2digit"])["multiplier"]
                      .sum()
                      .reset_index())
        total    = occ_dist.groupby("district_code")["multiplier"].sum().rename("total")
        occ_dist = occ_dist.join(total, on="district_code")
        occ_dist["occupation_share"] = occ_dist["multiplier"] / occ_dist["total"]

        # Map NIC codes to displacement risk
        occ_dist["displacement_risk"] = occ_dist["nic_2digit"].apply(
            lambda code: AI_DISPLACEMENT_RISK.get(str(code), ("unknown", 0.20))[1]
        )

        # Weighted risk per district
        risk_by_district = (
            occ_dist.groupby("district_code")
            .apply(lambda g: (g["occupation_share"] * g["displacement_risk"]).sum())
            .reset_index(name="raw_displacement_risk")
        )

        # Rural areas face higher NET risk: fewer replacement jobs created
        # Urban areas: AI creates jobs at 0.7x displacement rate (OECD 2024)
        # Rural areas: AI creates jobs at 0.15x displacement rate (low AI investment)
        RURAL_REPLACEMENT_RATE = 0.15
        URBAN_REPLACEMENT_RATE = 0.70

        sector_lookup = district_sector_df.set_index("district_code")["sector"].to_dict()
        risk_by_district["sector"] = risk_by_district["district_code"].map(sector_lookup)
        risk_by_district["replacement_rate"] = risk_by_district["sector"].map(
            {"urban": URBAN_REPLACEMENT_RATE, "rural": RURAL_REPLACEMENT_RATE}
        ).fillna(RURAL_REPLACEMENT_RATE)

        risk_by_district["net_displacement_risk"] = (
            risk_by_district["raw_displacement_risk"] *
            (1 - risk_by_district["replacement_rate"]) * 100
        ).clip(0, 100).round(2)

        return risk_by_district[["district_code", "raw_displacement_risk", "net_displacement_risk"]]

    # ── Synthetic PLFS Data ───────────────────────────────────────────────────

    def _generate_synthetic_plfs(self) -> pd.DataFrame:
        """
        Generates realistic synthetic PLFS person-level records.
        Based on PLFS 2023-24 summary statistics.
        """
        np.random.seed(123)
        records = []

        from pipelines.extractors.trai_extractor import PILOT_DISTRICTS

        for code, info in PILOT_DISTRICTS.items():
            district_class = info["class"]
            n_records = 500  # ~500 person records per district for pilot

            # Occupation mix differs by urban/rural
            if district_class == "urban":
                nic_codes   = np.random.choice(
                    list(AI_DISPLACEMENT_RISK.keys()),
                    size=n_records,
                    p=[0.02, 0.08, 0.02, 0.08, 0.10, 0.08, 0.08,
                       0.06, 0.12, 0.08, 0.06, 0.02, 0.10, 0.10]
                )
                base_wage   = 8000  # INR/week — urban average
                wage_spread = 4000
            else:
                nic_codes   = np.random.choice(
                    list(AI_DISPLACEMENT_RISK.keys()),
                    size=n_records,
                    p=[0.03, 0.12, 0.30, 0.10, 0.06, 0.06, 0.04,
                       0.05, 0.02, 0.08, 0.05, 0.04, 0.03, 0.02]
                )
                base_wage   = 3500  # INR/week — rural average
                wage_spread = 1500

            for i in range(n_records):
                records.append({
                    "district_code":     code,
                    "state_code":        code[:2],
                    "sector":            "1" if district_class == "urban" else "2",
                    "sector_label":      district_class if district_class != "mixed" else "rural",
                    "household_id":      f"{code}{i:04d}",
                    "person_id":         str(np.random.randint(1, 8)),
                    "age":               np.random.randint(15, 65),
                    "sex":               np.random.choice(["1", "2"]),
                    "nic_2digit":        nic_codes[i],
                    "employment_status": np.random.choice(
                        ["1", "2", "5", "81", "82"],
                        p=[0.50, 0.25, 0.10, 0.10, 0.05]
                    ),
                    "weekly_wage":       max(0, np.random.normal(base_wage, wage_spread)),
                    "multiplier":        np.random.uniform(80, 200),
                })

        df = pd.DataFrame(records)
        logger.info(f"Generated synthetic PLFS data: {len(df):,} person records "
                    f"across {len(PILOT_DISTRICTS)} districts")
        return df

    # ── Full Pipeline ─────────────────────────────────────────────────────────

    def run(self, plfs_path: Optional[Path] = None,
            survey_year: int = 2024) -> pd.DataFrame:
        """
        Full PLFS pipeline:
        Parse → Aggregate → Compute AI Risk → Save
        """
        logger.info(f"Starting PLFS extraction for survey year {survey_year}")

        df_raw       = self.parse_plfs_file(plfs_path)
        df_district  = self.aggregate_to_district(df_raw)
        df_risk      = self.compute_ai_displacement_risk(df_raw, df_district)
        df_final     = df_district.merge(df_risk, on="district_code", how="left")
        df_final["survey_year"] = survey_year

        output_path = self.CLEAN_DIR / f"plfs_district_{survey_year}.parquet"
        df_final.to_parquet(output_path, index=False)
        logger.success(f"Saved PLFS district data → {output_path}")
        return df_final


# ── Run as script ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = PLFSParser()
    df = parser.run(survey_year=2024)

    print("\n" + "="*70)
    print("AIRIS — PLFS Employment Extraction Results")
    print("="*70)
    print(f"\nDistricts processed: {df['district_code'].nunique()}")
    print(f"\nEmployment & Wage Summary:")
    summary = df.groupby("sector").agg(
        avg_wage=("avg_weekly_wage", "mean"),
        avg_unemployment=("unemployment_rate", "mean"),
        avg_displacement_risk=("net_displacement_risk", "mean"),
    ).round(2)
    print(summary)
    print(f"\nWage gap (urban vs rural): "
          f"{df[df['sector']=='urban']['avg_weekly_wage'].mean():.0f} vs "
          f"{df[df['sector']=='rural']['avg_weekly_wage'].mean():.0f} INR/week")
    print(f"Displacement risk gap:     "
          f"{df[df['sector']=='urban']['net_displacement_risk'].mean():.1f} vs "
          f"{df[df['sector']=='rural']['net_displacement_risk'].mean():.1f} (urban vs rural)")
    print("="*70)
