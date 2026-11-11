import pandas as pd
a=pd.read_pickle('outputs/rev/Year_2009-2010.pkl');b=pd.read_pickle('outputs/rev/Year_2010-2011.pkl')
oa=a[a.InvoiceDate>='2010-12-01'];ob=b[b.InvoiceDate<'2010-12-10']
print(len(oa),len(ob))
k=['Invoice','StockCode','Quantity','InvoiceDate','Price','Customer ID']
print(oa.Invoice.nunique(),ob.Invoice.nunique(),len(set(oa.Invoice)&set(ob.Invoice)))
print(a.duplicated().sum(),b.duplicated().sum())
d=pd.concat([a,b]);d['Invoice']=d.Invoice.astype(str)
print(d.Invoice.str[0].value_counts().head())
print((d.Price<=0).sum(),(d.Quantity<=0).sum())
nonp=d[~d.StockCode.astype(str).str.match(r'^\d{5}')]
print(nonp.groupby('StockCode').agg(n=('Price','size'),v=('Price',lambda s:0)).sort_values('n').tail(15))
print(d.Country.value_counts().head(12))
