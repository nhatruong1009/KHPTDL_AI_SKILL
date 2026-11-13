import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

m = pd.read_csv('data/members.csv')
m = m[(m.peak_id == 'EVER') & (m.year >= 1950)].copy()
m['dec'] = m.year // 10 * 10
m['nhom'] = m.hired.map({False: 'Thành viên đoàn', True: 'Nhân viên được thuê'})
g = m.groupby(['dec', 'nhom']).agg(n=('died', 'size'), d=('died', 'sum'), s=('success', 'sum')).reset_index()
g['rate'] = g.d / g.n * 100
g['per_summit'] = g.d / g.s * 100
g.to_csv('outputs/tyle_theo_thapky.csv', index=False)
print(g)
for lo, hi in [(1950, 1989), (1990, 2019)]:
    s = m[(m.year >= lo) & (m.year <= hi)].groupby('nhom').agg(n=('died', 'size'), d=('died', 'sum'), s=('success', 'sum'))
    s['rate'] = s.d / s.n * 100
    s['per_summit'] = s.d / s.s * 100
    print(lo, hi); print(s)
# 2014-2015 excluded sensitivity
x = m[(m.year >= 2010) & (~m.year.isin([2014, 2015]))].groupby('nhom').agg(n=('died', 'size'), d=('died', 'sum'))
x['rate'] = x.d / x.n * 100
print(x)

fig, ax = plt.subplots(figsize=(9, 5))
col = {'Thành viên đoàn': '#2a6fb0', 'Nhân viên được thuê': '#d9822b'}
for k, d in g.groupby('nhom'):
    d = d[d.dec >= 1970]
    ax.plot(d.dec.astype(str) + 's', d.rate, marker='o', color=col[k], lw=2.5, label=k)
    for _, r in d.iterrows():
        ax.annotate(f'{r.rate:.1f}%', (str(int(r.dec)) + 's', r.rate), textcoords='offset points', xytext=(0, 8), ha='center', fontsize=9, color=col[k])
ax.axvline(1.5, color='gray', ls='--', lw=1)
ax.text(1.55, ax.get_ylim()[1] * 0.9, 'Kỷ nguyên thương mại (từ ~1990)', fontsize=9, color='gray')
ax.set_title('Everest: tỉ lệ tử vong theo thập kỷ, thành viên đoàn và nhân viên được thuê')
ax.set_ylabel('Tử vong / 100 người lên núi (%)')
ax.set_xlabel('Thập kỷ (dữ liệu 2010s đến hết 2019)')
ax.spines[['top', 'right']].set_visible(False)
ax.legend(frameon=False)
plt.tight_layout()
plt.savefig('outputs/chart_tuvong_everest.png', dpi=150)
