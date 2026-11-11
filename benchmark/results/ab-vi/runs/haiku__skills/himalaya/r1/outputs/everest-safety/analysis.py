"""Everest (peak_id EVER): death rates of foreign members vs hired staff, by decade.

Denominators come from expeditions.csv expedition-level totals (members, hired_staff).
members.csv is used only as a cross-check (its death counts tie exactly to the totals).
Run: python -I analysis.py  (from this folder)
"""
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "..", "data"))
OUT = HERE
COMMERCIAL_START = 1990  # theo yêu cầu: khoảng từ 1990

e = pd.read_csv(os.path.join(DATA, "expeditions.csv"))
m = pd.read_csv(os.path.join(DATA, "members.csv"), low_memory=False)

ev = e[e.peak_id == "EVER"].copy()
em = m[m.peak_id == "EVER"].copy()
ev["decade"] = (ev.year // 10) * 10
ev["era"] = np.where(ev.year >= COMMERCIAL_START, "Thương mại (1990+)", "Trước 1990")


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (100 * (c - h), 100 * (c + h))


def summarize(df, by):
    g = df.groupby(by).agg(
        chuyen_thám_hiểm=("expedition_id", "count"),
        thanh_vien=("members", "sum"),
        tu_vong_thanh_vien=("member_deaths", "sum"),
        nhan_vien_thue=("hired_staff", "sum"),
        tu_vong_nhan_vien=("hired_staff_deaths", "sum"),
    )
    g["ti_le_tv_thanh_vien_%"] = 100 * g.tu_vong_thanh_vien / g.thanh_vien
    g["ti_le_tv_nhan_vien_%"] = 100 * g.tu_vong_nhan_vien / g.nhan_vien_thue
    g["mem_ci_low"] = [wilson(k, n)[0] for k, n in zip(g.tu_vong_thanh_vien, g.thanh_vien)]
    g["mem_ci_high"] = [wilson(k, n)[1] for k, n in zip(g.tu_vong_thanh_vien, g.thanh_vien)]
    g["hir_ci_low"] = [wilson(k, n)[0] for k, n in zip(g.tu_vong_nhan_vien, g.nhan_vien_thue)]
    g["hir_ci_high"] = [wilson(k, n)[1] for k, n in zip(g.tu_vong_nhan_vien, g.nhan_vien_thue)]
    return g


# ---------- 0. Kiểm tra chéo với members.csv ----------
chk = {
    "tổng tử vong thành viên (expeditions)": int(ev.member_deaths.sum()),
    "tổng tử vong thành viên (members.csv, died=True)": int(em[~em.hired].died.sum()),
    "tổng tử vong nhân viên (expeditions)": int(ev.hired_staff_deaths.sum()),
    "tổng tử vong nhân viên (members.csv, hired=True)": int(em[em.hired].died.sum()),
    "tổng thành viên (expeditions)": int(ev.members.sum()),
    "tổng nhân viên thuê (expeditions)": int(ev.hired_staff.sum()),
    "số dòng thành viên trong members.csv": int(len(em)),
    "số dòng thành viên hired=False": int((~em.hired).sum()),
    "số dòng thành viên hired=True": int(em.hired.sum()),
}
pd.Series(chk, name="gia_tri").to_csv(os.path.join(OUT, "kiem_tra_doi_chieu.csv"), header=True)
for k, v in chk.items():
    print(f"{k}: {v}")

# ---------- 1. Theo thập kỷ ----------
dec = summarize(ev, "decade")
dec.index.name = "thap_ky"
dec.round(3).to_csv(os.path.join(OUT, "ti_le_tu_vong_theo_thap_ky.csv"))
print("\n== Theo thập kỷ ==")
print(dec[["chuyen_thám_hiểm", "thanh_vien", "tu_vong_thanh_vien", "ti_le_tv_thanh_vien_%",
           "nhan_vien_thue", "tu_vong_nhan_vien", "ti_le_tv_nhan_vien_%"]].round(2).to_string())

# ---------- 2. Theo kỷ nguyên ----------
era = summarize(ev, "era")
era.index.name = "ky_nguyen"
era.round(3).to_csv(os.path.join(OUT, "ti_le_tu_vong_theo_ky_nguyen.csv"))
print("\n== Theo kỷ nguyên ==")
print(era[["chuyen_thám_hiểm", "thanh_vien", "tu_vong_thanh_vien", "ti_le_tv_thanh_vien_%",
           "nhan_vien_thue", "tu_vong_nhan_vien", "ti_le_tv_nhan_vien_%"]].round(2).to_string())

# ---------- 3. Kiểm định: trước vs sau 1990, và thành viên vs nhân viên ----------
def two_prop(k1, n1, k2, n2):
    tab = np.array([[k1, n1 - k1], [k2, n2 - k2]])
    chi2, p, _, _ = stats.chi2_contingency(tab, correction=False)
    p1, p2 = k1 / n1, k2 / n2
    rr = p2 / p1 if p1 > 0 else np.nan
    return {"ti_le_1": 100 * p1, "ti_le_2": 100 * p2, "ti_le_ratio_2_vs_1": rr, "p_value": p}


pre = ev[ev.era == "Trước 1990"]
post = ev[ev.era == "Thương mại (1990+)"]
tests = {
    "thanh_vien: trước 1990 vs 1990+": two_prop(
        pre.member_deaths.sum(), pre.members.sum(), post.member_deaths.sum(), post.members.sum()),
    "nhan_vien: trước 1990 vs 1990+": two_prop(
        pre.hired_staff_deaths.sum(), pre.hired_staff.sum(), post.hired_staff_deaths.sum(), post.hired_staff.sum()),
    "1990+: nhan_vien vs thanh_vien": two_prop(
        post.member_deaths.sum(), post.members.sum(), post.hired_staff_deaths.sum(), post.hired_staff.sum()),
    "trước 1990: nhan_vien vs thanh_vien": two_prop(
        pre.member_deaths.sum(), pre.members.sum(), pre.hired_staff_deaths.sum(), pre.hired_staff.sum()),
}
tests_df = pd.DataFrame(tests).T
tests_df.to_csv(os.path.join(OUT, "kiem_dinh_so_sanh.csv"))
print("\n== Kiểm định ==")
print(tests_df.round(4).to_string())

# ---------- 4. Độ nhạy: bỏ các dòng hired_staff=99 (nghi là mã thiếu dữ liệu) ----------
sens = ev[~ev.hired_staff.isin([99]) & ~ev.members.isin([99])]
sens_era = summarize(sens, "era")
print("\n== Độ nhạy (bỏ dòng có 99) ==")
print(sens_era[["ti_le_tv_thanh_vien_%", "ti_le_tv_nhan_vien_%"]].round(3).to_string())

# ---------- 4b. Độ nhạy: bỏ 2014-2015 (hai sự cố tập trung ở Khumbu) ----------
no1415 = post[~post.year.isin([2014, 2015])]
s1415 = {
    "1990+ nhan_vien (bỏ 2014-2015) %": 100 * no1415.hired_staff_deaths.sum() / no1415.hired_staff.sum(),
    "1990+ thanh_vien (bỏ 2014-2015) %": 100 * no1415.member_deaths.sum() / no1415.members.sum(),
    "1990+ nhan_vien (bỏ 2014-2015) p vs thanh_vien": two_prop(
        no1415.member_deaths.sum(), no1415.members.sum(),
        no1415.hired_staff_deaths.sum(), no1415.hired_staff.sum())["p_value"],
}
print("\n== Độ nhạy: bỏ 2014-2015 (kỷ nguyên 1990+) ==")
for k, v in s1415.items():
    print(f"{k}: {v:.4f}")

# ---------- 5. Theo năm (các năm có thảm họa) ----------
yr = ev.groupby("year").agg(
    thanh_vien=("members", "sum"), tu_vong_tv=("member_deaths", "sum"),
    nhan_vien=("hired_staff", "sum"), tu_vong_nv=("hired_staff_deaths", "sum"))
top_hired_years = yr.sort_values("tu_vong_nv", ascending=False).head(8)
print("\n== Năm có nhiều nhân viên thuê tử vong nhất ==")
print(top_hired_years.to_string())
yr.to_csv(os.path.join(OUT, "tu_vong_theo_nam.csv"))

# ---------- 6. Nguyên nhân tử vong (members.csv, died=True) ----------
died = em[em.died].copy()
died["kieu_nguoi"] = np.where(died.hired, "Nhân viên thuê", "Thành viên")
died["era"] = np.where(died.year >= COMMERCIAL_START, "Thương mại (1990+)", "Trước 1990")
cause = pd.crosstab(died.death_cause.fillna("Không rõ"), [died.kieu_nguoi])
cause.to_csv(os.path.join(OUT, "nguyen_nhan_tu_vong.csv"))
print("\n== Nguyên nhân tử vong ==")
print(cause.sort_values(cause.columns[0], ascending=False).to_string())

# ---------- Biểu đồ ----------
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
x = dec.index.astype(int).astype(str) + "s"

# Biểu đồ đường: bỏ các thập kỷ trước 1950 (dưới 100 thành viên mỗi thập kỷ, CI quá rộng); bảng CSV vẫn đầy đủ.
dec_plot = dec[dec.index >= 1950]
x = dec_plot.index.astype(int).astype(str) + "s"
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(x, dec_plot["ti_le_tv_thanh_vien_%"], marker="o", color="#1f5fa8", label="Thành viên đoàn")
ax.fill_between(x, dec_plot.mem_ci_low, dec_plot.mem_ci_high, color="#1f5fa8", alpha=0.15)
ax.plot(x, dec_plot["ti_le_tv_nhan_vien_%"], marker="s", color="#c8553d", label="Nhân viên được thuê")
ax.fill_between(x, dec_plot.hir_ci_low, dec_plot.hir_ci_high, color="#c8553d", alpha=0.15)
ax.set_title("Tỉ lệ tử vong trên Everest theo thập kỷ (có khoảng tin cậy 95%)")
ax.set_xlabel("Thập kỷ")
ax.set_ylabel("Tỉ lệ tử vong (%)")
ax.axvline(x=list(x).index("1990s") - 0.5, color="grey", ls="--", lw=1)
ax.text(list(x).index("1990s") - 0.45, ax.get_ylim()[1] * 0.92, "Bắt đầu kỷ nguyên thương mại", color="grey")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "chart_ti_le_theo_thap_ky.png"), dpi=150)
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5.5))
x_all = dec.index.astype(int).astype(str) + "s"
ax.bar(x_all, dec.chuyen_thám_hiểm, color="#9bb7d4")
ax.set_title("Số chuyến thám hiểm Everest theo thập kỷ")
ax.set_xlabel("Thập kỷ")
ax.set_ylabel("Số chuyến thám hiểm")
ax.spines[["top", "right"]].set_visible(False)
for i, v in enumerate(dec.chuyen_thám_hiểm):
    ax.text(i, v + 5, f"{int(v)}", ha="center")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "chart_so_chuyen_theo_thap_ky.png"), dpi=150)
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 5.5))
labels = ["Thành viên\ntrước 1990", "Thành viên\n1990+", "Nhân viên\ntrước 1990", "Nhân viên\n1990+"]
vals = [
    era.loc["Trước 1990", "ti_le_tv_thanh_vien_%"],
    era.loc["Thương mại (1990+)", "ti_le_tv_thanh_vien_%"],
    era.loc["Trước 1990", "ti_le_tv_nhan_vien_%"],
    era.loc["Thương mại (1990+)", "ti_le_tv_nhan_vien_%"],
]
cols = ["#1f5fa8", "#1f5fa8", "#c8553d", "#c8553d"]
alphas = [0.45, 1.0, 0.45, 1.0]
bars = ax.bar(labels, vals, color=cols)
for b, a in zip(bars, alphas):
    b.set_alpha(a)
for i, v in enumerate(vals):
    ax.text(i, v + 0.05, f"{v:.2f}%", ha="center")
ax.set_title("Tỉ lệ tử vong trước và sau 1990")
ax.set_ylabel("Tỉ lệ tử vong (%)")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "chart_truoc_sau_1990.png"), dpi=150)
plt.close(fig)

print("\nDone. Outputs in", OUT)
