"""Phân tích điện năng hộ gia đình 12/2006-11/2010 + dự báo tháng 12/2010.
Chạy: python -I outputs/dien_nang/prep.py && python -I outputs/dien_nang/analysis.py
kWh = Global_active_power (kW, trung bình mỗi phút) / 60."""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

O = 'outputs/dien_nang/'
plt.rcParams.update({'figure.dpi': 110, 'axes.spines.top': False, 'axes.spines.right': False,
                     'font.size': 10})
C1, C2, CR = '#2a6f97', '#9aa5b1', '#c8553d'
m = pd.read_pickle(O + 'minute.pkl')
kwh = m.kwh
MON = ['T1','T2','T3','T4','T5','T6','T7','T8','T9','T10','T11','T12']

# ---------- 1. Tháng: kWh/ngày quan sát (hiệu chỉnh theo độ phủ dữ liệu) ----------
g = kwh.resample('MS')
mo = pd.DataFrame({'kwh_quan_sat': g.sum(), 'phut_co_du_lieu': g.count(), 'phut_lich': g.size()})
mo['do_phu'] = mo.phut_co_du_lieu / mo.phut_lich
mo['kwh_ngay'] = mo.kwh_quan_sat / (mo.phut_co_du_lieu / 1440)
mo['kwh_thang_hieu_chinh'] = mo.kwh_ngay * (mo.phut_lich / 1440)
mo.round(3).to_csv(O + 'thang.csv')

# Xu hướng: 12 tháng liên tiếp (T12-T11) đầy đủ, không tính T12/2006 (chỉ có từ 16/12) và tháng 8/2008 bất thường
yr = {}
for y in [2007, 2008, 2009, 2010]:
    s = mo.loc[f'{y-1}-12-01':f'{y}-11-01'] if y > 2007 else mo.loc['2007-01-01':'2007-11-01']
    yr[f'{y-1}-12 → {y}-11' if y > 2007 else '2007-01 → 2007-11 (11 tháng)'] = s.kwh_ngay.mean()
yrdf = pd.Series(yr, name='kwh_ngay_trung_binh')
yrdf.round(2).to_csv(O + 'nam_kwh_ngay.csv')
print(yrdf.round(2))
# Cùng kỳ T1-T11 từng năm (loại 8/2008)
same = {}
for y in [2007, 2008, 2009, 2010]:
    s = mo.loc[f'{y}-01-01':f'{y}-11-01'].kwh_ngay
    s = s[~((s.index.year == 2008) & (s.index.month == 8))]
    same[y] = s.mean()
same = pd.Series(same); print('T1-T11 (bỏ T8/2008):\n', same.round(2))
same.round(3).to_csv(O + 'cungky_T1_T11.csv', header=['kwh_ngay'])
# xu hướng tuyến tính trên chuỗi đã khử mùa vụ (log, trừ hiệu ứng tháng)
t = mo.loc['2007-01-01':'2010-11-01'].copy()
t = t[~((t.index.year == 2008) & (t.index.month == 8))]
t['ln'] = np.log(t.kwh_ngay)
t['seas'] = t.groupby(t.index.month).ln.transform('mean')
t['ds'] = t.ln - t.seas
tt = np.arange(len(t)); idx_years = (t.index.year - 2007) + (t.index.month - 1) / 12
lr = stats.linregress(idx_years, t.ds)
print(f'Xu hướng: {np.expm1(lr.slope)*100:.1f}%/năm, p={lr.pvalue:.4f}, SE slope={lr.stderr:.3f}')
pd.Series({'pct_moi_nam': np.expm1(lr.slope)*100, 'p': lr.pvalue, 'slope_ln': lr.slope, 'se': lr.stderr}).to_csv(O + 'xu_huong.csv')

# ---------- 2. Mùa vụ ----------
h = m.Global_active_power
hod = h.groupby([h.index.hour]).mean()
we = h.index.dayofweek >= 5
hod_wd = h[~we].groupby(h[~we].index.hour).mean(); hod_we = h[we].groupby(h[we].index.hour).mean()
dow = kwh.resample('D').agg(['sum', 'count']); dow = dow[dow['count'] >= 1380]  # ngày gần đủ dữ liệu
dow['dow'] = dow.index.dayofweek
dow_m = dow.groupby('dow')['sum'].mean()
dow_m.index = ['T2','T3','T4','T5','T6','T7','CN']
dow_m.round(2).to_csv(O + 'thu_trong_tuan.csv', header=['kwh_ngay'])
hourly = pd.DataFrame({'ca_tuan_kW': hod, 'ngay_thuong_kW': hod_wd, 'cuoi_tuan_kW': hod_we}).round(3)
hourly.to_csv(O + 'theo_gio.csv')
print(hourly.round(2).T.to_string()); print(dow_m.round(2))
# kiểm định khác biệt cuối tuần vs ngày thường (ngày đủ dữ liệu)
d_we = dow[dow.dow >= 5]['sum']; d_wd = dow[dow.dow < 5]['sum']
mw = stats.mannwhitneyu(d_we, d_wd)
print(f'Cuối tuần {d_we.mean():.2f} vs ngày thường {d_wd.mean():.2f} kWh/ngày; MWU p={mw.pvalue:.2e}; n={len(d_we)},{len(d_wd)}')
# mùa vụ năm: chỉ số mùa theo tháng (tỉ lệ so với trung bình năm, bỏ T8/2008, T12/2006)
tm = t.copy(); tm['month'] = tm.index.month
# chuẩn hoá mỗi năm theo trung bình năm có đủ để tránh trend
seas_idx = np.exp(tm.groupby('month').ln.mean() - tm.groupby('month').ln.mean().mean())
seas_idx.round(3).to_csv(O + 'chi_so_mua.csv', header=['chi_so'])
print(seas_idx.round(2).to_dict())

fig, ax = plt.subplots(1, 3, figsize=(15, 4.2), gridspec_kw={'width_ratios': [1.2, 1, 1]})
ax[0].plot(hod_wd.index, hod_wd, color=C1, lw=2, label='Ngày thường')
ax[0].plot(hod_we.index, hod_we, color=CR, lw=2, label='Cuối tuần')
ax[0].set(title='Theo giờ: đỉnh sáng và đỉnh tối', xlabel='Giờ trong ngày', ylabel='Công suất TB (kW)'); ax[0].legend(frameon=False)
cols = [CR if i >= 5 else C1 for i in range(7)]
ax[1].bar(dow_m.index, dow_m.values, color=cols); ax[1].set(title='Theo thứ: cuối tuần dùng nhiều hơn', ylabel='kWh/ngày')
ax[1].set_ylim(dow_m.min() * 0.8, dow_m.max() * 1.05)
ax[2].bar(MON, seas_idx.values, color=[CR if v > 1 else C1 for v in seas_idx.values])
ax[2].axhline(1, color='k', lw=.8); ax[2].set(title='Theo tháng: cao mùa đông, thấp mùa hè', ylabel='Chỉ số mùa (1 = TB năm)')
fig.suptitle('Tính mùa vụ theo ngày, tuần và năm', fontweight='bold'); fig.tight_layout()
fig.savefig(O + 'mua_vu.png'); plt.close(fig)

# ---------- 3. Tuần bất thường & khoảng trống ----------
w = kwh.resample('W-SUN').agg(['sum', 'count'])
w['phu'] = w['count'] / 10080
w = w[w.phu > 0]
w['kwh_ngay'] = w['sum'] / (w['count'] / 1440)
w['ln'] = np.log(w.kwh_ngay)
# kỳ vọng = trung vị tuần cùng thời điểm trong năm (±3 tuần) của các năm khác, nhân hệ số mức năm
w['woy'] = w.index.isocalendar().week.astype(int); w['yr'] = w.index.year
def expected(r):
    pool = w[(w.yr != r.yr) & ((w.woy - r.woy).abs() <= 2) & (w.phu > .9)]
    return np.log(pool.kwh_ngay.median()) if len(pool) else np.nan
w['ln_exp'] = w.apply(expected, axis=1)
w['res'] = w.ln - w.ln_exp
good = w.phu > .9
med = w.res[good].median(); mad = (w.res[good] - med).abs().median() * 1.4826
w['z'] = (w.res - med) / mad
w['co_khoang_trong'] = w.phu < .9
w['bat_thuong'] = (w.z.abs() > 3) & ~w.co_khoang_trong
out = w[['sum','count','phu','kwh_ngay','ln_exp','z','co_khoang_trong','bat_thuong']].copy()
out['kwh_ngay_ky_vong'] = np.exp(out.ln_exp)
out.round(3).drop(columns='ln_exp').to_csv(O + 'tuan.csv')
an = out[out.bat_thuong | out.co_khoang_trong]
print(an.round(2).to_string())
an.round(3).drop(columns='ln_exp').to_csv(O + 'tuan_bat_thuong.csv')

# biểu đồ xu hướng + bất thường
fig, ax = plt.subplots(2, 1, figsize=(13, 7.5), gridspec_kw={'height_ratios': [1.1, 1]})
a = ax[0]
a.plot(w.index, w.kwh_ngay, color=C2, lw=1, label='Trung bình theo tuần (kWh/ngày)')
a.plot(mo.index + pd.Timedelta(days=14), mo.kwh_ngay, color=C1, lw=2.2, marker='o', ms=3, label='Trung bình theo tháng')
bt = w[w.bat_thuong]; a.scatter(bt.index, bt.kwh_ngay, color=CR, zorder=5, s=28, label='Tuần bất thường (|z|>3)')
for s_, e_, n_ in pd.read_csv(O + 'gaps.csv', parse_dates=['start', 'end']).query('minutes>=1440').itertuples(index=False):
    a.axvspan(s_, e_, color='#f2c14e', alpha=.6, lw=0)
a.axvspan(pd.NaT, pd.NaT) if False else None
a.plot([], [], color='#f2c14e', lw=8, alpha=.6, label='Khoảng trống ≥ 1 ngày')
a.set(title='Điện năng tiêu thụ giảm nhẹ theo năm, lặp mùa vụ rõ; T8/2008 thấp bất thường', ylabel='kWh/ngày'); a.legend(frameon=False, ncol=2, loc='upper right')
a.annotate('T8/2008: ~6,6 kWh/ngày\n(nghi vắng nhà)', xy=(pd.Timestamp('2008-08-10'), 6.6), xytext=(pd.Timestamp('2008-10-20'), 4), arrowprops=dict(arrowstyle='->'), fontsize=9)
a.set_ylim(0, None)
b = ax[1]
piv = mo.loc['2007-01-01':'2010-11-01'].copy(); piv['y'] = piv.index.year; piv['mth'] = piv.index.month
for y, c in zip([2007, 2008, 2009, 2010], ['#9aa5b1', '#6f9fc0', '#2a6f97', CR]):
    s = piv[piv.y == y]; b.plot(s.mth, s.kwh_ngay, marker='o', ms=3, color=c, lw=2 if y == 2010 else 1.5, label=str(y))
b.set_xticks(range(1, 13)); b.set_xticklabels(MON); b.set(ylabel='kWh/ngày', title='Đường mùa vụ theo năm (T12 chưa có dữ liệu 2010)'); b.legend(frameon=False, ncol=4)
fig.tight_layout(); fig.savefig(O + 'xu_huong_bat_thuong.png'); plt.close(fig)

# ---------- 4. Dự báo T12/2010 ----------
# Mô hình: kWh/ngày(T, năm y) = trung vị kWh/ngày cùng tháng các năm trước × hệ số mức
# hệ số mức = TB (log) kWh/ngày 12 tháng gần nhất / TB 12 tháng cùng kỳ năm trước (bỏ T8/2008 & tháng thiếu >10%)
M = mo.copy(); M = M[M.index >= '2007-01-01']
M.loc['2008-08-01', 'kwh_ngay'] = np.nan  # bất thường, không dùng làm tham chiếu
M.loc[M.do_phu < .9, 'kwh_ngay'] = np.nan
L = np.log(M.kwh_ngay)
def forecast(target, method):
    prev = [target - pd.DateOffset(years=k) for k in (1, 2, 3)]
    prev = [p for p in prev if p in L.index and not np.isnan(L[p])]
    if not prev: return np.nan
    if method == 'naive':
        return np.exp(L[prev[0]])
    if method == 'seasonal_mean':
        return np.exp(np.mean([L[p] for p in prev]))
    # 'mean_adj': trung bình cùng tháng các năm trước điều chỉnh theo mức 12 tháng gần nhất
    win = [target - pd.DateOffset(months=k) for k in range(1, 13)]
    ratios = []
    for p in prev:
        ref = [x - (target - p) for x in win]
        pairs = [(L[a_], L[b_]) for a_, b_ in zip(win, ref) if a_ in L.index and b_ in L.index and not np.isnan(L[a_]) and not np.isnan(L[b_])]
        if len(pairs) >= 8:
            ratios.append(np.mean([a_ - b_ for a_, b_ in pairs]) + L[p])
    return np.exp(np.mean(ratios)) if ratios else np.nan
targets = [d for d in M.index if d >= pd.Timestamp('2008-01-01')]
bt_rows = []
for d in targets:
    if np.isnan(L[d]): continue
    row = {'thang': d, 'thuc_te': np.exp(L[d])}
    for me in ['naive', 'seasonal_mean', 'mean_adj']:
        row[me] = forecast(d, me)
    bt_rows.append(row)
bt = pd.DataFrame(bt_rows).set_index('thang')
res = {}
for me in ['naive', 'seasonal_mean', 'mean_adj']:
    e = np.log(bt.thuc_te / bt[me]).dropna()
    res[me] = {'n': len(e), 'MAPE_%': (np.abs(np.expm1(e))).mean() * 100, 'sd_log': e.std(), 'bias_log': e.mean()}
res = pd.DataFrame(res).T; print(res.round(3)); res.round(4).to_csv(O + 'backtest_tom_tat.csv')
bt.round(2).to_csv(O + 'backtest_chi_tiet.csv')
best = res.MAPE_.idxmin() if False else res['MAPE_%'].idxmin()
print('Mô hình chọn:', best)

tgt = pd.Timestamp('2010-12-01')
# bổ sung dữ liệu: T11/2010 chỉ đến 26/11 (đã dùng kwh_ngay nên vẫn hợp lệ)
M.loc[tgt] = np.nan; L = np.log(M.kwh_ngay)
pt = forecast(tgt, best)
e = np.log(bt.thuc_te / bt[best]).dropna()
sd = e.std(ddof=1)
# khoảng 80% và 95% dựa phân bố sai số log của backtest (t-student, n-1 bậc tự do), thêm bias
q80, q95 = stats.t.ppf(.90, len(e) - 1), stats.t.ppf(.975, len(e) - 1)
days = 31
tot = pt * days
rows = {'diem': tot,
        'lo80': tot * np.exp(-q80 * sd), 'hi80': tot * np.exp(q80 * sd),
        'lo95': tot * np.exp(-q95 * sd), 'hi95': tot * np.exp(q95 * sd)}
# phương pháp đối chiếu
alt = {me: forecast(tgt, me) * days for me in ['naive', 'seasonal_mean', 'mean_adj']}
# ngoại suy tối giản: T12 = T11/2010 × tỉ lệ T12/T11 cùng các năm trước
r = [M.kwh_ngay[pd.Timestamp(f'{y}-12-01')] / M.kwh_ngay[pd.Timestamp(f'{y}-11-01')] for y in (2007, 2008, 2009)]
alt['T11_x_ti_le_T12/T11'] = M.kwh_ngay[pd.Timestamp('2010-11-01')] * np.mean(r) * days
print('Dự báo T12/2010 (kWh):', {k: round(v, 1) for k, v in rows.items()}); print('Đối chiếu:', {k: round(v, 1) for k, v in alt.items()})
print('tỉ lệ T12/T11 2007-09:', np.round(r, 3))
pd.concat([pd.Series(rows, name='kWh'), ]).round(1).to_csv(O + 'du_bao_T12_2010.csv', header=['kWh'])
pd.Series(alt, name='kWh').round(1).to_csv(O + 'du_bao_doi_chieu.csv', header=['kWh'])

hist = mo.loc['2007-01-01':'2010-11-01'].kwh_thang_hieu_chinh
dec = {y: mo.loc[f'{y}-12-01', 'kwh_thang_hieu_chinh'] for y in (2007, 2008, 2009)}
fig, ax = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw={'width_ratios': [2.2, 1]})
a = ax[0]
a.plot(hist.index, hist.values, color=C1, lw=1.8, marker='o', ms=3, label='Tổng tháng thực tế (hiệu chỉnh khoảng trống)')
a.errorbar([tgt], [rows['diem']], yerr=[[rows['diem'] - rows['lo95']], [rows['hi95'] - rows['diem']]], fmt='o', color=CR, capsize=5, lw=1.5, label='Dự báo T12/2010 + KTC 95%')
a.errorbar([tgt], [rows['diem']], yerr=[[rows['diem'] - rows['lo80']], [rows['hi80'] - rows['diem']]], fmt='none', color=CR, capsize=0, lw=5, alpha=.5, label='KTC 80%')
a.annotate(f"{rows['diem']:,.0f} kWh", (tgt, rows['diem']), xytext=(-70, 22), textcoords='offset points', color=CR, fontweight='bold')
a.set(title='Dự báo tổng điện năng tháng 12/2010', ylabel='kWh / tháng'); a.legend(frameon=False, loc='upper right', fontsize=8)
a.set_ylim(0, None)
b = ax[1]
b.barh(['T12/2007', 'T12/2008', 'T12/2009', 'Dự báo T12/2010'], [dec[2007], dec[2008], dec[2009], rows['diem']], color=[C2, C2, C2, CR])
b.errorbar(rows['diem'], 3, xerr=[[rows['diem'] - rows['lo95']], [rows['hi95'] - rows['diem']]], color='k', capsize=4)
b.set(title='So với các tháng 12 trước', xlabel='kWh');
fig.tight_layout(); fig.savefig(O + 'du_bao_T12_2010.png'); plt.close(fig)
print(dec)
