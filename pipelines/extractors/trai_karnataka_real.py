"""
AIRIS — TRAI Karnataka Complete Extraction
============================================
Produces:
  data/clean/karnataka/trai_karnataka_2025.csv   — all metrics
  data/clean/karnataka/trai_provenance_2025.csv  — field-level provenance

All REAL values sourced from TRAI QPIR Q4 2025 (Oct-Dec 2025).
DERIVED values are explicitly flagged with derivation logic.
NO values are estimated or synthetic.

Granularity: Karnataka LSA (state level).
TRAI does not publish district-level data.
"""

import pandas as pd
from pathlib import Path

OUT_DIR = Path("data/clean/karnataka")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_DOC   = "TRAI QPIR Q4 2025 (Oct-Dec 2025), Published 03-03-2026"
SOURCE_FILE  = "QPIR_03032026_0.pdf"
PERIOD_END   = "2025-12-31"
GRANULARITY  = "Karnataka LSA (state level) — district data not published by TRAI"

# ─── All extracted metrics with full provenance ───────────────────────────────
RECORDS = [

    # ── TOTAL SUBSCRIBERS (Wireline + Wireless) ──────────────────────────────
    dict(metric_id="KA_TOTAL_SUBS",
         metric_name="Total Telecom Subscribers",
         value=88.08, unit="million",
         rural_value=27.68, urban_value=60.40,
         rural_pct=31.43, urban_pct=68.57,
         data_status="REAL",
         page=24, table="1.3 / 1.5",
         source_column="Total Subscribers (million) — Karnataka row",
         notes="Wireline + Wireless combined"),

    # ── TOTAL TELE-DENSITY (Wireline + Wireless) ──────────────────────────────
    dict(metric_id="KA_TOTAL_TELE_DENSITY",
         metric_name="Total Tele-density (Wireline+Wireless)",
         value=127.85, unit="percent",
         rural_value=74.09, urban_value=191.54,
         rural_pct=None, urban_pct=None,
         data_status="REAL",
         page=26, table="1.4 / 1.6",
         source_column="Rural/Urban Tele-density (%) — Karnataka row",
         notes="Tele-density = subscribers per 100 population"),

    # ── WIRELESS SUBSCRIBERS (Mobile + FWA) ───────────────────────────────────
    dict(metric_id="KA_WIRELESS_SUBS",
         metric_name="Wireless Subscribers (Mobile + Fixed Wireless)",
         value=82.15, unit="million",
         rural_value=27.39, urban_value=54.76,
         rural_pct=33.34, urban_pct=66.66,
         data_status="REAL",
         page=35, table="1.13 / 1.15",
         source_column="Subscriber base (million) — Karnataka row",
         notes="Includes both mobile (handset) and FWA subscribers"),

    # ── WIRELESS TELE-DENSITY ─────────────────────────────────────────────────
    dict(metric_id="KA_WIRELESS_TELE_DENSITY",
         metric_name="Wireless Tele-density (Mobile + Fixed Wireless)",
         value=119.25, unit="percent",
         rural_value=73.32, urban_value=173.67,
         rural_pct=None, urban_pct=None,
         data_status="REAL",
         page=36, table="1.14 / 1.16",
         source_column="Wireless Tele-density (%) — Karnataka row",
         notes="Wireless mobile + FWA per 100 population"),

    # ── WIRELESS MOBILE ONLY (excl FWA) ───────────────────────────────────────
    dict(metric_id="KA_MOBILE_SUBS",
         metric_name="Wireless Mobile Subscribers (excl. Fixed Wireless)",
         value=81.27, unit="million",
         rural_value=27.10, urban_value=54.17,
         rural_pct=33.34, urban_pct=66.66,
         data_status="REAL",
         page=43, table="1.21 / 1.23",
         source_column="Subscriber base (million) — Karnataka row",
         notes="Mobile handset subscribers only, excluding FWA"),

    # ── MOBILE TELE-DENSITY ───────────────────────────────────────────────────
    dict(metric_id="KA_MOBILE_TELE_DENSITY",
         metric_name="Mobile Tele-density (excl. Fixed Wireless)",
         value=117.96, unit="percent",
         rural_value=72.53, urban_value=171.79,
         rural_pct=None, urban_pct=None,
         data_status="REAL",
         page=44, table="1.22 / 1.24",
         source_column="Wireless (mobile) Tele-density (%) — Karnataka row",
         notes="Primary mobile coverage indicator for rural areas"),

    # ── WIRELINE SUBSCRIBERS ──────────────────────────────────────────────────
    dict(metric_id="KA_WIRELINE_SUBS",
         metric_name="Wireline (Fixed Line) Subscribers",
         value=5.92, unit="million",
         rural_value=0.29, urban_value=5.63,
         rural_pct=4.89, urban_pct=95.11,
         data_status="REAL",
         page=55, table="1.31 / 1.33",
         source_column="Wireline Subscribers (million) — Karnataka row",
         notes="Only 4.89% of wireline subs are rural — urban-dominated"),

    # ── WIRELINE TELE-DENSITY ─────────────────────────────────────────────────
    dict(metric_id="KA_WIRELINE_TELE_DENSITY",
         metric_name="Wireline Tele-density",
         value=8.60, unit="percent",
         rural_value=0.78, urban_value=17.87,
         rural_pct=None, urban_pct=None,
         data_status="REAL",
         page=56, table="1.32 / 1.34",
         source_column="Wireline Tele-density (%) — Karnataka row",
         notes="Rural wireline 0.78% vs urban 17.87% — 17x gap"),

    # ── INTERNET SUBSCRIBERS ──────────────────────────────────────────────────
    dict(metric_id="KA_INTERNET_SUBS",
         metric_name="Total Internet Subscribers",
         value=65.17, unit="million",
         rural_value=22.69, urban_value=42.47,
         rural_pct=round(22.69/65.17*100, 2), urban_pct=round(42.47/65.17*100, 2),
         data_status="REAL",
         page=72, table="1.40 / 1.41",
         source_column="Total Subscribers (In million) — Karnataka row",
         notes="Internet = all download speed tiers (narrowband + broadband)"),

    # ── INTERNET TELE-DENSITY ─────────────────────────────────────────────────
    dict(metric_id="KA_INTERNET_DENSITY",
         metric_name="Internet Subscribers per 100 Population",
         value=94.59, unit="percent",
         rural_value=60.75, urban_value=134.69,
         rural_pct=None, urban_pct=None,
         data_status="REAL",
         page=72, table="1.41",
         source_column="Tele-density (%) — Karnataka row",
         notes="Rural internet penetration 60.75% vs national 47.63%"),

    # ── BROADBAND SUBSCRIBERS (DERIVED) ───────────────────────────────────────
    dict(metric_id="KA_BROADBAND_SUBS",
         metric_name="Estimated Broadband Subscribers (≥2Mbps)",
         value=round(65.17 * 0.9793, 2), unit="million",
         rural_value=None, urban_value=None,
         rural_pct=None, urban_pct=None,
         data_status="DERIVED",
         page=74, table="National broadband overview",
         source_column="Derived: KA internet 65.17M × (1 − national narrowband fraction 2.07%)",
         notes=(
             "TRAI does not publish service-area-wise broadband figures in QPIR Q4 2025. "
             "Derived using national narrowband fraction (21.25M / 1028.61M = 2.07%). "
             "Assumption: KA narrowband fraction ≈ national. "
             "This is an approximation. Label as DERIVED in all outputs."
         )),

    # ── QoS: ARPU ─────────────────────────────────────────────────────────────
    dict(metric_id="KA_ARPU",
         metric_name="Average Revenue Per User (wireless, prepaid)",
         value=208.0, unit="INR_per_month",
         rural_value=None, urban_value=None,
         rural_pct=None, urban_pct=None,
         data_status="REAL",
         page=125, table="QoS parameters Category-A",
         source_column="ARPU (Rs. per month) — Karnataka row",
         notes="National benchmark context: Category-A LSA (Bengaluru-heavy). "
               "May not represent rural Karnataka affordability."),

    # ── QoS: PREPAID FRACTION ─────────────────────────────────────────────────
    dict(metric_id="KA_PREPAID_PCT",
         metric_name="Prepaid subscribers as % of total wireless",
         value=84.45, unit="percent",
         rural_value=None, urban_value=None,
         rural_pct=None, urban_pct=None,
         data_status="REAL",
         page=125, table="QoS parameters Category-A",
         source_column="% of pre-paid in total Subscribers — Karnataka row",
         notes="84.45% prepaid. Lower than national average for rural areas. "
               "Indicates relatively more postpaid subscribers vs peer states."),
]


# ─── Compute gaps and derived fields ─────────────────────────────────────────
def build_main_csv(records):
    rows = []
    for r in records:
        rows.append({
            "metric_id":          r["metric_id"],
            "metric_name":        r["metric_name"],
            "state":              "Karnataka",
            "period_end":         PERIOD_END,
            "value_total":        r["value"],
            "value_rural":        r.get("rural_value"),
            "value_urban":        r.get("urban_value"),
            "rural_pct":          r.get("rural_pct"),
            "urban_pct":          r.get("urban_pct"),
            "unit":               r["unit"],
            "data_status":        r["data_status"],
            "granularity":        GRANULARITY,
        })
    return pd.DataFrame(rows)


def build_provenance_csv(records):
    rows = []
    for r in records:
        rows.append({
            "metric_id":       r["metric_id"],
            "metric_name":     r["metric_name"],
            "data_status":     r["data_status"],
            "source_document": SOURCE_DOC,
            "source_file":     SOURCE_FILE,
            "pdf_page":        r["page"],
            "table_reference": r["table"],
            "source_column":   r["source_column"],
            "period_end":      PERIOD_END,
            "notes":           r.get("notes", ""),
            "verified_by":     "Manual cross-reference of text extraction vs table extraction",
            "extraction_date": "2026-06-05",
        })
    return pd.DataFrame(rows)


def print_report(df_main):
    print("=" * 70)
    print("AIRIS — KARNATAKA TRAI INFRASTRUCTURE BASELINE")
    print(f"Period: Q4 2025 (Oct-Dec 2025) | Granularity: STATE (LSA)")
    print("=" * 70)

    print("\n[TELECOM COVERAGE]")
    for _, r in df_main[df_main["metric_id"].isin(
            ["KA_TOTAL_TELE_DENSITY","KA_WIRELESS_TELE_DENSITY",
             "KA_MOBILE_TELE_DENSITY","KA_WIRELINE_TELE_DENSITY",
             "KA_INTERNET_DENSITY"])].iterrows():
        tag = "[REAL]   " if r["data_status"] == "REAL" else "[DERIVED]"
        rv = f"{r['value_rural']:.2f}%" if pd.notna(r.get("value_rural")) else "N/A"
        uv = f"{r['value_urban']:.2f}%" if pd.notna(r.get("value_urban")) else "N/A"
        print(f"  {tag} {r['metric_name']:<46} Rural:{rv:>8}  Urban:{uv:>8}")

    print("\n[SUBSCRIBERS]")
    for _, r in df_main[df_main["metric_id"].isin(
            ["KA_TOTAL_SUBS","KA_WIRELESS_SUBS","KA_MOBILE_SUBS",
             "KA_WIRELINE_SUBS","KA_INTERNET_SUBS","KA_BROADBAND_SUBS"])].iterrows():
        tag = "[REAL]   " if r["data_status"] == "REAL" else "[DERIVED]"
        rv = f"{r['value_rural']:.2f}M" if pd.notna(r.get("value_rural")) else "N/A"
        print(f"  {tag} {r['metric_name']:<46} Total:{r['value_total']:>7.2f}M  Rural:{rv:>8}")

    print("\n[KEY GAPS]")
    td = df_main[df_main["metric_id"]=="KA_TOTAL_TELE_DENSITY"].iloc[0]
    md = df_main[df_main["metric_id"]=="KA_MOBILE_TELE_DENSITY"].iloc[0]
    wl = df_main[df_main["metric_id"]=="KA_WIRELINE_TELE_DENSITY"].iloc[0]
    net= df_main[df_main["metric_id"]=="KA_INTERNET_DENSITY"].iloc[0]
    print(f"  Total tele-density gap (urban-rural):     {td['value_urban']-td['value_rural']:.2f} pp")
    print(f"  Mobile tele-density gap (urban-rural):    {md['value_urban']-md['value_rural']:.2f} pp")
    print(f"  Wireline tele-density gap (urban-rural):  {wl['value_urban']-wl['value_rural']:.2f} pp")
    print(f"  Internet density gap (urban-rural):       {net['value_urban']-net['value_rural']:.2f} pp")
    print(f"  Rural internet density:                   {net['value_rural']:.2f}% (national: 47.63%)")
    print(f"  KA rural internet vs national:            +{net['value_rural']-47.63:.2f} pp advantage")

    print("\n[DERIVED METRIC WARNING]")
    derived = df_main[df_main["data_status"]=="DERIVED"]
    for _, r in derived.iterrows():
        print(f"  {r['metric_id']}: {r['metric_name']} — NOT DIRECTLY REPORTED BY TRAI")
    print("=" * 70)


if __name__ == "__main__":
    df_main = build_main_csv(RECORDS)
    df_prov = build_provenance_csv(RECORDS)

    out_main = OUT_DIR / "trai_karnataka_2025.csv"
    out_prov = OUT_DIR / "trai_provenance_2025.csv"
    out_main_p = OUT_DIR / "trai_karnataka_2025.parquet"

    df_main.to_csv(out_main, index=False)
    df_prov.to_csv(out_prov, index=False)
    df_main.to_parquet(out_main_p, index=False)

    print_report(df_main)
    print(f"\nSaved:")
    print(f"  Main:       {out_main}")
    print(f"  Provenance: {out_prov}")
    print(f"  Parquet:    {out_main_p}")
