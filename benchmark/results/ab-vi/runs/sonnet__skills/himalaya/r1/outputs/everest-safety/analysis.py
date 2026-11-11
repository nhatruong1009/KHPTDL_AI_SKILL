import pandas as pd, numpy as np, os
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

O = os.path.join('outputs', 'everest-safety')
m = pd.read_csv('data/members.csv')
e = pd.read_csv('data/expeditions.csv')
ev = m[(m.peak_name == 'Everest') & (m.year >= 1950)].copy()
ex = e[(e.peak_name == 'Everest') & (e.year >= 1950)].copy()
for d in (ev, ex):
    d['decade'] = d.year // 10 * 10
MEM, HIR = 'Thành viên đoàn', 'Nhân viên được thuê'
ev['group'] = np.where(ev.hired, HIR, MEM)


def wilson(k, n, z=1.96):
    p = k / n
    c = (p + z * z / 2 / n) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / 4 / n / n) / (1 + z * z / n)
    return c - h, c + h


def table(df, key):
    g = df.groupby([key, 'group']).agg(n=('died', 'size'), deaths=('died', 'sum')).reset_index()
    g['rate_per_1000'] = g.deaths / g.n * 1000
    ci = [wilson(k, n) for k, n in zip(g.deaths, g.n)]
    g['lo'] = [c[0] * 1000 for c in ci]
    g['hi'] = [c[1] * 1000 for c in ci]
    return g


t = table(ev, 'decade')
t.to_csv(os.path.join(O, 'death_rate_by_decade_group.csv'), index=False)
print(t.round(2).to_string())

ev['era'] = np.where(ev.year < 1990, '1950-1989', '1990-2019')
te = table(ev, 'era')
te.to_csv(os.path.join(O, 'death_rate_by_era_group.csv'), index=False)
print(te.round(2))

for era in ['1950-1989', '1990-2019']:
    s = ev[ev.era == era]
    a = s[s.hired]; b = s[~s.hired]
    tab = [[a.died.sum(), len(a) - a.died.sum()], [b.died.sum(), len(b) - b.died.sum()]]
    print(era, 'hired vs member p=', stats.fisher_exact(tab)[1], 'RR=', a.died.mean() / b.died.mean())
for g in [MEM, HIR]:
    s = ev[ev.group == g]
    a = s[s.era == '1990-2019']; b = s[s.era == '1950-1989']
    tab = [[a.died.sum(), len(a) - a.died.sum()], [b.died.sum(), len(b) - b.died.sum()]]
    print(g, 'era change p=', stats.fisher_exact(tab)[1], 'RR=', a.died.mean() / b.died.mean())

x = ex.groupby('decade').agg(members=('members', 'sum'), md=('member_deaths', 'sum'),
                             hired=('hired_staff', 'sum'), hd=('hired_staff_deaths', 'sum')).reset_index()
x['member_rate_per_1000'] = x.md / x.members * 1000
x['hired_rate_per_1000'] = x.hd / x.hired * 1000
x.to_csv(os.path.join(O, 'sensitivity_expedition_level.csv'), index=False)
print(x.round(2))

sh = ev.groupby('decade').agg(n=('died', 'size'), hired_n=('hired', 'sum'), hired_share=('hired', 'mean'),
                              deaths=('died', 'sum')).reset_index()
sh['hired_deaths'] = ev[ev.hired].groupby('decade').died.sum().reindex(sh.decade).fillna(0).values
sh['hired_share_of_deaths'] = sh.hired_deaths / sh.deaths
print(sh.round(3))
sh.to_csv(os.path.join(O, 'hired_share_by_decade.csv'), index=False)

y = ev.groupby(['year', 'group']).agg(n=('died', 'size'), d=('died', 'sum')).reset_index()
y.to_csv(os.path.join(O, 'yearly.csv'), index=False)
print(y[y.d >= 5].to_string())

ex1415 = ev[ev.year.isin([2014, 2015])]
print('2014-15 deaths by group'); print(ex1415.groupby('group').died.agg(['size', 'sum']))
print('excluding 2014/2015, since 1990')
tx = table(ev[(ev.year >= 1990) & ~ev.year.isin([2014, 2015])], 'decade')
print(tx.round(2)[['decade', 'group', 'n', 'deaths', 'rate_per_1000']])
tx.to_csv(os.path.join(O, 'excl_2014_2015.csv'), index=False)

c = ev[(ev.died) & (ev.year >= 1990)].groupby(['death_cause', 'group']).size().unstack().fillna(0).astype(int)
c.to_csv(os.path.join(O, 'death_causes_since1990.csv'))
print(c)
s = ev.groupby(['decade', 'group']).success.mean().unstack()
s.to_csv(os.path.join(O, 'success_rate.csv'))
print(s.round(3))

cols = {MEM: '#1f77b4', HIR: '#d95f02'}
fig, ax = plt.subplots(figsize=(9, 5.4))
tt = t[t.decade >= 1950]
for g, c_ in cols.items():
    d = tt[(tt.group == g) & (tt.n >= 100)]
    off = 2 if g == HIR else -2
    ax.errorbar(d.decade + off, d.rate_per_1000, yerr=[d.rate_per_1000 - d.lo, d.hi - d.rate_per_1000],
                marker='o', color=c_, capsize=3, label=g, lw=2)
    for _, r in d.iterrows():
        ax.annotate(f"{r.rate_per_1000:.1f}", (r.decade + off, r.rate_per_1000), textcoords='offset points',
                    xytext=(0, 9 if g == HIR else -15), ha='center', color=c_, fontsize=9)
ax.axvline(1990, ls='--', color='grey')
ax.text(1991, ax.get_ylim()[1] * 0.93, 'Kỷ nguyên thương mại', color='grey', fontsize=9)
dd = sorted(tt.decade.unique())
ax.set_xticks(dd); ax.set_xticklabels([f"{d}s" for d in dd])
ax.set_ylabel('Số ca tử vong trên 1.000 lượt tham gia')
ax.set_title('Everest: tử vong giảm rõ ở cả hai nhóm, nhưng nhân viên được thuê\nluôn có rủi ro cao hơn (thanh sai số = khoảng tin cậy 95%)', fontsize=11)
ax.legend(frameon=False); ax.spines[['top', 'right']].set_visible(False); ax.set_ylim(bottom=0)
plt.tight_layout(); plt.savefig(os.path.join(O, 'alt_members_table_rate.png'), dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(9, 4.8))
p = ev.groupby(['decade', 'group']).size().unstack().fillna(0)
p[[MEM, HIR]].plot(kind='bar', stacked=True, color=[cols[MEM], cols[HIR]], ax=ax)
ax.set_xticklabels([f"{d}s" for d in p.index], rotation=0)
ax.set_xlabel(''); ax.set_ylabel('Số lượt tham gia')
ax.set_title('Số lượt leo Everest tăng vọt; nhân viên được thuê ngày càng đông')
ax.legend(frameon=False); ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout(); plt.savefig(os.path.join(O, 'alt_members_table_participants.png'), dpi=150); plt.close()
