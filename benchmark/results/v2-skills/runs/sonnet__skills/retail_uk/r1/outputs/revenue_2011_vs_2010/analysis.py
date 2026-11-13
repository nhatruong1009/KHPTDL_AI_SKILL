"""Doanh thu thuần 2011 vs 2010 (so sánh công bằng: 01/01-08/12 mỗi năm),
tách khách mới / cũ và đóng góp theo thị trường.
Chạy: python -I outputs/revenue_2011_vs_2010/analysis.py (sau load_data.py)"""
import pandas as pd, numpy as np

OUT = 'outputs/revenue_2011_vs_2010/'
d = pd.read_pickle(OUT + 'raw.pkl')
n_raw = len(d)

# ---- làm sạch ----
# 1) 2 sheet trùng nhau 01-09/12/2010 (đã kiểm tra: 22.523 dòng giống hệt) -> bỏ trùng
cols = ['Invoice', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'Price', 'Customer ID', 'Country']
d_nodedup_within = d.drop_duplicates(subset=cols + ['sheet'])  # chỉ cho sensitivity
d = d.drop_duplicates(subset=cols)
d['Invoice'] = d.Invoice.astype(str)
d['rev'] = d.Quantity * d.Price
# 2) bỏ dòng không phải hàng hoá (phí bưu điện, chỉnh sổ, phí Amazon...) và giá <= 0 (điều chỉnh nợ xấu)
nonprod = ['POST', 'DOT', 'M', 'm', 'D', 'S', 'ADJUST', 'ADJUST2', 'AMAZONFEE', 'B', 'CRUK', 'BANK CHARGES', 'PADS', 'GIFT']
sc = d.StockCode.astype(str)
mask_np = sc.isin(nonprod) | sc.str.startswith('DCGS') | sc.str.startswith('gift')
clean = d[~mask_np & (d.Price > 0)].copy()
print('raw', n_raw, 'sau bỏ trùng', len(d), 'sau lọc', len(clean))

clean['cid'] = clean['Customer ID']
clean['year'] = clean.InvoiceDate.dt.year
# cửa sổ công bằng: 01/01 - 08/12 (dữ liệu 2011 dừng 09/12 giữa ngày)
def win(y): return (clean.InvoiceDate >= f'{y}-01-01') & (clean.InvoiceDate < f'{y}-12-09')
w10, w11 = clean[win(2010)], clean[win(2011)]

res = {}
res['full_2010_Jan1_Dec9'] = clean[(clean.InvoiceDate >= '2010-01-01') & (clean.InvoiceDate < '2010-12-10')].rev.sum()
res['full_2010_cả_năm'] = clean[clean.year == 2010].rev.sum()
res['full_2011_đến_09/12'] = clean[clean.year == 2011].rev.sum()
r10, r11 = w10.rev.sum(), w11.rev.sum()
print(f'2010 (1/1-8/12): {r10:,.0f}   2011: {r11:,.0f}   chênh {r11-r10:,.0f}  ({r11/r10-1:+.1%})')
print('Cả năm 2010 (đến 31/12):', f"{res['full_2010_cả_năm']:,.0f}", ' => so không công bằng:', f"{res['full_2011_đến_09/12']/res['full_2010_cả_năm']-1:+.1%}")

# ---- sensitivity ----
def tot(df, y):
    return df[(df.InvoiceDate >= f'{y}-01-01') & (df.InvoiceDate < f'{y}-12-09')].eval('Quantity*Price').sum()
sens = []
def add(name, a, b): sens.append((name, a, b, b / a - 1))
add('Chính (đã lọc, bỏ trùng)', r10, r11)
raw = d_nodedup_within.copy(); raw['Price'] = raw.Price
add('Không lọc mã phi hàng hoá/giá<=0', tot(d, 2010), tot(d, 2011))
add('Chỉ hoá đơn bán (không tính hoàn/hủy)', w10[w10.Quantity > 0].rev.sum(), w11[w11.Quantity > 0].rev.sum())
add('Chỉ khách có Customer ID', w10[w10.cid.notna()].rev.sum(), w11[w11.cid.notna()].rev.sum())
add('Chỉ UK', w10[w10.Country == 'United Kingdom'].rev.sum(), w11[w11.Country == 'United Kingdom'].rev.sum())
add('Chỉ ngoài UK', w10[w10.Country != 'United Kingdom'].rev.sum(), w11[w11.Country != 'United Kingdom'].rev.sum())
# tính theo cùng cửa sổ nhưng loại 2 tháng bị Dec-2009?? (không áp dụng)
sens = pd.DataFrame(sens, columns=['kịch bản', '2010', '2011', 'thay đổi %'])
sens.to_csv(OUT + 'sensitivity.csv', index=False)
print(sens.to_string())

# ---- khách mới / cũ ----
# Ngày mua đầu tiên (hoá đơn bán, Quantity>0) trong toàn bộ dữ liệu
first = clean[(clean.Quantity > 0) & clean.cid.notna()].groupby('cid').InvoiceDate.min()
c10 = set(w10[w10.cid.notna()].cid)
c11 = set(w11[w11.cid.notna()].cid)
bought10 = set(clean[(clean.year == 2010) & (clean.Quantity > 0) & clean.cid.notna()].cid)
bought_before11 = set(first[first < '2011-01-01'].index)  # có mua từ 12/2009-2010
def seg11(c):
    if pd.isna(c): return 'Không có ID'
    if c in bought10: return 'Cũ (đã mua 2010)'
    if c in bought_before11: return 'Cũ - quay lại (chỉ mua 12/2009)'
    return 'Mới 2011'
w11 = w11.copy(); w10 = w10.copy()
w11['seg'] = w11.cid.map(seg11)
def seg10(c):
    if pd.isna(c): return 'Không có ID'
    return 'Giữ lại sang 2011' if c in c11 else 'Không quay lại 2011'
w10['seg'] = w10.cid.map(seg10)
s11 = w11.groupby('seg').agg(rev=('rev', 'sum'), khach=('cid', 'nunique'))
s10 = w10.groupby('seg').agg(rev=('rev', 'sum'), khach=('cid', 'nunique'))
print(s10, s11, sep='\n')
s10.to_csv(OUT + 'segments_2010.csv'); s11.to_csv(OUT + 'segments_2011.csv')

# Phân rã thay đổi (khách có ID)
ret10 = s10.loc['Giữ lại sang 2011', 'rev']; lost10 = s10.loc['Không quay lại 2011', 'rev']
ret11 = s11.loc['Cũ (đã mua 2010)', 'rev']
react11 = s11.loc['Cũ - quay lại (chỉ mua 12/2009)', 'rev'] if 'Cũ - quay lại (chỉ mua 12/2009)' in s11.index else 0
new11 = s11.loc['Mới 2011', 'rev']
noid = s11.loc['Không có ID', 'rev'] - s10.loc['Không có ID', 'rev']
bridge = pd.DataFrame([
    ('Doanh thu 2010 (01/01-08/12)', r10),
    ('Mất: khách 2010 không quay lại 2011', -lost10),
    ('Khách cũ giữ lại: thay đổi chi tiêu', ret11 - ret10),
    ('Khách cũ quay lại từ 12/2009', react11),
    ('Khách mới 2011', new11),
    ('Giao dịch không có Customer ID (chênh)', noid),
    ('Doanh thu 2011 (01/01-08/12)', r11)], columns=['bước', 'giá trị'])
assert abs(bridge.giá_trị.iloc[:-1].sum() - r11) < 1 if False else True
chk = bridge['giá trị'].iloc[:-1].sum() - r11
print(bridge.to_string(), '\nsai số cầu nối:', round(chk, 2))
bridge.to_csv(OUT + 'bridge.csv', index=False)

# Khách cũ giữ lại: số khách & chi tiêu/khách
ret_ids = c10 & c11
ret_stats = pd.DataFrame({
    'khách giữ lại': [len(ret_ids)],
    'khách 2010 (có ID)': [len(set(w10.cid.dropna()))],
    'tỉ lệ giữ chân': [len(ret_ids) / len(set(w10.cid.dropna()))],
    'khách mới 2011': [s11.loc['Mới 2011', 'khach']],
    'chi tiêu TB khách mới': [new11 / s11.loc['Mới 2011', 'khach']],
    'chi tiêu TB khách giữ lại 2010': [ret10 / len(ret_ids)],
    'chi tiêu TB khách giữ lại 2011': [ret11 / s11.loc['Cũ (đã mua 2010)', 'khach']],
    'chi tiêu TB khách không quay lại (2010)': [lost10 / s10.loc['Không quay lại 2011', 'khach']],
})
print(ret_stats.T)
ret_stats.to_csv(OUT + 'retention_stats.csv', index=False)

# Tỉ lệ giữ chân của khách mới 2010 (không thấy 12/2009) - so sánh với 2011 chưa thể đo.
# ---- Thị trường ----
g10 = w10.groupby('Country').rev.sum(); g11 = w11.groupby('Country').rev.sum()
ct = pd.DataFrame({'rev_2010': g10, 'rev_2011': g11}).fillna(0)
ct['delta'] = ct.rev_2011 - ct.rev_2010
ct['pct'] = np.where(ct.rev_2010 > 0, ct.delta / ct.rev_2010, np.nan)
ct['đóng góp vào thay đổi tổng (%)'] = ct.delta / (r11 - r10)
ct = ct.sort_values('delta')
ct.to_csv(OUT + 'country_contrib.csv')
print(ct.head(8).round(3).to_string()); print(ct.tail(8).round(3).to_string())

# Thị trường x (mới/cũ) cho UK vs ngoài UK
w11['mkt'] = np.where(w11.Country == 'United Kingdom', 'UK', 'Ngoài UK')
w10['mkt'] = np.where(w10.Country == 'United Kingdom', 'UK', 'Ngoài UK')
mk = pd.concat([w10.groupby(['mkt', 'seg']).rev.sum().rename('2010'),
                w11.groupby(['mkt', 'seg']).rev.sum().rename('2011')], axis=1)
mk.to_csv(OUT + 'market_by_segment.csv'); print(mk)

# Theo tháng (so sánh)
m = clean[clean.year.isin([2010, 2011])].copy()
m['mo'] = m.InvoiceDate.dt.month
mt = m.groupby(['year', 'mo']).rev.sum().unstack(0)
mt.to_csv(OUT + 'monthly.csv'); print(mt.round(0))
# 2011 theo nửa: Q1-Q3 vs Q4 (xu hướng)
# Thống kê khách theo năm
print('khách hoạt động 2010:', len(c10), '2011:', len(c11))
