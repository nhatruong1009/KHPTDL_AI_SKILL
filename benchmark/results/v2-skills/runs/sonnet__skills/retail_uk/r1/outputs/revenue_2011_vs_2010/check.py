import pandas as pd
d = pd.read_pickle('outputs/revenue_2011_vs_2010/raw.pkl')
d['rev'] = d.Quantity * d.Price
a = d[d.sheet.str.contains('2009')]
b = d[d.sheet.str.contains('2010-2011')]
print(a.InvoiceDate.min(), a.InvoiceDate.max())
print(b.InvoiceDate.min(), b.InvoiceDate.max())
ov = (a.InvoiceDate >= b.InvoiceDate.min())
print('sheet1 rows in overlap window', ov.sum())
ob = b[b.InvoiceDate <= a.InvoiceDate.max()]
print('sheet2 rows in overlap window', len(ob))
k = ['Invoice', 'StockCode', 'Quantity', 'InvoiceDate', 'Price', 'Customer ID']
m = a[ov].merge(ob[k].drop_duplicates(), on=k, how='inner')
print('matching rows', len(m))
print('rev overlap s1', a[ov].rev.sum(), 's2', ob.rev.sum())
print('cancel invoices', d.Invoice.astype(str).str.startswith('C').sum())
print('non-product codes', d[d.StockCode.astype(str).str.match(r'^[A-Za-z]+$')].StockCode.value_counts().head(15))
print('neg price rows', (d.Price <= 0).sum(), 'qty<0 non C', ((d.Quantity < 0) & ~d.Invoice.astype(str).str.startswith('C')).sum())
print('missing cust rev share', d[d['Customer ID'].isna()].rev.sum() / d.rev.sum())
print(d.groupby('Country').rev.sum().sort_values().tail(8))
