"""Robustness checks: concentration of new-customer revenue, and market split by customer type.

Run from project root after analysis.py: python outputs/doanh-thu-2011-vs-2010/concentration_check.py
"""
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent
cust = pd.read_csv(OUT / "customer_segments.csv", index_col=0)
ct = pd.read_csv(OUT / "delta_by_country_segment.csv")

new = cust[cust["segment"] == "Khách mới (lần đầu mua 2011)"].sort_values("R2011", ascending=False)
tot_new = new["R2011"].sum()
print("New customers:", len(new), "revenue 2011 =", round(tot_new, 2))
for k in (1, 5, 10, 20, 50):
    print(f"  top {k:>2} new customers share of new revenue: {new['R2011'].head(k).sum() / tot_new * 100:.1f}%")

lost = cust[cust["segment"] == "Khách cũ - ngừng mua 2011"].sort_values("R2010", ascending=False)
tot_lost = lost["R2010"].sum()
print("Churned customers:", len(lost), "2010 revenue =", round(tot_lost, 2))
for k in (1, 5, 10, 20):
    print(f"  top {k:>2} churned customers share of churned revenue: {lost['R2010'].head(k).sum() / tot_lost * 100:.1f}%")

# per-customer economics and retention (identified customers only)
kept = cust[cust["segment"] == "Khách cũ - tiếp tục mua"]
n10 = int(cust["A2010"].sum())
print("\nActive identified customers 2010 window:", n10,
      "| retained into 2011:", len(kept), f"({len(kept)/n10*100:.1f}%)",
      "| churned:", len(lost), f"({len(lost)/n10*100:.1f}%)")
print("Avg revenue per retained customer: 2010 = %.0f, 2011 = %.0f (%+.1f%%)" % (
    kept["R2010"].mean(), kept["R2011"].mean(), (kept["R2011"].mean() / kept["R2010"].mean() - 1) * 100))
print("Avg 2011 revenue per new customer = %.0f (n=%d)" % (new["R2011"].mean(), len(new)))
print("Avg 2010 revenue per churned customer = %.0f (n=%d)" % (lost["R2010"].mean(), len(lost)))

# market x segment, UK vs rest of world
ct["market"] = ct["Country"].where(ct["Country"] == "United Kingdom", "Ngoài UK")
pv = ct.pivot_table(index="market", columns="segment", values="delta", aggfunc="sum", fill_value=0)
print("\nDelta by market x segment:\n", pv.round(0).to_string())

top_mkts = ["Australia", "France", "Netherlands", "Germany", "EIRE", "Spain", "Japan", "Norway", "Denmark", "Sweden"]
sub = ct[ct["Country"].isin(top_mkts)].pivot_table(index="Country", columns="segment", values="delta",
                                                   aggfunc="sum", fill_value=0)
print("\nDelta by top market x segment:\n", sub.round(0).to_string())
