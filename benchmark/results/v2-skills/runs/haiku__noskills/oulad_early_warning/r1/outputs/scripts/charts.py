"""Charts for the answer. Palette: reference categorical slots (blue, orange, aqua) from dataviz/references/palette.md
(light mode). Validator could not be executed in this run, so these hex values are the documented reference values."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "outputs/"
C = {'Pass': '#2a78d6', 'Fail': '#eb6834', 'Withdrawn': '#1baf7a'}
TEXT, MUTED, GRID = '#0b0b0b', '#52514e', '#e3e2de'

def style(ax):
    ax.set_facecolor('#fcfcfb')
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)
    ax.grid(axis='y', color=GRID, linewidth=0.8)
    ax.tick_params(colors=MUTED)

# Chart 1: weekly median clicks by outcome group (Q1)
q1 = pd.read_csv(OUT + "q1_weekly_by_outcome.csv")
fig, ax = plt.subplots(figsize=(7.5, 4.5))
for g in ['Pass', 'Fail', 'Withdrawn']:
    ax.plot(q1['tuần'], q1[f'{g}_median_clicks'], marker='o', markersize=8, linewidth=2, color=C[g], label=g)
    last = q1[f'{g}_median_clicks'].iloc[-1]
    ax.annotate(f"{g}: {last:.0f}", (q1['tuần'].iloc[-1], last), xytext=(8, 0), textcoords='offset points',
                va='center', color=TEXT, fontsize=9)
ax.set_xticks([1, 2, 3, 4])
ax.set_xticklabels(['Tuần 1', 'Tuần 2', 'Tuần 3', 'Tuần 4'])
ax.set_ylabel('Số lượt nhấp trung vị mỗi tuần', color=TEXT)
ax.set_title('Tương tác 4 tuần đầu theo kết quả: Pass cao nhất, Fail thấp nhất', color=TEXT, loc='left', fontsize=11)
ax.legend(frameon=False, loc='upper right')
style(ax)
fig.tight_layout()
fig.savefig(OUT + "chart1_tuong_tac_4_tuan.png", dpi=150)

# Chart 2: AUC (Pass vs non-completers) by week (Q2)
q2 = pd.read_csv(OUT + "q2_indicator_tests.csv")
pick = [('clicks_w1', 'Lượt nhấp tuần 1'), ('clicks_w2', 'Lượt nhấp tuần 2'), ('clicks_w3', 'Lượt nhấp tuần 3'),
        ('clicks_w4', 'Lượt nhấp tuần 4'), ('cum_active_w1', 'Ngày hoạt động lũy kế, tuần 1'),
        ('cum_active_w2', 'Ngày hoạt động lũy kế, tuần 2'), ('cum_active_w3', 'Ngày hoạt động lũy kế, tuần 3'),
        ('cum_active_w4', 'Ngày hoạt động lũy kế, tuần 4')]
vals = [q2.loc[q2.column == c, 'AUC_pass_vs_noncomp'].iloc[0] for c, _ in pick]
fig, ax = plt.subplots(figsize=(7.5, 4.5))
ax.barh([l for _, l in pick][::-1], vals[::-1], color=C['Pass'], height=0.6)
for i, v in enumerate(vals[::-1]):
    ax.text(v + 0.003, i, f"{v:.3f}", va='center', color=TEXT, fontsize=9)
ax.axvline(0.5, color=MUTED, linewidth=1, linestyle='--')
ax.set_xlim(0.45, 0.70)
ax.set_xlabel('AUC: Pass so với Fail/Withdrawn (0,5 = không phân biệt được)', color=TEXT)
ax.set_title('Khác biệt đã có từ tuần 1 và tăng dần đến tuần 4', color=TEXT, loc='left', fontsize=11)
style(ax)
ax.grid(axis='x', color=GRID, linewidth=0.8); ax.grid(axis='y', visible=False)
fig.tight_layout()
fig.savefig(OUT + "chart2_chi_bao_theo_tuan.png", dpi=150)

# Chart 3: capacity hits (Q4), model vs simple click rule
q4 = pd.read_csv(OUT + "q4_capacity_hits.csv")
fig, ax = plt.subplots(figsize=(7.5, 4.5))
labels = []; x = 0; width = 0.38
mods = list(q4.module.unique())
for i, mod in enumerate(mods):
    sub = q4[q4.module == mod].set_index('quy_tắc')
    m_hit = sub.iloc[0]['trúng']; b_hit = sub.iloc[1]['trúng']
    ax.bar(i - width / 2, m_hit, width, color=C['Pass'], label='Điểm rủi ro mô hình' if i == 0 else None)
    ax.bar(i + width / 2, b_hit, width, color=C['Withdrawn'], label='Baseline: ít lượt nhấp nhất' if i == 0 else None)
    ax.text(i - width / 2, m_hit + 3, str(m_hit), ha='center', color=TEXT, fontsize=9)
    ax.text(i + width / 2, b_hit + 3, str(b_hit), ha='center', color=TEXT, fontsize=9)
ax.set_xticks(range(len(mods)))
ax.set_xticklabels([f"{m} 2014J (200 suất)" for m in mods])
ax.set_ylabel('Số sinh viên không hoàn thành trong 200 ưu tiên', color=TEXT)
ax.set_title('Danh sách 200 ưu tiên mỗi module: trúng 287/400, tương đương baseline', color=TEXT, loc='left', fontsize=11)
ax.legend(frameon=False, loc='upper left', fontsize=9)
ax.set_ylim(0, 230)
style(ax)
fig.tight_layout()
fig.savefig(OUT + "chart3_trung_danh_sach_uu_tien.png", dpi=150)
print("ok")
