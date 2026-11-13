import pandas as pd, numpy as np
from scipy import stats


def pc(k, n, method='wilson'):
    k = np.asarray(k, float)
    n = np.asarray(n, float)
    z = 1.96
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return c - h, c + h


def trend_test(y, t):
    # Cochran-Armitage trend test (two-sided) for binary y over score t
    y = np.asarray(y, float)
    t = np.asarray(t, float)
    p = y.mean()
    T = np.sum((t - t.mean()) * y)
    var = p * (1 - p) * np.sum((t - t.mean())**2)
    z = T / np.sqrt(var)
    slope = T / np.sum((t - t.mean())**2)
    return z, 2 * (1 - stats.norm.cdf(abs(z))), slope

O = 'outputs/everest-safety/'
e = pd.read_csv('data/expeditions.csv')
m = pd.read_csv('data/members.csv')
ev = e[e.peak_name == 'Everest'].copy()
mv = m[m.peak_name == 'Everest'].copy()
for d in (ev, mv):
    d['decade'] = d.year // 10 * 10

# A. member-level (one row = one person-expedition)
r = mv.groupby(['decade', 'hired']).agg(n=('died', 'size'), deaths=('died', 'sum')).reset_index()
r['rate_pct'] = 100 * r.deaths / r.n
lo, hi = pc(r.deaths, r.n, method='wilson')
r['lo'] = 100 * lo
r['hi'] = 100 * hi
r['group'] = r.hired.map({True: 'Hired staff', False: 'Members'})
r.to_csv(O + 'rates_by_decade_members_table.csv', index=False)
A = r
print(A.pivot(index='decade', columns='group', values=['n', 'deaths', 'rate_pct']).round(2))

# B. expedition-level denominators (hired_staff above basecamp)
b = ev.groupby('decade').agg(exped=('expedition_id', 'size'), members=('members', 'sum'),
                             member_deaths=('member_deaths', 'sum'), hired=('hired_staff', 'sum'),
                             hired_deaths=('hired_staff_deaths', 'sum')).reset_index()
b['member_rate_pct'] = 100 * b.member_deaths / b.members
b['hired_rate_pct'] = 100 * b.hired_deaths / b.hired
b.to_csv(O + 'rates_by_decade_expedition_table.csv', index=False)
print(b.round(2))

# C. eras
mv['era2'] = pd.cut(mv.year, [1920, 1969, 1989, 1999, 2009, 2019],
                    labels=['<1970', '1970-89', '1990-99', '2000-09', '2010-19'])
C = mv.groupby(['era2', 'hired'], observed=True).agg(n=('died', 'size'), deaths=('died', 'sum')).reset_index()
C['rate_pct'] = 100 * C.deaths / C.n
C.to_csv(O + 'rates_by_era.csv', index=False)
print(C.round(2))
ev['era'] = np.where(ev.year < 1990, '1921-1989', '1990-2019')
E2 = ev.groupby('era').agg(members=('members', 'sum'), md=('member_deaths', 'sum'),
                           hired=('hired_staff', 'sum'), hd=('hired_staff_deaths', 'sum'))
E2['m_rate'] = 100 * E2.md / E2.members
E2['h_rate'] = 100 * E2.hd / E2.hired
E2.to_csv(O + 'rates_by_era_expedition.csv')
print(E2.round(2))


def fisher(a, n1, c, n2):
    return stats.fisher_exact([[a, n1 - a], [c, n2 - c]])


x = mv[mv.year >= 1990]
t = x.groupby('hired').died.agg(['sum', 'size'])
print(t)
print('hired vs members 1990+', fisher(t.loc[True, 'sum'], t.loc[True, 'size'], t.loc[False, 'sum'], t.loc[False, 'size']))
for h in (False, True):
    s = mv[(mv.hired == h) & (mv.year >= 1990)]
    a = s[s.year < 2000].died.agg(['sum', 'size'])
    z = s[s.year >= 2010].died.agg(['sum', 'size'])
    print('hired' if h else 'member', '1990s vs 2010s', a.tolist(), z.tolist(), fisher(a['sum'], a['size'], z['sum'], z['size']))
    p = mv[(mv.hired == h) & (mv.year >= 1960) & (mv.year < 1990)].died.agg(['sum', 'size'])
    q = s.died.agg(['sum', 'size'])
    print('1960-89 vs 1990+', p.tolist(), q.tolist(), fisher(p['sum'], p['size'], q['sum'], q['size']))
    z, pv, sl = trend_test(s.died, s.year)
    print('trend 1990+ hired=%s z=%.2f p=%.4f slope pp/yr=%.4f' % (h, z, pv, 100 * sl))

# D. context
ctx = mv.groupby('decade').agg(people=('died', 'size'), summit=('success', 'mean'), o2=('oxygen_used', 'mean')).reset_index()
bi = b.set_index('decade')
ctx['hired_per_member'] = ctx.decade.map(bi.hired / bi.members)
ctx['exped'] = ctx.decade.map(bi.exped)
ctx.to_csv(O + 'context_by_decade.csv', index=False)
print(ctx.round(2))

# E. causes, 1990+
dc = mv[(mv.died) & (mv.year >= 1990)].groupby(['death_cause', 'hired']).size().unstack(fill_value=0)
dc.to_csv(O + 'death_causes_1990plus.csv')
print(dc)

# F. deaths per year
yy = mv[mv.year >= 1990].groupby(['year', 'hired']).died.sum().unstack(fill_value=0)
yy.to_csv(O + 'deaths_by_year.csv')
print(yy[yy.sum(axis=1) >= 8])

# G. sensitivity: 2010-19 without 2014 and 2015
x2 = mv[(mv.year >= 2010) & (~mv.year.isin([2014, 2015]))].groupby('hired').died.agg(['sum', 'size'])
x2['rate'] = 100 * x2['sum'] / x2['size']
print(x2)

# H. who are hired staff
print(mv[mv.hired].citizenship.value_counts().head(4))

# I. deaths per 100 summiters 1990+
s = mv[mv.year >= 1990].groupby('hired').agg(summ=('success', 'sum'), d=('died', 'sum'))
s['d_per_100_summit'] = 100 * s.d / s.summ
print(s)
