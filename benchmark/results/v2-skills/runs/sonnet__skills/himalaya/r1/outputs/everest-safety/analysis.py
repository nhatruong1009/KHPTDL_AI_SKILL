"""Everest: tỉ lệ tử vong của thành viên đoàn vs nhân viên được thuê theo thập kỷ.
Chạy từ thư mục gốc dự án: python -I outputs/everest-safety/analysis.py
Đơn vị: một dòng members.csv (peak_id == 'EVER') = một lượt người tham gia một đoàn.
Tỉ lệ tử vong = died / số lượt tham gia."""
import pandas as pd, numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

O = 'outputs/everest-safety/'
m = pd.read_csv('data/members.csv')
e = pd.read_csv('data/expeditions.csv')
ev = m[m.peak_id == 'EVER'].copy()
ev['dec'] = ev.year // 10 * 10
MEM, HIR = 'Thành viên đoàn', 'Nhân viên được thuê'
ev['nhom'] = np.where(ev.hired, HIR, MEM)

# đối chiếu với bảng expeditions
x = e[e.peak_id == 'EVER']
print('Đối chiếu: members died', ev.died.sum(), 'vs expeditions', x.member_deaths.sum() + x.hired_staff_deaths.sum())
print('  thành viên', (~ev.hired & ev.died).sum(), x.member_deaths.sum(), '| thuê', (ev.hired & ev.died).sum(), x.hired_staff_deaths.sum())


def wilson(d, n, z=1.96):
    p = d / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def tab(df, key):
    g = df.groupby([key, 'nhom']).agg(n=('died', 'size'), deaths=('died', 'sum')).reset_index()
    g['rate_pct'] = g.deaths / g.n * 100
    lo, hi = wilson(g.deaths, g.n)
    g['lo'] = lo * 100
    g['hi'] = hi * 100
    return g


dec = tab(ev[ev.year >= 1950], 'dec')
dec.to_csv(O + 'rate_by_decade.csv', index=False)
print(dec.round(2).to_string())

ev['era'] = np.where(ev.year < 1990, '1950-1989', '1990-2019')
ev.loc[ev.year < 1950, 'era'] = np.nan
era = tab(ev.dropna(subset=['era']), 'era')
era.to_csv(O + 'rate_by_era.csv', index=False)
print(era.round(2))

# độ nhạy: bỏ 2014 (tuyết lở Khumbu) và 2015 (động đất)
s = tab(ev[(ev.year >= 1990) & ~ev.year.isin([2014, 2015])].assign(era='1990-2019 bỏ 2014-15'), 'era')
s.to_csv(O + 'sensitivity_excl_2014_2015.csv', index=False)
print(s.round(2))
print(ev[ev.year.isin([2014, 2015])].groupby(['year', 'nhom']).agg(n=('died', 'size'), d=('died', 'sum')))

# so sánh nhóm: RR thuê / thành viên theo từng giai đoạn (Fisher + CI log)
rr_rows = []
for key, d_ in [('era', ev.dropna(subset=['era'])), ('dec', ev[ev.year >= 1950])]:
    for k, g in d_.groupby(key):
        a = g[g.hired]
        b = g[~g.hired]
        da, na, db, nb = a.died.sum(), len(a), b.died.sum(), len(b)
        if da == 0 or db == 0:
            rr, lo, hi = np.nan, np.nan, np.nan
        else:
            rr = (da / na) / (db / nb)
            se = np.sqrt(1 / da - 1 / na + 1 / db - 1 / nb)
            lo, hi = np.exp(np.log(rr) - 1.96 * se), np.exp(np.log(rr) + 1.96 * se)
        p = stats.fisher_exact([[da, na - da], [db, nb - db]])[1]
        rr_rows.append((key, k, na, da, nb, db, rr, lo, hi, p))
rr = pd.DataFrame(rr_rows, columns=['loai', 'giai_doan', 'n_thue', 'tv_thue', 'n_thanhvien', 'tv_thanhvien', 'RR_thue_vs_thanhvien', 'lo', 'hi', 'p_fisher'])
rr.to_csv(O + 'rr_hired_vs_member.csv', index=False)
print(rr.round(3).to_string())

# xu hướng: Cochran-Armitage theo thập kỷ (1950+ và 1990+), từng nhóm
def ca(g):
    t = g.groupby('dec').agg(n=('died', 'size'), d=('died', 'sum'))
    t = t[t.n > 0]
    sc = ((t.index - 1990) / 10).values.astype(float)
    n, d = t.n.values, t.d.values
    N, D = n.sum(), d.sum()
    p = D / N
    T = (sc * (d - n * p)).sum()
    var = p * (1 - p) * ((n * sc ** 2).sum() - (n * sc).sum() ** 2 / N)
    z = T / np.sqrt(var)
    return z, 2 * stats.norm.sf(abs(z))


tr = []
for lbl, f in [('1950+', 1950), ('1990+', 1990)]:
    for h, g in ev[ev.year >= f].groupby('nhom'):
        z, p = ca(g)
        tr.append((lbl, h, z, p))
tr = pd.DataFrame(tr, columns=['tu_nam', 'nhom', 'z_xu_huong', 'p'])
tr.to_csv(O + 'trend_test.csv', index=False)
print(tr.round(4))

# thêm: tử vong / 100 người lên đỉnh, tỉ lệ dùng oxy
t2 = ev[ev.year >= 1950].groupby(['dec', 'nhom']).agg(n=('died', 'size'), summiters=('success', 'sum'), deaths=('died', 'sum'), o2=('oxygen_used', 'mean')).reset_index()
t2['deaths_per_100_summiters'] = t2.deaths / t2.summiters * 100
t2['o2_pct'] = t2.o2 * 100
t2.drop(columns='o2').to_csv(O + 'summiters_o2_by_decade.csv', index=False)
print(t2.round(2).to_string())

# cơ cấu, nguyên nhân
print(ev[ev.year >= 1950].groupby('dec').hired.agg(['size', 'mean']).round(3))
c = ev[ev.died & (ev.year >= 1990)].groupby(['death_cause', 'nhom']).size().unstack().fillna(0)
c.to_csv(O + 'death_causes_1990plus.csv')
print(c)
print('Quốc tịch Nepal trong nhân viên thuê 1990+', round((ev[(ev.year >= 1990) & ev.hired].citizenship == 'Nepal').mean(), 3))
yr = ev[ev.year >= 1990].groupby(['year', 'nhom']).agg(n=('died', 'size'), d=('died', 'sum')).unstack().fillna(0)
yr.to_csv(O + 'yearly_1990plus.csv')

# mùa xuân vs tất cả (độ nhạy: chỉ mùa Spring)
sp = tab(ev[(ev.season == 'Spring') & (ev.year >= 1950)], 'dec')
sp.to_csv(O + 'sensitivity_spring_only.csv', index=False)
print(sp.round(2).to_string())

# độ nhạy theo thập kỷ: bỏ 2014-2015
sx = tab(ev[(ev.year >= 1990) & ~ev.year.isin([2014, 2015])], 'dec')
sx.to_csv(O + 'sensitivity_decade_excl_2014_2015.csv', index=False)
print(sx.round(2).to_string())

# ---------- biểu đồ ----------
col = {MEM: '#1f77b4', HIR: '#d95f02'}
fig, ax = plt.subplots(figsize=(9.5, 5.5))
for k, g in dec.groupby('nhom'):
    xs = g.dec + (3 if k == HIR else 0)
    ax.errorbar(xs, g.rate_pct, yerr=[g.rate_pct - g.lo, g.hi - g.rate_pct], marker='o', capsize=3, color=col[k], label=k)
ax.axvline(1988, ls='--', color='grey')
ax.text(1989, ax.get_ylim()[1] * 0.92, 'Kỷ nguyên\nthương mại (~1990)', color='grey')
ax.set_xticks(range(1950, 2020, 10))
ax.set_xticklabels([str(d) + 's' for d in range(1950, 2020, 10)])
ax.set_ylabel('Tử vong / 100 lượt tham gia (KTC 95%)')
ax.set_title('Tử vong trên Everest giảm mạnh; khoảng cách thuê – thành viên khép lại sau 1990')
ax.legend(frameon=False)
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig(O + 'chart1_ty_le_tu_vong_theo_thap_ky.png', dpi=150)
plt.close()

fig, ax = plt.subplots(figsize=(9.5, 5))
p = ev[ev.year >= 1950].groupby(['dec', 'nhom']).size().unstack().fillna(0)[[MEM, HIR]]
p.plot(kind='bar', stacked=True, color=[col[c_] for c_ in p.columns], ax=ax)
ax.set_xticklabels([str(d) + 's' for d in p.index], rotation=0)
ax.set_xlabel('')
ax.set_ylabel('Số lượt tham gia (người-chuyến)')
ax.set_title('Số lượt leo Everest tăng ~4 lần từ 1980s đến 2010s, nhân viên thuê nay chiếm 44%')
ax.legend(title='', frameon=False)
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig(O + 'chart2_quy_mo_va_co_cau.png', dpi=150)
plt.close()
