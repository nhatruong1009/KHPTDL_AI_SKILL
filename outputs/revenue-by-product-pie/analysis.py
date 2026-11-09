"""Pie chart of revenue by product line.
Run from the project root: python outputs/revenue-by-product-pie/analysis.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).parent
df = pd.read_csv("sales_data_sample.csv", encoding="cp1252")
print("rows:", len(df), "| SALES missing:", df.SALES.isna().sum(), "| PRODUCTLINE missing:", df.PRODUCTLINE.isna().sum())
d = df[df.STATUS != "Cancelled"]
print("rows used (excluding Cancelled):", len(d))

rev = d.groupby("PRODUCTLINE").SALES.sum().sort_values(ascending=False)
res = pd.DataFrame({"revenue": rev, "share_pct": rev / rev.sum() * 100,
                    "lines": d.groupby("PRODUCTLINE").size()}).loc[rev.index]  # keep sorted by revenue
all_rev = df.groupby("PRODUCTLINE").SALES.sum()
res["share_pct_incl_cancelled"] = (all_rev / all_rev.sum() * 100).reindex(res.index)
print(res.round(2).to_string())
print("total:", round(rev.sum(), 2), "| shares sum:", round(res.share_pct.sum(), 2))
res.round(2).to_csv(OUT / "revenue_by_productline.csv")

palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]
fig, ax = plt.subplots(figsize=(9, 7.5))
wedges, _ = ax.pie(res.revenue, startangle=90, counterclock=False, colors=palette[:len(res)],
                   wedgeprops={"edgecolor": "white", "linewidth": 1.5})
for w, (name, row) in zip(wedges, res.iterrows()):
    ang = (w.theta2 + w.theta1) / 2

    x, y = np.cos(np.deg2rad(ang)), np.sin(np.deg2rad(ang))
    ax.annotate(f"{name}\n{row.share_pct:.1f}%  ({row.revenue / 1e6:.2f}M)",
                xy=(0.98 * x, 0.98 * y),
                xytext=(0.45, 1.2) if row.share_pct < 3 else (1.28 * x, 1.22 * y),  # tiny slice: move label aside
                ha="left" if (x >= 0 or row.share_pct < 3) else "right", va="center", fontsize=10,
                arrowprops={"arrowstyle": "-", "color": "#888", "lw": 0.8})
ax.set_aspect("equal")
top = res.index[0]
ratio = res.revenue.iloc[0] / res.revenue.iloc[1]
print(f"top: {top}, second: {res.index[1]}, ratio: {ratio:.2f}")
ax.set_title(f"{top} chiếm {res.share_pct.iloc[0]:.0f}% doanh thu - gấp {ratio:.1f} lần {res.index[1]} (thứ hai)",
             fontsize=13, loc="left", pad=28)
fig.text(0.01, 0.01, f"Doanh thu = tổng SALES 01/2003-05/2005, bỏ đơn Cancelled (tổng {rev.sum() / 1e6:.2f}M USD, "
         f"n = {len(d):,} dòng). Nguồn: sales_data_sample.csv.", fontsize=8, color="#555")
fig.tight_layout()
fig.savefig(OUT / "revenue_by_product_pie.png", dpi=150, bbox_inches="tight")
print("saved", OUT / "revenue_by_product_pie.png")
