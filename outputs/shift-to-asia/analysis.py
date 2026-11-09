"""What if the business shifts its market focus to Asia?
Descriptive + scenario arithmetic only (no causal / demand data available).
Run from the project root: python outputs/shift-to-asia/analysis.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
from scipy import stats

OUT = Path(__file__).parent
ASIA = ["Japan", "Singapore", "Philippines"]

df = pd.read_csv("sales_data_sample.csv", encoding="cp1252", keep_default_na=False, na_values=[""])
df["DATE"] = pd.to_datetime(df["ORDERDATE"], format="%m/%d/%Y %H:%M")
d = df[df.STATUS != "Cancelled"].copy()
print("rows:", len(df), "| non-cancelled used:", len(d))


def region(c):
    if c in ASIA:
        return "Asia"
    if c == "Australia":
        return "Australia"
    if c in ("USA", "Canada"):
        return "North America"
    return "Europe"


d["REGION"] = d.COUNTRY.map(region)
print("countries per region:", d.groupby("REGION").COUNTRY.unique().apply(list).to_dict())

L12 = (d.DATE >= "2004-06-01") & (d.DATE <= "2005-05-31")
P12 = (d.DATE >= "2003-06-01") & (d.DATE <= "2004-05-31")

# ---------- Q1: size and growth by region ----------
r = pd.DataFrame({
    "rev_total": d.groupby("REGION").SALES.sum(),
    "rev_L12M": d[L12].groupby("REGION").SALES.sum(),
    "rev_P12M": d[P12].groupby("REGION").SALES.sum(),
    "orders_total": d.groupby("REGION").ORDERNUMBER.nunique(),
    "orders_L12M": d[L12].groupby("REGION").ORDERNUMBER.nunique(),
    "customers_total": d.groupby("REGION").CUSTOMERNAME.nunique(),
    "customers_2005": d[d.YEAR_ID == 2005].groupby("REGION").CUSTOMERNAME.nunique(),
}).fillna(0)
r["share_total_pct"] = r.rev_total / r.rev_total.sum() * 100
r["share_L12M_pct"] = r.rev_L12M / r.rev_L12M.sum() * 100
r["growth_L12M_pct"] = (r.rev_L12M / r.rev_P12M - 1) * 100
r = r.sort_values("rev_L12M", ascending=False)
print("\n=== Region summary ===\n", r.round(1).to_string())
r.round(2).to_csv(OUT / "region_summary.csv")

asia = d[d.REGION == "Asia"]
print("\n=== Asia by country ===")
ac = asia.groupby("COUNTRY").agg(revenue=("SALES", "sum"), orders=("ORDERNUMBER", "nunique"),
                                 customers=("CUSTOMERNAME", "nunique"), first=("DATE", "min"), last=("DATE", "max"))
print(ac.round(0).to_string())
print("\nAsia customers:\n", asia.groupby(["COUNTRY", "CUSTOMERNAME"]).agg(
    revenue=("SALES", "sum"), orders=("ORDERNUMBER", "nunique"), last=("DATE", "max")).round(0).to_string())
print("\nAsia revenue by year:", asia.groupby("YEAR_ID").SALES.sum().round(0).to_dict())

# ---------- Q2: is Asian business different? (order level) ----------
orders = d.groupby(["ORDERNUMBER", "REGION"]).agg(order_value=("SALES", "sum"), lines=("SALES", "size"),
                                                   qty=("QUANTITYORDERED", "sum")).reset_index()
print("\n=== Order value by region (per order) ===")
print(orders.groupby("REGION").order_value.describe()[["count", "mean", "50%"]].round(0).to_string())
a_val = orders.loc[orders.REGION == "Asia", "order_value"]
o_val = orders.loc[orders.REGION != "Asia", "order_value"]
u = stats.mannwhitneyu(a_val, o_val, alternative="two-sided")
print(f"Asia vs rest order value: median {a_val.median():,.0f} vs {o_val.median():,.0f}; "
      f"Mann-Whitney U p = {u.pvalue:.3f} (n = {len(a_val)} vs {len(o_val)})")

d["discount_vs_msrp_pct"] = (1 - d.PRICEEACH / d.MSRP) * 100
print("\nAvg price vs MSRP (negative = above MSRP):",
      d.groupby(d.REGION.eq("Asia").map({True: "Asia", False: "Rest"})).discount_vs_msrp_pct.mean().round(1).to_dict())

mix = pd.crosstab(d.REGION.eq("Asia").map({True: "Asia", False: "Rest"}), d.PRODUCTLINE,
                  values=d.SALES, aggfunc="sum", normalize="index") * 100
print("\nProduct line mix (% of revenue):\n", mix.round(1).to_string())
deal = pd.crosstab(d.REGION.eq("Asia").map({True: "Asia", False: "Rest"}), d.DEALSIZE, normalize="index") * 100
print("\nDeal size mix (% of lines):\n", deal.round(1).to_string())
mix.round(2).to_csv(OUT / "productline_mix_asia_vs_rest.csv")

# ---------- Q3: scenarios (pure arithmetic on L12M revenue) ----------
total = r.rev_L12M.sum()
asia_l12 = r.loc["Asia", "rev_L12M"]
non_asia = total - asia_l12
usa_l12 = d[L12 & (d.COUNTRY == "USA")].SALES.sum()
print("\n=== Scenarios (L12M base) ===")
print(f"Total L12M: {total:,.0f} | Asia: {asia_l12:,.0f} ({asia_l12 / total * 100:.1f}%) | non-Asia: {non_asia:,.0f}")
scen = []
for lost_pct in (10, 25, 50, 100):
    lost = non_asia * lost_pct / 100
    need_mult = (asia_l12 + lost) / asia_l12
    scen.append({"non_asia_revenue_lost_pct": lost_pct, "revenue_lost": lost,
                 "asia_needed_to_break_even": asia_l12 + lost, "asia_multiple_needed": need_mult})
scen = pd.DataFrame(scen)
print(scen.round(2).to_string(index=False))
print(f"USA alone (L12M) = {usa_l12:,.0f} = {usa_l12 / asia_l12:.1f}x Asia")
asia_growth = r.loc["Asia", "growth_L12M_pct"]
print(f"Asia growth last 12M vs previous 12M: {asia_growth:+.1f}%")
scen.round(2).to_csv(OUT / "scenarios.csv", index=False)

# Sensitivity: APAC incl. Australia
apac = r.loc[["Asia", "Australia"], "rev_L12M"].sum()
print(f"Sensitivity - Asia + Australia L12M: {apac:,.0f} ({apac / total * 100:.1f}%)")

# ---------- Chart 1: revenue by region per quarter ----------
d["Q"] = d.DATE.dt.to_period("Q").astype(str)
qr = d.pivot_table(index="Q", columns="REGION", values="SALES", aggfunc="sum", fill_value=0) / 1e3
order = ["North America", "Europe", "Australia", "Asia"]
colors = {"North America": "#b0b7bf", "Europe": "#cfd4da", "Australia": "#8fa3b8", "Asia": "#d62728"}
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(12, 5.5))
bottom = pd.Series(0.0, index=qr.index)
for reg in order:
    ax.bar(qr.index, qr[reg], bottom=bottom, color=colors[reg], label=reg, edgecolor="white", lw=0.5)
    bottom += qr[reg]
for i, q in enumerate(qr.index):
    v = qr.loc[q, "Asia"]
    if v > 0:
        ax.text(i, bottom[q] + 15, f"{v:,.0f}K", ha="center", fontsize=8, color="#d62728")
ax.set_ylabel("Doanh thu (nghìn USD)")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{v:,.0f}K"))
ax.set_title(f"Châu Á chỉ chiếm {asia_l12 / total * 100:.1f}% doanh thu 12 tháng gần nhất "
             f"(số đỏ = doanh thu châu Á mỗi quý)", fontsize=12.5, loc="left")
ax.legend(frameon=False, ncol=4, loc="upper left")
ax.tick_params(axis="x", rotation=45)
fig.text(0.01, -0.03, "Châu Á = Japan, Singapore, Philippines. Doanh thu = SALES, bỏ đơn Cancelled. "
         "Q2-2005 chỉ có tháng 4-5. Nguồn: sales_data_sample.csv.", fontsize=8, color="#555")
fig.tight_layout()
fig.savefig(OUT / "revenue_by_region.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------- Chart 2: scenario - how big Asia must become ----------
fig, ax = plt.subplots(figsize=(11, 5.5))
labels = ["Châu Á hiện tại"] + [f"Bù {p}% doanh thu\nthị trường khác" for p in scen.non_asia_revenue_lost_pct]
vals = [asia_l12 / 1e3] + list(scen.asia_needed_to_break_even / 1e3)
cols = ["#d62728"] + ["#b0b7bf"] * len(scen)
bars = ax.bar(labels, vals, color=cols)
for b, v, mlt in zip(bars, vals, [1.0] + list(scen.asia_multiple_needed)):
    ax.text(b.get_x() + b.get_width() / 2, v, f"{v:,.0f}K\n(x{mlt:.1f})", ha="center", va="bottom", fontsize=9.5)
ax.set_ylim(0, max(vals) * 1.18)
ax.set_ylabel("Doanh thu châu Á cần có / 12 tháng (nghìn USD)")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{v:,.0f}K"))
ax.set_title(f"Mất 25% doanh thu thị trường khác thì châu Á phải tăng x{scen.loc[1, 'asia_multiple_needed']:.0f} mới bù được",
             fontsize=12.5, loc="left")
fig.text(0.01, -0.03, f"Kịch bản số học trên doanh thu 12 tháng gần nhất (06/2004-05/2005). (xN) = gấp N lần châu Á hiện tại. "
         f"Doanh thu châu Á 12 tháng qua: {asia_growth:+.1f}% so với 12 tháng trước (gần như đi ngang).", fontsize=8, color="#555")
fig.tight_layout()
fig.savefig(OUT / "scenario_asia_needed.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\nSaved charts to", OUT)
