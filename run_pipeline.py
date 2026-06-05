"""
AIRIS — Master Pipeline Runner
================================
Run this file to execute the full AIRIS pilot pipeline:

  1. Extract TRAI broadband data (or generate synthetic)
  2. Parse PLFS employment data (or generate synthetic)
  3. Compute AI Equity Index for all pilot districts
  4. Print results and save to data/features/

Usage:
  python run_pipeline.py

Then launch the dashboard:
  streamlit run dashboard/app.py
"""

import sys
from pathlib import Path
from loguru import logger

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from pipelines.extractors.trai_extractor import TRAIExtractor
from pipelines.extractors.plfs_parser import PLFSParser
from analysis.indices.ai_equity_index import AIEquityIndexCalculator


def run_airis_pilot():
    print("\n" + "="*70)
    print("  AIRIS - AI Rural Impact Surveillance System")
    print("  Pilot Run: 10 districts | Q3 2024")
    print("="*70 + "\n")

    # Step 1: TRAI
    print("─" * 50)
    print("STEP 1: Extracting TRAI Broadband Data")
    print("─" * 50)
    trai = TRAIExtractor()
    df_trai = trai.run(quarter="Q3", year=2024)
    print(f"[OK] Broadband data ready for {len(df_trai)} districts\n")

    # Step 2: PLFS
    print("─" * 50)
    print("STEP 2: Parsing PLFS Employment Data")
    print("─" * 50)
    plfs = PLFSParser()
    df_plfs = plfs.run(survey_year=2024)
    print(f"[OK] Employment data ready for {df_plfs['district_code'].nunique()} districts\n")

    # Step 3: Index
    print("─" * 50)
    print("STEP 3: Computing AI Equity Index")
    print("─" * 50)
    calc = AIEquityIndexCalculator()
    df_index, gdp = calc.run(quarter="Q3", year=2024)

    # Final summary
    print("\n" + "="*70)
    print("  AIRIS RESULTS - AI Equity Index (Q3 2024)")
    print("="*70)
    cols = ["national_rank", "district_name", "state_name",
            "ai_equity_index", "ai_equity_class", "net_ai_impact_score"]
    print(df_index.sort_values("national_rank")[cols].to_string(index=False))

    print(f"\n{'─'*70}")
    print("ESTIMATED ANNUAL GDP LOSS FROM AI EXCLUSION (PILOT DISTRICTS)")
    print(f"{'─'*70}")
    print(f"  Excluded districts : {gdp['excluded_districts']}")
    print(f"  Annual GDP loss    : ₹{gdp['total_annual_gdp_loss_cr']:,.0f} crore")
    print(f"                       ${gdp['total_annual_gdp_loss_usd_bn']:.2f} billion USD")

    print(f"\n{'─'*70}")
    print("CLASSIFICATION BREAKDOWN")
    print(f"{'─'*70}")
    for cls, cnt in df_index["ai_equity_class"].value_counts().items():
        bar = "#" * int(cnt * 5)
        print(f"  {cls:<22}: {bar} {cnt} ({cnt/len(df_index)*100:.0f}%)")

    print(f"\n{'─'*70}")
    print("NEXT STEP: Launch the dashboard")
    print(f"{'─'*70}")
    print("  streamlit run dashboard/app.py")
    print(f"\n{'='*70}\n")

    return df_index, gdp


if __name__ == "__main__":
    df, gdp = run_airis_pilot()
