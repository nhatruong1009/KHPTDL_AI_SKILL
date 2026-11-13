"""Kiem tra do nhay + khoang bat dinh du bao + bieu do. Chay sau prep.py va analysis.py."""
import pandas as pd, numpy as np
from scipy import stats
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

m = pd.read_csv('monthly.csv', index_col=0, parse_dates=True)
d = pd.read_csv('daily.csv', index_col=0, parse_dates=True)
w = pd.read_csv('weekly.csv', index_col=0, parse_dates=True)
bt = pd.read_csv('backtest_detail.csv', parse_dates=['target'])
gaps = pd.read_csv('data_gaps.csv', parse_dates=['start', 'end'])
y = m.kwh_per_day

# ---- Xu huong: Jan-Nov cung ky, co/khong thang 8, CI he so xu huong sau khi kiem soat mua vu ----
rows = []
for yr in [2007, 2008, 2009, 2010]:
    s = y[(y.index >= f'{yr}-01-01') & (y.index <= f'{yr}-10-01')]
    rows.append(dict(nam=yr, jan_oct=s.mean(), jan_oct_bo_thang8=s[s.index.month != 8].mean()))
tr = pd.DataFrame(rows); print(tr.round(2).to_string()); tr.to_csv('trend_jan_oct.csv', index=False)
full = y[(y.index >= '2007-01-01') & (y.index <= '2010-10-01')]
t = np.arange(len(full)); X = np.column_stack([t, pd.get_dummies(full.index.month).values.astype(float)])
b, *_ = np.linalg.lstsq(X, full.values, rcond=None)
res = full.values - X @ b; dof = len(full) - X.shape[1]; s2 = res @ res / dof
se = np.sqrt(s2 * np.linalg.inv(X.T @ X)[0, 0]); tc = stats.t.ppf(.975, dof)
print('He so xu huong/nam: %.2f  CI95 [%.2f, %.2f]' % (b[0] * 12, (b[0] - tc * se) * 12, (b[0] + tc * se) * 12))
# bo thang 8/2008 (nhà vang)
mask = ~((full.index.year == 2008) & (full.index.month == 8))
X2, y2 = X[mask], full.values[mask]
b2, *_ = np.linalg.lstsq(X2, y2, rcond=None); r2 = y2 - X2 @ b2; dof2 = len(y2) - X2.shape[1]
se2 = np.sqrt(r2 @ r2 / dof2 * np.linalg.inv(X2.T @ X2)[0, 0]); tc2 = stats.t.ppf(.975, dof2)
print('Bo 8/2008: %.2f  CI95 [%.2f, %.2f]' % (b2[0] * 12, (b2[0] - tc2 * se2) * 12, (b2[0] + tc2 * se2) * 12))

# ---- Do nhay nguong bat thuong tuan ----
for z in [3, 4, 5]:
    print('nguong |z|>%d: %d tuan' % (z, (w.rz.abs() > z).sum()))

# ---- Du bao 12/2010: nhieu phuong an muc nen/chi so mua vu ----
last12 = y['2009-12-01':'2010-11-01'].mean()
ratios = {}
for yr in [2007, 2008, 2009]:
    blk = y[f'{yr}-01-01':f'{yr}-12-01']
    ratios[yr] = (blk[f'{yr}-12-01'] / blk.mean(), blk[f'{yr}-12-01'] / blk.drop(pd.Timestamp(f'{yr}-08-01')).mean())
print('last12 (12/2009-11/2010):', round(last12, 2))
for yr, (a, c) in ratios.items(): print(yr, 'ty le Dec/TB nam %.3f ; bo thang 8: %.3f' % (a, c))
rat_all = np.mean([a for a, _ in ratios.values()])
rat_no8 = np.mean([c for _, c in ratios.values()])
last12_no8 = y['2009-12-01':'2010-11-01'].drop(pd.Timestamp('2010-08-01')).mean()
sens = {
    'A_chinh: muc 12T x chi so TB 3 nam': last12 * rat_all,
    'B: bo thang 8 khoi muc & chi so': last12_no8 * rat_no8,
    'C: chi so Dec 2009 (nam gan nhat)': last12 * ratios[2009][0],
    'D: lap lai Dec 2009 (seasonal naive)': y['2009-12-01'],
    'E: TB Dec 2007-2009': y[y.index.month == 12][1:].mean(),
}
sens = pd.Series(sens); print((sens * 31).round(0).to_string())
sens.mul(31).rename('kwh_thang12').to_csv('forecast_sensitivity.csv')

# ---- Khoang bat dinh: sai so log backtest cua mo hinh chinh (seasonal_ratio) ----
e = bt[bt.model == 'seasonal_ratio'].lerr.values
sd = e.std(ddof=1); n = len(e)
print('backtest n=%d, mean log err %.3f, sd %.3f' % (n, e.mean(), sd))
point = sens.iloc[0] * 31
tq = lambda p: stats.t.ppf(p, n - 1)
# sai so 1 buoc + do bat dinh cua chi so mua vu (sd log 3 nam Dec / sqrt(3))
lr = np.log([a for a, _ in ratios.values()]); sd_ratio = lr.std(ddof=1)
sd_tot = np.sqrt(sd ** 2 + sd_ratio ** 2 / 3)
print('sd log ty le Dec giua cac nam %.3f ; sd tong hop %.3f' % (sd_ratio, sd_tot))
out = []
for lvl in [0.8, 0.95]:
    q = stats.t.ppf(0.5 + lvl / 2, n - 1)
    out.append(dict(muc=lvl, thap=point * np.exp(-q * sd_tot), cao=point * np.exp(q * sd_tot)))
    # khoang kinh nghiem tu backtest
    qa, qb = np.quantile(e, [(1 - lvl) / 2, 0.5 + lvl / 2])
    out[-1].update(emp_thap=point * np.exp(-qb), emp_cao=point * np.exp(-qa))
pi = pd.DataFrame(out); print('diem:', round(point, 1)); print(pi.round(0).to_string())
pi.assign(diem=point).to_csv('forecast_interval.csv', index=False)
# do phu cua khoang: backtest coverage
cov = np.mean(np.abs(e) <= stats.t.ppf(.9, n - 1) * sd); print('coverage 80%% trong backtest: %.2f' % cov)

# ============ BIEU DO ============
plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
C1, C2, C3 = '#1f5fa8', '#d1495b', '#888888'
# 1. thang + du bao
fig, ax = plt.subplots(figsize=(12, 5.5))
mm = m.copy(); fm = mm[mm.full]
ax.plot(fm.index, fm.kwh_est, color=C1, marker='o', ms=3.5, label='kWh/thang (đã quy đổi theo độ phủ dữ liệu)')
ax.plot(mm.index[[0]], mm.kwh_est.iloc[[0]], 'o', color=C3, mfc='white', label='Tháng không đủ dữ liệu (12/2006, 11/2010)')
ax.plot(mm.index[[-1]], mm.kwh_est.iloc[[-1]], 'o', color=C3, mfc='white')
T = pd.Timestamp('2010-12-01')
ax.errorbar([T], [point], yerr=[[point - pi.thap[1]], [pi.cao[1] - point]], color=C2, capsize=5, lw=1.5, label='Dự báo 12/2010, khoảng 95%')
ax.errorbar([T], [point], yerr=[[point - pi.thap[0]], [pi.cao[0] - point]], color=C2, capsize=0, lw=5, alpha=.45, label='khoảng 80%')
ax.plot([T], [point], 'D', color=C2)
ax.annotate('Dự báo 12/2010\n≈ %d kWh' % round(point, -1), (T, point), (T - pd.Timedelta(days=330), 1330), color=C2, arrowprops=dict(arrowstyle='-', color=C2))
ax.annotate('8/2008: nhà gần như\nvắng người (206 kWh)', (pd.Timestamp('2008-08-01'), 206), (pd.Timestamp('2008-10-15'), 320), arrowprops=dict(arrowstyle='-', color=C3), color='#444')
ax.annotate('Có 5 ngày mất dữ liệu\n(17–22/8/2010)', (pd.Timestamp('2010-08-01'), 440), (pd.Timestamp('2010-02-01'), 250), arrowprops=dict(arrowstyle='-', color=C3), color='#444')
ax.set_ylabel('kWh/tháng'); ax.set_ylim(0, 1500)
ax.set_title('Điện năng tháng dao động theo mùa (đông cao, hè thấp) nhưng không có xu hướng tăng/giảm rõ; dự báo 12/2010 ≈ %d kWh' % round(point, -1), fontsize=11.5, loc='left')
ax.legend(loc='lower left', fontsize=9, frameon=False, bbox_to_anchor=(0.0, 0.0), ncol=1)
fig.tight_layout(); fig.savefig('01_thang_va_du_bao.png', dpi=150); plt.close()

# 2. Jan-Oct cung ky (xu huong phang) + mua vu thang
fig, axs = plt.subplots(1, 2, figsize=(12, 4.6))
ax = axs[0]
ax.bar(tr.nam.astype(str), tr.jan_oct, color=C1, width=.6)
for i, v in enumerate(tr.jan_oct): ax.text(i, v + .3, '%.1f' % v, ha='center')
ax.set_ylim(0, 32); ax.set_ylabel('kWh/ngày (TB tháng 1–10)')
ax.set_title('Cùng kỳ 1–10: 24,5–25,1 kWh/ngày,\nkhông có xu hướng rõ qua 4 năm', fontsize=11, loc='left')
ax = axs[1]
st = pd.read_csv('seasonal_month.csv', index_col=0)
for c in ['2007', '2008', '2009', '2010']: ax.plot(st.index, st[c], marker='o', ms=3, lw=1, alpha=.6, label=c)
ax.plot(st.index, st['mean'], color='k', lw=2.5, label='TB')
ax.set_xticks(range(1, 13)); ax.set_xlabel('Tháng'); ax.set_ylabel('kWh/ngày'); ax.legend(frameon=False, ncol=3, fontsize=9)
ax.set_title('Mùa vụ năm: tháng 1 cao gấp ~2,5 lần tháng 8', fontsize=11, loc='left')
fig.tight_layout(); fig.savefig('02_xu_huong_va_mua_vu_nam.png', dpi=150); plt.close()

# 3. Ngay + tuan
fig, axs = plt.subplots(1, 2, figsize=(12, 4.6))
ph = pd.read_csv('seasonal_hour.csv', index_col=0)
axs[0].plot(ph.index, ph.ngay_thuong, color=C1, lw=2, label='Ngày thường'); axs[0].plot(ph.index, ph.cuoi_tuan, color=C2, lw=2, label='Cuối tuần')
axs[0].set_xlabel('Giờ trong ngày'); axs[0].set_ylabel('kWh/giờ'); axs[0].legend(frameon=False)
axs[0].set_title('Hai đỉnh ngày thường (7h, 20–21h); cuối tuần\ndùng nhiều hơn ban ngày', fontsize=11, loc='left')
dw = pd.read_csv('seasonal_dow.csv', index_col=0).iloc[:, 0]
axs[1].bar(['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'], dw.values, color=[C1] * 5 + [C2] * 2)
for i, v in enumerate(dw.values): axs[1].text(i, v + .3, '%.1f' % v, ha='center')
axs[1].set_ylabel('kWh/ngày'); axs[1].set_ylim(0, 34)
axs[1].set_title('Thứ Bảy/Chủ nhật cao hơn ngày thường ~19%', fontsize=11, loc='left')
fig.tight_layout(); fig.savefig('03_mua_vu_ngay_tuan.png', dpi=150); plt.close()

# 4. Bat thuong: tuan + khoang trong
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(w.index, w['mean'], color=C1, lw=1, label='kWh/ngày theo tuần')
f = w[w.rz.abs() > 3]; ax.scatter(f.index, f['mean'], color=C2, zorder=3, s=22, label='Tuần bất thường (|z| > 3 so với mùa vụ tháng): %d' % len(f))
for i, g in gaps.iterrows():
    ax.axvspan(g.start, g.end, color='#f0b429', alpha=.6, lw=0, label='Khoảng trống dữ liệu ≥ 10 giờ (7 đợt)' if i == 0 else None)
ax.annotate('Tháng 8/2008: 4,4–8,6 kWh/ngày\n(nhà vắng)', (pd.Timestamp('2008-08-24'), 4.4), (pd.Timestamp('2008-11-15'), 3), arrowprops=dict(arrowstyle='-', color=C3))
ax.set_ylabel('kWh/ngày'); ax.legend(frameon=False, loc='upper right', fontsize=9)
ax.set_title('18/203 tuần bất thường, nhiều nhất ở tháng 8 và vài tuần thấp rải rác; 7 khoảng trống dữ liệu dài 0,6–5 ngày', fontsize=11.5, loc='left')
fig.tight_layout(); fig.savefig('04_bat_thuong.png', dpi=150); plt.close()

# 5. Backtest
b = bt.pivot(index='target', columns='model', values='pred')
fig, ax = plt.subplots(figsize=(11, 4.5))
act = bt[bt.model == 'seasonal_ratio'].set_index('target').actual
ax.plot(act.index, act, 'k-o', ms=3, label='Thực tế')
ax.plot(b.index, b.seasonal_ratio, color=C2, label='Mô hình chính (MAPE 6,3%)')
ax.plot(b.index, b.naive_seasonal, color=C3, ls='--', label='Cơ sở: lặp lại năm trước (MAPE 9,9%)')
ax.set_ylabel('kWh/ngày'); ax.legend(frameon=False)
ax.set_title('Kiểm định thời gian (dự báo trước 1 tháng, 2009–2010): mô hình chính sai số nhỏ hơn cơ sở', fontsize=11.5, loc='left')
fig.tight_layout(); fig.savefig('05_backtest.png', dpi=150); plt.close()
