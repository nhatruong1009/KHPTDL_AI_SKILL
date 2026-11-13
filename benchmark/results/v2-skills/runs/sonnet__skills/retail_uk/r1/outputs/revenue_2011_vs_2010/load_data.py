import pandas as pd
x = pd.read_excel('data/online_retail_II.xlsx', sheet_name=None)
for k, v in x.items():
    v['sheet'] = k
d = pd.concat(x.values(), ignore_index=True)
d.to_pickle('outputs/revenue_2011_vs_2010/raw.pkl')
print(d.shape)
