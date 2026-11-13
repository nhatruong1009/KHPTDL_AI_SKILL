import pandas as pd, glob

def load(folder, name):
    f = [x for x in glob.glob(f'data/{folder}/API*.csv')][0]
    d = pd.read_csv(f, skiprows=4, encoding='utf-8-sig')
    yrs = [c for c in d.columns if c.isdigit()]
    return d[['Country Name', 'Country Code'] + yrs].melt(['Country Name', 'Country Code'], yrs, 'year', name).assign(year=lambda x: x.year.astype(int))

def meta():
    f = glob.glob('data/life_expectancy/Metadata_Country*.csv')[0]
    return pd.read_csv(f, encoding='utf-8-sig')

if __name__ == '__main__':
    l = load('life_expectancy', 'le'); h = load('health_expenditure_per_capita', 'hx'); g = load('gdp_per_capita_ppp', 'gdp')
    m = l.merge(h, on=['Country Name', 'Country Code', 'year'], how='outer').merge(g, on=['Country Name', 'Country Code', 'year'], how='outer')
    print(m.shape, m['Country Code'].nunique())
    print(m.dropna(subset=['le', 'hx', 'gdp']).groupby('year').size().tail(14).to_string())
    print(m.groupby('year')[['le', 'hx', 'gdp']].count().tail(6))
    md = meta(); print(md.columns.tolist(), md.Region.isna().sum(), md.shape)
    print(md[md['Country Code'].isin(['VNM', 'WLD'])].T)
    print(m[m.year == 2022].describe().to_string())
