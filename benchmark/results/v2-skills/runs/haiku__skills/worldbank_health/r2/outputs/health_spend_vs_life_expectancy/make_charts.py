"""Bieu do cho phan tich chi tieu y te - tuoi tho (nam 2019, nam chinh).

Chay sau analysis.py: python make_charts.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import importlib.util as u

HERE = os.path.dirname(os.path.abspath(__file__))
spec = u.spec_from_file_location("analysis", os.path.join(HERE, "analysis.py"))
A = u.module_from_spec(spec)
spec.loader.exec_module(A)

YEAR = 2019
d, summ = A.analyse(YEAR)
# 'le' trung ten voi phuong thuc Series.le -> doi ten de truy cap an toan
d = d.rename(columns={"le": "life_exp"})

VI_NAME = {
    "VNM": "Việt Nam", "PSE": "Palestine", "SLB": "Quần đảo Solomon", "TJK": "Tajikistan",
    "SYR": "Syria", "NIC": "Nicaragua", "BDI": "Burundi", "JOR": "Jordan", "VUT": "Vanuatu",
    "MWI": "Malawi", "ALB": "Albania", "CPV": "Cabo Verde", "ECU": "Ecuador",
    "AGO": "Angola", "CIV": "Côte d'Ivoire", "NAM": "Namibia", "BHS": "Bahamas",
    "BRN": "Brunei", "LSO": "Lesotho", "TCD": "Chad", "NRU": "Nauru", "SWZ": "Eswatini",
    "GNQ": "Xích Đạo Guinea", "NGA": "Nigeria", "CAF": "Cộng hòa Trung Phi",
}
INCOME_VI = {
    "Low income": "Thu nhập thấp", "Lower middle income": "Trung bình thấp",
    "Upper middle income": "Trung bình cao", "High income": "Thu nhập cao",
}
COL = {"Low income": "#d95f02", "Lower middle income": "#e6ab02",
       "Upper middle income": "#1b9e77", "High income": "#7570b3"}

# ---- Bieu do 1: chi tieu y te vs tuoi tho ----
fig, ax = plt.subplots(figsize=(10, 6.5))
for g in ["Low income", "Lower middle income", "Upper middle income", "High income"]:
    s = d[d.IncomeGroup == g]
    ax.scatter(s.hexp, s.life_exp, s=38, alpha=0.8, color=COL[g], label=INCOME_VI[g], edgecolor="white", linewidth=0.5)
v = d[d["Country Code"] == "VNM"].iloc[0]
ax.scatter(v.hexp, v.life_exp, s=160, facecolor="none", edgecolor="black", linewidth=2)
ax.annotate(f"Việt Nam: {v.life_exp:.1f} tuổi\n(kỳ vọng theo thu nhập ~{v.expected_le:.1f})",
            (v.hexp, v.life_exp), xytext=(v.hexp * 1.6, v.life_exp - 9), fontsize=10,
            arrowprops=dict(arrowstyle="-", color="black"))
ax.set_xscale("log")
ax.set_xlabel("Chi tiêu y tế bình quân đầu người, USD hiện hành (thang log)")
ax.set_ylabel("Tuổi thọ trung bình khi sinh (năm)")
ax.set_title(f"Chi tiêu y tế cao đi kèm tuổi thọ cao (Spearman = {summ['spearman_hexp_le']:.2f}), "
             f"nhưng phần lớn là do thu nhập\n{YEAR}, {summ['n']} quốc gia", fontsize=13, loc="left")
ax.legend(title="Nhóm thu nhập (WB)", frameon=False, fontsize=9)
ax.grid(alpha=0.3)
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "chart1_chi_tieu_vs_tuoi_tho.png"), dpi=150)
plt.close(fig)

# ---- Bieu do 2: khoang cach so voi ky vong theo thu nhap ----
r = d.sort_values("gap_le", ascending=False).reset_index(drop=True)
top = r.head(10)
bot = r.tail(10)
vn = r[r["Country Code"] == "VNM"]
show = pd.concat([top, bot, vn]).drop_duplicates("Country Code")
show = show.sort_values("gap_le")
labels = [VI_NAME.get(c, n) for c, n in zip(show["Country Code"], show["Country Name"])]
colors = ["#1b9e77" if x > 0 else "#d95f02" for x in show.gap_le]
for i, c in enumerate(show["Country Code"]):
    if c == "VNM":
        colors[i] = "#000000"
fig, ax = plt.subplots(figsize=(10, 8))
ax.barh(labels, show.gap_le, color=colors)
for i, val in enumerate(show.gap_le):
    ax.text(val + (0.2 if val >= 0 else -0.2), i, f"{val:+.1f}", va="center",
            ha="left" if val >= 0 else "right", fontsize=9)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("Tuổi thọ thực tế − kỳ vọng theo GDP/người PPP (năm)")
ax.set_title(f"Nigeria và Cộng hòa Trung Phi thấp hơn kỳ vọng nhất\n"
             f"Việt Nam vượt kỳ vọng khoảng {vn.gap_le.iloc[0]:.1f} năm (hạng {int(vn.rank_gap.iloc[0])}/{summ['n']})\n"
             f"Mười nước vượt và mười nước dưới kỳ vọng nhiều nhất, {YEAR}", fontsize=12, loc="left")
ax.grid(axis="x", alpha=0.3)
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "chart2_vuot_duoi_ky_vong.png"), dpi=150)
plt.close(fig)

# ---- Thong ke cho Viet Nam ----
d["spend_pct_rank"] = d["hexp"].rank(pct=True)
inc_peers = d[d.IncomeGroup == v.IncomeGroup]
vn_spend_pct = d.loc[d["Country Code"] == "VNM", "spend_pct_rank"].iloc[0]
print("VN chi tieu:", round(v.hexp, 1), "USD; GDP:", round(v.gdp, 0), "; LE:", v.le, "; expected:", round(v.expected_le, 2))
print("VN gap:", round(v.gap_le, 2), "rank:", int(v.rank_gap), "/", len(d), "; quad rank:", int(v.rank_gap_quad))
print("VN spend percentile (all):", round(vn_spend_pct, 3))
print("Peers (upper-middle) median spend:", round(inc_peers.hexp.median(), 1), "n:", len(inc_peers))
print("Spend rank among upper-middle peers:", int((inc_peers.hexp > v.hexp).sum()) + 1, "/", len(inc_peers))
print("Upper-middle peers with gap > VN:", int((inc_peers.gap_le > v.gap_le).sum()))
print("Chart files written.")
