"""Biểu đồ cho báo cáo doanh thu 2011 vs 2010 (Tháng 1-11). Đọc các CSV do analysis.py tạo ra.
Chạy: python outputs/doanh-thu-2011-vs-2010/charts.py
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
M = 1e6

# ---------- Chart 1: bridge 2010 -> 2011 theo nhóm khách ----------
bridge = pd.read_csv(os.path.join(HERE, "customer_bridge_2010_2011.csv"), index_col=0)
seg = pd.read_csv(os.path.join(HERE, "revenue_by_segment_year.csv"), index_col=0)
rev10 = seg[["2010"]].sum().iloc[0]
unk_delta = seg.loc["Không xác định (thiếu Customer ID)", "delta"]

steps = [
    ("Khách 2010\nrời đi", bridge.loc['Khách rời đi (có 2010, không mua 2011)', "delta"]),
    ("Khách 2010\nmua lại 2011", bridge.loc["Khách mua cả 2010 & 2011", "delta"]),
    ("Khách mới\n2011", bridge.loc["Khách mới 2011", "delta"]),
    ("Khách quay\nlại", bridge.loc['Khách quay lại (mua trước 2010, không mua 2010)', "delta"]),
    ("Khác\n(hoàn trả)", bridge.loc["Khác", "delta"]),
    ("Không rõ\nCustomer ID", unk_delta),
]
total_delta = sum(v for _, v in steps)

fig, ax = plt.subplots(figsize=(11, 6))
labels = ["Doanh thu\n2010 (T1-11)"] + [s[0] for s in steps] + ["Doanh thu\n2011 (T1-11)"]
running = rev10 / M
ax.bar(0, running, color="#7f7f7f")
ax.text(0, running + 0.05, f"{running:.2f}M", ha="center", va="bottom", fontsize=10)
for i, (lab, v) in enumerate(steps, start=1):
    v_m = v / M
    color = "#2a9d8f" if v_m >= 0 else "#e76f51"
    bottom = running if v_m >= 0 else running + v_m
    ax.bar(i, abs(v_m), bottom=bottom, color=color)
    ax.text(i, running + max(v_m, 0) + 0.05, f"{v_m:+.2f}M", ha="center", va="bottom", fontsize=10)
    running += v_m
end = len(steps) + 1
ax.bar(end, running, color="#264653")
ax.text(end, running + 0.05, f"{running:.2f}M", ha="center", va="bottom", fontsize=10)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, fontsize=8.5)
ax.set_ylabel("Doanh thu thuần (triệu GBP)")
ax.set_ylim(0, max(rev10, running) / M * 1.25 if False else 11.5)
ax.set_title(
    f"Doanh thu thuần tăng {total_delta/M:+.2f}M (+{total_delta/rev10*100:.1f}%) nhờ khách mới 2011; "
    "khách 2010 rời đi làm mất 1.12M",
    fontsize=12, loc="left",
)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "chart1_bridge_khach_moi_vs_cu.png"), dpi=150)
plt.close(fig)

# ---------- Chart 2: thay đổi doanh thu theo thị trường ----------
ctry = pd.read_csv(os.path.join(HERE, "revenue_by_country_2010_2011.csv"), index_col=0)
ctry = ctry[ctry["2010"].abs() + ctry["2011"].abs() > 0]
rank = ctry["delta"].sort_values()
show = pd.concat([rank.head(8), rank.tail(8)])
show = show[~show.index.duplicated()]
show = show.sort_values()
names_vi = {
    "EIRE": "Ireland (EIRE)", "Denmark": "Đan Mạch", "Sweden": "Thụy Điển", "Greece": "Hy Lạp",
    "United Arab Emirates": "UAE", "USA": "Mỹ", "Lithuania": "Litva", "Thailand": "Thái Lan",
    "Germany": "Đức", "Japan": "Nhật Bản", "Spain": "Tây Ban Nha", "Norway": "Na Uy",
    "France": "Pháp", "Australia": "Úc", "Netherlands": "Hà Lan", "Belgium": "Bỉ",
    "Finland": "Phần Lan", "Hong Kong": "Hồng Kông", "Switzerland": "Thụy Sĩ",
    "Italy": "Ý", "Portugal": "Bồ Đào Nha", "Singapore": "Singapore", "Canada": "Canada",
    "Israel": "Israel", "Poland": "Ba Lan", "Cyprus": "Síp", "United Kingdom": "Vương quốc Anh",
}
fig, ax = plt.subplots(figsize=(10, 7))
colors = ["#2a9d8f" if v >= 0 else "#e76f51" for v in show.values]
ax.barh([names_vi.get(i, i) for i in show.index], show.values / 1000, color=colors)
for y, v in enumerate(show.values / 1000):
    ax.text(v + (2 if v >= 0 else -2), y, f"{v:+.0f}K", va="center",
            ha="left" if v >= 0 else "right", fontsize=9)
ax.axvline(0, color="black", lw=0.8)
ax.set_xlabel("Thay đổi doanh thu thuần 2011 vs 2010, T1-11 (nghìn GBP)")
ax.set_title(
    "Úc, Pháp và Tây Ban Nha kéo tăng; Ireland, Đan Mạch và Thụy Điển kéo giảm mạnh nhất",
    fontsize=12, loc="left",
)
ax.set_xlim(-110, 150)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "chart2_thi_truong_tang_giam.png"), dpi=150)
plt.close(fig)
print("saved charts")
