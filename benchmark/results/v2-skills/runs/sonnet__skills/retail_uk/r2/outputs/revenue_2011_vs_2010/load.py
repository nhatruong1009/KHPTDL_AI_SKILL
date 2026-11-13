import pandas as pd
x = pd.read_excel('data/online_retail_II.xlsx', sheet_name=None)
df = pd.concat(x.values(), ignore_index=True)
df.to_pickle('outputs/revenue_2011_vs_2010/raw_cache.pkl')
print(df.shape)
