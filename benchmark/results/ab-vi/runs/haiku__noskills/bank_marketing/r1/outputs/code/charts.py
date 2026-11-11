import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "/root/.cache/skill-bench/runs/ab-vi/haiku__noskills/bank_marketing/r1/workspace/outputs"
SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.facecolor": SURFACE,
    "figure.facecolor": SURFACE,
    "text.color": TEXT_PRIMARY,
    "axes.labelcolor": TEXT_SECONDARY,
    "xtick.color": TEXT_SECONDARY,
    "ytick.color": TEXT_SECONDARY,
})

# Biểu đồ 1: so sánh mô hình (độ lift top 20% theo CV 5 fold, có sai số)
cv = pd.read_csv(BASE + "/ket_qua_cv5.csv")
labels = cv["mo_hinh"].tolist()
vals = cv["lift20"].tolist()
errs = cv["lift20_sd"].tolist()
fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
bars = ax.bar(range(len(labels)), vals, yerr=errs, capsize=4,
              color=SERIES, width=0.6, edgecolor="none")
ax.axhline(1.0, color=TEXT_SECONDARY, linewidth=1, linestyle="--")
ax.text(len(labels) - 0.5, 1.03, "Ngẫu nhiên = 1,0", ha="right", va="bottom",
        fontsize=9, color=TEXT_SECONDARY)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.12, f"{v:.2f}".replace(".", ","),
            ha="center", va="bottom", fontsize=10, color=TEXT_PRIMARY)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels([l.replace(" (", "\n(") for l in labels], fontsize=9)
ax.set_ylabel("Lift trong nhóm 20% khách hàng được ưu tiên")
ax.set_title("Mô hình tốt hơn baseline bao nhiêu: lift ở top 20% (CV 5 fold)", loc="left",
             color=TEXT_PRIMARY, fontsize=12)
ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
ax.set_ylim(0, max(vals) + 0.6)
fig.tight_layout()
fig.savefig(BASE + "/bieu_do_so_sanh_mo_hinh.png")

# Biểu đồ 2: độ quan trọng biến (permutation importance, giảm AUC trên holdout thời gian)
imp = pd.read_csv(BASE + "/do_quan_trong_bien.csv").sort_values("giam_auc")
name_vi = {
    "poutcome": "Kết quả chiến dịch trước (poutcome)",
    "month": "Tháng liên hệ (month)",
    "age": "Tuổi (age)",
    "balance": "Số dư bình quân (balance)",
    "day": "Ngày trong tháng (day)",
    "contact": "Loại liên lạc (contact)",
    "marital": "Tình trạng hôn nhân (marital)",
    "housing": "Vay mua nhà (housing)",
    "pdays": "Số ngày từ lần liên hệ trước (pdays)",
    "education": "Trình độ học vấn (education)",
    "job": "Nghề nghiệp (job)",
    "loan": "Vay tiêu dùng (loan)",
    "default": "Nợ xấu (default)",
    "previous": "Số lần liên hệ trước (previous)",
}
fig, ax = plt.subplots(figsize=(9, 6), dpi=150)
ypos = range(len(imp))
ax.barh(list(ypos), imp["giam_auc"], xerr=imp["sd"], color=SERIES[0], height=0.6,
        capsize=3, edgecolor="none")
ax.set_yticks(list(ypos))
ax.set_yticklabels([name_vi.get(b, b) for b in imp["bien"]], fontsize=9)
ax.set_xlabel("Mức giảm AUC khi xáo trộn biến (lớn hơn = quan trọng hơn)")
ax.set_title("Yếu tố quan trọng nhất khi dự đoán đăng ký (holdout theo thời gian)",
             loc="left", color=TEXT_PRIMARY, fontsize=12)
ax.grid(axis="x", color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(BASE + "/bieu_do_do_quan_trong.png")
print("ok")
