import pandas as pd
from pathlib import Path
d = Path('data')


def load(sub):
    f = list((d / sub).glob('API_*'))[0]
    return pd.read_csv(f, skiprows=4, encoding='utf-8-sig')


le = load('life_expectancy')
he = load('health_expenditure_per_capita')
g = load('gdp_per_capita_ppp')
for n, x in [('le', le), ('he', he), ('gdp', g)]:
    yc = [c for c in x.columns if c.isdigit()]
    print(n, x.shape, x[yc].notna().sum().tail(8).to_dict())
    print(x[x['Country Code'] == 'VNM'][yc[-12:]].to_string())
