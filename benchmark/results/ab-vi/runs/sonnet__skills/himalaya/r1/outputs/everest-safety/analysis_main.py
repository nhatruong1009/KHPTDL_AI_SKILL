# KẾT QUẢ CHÍNH. Chạy sau analysis.py:  python -I outputs/everest-safety/analysis_main.py
# Mẫu số cấp đoàn (expeditions.csv) vì bảng members ghi thiếu nhân viên thuê (xem hired_coverage_check.csv).
import pandas as pd, numpy as np, os
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

O = os.path.join('outputs', 'everest-safety')
e = pd.read_csv('data/expeditions.csv')
m = pd.read_csv('data/members.csv')
ex = e[(e.peak_name == 'Everest') & (e.year >= 1950)].copy()
ev = m[(m.peak_name == 'Everest') & (m.year >= 1950)].copy()
ex['decade'] = ex.year // 10 * 10
ev['decade'] = ev.year // 10 * 10
ex['era'] = np.where(ex.year < 1990, '1950-1989', '1990-2019')
MEM, HIR = 'Thành viên đoàn', 'Nhân viên được thuê'


def wilson(k, n, z=1.96):
    p = k / n
    c = (p + z * z / 2 / n) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / 4 / n / n) / (1 + z * z / n)
    return c - h, c + h


def rows_for(label, g):
    out = []
    for gl, n, k in [(MEM, g.members.sum(), g.member_deaths.sum()), (HIR, g.hired_staff.sum(), g.hired_staff_deaths.sum())]:
        lo, hi = wilson(k, n)
        out.append(dict(period=label, group=gl, n=int(n), deaths=int(k), rate_per_1000=k / n * 1000, lo=lo * 1000, hi=hi * 1000))
    return out


rows = []
for dc, g in ex.groupby('decade'):
    rows += rows_for(str(dc), g)
for era, g in ex.groupby('era'):
    rows += rows_for(era, g)
rows += rows_for('1990-2019 bỏ 2014-2015', ex[(ex.year >= 1990) & ~ex.year.isin([2014, 2015])])
rows += rows_for('2014-2015', ex[ex.year.isin([2014, 2015])])
rows += rows_for('chỉ 2014', ex[ex.year.isin([2014])])
main = pd.DataFrame(rows)
main.to_csv(os.path.join(O, 'MAIN_death_rate_expedition_level.csv'), index=False)
print(main.round(2).to_string())


def fx(ak, an, bk, bn):
    return stats.fisher_exact([[ak, an - ak], [bk, bn - bk]])


for era, g in ex.groupby('era'):
    r = fx(g.hired_staff_deaths.sum(), g.hired_staff.sum(), g.member_deaths.sum(), g.members.sum())
    print(era, 'hired vs member: OR', round(r[0], 2), 'p', r[1])
a = ex[ex.era == '1990-2019']; b = ex[ex.era == '1950-1989']
print('members 1990+ vs <1990', fx(a.member_deaths.sum(), a.members.sum(), b.member_deaths.sum(), b.members.sum()))
print('hired 1990+ vs <1990', fx(a.hired_staff_deaths.sum(), a.hired_staff.sum(), b.hired_staff_deaths.sum(), b.hired_staff.sum()))
c = ex[ex.year >= 1990]
print('hired vs member 1990+ excl 2014-15:', fx(c[~c.year.isin([2014, 2015])].hired_staff_deaths.sum(), c[~c.year.isin([2014, 2015])].hired_staff.sum(),
      c[~c.year.isin([2014, 2015])].member_deaths.sum(), c[~c.year.isin([2014, 2015])].members.sum()))

cov = ev.groupby('decade').hired.sum().to_frame('hired_in_members_table').join(ex.groupby('decade').hired_staff.sum().to_frame('hired_in_expeditions'))
cov['coverage'] = cov.hired_in_members_table / cov.hired_in_expeditions
cov.to_csv(os.path.join(O, 'hired_coverage_check.csv'))
print(cov.round(2))

# Everest deaths share by hired group for 2010s and total counts
print('deaths by decade', ex.groupby('decade')[['member_deaths', 'hired_staff_deaths']].sum())

cols = {MEM: '#1f77b4', HIR: '#d95f02'}
decs = [str(x) for x in range(1960, 2020, 10)]
fig, ax = plt.subplots(figsize=(9, 5.4))
for g, c_ in cols.items():
    d = main[(main.group == g) & main.period.isin(decs)].copy()
    d['x'] = d.period.astype(int) + (2 if g == HIR else -2)
    ax.errorbar(d.x, d.rate_per_1000, yerr=[d.rate_per_1000 - d.lo, d.hi - d.rate_per_1000], marker='o', color=c_, capsize=3, label=g, lw=2)
    for _, r in d.iterrows():
        ax.annotate(f"{r.rate_per_1000:.1f}", (r.x, r.rate_per_1000), textcoords='offset points',
                    xytext=(0, 10 if g == HIR else -15), ha='center', color=c_, fontsize=9)
ax.axvline(1990, ls='--', color='grey')
ax.text(1991, ax.get_ylim()[1] * 0.93, 'Kỷ nguyên thương mại', color='grey', fontsize=9)
ax.set_xticks([int(x) for x in decs]); ax.set_xticklabels([f"{x}s" for x in decs])
ax.set_ylabel('Số ca tử vong trên 1.000 lượt tham gia')
ax.set_title('Everest: tử vong giảm ở cả hai nhóm; nhân viên thuê giảm sâu nhất rồi nhích lại\n'
             'ở thập niên 2010 (lở tuyết 2014). Thanh sai số = khoảng tin cậy 95%', fontsize=11)
ax.legend(frameon=False); ax.spines[['top', 'right']].set_visible(False); ax.set_ylim(bottom=0)
plt.tight_layout(); plt.savefig(os.path.join(O, 'death_rate_by_decade.png'), dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(9, 4.8))
p = ex.groupby('decade')[['members', 'hired_staff']].sum()
p.columns = [MEM, HIR]
p.plot(kind='bar', stacked=True, color=[cols[MEM], cols[HIR]], ax=ax)
ax.set_xticklabels([f"{d}s" for d in p.index], rotation=0)
ax.set_xlabel(''); ax.set_ylabel('Số lượt tham gia (theo đoàn)')
ax.set_title('Số lượt leo Everest tăng vọt; nhân viên được thuê đông gần bằng thành viên')
ax.legend(frameon=False); ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout(); plt.savefig(os.path.join(O, 'participants_by_decade.png'), dpi=150); plt.close()
