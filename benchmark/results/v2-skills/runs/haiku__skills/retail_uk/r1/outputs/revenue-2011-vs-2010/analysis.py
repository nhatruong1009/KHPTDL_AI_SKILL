"""Doanh thu thuần 2011 so với 2010 (so sánh cùng kỳ 1/1–8/12) và phân rã theo khách mới/cũ, theo thị trường.

Chạy: python -I analysis.py   (đọc data/ tương đối so với thư mục workspace)
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "online_retail_II.xlsx"
OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)

# Cửa sổ so sánh công bằng: 1/1 đến 8/12 cho cả hai năm (dữ liệu 2011 kết thúc giữa ngày 9/12/2011)
WIN_START = {2010: "2010-01-01", 2011: "2011-01-01"}
WIN_END = {2010: "2010-12-09", 2011: "2011-12-09"}  # exclusive

# Mã không phải bán hàng cho khách (điều chỉnh nội bộ, phí, bù nợ xấu, test)
ADMIN_CODES = {"M", "B", "ADJUST", "AMAZONFEE", "BANK CHARGES", "TEST001", "TEST002", "CRUK"}

# ---------- 1. Nạp & làm sạch ----------
a = pd.read_excel(SRC, sheet_name="Year 2009-2010")
b = pd.read_excel(SRC, sheet_name="Year 2010-2011")
# Hai sheet trùng nhau 1–9/12/2010: lấy sheet 1 cho trước 1/12/2010, sheet 2 cho phần còn lại
df = pd.concat([a[a.InvoiceDate < "2010-12-01"], b], ignore_index=True)
n_raw = len(df)
df = df.drop_duplicates().copy()
n_dup = n_raw - len(df)
df["StockCode"] = df["StockCode"].astype(str)
df["rev"] = df.Quantity * df.Price  # âm = hoàn trả/hủy (giữ để ra doanh thu thuần)
df["is_admin"] = df.StockCode.isin(ADMIN_CODES)
df["has_cust"] = df["Customer ID"].notna()
df["cust"] = df["Customer ID"]

# Dòng giá <= 0 (điều chỉnh, miễn phí) bị loại khỏi cả hai phương án
df = df[df.Price > 0].copy()

# Cửa sổ so sánh
def in_window(d):
    y = d.dt.year
    out = pd.Series(False, index=d.index)
    for yr in (2010, 2011):
        m = (y == yr) & (d >= WIN_START[yr]) & (d < WIN_END[yr])
        out |= m
    return out

df["win"] = in_window(df.InvoiceDate)
df["year"] = df.InvoiceDate.dt.year
w = df[df.win].copy()

log = []
log.append(f"Dòng gốc (2 sheet): {n_raw:,}; trùng lặp hoàn toàn bỏ: {n_dup:,}; sau khi bỏ giá<=0: {len(df):,}")
log.append(f"Cửa sổ so sánh: 1/1–8/12 mỗi năm; dòng trong cửa sổ: {len(w):,}")

# ---------- 2. Doanh thu thuần: headline và độ nhạy ----------
tot = w.groupby("year").rev.sum()
core = w[~w.is_admin].groupby("year").rev.sum()
headline = pd.DataFrame({
    "doanh_thu_tat_ca_dong": tot,
    "doanh_thu_ban_hang_bo_admin": core,
})
headline["so_dong"] = w.groupby("year").size()
headline.loc["thay_doi"] = headline.loc[2011] - headline.loc[2010]
headline.loc["thay_doi_%"] = (headline.loc[2011] / headline.loc[2010] - 1) * 100
headline.to_csv(OUT / "headline_revenue.csv")

# Doanh thu thuần của năm đầy đủ 2010 (để tham khảo, không dùng làm so sánh)
full2010 = df[(df.year == 2010)].rev.sum()
full2010_core = df[(df.year == 2010) & (~df.is_admin)].rev.sum()
log.append(f"Tham khảo: doanh thu 2010 cả năm (không cùng kỳ) = {full2010:,.0f} (bỏ admin: {full2010_core:,.0f})")

# ---------- 3. Phân rã khách mới / cũ (chỉ khách có mã; dùng bộ 'core' bỏ admin) ----------
c = w[(~w.is_admin)].copy()
cust = c[c.has_cust]
first_ever = df[df.has_cust].groupby("cust").InvoiceDate.min().dt.year
cust_year_rev = cust.groupby(["cust", "year"]).rev.sum().unstack(fill_value=0.0)
cust_year_rev = cust_year_rev.reindex(columns=[2010, 2011], fill_value=0.0)

rev10 = cust_year_rev[2010]
rev11 = cust_year_rev[2011]
active10 = rev10 != 0
active11 = rev11 != 0
first = first_ever.reindex(cust_year_rev.index)

new_mask = active11 & (first == 2011)                   # lần đầu mua trong dữ liệu là 2011
old_mask = active11 & (first < 2011)                    # đã mua trước 2011
retained_mask = old_mask & active10                     # khách cũ đã mua 2010 và mua lại 2011
reactivated_mask = old_mask & ~active10                 # khách cũ, không mua 2010, quay lại 2011
churn_mask = active10 & ~active11                       # mua 2010, không mua 2011

bridge = {
    "Doanh thu 2010 (cùng kỳ, có mã KH)": rev10[active10].sum(),
    "Khách mất (mua 2010, không mua 2011)": -rev10[churn_mask].sum(),
    "Khách giữ lại: thay đổi chi tiêu": rev11[retained_mask].sum() - rev10[retained_mask].sum(),
    "Khách cũ quay lại (không mua 2010)": rev11[reactivated_mask].sum(),
    "Khách mới 2011": rev11[new_mask].sum(),
}
null_10 = headline.loc[2010, "doanh_thu_ban_hang_bo_admin"] - c[c.has_cust].groupby("year").rev.sum().get(2010, 0)
null_11 = headline.loc[2011, "doanh_thu_ban_hang_bo_admin"] - c[c.has_cust].groupby("year").rev.sum().get(2011, 0)
bridge["Doanh thu không có mã KH: thay đổi"] = null_11 - null_10
bridge["Doanh thu 2011 (cùng kỳ, bỏ admin)"] = headline.loc[2011, "doanh_thu_ban_hang_bo_admin"]

bridge_df = pd.Series(bridge, name="gia_tri")
bridge_df.to_csv(OUT / "bridge_new_vs_old.csv", header=True)
cust_part = (bridge["Doanh thu 2010 (cùng kỳ, có mã KH)"] + bridge["Khách mất (mua 2010, không mua 2011)"]
             + bridge["Khách giữ lại: thay đổi chi tiêu"] + bridge["Khách cũ quay lại (không mua 2010)"]
             + bridge["Khách mới 2011"])
log.append(f"Kiểm tra bridge khách có mã: {cust_part:,.0f} vs 2011 có mã {rev11[active11].sum():,.0f}")
total_chk = (headline.loc[2010, "doanh_thu_ban_hang_bo_admin"] + (cust_part - bridge["Doanh thu 2010 (cùng kỳ, có mã KH)"])
             + bridge["Doanh thu không có mã KH: thay đổi"])
log.append(f"Kiểm tra tổng: 2010 (bỏ admin) + thay đổi khách có mã + thay đổi không mã = {total_chk:,.0f} vs 2011 {bridge['Doanh thu 2011 (cùng kỳ, bỏ admin)']:,.0f}")

# Thống kê khách
stats = pd.DataFrame({
    "so_khach_2010": [int(active10.sum())],
    "so_khach_2011": [int(active11.sum())],
    "khach_moi_2011": [int(new_mask.sum())],
    "khach_giu_lai": [int(retained_mask.sum())],
    "khach_quay_lai": [int(reactivated_mask.sum())],
    "khach_mat": [int(churn_mask.sum())],
    "ty_le_mat_khach_%": [round(churn_mask.sum() / active10.sum() * 100, 1)],
    "doanh_thu_TB_khach_moi": [round(rev11[new_mask].mean(), 0)],
    "doanh_thu_TB_khach_giu_lai_2011": [round(rev11[retained_mask].mean(), 0)],
    "doanh_thu_TB_khach_giu_lai_2010": [round(rev10[retained_mask].mean(), 0)],
})
stats.T.rename(columns={0: "gia_tri"}).to_csv(OUT / "customer_stats.csv")

# Tập trung: khách lớn nhất đóng góp bao nhiêu vào thay đổi của từng thị trường lớn
cc = w[(~w.is_admin) & w.has_cust].groupby(["Country", "cust", "year"]).rev.sum().unstack(fill_value=0.0)
cc = cc.reindex(columns=[2010, 2011], fill_value=0.0)
cc["d"] = cc[2011] - cc[2010]
conc_rows = []
for ctry in ["Australia", "France", "United Kingdom", "EIRE", "Denmark", "Netherlands"]:
    sub = cc.xs(ctry, level=0) if ctry in cc.index.get_level_values(0) else None
    if sub is None:
        continue
    cty_d = sub.d.sum()
    top3 = sub.d.abs().sort_values(ascending=False).head(3).index
    conc_rows.append({"thi_truong": ctry, "thay_doi_tong": round(cty_d, 0),
                      "top3_KH_dong_gop": round(sub.loc[top3, "d"].sum(), 0),
                      "top3_KH_id": ";".join(str(int(i)) for i in top3),
                      "thay_doi_khong_top3": round(cty_d - sub.loc[top3, "d"].sum(), 0)})
pd.DataFrame(conc_rows).to_csv(OUT / "market_concentration.csv", index=False)

# Độ nhạy: bao gồm cả dòng admin, và gồm cả dòng không có mã
sens = []
for label, sub in [
    ("Headline: bỏ admin, có mã KH", c[c.has_cust]),
    ("Độ nhạy: gồm admin", w[w.has_cust]),
    ("Độ nhạy: gồm cả dòng không có mã", w[~w.is_admin]),
]:
    s = sub.groupby("year").rev.sum()
    sens.append({"phuong_an": label, "dt_2010": s[2010], "dt_2011": s[2011],
                 "thay_doi": s[2011] - s[2010], "thay_doi_%": (s[2011] / s[2010] - 1) * 100})
sens_df = pd.DataFrame(sens)
sens_df.to_csv(OUT / "sensitivity.csv", index=False)

# ---------- 4. Thị trường ----------
mk = w[~w.is_admin].groupby(["Country", "year"]).rev.sum().unstack(fill_value=0.0)
mk = mk.reindex(columns=[2010, 2011], fill_value=0.0)
mk["thay_doi"] = mk[2011] - mk[2010]
mk["thay_doi_%"] = (mk[2011] / mk[2010].replace(0, pd.NA) - 1) * 100
mk["dong_gop_%_tong_thay_doi"] = mk["thay_doi"] / mk["thay_doi"].sum() * 100
mk = mk.sort_values("thay_doi")
mk.to_csv(OUT / "country_change.csv")

# ---------- 5. Biểu đồ ----------
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})

# Waterfall
total_2010 = headline.loc[2010, "doanh_thu_ban_hang_bo_admin"]
labels = ["DT 2010\n(cùng kỳ)", "Khách mất", "Khách giữ lại\n(chi tiêu giảm)", "Khách cũ\nquay lại", "Khách mới\n2011", "Đơn không\ncó mã KH", "DT 2011\n(cùng kỳ)"]
steps = [
    bridge["Khách mất (mua 2010, không mua 2011)"],
    bridge["Khách giữ lại: thay đổi chi tiêu"],
    bridge["Khách cũ quay lại (không mua 2010)"],
    bridge["Khách mới 2011"],
    bridge["Doanh thu không có mã KH: thay đổi"],
]
fig, ax = plt.subplots(figsize=(11, 5.5))
ax.bar(0, total_2010 / 1e6, color="#7f8c8d")
ax.text(0, total_2010 / 1e6 + 0.1, f"{total_2010/1e6:.2f} tr£", ha="center", fontsize=9)
running = total_2010
for i, v in enumerate(steps, start=1):
    bottom = running if v >= 0 else running + v
    ax.bar(i, abs(v) / 1e6, bottom=bottom / 1e6, color="#2e8b57" if v >= 0 else "#c0392b")
    ax.text(i, (max(running, running + v)) / 1e6 + 0.1, f"{v/1e6:+.2f} tr£", ha="center", fontsize=9)
    running += v
end = bridge["Doanh thu 2011 (cùng kỳ, bỏ admin)"]
ax.bar(len(steps) + 1, end / 1e6, color="#34495e")
ax.text(len(steps) + 1, end / 1e6 + 0.1, f"{end/1e6:.2f} tr£", ha="center", fontsize=9)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, fontsize=8.5)
ax.set_ylabel("Doanh thu thuần (triệu £)")
ax.set_title("Doanh thu 2011 chỉ tăng ~4%: khách mới bù đắp gần hết phần khách cũ rời đi")
ax.set_ylim(0, max(total_2010, end) / 1e6 * 1.12)
fig.tight_layout()
fig.savefig(OUT / "bridge_waterfall.png", dpi=150)
plt.close(fig)

# Country bars (top movers)
top = pd.concat([mk.head(6), mk.tail(6)]).drop_duplicates()
top = top.sort_values("thay_doi")
fig, ax = plt.subplots(figsize=(10, 6))
colors = ["#c0392b" if v < 0 else "#2e8b57" for v in top["thay_doi"]]
ax.barh(top.index.astype(str), top["thay_doi"] / 1e3, color=colors)
ax.axvline(0, color="black", lw=0.8)
ax.set_xlabel("Thay đổi doanh thu thuần 2011 vs 2010 cùng kỳ (nghìn £)")
ax.set_title("Úc, Pháp và Anh kéo tăng mạnh nhất; Ireland (EIRE) và Đan Mạch giảm mạnh nhất")
fig.tight_layout()
fig.savefig(OUT / "country_movers.png", dpi=150)
plt.close(fig)

# ---------- 6. In kết quả ----------
print("\n".join(log))
print("\nHEADLINE\n", headline.to_string())
print("\nBRIDGE (£)\n", bridge_df.round(0).to_string())
print("\nCUSTOMERS\n", stats.T.to_string())
print("\nSENSITIVITY\n", sens_df.round(1).to_string())
print("\nCOUNTRY (top/bottom)\n", mk.round(0).to_string())
