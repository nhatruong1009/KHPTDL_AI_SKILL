"""Expedition-level (headline) rates with CIs, tests, sensitivity. Run after analysis.py."""
import pandas as pd, numpy as np
from scipy import stats

O = 'outputs/everest-safety/'
e = pd.read_csv('data/expeditions.csv')
ev = e[e.peak_name == 'Everest'].copy()


def wil(k, n):
    z = 1.96
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return 100 * (c - h), 100 * (c + h)


def summarize(df, key):
    g = df.groupby(key).agg(exped=('expedition_id', 'size'), members=('members', 'sum'),
                            member_deaths=('member_deaths', 'sum'), hired=('hired_staff', 'sum'),
                            hired_deaths=('hired_staff_deaths', 'sum')).reset_index()
    for p, k, n in (('member', 'member_deaths', 'members'), ('hired', 'hired_deaths', 'hired')):
        g[p + '_rate_pct'] = 100 * g[k] / g[n]
        lo, hi = wil(g[k].values, g[n].values)
        g[p + '_lo'] = lo
        g[p + '_hi'] = hi
    return g


ev['period'] = pd.cut(ev.year, [1920, 1969, 1989, 1999, 2009, 2019],
                      labels=['1921-69', '1970-89', '1990-99', '2000-09', '2010-19'])
ev['decade'] = ev.year // 10 * 10
D = summarize(ev, 'decade')
P = summarize(ev, 'period')
D.to_csv(O + 'headline_expedition_by_decade.csv', index=False)
P.to_csv(O + 'headline_expedition_by_period.csv', index=False)
pd.set_option('display.width', 250)
print(D.round(2).to_string())
print(P.round(2).to_string())


def fisher(k1, n1, k2, n2):
    return stats.fisher_exact([[k1, n1 - k1], [k2, n2 - k2]])


# sanity: deaths never exceed headcount
print('rows with deaths>headcount:', ((ev.member_deaths > ev.members) | (ev.hired_staff_deaths > ev.hired_staff)).sum())
print('rows hired_staff==0 & hired deaths>0:', ((ev.hired_staff == 0) & (ev.hired_staff_deaths > 0)).sum())

# tests
pre = ev[(ev.year >= 1970) & (ev.year < 1990)]
post = ev[ev.year >= 1990]
for lab, col_d, col_n in (('members', 'member_deaths', 'members'), ('hired', 'hired_staff_deaths', 'hired_staff')):
    a, an, b, bn = pre[col_d].sum(), pre[col_n].sum(), post[col_d].sum(), post[col_n].sum()
    print(lab, '1970-89 vs 1990+: %d/%d=%.2f%% vs %d/%d=%.2f%%' % (a, an, 100 * a / an, b, bn, 100 * b / bn), fisher(a, an, b, bn))
# hired vs members within periods
for p in P.period:
    r = P[P.period == p].iloc[0]
    f = fisher(r.hired_deaths, r.hired, r.member_deaths, r.members)
    print(p, 'hired vs member OR=%.2f p=%.4f' % (f[0], f[1]))
# 1990s vs 2010s each group
for lab, kd, kn in (('members', 'member_deaths', 'members'), ('hired', 'hired_deaths', 'hired')):
    a = P[P.period == '1990-99'].iloc[0]
    b = P[P.period == '2010-19'].iloc[0]
    print(lab, '1990s vs 2010s', fisher(a[kd], a[kn], b[kd], b[kn]))

# sensitivity: 2010-19 without 2014 & 2015
s = ev[(ev.year >= 2010) & (~ev.year.isin([2014, 2015]))]
print('2010-19 excl 2014/15: members %.2f%% (%d/%d) hired %.2f%% (%d/%d)' % (
    100 * s.member_deaths.sum() / s.members.sum(), s.member_deaths.sum(), s.members.sum(),
    100 * s.hired_staff_deaths.sum() / s.hired_staff.sum(), s.hired_staff_deaths.sum(), s.hired_staff.sum()))
y = ev[ev.year.isin([2014, 2015])]
print('2014/15 hired deaths', y.hired_staff_deaths.sum(), 'member deaths', y.member_deaths.sum())
yr = ev[ev.year >= 2000].groupby('year').agg(md=('member_deaths', 'sum'), m=('members', 'sum'),
                                              hd=('hired_staff_deaths', 'sum'), h=('hired_staff', 'sum'))
print(yr)

# per-expedition fatality incidence and staffing
ev['any_death'] = (ev.member_deaths + ev.hired_staff_deaths) > 0
f = ev.groupby('period', observed=True).agg(exped=('expedition_id', 'size'), fatal=('any_death', 'mean'),
                                            hired_ratio=('hired_staff', 'sum'), m=('members', 'sum'))
f['hired_ratio'] = f.hired_ratio / f.m
print(f.round(3))
f.to_csv(O + 'expedition_fatality_incidence.csv')
# share of 1990+ hired deaths from avalanche/icefall (members table)
m = pd.read_csv('data/members.csv')
mv = m[(m.peak_name == 'Everest') & m.died & (m.year >= 1990)]
for h in (True, False):
    x = mv[mv.hired == h]
    print('hired' if h else 'member', len(x), x.death_cause.isin(['Avalanche', 'Icefall collapse', 'Falling rock / ice', 'Crevasse']).mean().round(2))
