"""Biểu đồ cho phân tích uống rượu và G3. Đọc các CSV do analysis.py tạo ra."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

OUT = Path(__file__).resolve().parent
desc = pd.read_csv(OUT / "descriptives_by_level.csv")
scen = pd.read_csv(OUT / "results_scenarios.csv")

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})

# ---- Biểu đồ 1: G3 trung bình theo mức uống rượu ----
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
for ax, meas, label in [(axes[0], "Walc", "Uống rượu cuối tuần (Walc)"),
                        (axes[1], "Dalc", "Uống rượu ngày thường (Dalc)")]:
    d = desc[desc.measure == meas].sort_values("level")
    yerr = [d.mean_G3 - d.ci_lo, d.ci_hi - d.mean_G3]
    ax.errorbar(d.level, d.mean_G3, yerr=yerr, fmt="o-", color="#1f4e79",
                capsize=4, lw=2, ms=7)
    for _, r in d.iterrows():
        ax.annotate(f"{r.mean_G3:.1f}\n(n={int(r.n)})", (r.level, r.mean_G3),
                    textcoords="offset points", xytext=(0, 10), ha="center", fontsize=8)
    ax.set_xticks(d.level)
    ax.set_xlabel("Mức (1 = rất thấp, 5 = rất cao)")
    ax.set_title(label, fontsize=10)
    ax.set_ylim(9, 14)
    ax.grid(axis="y", alpha=0.3)
axes[0].set_ylabel("Điểm cuối kỳ G3 trung bình (95% CI)")
fig.suptitle("Điểm G3 trung bình giảm theo mức uống rượu: "
             "từ 12,4 (Walc = 1) xuống 10,9 (Walc = 4)", fontsize=12, y=1.02)
fig.tight_layout()
fig.savefig(OUT / "chart_g3_by_alcohol.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---- Biểu đồ 2: hệ số điều chỉnh qua các kịch bản ----
fig, ax = plt.subplots(figsize=(10, 5))
labels = []
y_pos = []
scen_short = scen.copy()
scen_short["sc"] = scen_short.scenario.str.split(".").str[0]
ypos = 0
for sc in scen_short.sc.unique():
    for meas, off, color in [("Dalc", 0.15, "#c0504d"), ("Walc", -0.15, "#1f4e79")]:
        r = scen_short[(scen_short.sc == sc) & (scen_short.measure == meas)].iloc[0]
        y = ypos + off
        ax.errorbar(r.adj_slope_per_level, y,
                    xerr=[[r.adj_slope_per_level - r.adj_ci_lo], [r.adj_ci_hi - r.adj_slope_per_level]],
                    fmt="o", color=color, capsize=3,
                    label=meas if sc == "A" else None)
    labels.append(f"Kịch bản {sc}")
    y_pos.append(ypos)
    ypos += 1
ax.axvline(0, color="grey", ls="--", lw=1)
ax.set_yticks(y_pos)
ax.set_yticklabels(labels)
ax.invert_yaxis()
ax.set_xlabel("Chênh lệch G3 cho mỗi mức uống rượu (điều chỉnh G1, G2, môn, giới, tuổi, học tập, trượt môn)")
ax.set_title("Sau khi kiểm soát điểm G1–G2, mức uống rượu không còn liên quan rõ đến G3 "
             "(khoảng tin cậy đều chứa 0)", fontsize=11)
ax.legend(title="Chỉ số", loc="lower right")
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "chart_adjusted_effects.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("saved charts")
