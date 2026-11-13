"""Vẽ 2 biểu đồ cho data story. Màu lấy từ bảng màu tham chiếu (đã kiểm chứng):
xanh dương #2a78d6 (categorical slot 1 / cực vượt kỳ vọng),
đỏ #e34948 (cực dưới kỳ vọng), xám #898781 (điểm nền), nền #fcfcfb, chữ #0b0b0b / #52514e.
"""
import sys
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analysis import build  # noqa: E402

OUT = "outputs/charts/"
os.makedirs(OUT, exist_ok=True)

BLUE, RED, GREY = "#2a78d6", "#e34948", "#898781"
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e1e0d9"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "figure.facecolor": SURF, "axes.facecolor": SURF,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
    "ytick.color": INK2, "text.color": INK, "axes.spines.top": False,
    "axes.spines.right": False,
})

df = build("2019")
X = np.column_stack([np.ones(len(df)), df.ln_gdp, df.ln_gdp ** 2])
b, *_ = np.linalg.lstsq(X, df.life_exp.values, rcond=None)
df["expected"] = X @ b
df["gap"] = df.life_exp - df.expected
VN = df[df.code == "VNM"].iloc[0]

# ---- Biểu đồ 1: tuổi thọ vs GDP/người (log), đường kỳ vọng ----
fig, ax = plt.subplots(figsize=(9, 5.6), dpi=150)
ax.scatter(df.gdp_pc_ppp, df.life_exp, s=22, color=GREY, alpha=0.55, linewidths=0,
           label="Các nước (2019)")
xs = np.logspace(np.log10(df.gdp_pc_ppp.min()), np.log10(df.gdp_pc_ppp.max()), 300)
lx = np.log(xs)
ys = b[0] + b[1] * lx + b[2] * lx ** 2
ax.plot(xs, ys, color=INK2, lw=1.6, label="Kỳ vọng theo thu nhập")
ax.scatter([VN.gdp_pc_ppp], [VN.life_exp], s=90, color=BLUE, zorder=5,
           label="Việt Nam")
ax.annotate(f"Việt Nam: {VN.life_exp:.1f} tuổi\nKỳ vọng: {VN.expected:.1f} tuổi",
            (VN.gdp_pc_ppp, VN.life_exp), xytext=(-170, 28),
            textcoords="offset points", color=INK, fontsize=9,
            arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
ax.set_xscale("log")
ax.set_xticks([1000, 3000, 10000, 30000, 100000])
ax.set_xticklabels(["1.000", "3.000", "10.000", "30.000", "100.000"])
ax.set_xlabel("GDP bình quân đầu người, PPP (USD quốc tế hiện hành, thang log)")
ax.set_ylabel("Tuổi thọ trung bình (năm)")
ax.set_title("Tuổi thọ tăng theo thu nhập, nhưng với độ dốc giảm dần",
             loc="left", fontsize=13, color=INK, pad=30)
ax.text(0, 1.01, "Mỗi điểm là một nước, năm 2019. Đường cong là kỳ vọng theo GDP/người.",
        transform=ax.transAxes, fontsize=9, color=INK2)
ax.grid(axis="y", color=GRID, lw=0.6)
ax.legend(frameon=False, loc="lower right", fontsize=9)
fig.text(0.01, 0.01, "Nguồn: World Bank WDI (SP.DYN.LE00.IN, NY.GDP.PCAP.PP.CD)",
         fontsize=8, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(OUT + "bieu_do_1_tuoi_tho_vs_thu_nhap.png")
plt.close(fig)

# ---- Biểu đồ 2: chênh lệch so với kỳ vọng (top 8 vượt, top 8 dưới, Việt Nam) ----
s = df.sort_values("gap")
bottom = s.head(8)
top = s.tail(8).iloc[::-1]
sel = pd.concat([top, bottom]).reset_index(drop=True)
label_vi = {"Naoero": "Nauru", "Bahamas, The": "Bahamas", "Syrian Arab Republic": "Syria",
            "Central African Republic": "CH Trung Phi (dữ liệu nghi ngờ)"}
names = [label_vi.get(n, n) for n in sel.country]
fig, ax = plt.subplots(figsize=(9, 7.4), dpi=150)
colors = [BLUE if g > 0 else RED for g in sel.gap]
y = np.arange(len(sel))[::-1]
ax.barh(y, sel.gap, color=colors, height=0.62)
for yi, g, nm in zip(y, sel.gap, names):
    ax.text(g + (0.3 if g > 0 else -0.3), yi, f"{g:+.1f}", va="center",
            ha="left" if g > 0 else "right", fontsize=8.5, color=INK)
ax.set_yticks(y)
ax.set_yticklabels(names, fontsize=8.5)
ax.axvline(0, color=INK2, lw=0.8)
ax.axhline(len(top) - 0.5 + 0.0, color=GRID, lw=0.8, ls="--")
ax.set_xlabel("Chênh lệch tuổi thọ so với kỳ vọng theo thu nhập (năm)")
ax.set_title("Nước vượt và dưới kỳ vọng nhiều nhất, sau khi tính thu nhập",
             loc="left", fontsize=13, color=INK, pad=30)
ax.set_xlim(-29, 9)
ax.text(0, 1.01, "Năm 2019. Xanh: vượt kỳ vọng. Đỏ: dưới kỳ vọng.",
        transform=ax.transAxes, fontsize=9, color=INK2)
ax.grid(axis="x", color=GRID, lw=0.6)
ax.set_axisbelow(True)
# Việt Nam: ghi chú riêng vì không nằm trong top 8
vn_gap = VN.gap
ax.text(0.02, 0.02, f"Việt Nam: {vn_gap:+.1f} năm (hạng 47/186)",
        transform=ax.transAxes, ha="left", fontsize=9, color=BLUE, fontweight="bold")
fig.text(0.01, 0.01, "Nguồn: World Bank WDI. Kỳ vọng từ hồi quy LE theo ln(GDP/người PPP) và bình phương của nó.",
         fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(OUT + "bieu_do_2_chenh_lech_ky_vong.png")
plt.close(fig)

print("Đã lưu biểu đồ vào", OUT)
print("Việt Nam chênh:", round(vn_gap, 2), "rank:", int(df.gap.rank(ascending=False, method='min')[df.code=='VNM'].iloc[0]))
