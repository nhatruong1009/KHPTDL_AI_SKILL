"""Phân tích điện năng hộ gia đình 12/2006-11/2010 và dự báo tháng 12/2010.
Chạy từ thư mục gốc: python -I outputs/dien_nang_xu_huong/analysis.py
Đơn vị: kWh = Global_active_power (kW) / 60 cho mỗi phút."""
import os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = 'outputs/dien_nang_xu_huong'
df = pd.read_csv('data/household_power_consumption.txt', sep=';', na_values='?', low_memory=False)
df['ts'] = pd.to_datetime(df.Date + ' ' + df.Time, format='%d/%m/%Y %H:%M:%S')
df = df.set_index('ts').sort_index()
df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq='min'))
k = df.Global_active_power / 60.0          # kWh mỗi phút
obs = k.notna()

# ---------------- 1. Khoảng trống dữ liệu ----------------
m = ~obs
gid = (m != m.shift()).cumsum().values
gaps = pd.DataFrame(dict(start=m.index.to_series().groupby(gid).first(),
                         end=m.index.to_series().groupby(gid).last(),
                         minutes=m.groupby(gid).size(), miss=m.groupby(gid).first()))
gaps = gaps[gaps.miss].drop(columns='miss').sort_values('minutes', ascending=False)
gaps['days'] = (gaps.minutes / 1440).round(2)
gaps[gaps.minutes >= 60].to_csv(f'{OUT}/khoang_trong_du_lieu.csv', index=False)
print('Tổng phút thiếu', m.sum(), f'({m.mean():.2%}); số khoảng >=60 phút:', (gaps.minutes >= 60).sum())
print(gaps[gaps.minutes >= 60].head(10).to_string())

# ---------------- 2. Chuỗi tháng/ngày/tuần (hiệu chỉnh theo độ phủ) ----------------
# tổng hiệu chỉnh = trung bình kWh/phút quan sát * số phút của kỳ (giả định phút thiếu giống phút có dữ liệu)
mo = pd.DataFrame(dict(cov=obs.resample('MS').mean(), mean_min=k.resample('MS').mean(),
                       obs_kwh=k.resample('MS').sum()))
mo['adj_kwh'] = mo.mean_min * mo.index.days_in_month * 1440
mo = mo.drop(index=pd.Timestamp('2006-12-01'))     # tháng 12/2006 chỉ có từ 16/12
mo['adj_kwh_per_day'] = mo.adj_kwh / mo.index.days_in_month
mo.drop(columns='mean_min').round(3).to_csv(f'{OUT}/tong_thang.csv')

# Xu hướng theo năm: so sánh cùng 11 tháng (T1-T11)
mo['year'] = mo.index.year; mo['month'] = mo.index.month
j11 = mo[mo.month <= 11].groupby('year').adj_kwh.sum()
j11 = j11.drop(2006, errors='ignore')
tr = pd.DataFrame(dict(T1_T11_kWh=j11, thay_doi_pct=j11.pct_change() * 100))
print(tr.round(1))
tr.round(2).to_csv(f'{OUT}/xu_huong_nam.csv')
r12 = mo.adj_kwh.rolling(12).sum()
print('Tổng 12 tháng gần nhất (12/2009-11/2010):', r12.iloc[-1].round(0), ' 12 tháng trước đó:', r12.iloc[-13].round(0),
      ' 12 tháng 12/2007-11/2008:', r12.loc['2008-11-01'].round(0))
# tuyến tính: độ dốc của chuỗi đã khử mùa (tỷ lệ với trung bình cùng tháng)
mm = mo[(mo.index >= '2007-01-01')].copy()
mm['idx'] = mm.adj_kwh / mm.groupby('month').adj_kwh.transform('mean')
x = np.arange(len(mm)); sl = np.polyfit(x, mm.idx, 1)[0]
print(f'Độ dốc chỉ số khử mùa: {sl*12*100:.1f} điểm % / năm')

# ---------------- 3. Mùa vụ ----------------
# năm: chỉ số tháng, dùng 3 năm đầy đủ 2007-2009 (tránh Aug-2008 bất thường bằng trung vị)
full = mo[(mo.year >= 2007) & (mo.year <= 2009)].copy()
full['ratio'] = full.adj_kwh / full.groupby('year').adj_kwh.transform('mean')
mi = full.pivot(index='month', columns='year', values='ratio')
mi['trung_vi'] = mi.median(axis=1)
mi.round(3).to_csv(f'{OUT}/chi_so_mua_thang.csv')
print(mi.round(2))
# tuần (thứ trong tuần) và ngày (giờ)
daily = k.resample('D').sum(min_count=1)
dcov = obs.resample('D').mean()
dd = daily[dcov >= 0.95]
dow = dd.groupby(dd.index.dayofweek).mean()
dow_idx = dow / dow.mean()
names = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
print(pd.DataFrame(dict(kWh_ngay=dow.values.round(2), chi_so=dow_idx.values.round(3)), index=names))
pd.DataFrame(dict(kWh_ngay=dow.values, chi_so=dow_idx.values), index=names).to_csv(f'{OUT}/mua_vu_thu.csv')
from scipy import stats
groups = [dd[dd.index.dayofweek == i].values for i in range(7)]
# kiểm định khử mùa năm: chia cho trung bình tháng
dm = dd / dd.groupby([dd.index.year, dd.index.month]).transform('mean')
print('Kruskal thứ (chỉ số trong tháng):', stats.kruskal(*[dm[dm.index.dayofweek == i].values for i in range(7)]))
dow_adj = dm.groupby(dm.index.dayofweek).mean()
print('Chỉ số thứ đã khử mùa tháng:', dow_adj.round(3).tolist())
hr = pd.DataFrame(dict(kw=k.groupby([k.index.dayofweek >= 5, k.index.hour]).mean() * 60)).unstack(0)
hr.columns = ['ngay_thuong', 'cuoi_tuan']
hr.round(3).to_csv(f'{OUT}/mua_vu_gio.csv')
print(hr.round(2).T.to_string())
# mùa hè/đông
season = mo.groupby('month').adj_kwh.median()

# ---------------- 4. Tuần bất thường ----------------
wk = pd.DataFrame(dict(cov=obs.resample('W-SUN').mean(), mean_min=k.resample('W-SUN').mean()))
wk['adj_kwh'] = wk.mean_min * 7 * 1440
wk = wk.loc['2007-01-01':'2010-11-21']             # tuần đầy đủ, bỏ tuần đầu và cuối thiếu
wk['good'] = wk['cov'] >= 0.9
# đường cơ sở: trung vị trượt 9 tuần ở tâm trên các tuần đủ dữ liệu
base = wk.adj_kwh.where(wk.good).rolling(9, center=True, min_periods=5).median()
res = np.log(wk.adj_kwh.where(wk.good) / base)
mad = (res - res.median()).abs().median() * 1.4826
wk['baseline'] = base; wk['z'] = (res - res.median()) / mad
wk['flag'] = np.where(~wk.good, 'thiếu dữ liệu (<90% phút)',
                      np.where(wk.z.abs() > 3, np.where(wk.z < 0, 'thấp bất thường', 'cao bất thường'), ''))
wk.round(3).to_csv(f'{OUT}/tuan_bat_thuong.csv')
an = wk[wk.flag != '']
print('MAD-sigma log:', round(mad, 3))
print(an[['cov', 'adj_kwh', 'baseline', 'z', 'flag']].round(2).to_string())

# ---------------- 5. Dự báo tháng 12/2010 ----------------
ma = mo.adj_kwh.copy()
ma.index = ma.index.to_period('M')
def f_sn(t):            # cùng tháng năm trước
    return ma[t - 12]
def f_yoy(t):           # cùng tháng năm trước * tỷ lệ 12 tháng liền trước / 12 tháng trước đó nữa
    return ma[t - 12] * ma[t - 12:t - 1 + 0].sum() / ma[t - 24:t - 12].sum() if False else \
        ma[t - 12] * ma[t - 12:t].sum() / ma[t - 24:t - 12].sum()
def f_ratio(t):         # tỷ lệ (tháng t / 2 tháng trước đó) ở các năm trước * 2 tháng gần nhất
    rs = []
    for y in range(1, 4):
        a = t - 12 * y
        if a - 2 >= ma.index[0]:
            rs.append(np.log(ma[a] / ma[a - 2:a].mean()))
    return np.exp(np.mean(rs)) * ma[t - 2:t].mean() if rs else np.nan
methods = dict(seasonal_naive=f_sn, yoy_scaled=f_yoy, ratio_2m=f_ratio)
covm = mo['cov']; covm.index = covm.index.to_period('M')
rows = []
for t in pd.period_range('2009-01', '2010-11', freq='M'):
    for n, f in methods.items():
        try:
            p = f(t)
        except Exception:
            p = np.nan
        rows.append(dict(month=str(t), method=n, forecast=p, actual=ma[t], cov=covm[t]))
bt = pd.DataFrame(rows); bt['logerr'] = np.log(bt.actual / bt.forecast)
bt['ape'] = (bt.forecast - bt.actual).abs() / bt.actual * 100
bt.round(3).to_csv(f'{OUT}/backtest.csv', index=False)
# chỉ đánh giá trên tháng đủ dữ liệu (>=95%), loại 8/2009 do tham chiếu 8/2008 bất thường nằm trong lịch sử
ok = bt[(bt['cov'] >= 0.95) & bt.forecast.notna()]
summ = ok.groupby('method').agg(n=('ape', 'size'), MAPE=('ape', 'mean'), medAPE=('ape', 'median'),
                                bias_log=('logerr', 'mean'), sd_log=('logerr', 'std'))
print(summ.round(3))
summ.round(3).to_csv(f'{OUT}/backtest_tom_tat.csv')

T = pd.Period('2010-12', 'M')
ma_f = ma.copy()
fc = {n: f(T) if n != 'x' else np.nan for n, f in methods.items()}
# f dùng ma[t-1..] nên cần chuỗi đến 11/2010: đã có
print('Dự báo 12/2010 từng phương pháp:', {n: round(v, 0) for n, v in fc.items()})
# Nov-2010 đã hiệu chỉnh (26/11) - dùng giá trị hiệu chỉnh; chạy nhạy cảm: bỏ T11 (dùng 10/2010 làm mốc)
best = summ.MAPE.idxmin()
print('Phương pháp tốt nhất theo MAPE:', best)
# nhạy cảm: Dec 2007-2009 thực tế
dec = ma[[pd.Period(f'{y}-12', 'M') for y in (2007, 2008, 2009)]]
print('Tháng 12 các năm:', dec.round(0).to_dict())
# Khoảng bất định: sai số log thực nghiệm của backtest (tất cả tháng) cho phương pháp chọn, phân vị 10-90 & 5-95 qua bootstrap
e = ok[ok.method == best].logerr.values
rng = np.random.default_rng(0)
point = fc[best]
# actual = forecast * exp(logerr) -> mô phỏng
sim = point * np.exp(rng.choice(e - e.mean() * 0, 20000))
lo80, hi80 = np.percentile(sim, [10, 90]); lo95, hi95 = np.percentile(sim, [2.5, 97.5])
# khoảng chuẩn theo sd (bền hơn khi n nhỏ)
sd = e.std(ddof=1)
n95 = (point * np.exp(e.mean() - 1.96 * sd), point * np.exp(e.mean() + 1.96 * sd))
n80 = (point * np.exp(e.mean() - 1.2816 * sd), point * np.exp(e.mean() + 1.2816 * sd))
print('Điểm', round(point), 'sd_log', round(sd, 3), 'bias', round(e.mean(), 3))
print('80% (chuẩn):', np.round(n80), ' 95% (chuẩn):', np.round(n95))
print('80% (bootstrap):', np.round([lo80, hi80]), '95%:', np.round([lo95, hi95]))
# trung bình các phương pháp
ens = np.mean(list(fc.values()))
print('Trung bình 3 phương pháp:', round(ens))
pd.DataFrame(dict(method=list(fc), forecast_kwh=list(fc.values()))).round(1).to_csv(f'{OUT}/du_bao_thang12_2010.csv', index=False)
pd.DataFrame(dict(diem=[point], lo80=[n80[0]], hi80=[n80[1]], lo95=[n95[0]], hi95=[n95[1]], phuong_phap=[best])).round(1)\
    .to_csv(f'{OUT}/du_bao_khoang.csv', index=False)

# ---------------- 6. Biểu đồ ----------------
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
C0, C1, C2 = '#1f4e79', '#d95f02', '#7f7f7f'

# (a) xu hướng + dự báo
fig, ax = plt.subplots(figsize=(11, 4.8))
x = mo.index
ax.plot(x, mo.adj_kwh, color=C0, marker='o', ms=3, label='Tổng kWh/tháng (đã hiệu chỉnh theo độ phủ)')
low = mo[mo['cov'] < 0.95]
ax.scatter(low.index, low.adj_kwh, color=C1, zorder=5, s=35, label='Tháng thiếu >5% dữ liệu')
ax.axvspan(pd.Timestamp('2008-08-01'), pd.Timestamp('2008-08-31'), color='#fdd', alpha=.6)
ax.annotate('8/2008: ~206 kWh\n(gần như không dùng điện)', (pd.Timestamp('2008-08-15'), 210), xytext=(pd.Timestamp('2008-10-10'), 330),
            arrowprops=dict(arrowstyle='->', color=C2), fontsize=9)
ft = pd.Timestamp('2010-12-01')
ax.errorbar([ft], [point], yerr=[[point - n95[0]], [n95[1] - point]], fmt='D', color=C1, capsize=5, label='Dự báo 12/2010 (khoảng 95%)')
ax.errorbar([ft], [point], yerr=[[point - n80[0]], [n80[1] - point]], fmt='none', color=C1, lw=4, alpha=.5)
ax.set_ylabel('kWh / tháng'); ax.set_ylim(0)
ax.set_title('Điện năng theo mùa rõ rệt (đông cao, hè thấp) và giảm nhẹ qua các năm; dự báo 12/2010 ≈ %d kWh' % round(point), loc='left', fontsize=11)
ax.legend(loc='lower right', fontsize=8, frameon=False)
fig.tight_layout(); fig.savefig(f'{OUT}/01_xu_huong_va_du_bao.png', dpi=140); plt.close()

# (b) mùa vụ năm theo các năm
fig, ax = plt.subplots(figsize=(8, 4.5))
for y, c in zip([2007, 2008, 2009, 2010], ['#9ecae1', '#6baed6', '#2171b5', C1]):
    s = mo[mo.year == y]
    ax.plot(s.month, s.adj_kwh, marker='o', ms=3, color=c, label=str(y))
ax.set_xticks(range(1, 13)); ax.set_xlabel('Tháng'); ax.set_ylabel('kWh / tháng'); ax.set_ylim(0)
ax.set_title('Mùa vụ năm: tháng 7-8 thấp nhất, tháng 12-1 cao nhất', loc='left', fontsize=11)
ax.legend(frameon=False, ncol=4)
fig.tight_layout(); fig.savefig(f'{OUT}/02_mua_vu_nam.png', dpi=140); plt.close()

# (c) ngày & tuần
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
axs[0].plot(hr.index, hr.ngay_thuong, color=C0, label='Ngày thường')
axs[0].plot(hr.index, hr.cuoi_tuan, color=C1, label='Cuối tuần')
axs[0].set_xlabel('Giờ trong ngày'); axs[0].set_ylabel('Công suất TB (kW)'); axs[0].legend(frameon=False)
axs[0].set_title('Đỉnh buổi tối 19-21h; cuối tuần dùng nhiều ban ngày', loc='left', fontsize=10)
axs[1].bar(names, dow_idx.values, color=[C0] * 5 + [C1] * 2)
axs[1].axhline(1, color=C2, lw=1); axs[1].set_ylim(.8, 1.15); axs[1].set_ylabel('Chỉ số so với TB ngày')
axs[1].set_title('Thứ 7 - CN cao hơn ~%d%% so với thứ 2-6' % round((dow_idx.values[5:].mean() / dow_idx.values[:5].mean() - 1) * 100), loc='left', fontsize=10)
fig.tight_layout(); fig.savefig(f'{OUT}/03_mua_vu_ngay_tuan.png', dpi=140); plt.close()

# (d) tuần bất thường
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(wk.index, wk.adj_kwh.where(wk.good), color=C0, lw=1, label='kWh/tuần')
ax.plot(wk.index, wk.baseline, color=C2, lw=1, ls='--', label='Đường cơ sở (trung vị trượt 9 tuần)')
lo_ = wk[wk.flag == 'thấp bất thường']; hi_ = wk[wk.flag == 'cao bất thường']
ax.scatter(lo_.index, lo_.adj_kwh, color=C1, zorder=5, label='Tuần thấp bất thường (|z|>3)')
ax.scatter(hi_.index, hi_.adj_kwh, color='#e7298a', zorder=5, label='Tuần cao bất thường')
for _, g in gaps[gaps.minutes >= 1000].iterrows():
    ax.axvspan(g.start, g.end, color='#bbb', alpha=.5)
ax.axvspan(pd.Timestamp('2010-01-01'), pd.Timestamp('2010-01-01'), color='#bbb', alpha=.5, label='Khoảng trống dữ liệu (≥17 giờ)')
ax.set_ylabel('kWh / tuần'); ax.set_ylim(0)
ax.set_title('Tuần bất thường: kỳ nghỉ 8/2008 và các khoảng trống dữ liệu', loc='left', fontsize=11)
ax.legend(frameon=False, fontsize=8, loc='upper right', ncol=2)
fig.tight_layout(); fig.savefig(f'{OUT}/04_tuan_bat_thuong.png', dpi=140); plt.close()

# (e) backtest
fig, ax = plt.subplots(figsize=(8, 4.2))
b = ok[ok.method == best]
ax.plot(pd.PeriodIndex(b.month, freq='M').to_timestamp(), b.actual, color=C0, marker='o', ms=3, label='Thực tế')
ax.plot(pd.PeriodIndex(b.month, freq='M').to_timestamp(), b.forecast, color=C1, marker='x', label=f'Dự báo lùi ({best})')
ax.set_ylim(0); ax.set_ylabel('kWh / tháng'); ax.legend(frameon=False)
ax.set_title('Kiểm tra lùi 2009-2010: sai số trung bình %.0f%% (MAPE)' % summ.loc[best, 'MAPE'], loc='left', fontsize=11)
fig.tight_layout(); fig.savefig(f'{OUT}/05_backtest.png', dpi=140); plt.close()
