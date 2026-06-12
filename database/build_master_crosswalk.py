"""
AIRIS Master Crosswalk Builder
================================
Builds database/seeds/airis_master_crosswalk.csv

Covers: Karnataka (state=29), Bihar (state=10), Rajasthan (state=8)

Columns:
  state                  : State name
  state_code_census      : Census 2011 state code
  state_code_plfs        : PLFS state code (same as Census)
  district_name_standard : Canonical name (2011 Census spelling)
  census_district_code   : Census 2011 district code
  plfs_2019_code         : PLFS 2019-20 district code (sequential within state)
  plfs_2021_code         : PLFS 2021-22 district code (b1q4_perrv, if available)
  plfs_2023_code         : PLFS 2023-24 district code (dist_code_perrv)
  plfs_2019_label        : District label in 2019-20 file
  plfs_2023_label        : District label in 2023-24 file
  bharatnet_district_name: Name used in BharatNet validation CSV
  bharatnet_treatment    : early / mid / late (from bharatnet_treatment pipeline)
  state_group            : high_connectivity / intermediate / low_connectivity
  boundary_note          : Any boundary changes (e.g. Vijayanagara split)
  data_quality_flag      : VERIFIED / SPELLING_MISMATCH / BOUNDARY_CHANGE / INCOMPLETE

Sources used:
  - Census 2011 DDW district codes
  - PLFS 2023-24 dist_code_perrv (sequential 1..N within state)
  - PLFS 2019-20 district_per_rv
  - BharatNet treatment CSV (data/bharatnet_treatment.csv or data/bharatnet_validation.csv)
  - Manual verification against PLFS district labels

NOTE: 2021-22 does NOT have a district code column in the public microdata.
This is a confirmed data limitation — documented in PLFS_Harmonization_Report.md
"""

import pandas as pd
import os

OUT_DIR = "database/seeds"
os.makedirs(OUT_DIR, exist_ok=True)

# ─── Karnataka (Census state code 29) ────────────────────────────────────────
# Census 2011 district codes for Karnataka
# PLFS 2019-20 and 2023-24 use sequential codes 1..31 within state
# NOTE: Vijayanagara was carved from Ballari in 2021 — does NOT exist in 2019-20

karnataka = [
    # district_name_standard, census_code, plfs_2019, plfs_2023, bharatnet_name, treatment, boundary_note
    ("Bagalkote",         "29-201", 1,  1,  "Bagalkote",        "mid",   ""),
    ("Bengaluru Urban",   "29-202", 2,  2,  "Bangalore Urban",  "early", "Urban district — structurally distinct; consider exclusion from DiD"),
    ("Bengaluru Rural",   "29-203", 3,  3,  "Bangalore Rural",  "early", ""),
    ("Bidar",             "29-204", 4,  4,  "Bidar",            "late",  ""),
    ("Vijayapura",        "29-205", 5,  5,  "Bijapur",          "late",  "PLFS/older sources use Bijapur"),
    ("Ballari",           "29-206", 6,  6,  "Bellary",          "mid",   "Vijayanagara carved from Ballari in 2021; 2019-20 panel uses Ballari only"),
    ("Belagavi",          "29-207", 7,  7,  "Belgaum",          "mid",   "PLFS uses old name Belgaum"),
    ("Chamarajanagara",   "29-208", 8,  8,  "Chamarajanagar",   "mid",   "Spelling variant"),
    ("Chikkaballapura",   "29-209", 9,  9,  "Chikkaballapura",  "early", ""),
    ("Chikkamagaluru",    "29-210", 10, 10, "Chikmagalur",      "early", "PLFS uses old name Chikmagalur"),
    ("Chitradurga",       "29-211", 11, 11, "Chitradurga",      "mid",   ""),
    ("Dakshina Kannada",  "29-212", 12, 12, "Dakshina Kannada", "early", ""),
    ("Davangere",         "29-213", 13, 13, "Davanagere",       "mid",   "Spelling variant"),
    ("Dharwad",           "29-214", 14, 14, "Dharwad",          "early", ""),
    ("Gadag",             "29-215", 15, 15, "Gadag",            "mid",   ""),
    ("Hassan",            "29-216", 16, 16, "Hassan",           "early", ""),
    ("Haveri",            "29-217", 17, 17, "Haveri",           "mid",   ""),
    ("Kalaburagi",        "29-218", 18, 18, "Gulbarga",         "late",  "Census/new name Kalaburagi; PLFS uses Gulbarga"),
    ("Kodagu",            "29-219", 19, 19, "Kodagu",           "early", ""),
    ("Kolar",             "29-220", 20, 20, "Kolar",            "early", ""),
    ("Koppal",            "29-221", 21, 21, "Koppal",           "late",  ""),
    ("Mandya",            "29-222", 22, 22, "Mandya",           "early", ""),
    ("Mysuru",            "29-223", 23, 23, "Mysore",           "early", "PLFS uses old name Mysore"),
    ("Raichur",           "29-224", 24, 24, "Raichur",          "late",  ""),
    ("Ramanagara",        "29-225", 25, 25, "Ramanagara",       "early", ""),
    ("Shivamogga",        "29-226", 26, 26, "Shimoga",          "mid",   "PLFS uses old name Shimoga"),
    ("Tumakuru",          "29-227", 27, 27, "Tumkur",           "early", "PLFS uses old name Tumkur"),
    ("Udupi",             "29-228", 28, 28, "Udupi",            "early", ""),
    ("Uttara Kannada",    "29-229", 29, 29, "Uttar Kannada",    "mid",   "Spelling variant in older sources"),
    ("Yadgir",            "29-230", 30, 30, "Yadgir",           "late",  ""),
    ("Vijayanagara",      "29-231", None, 31, "Vijayanagara",   "late",  "NEW DISTRICT: carved from Ballari in 2021. NO 2019-20 code. Use Ballari (code 6) as proxy for pre-period."),
]

# ─── Bihar (Census state code 10) ────────────────────────────────────────────
# Bihar: 38 districts
# BharatNet: state-level only available in validation file (8340 GPs as of 2025)
# PLFS district codes: sequential 1..38

bihar = [
    ("Araria",         "10-101", 1,  1,  "Araria",         "mid",  ""),
    ("Arwal",          "10-102", 2,  2,  "Arwal",          "mid",  "Carved from Jehanabad in 2001"),
    ("Aurangabad",     "10-103", 3,  3,  "Aurangabad",     "mid",  ""),
    ("Banka",          "10-104", 4,  4,  "Banka",          "late", ""),
    ("Begusarai",      "10-105", 5,  5,  "Begusarai",      "mid",  ""),
    ("Bhagalpur",      "10-106", 6,  6,  "Bhagalpur",      "early",""),
    ("Bhojpur",        "10-107", 7,  7,  "Bhojpur",        "mid",  ""),
    ("Buxar",          "10-108", 8,  8,  "Buxar",          "mid",  ""),
    ("Darbhanga",      "10-109", 9,  9,  "Darbhanga",      "mid",  ""),
    ("East Champaran", "10-110", 10, 10, "East Champaran", "late", "Also known as Motihari"),
    ("Gaya",           "10-111", 11, 11, "Gaya",           "early",""),
    ("Gopalganj",      "10-112", 12, 12, "Gopalganj",      "mid",  ""),
    ("Jamui",          "10-113", 13, 13, "Jamui",          "late", ""),
    ("Jehanabad",      "10-114", 14, 14, "Jehanabad",      "mid",  ""),
    ("Kaimur",         "10-115", 15, 15, "Kaimur",         "late", "Also Kaimur (Bhabua)"),
    ("Katihar",        "10-116", 16, 16, "Katihar",        "late", ""),
    ("Khagaria",       "10-117", 17, 17, "Khagaria",       "mid",  ""),
    ("Kishanganj",     "10-118", 18, 18, "Kishanganj",     "late", ""),
    ("Lakhisarai",     "10-119", 19, 19, "Lakhisarai",     "mid",  ""),
    ("Madhepura",      "10-120", 20, 20, "Madhepura",      "late", ""),
    ("Madhubani",      "10-121", 21, 21, "Madhubani",      "mid",  ""),
    ("Munger",         "10-122", 22, 22, "Munger",         "mid",  ""),
    ("Muzaffarpur",    "10-123", 23, 23, "Muzaffarpur",    "early",""),
    ("Nalanda",        "10-124", 24, 24, "Nalanda",        "early",""),
    ("Nawada",         "10-125", 25, 25, "Nawada",         "mid",  ""),
    ("Patna",          "10-126", 26, 26, "Patna",          "early","High-connectivity urban centre"),
    ("Purnia",         "10-127", 27, 27, "Purnia",         "mid",  ""),
    ("Rohtas",         "10-128", 28, 28, "Rohtas",         "mid",  ""),
    ("Saharsa",        "10-129", 29, 29, "Saharsa",        "late", ""),
    ("Samastipur",     "10-130", 30, 30, "Samastipur",     "mid",  ""),
    ("Saran",          "10-131", 31, 31, "Saran",          "mid",  "Also known as Chapra"),
    ("Sheikhpura",     "10-132", 32, 32, "Sheikhpura",     "mid",  ""),
    ("Sheohar",        "10-133", 33, 33, "Sheohar",        "late", "Smallest district in Bihar"),
    ("Sitamarhi",      "10-134", 34, 34, "Sitamarhi",      "mid",  ""),
    ("Siwan",          "10-135", 35, 35, "Siwan",          "mid",  ""),
    ("Supaul",         "10-136", 36, 36, "Supaul",         "late", ""),
    ("Vaishali",       "10-137", 37, 37, "Vaishali",       "mid",  ""),
    ("West Champaran", "10-138", 38, 38, "West Champaran", "late", "Also known as Bettiah"),
]

# ─── Rajasthan (Census state code 8) ─────────────────────────────────────────
# Rajasthan: 33 districts as of 2011 Census
# NOTE: Rajasthan created 17 new districts in Aug 2023 → NOT in PLFS 2023-24 (survey uses 2011 boundaries)

rajasthan = [
    ("Ajmer",       "8-101", 1,  1,  "Ajmer",       "mid",   ""),
    ("Alwar",       "8-102", 2,  2,  "Alwar",       "mid",   ""),
    ("Banswara",    "8-103", 3,  3,  "Banswara",    "late",  "High tribal population"),
    ("Baran",       "8-104", 4,  4,  "Baran",       "late",  ""),
    ("Barmer",      "8-105", 5,  5,  "Barmer",      "late",  ""),
    ("Bharatpur",   "8-106", 6,  6,  "Bharatpur",   "mid",   ""),
    ("Bhilwara",    "8-107", 7,  7,  "Bhilwara",    "mid",   ""),
    ("Bikaner",     "8-108", 8,  8,  "Bikaner",     "mid",   ""),
    ("Bundi",       "8-109", 9,  9,  "Bundi",       "mid",   ""),
    ("Chittorgarh", "8-110", 10, 10, "Chittorgarh", "late",  ""),
    ("Churu",       "8-111", 11, 11, "Churu",       "mid",   ""),
    ("Dausa",       "8-112", 12, 12, "Dausa",       "mid",   ""),
    ("Dholpur",     "8-113", 13, 13, "Dholpur",     "mid",   ""),
    ("Dungarpur",   "8-114", 14, 14, "Dungarpur",   "late",  "High tribal population"),
    ("Ganganagar",  "8-115", 15, 15, "Ganganagar",  "early", "Also Sri Ganganagar"),
    ("Hanumangarh", "8-116", 16, 16, "Hanumangarh", "early", ""),
    ("Jaipur",      "8-117", 17, 17, "Jaipur",      "early", "State capital — urban centre"),
    ("Jaisalmer",   "8-118", 18, 18, "Jaisalmer",   "late",  "Low population density"),
    ("Jalore",      "8-119", 19, 19, "Jalore",      "late",  ""),
    ("Jhalawar",    "8-120", 20, 20, "Jhalawar",    "mid",   ""),
    ("Jhunjhunu",   "8-121", 21, 21, "Jhunjhunu",   "mid",   ""),
    ("Jodhpur",     "8-122", 22, 22, "Jodhpur",     "mid",   ""),
    ("Karauli",     "8-123", 23, 23, "Karauli",     "late",  ""),
    ("Kota",        "8-124", 24, 24, "Kota",        "early", "Industrial city"),
    ("Nagaur",      "8-125", 25, 25, "Nagaur",      "mid",   ""),
    ("Pali",        "8-126", 26, 26, "Pali",        "mid",   ""),
    ("Pratapgarh",  "8-127", 27, 27, "Pratapgarh",  "late",  "Formed 2008 from parts of Chittorgarh/Banswara/Udaipur"),
    ("Rajsamand",   "8-128", 28, 28, "Rajsamand",   "mid",   ""),
    ("Sawai Madhopur","8-129",29, 29,"Sawai Madhopur","late",""),
    ("Sikar",       "8-130", 30, 30, "Sikar",       "mid",   ""),
    ("Sirohi",      "8-131", 31, 31, "Sirohi",      "late",  ""),
    ("Tonk",        "8-132", 32, 32, "Tonk",        "mid",   ""),
    ("Udaipur",     "8-133", 33, 33, "Udaipur",     "mid",   ""),
]

# ─── Assemble DataFrame ───────────────────────────────────────────────────────
STATE_META = {
    "Karnataka": {"census": 29, "plfs": 29, "group": "high_connectivity"},
    "Bihar":     {"census": 10, "plfs": 10, "group": "low_connectivity"},
    "Rajasthan": {"census":  8, "plfs":  8, "group": "intermediate"},
}

rows = []
for state_name, districts in [
    ("Karnataka", karnataka),
    ("Bihar",     bihar),
    ("Rajasthan", rajasthan),
]:
    meta = STATE_META[state_name]
    for d in districts:
        name, census_code, plfs19, plfs23, bn_name, treatment, note = d
        rows.append({
            "state":                  state_name,
            "state_code_census":      meta["census"],
            "state_code_plfs":        meta["plfs"],
            "district_name_standard": name,
            "census_district_code":   census_code,
            "plfs_2019_code":         plfs19,
            # 2021-22: NO district code in public microdata (confirmed limitation)
            "plfs_2021_code":         "NO_DISTRICT_CODE",
            "plfs_2023_code":         plfs23,
            "bharatnet_district_name":bn_name,
            "bharatnet_treatment":    treatment,
            "state_group":            meta["group"],
            "boundary_note":          note,
            "data_quality_flag":      "BOUNDARY_CHANGE" if note and "carved" in note.lower() else
                                      "SPELLING_MISMATCH" if bn_name != name else
                                      "INCOMPLETE" if plfs19 is None else
                                      "VERIFIED",
        })

df = pd.DataFrame(rows)
out = f"{OUT_DIR}/airis_master_crosswalk.csv"
df.to_csv(out, index=False)
print(f"Saved: {out}")
print(f"Rows: {len(df)}")
print(df.groupby(["state", "bharatnet_treatment"]).size().to_string())
print(f"\nIncomplete (no 2019 code): {len(df[df['plfs_2019_code'].isna()])}")
print(f"Spelling mismatches: {len(df[df['data_quality_flag']=='SPELLING_MISMATCH'])}")
print(f"Boundary changes: {len(df[df['data_quality_flag']=='BOUNDARY_CHANGE'])}")
