"""
live_nav_fetch.py
Fetches live NAV data from mfapi.in for 6 key mutual fund schemes.
Tasks covered: 4, 5
"""

from pathlib import Path
import requests
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# ── Paths (never hardcode — always use pathlib) ───────────────────────────────
RAW  = Path("data/raw")
PROC = Path("data/processed")
RAW.mkdir(parents=True,  exist_ok=True)
PROC.mkdir(parents=True, exist_ok=True)

# ── Task 4 + 5: All 6 schemes ─────────────────────────────────────────────────
SCHEMES = {
    125497: "HDFC_Top100",
    119551: "SBI_Bluechip",
    120503: "ICICI_Bluechip",
    118632: "Nippon_LargeCap",
    119092: "Axis_Bluechip",
    120841: "Kotak_Bluechip",
}

all_frames = []

for code, name in SCHEMES.items():
    try:
        url = f"https://api.mfapi.in/mf/{code}"
        log.info(f"Fetching {name} ({code}) ...")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        payload = r.json()

        # Build dataframe from API response
        df = pd.DataFrame(payload["data"])          # columns: date, nav
        df["amfi_code"]   = code
        df["scheme_name"] = payload["meta"]["scheme_name"]
        df["fund_house"]  = payload["meta"]["fund_house"]
        df["category"]    = payload["meta"]["scheme_category"]

        # Fix date format (API returns DD-MM-YYYY)
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
        df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
        df = df.sort_values("date").reset_index(drop=True)

        # ✅ Fill weekends & holidays forward (important for correctness)
        full_range = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
        df = (df.set_index("date")
                .reindex(full_range)
                .ffill()
                .reset_index()
                .rename(columns={"index": "date"}))

        # Save individual CSV
        out = RAW / f"nav_{code}_{name}.csv"
        df.to_csv(out, index=False)
        log.info(f"  Saved {len(df):,} rows → {out.name}")
        log.info(f"  Latest NAV : Rs.{df['nav'].iloc[-1]:.4f}  on  {df['date'].iloc[-1].date()}")

        all_frames.append(df)

    except requests.exceptions.ConnectionError:
        log.error(f"  No internet connection — skipping {name}")
    except requests.exceptions.Timeout:
        log.error(f"  Timeout — skipping {name}")
    except Exception as e:
        log.error(f"  FAILED {name} ({code}): {e}")

# ── Combine all into one master CSV ──────────────────────────────────────────
if all_frames:
    combined = pd.concat(all_frames, ignore_index=True)
    out_combined = PROC / "all_bluechip_nav.csv"
    combined.to_csv(out_combined, index=False)
    log.info(f"\nCombined file: {len(combined):,} rows → {out_combined}")
else:
    log.warning("No data fetched — check your internet connection")

log.info("live_nav_fetch.py — DONE ✓")
