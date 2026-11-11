import pandas as pd
m = pd.read_csv('data/members.csv')
e = pd.read_csv('data/expeditions.csv')
m = m[m.peak_id == 'EVER'].copy()
print(len(m), m.year.min(), m.year.max(), m.hired.value_counts(dropna=False).to_dict(), m.died.value_counts(dropna=False).to_dict())
m['dec'] = m.year // 10 * 10
g = m.groupby(['dec', 'hired']).agg(n=('died', 'size'), d=('died', 'sum'), s=('success', 'mean')).reset_index()
g['rate'] = g.d / g.n * 100
print(g.to_string())
m['era'] = (m.year >= 1990).map({False: '<1990', True: '>=1990'})
r = m.groupby(['era', 'hired']).agg(n=('died', 'size'), d=('died', 'sum'), s=('success', 'mean'))
r['r'] = r.d / r.n * 100
print(r)
e = e[e.peak_id == 'EVER'].copy()
e['dec'] = e.year // 10 * 10
x = e.groupby('dec')[['members', 'member_deaths', 'hired_staff', 'hired_staff_deaths']].sum()
x['mr'] = x.member_deaths / x.members * 100
x['hr'] = x.hired_staff_deaths / x.hired_staff * 100
print(x)
print(m[m.died].groupby(['hired', 'death_cause']).size().unstack(0).sort_values(True, ascending=False).head(10))
print(m[m.year >= 1990].groupby(['year', 'hired']).died.sum().unstack().tail(12))
print(m.groupby(['dec', 'hired']).oxygen_used.mean().unstack())
