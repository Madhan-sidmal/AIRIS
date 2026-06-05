"""
AIRIS — Data Provenance & Lineage Tracker
==========================================
Answers the question every reviewer will ask:
  "Where exactly did this number come from?"

For every score in the AI Equity Index, this module produces a
complete audit trail:
  Source → Transformation → Feature → Index Component → Final Score

HONEST CLASSIFICATION:
  REAL      = Directly from a government/official source, unmodified
  DERIVED   = Computed from REAL data using documented formula
  ESTIMATED = Imputed using a model or proxy (labelled, not presented as measured)
  SYNTHETIC = Generated from statistical distributions for development/testing only
              MUST NEVER appear in a publication without this label
"""

import pandas as pd
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from typing import Literal
from loguru import logger


DataStatus = Literal["REAL", "DERIVED", "ESTIMATED", "SYNTHETIC"]


@dataclass
class DataPoint:
    """A single traceable data point in the AIRIS pipeline."""
    value:       float
    status:      DataStatus
    source_name: str
    source_url:  str
    source_date: str
    transformation: str
    notes:       str = ""


@dataclass
class DistrictProvenance:
    """Complete audit trail for one district's AI Equity Index score."""
    district_code:  str
    district_name:  str
    state_name:     str

    # Raw inputs
    rural_broadband_pct:  DataPoint = None
    urban_broadband_pct:  DataPoint = None
    fiber_penetration:    DataPoint = None
    avg_speed_mbps:       DataPoint = None
    avg_rural_wage:       DataPoint = None
    unemployment_rate:    DataPoint = None
    occupation_mix:       DataPoint = None

    # Benchmarks used
    benchmarks: dict = field(default_factory=dict)

    # Computed sub-indices
    infrastructure_gap_index: DataPoint = None
    adoption_gap_index:       DataPoint = None
    job_impact_index:         DataPoint = None

    # Final score
    ai_equity_index:          DataPoint = None

    def data_status_summary(self) -> dict:
        """Returns count of REAL / DERIVED / ESTIMATED / SYNTHETIC inputs."""
        points = [
            self.rural_broadband_pct, self.urban_broadband_pct,
            self.fiber_penetration, self.avg_speed_mbps,
            self.avg_rural_wage, self.unemployment_rate, self.occupation_mix,
        ]
        counts = {"REAL": 0, "DERIVED": 0, "ESTIMATED": 0, "SYNTHETIC": 0}
        for p in points:
            if p is not None:
                counts[p.status] = counts.get(p.status, 0) + 1
        return counts

    def is_publishable(self) -> bool:
        """A score is publishable only when ZERO inputs are SYNTHETIC."""
        summary = self.data_status_summary()
        return summary["SYNTHETIC"] == 0

    def publication_warning(self) -> str:
        summary = self.data_status_summary()
        if summary["SYNTHETIC"] > 0:
            return (f"NOT PUBLISHABLE: {summary['SYNTHETIC']} input(s) are SYNTHETIC. "
                    f"Replace with real data before publication.")
        elif summary["ESTIMATED"] > 0:
            return (f"PUBLISHABLE WITH CAVEATS: {summary['ESTIMATED']} input(s) are ESTIMATED. "
                    f"Label estimates clearly in paper.")
        else:
            return "PUBLISHABLE: All inputs are REAL or DERIVED from real sources."


class ProvenanceTracker:
    """
    Builds and stores data provenance records for every district.
    """

    FEAT_DIR = Path("data/features")

    # ── Benchmark provenance (these ARE real — from your research notes) ──────
    REAL_BENCHMARKS = {
        "urban_broadband_india_pct": DataPoint(
            value=93.0, status="REAL",
            source_name="TRAI Performance Indicator Report",
            source_url="https://www.trai.gov.in/release-publication/reports/performance-indicators-reports",
            source_date="Q3 2024",
            transformation="Direct reading from Table 1.1: Urban broadband penetration"
        ),
        "rural_broadband_india_pct": DataPoint(
            value=29.3, status="REAL",
            source_name="TRAI Performance Indicator Report",
            source_url="https://www.trai.gov.in/release-publication/reports/performance-indicators-reports",
            source_date="Q3 2024",
            transformation="Direct reading from Table 1.1: Rural broadband penetration"
        ),
        "urban_fiber_india_pct": DataPoint(
            value=15.3, status="REAL",
            source_name="TRAI Performance Indicator Report",
            source_url="https://www.trai.gov.in/release-publication/reports/performance-indicators-reports",
            source_date="Q3 2024",
            transformation="Direct reading from Table 1.3: Urban fiber (FTTH) penetration"
        ),
        "rural_fiber_india_pct": DataPoint(
            value=3.8, status="REAL",
            source_name="TRAI Performance Indicator Report",
            source_url="https://www.trai.gov.in/release-publication/reports/performance-indicators-reports",
            source_date="Q3 2024",
            transformation="Direct reading from Table 1.3: Rural fiber (FTTH) penetration"
        ),
        "urban_ai_job_exposure_pct": DataPoint(
            value=32.0, status="REAL",
            source_name="OECD Employment Outlook 2024, Chapter 3",
            source_url="https://www.oecd.org/employment/employment-outlook/",
            source_date="2024",
            transformation="Direct reading: 'Urban workers exposed to generative AI: 32%'"
        ),
        "rural_ai_job_exposure_pct": DataPoint(
            value=21.0, status="REAL",
            source_name="OECD Employment Outlook 2024, Chapter 3",
            source_url="https://www.oecd.org/employment/employment-outlook/",
            source_date="2024",
            transformation="Direct reading: 'Rural workers exposed to generative AI: 21%'"
        ),
        "cashier_automation_risk_pct": DataPoint(
            value=65.0, status="REAL",
            source_name="OECD Employment Outlook 2024",
            source_url="https://www.oecd.org/employment/employment-outlook/",
            source_date="2024",
            transformation="Direct reading: cashiers/retail automation risk"
        ),
        "manufacturing_automation_risk_pct": DataPoint(
            value=45.0, status="REAL",
            source_name="OECD Employment Outlook 2024",
            source_url="https://www.oecd.org/employment/employment-outlook/",
            source_date="2024",
            transformation="Direct reading: manufacturing automation risk"
        ),
        "farm_labour_automation_risk_pct": DataPoint(
            value=25.0, status="REAL",
            source_name="FAO State of Food and Agriculture 2024",
            source_url="https://www.fao.org/state-of-food-agriculture/",
            source_date="2024",
            transformation="Direct reading: agricultural labour automation risk"
        ),
        "china_urban_rural_income_ratio": DataPoint(
            value=2.46, status="REAL",
            source_name="National Bureau of Statistics China",
            source_url="https://www.stats.gov.cn/",
            source_date="H1 2024",
            transformation="Urban disposable income / Rural disposable income, H1 2024"
        ),
        "imf_ai_tfp_boost_pct": DataPoint(
            value=1.5, status="ESTIMATED",
            source_name="IMF World Economic Outlook 2024",
            source_url="https://www.imf.org/en/Publications/WEO",
            source_date="April 2024",
            transformation="Model estimate: AI adoption raises annual TFP by ~1.5% for adopters. "
                           "This is a macro-level estimate, not directly measured at district level.",
            notes="CAUTION: Use only as exploratory estimate in GDP loss calculation. "
                  "Label as 'model-derived' not 'measured' in any publication."
        ),
    }

    def build_provenance_for_district(
        self,
        district_code: str,
        district_name: str,
        state_name: str,
        trai_row: pd.Series,
        plfs_row: pd.Series,
        data_source_type: str = "SYNTHETIC"
    ) -> DistrictProvenance:
        """
        Builds a complete audit trail for one district.
        data_source_type: 'REAL', 'SYNTHETIC', or 'MIXED'
        """
        prov = DistrictProvenance(
            district_code=district_code,
            district_name=district_name,
            state_name=state_name,
            benchmarks=self.REAL_BENCHMARKS,
        )

        # ── Tag district-level inputs with their true status ──────────────────
        prov.rural_broadband_pct = DataPoint(
            value=trai_row.get("rural_penetration_pct", np.nan),
            status=data_source_type,
            source_name="TRAI Quarterly Broadband Report" if data_source_type == "REAL"
                         else "SYNTHETIC — generated from TRAI national range (15–35%)",
            source_url="https://www.trai.gov.in/release-publication/reports/telecom-subscription-data"
                       if data_source_type == "REAL" else "N/A",
            source_date="Q3 2024",
            transformation="Read from district-level table in TRAI PDF. "
                           "Cleaned: removed commas, converted to float, validated range [0,100]."
                           if data_source_type == "REAL" else
                           "np.random.uniform(15, 35) with seed=42. NOT a real measurement.",
            notes="" if data_source_type == "REAL" else
                  "MUST be replaced with real TRAI data before any publication."
        )

        prov.urban_broadband_pct = DataPoint(
            value=trai_row.get("urban_penetration_pct", np.nan),
            status=data_source_type,
            source_name="TRAI Quarterly Broadband Report" if data_source_type == "REAL"
                         else "SYNTHETIC",
            source_url="https://www.trai.gov.in/release-publication/reports/telecom-subscription-data",
            source_date="Q3 2024",
            transformation="Same as rural_broadband_pct" if data_source_type == "REAL"
                           else "np.random.uniform(88, 97) for urban districts. NOT real.",
        )

        prov.fiber_penetration = DataPoint(
            value=trai_row.get("fiber_penetration_pct", np.nan),
            status=data_source_type,
            source_name="TRAI" if data_source_type == "REAL" else "SYNTHETIC",
            source_url="https://www.trai.gov.in",
            source_date="Q3 2024",
            transformation="FTTH/FTTB subscriber count / district population * 100",
        )

        prov.avg_rural_wage = DataPoint(
            value=plfs_row.get("avg_weekly_wage", np.nan),
            status=data_source_type,
            source_name="PLFS Annual Report 2023-24" if data_source_type == "REAL"
                         else "SYNTHETIC — np.random.normal(3500, 1500)",
            source_url="https://mospi.gov.in/web/plfs",
            source_date="2023-24",
            transformation="Weighted mean of weekly wages using PLFS multipliers. "
                           "Sector filter: rural only (sector_code=2).",
        )

        prov.occupation_mix = DataPoint(
            value=plfs_row.get("net_displacement_risk", np.nan),
            status=data_source_type,
            source_name="PLFS 2023-24, NIC-2008 occupation codes" if data_source_type == "REAL"
                         else "SYNTHETIC occupation distribution + OECD/FAO risk coefficients",
            source_url="https://mospi.gov.in/web/plfs",
            source_date="2023-24",
            transformation="Σ(occupation_share × AI_displacement_risk) × (1 - replacement_rate). "
                           "Displacement risks from OECD 2024 and FAO 2024 (REAL benchmarks). "
                           "Occupation shares from PLFS (SYNTHETIC in this run).",
            notes="Hybrid: occupation RISKS are from real published sources. "
                  "Occupation SHARES for specific districts are synthetic in pilot."
        )

        # ── Computed sub-indices (DERIVED from inputs) ────────────────────────
        infra_idx = trai_row.get("infrastructure_gap_index", np.nan)
        prov.infrastructure_gap_index = DataPoint(
            value=infra_idx,
            status="DERIVED" if data_source_type == "REAL" else "SYNTHETIC",
            source_name="AIRIS computation",
            source_url="See analysis/indices/ai_equity_index.py:compute_infrastructure_gap_index()",
            source_date="Q3 2024",
            transformation=(
                "infrastructure_gap_index = "
                "  0.40 × (93.0 - rural_broadband_pct).clip(0,100)  [benchmark: TRAI 2024 urban avg] "
                "+ 0.25 × ((15.3 - fiber_pct) / 15.3 × 100).clip(0,100)  [benchmark: TRAI 2024] "
                "+ 0.20 × ((50 - avg_speed_mbps) / 50 × 100).clip(0,100) "
                "+ 0.15 × broadband_gap_pp.clip(0,100)"
            ),
            notes="Weight justification: Infrastructure is foundational — all other AI equity "
                  "dimensions depend on connectivity. 35% total weight in composite index. "
                  "Weights derived from literature review of digital divide indices "
                  "(ITU Digital Development Dashboard methodology, 2023)."
        )

        # ── Final index ───────────────────────────────────────────────────────
        final_idx = (
            0.35 * infra_idx +
            0.30 * trai_row.get("adoption_gap_index", np.nan) +
            0.35 * plfs_row.get("job_impact_index", np.nan)
        ) if not any(np.isnan([
            infra_idx,
            trai_row.get("adoption_gap_index", np.nan),
            plfs_row.get("job_impact_index", np.nan)
        ])) else np.nan

        prov.ai_equity_index = DataPoint(
            value=round(final_idx, 2) if not np.isnan(final_idx) else np.nan,
            status="DERIVED" if data_source_type == "REAL" else "SYNTHETIC",
            source_name="AIRIS Composite Index",
            source_url="See analysis/indices/ai_equity_index.py:compute_composite_index()",
            source_date="Q3 2024",
            transformation=(
                "ai_equity_index = "
                "  0.35 × infrastructure_gap_index "
                "+ 0.30 × adoption_gap_index "
                "+ 0.35 × job_impact_index"
            ),
            notes="Weight justification documented in methodology.md"
        )

        return prov

    def generate_provenance_report(
        self,
        df_trai: pd.DataFrame,
        df_plfs: pd.DataFrame,
        df_index: pd.DataFrame,
        data_source_type: str = "SYNTHETIC"
    ) -> pd.DataFrame:
        """Generates a full provenance report for all districts."""
        records = []
        plfs_lookup = df_plfs.set_index("district_code")

        for _, trai_row in df_trai.iterrows():
            code  = trai_row.get("district_code", "UNKNOWN")
            plfs_row = plfs_lookup.loc[code] if code in plfs_lookup.index else pd.Series()

            index_row = df_index[df_index.get("district_code", pd.Series()) == code]
            final_score = index_row["ai_equity_index"].values[0] if len(index_row) else np.nan

            prov = self.build_provenance_for_district(
                district_code=code,
                district_name=trai_row.get("district_name", "Unknown"),
                state_name=trai_row.get("state_name", "Unknown"),
                trai_row=trai_row,
                plfs_row=plfs_row,
                data_source_type=data_source_type
            )

            status_summary = prov.data_status_summary()
            records.append({
                "district_code":       code,
                "district_name":       trai_row.get("district_name"),
                "state_name":          trai_row.get("state_name"),
                "ai_equity_index":     round(final_score, 2) if not np.isnan(final_score) else np.nan,
                "rural_broadband_pct": prov.rural_broadband_pct.value,
                "rural_bb_status":     prov.rural_broadband_pct.status,
                "rural_bb_source":     prov.rural_broadband_pct.source_name,
                "wage_status":         prov.avg_rural_wage.status if prov.avg_rural_wage else "MISSING",
                "wage_source":         prov.avg_rural_wage.source_name if prov.avg_rural_wage else "MISSING",
                "occupation_status":   prov.occupation_mix.status if prov.occupation_mix else "MISSING",
                "is_publishable":      prov.is_publishable(),
                "publication_warning": prov.publication_warning(),
                "synthetic_count":     status_summary["SYNTHETIC"],
                "real_count":          status_summary["REAL"],
            })

        return pd.DataFrame(records)

    def print_district_audit(self, district_name: str,
                              df_trai: pd.DataFrame,
                              df_plfs: pd.DataFrame,
                              df_index: pd.DataFrame,
                              data_source_type: str = "SYNTHETIC"):
        """Prints a complete audit trail for a single district — the format reviewers want."""
        trai_row = df_trai[df_trai["district_name"] == district_name]
        if trai_row.empty:
            print(f"District '{district_name}' not found in TRAI data.")
            return

        trai_row = trai_row.iloc[0]
        code = trai_row["district_code"]
        plfs_lookup = df_plfs.set_index("district_code")
        plfs_row = plfs_lookup.loc[code] if code in plfs_lookup.index else pd.Series()

        idx_row = df_index[df_index["district_code"] == code]
        score = idx_row["ai_equity_index"].values[0] if len(idx_row) else np.nan

        prov = self.build_provenance_for_district(
            code, district_name,
            trai_row.get("state_name", ""),
            trai_row, plfs_row, data_source_type
        )

        print(f"\n{'='*70}")
        print(f"DATA PROVENANCE AUDIT: {district_name} ({trai_row.get('state_name', '')})")
        print(f"{'='*70}")
        print(f"\nFINAL SCORE: AI Equity Index = {score:.2f}/100  [{prov.ai_equity_index.status}]")
        print(f"\n{prov.publication_warning()}")

        print(f"\n{'─'*70}")
        print("INPUT DATA AUDIT")
        print(f"{'─'*70}")

        inputs = [
            ("Rural Broadband %", prov.rural_broadband_pct),
            ("Urban Broadband %", prov.urban_broadband_pct),
            ("Fiber Penetration %", prov.fiber_penetration),
            ("Avg Rural Wage (INR/week)", prov.avg_rural_wage),
            ("Occupation Mix / Displacement Risk", prov.occupation_mix),
        ]

        for label, point in inputs:
            if point is None:
                continue
            status_marker = {"REAL": "[REAL]", "DERIVED": "[DERIVED]",
                             "ESTIMATED": "[ESTIMATED]", "SYNTHETIC": "[SYNTHETIC ***]"}
            print(f"\n  {label}")
            print(f"  Value:  {point.value:.2f}" if isinstance(point.value, float) else f"  Value: {point.value}")
            print(f"  Status: {status_marker.get(point.status, point.status)}")
            print(f"  Source: {point.source_name}")
            print(f"  Date:   {point.source_date}")
            print(f"  Transform: {point.transformation[:120]}...")

        print(f"\n{'─'*70}")
        print("COMPUTATION TRACE")
        print(f"{'─'*70}")
        idx_row = df_index[df_index["district_code"] == code].iloc[0] if len(df_index[df_index["district_code"] == code]) else None
        if idx_row is not None:
            infra  = idx_row.get("infrastructure_gap_index", np.nan)
            adopt  = idx_row.get("adoption_gap_index", np.nan)
            job    = idx_row.get("job_impact_index", np.nan)
            final  = idx_row.get("ai_equity_index", np.nan)
            print(f"  Infrastructure Gap Index : {infra:.2f}  (weight: 35%  → contribution: {infra*0.35:.2f})")
            print(f"  AI Adoption Gap Index    : {adopt:.2f}  (weight: 30%  → contribution: {adopt*0.30:.2f})")
            print(f"  Job Impact Index         : {job:.2f}  (weight: 35%  → contribution: {job*0.35:.2f})")
            print(f"                             {'─'*40}")
            print(f"  AI Equity Index          : {final:.2f}")
        print(f"{'='*70}\n")
