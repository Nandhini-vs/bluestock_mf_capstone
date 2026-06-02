# Bluestock MF Capstone

Mutual Fund data analysis project — ETL, EDA, performance metrics, dashboard, and report.

## Setup

```bash
pip install -r requirements.txt
```

## Day 1 — Data Ingestion

```bash
python scripts/live_nav_fetch.py    # Downloads live NAV from mfapi.in
python scripts/data_ingestion.py    # Loads all 10 CSVs and validates data
```

## Folder Structure

```
data/raw/        ← original CSV files
data/processed/  ← cleaned and merged files
notebooks/       ← Jupyter analysis notebooks
scripts/         ← Python scripts
sql/             ← schema and queries
reports/         ← quality reports and outputs
```
