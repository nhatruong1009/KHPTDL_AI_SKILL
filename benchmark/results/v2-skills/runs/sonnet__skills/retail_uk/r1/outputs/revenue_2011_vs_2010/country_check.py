import pandas as pd
d = pd.read_pickle('outputs/revenue_2011_vs_2010/raw.pkl').drop_duplicates(
    subset=['Invoice','StockCode','Description','Quantity','InvoiceDate','Price','Customer ID','Country'])
d = d[d.Price > 0]; d['rev'] = d.Quantity * d.Price
for c in ['Australia', 'EIRE', 'France', 'Denmark']:
    for y in [2010, 2011]:
        x = d[(d.Country == c) & (d.InvoiceDate >= f'{y}-01-01') & (d.InvoiceDate < f'{y}-12-09')]
        t = x.groupby('Customer ID', dropna=False).rev.sum().sort_values(ascending=False)
        print(c, y, round(x.rev.sum()), 'khách', len(t), 'top3', t.head(3).round(0).to_dict())
