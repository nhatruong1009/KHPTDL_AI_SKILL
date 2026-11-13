"""Doanh thu thuan 2011 vs 2010 (so sanh cong bang), moi/cu, theo thi truong.
Chay tu thu muc goc project:  python -I outputs/revenue_2011_vs_2010/analysis.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = 'outputs/revenue_2011_vs_2010'
CACHE = f'{OUT}/raw_cache.pkl'
if os.path.exists(CACHE):
    raw = pd.read_pickle(CACHE)
    n_sheet1 = 525461
else:
    sh = pd.read_excel('data/online_retail_II.xlsx', sheet_name=None)
    raw = pd.concat(sh.values(), ignore_index=True)
    n_sheet1 = len(list(sh.values())[0])
raw['sheet'] = np.where(np.arange(len(raw)) < n_sheet1, 1, 2)
raw['Invoice'] = raw['Invoice'].astype(str)
raw['StockCode'] = raw['StockCode'].astype(str)
raw['rev'] = raw.Quantity * raw.Price
log = {}

# ---------- 1. Làm sạch ----------
# (a) Sheet 1 (2009-12-01..2010-12-09) và sheet 2 (2010-12-01..2011-12-09) trùng nhau 1-9/12/2010.
ov1 = raw[(raw.sheet == 1) & (raw.InvoiceDate >= '2010-12-01')]
ov2 = raw[(raw.sheet == 2) & (raw.InvoiceDate < '2010-12-10')]
key = ['Invoice', 'StockCode', 'Quantity', 'InvoiceDate', 'Price', 'Customer ID', 'Country']
log['overlap_rows_sheet1'] = len(ov1)
log['overlap_rows_sheet2'] = len(ov2)
log['overlap_rev_sheet1'] = ov1.rev.sum()
log['overlap_rev_sheet2'] = ov2.rev.sum()
df = raw[~((raw.sheet == 1) & (raw.InvoiceDate >= '2010-12-01'))].copy()   # giữ bản sheet 2

# (b) Loại dòng không phải hàng hoá (phí bưu điện, phí Amazon, điều chỉnh nợ xấu, chi phí ngân hàng...)
NONPROD = {'POST', 'DOT', 'AMAZONFEE', 'B', 'M', 'm', 'BANK CHARGES', 'D', 'CRUK', 'S', 'ADJUST', 'ADJUST2',
           'PADS', 'C2', 'TEST001', 'TEST002'}
is_np = df.StockCode.isin(NONPROD) | df.StockCode.str.startswith(('gift_', 'DCGS', 'SP1002'))
log['nonproduct_rev_removed'] = df[is_np].rev.sum()
log['rows_after_overlap'] = len(df)
prod = df[~is_np].copy()
prod['year'] = prod.InvoiceDate.dt.year
prod['cid'] = prod['Customer ID']

# ---------- 2. Cửa sổ so sánh công bằng ----------
# Dữ liệu 2011 kết thúc 09/12/2011 12:50 -> so 01/01 - 08/12 mỗi năm (ngày đủ).
def win(d, y):
    return d[(d.InvoiceDate >= f'{y}-01-01') & (d.InvoiceDate < f'{y}-12-09')]
w10, w11 = win(prod, 2010), win(prod, 2011)
full10 = prod[prod.year == 2010]
full11 = prod[prod.year == 2011]
res = {
    'full_2010': full10.rev.sum(), 'full_2011_to_9Dec': full11.rev.sum(),
    'win_2010_1Jan_8Dec': w10.rev.sum(), 'win_2011_1Jan_8Dec': w11.rev.sum(),
}
res['naive_change_%'] = (res['full_2011_to_9Dec'] / res['full_2010'] - 1) * 100
res['fair_change_abs'] = res['win_2011_1Jan_8Dec'] - res['win_2010_1Jan_8Dec']
res['fair_change_%'] = (res['win_2011_1Jan_8Dec'] / res['win_2010_1Jan_8Dec'] - 1) * 100
# doanh thu thuần: gồm cả hàng trả (hoá đơn C có Quantity âm) - đã nằm trong rev
gross = lambda d: d[d.rev > 0].rev.sum()
ret = lambda d: d[d.rev < 0].rev.sum()
res.update({'gross_2010w': gross(w10), 'returns_2010w': ret(w10), 'gross_2011w': gross(w11), 'returns_2011w': ret(w11)})
res['orders_2010w'] = w10[w10.rev > 0].Invoice.nunique()
res['orders_2011w'] = w11[w11.rev > 0].Invoice.nunique()
res['active_cust_2010w'] = w10.cid.nunique()
res['active_cust_2011w'] = w11.cid.nunique()
pd.Series(res).to_csv(f'{OUT}/headline_numbers.csv', header=['value'])

# Kiểm tra nhạy cảm
sens = {}
sens['A_chuan (bo dong khong phai hang hoa, bo trung sheet)'] = res['fair_change_%']
all_ = df.copy()
sens['B_giu moi dong (gom phi/dieu chinh)'] = (win(all_, 2011).rev.sum() / win(all_, 2010).rev.sum() - 1) * 100
dd = prod.drop_duplicates(key)
sens['C_bo dong trung hoan toan'] = (win(dd, 2011).rev.sum() / win(dd, 2010).rev.sum() - 1) * 100
g10, g11 = w10[w10.rev > 0].rev.sum(), w11[w11.rev > 0].rev.sum()
sens['D_chi doanh thu gop (khong tru hang tra)'] = (g11 / g10 - 1) * 100
idn = prod[prod.cid.notna()]
sens['E_chi khach co Customer ID'] = (win(idn, 2011).rev.sum() / win(idn, 2010).rev.sum() - 1) * 100
# Nếu quên loại trùng sheet (sai) -> cho thấy tác động
bad = pd.concat([raw[raw.sheet == 1], raw[raw.sheet == 2]])
bad = bad[~bad.StockCode.isin(NONPROD)]
sens['F_SAI: cong trung sheet 1-9/12/2010'] = (win(bad, 2011).rev.sum() / win(bad, 2010).rev.sum() - 1) * 100
pd.Series(sens).to_csv(f'{OUT}/sensitivity.csv', header=['change_%'])

# Bootstrap theo khách hàng (khoảng tin cậy cho % thay đổi)
cust = pd.concat([w10.groupby('cid', dropna=False).rev.sum().rename('r10'),
                  w11.groupby('cid', dropna=False).rev.sum().rename('r11')], axis=1).fillna(0)
rng = np.random.default_rng(0)
idx = np.arange(len(cust)); a = cust.r10.values; b = cust.r11.values
bs = []
for _ in range(2000):
    s = rng.choice(idx, len(idx))
    bs.append((b[s].sum() / a[s].sum() - 1) * 100)
res['ci_lo'], res['ci_hi'] = np.percentile(bs, [2.5, 97.5])
pd.Series(res).to_csv(f'{OUT}/headline_numbers.csv', header=['value'])

# ---------- 3. Mới / cũ ----------
first_date = prod[prod.rev > 0].groupby('cid').InvoiceDate.min()   # lần mua đầu tiên trong dữ liệu
r10 = w10.groupby('cid').rev.sum(); r11 = w11.groupby('cid').rev.sum()
c = pd.concat([r10.rename('r10'), r11.rename('r11')], axis=1).fillna(0)
c['first'] = first_date.reindex(c.index)
def seg(row):
    if row.r10 != 0 and row.r11 != 0: return 'Cũ - mua cả 2 năm (giữ chân)'
    if row.r10 != 0 and row.r11 == 0: return 'Cũ - rời bỏ (có 2010, không có 2011)'
    # có 2011, không có 2010
    if pd.notna(row['first']) and row['first'] < pd.Timestamp('2011-01-01'):
        return 'Cũ - quay lại (mua trước 2010/ngoài cửa sổ, không mua 2010)'
    return 'Mới - lần đầu mua năm 2011'
c['segment'] = c.apply(seg, axis=1)
unid10 = w10[w10.cid.isna()].rev.sum(); unid11 = w11[w11.cid.isna()].rev.sum()
s = c.groupby('segment').agg(khach=('r10', 'size'), rev_2010=('r10', 'sum'), rev_2011=('r11', 'sum'))
s.loc['Không có Customer ID (không phân loại được)'] = [np.nan, unid10, unid11]
s['thay_doi'] = s.rev_2011 - s.rev_2010
s['dong_gop_%_vao_thay_doi_tong'] = s.thay_doi / res['fair_change_abs'] * 100
s.to_csv(f'{OUT}/segment_new_vs_existing.csv')
print(s.round(0).to_string())

# Chi tiết nhóm giữ chân: bao nhiêu % khách 2010 còn mua 2011, doanh thu/khách
n10 = (c.r10 != 0).sum(); kept = ((c.r10 != 0) & (c.r11 != 0)).sum()
ret_tbl = pd.Series({
    'khach_2010': n10, 'khach_2010_con_mua_2011': kept, 'ty_le_giu_chan_%': kept / n10 * 100,
    'khach_moi_2011': (c.segment == 'Mới - lần đầu mua năm 2011').sum(),
    'rev_moi_tren_khach': c[c.segment == 'Mới - lần đầu mua năm 2011'].r11.mean(),
    'rev_giu_chan_2010_tren_khach': c[c.segment.str.startswith('Cũ - mua cả')].r10.mean(),
    'rev_giu_chan_2011_tren_khach': c[c.segment.str.startswith('Cũ - mua cả')].r11.mean(),
    'rev_roi_bo_2010_tren_khach': c[c.segment.str.startswith('Cũ - rời')].r10.mean(),
})
ret_tbl.to_csv(f'{OUT}/retention_summary.csv', header=['value'])
print(ret_tbl.round(1))

# Cùng cách làm: khách mới 2010 (lần đầu mua trong 2010) để biết 2011 có yếu về khách mới không
new10 = c[(c.r10 != 0) & (c['first'] >= pd.Timestamp('2010-01-01'))]
log['new_cust_2010_in_window'] = len(new10)
log['new_cust_2010_rev'] = new10.r10.sum()
# Dec 2009 khách "cũ" thật sự chỉ biết từ 2009-12 -> khách mới 2010 bị thổi phồng nhẹ: ghi chú caveat

# ---------- 4. Thị trường ----------
cty = pd.concat([w10.groupby('Country').rev.sum().rename('rev_2010'),
                 w11.groupby('Country').rev.sum().rename('rev_2011')], axis=1).fillna(0)
cty['thay_doi'] = cty.rev_2011 - cty.rev_2010
cty['thay_doi_%'] = cty.thay_doi / cty.rev_2010.replace(0, np.nan) * 100
cty['dong_gop_diem_%'] = cty.thay_doi / res['win_2010_1Jan_8Dec'] * 100
cty = cty.sort_values('thay_doi')
cty.to_csv(f'{OUT}/country_contribution.csv')
print(cty.head(6).round(0).to_string()); print(cty.tail(8).round(0).to_string())
# Anh vs ngoài Anh, mới/cũ theo thị trường
uk = pd.DataFrame({'uk': np.where(w10.Country == 'United Kingdom', 'UK', 'Ngoài UK')})
def grp(d): return d.assign(g=np.where(d.Country == 'United Kingdom', 'UK', 'Ngoài UK')).groupby('g').rev.sum()
ukt = pd.concat([grp(w10).rename('rev_2010'), grp(w11).rename('rev_2011')], axis=1)
ukt['thay_doi'] = ukt.rev_2011 - ukt.rev_2010; ukt['thay_doi_%'] = ukt.thay_doi / ukt.rev_2010 * 100
ukt.to_csv(f'{OUT}/uk_vs_nonuk.csv'); print(ukt.round(1))

# Mới/cũ trong từng thị trường lớn (khách gán nước theo dòng giao dịch đầu tiên của họ)
cc = prod[prod.cid.notna()].sort_values('InvoiceDate').groupby('cid').Country.first()
c['Country'] = cc.reindex(c.index)
mc = c.groupby(['Country', 'segment']).apply(lambda g: g.r11.sum() - g.r10.sum()).unstack(fill_value=0)
mc['tong'] = mc.sum(axis=1)
mc.sort_values('tong').to_csv(f'{OUT}/country_by_segment_change.csv')

# Theo tháng (kiểm tra mùa vụ)
m = prod.assign(m=prod.InvoiceDate.dt.month, y=prod.year).query('y in (2010, 2011)')
mm = m.pivot_table(index='m', columns='y', values='rev', aggfunc='sum')
mm['thay_doi_%'] = (mm[2011] / mm[2010] - 1) * 100
mm.to_csv(f'{OUT}/monthly_2010_2011.csv'); print(mm.round(0))
# Nửa năm
h = lambda d, a, b: d[(d.InvoiceDate.dt.month >= a) & (d.InvoiceDate.dt.month <= b)].rev.sum()
log['H1_chg'] = (h(w11, 1, 6) / h(w10, 1, 6) - 1) * 100
log['Q3_Q4_chg_to_8Dec'] = (h(w11, 7, 12) / h(w10, 7, 12) - 1) * 100
pd.Series(log).to_csv(f'{OUT}/qc_log.csv', header=['value'])
print(pd.Series(res).round(2)); print(pd.Series(sens).round(2)); print(pd.Series(log).round(1))

# ---------- 5. Biểu đồ ----------
plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
BLUE, RED, GREY, GREEN = '#2a6fb0', '#c8453b', '#9aa0a6', '#3a8f5c'
fmt = lambda v: f'{v/1e6:+.2f} tr'

# Chart 1: thác nước mới/cũ
order = ['Cũ - rời bỏ (có 2010, không có 2011)', 'Cũ - mua cả 2 năm (giữ chân)',
         'Cũ - quay lại (mua trước 2010/ngoài cửa sổ, không mua 2010)', 'Mới - lần đầu mua năm 2011',
         'Không có Customer ID (không phân loại được)']
lab = ['Khách cũ\nrời bỏ', 'Khách cũ\ngiữ chân\n(mua cả 2 năm)', 'Khách cũ\nquay lại', 'Khách mới\n2011', 'Không có\nMã KH']
vals = [s.loc[o, 'thay_doi'] for o in order]
fig, ax = plt.subplots(figsize=(10, 5.8))
cum = 0
for i, v in enumerate(vals):
    ax.bar(i, v, bottom=cum, color=GREEN if v >= 0 else RED, width=.6)
    ax.text(i, cum + v + (0.04e6 if v >= 0 else -0.04e6), f'{v/1e6:+.2f} tr', ha='center',
            va='bottom' if v >= 0 else 'top', fontweight='bold')
    cum += v
ax.bar(len(vals), cum, color=BLUE, width=.6)
ax.text(len(vals), cum + 0.04e6, f'{cum/1e6:+.2f} tr\n({res["fair_change_%"]:+.1f}%)', ha='center', va='bottom', fontweight='bold')
ax.set_xticks(range(len(vals) + 1)); ax.set_xticklabels(lab + ['Tổng thay đổi'])
ax.axhline(0, color='k', lw=.8)
ax.set_ylim(-1.65e6, 0.5e6); ax.set_yticks([-1.5e6, -1e6, -.5e6, 0, .5e6])
ax.set_ylabel('Thay đổi doanh thu thuần (GBP)'); ax.yaxis.set_major_formatter(lambda v, p: f'{v/1e6:.1f} tr')
ax.set_title(f'Doanh thu thuần cùng kỳ {res["fair_change_%"]:+.1f}% (gần đi ngang): khách mới +{vals[3]/1e6:.2f} tr chỉ vừa bù khách cũ rời bỏ ({vals[0]/1e6:.2f} tr) và khách giữ chân chi ít hơn ({vals[1]/1e6:.2f} tr)',
             fontsize=12, loc='left', wrap=True)
fig.text(.01, .01, 'Nguồn: online_retail_II, cùng cửa sổ 1/1–8/12 mỗi năm; đã loại phí/điều chỉnh và loại trùng sheet. tr = triệu GBP',
         fontsize=8, color='grey')
plt.tight_layout(rect=(0, .03, 1, 1)); plt.savefig(f'{OUT}/chart1_new_vs_existing.png', dpi=150); plt.close()

# Chart 2: quốc gia
top = pd.concat([cty.head(5), cty.tail(5)]).drop_duplicates().sort_values('thay_doi')
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(top.index, top.thay_doi, color=[GREEN if v > 0 else RED for v in top.thay_doi])
for y, (n, r) in enumerate(top.iterrows()):
    ax.text(r.thay_doi + (8e3 if r.thay_doi >= 0 else -8e3), y, f'{r.thay_doi/1e3:+,.0f} k ({r["thay_doi_%"]:+.0f}%)',
            va='center', ha='left' if r.thay_doi >= 0 else 'right', fontsize=9)
ax.axvline(0, color='k', lw=.8); ax.xaxis.set_major_formatter(lambda v, p: f'{v/1e3:,.0f} k')
ax.set_xlim(top.thay_doi.min() * 2.0, top.thay_doi.max() * 1.45 if top.thay_doi.max() > 0 else 1e4)
ax.set_xlabel('Thay đổi doanh thu thuần 2011 vs 2010 (GBP)')
ax.set_title(f'Ngoài UK tăng {ukt.loc["Ngoài UK","thay_doi_%"]:.0f}% (Australia, Pháp kéo tăng; EIRE, Đan Mạch kéo giảm); '
             f'UK gần như đi ngang ({ukt.loc["UK","thay_doi_%"]:+.1f}%)', fontsize=12, loc='left', wrap=True)
plt.tight_layout(); plt.savefig(f'{OUT}/chart2_country.png', dpi=150); plt.close()

# Chart 3: theo tháng
fig, ax = plt.subplots(figsize=(10, 5.2))
ax.plot(mm.index, mm[2010] / 1e3, marker='o', color=GREY, label='2010')
ax.plot(mm.index, mm[2011] / 1e3, marker='o', color=BLUE, label='2011')
ax.annotate('Tháng 12/2011 chỉ có dữ liệu đến 9/12\n→ không so sánh nguyên tháng', xy=(12, mm.loc[12, 2011] / 1e3),
            xytext=(8.3, 1000), arrowprops=dict(arrowstyle='->'), fontsize=9)
ax.set_xticks(range(1, 13)); ax.set_xlabel('Tháng'); ax.set_ylabel('Doanh thu thuần (nghìn GBP)')
ax.legend(frameon=False)
ax.set_title('Doanh thu 2011 thấp hơn 2010 ở T1–T4, cao hơn ở T5–T9, T10–T11 gần bằng; T12/2011 mới có 9 ngày', fontsize=12, loc='left')
plt.tight_layout(); plt.savefig(f'{OUT}/chart3_monthly.png', dpi=150); plt.close()

# ---------- 6. Tập trung khách lớn theo thị trường (kiểm tra độ bền) ----------
conc = []
for k in ['Australia', 'France', 'EIRE', 'Denmark', 'Netherlands']:
    a = w11[w11.Country == k].groupby('cid').rev.sum().sort_values(ascending=False)
    b = w10[w10.Country == k].groupby('cid').rev.sum().sort_values(ascending=False)
    conc.append({'Country': k, 'top1_share_2011_pct': a.iloc[0] / a.sum() * 100, 'top1_share_2010_pct': b.iloc[0] / b.sum() * 100,
                 'n_cust_2010': len(b), 'n_cust_2011': len(a)})
pd.DataFrame(conc).to_csv(f'{OUT}/country_concentration.csv', index=False)
print(pd.DataFrame(conc).round(1))
print(mc.sort_values('tong').round(0).iloc[[0, 1, 2, -3, -2, -1]].to_string())
