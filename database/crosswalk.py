"""
AIRIS — District Crosswalk Loader & Validator
==============================================
Loads district_crosswalk.csv and provides:
  - Canonical name resolution (TRAI label -> AIRIS code)
  - Spelling mismatch detection at join time
  - Boundary change warnings
  - Unmatched district auditing

Usage pattern:
  from database.crosswalk import CrosswalkResolver
  xw = CrosswalkResolver()
  airis_code = xw.resolve_trai("Mysore")  # -> "KA003"
  airis_code = xw.resolve_plfs("GULBARGA")  # -> "KA007"

Run as script to validate crosswalk integrity:
  python database/crosswalk.py
"""

import pandas as pd
from pathlib import Path
from loguru import logger
from typing import Optional


class CrosswalkResolver:
    """
    The single source of truth for district name resolution in AIRIS.
    Prevents the silent join failures that kill research projects.
    """

    CROSSWALK_PATH = Path("database/seeds/district_crosswalk.csv")

    def __init__(self):
        self.df = self._load()
        self._build_lookup_maps()
        self._log_warnings()

    def _load(self) -> pd.DataFrame:
        if not self.CROSSWALK_PATH.exists():
            raise FileNotFoundError(
                f"Crosswalk file not found: {self.CROSSWALK_PATH}\n"
                "This file is required before any data join operations."
            )
        df = pd.read_csv(self.CROSSWALK_PATH)
        logger.info(f"Crosswalk loaded: {len(df)} districts")
        return df

    def _build_lookup_maps(self):
        """Builds all lookup dictionaries for fast resolution."""
        # TRAI label -> AIRIS code (case-insensitive, stripped)
        self._trai_map = {
            row["trai_district_label"].strip().upper(): row["district_code"]
            for _, row in self.df.iterrows()
        }
        # PLFS label -> AIRIS code
        self._plfs_map = {
            row["plfs_district_label"].strip().upper(): row["district_code"]
            for _, row in self.df.iterrows()
        }
        # Canonical name -> AIRIS code
        self._canonical_map = {
            row["canonical_name"].strip().upper(): row["district_code"]
            for _, row in self.df.iterrows()
        }
        # Census 2011 code -> AIRIS code
        self._census_map = {
            str(row["district_code_census_2011"]): row["district_code"]
            for _, row in self.df.iterrows()
        }
        # AIRIS code -> canonical name
        self._code_to_name = {
            row["district_code"]: row["canonical_name"]
            for _, row in self.df.iterrows()
        }

    def _log_warnings(self):
        """Logs all districts requiring special handling."""
        mismatches = self.df[self.df["data_quality_flag"] != "VERIFIED"]
        if not mismatches.empty:
            logger.warning(
                f"{len(mismatches)} districts have data quality flags — "
                "check crosswalk before joining TRAI/PLFS data"
            )
            for _, row in mismatches.iterrows():
                logger.warning(
                    f"  [{row['data_quality_flag']}] {row['canonical_name']}: "
                    f"TRAI='{row['trai_district_label']}' / "
                    f"PLFS='{row['plfs_district_label']}' "
                    f"({row['boundary_change_note']})"
                )

    def resolve_trai(self, trai_label: str) -> Optional[str]:
        """Returns AIRIS code for a TRAI district label. Returns None if not found."""
        code = self._trai_map.get(trai_label.strip().upper())
        if code is None:
            logger.warning(
                f"TRAI label '{trai_label}' not found in crosswalk. "
                "This will cause a silent join failure. Add to district_crosswalk.csv."
            )
        return code

    def resolve_plfs(self, plfs_label: str) -> Optional[str]:
        """Returns AIRIS code for a PLFS district label."""
        code = self._plfs_map.get(plfs_label.strip().upper())
        if code is None:
            logger.warning(
                f"PLFS label '{plfs_label}' not found in crosswalk. "
                "This will cause a silent join failure."
            )
        return code

    def resolve_census(self, census_code: str) -> Optional[str]:
        """Returns AIRIS code for a Census 2011 district code."""
        return self._census_map.get(str(census_code))

    def canonical_name(self, airis_code: str) -> str:
        """Returns the canonical name for an AIRIS district code."""
        return self._code_to_name.get(airis_code, airis_code)

    def get_flag(self, airis_code: str) -> str:
        """Returns the data quality flag for a district."""
        row = self.df[self.df["district_code"] == airis_code]
        return row["data_quality_flag"].values[0] if not row.empty else "UNKNOWN"

    def get_boundary_note(self, airis_code: str) -> str:
        """Returns the boundary change note for a district."""
        row = self.df[self.df["district_code"] == airis_code]
        note = row["boundary_change_note"].values[0] if not row.empty else ""
        return note if pd.notna(note) else ""

    def annotate_dataframe(self, df: pd.DataFrame,
                           label_col: str,
                           source: str = "trai") -> pd.DataFrame:
        """
        Adds 'district_code' and 'canonical_name' columns to a DataFrame
        by resolving district labels using the crosswalk.

        source: 'trai', 'plfs', or 'census'
        """
        resolver = {
            "trai":   self.resolve_trai,
            "plfs":   self.resolve_plfs,
            "census": self.resolve_census,
        }.get(source, self.resolve_trai)

        df = df.copy()
        df["district_code"]   = df[label_col].apply(resolver)
        df["canonical_name"]  = df["district_code"].apply(
            lambda c: self.canonical_name(c) if c else None
        )
        df["crosswalk_flag"]  = df["district_code"].apply(
            lambda c: self.get_flag(c) if c else "UNMATCHED"
        )

        unmatched = df["district_code"].isna().sum()
        if unmatched > 0:
            logger.error(
                f"{unmatched} rows could not be matched via crosswalk ({source}). "
                "These will be DROPPED from analysis. Add missing labels to crosswalk."
            )
        return df

    def audit_unmatched(self, labels: list, source: str = "trai") -> list:
        """
        Given a list of district labels from a data source, returns those
        that are NOT in the crosswalk — these will cause silent join failures.
        """
        resolver_map = {
            "trai":   self._trai_map,
            "plfs":   self._plfs_map,
            "census": self._census_map,
        }
        lookup = resolver_map.get(source, self._trai_map)
        unmatched = [l for l in labels if l.strip().upper() not in lookup]
        return unmatched

    def validate(self) -> dict:
        """Full validation report for the crosswalk file."""
        total     = len(self.df)
        verified  = (self.df["data_quality_flag"] == "VERIFIED").sum()
        spelling  = (self.df["data_quality_flag"] == "SPELLING_MISMATCH").sum()
        boundary  = (self.df["data_quality_flag"] == "BOUNDARY_CHANGE").sum()
        label_mm  = (self.df["data_quality_flag"] == "LABEL_MISMATCH").sum()
        trai_split = (self.df["data_quality_flag"] == "TRAI_SPLIT_DISTRICT").sum()

        return {
            "total_districts":          total,
            "verified":                 int(verified),
            "spelling_mismatches":      int(spelling),
            "boundary_changes":         int(boundary),
            "label_mismatches":         int(label_mm),
            "trai_split_districts":     int(trai_split),
            "risk_level":               "HIGH" if boundary > 0 else
                                        "MEDIUM" if spelling > 2 else "LOW",
            "recommendation": (
                "Review BOUNDARY_CHANGE districts manually before time-series joins. "
                "Vijayanagara (KA030) was created in 2021 — TRAI reports may still show Ballari."
            ) if boundary > 0 else "Crosswalk integrity acceptable for Beta."
        }


def print_crosswalk_audit():
    """Standalone audit — run before any real data ingestion."""
    xw = CrosswalkResolver()
    report = xw.validate()

    print("\n" + "="*70)
    print("AIRIS DISTRICT CROSSWALK AUDIT")
    print("="*70)
    print(f"\nTotal districts mapped:     {report['total_districts']}")
    print(f"Verified (no issues):       {report['verified']}")
    print(f"Spelling mismatches:        {report['spelling_mismatches']}")
    print(f"  (e.g. Mysore/Mysuru, Belgaum/Belagavi, Gulbarga/Kalaburagi)")
    print(f"Boundary changes:           {report['boundary_changes']}")
    print(f"  (e.g. Vijayanagara created 2021 from Ballari)")
    print(f"Label mismatches:           {report['label_mismatches']}")
    print(f"  (e.g. Bhubaneswar->Khordha in TRAI/PLFS)")
    print(f"TRAI split districts:       {report['trai_split_districts']}")
    print(f"\nRisk Level: {report['risk_level']}")
    print(f"\nRecommendation: {report['recommendation']}")

    print(f"\n{'─'*70}")
    print("SAMPLE RESOLUTION TESTS")
    print(f"{'─'*70}")
    test_cases = [
        ("Mysore",         "trai",   "KA003"),
        ("GULBARGA",       "plfs",   "KA007"),
        ("BIJAPUR",        "plfs",   "KA008"),
        ("Bangalore Urban","trai",   "KA001"),
        ("KHORDHA",        "plfs",   "OR001"),
        ("Shimoga",        "trai",   "KA005"),
        ("BELLARY",        "plfs",   "KA010"),
        ("PATNA",          "plfs",   "BR001"),
        ("Unknown District","trai",  None),
    ]
    all_pass = True
    for label, source, expected in test_cases:
        resolver = xw.resolve_trai if source == "trai" else xw.resolve_plfs
        result = resolver(label)
        status = "PASS" if result == expected else "FAIL"
        if status == "FAIL":
            all_pass = False
        print(f"  [{status}] {source.upper()} '{label}' -> {result}  (expected: {expected})")

    print(f"\nCrosswalk test suite: {'ALL PASS' if all_pass else 'FAILURES DETECTED — fix crosswalk.csv'}")
    print("="*70)


if __name__ == "__main__":
    print_crosswalk_audit()
