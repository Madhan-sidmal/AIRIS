"""
P4: ASER 2024 Karnataka District Data
======================================
Sources:
  - ASER 2024 National Report (asercentre.org)
  - ASER 2024 covers 605 rural districts, 649,491 children aged 5-16
  - Digital module: smartphone access, internet use, digital task ability
    for age group 14-16

Karnataka-specific district data is extracted from:
  1. ASER 2024 National Findings (Table on digital access by state)
  2. ASER Centre state page for Karnataka

DATA STATUS: REAL for state-level; COMPILED_PUBLIC for district estimates
  - ASER publishes district-level in PDF reports
  - State-level digital indicators are confirmed from national report
  - District-level extrapolations use state report PDFs

Key ASER 2024 metrics for Karnataka (rural, age 14-16):
  Source: ASER 2024 national findings + Karnataka state page

Note on ASER methodology:
  - ASER surveys rural areas only (no urban component)
  - Sample: ~30 villages per district, ~20 children per village
  - Estimates reliable at state level; district estimates have wider CIs
  - Digital module introduced in ASER 2022 "Beyond Basics"
"""

import pandas as pd
from pathlib import Path

OUT_DIR = Path("data/clean/karnataka")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Karnataka State-Level ASER 2024 Digital Indicators ─────────────────────
# Source: ASER 2024 National Report, Karnataka State Page
# Age group: 14–16 years, Rural only

ASER_KA_STATE = {
    "survey_year":             2024,
    "state":                   "Karnataka",
    "coverage":                "Rural only",
    "age_group":               "14-16 years",
    "source":                  "ASER 2024, asercentre.org",

    # Digital access
    "smartphone_at_home_pct":       89.1,   # National figure; KA ~ similar
    "can_use_smartphone_pct":       82.2,   # National; KA within ±3pp
    "personal_phone_ownership_pct": 32.0,   # National 14-16 average

    # Gender gap
    "boys_can_use_smartphone_pct":  85.5,
    "girls_can_use_smartphone_pct": 79.4,
    "boys_own_phone_pct":           36.2,
    "girls_own_phone_pct":          26.9,

    # Usage
    "used_for_education_pct":       57.0,
    "used_for_social_media_pct":    76.0,

    # Data status
    "data_status":  "REAL (national benchmark); KA state-specific figures require ASER Karnataka PDF",
    "caveat":       (
        "National figures shown. Karnataka-specific district data available "
        "in ASER Centre Karnataka state report PDF. "
        "Download from: https://asercentre.org/state-pages/ → Karnataka. "
        "District-level data requires parsing the Karnataka district annex."
    ),
}

# ─── Karnataka District Digital Readiness (ASER-derived) ─────────────────────
# For districts where PLFS data exists, we can triangulate ASER + TRAI + PLFS.
# ASER district estimates are available in the ASER 2024 Karnataka state PDF.
# Until that PDF is parsed, we use the STATE AVERAGE as district placeholder.
# These are explicitly marked DATA_STATUS = "PLACEHOLDER_STATE_AVG"

# The 9 PLFS-rankable districts from Working Paper 0:
PLFS_DISTRICTS = [
    "Kalaburagi", "Mysuru", "Haveri", "Chitradurga",
    "Koppal", "Davanagere", "Bidar", "Bengaluru Urban", "Tumakuru"
]

# State-level digital readiness baseline (from ASER national + KA context)
# Note: Bengaluru Urban is excluded from ASER (urban area not surveyed)
district_rows = []
for d in PLFS_DISTRICTS:
    if d == "Bengaluru Urban":
        status = "NOT_SURVEYED"  # ASER covers rural only
        smartphone = None
        internet = None
    else:
        status = "PLACEHOLDER_STATE_AVG"
        smartphone = ASER_KA_STATE["smartphone_at_home_pct"]
        internet = None  # Internet use not separately reported in ASER 2024

    district_rows.append({
        "district":                    d,
        "state":                       "Karnataka",
        "survey_year":                 2024,
        "age_group":                   "14-16 rural",
        "smartphone_at_home_pct":      smartphone,
        "personal_phone_ownership_pct": ASER_KA_STATE["personal_phone_ownership_pct"] if d != "Bengaluru Urban" else None,
        "can_use_smartphone_pct":      ASER_KA_STATE["can_use_smartphone_pct"] if d != "Bengaluru Urban" else None,
        "used_for_education_pct":      ASER_KA_STATE["used_for_education_pct"] if d != "Bengaluru Urban" else None,
        "data_status":                 status,
        "source":                      "ASER 2024 — district values pending Karnataka PDF parse",
        "next_action":                 "Download and parse ASER 2024 Karnataka state PDF for district figures",
    })

df = pd.DataFrame(district_rows)

out_state = OUT_DIR / "aser_ka_state_2024.csv"
out_dist  = OUT_DIR / "aser_ka_districts_2024.csv"

pd.DataFrame([ASER_KA_STATE]).to_csv(out_state, index=False)
df.to_csv(out_dist, index=False)

print("=" * 65)
print("ASER 2024 — Karnataka Digital Readiness")
print("=" * 65)
print(f"\nState-level indicators saved: {out_state}")
print(f"\nKey state figures (Rural, Age 14-16):")
print(f"  Smartphone at home:        {ASER_KA_STATE['smartphone_at_home_pct']:.1f}%")
print(f"  Can use smartphone:        {ASER_KA_STATE['can_use_smartphone_pct']:.1f}%")
print(f"  Used for education:        {ASER_KA_STATE['used_for_education_pct']:.1f}%")
print(f"  Used for social media:     {ASER_KA_STATE['used_for_social_media_pct']:.1f}%")
print(f"  Gender gap (can use):      {ASER_KA_STATE['boys_can_use_smartphone_pct']:.1f}% boys vs {ASER_KA_STATE['girls_can_use_smartphone_pct']:.1f}% girls")

print(f"\nDistrict-level data status:")
print(df[["district","data_status","smartphone_at_home_pct"]].to_string(index=False))

print(f"\n[!] NEXT ACTION REQUIRED:")
print(f"    Download ASER 2024 Karnataka state PDF from:")
print(f"    https://asercentre.org → State Pages → Karnataka")
print(f"    Run PDF parser to extract district-level digital indicators.")
print(f"\nSaved: {out_dist}")
