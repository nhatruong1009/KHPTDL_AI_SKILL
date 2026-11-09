"""Which market to focus on for revenue growth next quarter (Q3-2005).
Run from the project root: python outputs/market-focus-next-quarter/analysis.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

OUT = Path(__file__).parent
MIN_ORDERS = 10  # below this, growth figures are too noisy to rank on
OFFSETS = {"Spain": (8, -22), "France": (-10, 10), "Denmark": (-58, 4), "Singapore": (8, -20), "Norway": (8, 6)}  # avoid label overlap

# keep_default_na=False: TERRITORY "NA" means North America, not missing
df = pd.read_csv("sales_data_sample.csv", encoding="cp1252", keep_default_na=False, na_values=[""])
df["DATE"] = pd.to_datetime(df["ORDERDATE"], format="%m/%d/%Y %H:%M")
print("rows:", len(df), "| range:", df.DATE.min().date(), "->", df.DATE.max().date())
canc = df["STATUS"].eq("Cancelled")
print(f"Cancelled rows excluded: {canc.sum()} ({df.loc[canc, 'SALES'].sum():,.0f} USD)")
d = df[~canc].copy()
print("rows used:", len(d))

# Windows
L12 = (d.DATE >= "2004-06-01") & (d.DATE <= "2005-05-31")
P12 = (d.DATE >= "2003-06-01") & (d.DATE <= "2004-05-31")
JM05 = (d.YEAR_ID == 2005) & (d.MONTH_ID <= 5)
JM04 = (d.YEAR_ID == 2004) & (d.MONTH_ID <= 5)
Q3_03 = (d.YEAR_ID == 2003) & (d.QTR_ID == 3)
Q3_04 = (d.YEAR_ID == 2004) & (d.QTR_ID == 3)

g = d.groupby("COUNTRY")
m = pd.DataFrame({
    "rev_L12M": d[L12].groupby("COUNTRY").SALES.sum(),
    "rev_P12M": d[P12].groupby("COUNTRY").SALES.sum(),
    "rev_JanMay05": d[JM05].groupby("COUNTRY").SALES.sum(),
    "rev_JanMay04": d[JM04].groupby("COUNTRY").SALES.sum(),
    "rev_Q3_03": d[Q3_03].groupby("COUNTRY").SALES.sum(),
    "rev_Q3_04": d[Q3_04].groupby("COUNTRY").SALES.sum(),
    "orders_L12M": d[L12].groupby("COUNTRY").ORDERNUMBER.nunique(),
    "customers_L12M": d[L12].groupby("COUNTRY").CUSTOMERNAME.nunique(),
    "customers_2005": d[d.YEAR_ID == 2005].groupby("COUNTRY").CUSTOMERNAME.nunique(),
    "territory": g.TERRITORY.agg(lambda s: "/".join(sorted(s.unique()))),
}).fillna({c: 0 for c in ["rev_L12M", "rev_P12M", "rev_JanMay05", "rev_JanMay04", "rev_Q3_03", "rev_Q3_04",
                          "orders_L12M", "customers_L12M", "customers_2005"]})

first_order = d.groupby("CUSTOMERNAME").DATE.min()
newc = d[L12 & d.CUSTOMERNAME.map(first_order).ge(pd.Timestamp("2004-06-01"))]
m["new_customers_L12M"] = newc.groupby("COUNTRY").CUSTOMERNAME.nunique()
m["new_customers_L12M"] = m["new_customers_L12M"].fillna(0)
top_cust = d[L12].groupby(["COUNTRY", "CUSTOMERNAME"]).SALES.sum().groupby("COUNTRY").max()
m["top_customer_share_pct"] = (top_cust / m["rev_L12M"] * 100).round(1)

m["growth_abs_L12M"] = m.rev_L12M - m.rev_P12M
m["growth_pct_L12M"] = (m.growth_abs_L12M / m.rev_P12M.replace(0, float("nan")) * 100)
m["growth_pct_JanMay"] = ((m.rev_JanMay05 / m.rev_JanMay04.replace(0, float("nan")) - 1) * 100)
m["growth_pct_Q3"] = ((m.rev_Q3_04 / m.rev_Q3_03.replace(0, float("nan")) - 1) * 100)
m["share_L12M_pct"] = m.rev_L12M / m.rev_L12M.sum() * 100
m["share_of_growth_pct"] = m.growth_abs_L12M / m.growth_abs_L12M.sum() * 100
m["reliable"] = m.orders_L12M >= MIN_ORDERS
m = m.sort_values("rev_L12M", ascending=False)

print(f"\nTotal L12M: {m.rev_L12M.sum():,.0f} | P12M: {m.rev_P12M.sum():,.0f} | "
      f"growth {m.growth_abs_L12M.sum() / m.rev_P12M.sum() * 100:+.1f}%")
cols = ["territory", "rev_L12M", "share_L12M_pct", "rev_P12M", "growth_abs_L12M", "growth_pct_L12M",
        "share_of_growth_pct", "growth_pct_JanMay", "rev_Q3_04", "growth_pct_Q3", "orders_L12M",
        "customers_L12M", "new_customers_L12M", "customers_2005", "top_customer_share_pct", "reliable"]
print(m[cols].round(1).to_string())
m[cols].round(2).to_csv(OUT / "market_metrics.csv")

# Q3 seasonality overall
q = d.groupby(["YEAR_ID", "QTR_ID"]).SALES.sum().unstack()
print("\nRevenue by quarter (USD):\n", q.round(0).to_string())
print("Q3 share of year: 2003 {:.1f}% | 2004 {:.1f}%".format(q.loc[2003, 3] / q.loc[2003].sum() * 100,
                                                          q.loc[2004, 3] / q.loc[2004].sum() * 100))

# Robustness: Shipped/Resolved only (excludes pending In Process / On Hold / Disputed)
done = d[d.STATUS.isin(["Shipped", "Resolved"])]
rL = done[(done.DATE >= "2004-06-01") & (done.DATE <= "2005-05-31")].groupby("COUNTRY").SALES.sum()
rP = done[(done.DATE >= "2003-06-01") & (done.DATE <= "2004-05-31")].groupby("COUNTRY").SALES.sum()
rob = pd.DataFrame({"L12M_done": rL, "P12M_done": rP}).fillna(0)
rob["growth_abs_done"] = rob.L12M_done - rob.P12M_done
rob["growth_pct_done"] = rob.growth_abs_done / rob.P12M_done * 100
print("\nRobustness (Shipped/Resolved only), top 8 by L12M:\n",
      rob.sort_values("L12M_done", ascending=False).head(8).round(1).to_string())

# Product lines in the reliable markets, L12M vs P12M
rel = m[m.reliable].index.tolist()
pl = (d[(L12 | P12) & d.COUNTRY.isin(rel)]
      .assign(window=lambda x: x.DATE.ge("2004-06-01").map({True: "L12M", False: "P12M"}))
      .pivot_table(index=["COUNTRY", "PRODUCTLINE"], columns="window", values="SALES", aggfunc="sum", fill_value=0))
pl["growth_abs"] = pl.L12M - pl.P12M
pl.round(0).to_csv(OUT / "productline_by_market.csv")
print("\nTop product-line growth within reliable markets:")
for c in rel:
    print(" ", c, ":", ", ".join(f"{p} {v:+,.0f}" for p, v in
                               pl.loc[c].growth_abs.sort_values(ascending=False).head(3).items()))

# ---------- Chart 1: priority map (size vs growth) ----------
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(12, 7))
x = m.rev_L12M / 1e3
y = m.growth_pct_L12M
for c in m.index:
    r = m.loc[c]
    color = "#1f77b4" if r.reliable else "#b0b7bf"
    ax.scatter(r.rev_L12M / 1e3, r.growth_pct_L12M, s=60 + r.customers_L12M * 25, color=color,
               alpha=0.8, edgecolor="white", zorder=3)
    ax.annotate(f"{c}\n({int(r.orders_L12M)} đơn)", (r.rev_L12M / 1e3, r.growth_pct_L12M),
                textcoords="offset points", xytext=OFFSETS.get(c, (8, 4)), fontsize=8.5,
                color="#111" if r.reliable else "#777")
total_g = m.growth_abs_L12M.sum() / m.rev_P12M.sum() * 100
ax.axhline(total_g, color="#d62728", lw=1, ls="--")
ax.text(x.max(), total_g, f" Tăng trưởng chung {total_g:+.0f}%",
        color="#d62728", va="bottom", ha="right", fontsize=9)
ax.axhline(0, color="#444", lw=0.8)
ax.set_xscale("log")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{v:,.0f}K"))
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_xlabel("Doanh thu 12 tháng gần nhất (06/2004-05/2005, nghìn USD, thang log)")
ax.set_ylabel("Tăng trưởng so với 12 tháng trước đó")
ax.set_title("USA lớn gấp 3 thị trường kế tiếp và vẫn tăng +20%; % tăng cao ở thị trường nhỏ (xám) dựa trên quá ít đơn",
             fontsize=12, loc="left")
ax.grid(alpha=0.25)
fig.text(0.01, -0.02, f"Kích thước điểm = số khách hàng 12 tháng gần nhất. Xanh = >= {MIN_ORDERS} đơn; xám = < {MIN_ORDERS} đơn. "
         "Doanh thu = SALES, đã bỏ đơn Cancelled. Nguồn: sales_data_sample.csv.", fontsize=8, color="#555")
fig.tight_layout()
fig.savefig(OUT / "market_priority_map.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------- Chart 2: contribution to growth (absolute USD) ----------
top = m.sort_values("growth_abs_L12M", ascending=True)
fig, ax = plt.subplots(figsize=(10, 7))
colors = ["#1f77b4" if (v > 0 and r) else ("#d62728" if v < 0 else "#b0b7bf")
          for v, r in zip(top.growth_abs_L12M, top.reliable)]
bars = ax.barh(top.index, top.growth_abs_L12M / 1e3, color=colors)
for b, v, p in zip(bars, top.growth_abs_L12M / 1e3, top.share_of_growth_pct):
    ax.text(v + (8 if v >= 0 else -8), b.get_y() + b.get_height() / 2, f"{v:+,.0f}K ({p:.0f}%)",
            va="center", ha="left" if v >= 0 else "right", fontsize=8.5)
ax.axvline(0, color="#444", lw=0.8)
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{v:,.0f}K"))
ax.set_xlabel("Doanh thu tăng thêm (12 tháng gần nhất so với 12 tháng trước, nghìn USD)")
ax.set_title("USA đóng góp 1/4 mức tăng doanh thu; phần còn lại rải rác ở nhiều thị trường", fontsize=12.5, loc="left")
lim = top.growth_abs_L12M.abs().max() / 1e3 * 1.35
ax.set_xlim(min(-lim * 0.3, top.growth_abs_L12M.min() / 1e3 * 1.6), lim)
fig.text(0.01, -0.02, f"(%) = tỷ trọng trong tổng mức tăng. Xanh = >= {MIN_ORDERS} đơn; xám = ít đơn; đỏ = giảm.",
         fontsize=8, color="#555")
fig.tight_layout()
fig.savefig(OUT / "growth_contribution.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\nSaved charts to", OUT)
