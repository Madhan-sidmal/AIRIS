# PLFS Harmonization Report
## AIRIS Phase 3 — Pre-Analysis Data Verification
### Version 1.0 | June 2026

> [!IMPORTANT]
> This report documents confirmed variable-level incompatibilities between PLFS rounds. No district-year panel should be constructed until every item in Section 7 is resolved.

---

## 1. Files Audited

| Round | ZIP Filename | Rural Persons File | Records (All India) | Karnataka Records |
|---|---|---|---|---|
| 2019-20 | `CSV_PLFS_19_20.zip` | `CSV_PLFS_19_20/PERRV_2019-20.csv` | 523,163 | 24,859 |
| 2021-22 | `PLFS_Data_2021-22_CSV.zip` | `PLFS_Data_2021-22_CSV/perrv.csv` | 511,361 | 24,944 |
| 2023-24 | `CSV_data_PLFS_2023_2024.zip` | `CSV_data_PLFS_2023_2024/perrv.csv` | 504,440 | 23,400 |

All three files contain 104 columns. Column names differ systematically between 2019-20 (`_per_rv` suffix) and 2021-22/2023-24 (`_perrv` suffix).

---

## 2. Column Naming Convention Changes

| Variable | 2019-20 Column | 2021-22 Column | 2023-24 Column | Notes |
|---|---|---|---|---|
| **State code** | `state_per_rv` | `state_perrv` | `state_perrv` | Numeric, consistent codes |
| **District code** | `district_per_rv` | `b1q4_perrv` | `dist_code_perrv` | ⚠️ Different column names across all 3 rounds |
| **Multiplier weight** | `MULT_per_rv` | `mult_perrv` | `mult_perrv` | Case differs in 2019-20 |
| **Activity status** | `b4q4_per_rv` | `b4q4_perrv` | `b4q4_perrv` | |
| **Broad sector** | `b4q5_per_rv` | `b4q5_perrv` | `b4q5_perrv` | See Section 4 |
| **NIC 2-digit** | `b4q6_per_rv` | `b4q6_perrv` | `b4q6_perrv` | See Section 5 |
| **Education level** | `b2q7_per_rv` | `b2q7_perrv` | `b2q7_perrv` | |
| **Wage earnings** | `b6q5_3pt1_Act1_per_rv` | `b6q5_3pt1_perrv` | `b6q5_3pt1_perrv` | Column name differs in 2019-20 |

---

## 3. District Code Availability

> [!CAUTION]
> The 2021-22 round does NOT contain a dedicated district code column in its public microdata. This is the most critical harmonization issue.

| Round | District Column | Values | Districts (Karnataka) | Notes |
|---|---|---|---|---|
| 2019-20 | `district_per_rv` | 1–30 | 30 districts | Sequential within state |
| **2021-22** | **`b1q4_perrv`** | **1–30** | **30 districts** | ⚠️ This is NOT documented as the district column in the PLFS 2021-22 codebook. It produces 30 unique values for Karnataka matching the 30 districts that existed before Vijayanagara was carved in Aug 2021. Verified by record count per code — plausible distribution. **Treat as PROBABLE_DISTRICT_CODE until codebook confirms.** |
| 2023-24 | `dist_code_perrv` | 1–31 | 31 districts | Includes Vijayanagara (code 31) |

**Action required before regression:** Verify that `b1q4_perrv` in 2021-22 is the district code by cross-referencing with PLFS 2021-22 Annual Report Table 1 (district-level sample counts).

---

## 4. Activity Status Coding

> [!NOTE]
> All three rounds use the SAME 1-digit activity status coding (1–9). The 2-digit coding (11–71) used in pre-2017 PLFS rounds is NOT present in any of the three rounds covered by this panel.

| Code | Meaning | Employment Status |
|---|---|---|
| 1 | Self-employed: Employer | Employed |
| 2 | Self-employed: Own Account | Employed |
| 3 | Self-employed: Unpaid Helper | Employed |
| 4 | Regular Wage/Salary | Employed |
| 5 | Casual Wage | Employed |
| 6 | Seeking/Available for work (Unemployed) | Unemployed |
| 7 | Domestic duties only | Not in Labour Force |
| 8 | Attending educational institution | Not in Labour Force |
| 9 | Other (including aged/infirm) | Not in Labour Force |

**Employed persons (for panel):** Codes 1–5  
**Unemployed (for unemployment rate):** Code 6  
**Labour force (denominator for UER):** Codes 1–6  
**Wage workers (for wage estimation):** Codes 4–5

---

## 5. Sector / Industry Coding

> [!CAUTION]
> **Root cause of the `agri_share = 100%` bug:** The column `b4q5_perrv` was incorrectly assumed to be an NIC industry code. It is actually the broad sector flag.

### 5.1 `b4q5` — Broad Sector Flag

| Value | Sector | Comparable to |
|---|---|---|
| 1 | Agriculture, Forestry, and Fishing | NIC-2 codes 01–03 |
| 2 | Industry (Mining, Manufacturing, Utilities, Construction) | NIC-2 codes 05–43 |
| 3 | Services (all other) | NIC-2 codes 45–99 |

This coding is **identical** across all three rounds. Use `b4q5` for the primary sector split in the DiD panel.

### 5.2 `b4q6` — NIC 2-Digit Industry Code

Range in 2021-22 Karnataka: 0–96 (over 90 unique values).  
Range in 2023-24 Karnataka: 0–96.  
Range in 2019-20 Karnataka: 0–96.

> [!NOTE]
> NIC code 0 (zero) appears in all rounds. This represents "not applicable" (e.g., for unemployed or non-working persons). Filter to employed persons (codes 1–5) before computing NIC-based sector shares.

Use `b4q6` only for finer-grained services sub-splits (e.g., IT sector: NIC 62–63; Financial Services: NIC 64–66). Do not use for the primary agri/non-agri split.

---

## 6. Wage Column

| Round | Weekly Earnings Column | Notes |
|---|---|---|
| 2019-20 | `b6q5_3pt1_Act1_per_rv` | Long column name; same semantic content |
| 2021-22 | `b6q5_3pt1_perrv` | Simplified name |
| 2023-24 | `b6q5_3pt1_perrv` | Identical to 2021-22 |

**Condition wage estimation on:** Wage workers (activity codes 4–5) only.  
**Unit:** Weekly earnings in rupees.  
**Median log transformation** is the preferred approach for DiD (less sensitive to top-tail outliers in small district samples).

---

## 7. Boundary Changes

| Change | Date | Impact on Panel |
|---|---|---|
| **Vijayanagara carved from Ballari** | Aug 2021 | PLFS 2021-22 has 30 Karnataka districts (Vijayanagara had just been formed and is not yet in the PLFS sample frame). PLFS 2023-24 has 31 districts. For the 2×2 DiD (2019-20 vs 2023-24), use Ballari (code 6) as the 2019-20 proxy for the Ballari+Vijayanagara combined area. |
| **Rajasthan 17 new districts** | Aug 2023 | Rajasthan created 17 new districts from existing ones. PLFS 2023-24 likely uses pre-split boundaries (survey frames lag administrative changes). **Verify against PLFS 2023-24 Rajasthan district count before regression.** |

---

## 8. Education Coding

Column `b2q7_perrv` / `b2q7_per_rv`:

| Code | Level |
|---|---|
| 1 | Not literate |
| 2 | Below primary |
| 3 | Primary |
| 4 | Middle |
| 5 | Secondary |
| 6 | Higher Secondary |
| 7 | Diploma/Certificate |
| 8 | Graduate |
| 9 | Post-graduate and above |

**Secondary or above (for DiD control):** Codes ≥ 5.  
Coding is consistent across all three rounds.

---

## 9. Pre-Analysis Decisions Required

Before running any regression, the following must be locked:

| Decision | Options | Recommended |
|---|---|---|
| Sector variable | b4q5 (3-category) or b4q6 (NIC-2 digit) | **b4q5 for primary split; b4q6 for robustness only** |
| Wage conditioning | All employed vs wage workers only | **Wage workers only (codes 4–5)** |
| 2021-22 district code | b1q4_perrv (unverified) | **Use with PROBABLE_DISTRICT_CODE flag; exclude from primary DiD if unverifiable** |
| Vijayanagara | Include (code 31) or merge with Ballari | **Merge into Ballari for panel consistency** |
| Rajasthan boundary | 2011 or 2023 districts | **2011 boundaries; verify PLFS 2023-24 sample frame** |
| Education threshold | ≥4 (Middle+) or ≥5 (Secondary+) | **≥5 (Secondary+) to match DiD control definition** |

---

## 10. Column Mapping Summary (Canonical → Round-Specific)

| Canonical Name | 2019-20 | 2021-22 | 2023-24 |
|---|---|---|---|
| `district_code` | `district_per_rv` | `b1q4_perrv` ⚠️ | `dist_code_perrv` |
| `state_code` | `state_per_rv` | `state_perrv` | `state_perrv` |
| `weight` | `MULT_per_rv` | `mult_perrv` | `mult_perrv` |
| `activity_status` | `b4q4_per_rv` | `b4q4_perrv` | `b4q4_perrv` |
| `broad_sector` | `b4q5_per_rv` | `b4q5_perrv` | `b4q5_perrv` |
| `nic_2digit` | `b4q6_per_rv` | `b4q6_perrv` | `b4q6_perrv` |
| `education` | `b2q7_per_rv` | `b2q7_perrv` | `b2q7_perrv` |
| `wage_weekly` | `b6q5_3pt1_Act1_per_rv` | `b6q5_3pt1_perrv` | `b6q5_3pt1_perrv` |

All mappings are implemented in `pipelines/transformers/plfs_panel_builder.py` via the `COLUMN_ALIASES` dictionary.
