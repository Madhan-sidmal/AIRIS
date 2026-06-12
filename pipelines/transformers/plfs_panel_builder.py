"""
AIRIS Phase 3 — Harmonized PLFS Schema Builder
================================================
Produces a consistent district-year panel from:
  - PLFS 2019-20 (pre-period baseline)
  - PLFS 2023-24 (post-period, already extracted)

Designed to receive any PLFS annual round and output
a standardized district-level summary CSV.

Usage:
  python pipelines/transformers/plfs_panel_builder.py \
    --year 2019 --state_code 29

Schema (output: plfs_district_panel.csv):
  district_code   : PLFS sequential district code
  district_name   : Canonical name (from crosswalk)
  state_code      : PLFS state code (29 = Karnataka)
  survey_year     : e.g., 2019, 2023
  n_rural_persons : Unweighted rural person records
  n_employed      : Unweighted employed persons (activity 11-51 principal)
  employed_weight : Weighted employed count
  unemp_rate_wt   : Weighted unemployment rate (%)
  agri_share_wt   : Weighted agriculture employment share (NIC 01-03, %)
  nonagri_share_wt: Weighted non-agricultural employment share (%)
  services_share  : Weighted services sector share (NIC 45-99, %)
  edu_secondary_wt: Weighted share with secondary+ education (%)
  log_wage_median : Median log real weekly wage (wage workers, activities 21/31/32)
  wage_n          : Count of wage worker observations
  sample_grade    : A/B/C/D by n_employed threshold
  data_status     : REAL or SYNTHETIC
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import zipfile
import io


# ─── Configuration ────────────────────────────────────────────────────────────
SCHEMA_VERSION = "1.0"
DATA_DIR       = Path("data/raw/plfs")
OUT_DIR        = Path("data/clean/panel")
CROSSWALK_FILE = Path("database/seeds/district_crosswalk.csv")

# Activity codes: PLFS uses different coding in 2019-20 vs 2023-24
# 2019-20 (2-digit): 11,12=self-employed; 21=regular wage; 31,32=casual; 41,51=others; 61,71=unemployed
# 2023-24 (1-digit): 1,2,3=self-employed; 4=regular wage; 5=casual; 6=unemployed; 7-9=others
EMPLOYED_CODES_OLD  = [11, 12, 21, 31, 32, 41, 51]   # 2019-20 coding
EMPLOYED_CODES_NEW  = [1, 2, 3, 4, 5]                # 2023-24 coding
UNEMP_CODES_OLD     = [61, 71]
UNEMP_CODES_NEW     = [6]
LABOUR_FORCE_OLD    = list(range(11, 72))
LABOUR_FORCE_NEW    = list(range(1, 7))
WAGE_WORKER_OLD     = [21, 31, 32]
WAGE_WORKER_NEW     = [4, 5]

# Keep legacy name for backward compatibility
EMPLOYED_CODES      = EMPLOYED_CODES_OLD
WAGE_WORKER_CODES   = WAGE_WORKER_OLD

# NIC sector groupings (NIC 2008)
AGRI_NIC   = list(range(1, 4))    # 01-03: Agriculture, forestry, fishing
NONAGRI_NIC= list(range(10, 100)) # 10-99: All non-agricultural
SERVICES_NIC = list(range(45, 100)) # 45-99: Trade + services

# Sample grade thresholds
GRADE_THRESHOLDS = {"A": 500, "B": 300, "C": 200, "D": 0}

# PLFS column name variants across rounds
# Some column names changed between 2019-20 and 2023-24
COLUMN_ALIASES = {
    # ─── 2023-24 PLFS (_perrv suffix) ───────────────────────────────────────
    "dist_code_perrv":   "district_code",   # 2023-24 district sequential code
    "state_perrv":       "state_code_col",
    "mult_perrv":        "weight",
    "b4q4_perrv":        "activity_status",  # principal activity status (1-9)
    # b4q5_perrv = broad sector (1=Agri, 2=Industry, 3=Services) — USE THIS for agri share
    # b4q6_perrv = NIC 2-digit industry code — USE THIS for services sub-split only
    "b2q7_perrv":        "education",        # general education level
    "b2q3_perrv":        "age",
    "b6q5_3pt1_perrv":   "wage_earnings",    # earnings for principal activity
    # ─── 2021-22 PLFS (same _perrv suffix, but district col is b1q4_perrv) ──
    "b1q4_perrv":        "district_code",    # 2021-22 district sequential code
    # ─── 2019-20 PLFS (_per_rv suffix) ──────────────────────────────────────
    "district_per_rv":   "district_code",   # 2019-20 district sequential code
    "state_per_rv":      "state_code_col",
    "MULT_per_rv":       "weight",
    "mult_per_rv":       "weight",
    "b4q4_per_rv":       "activity_status",  # activity status in 2019-20
    # b4q5_per_rv = broad sector (1=Agri, 2=Industry, 3=Services) — SAME CODING
    # b4q6_per_rv = NIC 2-digit
    "b2q7_per_rv":       "education",
    "b2q3_per_rv":       "age",
}


def load_plfs_rural(zip_path: Path, year: int) -> pd.DataFrame:
    """
    Load rural persons file from PLFS ZIP.
    Handles both 2019-20 and 2023-24 file naming conventions.
    """
    possible_names = [
        "perrv.csv", "PERRV.CSV",
        f"perrv_{year}.csv",
        "per_rv.csv", "PER_RV.CSV",
    ]
    with zipfile.ZipFile(zip_path, "r") as z:
        available = z.namelist()
        match = next(
            (n for n in available if any(p.lower() in n.lower() for p in ["perrv", "per_rv"])),
            None
        )
        if match is None:
            raise FileNotFoundError(
                f"Cannot find rural persons file in {zip_path}.\n"
                f"Available: {available}"
            )
        print(f"  Loading: {match}")
        with z.open(match) as f:
            df = pd.read_csv(f, low_memory=False)

    # Normalise column names
    df.columns = [c.strip() for c in df.columns]
    return df


def normalise_columns(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Apply column aliases and ensure canonical column names exist."""
    for old, new in COLUMN_ALIASES.items():
        if old in df.columns and new not in df.columns:
            df = df.rename(columns={old: new})

    # Ensure weight column exists
    weight_candidates = ["mult_perrv", "weight", "MULT_PERRV", "wt"]
    for wc in weight_candidates:
        if wc in df.columns:
            df["weight"] = df[wc]
            break

    return df


def get_sample_grade(n: int) -> str:
    for grade, threshold in sorted(GRADE_THRESHOLDS.items(), key=lambda x: -x[1]):
        if n >= threshold:
            return grade
    return "D"


def compute_district_stats(df: pd.DataFrame, state_code: int, year: int,
                            crosswalk: pd.DataFrame) -> pd.DataFrame:
    """
    Core computation: district-level weighted statistics.
    Applies the same methodology as plfs_karnataka_real.py (Working Paper 0).
    """
    # Filter to state — handle both naming conventions
    state_col = next(
        (c for c in df.columns if c in
         ["state_code_col", "state_perrv", "B_001", "State", "state"]),
        None
    )
    if state_col is None:
        # Try any column with 'state' in name
        state_col = next((c for c in df.columns if "state" in c.lower()), None)
    if state_col:
        df = df[pd.to_numeric(df[state_col], errors='coerce') == state_code].copy()
    print(f"  Records for state {state_code}: {len(df):,}")

    if len(df) == 0:
        raise ValueError(
            f"No records found for state_code={state_code}. "
            f"State column used: {state_col}. "
            f"Unique state values: {df[state_col].unique()[:10] if state_col else 'N/A'}"
        )

    # Ensure district code exists
    if "district_code" not in df.columns:
        raise ValueError(f"district_code column not found. Available: {list(df.columns[:20])}")

    # Activity status: employed
    act_col = next(
        (c for c in df.columns if c in
         ["activity_status", "b4q4_perrv", "B_019", "B_020"]),
        None
    )
    if act_col is None:
        raise ValueError(f"Activity status column not found. Available: {list(df.columns[:30])}")

    df["is_employed"] = df[act_col].isin(EMPLOYED_CODES)

    # Detect PLFS coding round (2023-24 uses 1-digit codes)
    act_values = set(pd.to_numeric(df[act_col], errors='coerce').dropna().unique())
    is_new_coding = max(act_values) <= 9  # 2023-24: max code is 9
    employed_codes = EMPLOYED_CODES_NEW if is_new_coding else EMPLOYED_CODES_OLD
    unemp_codes    = UNEMP_CODES_NEW    if is_new_coding else UNEMP_CODES_OLD
    lf_codes       = LABOUR_FORCE_NEW   if is_new_coding else LABOUR_FORCE_OLD
    wage_codes     = WAGE_WORKER_NEW    if is_new_coding else WAGE_WORKER_OLD
    print(f"  Coding scheme: {'2023-24 (1-digit)' if is_new_coding else '2019-20 (2-digit)'}")

    df["is_employed"] = df[act_col].isin(employed_codes)

    # NIC industry code
    nic_col = next(
        (c for c in df.columns if c in
         ["nic_industry", "b4q5_perrv", "b4q6_perrv", "B_020", "B_021"]
         or c.lower().startswith("nic")),
        None
    )

    # Education
    edu_col = next(
        (c for c in df.columns if c in
         ["education", "b2q7_perrv", "B_007", "B_006", "gen_edu"]),
        None
    )

    # Wage
    wage_col = next(
        (c for c in df.columns if c in
         ["wage_per_day", "b3q10_perrv", "b3q11_perrv", "B_054", "B_041", "earn_per_day"]),
        None
    )

    results = []
    for dist_code, group in df.groupby("district_code"):
        n_total = len(group)
        emp = group[group["is_employed"]].copy()
        n_emp = len(emp)

        if n_emp == 0:
            continue

        w = emp["weight"].fillna(0)
        w_total = w.sum()
        if w_total == 0:
            continue

        # ─── Sector shares ───────────────────────────────────────────────────
        # CONFIRMED: b4q5 = broad sector flag (1=Agriculture, 2=Industry, 3=Services)
        # This coding is CONSISTENT across 2019-20, 2021-22, 2023-24
        # Do NOT use b4q5 as NIC code — it has only 3 values (1,2,3)
        # Do NOT use b4q6 for agriculture — b4q6 is NIC-2 digit (0-96)
        agri_share, nonagri_share, svc_share = None, None, None
        broad_col = next(
            (c for c in emp.columns if c in ["b4q5_perrv", "b4q5_per_rv"]),
            None
        )
        nic2_col = next(
            (c for c in emp.columns if c in ["b4q6_perrv", "b4q6_per_rv"]),
            None
        )
        if broad_col:
            try:
                broad = pd.to_numeric(emp[broad_col], errors='coerce')
                # 1 = Agriculture/Forestry/Fishing
                # 2 = Industry (Mining, Manufacturing, Utilities, Construction)
                # 3 = Services (Trade, Transport, Finance, Public Admin, etc.)
                agri_share    = float(w[broad == 1].sum() / w_total * 100)
                nonagri_share = float(w[broad.isin([2, 3])].sum() / w_total * 100)
                # Services sub-split from b4q6 NIC-2 digit (when available)
                if nic2_col:
                    nic2 = pd.to_numeric(emp[nic2_col], errors='coerce')
                    # NIC 45-96 ≈ services sectors
                    svc_share = float(w[nic2 >= 45].sum() / w_total * 100)
            except Exception as e:
                pass

        # Unemployment rate
        lf  = group[pd.to_numeric(group[act_col], errors='coerce').isin(lf_codes)].copy()
        lf_w    = lf["weight"].fillna(0).sum()
        unemp_w = group[pd.to_numeric(group[act_col], errors='coerce').isin(unemp_codes)]["weight"].fillna(0).sum()
        unemp_rate = (unemp_w / lf_w * 100) if lf_w > 0 else None

        # Education: secondary+ (usually coded 4,5,6+ depending on round)
        edu_share = None
        if edu_col and edu_col in emp.columns:
            try:
                edu = pd.to_numeric(emp[edu_col], errors="coerce")
                # Codes ≥ 4 = secondary and above (standard PLFS education codes)
                edu_share = (w[edu >= 4].sum() / w_total * 100)
            except Exception:
                pass

        # ─── Wages ───────────────────────────────────────────────────────────
        # Wage earnings: b6q5_3pt1 = weekly earnings for principal regular/casual wage job
        # In 2019-20: b6q5_3pt1_per_rv; 2021-22/2023-24: b6q5_3pt1_perrv
        log_wage_median, wage_n = None, 0
        wage_col = next(
            (c for c in emp.columns if 'b6q5_3pt1' in c or c in ["wage_earnings", "wage_per_day"]),
            None
        )
        if wage_col:
            try:
                ww = emp[pd.to_numeric(emp[act_col], errors='coerce').isin(wage_codes)].copy()
                wages = pd.to_numeric(ww[wage_col], errors="coerce").dropna()
                wages = wages[wages > 0]
                wage_n = len(wages)
                if wage_n >= 10:
                    log_wage_median = float(np.log(wages.median()))
            except Exception:
                pass

        # District name from crosswalk
        cw_match = crosswalk[
            crosswalk["plfs_sequential_code"].astype("Int64") == int(dist_code)
        ]
        dist_name = (
            cw_match["canonical_name"].values[0]
            if len(cw_match) > 0
            else f"UNKNOWN_{dist_code}"
        )

        results.append({
            "district_code":    dist_code,
            "district_name":    dist_name,
            "state_code":       state_code,
            "survey_year":      year,
            "n_rural_persons":  n_total,
            "n_employed":       n_emp,
            "employed_weight":  round(w_total, 1),
            "unemp_rate_wt":    round(unemp_rate, 2) if unemp_rate is not None else None,
            "agri_share_wt":    round(agri_share, 2) if agri_share is not None else None,
            "nonagri_share_wt": round(nonagri_share, 2) if nonagri_share is not None else None,
            "services_share":   round(svc_share, 2) if svc_share is not None else None,
            "edu_secondary_wt": round(edu_share, 2) if edu_share is not None else None,
            "log_wage_median":  round(log_wage_median, 4) if log_wage_median is not None else None,
            "wage_n":           wage_n,
            "sample_grade":     get_sample_grade(n_emp),
            "data_status":      "REAL",
            "schema_version":   SCHEMA_VERSION,
        })

    return pd.DataFrame(results)


def main(year: int, state_code: int, zip_override: str = None):
    print(f"\n{'='*60}")
    print(f"AIRIS PLFS Panel Builder — Year: {year}, State: {state_code}")
    print(f"{'='*60}")

    # Locate ZIP
    if zip_override:
        zip_path = Path(zip_override)
    else:
        # Try multiple naming conventions:
        # - *2019*.zip (e.g. PLFS_Annual_2019.zip)
        # - *19_20*.zip (e.g. CSV_PLFS_19_20.zip)
        # - *2021-22*.zip (e.g. PLFS_Data_2021-22_CSV.zip)
        short_year = str(year)[2:]                     # "19" for 2019, "21" for 2021
        next_short = str(year + 1)[2:]                 # "20" for 2019, "22" for 2021
        candidates = (
            list(DATA_DIR.glob(f"*{year}*.zip")) +
            list(DATA_DIR.glob(f"*{short_year}_{next_short}*.zip")) +
            list(DATA_DIR.glob(f"*{year}-{year+1}*.zip")) +
            list(DATA_DIR.glob(f"*{year}-{next_short}*.zip"))
        )
        if not candidates:
            raise FileNotFoundError(
                f"No PLFS ZIP for {year} found in {DATA_DIR}.\n"
                f"Tried patterns: *{year}*, *{short_year}_{next_short}*, *{year}-{next_short}*\n"
                f"Available ZIPs: {list(DATA_DIR.glob('*.zip'))}\n"
                f"Download from microdata.gov.in → PLFS Annual {year}-{str(year+1)[2:]}"
            )
        zip_path = candidates[0]
    print(f"  ZIP: {zip_path}")

    # Load crosswalk
    crosswalk = pd.read_csv(CROSSWALK_FILE)
    print(f"  Crosswalk: {len(crosswalk)} districts loaded")

    # Load and normalise
    df = load_plfs_rural(zip_path, year)
    print(f"  Raw records: {len(df):,} | Columns: {len(df.columns)}")
    df = normalise_columns(df, year)

    # Compute stats
    panel = compute_district_stats(df, state_code, year, crosswalk)

    # Save
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"plfs_panel_state{state_code}_{year}.csv"
    panel.to_csv(out, index=False)

    # Report
    print(f"\nDistricts extracted: {len(panel)}")
    print(f"Grade A/B/C (n≥200): {len(panel[panel['sample_grade'].isin(['A','B','C'])])}")
    print(f"Grade D (n<200):     {len(panel[panel['sample_grade']=='D'])}")
    print(f"\n{panel[['district_name','survey_year','n_employed','unemp_rate_wt','agri_share_wt','nonagri_share_wt','sample_grade']].to_string(index=False)}")
    print(f"\nSaved: {out}")
    return panel


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIRIS PLFS Panel Builder")
    parser.add_argument("--year",       type=int, default=2023, help="Survey start year (e.g. 2019, 2023)")
    parser.add_argument("--state_code", type=int, default=29,   help="PLFS state code (29=Karnataka)")
    parser.add_argument("--zip",        type=str, default=None, help="Override ZIP path")
    args = parser.parse_args()
    main(args.year, args.state_code, args.zip)
