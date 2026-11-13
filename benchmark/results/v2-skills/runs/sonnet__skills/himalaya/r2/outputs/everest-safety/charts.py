import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

O = 'outputs/everest-safety/'
sns.set_theme(style='whitegrid')
BLUE, ORANGE, GREY = '#1f77b4', '#d55e00', '#888888'
P = pd.read_csv(O + 'headline_expedition_by_period.csv')
lab = ['1921-69', '1970-89', '1990-99', '2000-09', '2010-19']

# Chart 1: grouped bars with CI
fig, ax = plt.subplots(figsize=(9, 5.2))
x = np.arange(len(P))
w = 0.38
for off, pre, col, name in ((-w / 2, 'member', BLUE, 'Thành viên đoàn'), (w / 2, 'hired', ORANGE, 'Nhân viên thuê (hired staff)')):
    v = P[pre + '_rate_pct']
    err = [v - P[pre + '_lo'], P[pre + '_hi'] - v]
    ax.bar(x + off, v, w, color=col, label=name, yerr=err, capsize=3, error_kw=dict(ecolor='#444', lw=1))
    for xi, vi in zip(x + off, v):
        ax.text(xi, vi + 0.12 + (0.55 if pre == 'hired' and vi > 2 else 0.0) * 0, f'{vi:.1f}%', ha='center', va='bottom', fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels(lab)
ax.set_ylabel('Tỉ lệ tử vong (% số người lên núi)')
ax.set_title('Tỉ lệ tử vong trên Everest giảm khoảng một nửa sau 1990,\nnhân viên thuê giảm mạnh nhất (nhưng không thấp hơn hẳn thành viên)', fontsize=12, loc='left')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.1f}%'))
ax.legend(frameon=False)
sns.despine()
fig.text(0.01, -0.02, 'Nguồn: Himalayan Database (Everest, 1921-2019). Mẫu số = số người trong đoàn ghi ở expeditions.csv. Thanh sai số = khoảng tin cậy 95% (Wilson).', fontsize=8, color='#555')
fig.savefig(O + 'chart1_tu_vong_theo_giai_doan.png', dpi=150, bbox_inches='tight')
plt.close(fig)

# Chart 2: hired deaths by year 2000+
e = pd.read_csv('data/expeditions.csv')
ev = e[(e.peak_name == 'Everest') & (e.year >= 2000)]
y = ev.groupby('year').agg(hd=('hired_staff_deaths', 'sum'), md=('member_deaths', 'sum'))
fig, ax = plt.subplots(figsize=(9, 4.8))
cols = [ORANGE if i in (2014, 2015) else '#e8b48f' for i in y.index]
ax.bar(y.index, y.hd, color=cols, label='Nhân viên thuê')
ax.plot(y.index, y.md, color=BLUE, marker='o', lw=1.8, label='Thành viên đoàn')
for yr in (2014, 2015):
    ax.text(yr, y.hd[yr] + 0.5, str(int(y.hd[yr])), ha='center', fontweight='bold')
ax.set_xticks(range(2000, 2020, 2))
ax.set_ylabel('Số người chết mỗi năm')
ax.set_title('Phần lớn ca tử vong của nhân viên thuê thập niên 2010\nđến từ hai thảm họa năm 2014 và 2015 (28/40)', fontsize=12, loc='left')
ax.legend(frameon=False, loc='upper left')
sns.despine()
fig.text(0.01, -0.02, 'Nguồn: Himalayan Database, expeditions.csv (Everest).', fontsize=8, color='#555')
fig.savefig(O + 'chart2_tu_vong_theo_nam.png', dpi=150, bbox_inches='tight')
plt.close(fig)

# Chart 3: share of fatal expeditions + hired per member
f = pd.read_csv(O + 'expedition_fatality_incidence.csv')
fig, ax = plt.subplots(figsize=(8.5, 4.6))
cc = [GREY, GREY, BLUE, BLUE, BLUE]
ax.bar(f.period, 100 * f.fatal, color=cc)
for i, v in enumerate(100 * f.fatal):
    ax.text(i, v + 0.8, f'{v:.0f}%', ha='center')
ax.set_ylabel('% chuyến thám hiểm có ít nhất 1 người chết')
ax.set_title('Từ 1990, tỉ lệ chuyến đi có người chết giảm từ gần 30% xuống còn 6-7%', fontsize=12, loc='left')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0f}%'))
sns.despine()
fig.text(0.01, -0.02, 'Nguồn: Himalayan Database. Số chuyến: 34 / 170 / 331 / 745 / 869. Giai đoạn 1921-69 chỉ 34 chuyến nên kém chắc chắn.', fontsize=8, color='#555')
fig.savefig(O + 'chart3_chuyen_di_co_nguoi_chet.png', dpi=150, bbox_inches='tight')
plt.close(fig)
