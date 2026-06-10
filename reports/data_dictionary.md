# Data Dictionary — Bluestock MF Capstone

## Table of Contents
1. [dim_fund](#1-dim_fund)
2. [fact_nav](#2-fact_nav)
3. [fact_transactions](#3-fact_transactions)
4. [fact_performance](#4-fact_performance)
5. [fact_aum](#5-fact_aum)
6. [fact_sip_inflows](#6-fact_sip_inflows)
7. [fact_category_inflows](#7-fact_category_inflows)
8. [fact_portfolio_holdings](#8-fact_portfolio_holdings)
9. [fact_benchmark](#9-fact_benchmark)
10. [dim_date](#10-dim_date)

---

## 1. dim_fund
**Source:** 01_fund_master.csv
**Description:** Master list of all mutual fund schemes.

| Column | Type | Description |
|--------|------|-------------|
| amfi_code | INTEGER (PK) | Unique 6-digit ID assigned by AMFI to every scheme |
| fund_house | TEXT | Name of the Asset Management Company |
| scheme_name | TEXT | Full name of the mutual fund scheme |
| category | TEXT | Broad category — Equity, Debt, Hybrid |
| sub_category | TEXT | Detailed category — Large Cap, Mid Cap, Gilt, etc. |
| plan | TEXT | Regular (higher expense) or Direct (lower expense) |
| launch_date | DATE | Date the scheme was launched |
| benchmark | TEXT | Index used to compare fund performance |
| expense_ratio_pct | REAL | Annual fee charged by fund house as % of AUM |
| exit_load_pct | REAL | Penalty charged on early redemption (%) |
| min_sip_amount | INTEGER | Minimum monthly SIP investment in INR |
| min_lumpsum_amount | INTEGER | Minimum one-time investment in INR |
| fund_manager | TEXT | Name of the person managing the fund |
| risk_category | TEXT | Low, Moderate, Moderately High, High, Very High |
| sebi_category_code | TEXT | SEBI classification code |

---

## 2. fact_nav
**Source:** 02_nav_history.csv
**Description:** Daily NAV for each scheme. NAV = price per unit of the fund.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Auto-generated row ID |
| amfi_code | INTEGER (FK) | Links to dim_fund |
| date | DATE | Trading date (weekends/holidays forward-filled) |
| nav | REAL | Net Asset Value in INR |

**Notes:**
- 46,000 original rows → 64,320 after forward-filling weekends
- NAV <= 0 rows removed

---

## 3. fact_transactions
**Source:** 08_investor_transactions.csv
**Description:** Individual investor buy/sell transactions. 32,778 records.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Auto-generated row ID |
| investor_id | TEXT | Unique investor identifier |
| transaction_date | DATE | Date the transaction was made |
| amfi_code | INTEGER (FK) | Fund invested in |
| transaction_type | TEXT | SIP / Lumpsum / Redemption |
| amount_inr | REAL | Transaction amount in Indian Rupees |
| state | TEXT | Indian state of the investor |
| city | TEXT | City of the investor |
| city_tier | TEXT | T30 (top 30 cities) or B30 (beyond top 30) |
| age_group | TEXT | 18-25, 26-35, 36-45, 46-55, 56+ |
| gender | TEXT | Male / Female |
| annual_income_lakh | REAL | Annual income in lakhs |
| payment_mode | TEXT | UPI / Mandate / Cheque / NEFT |
| kyc_status | TEXT | Verified / Pending |

---

## 4. fact_performance
**Source:** 07_scheme_performance.csv
**Description:** Performance metrics for each fund scheme.

| Column | Type | Description |
|--------|------|-------------|
| amfi_code | INTEGER (FK) | Links to dim_fund |
| return_1yr_pct | REAL | 1-year absolute return (%) |
| return_3yr_pct | REAL | 3-year CAGR return (%) |
| return_5yr_pct | REAL | 5-year CAGR return (%) |
| benchmark_3yr_pct | REAL | Benchmark 3-year return for comparison |
| alpha | REAL | Excess return over benchmark |
| beta | REAL | Fund sensitivity to market movements |
| sharpe_ratio | REAL | Return per unit of risk |
| sortino_ratio | REAL | Like Sharpe but only penalises downside risk |
| std_dev_ann_pct | REAL | Annualised volatility |
| max_drawdown_pct | REAL | Largest peak-to-trough loss |
| aum_crore | REAL | Assets Under Management in crore INR |
| expense_ratio_pct | REAL | Annual fee — valid range 0.1% to 2.5% |
| morningstar_rating | INTEGER | 1 to 5 star rating |
| risk_grade | TEXT | Moderate / High / Very High / Low |

---

## 5. fact_aum
**Source:** 03_aum_by_fund_house.csv
**Description:** Monthly AUM snapshot per fund house.

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Quarter-end date of AUM snapshot |
| fund_house | TEXT | Name of the AMC |
| aum_lakh_crore | REAL | AUM in lakh crore |
| aum_crore | REAL | AUM in crore |
| num_schemes | INTEGER | Number of schemes managed |

---

## 6. fact_sip_inflows
**Source:** 04_monthly_sip_inflows.csv
**Description:** Industry-level monthly SIP statistics.

| Column | Type | Description |
|--------|------|-------------|
| month | DATE | First day of the month |
| sip_inflow_crore | REAL | Total SIP money received industry-wide |
| active_sip_accounts_crore | REAL | Active SIP accounts in crore |
| new_sip_accounts_lakh | REAL | New SIP accounts opened in lakh |
| sip_aum_lakh_crore | REAL | Total SIP AUM in lakh crore |
| yoy_growth_pct | REAL | Year-on-year growth (NaN for first 12 months) |

---

## 7. fact_category_inflows
**Source:** 05_category_inflows.csv
**Description:** Monthly net inflows by fund category.

| Column | Type | Description |
|--------|------|-------------|
| month | DATE | First day of the month |
| category | TEXT | Large Cap, Mid Cap, Small Cap, Liquid, etc. |
| net_inflow_crore | REAL | Net money into this category that month |

---

## 8. fact_portfolio_holdings
**Source:** 09_portfolio_holdings.csv
**Description:** Stock-level holdings for each fund.

| Column | Type | Description |
|--------|------|-------------|
| amfi_code | INTEGER (FK) | Links to dim_fund |
| stock_symbol | TEXT | NSE/BSE ticker symbol |
| stock_name | TEXT | Full company name |
| sector | TEXT | Banking, IT, Consumer Goods, etc. |
| weight_pct | REAL | Percentage of fund in this stock |
| market_value_cr | REAL | Market value of holding in crore INR |
| current_price_inr | REAL | Stock price at portfolio date |
| portfolio_date | DATE | Date of portfolio snapshot |

---

## 9. fact_benchmark
**Source:** 10_benchmark_indices.csv
**Description:** Daily closing values for benchmark indices.

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Trading date |
| index_name | TEXT | NIFTY50, NIFTY100, BSE500, etc. |
| close_value | REAL | Closing value of the index |

---

## 10. dim_date
**Source:** Generated from fact_nav dates
**Description:** Date dimension for time-based analysis.

| Column | Type | Description |
|--------|------|-------------|
| date_id | TEXT (PK) | Date in YYYY-MM-DD format |
| year | INTEGER | Calendar year |
| month | INTEGER | Month number 1 to 12 |
| month_name | TEXT | January to December |
| quarter | INTEGER | Quarter 1 to 4 |
| day_of_week | TEXT | Monday to Sunday |
| is_weekend | INTEGER | 1 if Saturday or Sunday, 0 otherwise |

---

## Key Business Terms

| Term | Meaning |
|------|---------|
| NAV | Net Asset Value — price of 1 unit of a mutual fund |
| AUM | Assets Under Management — total money managed |
| SIP | Systematic Investment Plan — fixed monthly investment |
| AMFI | Association of Mutual Funds in India |
| CAGR | Compound Annual Growth Rate — annualised return |
| Sharpe Ratio | Return divided by risk — higher is better |
| Alpha | Return earned above the benchmark |
| Beta | How much the fund moves with the market |
| T30 | Top 30 cities in India |
| B30 | Beyond top 30 cities |
| Direct Plan | No distributor — lower expense ratio |
| Regular Plan | Through distributor — higher expense ratio |