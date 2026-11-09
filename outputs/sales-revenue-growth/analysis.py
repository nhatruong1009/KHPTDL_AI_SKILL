"""Revenue growth from sales_data_sample.csv.
Run from the project root: python outputs/sales-revenue-growth/analysis.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

OUT = Path(__file__).parent
df = pd.read_csv("sales_data_sample.csv", encoding="cp1252")
df["ORDERDATE"] = pd.to_datetime(df["ORDERDATE"], format="%m/%d/%Y %H:%M")
print("rows:", len(df), "| date range:", df["ORDERDATE"].min().date(), "->", df["ORDERDATE"].max().date())
print("SALES missing:", df["SALES"].isna().sum())

# Status mix (revenue is the SALES column for all order lines; status shown for transparency)
status = df.groupby("STATUS")["SALES"].agg(["count", "sum"])
status["pct_sales"] = (status["sum"] / status["sum"].sum() * 100).round(2)
print("\nSales by STATUS:\n", status.round(2))

# Consistency: date-derived year/month vs YEAR_ID/MONTH_ID
mism = ((df["ORDERDATE"].dt.year != df["YEAR_ID"]) | (df["ORDERDATE"].dt.month != df["MONTH_ID"])).sum()
print("rows where ORDERDATE disagrees with YEAR_ID/MONTH_ID:", mism)

# Monthly revenue (all months kept, none silently missing)
monthly = df.set_index("ORDERDATE")["SALES"].resample("MS").sum()
monthly = monthly.to_frame("revenue")
monthly["year"] = monthly.index.year
monthly["month"] = monthly.index.month
monthly["yoy_pct"] = monthly["revenue"].pct_change(12) * 100
monthly["mom_pct"] = monthly["revenue"].pct_change() * 100
print("\nMonths:", len(monthly), "| zero-revenue months:", int((monthly["revenue"] == 0).sum()))
monthly.round(2).to_csv(OUT / "monthly_revenue.csv")
print(monthly.round(1).to_string())

# Yearly totals and like-for-like Jan-May
yearly = df.groupby("YEAR_ID")["SALES"].sum().to_frame("full_year")
yearly["months_covered"] = df.groupby("YEAR_ID")["MONTH_ID"].nunique()
yearly["jan_may"] = df[df["MONTH_ID"] <= 5].groupby("YEAR_ID")["SALES"].sum()
yearly["full_year_growth_pct"] = yearly["full_year"].pct_change() * 100
yearly["jan_may_growth_pct"] = yearly["jan_may"].pct_change() * 100
yearly.round(2).to_csv(OUT / "yearly_revenue.csv")
print("\nYearly:\n", yearly.round(1).to_string())
print("\nTotal SALES:", round(df["SALES"].sum(), 2), "| sum of monthly:", round(monthly["revenue"].sum(), 2))

# ---------- Chart 1: monthly revenue over time ----------
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(12, 5.5))
colors = {2003: "#9aa5b1", 2004: "#1f77b4", 2005: "#d62728"}
ax.plot(monthly.index, monthly["revenue"] / 1e3, color="#555", lw=1, alpha=0.5, zorder=1)
for y, g in monthly.groupby("year"):
    ax.plot(g.index, g["revenue"] / 1e3, marker="o", ms=4, lw=2, color=colors.get(y, "k"), label=str(y), zorder=2)
for d in monthly.loc[monthly["month"] == 11].index:  # annotate November peaks
    v = monthly.loc[d, "revenue"] / 1e3
    ax.annotate(f"{v:,.0f}K", (d, v), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
ax.set_ylim(0, None)
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}K"))
ax.set_ylabel("Doanh thu (nghìn USD)")
ax.set_xlabel("Tháng")
ax.set_title("Doanh thu theo tháng tăng qua các năm, đỉnh mùa vụ vào tháng 11", fontsize=13, loc="left")
ax.legend(title="Năm", frameon=False)
ax.grid(axis="y", alpha=0.3)
fig.text(0.01, -0.02, f"Nguồn: sales_data_sample.csv, n = {len(df):,} dòng đơn hàng; doanh thu = tổng SALES mọi trạng thái. "
         "Năm 2005 chỉ có dữ liệu đến 31/05.", fontsize=8, color="#555")
fig.tight_layout()
fig.savefig(OUT / "monthly_revenue.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------- Chart 2: yearly growth, full year vs Jan-May ----------
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, col, title in [
    (axes[0], "full_year", "Cả năm (2005 chỉ có 5 tháng)"),
    (axes[1], "jan_may", "So sánh cùng kỳ: tháng 1-5"),
]:
    vals = yearly[col] / 1e6
    bars = ax.bar(vals.index.astype(str), vals, color=[colors[y] for y in vals.index])
    gcol = "full_year_growth_pct" if col == "full_year" else "jan_may_growth_pct"
    for b, y in zip(bars, vals.index):
        g = yearly.loc[y, gcol]
        partial = col == "full_year" and yearly.loc[y, "months_covered"] < 12
        if partial:
            label = f"{vals[y]:.2f}M\n(chỉ 5 tháng)"
        else:
            label = f"{vals[y]:.2f}M" + ("" if pd.isna(g) else f"\n({g:+.1f}%)")
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(), label, ha="center", va="bottom", fontsize=10)
    ax.set_ylim(0, vals.max() * 1.25)
    ax.set_title(title, fontsize=11)
    ax.set_ylabel("Doanh thu (triệu USD)")
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:.2f}M"))
fig.suptitle("Doanh thu tăng mỗi năm: +34% năm 2004; cùng kỳ tháng 1-5 tăng +57% (2004) và +36% (2005)",
             fontsize=13, x=0.01, ha="left")
fig.text(0.01, -0.02, "% trong ngoặc = tăng trưởng so với năm trước. Không so sánh cột 2005 ở biểu đồ trái vì thiếu tháng 6-12.",
         fontsize=8, color="#555")
fig.tight_layout()
fig.savefig(OUT / "yearly_growth.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\nSaved charts to", OUT)
