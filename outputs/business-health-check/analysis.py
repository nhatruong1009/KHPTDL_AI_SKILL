"""Business health check: scan for warning signals in sales_data_sample.csv.
Run from the project root: python outputs/business-health-check/analysis.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

OUT = Path(__file__).parent
df = pd.read_csv("sales_data_sample.csv", encoding="cp1252", keep_default_na=False, na_values=[""])
df["DATE"] = pd.to_datetime(df["ORDERDATE"], format="%m/%d/%Y %H:%M")
df["Q"] = df.DATE.dt.to_period("Q").astype(str)
print("rows:", len(df), "| range:", df.DATE.min().date(), "->", df.DATE.max().date())
JM = df.MONTH_ID <= 5  # like-for-like window: Jan-May (2005 data ends 31 May)

# ---------- 1. Revenue like-for-like ----------
print("\n[1] Revenue Jan-May by year (all statuses / excluding Cancelled):")
r1 = pd.DataFrame({
    "all": df[JM].groupby("YEAR_ID").SALES.sum(),
    "excl_cancelled": df[JM & (df.STATUS != "Cancelled")].groupby("YEAR_ID").SALES.sum(),
    "shipped_resolved": df[JM & df.STATUS.isin(["Shipped", "Resolved"])].groupby("YEAR_ID").SALES.sum(),
})
r1_g = r1.pct_change() * 100
r1["shipped_resolved_inprocess"] = df[JM & df.STATUS.isin(["Shipped", "Resolved", "In Process"])].groupby("YEAR_ID").SALES.sum()
r1_g = r1.pct_change() * 100
print(r1.round(0).to_string()); print("growth %:\n", r1_g.round(1).to_string())
stuck = df[(df.YEAR_ID == 2005) & df.STATUS.isin(["On Hold", "Disputed"])].SALES.sum()
print(f"On Hold + Disputed value in 2005 orders: {stuck:,.0f}")

# ---------- 2. Order status / fulfilment ----------
orders = df.groupby("ORDERNUMBER").agg(DATE=("DATE", "min"), STATUS=("STATUS", "first"), n_status=("STATUS", "nunique"),
                                       value=("SALES", "sum"), customer=("CUSTOMERNAME", "first"),
                                       country=("COUNTRY", "first"), Q=("Q", "first"), YEAR=("YEAR_ID", "first"))
print("\n[2] orders with >1 status:", int((orders.n_status > 1).sum()), "| total orders:", len(orders))
st_q = pd.crosstab(orders.Q, orders.STATUS)
st_q_val = orders.pivot_table(index="Q", columns="STATUS", values="value", aggfunc="sum", fill_value=0)
print("Orders by quarter x status:\n", st_q.to_string())
not_done = orders[~orders.STATUS.isin(["Shipped", "Resolved", "Cancelled"])]
print("\nOpen / problem orders (In Process, On Hold, Disputed):")
print(not_done.groupby("STATUS").agg(orders=("value", "size"), value=("value", "sum"),
                                     oldest=("DATE", "min"), newest=("DATE", "max")).to_string())
print("\nOn Hold & Disputed orders detail:")
print(not_done[not_done.STATUS.isin(["On Hold", "Disputed"])]
      .sort_values("DATE")[["DATE", "STATUS", "customer", "country", "value"]].to_string())
print("\nCancelled orders:")
print(orders[orders.STATUS == "Cancelled"][["DATE", "customer", "country", "value"]].sort_values("DATE").to_string())
print("\nResolved orders by year:", orders[orders.STATUS == "Resolved"].groupby("YEAR").size().to_dict())
problem_share = (orders.assign(prob=~orders.STATUS.eq("Shipped"))
                 .groupby("YEAR").agg(orders=("prob", "size"), not_shipped=("prob", "sum")))
problem_share["pct_not_shipped"] = problem_share.not_shipped / problem_share.orders * 100
print("\nShare of orders not 'Shipped' by year:\n", problem_share.round(1).to_string())

# ---------- 3. Customer retention (like-for-like) ----------
def cust(year, months=None):
    m = df.YEAR_ID == year
    if months:
        m &= df.MONTH_ID <= months
    return set(df[m & (df.STATUS != "Cancelled")].CUSTOMERNAME)

c03, c04, c04_jm, c05_jm = cust(2003), cust(2004), cust(2004, 5), cust(2005, 5)
ret = {
    "2003 customers back in Jan-May 2004": (len(c03 & c04_jm), len(c03)),
    "2004 customers back in Jan-May 2005": (len(c04 & c05_jm), len(c04)),
}
print("\n[3] Retention:")
for k, (a, b) in ret.items():
    print(f"  {k}: {a}/{b} = {a / b * 100:.1f}%")
new05 = c05_jm - c03 - c04
new04 = c04_jm - c03
print(f"  new customers Jan-May 2004: {len(new04)} | Jan-May 2005: {len(new05)}")
print(f"  active customers Jan-May: 2004 {len(c04_jm)} | 2005 {len(c05_jm)}")
lost = df[df.CUSTOMERNAME.isin(c04 - c05_jm) & (df.YEAR_ID == 2004) & (df.STATUS != "Cancelled")]
lost_rev = lost.groupby("CUSTOMERNAME").SALES.sum().sort_values(ascending=False)
print(f"  2004 customers not seen in Jan-May 2005: {len(lost_rev)}, their 2004 revenue = {lost_rev.sum():,.0f} "
      f"({lost_rev.sum() / df[(df.YEAR_ID == 2004) & (df.STATUS != 'Cancelled')].SALES.sum() * 100:.1f}% of 2004)")
print("  top 5 of them:", lost_rev.head(5).round(0).to_dict())

# ---------- 4. Customer concentration ----------
print("\n[4] Concentration (share of revenue, excl. Cancelled):")
ok = df[df.STATUS != "Cancelled"]
for label, m in [("2004", ok.YEAR_ID == 2004), ("Jan-May 2005", (ok.YEAR_ID == 2005))]:
    s = ok[m].groupby("CUSTOMERNAME").SALES.sum().sort_values(ascending=False)
    print(f"  {label}: top1 {s.iloc[0] / s.sum() * 100:.1f}% ({s.index[0]}), top2 {s.iloc[:2].sum() / s.sum() * 100:.1f}%, "
          f"top5 {s.iloc[:5].sum() / s.sum() * 100:.1f}%, customers {len(s)}")
for label, m in [("Jan-May 2004 (like-for-like)", (ok.YEAR_ID == 2004) & (ok.MONTH_ID <= 5))]:
    s = ok[m].groupby("CUSTOMERNAME").SALES.sum().sort_values(ascending=False)
    print(f"  {label}: top1 {s.iloc[0] / s.sum() * 100:.1f}% ({s.index[0]}), top2 {s.iloc[:2].sum() / s.sum() * 100:.1f}%, "
          f"top5 {s.iloc[:5].sum() / s.sum() * 100:.1f}%, customers {len(s)}")
top2_05 = ok[ok.YEAR_ID == 2005].groupby("CUSTOMERNAME").SALES.sum().nlargest(2)
print("  Jan-May 2005 top 2:", top2_05.round(0).to_dict())

# ---------- 5. Shrinking markets / product lines (Jan-May 2005 vs 2004) ----------
print("\n[5] Jan-May 2005 vs 2004, excluding Cancelled:")
okjm = ok[ok.MONTH_ID <= 5]
for dim in ["COUNTRY", "PRODUCTLINE"]:
    t = okjm.pivot_table(index=dim, columns="YEAR_ID", values="SALES", aggfunc="sum", fill_value=0)[[2004, 2005]]
    t["change"] = t[2005] - t[2004]
    t["change_pct"] = t.change / t[2004].replace(0, float("nan")) * 100
    print(f"  by {dim}:\n", t.sort_values("change").round(0).to_string())
    t.round(2).to_csv(OUT / f"janmay_change_by_{dim.lower()}.csv")

# ---------- 6. Growth source: orders vs order size ----------
print("\n[6] Jan-May orders and order value (excl. Cancelled):")
oj = orders[(orders.DATE.dt.month <= 5) & (orders.STATUS != "Cancelled")]
src = oj.groupby("YEAR").agg(orders=("value", "size"), revenue=("value", "sum"), avg_order=("value", "mean"),
                             customers=("customer", "nunique"))
src["orders_per_customer"] = src.orders / src.customers
print(src.round(1).to_string())
src.round(2).to_csv(OUT / "janmay_growth_source.csv")

# ---------- New customers per quarter (first non-cancelled order) ----------
first = ok.groupby("CUSTOMERNAME").DATE.min().dt.to_period("Q").astype(str)
newq = first.value_counts().reindex(sorted(df.Q.unique()), fill_value=0)
activeq = ok.groupby("Q").CUSTOMERNAME.nunique()
nq = pd.DataFrame({"new_customers": newq, "active_customers": activeq})
print("\nNew vs active customers per quarter:\n", nq.to_string())
nq.to_csv(OUT / "customers_per_quarter.csv")

# ---------- Chart 1: order status by quarter ----------
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False})
pct = st_q.div(st_q.sum(axis=1), axis=0) * 100
cols = ["Shipped", "Resolved", "In Process", "On Hold", "Disputed", "Cancelled"]
cols = [c for c in cols if c in pct.columns]
colors = {"Shipped": "#c9d1d9", "Resolved": "#8fa3b8", "In Process": "#f2b134",
          "On Hold": "#e8702a", "Disputed": "#d62728", "Cancelled": "#6b1d1d"}
fig, ax = plt.subplots(figsize=(12, 5.5))
bottom = pd.Series(0.0, index=pct.index)
for c in cols:
    ax.bar(pct.index, pct[c], bottom=bottom, color=colors[c], label=c, edgecolor="white", lw=0.5)
    bottom += pct[c]
for i, q in enumerate(pct.index):
    n_bad = int(st_q.loc[q, [c for c in cols if c != "Shipped"]].sum())
    if n_bad:
        ax.text(i, 101, f"{n_bad}/{int(st_q.loc[q].sum())}", ha="center", fontsize=8.5, color="#333")
ax.set_ylim(0, 110)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylabel("% số đơn hàng trong quý")
ax.tick_params(axis="x", rotation=45)
ax.legend(frameon=False, ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.18))
first05 = pct.index.get_loc("2005Q1")
bad_q2 = int(st_q.loc["2005Q2"].sum() - st_q.loc["2005Q2", "Shipped"])
ax.set_title(f"Q2-2005: {bad_q2}/{int(st_q.loc['2005Q2'].sum())} đơn chưa giao (tạm giữ, tranh chấp, đang xử lý); "
             "trước 2005 gần như mọi đơn đều đã giao", fontsize=12, loc="left")
fig.text(0.01, -0.12, "Số trên cột = số đơn không ở trạng thái Shipped / tổng số đơn trong quý. "
         "Q2-2005 chỉ có tháng 4-5. Nguồn: sales_data_sample.csv.", fontsize=8, color="#555")
fig.tight_layout()
fig.savefig(OUT / "order_status_by_quarter.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------- Chart 2: new vs returning active customers per quarter ----------
fig, ax = plt.subplots(figsize=(12, 5))
ret_c = nq.active_customers - nq.new_customers
ax.bar(nq.index, ret_c, color="#c9d1d9", label="Khách cũ quay lại")
ax.bar(nq.index, nq.new_customers, bottom=ret_c, color="#1f77b4", label="Khách mới (đơn đầu tiên)")
for i, q in enumerate(nq.index):
    ax.text(i, nq.loc[q, "active_customers"] + 0.6, f"{int(nq.loc[q, 'new_customers'])} mới",
            ha="center", fontsize=8.5, color="#d62728" if nq.loc[q, "new_customers"] == 0 else "#1f77b4")
ax.set_ylim(0, nq.active_customers.max() * 1.15)
ax.set_ylabel("Số khách hàng có mua trong quý")
ax.tick_params(axis="x", rotation=45)
ax.legend(frameon=False, loc="upper left")
z = nq.index[nq.new_customers.eq(0)].tolist()
ax.set_title(f"Không có khách hàng mới nào kể từ {z[0] if z else '-'}: tăng trưởng 2005 hoàn toàn đến từ khách cũ",
             fontsize=12, loc="left")
fig.text(0.01, -0.08, "Khách mới = khách có đơn (không hủy) đầu tiên trong quý đó. Q2-2005 chỉ có tháng 4-5. "
         "Nguồn: sales_data_sample.csv.", fontsize=8, color="#555")
fig.tight_layout()
fig.savefig(OUT / "new_vs_returning_customers.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\nSaved charts to", OUT)
