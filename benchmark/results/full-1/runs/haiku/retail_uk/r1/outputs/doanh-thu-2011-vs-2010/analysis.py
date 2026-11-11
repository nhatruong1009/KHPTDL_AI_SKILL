"""Net revenue 2011 vs 2010 (like-for-like window), decomposed by customer type and market.

Run from project root:  python outputs/doanh-thu-2011-vs-2010/analysis.py
Input : data/online_retail_II.xlsx (read-only)
Output: CSVs and PNGs in outputs/doanh-thu-2011-vs-2010/
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

OUT = Path(__file__).resolve().parent
SRC = Path(__file__).resolve().parents[2] / "data" / "online_retail_II.xlsx"
if not SRC.exists():  # fallback when run from project root
    SRC = Path("data/online_retail_II.xlsx")

# ---------------------------------------------------------------- load & clean
x = pd.ExcelFile(SRC)
s1 = x.parse("Year 2009-2010")
s2 = x.parse("Year 2010-2011")

# The two sheets overlap on 1-9 Dec 2010. Use sheet 1 before 1 Dec 2010 and
# sheet 2 from 1 Dec 2010 onward, so each day is counted once.
cut = pd.Timestamp("2010-12-01")
ov1 = s1[s1["InvoiceDate"] >= cut]
ov2 = s2[s2["InvoiceDate"] < pd.Timestamp("2010-12-10")]
overlap_check = {
    "rows_sheet1_dec1_9_2010": len(ov1),
    "rows_sheet2_dec1_9_2010": len(ov2),
}
df = pd.concat([s1[s1["InvoiceDate"] < cut], s2], ignore_index=True)
n_raw = len(df)
df = df.drop_duplicates()  # exact duplicate lines (data-entry duplicates)
n_dedup = n_raw - len(df)

df = df[df["Price"] > 0].copy()  # drop zero/negative price lines (write-offs, tests)
df["Revenue"] = df["Quantity"] * df["Price"]  # net of returns (negative quantity)
df["Year"] = df["InvoiceDate"].dt.year
md = df["InvoiceDate"].dt.month * 100 + df["InvoiceDate"].dt.day
# Like-for-like window: 1 Jan - 9 Dec in both years (2011 data ends 9 Dec 2011)
win = df[(md <= 1209) & df["Year"].isin([2010, 2011])].copy()

# ---------------------------------------------------------- customer typing
pos = df[df["Quantity"] > 0]
first_buy = pos.groupby("Customer ID")["InvoiceDate"].min()  # first purchase in dataset

win["cid"] = win["Customer ID"]
has_id = win["cid"].notna()
rev = win[has_id].groupby(["cid", "Year"])["Revenue"].sum().unstack("Year").fillna(0.0)
rev.columns = ["R2010", "R2011"]
act = (win[has_id & (win["Quantity"] > 0)]
       .groupby(["cid", "Year"]).size().unstack("Year").fillna(0) > 0)
act.columns = ["A2010", "A2011"]
cust = rev.join(act, how="outer").fillna({"R2010": 0, "R2011": 0, "A2010": False, "A2011": False})
cust["A2010"] = cust["A2010"].astype(bool)
cust["A2011"] = cust["A2011"].astype(bool)
cust["first_buy"] = first_buy.reindex(cust.index)
cust["new_2011"] = cust["first_buy"] >= pd.Timestamp("2011-01-01")


def classify(r):
    if r["new_2011"] and r["A2011"]:
        return "Khách mới (lần đầu mua 2011)"
    if r["A2010"] and r["A2011"]:
        return "Khách cũ - tiếp tục mua"
    if r["A2010"] and not r["A2011"]:
        return "Khách cũ - ngừng mua 2011"
    if (not r["A2010"]) and r["A2011"]:
        return "Khách cũ - quay lại 2011"
    return "Khác (chỉ hoàn trả)"


cust["segment"] = cust.apply(classify, axis=1)
cust.to_csv(OUT / "customer_segments.csv")

# attach segment to rows; unidentified buyers get their own bucket
seg_map = cust["segment"].to_dict()
win["segment"] = win["cid"].map(seg_map).fillna("Không rõ mã khách")

# ------------------------------------------------------------ totals
tot = win.groupby("Year")["Revenue"].sum()
R10, R11 = tot[2010], tot[2011]
naive_2010_full = df[df["Year"] == 2010]["Revenue"].sum()
naive_2011_full = df[df["Year"] == 2011]["Revenue"].sum()

# ------------------------------------------------- decomposition of change
seg_year = win.groupby(["segment", "Year"])["Revenue"].sum().unstack("Year").fillna(0.0)
seg_year.columns = ["R2010", "R2011"]
seg_year["delta"] = seg_year["R2011"] - seg_year["R2010"]
seg_year["share_of_delta_pct"] = seg_year["delta"] / (R11 - R10) * 100
seg_year["customers_2010"] = cust.groupby("segment")["A2010"].sum().reindex(seg_year.index).fillna(0).astype(int)
seg_year["customers_2011"] = cust.groupby("segment")["A2011"].sum().reindex(seg_year.index).fillna(0).astype(int)
seg_year = seg_year.sort_values("delta", ascending=False)
seg_year.to_csv(OUT / "decomposition_by_segment.csv")

new_delta = seg_year.loc["Khách mới (lần đầu mua 2011)", "delta"]
unid_delta = seg_year.loc["Không rõ mã khách", "delta"]
old_delta = seg_year.drop(["Khách mới (lần đầu mua 2011)", "Không rõ mã khách"]).delta.sum()
assert abs(new_delta + old_delta + unid_delta - (R11 - R10)) < 1e-6

# ------------------------------------------------- market (country) breakdown
ctry = win.groupby(["Country", "Year"])["Revenue"].sum().unstack("Year").fillna(0.0)
ctry.columns = ["R2010", "R2011"]
ctry["delta"] = ctry["R2011"] - ctry["R2010"]
ctry["growth_pct"] = (ctry["R2011"] / ctry["R2010"] - 1) * 100
ctry["share_of_delta_pct"] = ctry["delta"] / (R11 - R10) * 100
ctry = ctry.sort_values("delta")
ctry.to_csv(OUT / "delta_by_country.csv")

# country x customer type, delta
ct = win.groupby(["Country", "segment", "Year"])["Revenue"].sum().unstack("Year").fillna(0.0)
ct.columns = ["R2010", "R2011"]
ct["delta"] = ct["R2011"] - ct["R2010"]
ct.to_csv(OUT / "delta_by_country_segment.csv")

# ------------------------------------------------------------ summary numbers
uk = ctry.loc["United Kingdom"]
ex_uk_delta = (R11 - R10) - uk["delta"]
summary = pd.DataFrame(
    {
        "metric": [
            "raw_rows_both_sheets", "exact_duplicates_removed", "rows_after_price_filter",
            "window", "net_revenue_2010_window", "net_revenue_2011_window", "delta_abs",
            "delta_pct", "delta_new_customers", "delta_old_customers", "delta_unidentified_id",
            "delta_UK", "delta_outside_UK", "naive_full_2010", "naive_full_2011_to_9dec",
            "customers_2010_with_id", "customers_2011_with_id",
            "overlap_rows_sheet1_dec1_9_2010", "overlap_rows_sheet2_dec1_9_2010",
        ],
        "value": [
            n_raw, n_dedup, len(df),
            "1 Jan - 9 Dec each year", round(R10, 2), round(R11, 2), round(R11 - R10, 2),
            round((R11 / R10 - 1) * 100, 2), round(new_delta, 2), round(old_delta, 2),
            # old_delta = identified existing customers (churned + retained + returning + returns-only)
            round(seg_year.loc["Không rõ mã khách", "delta"], 2),
            round(uk["delta"], 2), round(ex_uk_delta, 2),
            round(naive_2010_full, 2), round(naive_2011_full, 2),
            int(cust["A2010"].sum()), int(cust["A2011"].sum()),
            overlap_check["rows_sheet1_dec1_9_2010"], overlap_check["rows_sheet2_dec1_9_2010"],
        ],
    }
)
summary.to_csv(OUT / "summary.csv", index=False)

# sensitivity: product lines only (exclude postage, fees, adjustments, etc.)
nonprod = {"POST", "D", "M", "C2", "BANK CHARGES", "AMAZONFEE", "DOT", "CRUK", "ADJUST", "ADJUST2", "PADS", "B", "S"}
wp = win[~win["StockCode"].astype(str).str.upper().isin(nonprod)]
pt = wp.groupby("Year")["Revenue"].sum()
print("Sensitivity (product lines only): 2010=%.0f 2011=%.0f growth=%.2f%%" %
      (pt[2010], pt[2011], (pt[2011] / pt[2010] - 1) * 100))

# ------------------------------------------------------------------- charts
# 1) waterfall of change
steps = [
    ("Doanh thu 2010\n(1/1-9/12)", R10, "total"),
    ("Khách cũ\nngừng mua", seg_year.loc["Khách cũ - ngừng mua 2011", "delta"], "delta"),
    ("Khách cũ\ntiếp tục mua", seg_year.loc["Khách cũ - tiếp tục mua", "delta"], "delta"),
    ("Khách cũ\nquay lại", seg_year.loc["Khách cũ - quay lại 2011", "delta"], "delta"),
    ("Khách mới", new_delta, "delta"),
    ("Không rõ\nmã khách", seg_year.loc["Không rõ mã khách", "delta"], "delta"),
    ("Doanh thu 2011\n(1/1-9/12)", R11, "total"),
]
if "Khác (chỉ hoàn trả)" in seg_year.index:
    steps.insert(5, ("Khác", seg_year.loc["Khác (chỉ hoàn trả)", "delta"], "delta"))

fig, ax = plt.subplots(figsize=(11, 6))
running = 0.0
for i, (label, val, kind) in enumerate(steps):
    if kind == "total":
        ax.bar(i, val / 1e6, color="#4a4a4a")
        ax.text(i, val / 1e6 + 0.05, f"{val/1e6:.2f}M", ha="center", fontsize=10, fontweight="bold")
        running = val
    else:
        bottom = running if val >= 0 else running + val
        color = "#2a9d8f" if val >= 0 else "#e76f51"
        ax.bar(i, abs(val) / 1e6, bottom=bottom / 1e6, color=color)
        ax.text(i, (max(running, running + val)) / 1e6 + 0.05, f"{val/1e6:+.2f}M",
                ha="center", fontsize=10)
        running += val
ax.set_xticks(range(len(steps)))
ax.set_xticklabels([s[0] for s in steps], fontsize=9)
ax.set_ylabel("Doanh thu thuần (triệu GBP)")
ax.set_title(f"Doanh thu thuần 1/1-9/12: {R10/1e6:.2f}M (2010) → {R11/1e6:.2f}M (2011), "
             f"{(R11/R10-1)*100:+.1f}%", fontsize=12, loc="left")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(OUT / "waterfall_change.png", dpi=150)
plt.close()

# 2) market contributions (top 8 by |delta| + rest)
top = ctry.reindex(ctry["delta"].abs().sort_values(ascending=False).index)
top8 = top.head(8).sort_values("delta")
rest = top.iloc[8:]["delta"].sum()
labels = list(top8.index) + ["Các thị trường khác"]
vals = list(top8["delta"]) + [rest]
fig, ax = plt.subplots(figsize=(10, 6))
colors = ["#2a9d8f" if v >= 0 else "#e76f51" for v in vals]
ax.barh(labels, [v / 1e3 for v in vals], color=colors)
for i, v in enumerate(vals):
    ax.text(v / 1e3, i, f" {v/1e3:+,.0f}K", va="center", ha="left" if v >= 0 else "right", fontsize=9)
ax.axvline(0, color="black", lw=0.8)
ax.set_xlabel("Thay đổi doanh thu thuần 2011 vs 2010 (nghìn GBP)")
ax.set_title("Thị trường đóng góp vào thay đổi doanh thu (1/1-9/12)", loc="left", fontsize=12)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(OUT / "delta_by_country.png", dpi=150)
plt.close()

# ------------------------------------------------------------- console report
pd.set_option("display.width", 200)
print(summary.to_string(index=False))
print("\nDecomposition:\n", seg_year.round(2).to_string())
print("\nTop countries by delta:\n", ctry.sort_values("delta").round(1).to_string())
print("\nOverlap check:", overlap_check)
