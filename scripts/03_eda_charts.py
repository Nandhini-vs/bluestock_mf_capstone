"""
03_eda_charts.py
Generates all 15 EDA charts and saves them as PNG files.
Tasks covered: 1-10
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────
RAW    = Path("data/raw")
PROC   = Path("data/processed")
CHARTS = Path("reports/charts")
CHARTS.mkdir(parents=True, exist_ok=True)

def load(fname_clean, fname_raw):
    p = PROC / fname_clean
    if p.exists(): return pd.read_csv(p)
    return pd.read_csv(RAW / fname_raw)

# ── Load all datasets ─────────────────────────────────────────
nav   = load("02_nav_history_clean.csv",           "02_nav_history.csv")
aum   = load("03_aum_by_fund_house_clean.csv",     "03_aum_by_fund_house.csv")
sip   = load("04_monthly_sip_inflows_clean.csv",   "04_monthly_sip_inflows.csv")
cat   = load("05_category_inflows_clean.csv",      "05_category_inflows.csv")
folio = load("06_industry_folio_count_clean.csv",  "06_industry_folio_count.csv")
txn   = load("08_investor_transactions_clean.csv", "08_investor_transactions.csv")
port  = load("09_portfolio_holdings_clean.csv",    "09_portfolio_holdings.csv")
fm    = load("01_fund_master_clean.csv",           "01_fund_master.csv")
perf  = load("07_scheme_performance_clean.csv",    "07_scheme_performance.csv")

# Fix dates
nav["date"]             = pd.to_datetime(nav["date"])
aum["date"]             = pd.to_datetime(aum["date"])
sip["month"]            = pd.to_datetime(sip["month"])
cat["month"]            = pd.to_datetime(cat["month"])
folio["month"]          = pd.to_datetime(folio["month"])
txn["transaction_date"] = pd.to_datetime(txn["transaction_date"])

nav = nav.merge(
    fm[["amfi_code","scheme_name","fund_house","category"]],
    on="amfi_code", how="left"
)

sns.set_theme(style="darkgrid", palette="tab10")
print("All datasets loaded ✓")

# ── Chart 1 — NAV Trends ──────────────────────────────────────
print("Chart 1: NAV trends ...")
key_funds = [119551, 119552, 119598, 125497, 120503, 119092]
nav6 = nav[nav["amfi_code"].isin(key_funds)].copy()

fig, ax = plt.subplots(figsize=(14, 6))
for code, grp in nav6.groupby("amfi_code"):
    name = grp["scheme_name"].iloc[0].split(" - ")[0]
    ax.plot(grp["date"], grp["nav"], label=name, linewidth=1.5)

ax.axvspan(pd.Timestamp("2023-01-01"), pd.Timestamp("2023-12-31"),
           alpha=0.12, color="green", label="2023 Bull Run")
ax.axvspan(pd.Timestamp("2024-09-01"), pd.Timestamp("2024-12-31"),
           alpha=0.12, color="red", label="2024 Correction")

ax.set_title("NAV Trend — 6 Key Schemes (2022–2026)", fontsize=14, fontweight="bold")
ax.set_xlabel("Date")
ax.set_ylabel("NAV (₹)")
ax.legend(fontsize=8, loc="upper left")
plt.tight_layout()
plt.savefig(CHARTS / "01_nav_trends.png", dpi=150)
plt.close()
print("  Saved 01_nav_trends.png")

# ── Chart 2 — AUM Grouped Bar ─────────────────────────────────
print("Chart 2: AUM grouped bar ...")
aum["year"] = aum["date"].dt.year
aum_yr = aum.groupby(["year","fund_house"])["aum_crore"].max().reset_index()

fig, ax = plt.subplots(figsize=(14, 6))
sns.barplot(data=aum_yr, x="fund_house", y="aum_crore",
            hue="year", ax=ax, palette="Blues")
ax.set_title("AUM Growth by Fund House (2022–2025)", fontsize=14, fontweight="bold")
ax.set_xlabel("Fund House")
ax.set_ylabel("AUM (₹ Crore)")
ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)

sbi_val = aum_yr[aum_yr["fund_house"]=="SBI Mutual Fund"]["aum_crore"].max()
ax.annotate(f"SBI ₹{sbi_val/1e5:.1f}L Cr",
            xy=(0, sbi_val), xytext=(1.5, sbi_val * 0.9),
            arrowprops=dict(arrowstyle="->", color="red"),
            fontsize=9, color="red", fontweight="bold")
plt.tight_layout()
plt.savefig(CHARTS / "02_aum_growth.png", dpi=150)
plt.close()
print("  Saved 02_aum_growth.png")

# ── Chart 3 — SIP Inflows ─────────────────────────────────────
print("Chart 3: SIP inflows ...")
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(sip["month"], sip["sip_inflow_crore"],
        color="#2196F3", linewidth=2, marker="o", markersize=3)
ax.fill_between(sip["month"], sip["sip_inflow_crore"],
                alpha=0.15, color="#2196F3")

max_idx   = sip["sip_inflow_crore"].idxmax()
max_val   = sip.loc[max_idx, "sip_inflow_crore"]
max_month = sip.loc[max_idx, "month"]
ax.annotate(f"All-Time High\n₹{max_val:,.0f} Cr (Dec 2025)",
            xy=(max_month, max_val),
            xytext=(max_month - pd.DateOffset(months=10), max_val * 0.92),
            arrowprops=dict(arrowstyle="->", color="red"),
            fontsize=9, color="red", fontweight="bold")

ax.set_title("Monthly SIP Inflows Jan 2022 – Dec 2025", fontsize=14, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("SIP Inflow (₹ Crore)")
plt.tight_layout()
plt.savefig(CHARTS / "03_sip_inflows.png", dpi=150)
plt.close()
print("  Saved 03_sip_inflows.png")

# ── Chart 4 — Category Heatmap ────────────────────────────────
print("Chart 4: Category heatmap ...")
cat["month_str"] = cat["month"].dt.strftime("%Y-%m")
pivot = cat.pivot_table(index="category", columns="month_str",
                        values="net_inflow_crore", aggfunc="sum")

fig, ax = plt.subplots(figsize=(16, 6))
sns.heatmap(pivot, cmap="RdYlGn", center=0, linewidths=0.3,
            ax=ax, cbar_kws={"label": "Net Inflow (₹ Cr)"})
ax.set_title("Category-wise Net Inflows Heatmap", fontsize=14, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Fund Category")
plt.xticks(rotation=45, ha="right", fontsize=7)
plt.tight_layout()
plt.savefig(CHARTS / "04_category_heatmap.png", dpi=150)
plt.close()
print("  Saved 04_category_heatmap.png")

# ── Chart 5 — Age Group ───────────────────────────────────────
print("Chart 5: Age group ...")
age_counts = txn["age_group"].value_counts()
fig, axes  = plt.subplots(1, 2, figsize=(13, 5))

axes[0].pie(age_counts.values, labels=age_counts.index,
            autopct="%1.1f%%", startangle=90,
            colors=sns.color_palette("pastel"))
axes[0].set_title("Investor Age Group Distribution", fontweight="bold")

sip_txn = txn[txn["transaction_type"].str.title() == "Sip"]
order   = ["18-25","26-35","36-45","46-55","56+"]
sns.boxplot(data=sip_txn, x="age_group", y="amount_inr",
            order=order, palette="Set2", ax=axes[1])
axes[1].set_title("SIP Amount by Age Group", fontweight="bold")
axes[1].set_xlabel("Age Group")
axes[1].set_ylabel("SIP Amount (₹)")
axes[1].set_ylim(0, 20000)
plt.tight_layout()
plt.savefig(CHARTS / "05_age_distribution.png", dpi=150)
plt.close()
print("  Saved 05_age_distribution.png")

# ── Chart 6 — Gender Split ────────────────────────────────────
print("Chart 6: Gender split ...")
gender = txn["gender"].value_counts()
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].pie(gender.values, labels=gender.index,
            autopct="%1.1f%%",
            colors=["#42A5F5","#EF5350"], startangle=90)
axes[0].set_title("Investor Gender Split", fontweight="bold")

gender_amount = txn.groupby("gender")["amount_inr"].mean().reset_index()
sns.barplot(data=gender_amount, x="gender", y="amount_inr",
            palette=["#42A5F5","#EF5350"], ax=axes[1])
axes[1].set_title("Average Transaction Amount by Gender", fontweight="bold")
axes[1].set_ylabel("Average Amount (₹)")
axes[1].set_xlabel("Gender")
plt.tight_layout()
plt.savefig(CHARTS / "06_gender_split.png", dpi=150)
plt.close()
print("  Saved 06_gender_split.png")

# ── Chart 7 — Geographic Distribution ────────────────────────
print("Chart 7: Geographic distribution ...")
state_amt = (txn.groupby("state")["amount_inr"]
               .sum()
               .sort_values(ascending=True) / 1e7)

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.barh(state_amt.index, state_amt.values,
               color=sns.color_palette("viridis", len(state_amt)))
ax.set_title("Total Investment by State (₹ Crore)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Total Investment (₹ Crore)")
for bar, val in zip(bars, state_amt.values):
    ax.text(bar.get_width() + 0.3,
            bar.get_y() + bar.get_height()/2,
            f"₹{val:.0f}Cr", va="center", fontsize=8)
plt.tight_layout()
plt.savefig(CHARTS / "07_geographic_distribution.png", dpi=150)
plt.close()
print("  Saved 07_geographic_distribution.png")

# ── Chart 8 — T30 vs B30 ─────────────────────────────────────
print("Chart 8: T30 vs B30 ...")
tier = txn["city_tier"].value_counts()
fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(tier.values, labels=tier.index,
       autopct="%1.1f%%",
       colors=["#FF7043","#66BB6A"],
       startangle=90, explode=[0.05]*len(tier))
ax.set_title("T30 vs B30 Investment Split", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(CHARTS / "08_city_tier.png", dpi=150)
plt.close()
print("  Saved 08_city_tier.png")

# ── Chart 9 — Folio Growth ────────────────────────────────────
print("Chart 9: Folio growth ...")
fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(folio["month"], folio["total_folios_crore"],
        color="#7B1FA2", linewidth=2.5, marker="o", markersize=5)
ax.fill_between(folio["month"], folio["total_folios_crore"],
                alpha=0.15, color="#7B1FA2")

ax.annotate("13.26 Cr\n(Jan 2022)",
            xy=(folio["month"].iloc[0], folio["total_folios_crore"].iloc[0]),
            xytext=(folio["month"].iloc[0], folio["total_folios_crore"].iloc[0]+1.5),
            ha="center", fontsize=8, fontweight="bold", color="#7B1FA2",
            arrowprops=dict(arrowstyle="->", color="#7B1FA2"))
ax.annotate("26.12 Cr\n(Dec 2025)",
            xy=(folio["month"].iloc[-1], folio["total_folios_crore"].iloc[-1]),
            xytext=(folio["month"].iloc[-1], folio["total_folios_crore"].iloc[-1]+1),
            ha="center", fontsize=8, fontweight="bold", color="#7B1FA2",
            arrowprops=dict(arrowstyle="->", color="#7B1FA2"))

ax.set_title("Industry Folio Count Growth (Jan 2022 – Dec 2025)",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Total Folios (Crore)")
plt.tight_layout()
plt.savefig(CHARTS / "09_folio_growth.png", dpi=150)
plt.close()
print("  Saved 09_folio_growth.png")

# ── Chart 10 — Correlation Matrix ────────────────────────────
print("Chart 10: Correlation matrix ...")
top10   = fm["amfi_code"].head(10).tolist()
nav10   = nav[nav["amfi_code"].isin(top10)].copy()
nav10["return"] = nav10.groupby("amfi_code")["nav"].pct_change()

pivot_ret = nav10.pivot_table(
    index="date", columns="amfi_code", values="return")
pivot_ret.columns = [
    fm.loc[fm["amfi_code"]==c,"scheme_name"].values[0].split(" - ")[0][:18]
    for c in pivot_ret.columns
]
corr = pivot_ret.corr()

fig, ax = plt.subplots(figsize=(11, 9))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f",
            cmap="coolwarm", center=0, linewidths=0.5, ax=ax,
            cbar_kws={"label": "Pearson Correlation"})
ax.set_title("NAV Return Correlation Matrix (10 Funds)",
             fontsize=13, fontweight="bold")
plt.xticks(rotation=30, ha="right", fontsize=8)
plt.tight_layout()
plt.savefig(CHARTS / "10_correlation_matrix.png", dpi=150)
plt.close()
print("  Saved 10_correlation_matrix.png")

# ── Chart 11 — Sector Donut ───────────────────────────────────
print("Chart 11: Sector donut ...")
sector = port.groupby("sector")["weight_pct"].mean().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 8))
wedges, texts, autotexts = ax.pie(
    sector.values, labels=sector.index,
    autopct="%1.1f%%", startangle=90, pctdistance=0.82,
    colors=sns.color_palette("Set3", len(sector)),
    wedgeprops=dict(width=0.5)
)
for t in autotexts: t.set_fontsize(8)
ax.set_title("Sector Allocation Across Equity Funds",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(CHARTS / "11_sector_donut.png", dpi=150)
plt.close()
print("  Saved 11_sector_donut.png")

# ── Chart 12 — SIP YoY Bar ────────────────────────────────────
print("Chart 12: SIP YoY ...")
sip_yr = sip.groupby(sip["month"].dt.year)["sip_inflow_crore"].sum().reset_index()
sip_yr.columns = ["year","total_sip"]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(sip_yr["year"].astype(str), sip_yr["total_sip"]/1000,
              color=["#42A5F5","#66BB6A","#FFA726","#EF5350"])
for bar, val in zip(bars, sip_yr["total_sip"]/1000):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
            f"₹{val:.0f}K Cr", ha="center", fontsize=9, fontweight="bold")
ax.set_title("Year-wise Total SIP Inflows", fontsize=13, fontweight="bold")
ax.set_xlabel("Year")
ax.set_ylabel("Total SIP (₹ '000 Crore)")
plt.tight_layout()
plt.savefig(CHARTS / "12_sip_yoy.png", dpi=150)
plt.close()
print("  Saved 12_sip_yoy.png")

# ── Chart 13 — Payment Mode ───────────────────────────────────
print("Chart 13: Payment mode ...")
pay = txn["payment_mode"].value_counts()
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x=pay.index, y=pay.values, palette="Set2", ax=ax)
for i, v in enumerate(pay.values):
    ax.text(i, v+50, str(v), ha="center", fontsize=9, fontweight="bold")
ax.set_title("Transactions by Payment Mode", fontsize=13, fontweight="bold")
ax.set_xlabel("Payment Mode")
ax.set_ylabel("Number of Transactions")
plt.tight_layout()
plt.savefig(CHARTS / "13_payment_mode.png", dpi=150)
plt.close()
print("  Saved 13_payment_mode.png")

# ── Chart 14 — Folio Breakdown Stacked Area ───────────────────
print("Chart 14: Folio breakdown ...")
fig, ax = plt.subplots(figsize=(13, 5))
ax.stackplot(folio["month"],
             folio["equity_folios_crore"],
             folio["debt_folios_crore"],
             folio["hybrid_folios_crore"],
             folio["others_folios_crore"],
             labels=["Equity","Debt","Hybrid","Others"],
             colors=["#42A5F5","#EF5350","#66BB6A","#FFA726"],
             alpha=0.85)
ax.set_title("Folio Count by Category Over Time",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Folios (Crore)")
ax.legend(loc="upper left")
plt.tight_layout()
plt.savefig(CHARTS / "14_folio_breakdown.png", dpi=150)
plt.close()
print("  Saved 14_folio_breakdown.png")

# ── Chart 15 — Expense vs Sharpe Scatter ─────────────────────
print("Chart 15: Expense vs Sharpe ...")
fig, ax = plt.subplots(figsize=(10, 6))
scatter = ax.scatter(perf["expense_ratio_pct"], perf["sharpe_ratio"],
                     c=perf["return_3yr_pct"], cmap="RdYlGn",
                     s=80, alpha=0.8, edgecolors="gray", linewidth=0.5)
plt.colorbar(scatter, ax=ax, label="3-Year Return (%)")
ax.axvline(1.0, color="red", linestyle="--",
           alpha=0.5, label="1% threshold")
ax.set_title("Expense Ratio vs Sharpe Ratio",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Expense Ratio (%)")
ax.set_ylabel("Sharpe Ratio")
ax.legend()
plt.tight_layout()
plt.savefig(CHARTS / "15_expense_vs_sharpe.png", dpi=150)
plt.close()
print("  Saved 15_expense_vs_sharpe.png")

print(f"\n✅ All 15 charts saved to {CHARTS}")