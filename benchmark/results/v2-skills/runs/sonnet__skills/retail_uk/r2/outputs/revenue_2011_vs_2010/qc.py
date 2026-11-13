import pandas as pd
d = pd.read_pickle('outputs/revenue_2011_vs_2010/raw_cache.pkl')
print(len(d), 'full dups', d.duplicated().sum())
o = d[(d.InvoiceDate >= '2010-12-01') & (d.InvoiceDate < '2010-12-10')]
print(o.groupby(o.InvoiceDate.dt.date).size())
# overlap between sheets: same invoice in both?
s1 = d.iloc[:525461]; s2 = d.iloc[525461:]
ov = set(s1.Invoice.astype(str)) & set(s2.Invoice.astype(str))
print('invoices in both sheets', len(ov))
print(d.InvoiceDate.min(), d.InvoiceDate.max())
d['rev'] = d.Quantity * d.Price
inv = d.Invoice.astype(str)
print(inv.str[0].where(~inv.str[0].str.isdigit(), '#').value_counts())
print('cancel qty', d[inv.str.startswith('C')].Quantity.describe())
sc = d.StockCode.astype(str)
non = d[sc.str.match(r'^[A-Za-z]') & ~sc.str.match(r'^[A-Za-z]?\d')]
print(non.groupby('StockCode').rev.agg(['size', 'sum']).sort_values('sum'))
print('price<=0', (d.Price <= 0).sum(), d[d.Price < 0].Description.unique())
print('null cust rev share', d[d['Customer ID'].isna()].rev.sum() / d.rev.sum())
print(d.groupby(d.InvoiceDate.dt.to_period('M')).rev.sum())
