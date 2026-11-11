import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'DejaVu Sans'

a = pd.read_pickle('_Year_2009-2010.pkl')
b = pd.read_pickle('_Year_2010-2011.pkl')
# bỏ phần trùng giữa 2 sheet (01-09/12/2010 xuất hiện ở cả hai)
b = b[b.InvoiceDate > a.InvoiceDate.max()]
d = pd.concat([a, b], ignore_index=True)
d['Invoice'] = d.Invoice.astype(str)
d['rev'] = d.Quantity * d.Price
d['cid'] = d['Customer ID']
nonprod = ['POST', 'DOT', 'M', 'C2', 'D', 'S', 'BANK CHARGES', 'ADJUST', 'ADJUST2', 'AMAZONFEE', 'CRUK', 'B', 'TEST001', 'TEST002', 'm']
sc = d.StockCode.astype(str)
d['isprod'] = ~sc.isin(nonprod) & ~sc.str.startswith('gift_') & ~d.Invoice.str.startswith('A')
d['y'] = d.InvoiceDate.dt.year


def win(y):
    return (d.InvoiceDate >= f'{y}-01-01') & (d.InvoiceDate < f'{y}-12-10')


# ---- tổng quan: nhiều định nghĩa
out = []
for lab, m in [('Hàng hoá (loại phí ship/điều chỉnh)', d.isprod), ('Tất cả dòng (trừ hóa đơn A)', ~d.Invoice.str.startswith('A'))]:
    for nm, w in [('Cả năm lịch (2011 chỉ đến 9/12)', lambda y: d.y == y), ('01/01-09/12', win)]:
        r10 = d[m & w(2010)].rev.sum()
        r11 = d[m & w(2011)].rev.sum()
        out.append((lab, nm, r10, r11, r11 - r10, (r11 / r10 - 1) * 100))
t = pd.DataFrame(out, columns=['định_nghĩa', 'cửa_sổ', 'rev_2010', 'rev_2011', 'chênh', 'pct'])
print(t.round(1).to_string())
t.to_csv('tong_quan.csv', index=False)

D = d[d.isprod].copy()
w10 = D[(D.InvoiceDate >= '2010-01-01') & (D.InvoiceDate < '2010-12-10')]
w11 = D[(D.InvoiceDate >= '2011-01-01') & (D.InvoiceDate < '2011-12-10')]
mm = pd.DataFrame({'2010': w10.groupby(w10.InvoiceDate.dt.month).rev.sum(), '2011': w11.groupby(w11.InvoiceDate.dt.month).rev.sum()})
mm['pct'] = (mm['2011'] / mm['2010'] - 1) * 100
print(mm.round(0))
mm.to_csv('theo_thang.csv')

# ---- khách mới / cũ
first = D.dropna(subset=['cid']).groupby('cid').InvoiceDate.min()
c10 = w10.groupby('cid').rev.sum()
c11 = w11.groupby('cid').rev.sum()
ids = c10.index.union(c11.index)
df = pd.DataFrame({'r10': c10, 'r11': c11}).reindex(ids).fillna(0)
df['first'] = first.reindex(df.index)


def cls(r):
    if r.r10 != 0 and r.r11 != 0:
        return '1. Khách cũ giữ lại'
    if r.r10 != 0:
        return '2. Khách cũ rời bỏ'
    if r['first'] >= pd.Timestamp('2011-01-01'):
        return '3. Khách mới 2011'
    return '4. Khách cũ quay lại'


df['nhom'] = df.apply(cls, axis=1)
g = df.groupby('nhom').agg(so_khach=('r10', 'size'), rev_2010=('r10', 'sum'), rev_2011=('r11', 'sum'))
g['chenh'] = g.rev_2011 - g.rev_2010
un10 = w10[w10.cid.isna()].rev.sum()
un11 = w11[w11.cid.isna()].rev.sum()
g.loc['5. Không có Customer ID'] = [np.nan, un10, un11, un11 - un10]
g.loc['TỔNG'] = [np.nan, g.rev_2010.sum(), g.rev_2011.sum(), g.chenh.sum()]
print(g.round(0).to_string())
g.to_csv('khach_moi_cu.csv')
print('check', w10.rev.sum(), w11.rev.sum())
n10 = (c10 != 0).sum()
ret = ((df.r10 != 0) & (df.r11 != 0)).sum()
print('retention', ret / n10, n10, ret)
# khách giữ lại: doanh thu/khách
k = df[df.nhom == '1. Khách cũ giữ lại']
print('giữ lại: r10/khách', k.r10.mean(), 'r11/khách', k.r11.mean())

# ---- quốc gia
cn = pd.DataFrame({'2010': w10.groupby('Country').rev.sum(), '2011': w11.groupby('Country').rev.sum()}).fillna(0)
cn['chenh'] = cn['2011'] - cn['2010']
cn['pct'] = cn.chenh / cn['2010'] * 100
cn = cn.sort_values('chenh')
cn['dong_gop_pct_tong_chenh'] = cn.chenh / cn.chenh.sum() * 100
print(cn.head(6).round(0))
print(cn.tail(8).round(0))
cn.to_csv('theo_quoc_gia.csv')

D2 = pd.concat([w10.assign(P='2010'), w11.assign(P='2011')])
D2['uk'] = np.where(D2.Country == 'United Kingdom', 'UK', 'Ngoài UK')
D2['nhom'] = D2.cid.map(df['nhom']).fillna('5. Không có Customer ID')
x = D2.pivot_table(index=['uk', 'nhom'], columns='P', values='rev', aggfunc='sum').fillna(0)
x['chenh'] = x['2011'] - x['2010']
print(x.round(0))
x.to_csv('uk_x_nhom.csv')
print(df.sort_values('r11', ascending=False).head(8)[['r10', 'r11', 'nhom']].round(0))
for nm, w in [('2010', w10), ('2011', w11)]:
    kk = w.dropna(subset=['cid'])
    inv = kk.groupby('Invoice').rev.sum()
    print(nm, 'khách', kk.cid.nunique(), 'đơn', kk.Invoice.nunique(), 'AOV', round(inv.mean()), 'rev/khách', round(kk.rev.sum() / kk.cid.nunique()))

# ---- biểu đồ
C = {'g': '#2a9d8f', 'r': '#e76f51', 'b': '#264653', 'gr': '#9aa5a8'}
fig, ax = plt.subplots(figsize=(10, 5.5))
rows = g.drop('TỔNG')
lab = ['Doanh thu\n2010', 'Khách cũ\ngiữ lại', 'Khách cũ\nrời bỏ', 'Khách mới\n2011', 'Khách cũ\nquay lại', 'Không có\nCustomer ID', 'Doanh thu\n2011']
cum = g.loc['TỔNG', 'rev_2010'] / 1e6
ax.bar(0, cum, color=C['gr'])
ax.text(0, cum + .1, f'{cum:.2f}', ha='center')
cur = cum
for i, v in enumerate(rows.chenh.values, 1):
    v /= 1e6
    ax.bar(i, v, bottom=cur, color=C['g'] if v > 0 else C['r'])
    ax.text(i, max(cur, cur + v) + .1, f'{v:+.2f}', ha='center')
    cur += v
ax.bar(6, cur, color=C['b'])
ax.text(6, cur + .1, f'{cur:.2f}', ha='center')
ax.set_xticks(range(7))
ax.set_xticklabels(lab, fontsize=9)
ax.set_ylabel('Triệu GBP')
ax.set_title('Doanh thu thuần 01/01–09/12: khách mới chưa bù hết phần mất từ khách cũ', fontsize=11)
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig('cau_noi_khach_hang.png', dpi=150)
plt.close()

fig, ax = plt.subplots(figsize=(9, 5.5))
s = pd.concat([cn.head(5), cn.tail(5)]).chenh / 1e3
ax.barh(s.index, s.values, color=[C['r'] if v < 0 else C['g'] for v in s.values])
for i, v in enumerate(s.values):
    ax.text(v, i, f' {v:+,.0f}', va='center', ha='left' if v > 0 else 'right', fontsize=9)
ax.set_xlabel('Chênh lệch doanh thu 2011 so với 2010 (nghìn GBP)')
ax.set_title('Thị trường kéo tăng/giảm nhiều nhất (01/01–09/12)')
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig('thi_truong.png', dpi=150)
plt.close()

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(mm.index, mm['2010'] / 1e3, label='2010', color=C['gr'], marker='o')
ax.plot(mm.index, mm['2011'] / 1e3, label='2011', color=C['b'], marker='o')
ax.set_xticks(range(1, 13))
ax.set_xlabel('Tháng (tháng 12 chỉ đến ngày 9)')
ax.set_ylabel('Nghìn GBP')
ax.legend()
ax.set_title('Doanh thu thuần theo tháng')
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig('theo_thang.png', dpi=150)
