-- ============================================================
-- queries.sql
-- Bluestock MF Capstone — 10 Analytical SQL Queries
-- ============================================================

-- Query 1: Top 5 fund houses by AUM
SELECT
    fund_house,
    ROUND(SUM(aum_crore), 0)        AS total_aum_crore,
    ROUND(SUM(aum_lakh_crore), 2)   AS total_aum_lakh_crore,
    MAX(num_schemes)                AS num_schemes
FROM fact_aum
WHERE date = (SELECT MAX(date) FROM fact_aum)
GROUP BY fund_house
ORDER BY total_aum_crore DESC
LIMIT 5;

-- Query 2: Average NAV per month
SELECT
    strftime('%Y-%m', date)     AS month,
    ROUND(AVG(nav), 2)          AS avg_nav,
    ROUND(MIN(nav), 2)          AS min_nav,
    ROUND(MAX(nav), 2)          AS max_nav,
    COUNT(DISTINCT amfi_code)   AS num_funds
FROM fact_nav
GROUP BY strftime('%Y-%m', date)
ORDER BY month;

-- Query 3: SIP YoY growth
SELECT
    strftime('%Y', month)           AS year,
    ROUND(SUM(sip_inflow_crore), 0) AS total_sip_inflow_crore,
    ROUND(AVG(yoy_growth_pct), 2)   AS avg_yoy_growth_pct
FROM fact_sip_inflows
GROUP BY strftime('%Y', month)
ORDER BY year;

-- Query 4: Transactions by state
SELECT
    state,
    COUNT(*)                            AS total_transactions,
    ROUND(SUM(amount_inr) / 1e7, 2)    AS total_amount_crore,
    COUNT(DISTINCT investor_id)         AS unique_investors
FROM fact_transactions
GROUP BY state
ORDER BY total_transactions DESC;

-- Query 5: Funds with expense ratio less than 1%
SELECT
    scheme_name,
    fund_house,
    category,
    plan,
    expense_ratio_pct,
    aum_crore,
    sharpe_ratio
FROM fact_performance
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- Query 6: Best performing funds by 3-year return
SELECT
    scheme_name,
    fund_house,
    category,
    return_3yr_pct,
    benchmark_3yr_pct,
    ROUND(return_3yr_pct - benchmark_3yr_pct, 2)    AS alpha_vs_benchmark,
    sharpe_ratio,
    risk_grade
FROM fact_performance
ORDER BY return_3yr_pct DESC
LIMIT 10;

-- Query 7: Transaction breakdown by type and gender
SELECT
    transaction_type,
    gender,
    COUNT(*)                            AS num_transactions,
    ROUND(AVG(amount_inr), 0)           AS avg_amount_inr,
    ROUND(SUM(amount_inr) / 1e7, 2)    AS total_amount_crore
FROM fact_transactions
GROUP BY transaction_type, gender
ORDER BY transaction_type, num_transactions DESC;

-- Query 8: Top sectors by portfolio weight
SELECT
    sector,
    ROUND(AVG(weight_pct), 2)       AS avg_weight_pct,
    ROUND(SUM(market_value_cr), 0)  AS total_market_value_cr,
    COUNT(DISTINCT amfi_code)       AS num_funds_holding
FROM fact_portfolio_holdings
GROUP BY sector
ORDER BY avg_weight_pct DESC;

-- Query 9: SBI Bluechip NAV growth year by year
SELECT
    strftime('%Y', date)    AS year,
    ROUND(MIN(nav), 4)      AS nav_start,
    ROUND(MAX(nav), 4)      AS nav_peak,
    ROUND(AVG(nav), 4)      AS nav_avg,
    ROUND(
        (MAX(nav) - MIN(nav)) * 100.0 / MIN(nav), 2
    )                       AS yearly_range_pct
FROM fact_nav
WHERE amfi_code = 119551
GROUP BY strftime('%Y', date)
ORDER BY year;

-- Query 10: Category-wise net inflows per year
SELECT
    strftime('%Y', month)               AS year,
    category,
    ROUND(SUM(net_inflow_crore), 0)     AS total_net_inflow_crore
FROM fact_category_inflows
GROUP BY strftime('%Y', month), category
ORDER BY year, total_net_inflow_crore DESC;