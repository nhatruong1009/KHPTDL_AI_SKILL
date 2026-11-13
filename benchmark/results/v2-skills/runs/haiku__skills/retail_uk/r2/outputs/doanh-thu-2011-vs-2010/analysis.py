"""Doanh thu thuần 2011 vs 2010 (so sánh cùng kỳ Tháng 1-11), phân rã theo khách mới/cũ và theo thị trường.
Chạy: python outputs/doanh-thu-2011-vs-2010/analysis.py  (từ thư mục workspace)
"""
import os
import pandas as pd
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "..", "data", "online_retail_II.xlsx"))
OUT = HERE

# ---------- 1. Load & clean ----------
a = pd.read_excel(DATA, sheet_name="Year 2009-2010", dtype={"Invoice": str, "StockCode": str})
b = pd.read_excel(DATA, sheet_name="Year 2010-2011", dtype={"Invoice": str, "StockCode": str})
raw_rows = len(a) + len(b)
df = pd.concat([a, b], ignore_index=True)
n_before = len(df)
df = df.drop_duplicates()  # sheets overlap (1-9 Dec 2010) + exact duplicate lines
print(f"Rows raw={raw_rows:,} after exact-dedupe={len(df):,} (removed {n_before-len(df):,})")

df["revenue"] = df["Quantity"] * df["Price"]
df["is_return"] = df["Invoice"].str.startswith("C")
df["year"] = df["InvoiceDate"].dt.year
df["month"] = df["InvoiceDate"].dt.month
df["has_cust"] = df["Customer ID"].notna()
df["is_product"] = df["StockCode"].astype(str).str.match(r"^\d{5}")

print("Date range:", df["InvoiceDate"].min(), "->", df["InvoiceDate"].max())
print("Return lines:", int(df["is_return"].sum()), " revenue of returns:", round(df.loc[df.is_return, "revenue"].sum(), 2))
print("Missing Customer ID share of lines:", round((~df.has_cust).mean() * 100, 2), "%")

# ---------- 2. Fair window: Jan-Nov both years ----------
w = df[df["month"] <= 11].copy()
rev = w.groupby("year")["revenue"].sum()
print("\nNet revenue Jan-Nov (all rows):")
print(rev.round(0))
full2010 = df.loc[df.year == 2010, "revenue"].sum()
ytd2011 = df.loc[df.year == 2011, "revenue"].sum()
print(f"Full 2010 = {full2010:,.0f}; 2011 to 9-Dec = {ytd2011:,.0f}")

# ---------- 3. New vs old customers ----------
first_purchase = df.dropna(subset=["Customer ID"]).groupby("Customer ID")["InvoiceDate"].min()
first_year = first_purchase.dt.year.rename("first_year")
w = w.merge(first_year, left_on="Customer ID", right_index=True, how="left")


def seg(r):
    if pd.isna(r["Customer ID"]):
        return "Không xác định (thiếu Customer ID)"
    if r["first_year"] == r["year"]:
        return "Khách mới trong năm"
    return "Khách cũ (mua trước năm đó)"


w["segment"] = w.apply(seg, axis=1)
seg_tab = w.pivot_table(index="segment", columns="year", values="revenue", aggfunc="sum").fillna(0)
seg_tab["delta"] = seg_tab[2011] - seg_tab[2010]
print("\nRevenue by segment (Jan-Nov):")
print(seg_tab.round(0))
seg_tab.round(2).to_csv(os.path.join(OUT, "revenue_by_segment_year.csv"))

# Customer-level bridge: 2010 -> 2011 (Jan-Nov)
cust = w.dropna(subset=["Customer ID"]).groupby(["Customer ID", "year"])["revenue"].sum().unstack("year").fillna(0)
cust = cust.join(first_year)
cust[2010] = cust[2010].fillna(0) if 2010 in cust else 0
cust[2011] = cust[2011].fillna(0) if 2011 in cust else 0


def bridge_cat(r):
    if r[2010] > 0 and r[2011] > 0:
        return "Khách mua cả 2010 & 2011"
    if r[2010] > 0 and r[2011] <= 0:
        return "Khách rời đi (có 2010, không mua 2011)"
    if r[2010] <= 0 and r[2011] > 0 and r["first_year"] == 2011:
        return "Khách mới 2011"
    if r[2010] <= 0 and r[2011] > 0:
        return "Khách quay lại (mua trước 2010, không mua 2010)"
    return "Khác"


cust["bridge"] = cust.apply(bridge_cat, axis=1)
bridge = cust.groupby("bridge")[[2010, 2011]].sum()
bridge["delta"] = bridge[2011] - bridge[2010]
bridge["n_customers"] = cust.groupby("bridge").size()
bridge["n_active_2010"] = cust[cust[2010] > 0].groupby("bridge").size()
bridge["n_active_2011"] = cust[cust[2011] > 0].groupby("bridge").size()
print("\nCustomer bridge (Jan-Nov, identified customers):")
print(bridge.round(0))
bridge.round(2).to_csv(os.path.join(OUT, "customer_bridge_2010_2011.csv"))

print("\nActive identified customers 2010:", int((cust[2010] > 0).sum()), " 2011:", int((cust[2011] > 0).sum()))
print("Avg revenue per active customer 2010:", round(cust.loc[cust[2010] > 0, 2010].mean(), 0),
      " 2011:", round(cust.loc[cust[2011] > 0, 2011].mean(), 0))

# ---------- 4. Market (Country) ----------
ctry = w.pivot_table(index="Country", columns="year", values="revenue", aggfunc="sum").fillna(0)
ctry["delta"] = ctry[2011] - ctry[2010]
ctry["pct"] = np.where(ctry[2010].abs() > 0, ctry["delta"] / ctry[2010].abs() * 100, np.nan)
ctry = ctry.sort_values("delta")
ctry.round(2).to_csv(os.path.join(OUT, "revenue_by_country_2010_2011.csv"))
print("\nTop decliners:")
print(ctry.head(6).round(0))
print("\nTop gainers:")
print(ctry.tail(6).round(0))
uk = ctry.loc["United Kingdom", "delta"]
print(f"\nUK delta {uk:,.0f}; non-UK delta {ctry['delta'].sum() - uk:,.0f}; total {ctry['delta'].sum():,.0f}")

# ---------- 5. Sensitivity: product lines only, price > 0 ----------
s = w[w.is_product & (w.Price > 0)]
s_rev = s.groupby("year")["revenue"].sum()
print("\nSensitivity (product lines, price>0):", s_rev.round(0).to_dict(),
      "change %", round((s_rev[2011] / s_rev[2010] - 1) * 100, 2))

# ---------- 6. Headline ----------
tot10, tot11 = rev[2010], rev[2011]
print(f"\nHEADLINE: Jan-Nov 2010={tot10:,.0f}  2011={tot11:,.0f}  delta={tot11-tot10:,.0f}  pct={(tot11/tot10-1)*100:.2f}%")
