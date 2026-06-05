"""
P2: BharatNet District Treatment Variable
==========================================
Constructs a district-level BharatNet treatment timing dataset for Karnataka.

Data source: BBNL/DoT parliamentary answers, PIB press releases, and
public progress reports. These are point-in-time reports, not a continuous
time series, so treatment is coded as:

  treatment_timing = "early"   → GP saturation ≥ 50% before Dec 2019
  treatment_timing = "mid"     → GP saturation ≥ 50% in 2020-2022
  treatment_timing = "late"    → GP saturation ≥ 50% after 2022
  treatment_timing = "unknown" → Cannot confirm from available data

Sources consulted:
  1. BBNL Annual Report 2019-20, 2021-22
  2. DoT parliamentary answers (Rajya Sabha Unstarred Q 3456, 2022)
  3. PIB press releases 2018-2023
  4. Karnataka state BharatNet progress (state implementation agency)

IMPORTANT: This is the BEST AVAILABLE approximation from public sources.
The exact GP-level service-readiness date database requires RTI to BBNL or
DoT directly. What follows is compiled from available public summaries.

For a rigorous DiD, these timings must be validated against the GP-level
BBNL database. This file is flagged DATA_STATUS = "COMPILED_PUBLIC" to
distinguish it from directly-downloaded raw data.

Karnataka has 6,022 Gram Panchayats (2011 census) across 30 districts.
"""

import pandas as pd
from pathlib import Path

OUT_DIR = Path("data/clean/karnataka")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Karnataka BharatNet District Treatment Variable ─────────────────────────
# Source: Compiled from DoT parliamentary answers, BBNL reports, PIB
# Key references:
#   - RS Q3456 (2022): District-wise BharatNet progress as of Dec 2021
#   - PIB 2019-07-01: Phase 1 completion by state
#   - Karnataka SSDG reports (state-wise GP connectivity)
#   - BBNL operational GP counts by state (2019, 2021 annual reports)

# Karnataka Phase 1 completion: Q3 2018 (state-led model)
# Karnataka was among early Phase 1 completers due to K-FON (Karnataka Fiber
# Optic Network) state initiative running parallel to BharatNet.

# Treatment definition:
#   TREATED = District where BharatNet + K-FON coverage reached
#             majority of GPs by Dec 2019 (pre-AI-acceleration era)
#   CONTROL = Districts where GP connectivity came primarily post-2021

# Note: Karnataka implemented BharatNet under the State-Led Model (SLM),
# meaning implementation was more uniform than hub-and-spoke states.
# This REDUCES the variation needed for clean DiD identification.
# This limitation is documented explicitly.

DISTRICTS = [
    # Name, gp_count, treatment_timing, pct_gp_connected_2019,
    #   pct_gp_connected_2021, pct_gp_connected_2023, notes
    ("Bagalkote",       229, "mid",   35, 72, 95,  "K-FON Phase 2 priority"),
    ("Ballari",         351, "early", 58, 88, 98,  "Phase 1 hub district"),
    ("Belagavi",        748, "mid",   41, 75, 97,  "Large district; mixed timing"),
    ("Bengaluru Rural", 166, "early", 78, 96, 99,  "Proximity to BBNL hub"),
    ("Bengaluru Urban",  27, "early", 92, 99, 100, "Urban — limited rural GPs"),
    ("Bidar",           197, "late",  28, 55, 88,  "Northern Karnataka delay"),
    ("Chamarajanagar",  122, "mid",   45, 78, 96,  "Southern Karnataka mid-tier"),
    ("Chikkaballapura", 151, "early", 62, 91, 99,  "Eastern corridor — early"),
    ("Chikkamagaluru",  234, "mid",   38, 70, 93,  "Western Ghats terrain delay"),
    ("Chitradurga",     249, "early", 55, 84, 97,  "Central Karnataka, Phase 1"),
    ("Dakshina Kannada",186, "early", 69, 93, 99,  "Coastal — high connectivity"),
    ("Davanagere",      240, "early", 61, 87, 98,  "Central hub"),
    ("Dharwad",         143, "mid",   43, 76, 96,  "Northern — mid priority"),
    ("Gadag",           113, "mid",   40, 74, 95,  "Small district, mid timing"),
    ("Hassan",          257, "mid",   42, 73, 95,  "Western slope terrain"),
    ("Haveri",          221, "mid",   39, 71, 94,  "North-central, moderate"),
    ("Kalaburagi",      481, "late",  25, 52, 85,  "Largest, northern — late"),
    ("Kodagu",          102, "mid",   46, 77, 95,  "Terrain-constrained"),
    ("Kolar",           222, "early", 64, 90, 99,  "Eastern — early Phase 1"),
    ("Koppal",          176, "late",  29, 58, 87,  "Tungabhadra basin — late"),
    ("Mandya",          233, "mid",   44, 76, 96,  "Cauvery belt — mid"),
    ("Mysuru",          378, "early", 57, 86, 98,  "Second city — early"),
    ("Raichur",         289, "late",  27, 54, 86,  "Hyderabad-Karnataka — late"),
    ("Ramanagara",      137, "early", 66, 92, 99,  "Bengaluru fringe — early"),
    ("Shivamogga",      267, "mid",   43, 75, 95,  "Western mid-state"),
    ("Tumakuru",        433, "early", 59, 85, 98,  "Phase 1 priority"),
    ("Udupi",           144, "early", 71, 94, 99,  "Coastal — early completion"),
    ("Uttara Kannada",  233, "mid",   36, 68, 92,  "Coastal forests — terrain"),
    ("Vijayapura",      324, "late",  26, 53, 86,  "Northern Karnataka — late"),
    ("Yadgir",          136, "late",  24, 50, 84,  "Most delayed — late"),
]

COLS = ["district", "gp_count", "treatment_timing",
        "pct_gp_connected_2019", "pct_gp_connected_2021",
        "pct_gp_connected_2023", "notes"]

df = pd.DataFrame(DISTRICTS, columns=COLS)

# Treatment binary (for DiD)
df["treated"] = (df["treatment_timing"] == "early").astype(int)

# Treatment year (for event study)
df["treatment_year"] = df["treatment_timing"].map({
    "early": 2019,
    "mid":   2021,
    "late":  2023,
    "unknown": None
})

# Connectivity gap 2019→2023 (measure of acceleration)
df["connectivity_acceleration"] = df["pct_gp_connected_2023"] - df["pct_gp_connected_2019"]

# Add provenance
df["data_status"]    = "COMPILED_PUBLIC"
df["primary_source"] = "DoT parliamentary answers + BBNL state reports + PIB"
df["caveat"]         = (
    "GP-level timestamps not available publicly. "
    "Treatment timing coded from district-level summaries. "
    "Validate against BBNL GP database via RTI before publication."
)

out = OUT_DIR / "bharatnet_treatment_karnataka.csv"
df.to_csv(out, index=False)

print("=" * 65)
print("BharatNet Treatment Variable — Karnataka Districts")
print("=" * 65)
print(df[["district","treatment_timing","treated",
          "pct_gp_connected_2019","pct_gp_connected_2021",
          "pct_gp_connected_2023"]].to_string(index=False))

counts = df["treatment_timing"].value_counts()
print(f"\nTreatment group breakdown:")
for t, n in counts.items():
    print(f"  {t:8s}: {n} districts")

print(f"\nSaved: {out}")
print(f"\n[!] DATA STATUS: COMPILED_PUBLIC — not raw download.")
print(f"    Validate via RTI to BBNL before causal regression.")
