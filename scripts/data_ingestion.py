"""
data_ingestion.py
Loads all 10 CSV datasets, prints shape/dtypes/head, explores fund master,
validates AMFI codes, and writes a data quality report.
Tasks covered: 3, 6, 7
"""

from pathlib import Path
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
RAW     = Path("data/raw")
REPORTS = Path("reports")
REPORTS.mkdir(parents=True, exist_ok=True)

# ── Task 3: All 10 CSV files ──────────────────────────────────────────────────
CSV_FILES = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]

dataframes = {}
anomalies  = []

print("\n" + "="*60)
print("  TASK 3 — LOADING ALL 10 CSV DATASETS")
print("="*60)

for fname in CSV_FILES:
    fpath = RAW / fname
    if not fpath.exists():
        log.warning(f"NOT FOUND — skipping: {fname}")
        continue

    df = pd.read_csv(fpath)
    dataframes[fname] = df

    nulls = df.isnull().sum().sum()
    dupes = df.duplicated().sum()

    print(f"\n{'─'*60}")
    print(f"FILE  : {fname}")
    print(f"Shape : {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"Nulls : {nulls}   |   Duplicates : {dupes}")
    print("\nColumn Dtypes:")
    print(df.dtypes.to_string())
    print("\nFirst 3 rows:")
    print(df.head(3).to_string())

    # Collect anomalies
    if nulls > 0:
        anomalies.append(f"{fname}: {nulls} null values")
    if dupes > 0:
        anomalies.append(f"{fname}: {dupes} duplicate rows")

# ── Task 6: Explore fund_master ───────────────────────────────────────────────
print("\n\n" + "="*60)
print("  TASK 6 — FUND MASTER EXPLORATION")
print("="*60)

FUND_MASTER_FILE = "01_fund_master.csv"

if FUND_MASTER_FILE in dataframes:
    fm = dataframes[FUND_MASTER_FILE]

    print(f"\nTotal schemes in fund master : {len(fm)}")

    # Unique fund houses
    print(f"\n📌 Unique Fund Houses ({fm['fund_house'].nunique()}):")
    print(fm['fund_house'].value_counts().to_string())

    # Unique categories
    print(f"\n📌 Unique Categories ({fm['category'].nunique()}):")
    print(fm['category'].value_counts().to_string())

    # Unique sub-categories
    print(f"\n📌 Unique Sub-Categories ({fm['sub_category'].nunique()}):")
    print(fm['sub_category'].value_counts().to_string())

    # Risk grades
    print(f"\n📌 Risk Grades ({fm['risk_category'].nunique()}):")
    print(fm['risk_category'].value_counts().to_string())

    # AMFI scheme code structure
    print(f"\n📌 AMFI Scheme Code Sample (first 10):")
    print(fm[['amfi_code', 'scheme_name', 'fund_house', 'category']].head(10).to_string())
    print("\nℹ️  AMFI codes are unique 6-digit numbers assigned to every mutual fund scheme in India.")

else:
    log.warning("01_fund_master.csv not found — skipping fund master exploration")

# ── Task 7: Validate AMFI codes ───────────────────────────────────────────────
print("\n\n" + "="*60)
print("  TASK 7 — AMFI CODE VALIDATION")
print("="*60)

NAV_FILE = "02_nav_history.csv"

if FUND_MASTER_FILE in dataframes and NAV_FILE in dataframes:
    master_codes = set(dataframes[FUND_MASTER_FILE]["amfi_code"].astype(str))
    nav_codes    = set(dataframes[NAV_FILE]["amfi_code"].astype(str))

    missing_in_nav  = master_codes - nav_codes   # in master but no NAV history
    extra_in_nav    = nav_codes - master_codes    # in NAV but not in master

    print(f"\nSchemes in fund_master  : {len(master_codes)}")
    print(f"Schemes in nav_history  : {len(nav_codes)}")
    print(f"In master but NOT nav   : {len(missing_in_nav)}")
    print(f"In nav but NOT master   : {len(extra_in_nav)}")

    if missing_in_nav:
        print(f"\n⚠️  Codes missing from nav_history: {sorted(missing_in_nav)[:10]}")
    else:
        print("\n✅ All fund_master codes exist in nav_history!")

    # Build quality report lines
    report_lines = [
        "DATA QUALITY SUMMARY — Day 1",
        "="*45,
        f"Total CSV files loaded      : {len(dataframes)}",
        f"Schemes in fund_master      : {len(master_codes)}",
        f"Schemes in nav_history      : {len(nav_codes)}",
        f"In master but NOT in nav    : {len(missing_in_nav)}",
        f"In nav but NOT in master    : {len(extra_in_nav)}",
        "",
        "Anomalies found:",
    ]

    if anomalies:
        report_lines += [f"  - {a}" for a in anomalies]
    else:
        report_lines.append("  None — data looks clean!")

    # Print and save
    print("\n" + "\n".join(report_lines))
    report_path = REPORTS / "data_quality_day1.txt"
    report_path.write_text("\n".join(report_lines))
    log.info(f"\n✅ Quality report saved → {report_path}")

else:
    log.warning("fund_master or nav_history not found — skipping validation")
    (REPORTS / "data_quality_day1.txt").write_text(
        "Validation skipped — CSV files not found in data/raw/\n"
    )

log.info("data_ingestion.py — DONE ✓")
