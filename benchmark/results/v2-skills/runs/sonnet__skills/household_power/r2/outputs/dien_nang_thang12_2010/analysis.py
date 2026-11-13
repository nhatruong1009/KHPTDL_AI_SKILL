"""Phan tich xu huong / mua vu / bat thuong / du bao thang 12/2010. Chay sau prep.py (tao daily.csv, hourly.csv, gap_runs.csv)."""
import pandas as pd, numpy as np
from scipy import stats

d = pd.read_csv('daily.csv', index_col=0, parse_dates=True)
h = pd.read_csv('hourly.csv', index_col=0, parse_dates=True)

# ---------- 1. Thang: kWh uoc tinh theo do phu (kWh/phut quan sat * so phut cua thang) ----------
m = d.resample('MS').agg(kwh_obs=('kwh', 'sum'), n=('n', 'sum'))
m['days_in_month'] = m.index.days_in_month
m['cov_month'] = m.n / (m.days_in_month * 1440)
# thang dau/cuoi chi co du lieu mot phan: tinh toi so phut thuc te trong cua so du lieu
start, end = d.index.min(), pd.Timestamp('2010-11-26 21:02')
first_min = (pd.Timestamp('2006-12-16 17:24'))
m['kwh_per_obs_day'] = m.kwh_obs / (m.n / 1440)
m['kwh_est'] = m.kwh_per_obs_day * m.days_in_month
m['kwh_per_day'] = m.kwh_per_obs_day
m['full'] = (m.index > '2006-12-01') & (m.index < '2010-11-01')
m.to_csv('monthly.csv')
print(m.round(2).to_string())

full = m[m.full].copy()
# ---------- 2. Xu huong ----------
full['year'] = full.index.year
print('\nTB kWh/ngay theo nam lich (thang day du):')
print(full.groupby('year').kwh_per_day.agg(['mean', 'count']).round(2))
# 12 thang lien ke (Dec->Nov) so sanh cung ky
def span(a, b): return m.loc[a:b, 'kwh_obs'].sum() / (m.loc[a:b, 'n'].sum() / 1440)
for a, b in [('2007-01-01', '2007-11-01'), ('2008-01-01', '2008-11-01'), ('2009-01-01', '2009-11-01'), ('2010-01-01', '2010-11-01')]:
    print('Jan-Nov', a[:4], 'kWh/ngay:', round(span(a, b), 2))
t = np.arange(len(full))
lr = stats.linregress(t, full.kwh_per_day)
print('Hoi quy tuyen tinh kWh/ngay theo thang: slope/thang=%.3f p=%.3g' % (lr.slope, lr.pvalue))
# tuyen tinh sau khi loai mua vu (thang dummies)
X = np.column_stack([t, pd.get_dummies(full.index.month).values.astype(float)])
beta, *_ = np.linalg.lstsq(X, full.kwh_per_day.values, rcond=None)
res = full.kwh_per_day.values - X @ beta
print('Xu huong sau khi kiem soat mua vu: %.3f kWh/ngay moi thang (~%.2f/nam)' % (beta[0], beta[0] * 12))

# ---------- 3. Mua vu ----------
# nam: ty le so voi trung binh nam
full['ratio_year'] = full.kwh_per_day / full.groupby('year').kwh_per_day.transform('mean')
dec = d.copy(); dec['ok'] = dec.coverage >= 0.9
dd = dec[dec.ok].copy(); dd['kwh_day'] = dd.kwh
dd['dow'] = dd.index.dayofweek; dd['month'] = dd.index.month
mon_tab = full.assign(month=full.index.month).pivot_table(index='month', columns='year', values='kwh_per_day')
mon_tab['mean'] = mon_tab.mean(axis=1)
print('\nkWh/ngay theo thang x nam:\n', mon_tab.round(2).to_string())
mon_tab.to_csv('seasonal_month.csv')
dow = dd.groupby('dow').kwh_day.mean(); print('\nTheo thu (0=T2):\n', dow.round(2).to_string())
dow.to_csv('seasonal_dow.csv')
wk = dd.kwh_day[dd.dow >= 5].mean() / dd.kwh_day[dd.dow < 5].mean(); print('cuoi tuan / ngay thuong = %.3f' % wk)
f = stats.f_oneway(*[g.kwh_day.values for _, g in dd.groupby('dow')]); print('ANOVA thu: F=%.1f p=%.3g' % f)
# gio trong ngay
hh = h[h['count'] == 60].copy(); hh['hour'] = hh.index.hour; hh['we'] = hh.index.dayofweek >= 5
prof = hh.groupby(['we', 'hour'])['sum'].mean().unstack(0); prof.columns = ['ngay_thuong', 'cuoi_tuan']
print('\nProfile gio (kWh/gio):\n', prof.round(3).to_string()); prof.to_csv('seasonal_hour.csv')
print('Dinh gio:', prof.idxmax().to_dict(), ' day:', prof.idxmin().to_dict())
# do manh mua vu: phan phuong sai thang giai thich
print('Bien thien mua vu thang (max/min trung binh): %.2f' % (mon_tab['mean'].max() / mon_tab['mean'].min()))
print('Ty le Dec/TB nam:', full[full.index.month == 12].ratio_year.round(3).to_dict())

# ---------- 4. Bat thuong ----------
gaps = pd.read_csv('gap_runs.csv', parse_dates=['start', 'end'])
big = gaps[gaps.minutes >= 600].copy(); big['days'] = (big.minutes / 1440).round(2)
print('\nKhoang trong lon (>=10 gio):\n', big.to_string()); big.to_csv('data_gaps.csv', index=False)
print('Tong phut thieu %d = %.2f%%; trong do khoang >=10h: %d phut' % (gaps.minutes.sum(), gaps.minutes.sum() / (len(d) * 1440) * 100, big.minutes.sum()))
# tuan: dung ngay co do phu >=0.9, tuan can >=5 ngay hop le
w = dd.kwh_day.resample('W-SUN').agg(['mean', 'count']); w = w[w['count'] >= 5]
w['month'] = w.index.month
# bat thuong so voi gia tri thang-trong-nam (trung vi) va trung vi truot
w['seasonal'] = w.groupby('month')['mean'].transform('median')
w['resid'] = np.log(w['mean']) - np.log(w['seasonal'])
med = w.resid.median(); mad = 1.4826 * (w.resid - med).abs().median()
w['rz'] = (w.resid - med) / mad
w['flag'] = w.rz.abs() > 3
print('\nTuan bat thuong (|robust z|>3):', int(w.flag.sum()), '/', len(w))
print(w[w.flag].sort_values('rz').round(3).to_string())
w.to_csv('weekly.csv')
# ngay bat thuong
dd['seasonal'] = dd.groupby('month').kwh_day.transform('median')
r = dd.kwh_day - dd.seasonal; mm = r.median(); sg = 1.4826 * (r - mm).abs().median()
dd['rz'] = (r - mm) / sg
print('\nNgay |z|>3.5 cao nhat:'); print(dd[dd.rz > 3.5].sort_values('rz', ascending=False).head(8)[['kwh_day', 'rz']].round(2).to_string())
print('So ngay thap bat thuong (z<-3.5):', int((dd.rz < -3.5).sum()))
print(dd[dd.rz < -3.5].sort_values('rz').head(8)[['kwh_day', 'rz']].round(2).to_string())
low_dec = dd.loc['2006-12-16':'2010-11-26']
# tuan nghi he thang 8 & cuoi nam
print('\nTuan thap nhat:\n', w.sort_values('mean').head(8)[['mean', 'rz']].round(2).to_string())

# ---------- 5. Du bao thang 12/2010 ----------
y = full.kwh_per_day.copy()            # thang day du 2007-01..2010-10; (12/2006 va 11/2010 mot phan)
# them 2006-12 va 2010-11 (mot phan) vao chuoi lam thong tin tham khao
ally = m.kwh_per_day.copy()
print('\nThang 11/2010 (den 26/11): %.2f kWh/ngay, 12/2006 (tu 16/12): %.2f' % (ally['2010-11-01'], ally['2006-12-01']))
logy = np.log(ally)
months = ally.index

def fit_predict(train_idx_end, target, kind):
    """Du bao kWh/ngay cho `target` chi dung du lieu < target (thang >= origin)."""
    tr = ally[ally.index < target]
    ly = np.log(tr)
    if kind == 'naive_seasonal':
        return ally[target - pd.DateOffset(years=1)]
    if kind == 'seasonal_ratio':   # muc 12 thang gan nhat * chi so mua vu cua thang do (TB cac nam truoc)
        last12 = tr.iloc[-12:].mean()
        idx = []
        for yr in sorted(set(tr.index.year)):
            blk = tr[(tr.index >= pd.Timestamp(yr, 1, 1)) & (tr.index <= pd.Timestamp(yr, 12, 1))]
            if len(blk) == 12 and (pd.Timestamp(yr, target.month, 1) in blk.index):
                idx.append(blk[pd.Timestamp(yr, target.month, 1)] / blk.mean())
        return last12 * np.mean(idx) if idx else np.nan
    if kind == 'reg':   # log y = a + b t + dummy thang (ridge nhe) - xu huong tuyen tinh
        t = np.arange(len(tr)); tt = len(tr) + (target.to_period('M') - tr.index[-1].to_period('M')).n - 1
        D = lambda ms: np.eye(12)[np.array(ms) - 1]
        X = np.column_stack([t, D(tr.index.month)])
        lam = 0.1
        b = np.linalg.solve(X.T @ X + lam * np.eye(13), X.T @ ly.values)
        return float(np.exp(np.r_[tt, D([target.month])[0]] @ b))
    if kind == 'mean_last3y':
        s = tr[tr.index.month == target.month].iloc[-3:]
        return s.mean()

kinds = ['naive_seasonal', 'seasonal_ratio', 'reg', 'mean_last3y']
bt_targets = [t for t in ally.index if t >= pd.Timestamp('2009-01-01') and t <= pd.Timestamp('2010-10-01')]
rows = []
for k in kinds:
    for t in bt_targets:
        # du bao 1 buoc: chi du lieu truoc thang t (bo thang phia truoc 1 thang de co chu ky tuong tu dec)
        p = fit_predict(None, t, k)
        rows.append(dict(model=k, target=t, pred=p, actual=ally[t]))
bt = pd.DataFrame(rows); bt['err'] = bt.pred - bt.actual; bt['pe'] = bt.err / bt.actual; bt['lerr'] = np.log(bt.pred / bt.actual)
sm = bt.groupby('model').agg(MAE=('err', lambda x: x.abs().mean()), MAPE=('pe', lambda x: x.abs().mean() * 100), bias=('pe', lambda x: x.mean() * 100), sd_log=('lerr', 'std'), n=('err', 'size'))
print('\nBacktest 1 buoc (2009-01..2010-10, kWh/ngay):\n', sm.round(3).to_string())
sm.to_csv('backtest_summary.csv'); bt.to_csv('backtest_detail.csv', index=False)
# rieng cac thang 12 / 11 / 1 de xem do on dinh
print(bt[bt.target.dt.month.isin([12, 1])].round(2).to_string())

T = pd.Timestamp('2010-12-01')
preds = {k: fit_predict(None, T, k) for k in kinds}
print('\nDu bao kWh/ngay thang 12/2010:', {k: round(v, 3) for k, v in preds.items()})
print('x31 ngay:', {k: round(v * 31, 1) for k, v in preds.items()})
# Thang 12 qua cac nam
print('Thang 12 thuc te (kWh/ngay):', {str(i.year): round(v, 3) for i, v in ally[ally.index.month == 12].items()})
print('Thang 12 thuc te (kWh/thang, uoc tinh):', {str(i.year): round(v, 1) for i, v in m.kwh_est[m.index.month == 12].items()})
# ensemble: trung binh seasonal_ratio va reg va mean_last3y? chon dua tren backtest
best = sm.MAE.idxmin(); print('Mo hinh MAE thap nhat:', best)
preds_df = pd.Series(preds); preds_df.to_csv('forecast_models.csv')
