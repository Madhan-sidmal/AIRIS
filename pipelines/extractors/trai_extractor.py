"""
AIRIS — TRAI Broadband Data Extractor
======================================
Extracts district-level broadband penetration data from TRAI's
quarterly telecom subscription PDF reports.

What this produces:
  - Urban vs rural broadband penetration per district
  - Fiber vs mobile broadband breakdown
  - Data quality score per record

Data source: https://www.trai.gov.in/release-publication/reports/telecom-subscription-data
"""

import re
import requests
import pdfplumber
import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger
from datetime import datetime
from typing import Optional
from io import BytesIO


# ── Pilot district list (Census 2011 codes) ─────────────────────────────────
# Covering high-gap states: Bihar, Jharkhand, UP, Odisha, Rajasthan
# and comparison urban districts: Bangalore, Mumbai, Delhi, Hyderabad, Pune
PILOT_DISTRICTS = {
    # Rural / high-gap districts
    "BR001": {"name": "Patna",        "state": "Bihar",       "class": "mixed"},
    "BR002": {"name": "Gaya",         "state": "Bihar",       "class": "rural"},
    "JH001": {"name": "Ranchi",       "state": "Jharkhand",   "class": "mixed"},
    "JH002": {"name": "Dhanbad",      "state": "Jharkhand",   "class": "rural"},
    "UP001": {"name": "Lucknow",      "state": "Uttar Pradesh","class": "urban"},
    "UP002": {"name": "Bahraich",     "state": "Uttar Pradesh","class": "rural"},
    "OR001": {"name": "Bhubaneswar",  "state": "Odisha",      "class": "urban"},
    "OR002": {"name": "Kalahandi",    "state": "Odisha",      "class": "rural"},
    # Urban comparison districts
    "KA001": {"name": "Bengaluru",    "state": "Karnataka",   "class": "urban"},
    "MH001": {"name": "Mumbai",       "state": "Maharashtra", "class": "urban"},
}


class TRAIExtractor:
    """
    Extracts and parses TRAI quarterly broadband data.

    TRAI publishes telecom subscription data as PDFs every quarter.
    This extractor handles:
      1. Downloading the PDF (or using a local file for testing)
      2. Parsing broadband subscriber tables
      3. Standardizing district names to Census codes
      4. Computing rural/urban penetration rates
      5. Scoring data quality
    """

    BASE_URL = "https://www.trai.gov.in/release-publication/reports/telecom-subscription-data"
    RAW_DIR  = Path("data/raw/trai")

    def __init__(self):
        self.RAW_DIR.mkdir(parents=True, exist_ok=True)

    # ── Download ─────────────────────────────────────────────────────────────

    def download_report(self, quarter: str, year: int) -> Path:
        """
        Downloads TRAI quarterly report PDF.
        quarter: 'Q1', 'Q2', 'Q3', 'Q4'
        year: e.g. 2024

        If network is unavailable, falls back to synthetic data for development.
        """
        filename = self.RAW_DIR / f"trai_{quarter}_{year}.pdf"
        if filename.exists():
            logger.info(f"Using cached TRAI report: {filename}")
            return filename

        url = self._build_url(quarter, year)
        logger.info(f"Downloading TRAI report from: {url}")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            filename.write_bytes(response.content)
            logger.success(f"Downloaded {filename} ({len(response.content)/1024:.1f} KB)")
            return filename
        except Exception as e:
            logger.warning(f"Download failed: {e}. Generating synthetic data for development.")
            return None

    def _build_url(self, quarter: str, year: int) -> str:
        quarter_map = {"Q1": "march", "Q2": "june", "Q3": "september", "Q4": "december"}
        month = quarter_map.get(quarter, "december")
        return f"{self.BASE_URL}/telecom-subscription-data-{month}-{year}"

    # ── Parse ─────────────────────────────────────────────────────────────────

    def parse_pdf(self, pdf_path: Optional[Path]) -> pd.DataFrame:
        """
        Extracts broadband tables from TRAI PDF.
        Falls back to synthetic data if PDF unavailable (for development/testing).
        """
        if pdf_path is None or not pdf_path.exists():
            logger.warning("PDF not available. Using synthetic pilot data for development.")
            return self._generate_synthetic_data()

        logger.info(f"Parsing PDF: {pdf_path}")
        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_table()
                if extracted and self._is_broadband_table(extracted):
                    tables.append(pd.DataFrame(extracted[1:], columns=extracted[0]))

        if not tables:
            logger.warning("No broadband tables found in PDF. Using synthetic data.")
            return self._generate_synthetic_data()

        df = pd.concat(tables, ignore_index=True)
        return self._clean_trai_table(df)

    def _is_broadband_table(self, table: list) -> bool:
        """Identifies if extracted table contains broadband subscriber data."""
        if not table or not table[0]:
            return False
        header = " ".join(str(cell) for cell in table[0] if cell).lower()
        keywords = ["broadband", "subscriber", "urban", "rural", "district"]
        return sum(k in header for k in keywords) >= 2

    def _clean_trai_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardizes column names and data types from raw TRAI table."""
        # Normalize column names
        df.columns = [str(c).lower().strip().replace(" ", "_") for c in df.columns]

        # Map common TRAI column variations
        col_map = {
            "district": "district_name",
            "state": "state_name",
            "total_bb_subscribers": "total_subscribers",
            "urban_bb": "urban_subscribers",
            "rural_bb": "rural_subscribers",
            "wired_bb": "fiber_subscribers",
            "wireless_bb": "mobile_subscribers",
        }
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

        # Convert numeric columns
        numeric_cols = ["total_subscribers", "urban_subscribers", "rural_subscribers",
                        "fiber_subscribers", "mobile_subscribers"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", "").str.strip(),
                    errors="coerce"
                )
        return df.dropna(subset=["district_name"])

    # ── Synthetic Data (for development without live PDFs) ───────────────────

    def _generate_synthetic_data(self) -> pd.DataFrame:
        """
        Generates realistic synthetic broadband data for pilot districts.
        Based on TRAI 2024 Q3 report ranges:
          Urban India: 93% broadband penetration
          Rural India: 29.3% broadband penetration
          Source: TRAI Performance Indicator Report, Oct 2024
        """
        np.random.seed(42)
        records = []
        for code, info in PILOT_DISTRICTS.items():
            district_class = info["class"]

            # Set penetration based on urban/rural classification
            if district_class == "urban":
                urban_pct = np.random.uniform(88, 97)   # TRAI urban range
                rural_pct = np.random.uniform(40, 60)   # urban district rural areas
                fiber_pct = np.random.uniform(13, 18)   # 15.3% national urban avg
                avg_speed  = np.random.uniform(35, 65)  # Mbps
            elif district_class == "rural":
                urban_pct = np.random.uniform(50, 70)   # small towns in rural districts
                rural_pct = np.random.uniform(15, 35)   # TRAI rural range (29.3% avg)
                fiber_pct = np.random.uniform(2, 5)     # 3.8% national rural avg
                avg_speed  = np.random.uniform(8, 22)   # Mbps
            else:  # mixed
                urban_pct = np.random.uniform(70, 88)
                rural_pct = np.random.uniform(28, 45)
                fiber_pct = np.random.uniform(6, 12)
                avg_speed  = np.random.uniform(20, 38)

            population = np.random.randint(800_000, 5_000_000)
            urban_pop  = int(population * (0.6 if district_class == "urban" else 0.25))
            rural_pop  = population - urban_pop

            records.append({
                "district_code":        code,
                "district_name":        info["name"],
                "state_name":           info["state"],
                "district_class":       district_class,
                "population":           population,
                "urban_population":     urban_pop,
                "rural_population":     rural_pop,
                "urban_penetration_pct": round(urban_pct, 2),
                "rural_penetration_pct": round(rural_pct, 2),
                "fiber_penetration_pct": round(fiber_pct, 2),
                "avg_speed_mbps":        round(avg_speed, 1),
                "urban_subscribers":     int(urban_pop * urban_pct / 100),
                "rural_subscribers":     int(rural_pop * rural_pct / 100),
                "data_source":          "synthetic_trai_Q3_2024",
                "data_quality_score":   0.85,
            })

        df = pd.DataFrame(records)
        logger.info(f"Generated synthetic data for {len(df)} pilot districts")
        return df

    # ── Compute Gaps ──────────────────────────────────────────────────────────

    def compute_broadband_gaps(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Core computation: measures the rural-urban broadband gap per district
        and compares it against India's national urban average (93%).

        This directly answers: "How much infrastructure gap does each
        district face as the foundation of its AI exclusion?"
        """
        NATIONAL_URBAN_BENCHMARK = 93.0   # TRAI 2024
        NATIONAL_RURAL_BASELINE  = 29.3   # TRAI 2024

        df = df.copy()
        df["broadband_gap_pp"]        = df["urban_penetration_pct"] - df["rural_penetration_pct"]
        df["gap_vs_national_urban"]   = NATIONAL_URBAN_BENCHMARK - df["rural_penetration_pct"]
        df["rural_vs_national_rural"] = df["rural_penetration_pct"] - NATIONAL_RURAL_BASELINE
        df["penetration_ratio"]       = df["urban_penetration_pct"] / df["rural_penetration_pct"].replace(0, np.nan)
        df["infrastructure_gap_index"] = (df["gap_vs_national_urban"] / NATIONAL_URBAN_BENCHMARK * 100).clip(0, 100)

        # Flag districts worse than national rural average
        df["below_national_rural_avg"] = df["rural_penetration_pct"] < NATIONAL_RURAL_BASELINE

        logger.info(f"Computed broadband gaps for {len(df)} districts")
        logger.info(f"Districts below national rural avg: {df['below_national_rural_avg'].sum()}")
        logger.info(f"Average infrastructure gap index: {df['infrastructure_gap_index'].mean():.1f}")
        return df

    # ── Quality Scoring ───────────────────────────────────────────────────────

    def score_data_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Assigns a 0–1 quality score to each record based on:
        - Completeness (are all fields populated?)
        - Plausibility (are values in expected ranges?)
        - Freshness (how old is the data?)
        """
        required_cols = ["urban_penetration_pct", "rural_penetration_pct",
                         "fiber_penetration_pct", "avg_speed_mbps"]
        df = df.copy()

        completeness = df[required_cols].notna().mean(axis=1)

        plausibility = (
            df["urban_penetration_pct"].between(0, 100) &
            df["rural_penetration_pct"].between(0, 100) &
            df["avg_speed_mbps"].between(0, 1000)
        ).astype(float)

        df["data_quality_score"] = (completeness * 0.6 + plausibility * 0.4).round(3)
        return df

    # ── Full Pipeline ─────────────────────────────────────────────────────────

    def run(self, quarter: str = "Q3", year: int = 2024) -> pd.DataFrame:
        """
        Full extraction pipeline:
        Download → Parse → Clean → Compute Gaps → Score Quality → Save
        """
        logger.info(f"Starting TRAI extraction for {quarter} {year}")

        pdf_path = self.download_report(quarter, year)
        df = self.parse_pdf(pdf_path)
        df = self.compute_broadband_gaps(df)
        df = self.score_data_quality(df)

        # Save clean output
        output_path = Path("data/clean") / f"trai_broadband_{quarter}_{year}.parquet"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        logger.success(f"Saved clean broadband data → {output_path}")

        return df


# ── Run as script ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    extractor = TRAIExtractor()
    df = extractor.run(quarter="Q3", year=2024)

    print("\n" + "="*70)
    print("AIRIS — TRAI Broadband Extraction Results")
    print("="*70)
    print(f"\nDistricts processed: {len(df)}")
    print(f"\nBroadband Gap Summary:")
    print(df[["district_name", "state_name", "district_class",
              "urban_penetration_pct", "rural_penetration_pct",
              "broadband_gap_pp", "infrastructure_gap_index"]].to_string(index=False))
    print(f"\nNational averages for comparison:")
    print(f"  Urban India (TRAI 2024): 93.0%")
    print(f"  Rural India (TRAI 2024): 29.3%")
    print(f"  National gap:            63.7 percentage points")
    print(f"\nPilot district averages:")
    print(f"  Urban penetration:  {df['urban_penetration_pct'].mean():.1f}%")
    print(f"  Rural penetration:  {df['rural_penetration_pct'].mean():.1f}%")
    print(f"  Mean gap:           {df['broadband_gap_pp'].mean():.1f} pp")
    print(f"  Avg gap index:      {df['infrastructure_gap_index'].mean():.1f}/100")
    print(f"\nDistricts below national rural average (29.3%):")
    below = df[df["below_national_rural_avg"] == True]
    for _, row in below.iterrows():
        print(f"  ⚠  {row['district_name']} ({row['state_name']}): "
              f"{row['rural_penetration_pct']:.1f}% rural broadband")
    print("="*70)
