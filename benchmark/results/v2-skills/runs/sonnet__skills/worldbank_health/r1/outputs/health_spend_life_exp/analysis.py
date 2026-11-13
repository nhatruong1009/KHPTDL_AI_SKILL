"""Chi tieu y te vs tuoi tho; vuot/duoi ky vong sau khi kiem soat thu nhap. Chay tu thu muc goc: python outputs/health_spend_life_exp/analysis.py"""
import os, sys
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(__file__))
from eda import load, meta


class Fit:
    """OLS toi gian bang numpy (khong can statsmodels)."""
    def __init__(self, d, cols):
        self.cols = cols
        X = np.column_stack([np.ones(len(d))] + [d[c].values for c in cols]); y = d['life_exp'].values
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        self.fittedvalues = pd.Series(X @ b, index=d.index)
        res = y - X @ b; dof = len(y) - X.shape[1]
        s2 = res @ res / dof; se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
        self.params = pd.Series(b, index=['const'] + cols)
        self.pvalues = pd.Series(2 * stats.t.sf(np.abs(b / se), dof), index=self.params.index)
        self.rsquared = 1 - res @ res / ((y - y.mean()) @ (y - y.mean()))

    def predict(self, d):
        return self.params['const'] + sum(self.params[c] * d[c] for c in self.cols)

OUT = os.path.dirname(__file__)
l = load('life_expectancy', 'life_exp'); h = load('health_expenditure_per_capita', 'hx'); g = load('gdp_per_capita_ppp', 'gdp')
m = l.merge(h, on=['Country Name', 'Country Code', 'year'], how='outer').merge(g, on=['Country Name', 'Country Code', 'year'], how='outer')
md = meta()[['Country Code', 'Region', 'IncomeGroup']]
m = m.merge(md, on='Country Code', how='left')
m = m[m.Region.notna()]  # loai cac nhom tong hop (khu vuc, thu nhap...)
m['ln_hx'] = np.log(m.hx); m['ln_gdp'] = np.log(m.gdp)

def ols(d, cols):
    return Fit(d, cols)

rows = []; res = {}
for yr in [2023, 2022, 2019]:
    d = m[m.year == yr].dropna(subset=['life_exp', 'hx', 'gdp']).copy()
    r_hx = np.corrcoef(d.ln_hx, d['life_exp'])[0, 1]
    from scipy.stats import spearmanr
    rho = spearmanr(d.hx, d['life_exp'])[0]
    m1 = ols(d, ['ln_hx']); m2 = ols(d, ['ln_gdp']); m3 = ols(d, ['ln_hx', 'ln_gdp'])
    d['exp_gdp'] = m2.predict(d); d['res_gdp'] = d['life_exp'] - d.exp_gdp
    d['exp_both'] = m3.fittedvalues; d['res_both'] = d['life_exp'] - d.exp_both
    d['rank_gdp'] = d.res_gdp.rank(ascending=False).astype(int)
    d['rank_both'] = d.res_both.rank(ascending=False).astype(int)
    rows.append(dict(year=yr, n=len(d), pearson_lnhx_le=r_hx, spearman_hx_le=rho, R2_hx=m1.rsquared, slope_hx=m1.params['ln_hx'],
                     R2_gdp=m2.rsquared, slope_gdp=m2.params['ln_gdp'], R2_both=m3.rsquared,
                     b_hx_both=m3.params['ln_hx'], p_hx_both=m3.pvalues['ln_hx'], b_gdp_both=m3.params['ln_gdp'], p_gdp_both=m3.pvalues['ln_gdp'],
                     resid_sd_gdp=d.res_gdp.std(), resid_sd_both=d.res_both.std()))
    res[yr] = d
pd.DataFrame(rows).to_csv(f'{OUT}/model_summary.csv', index=False)
print(pd.DataFrame(rows).T.to_string())

d = res[2023]
cols = ['Country Name', 'Country Code', 'Region', 'IncomeGroup', 'life_exp', 'hx', 'gdp', 'exp_gdp', 'res_gdp', 'rank_gdp', 'exp_both', 'res_both', 'rank_both']
d[cols].sort_values('res_gdp', ascending=False).to_csv(f'{OUT}/residuals_2023.csv', index=False)
print('TOP over (income only)\n', d.nlargest(10, 'res_gdp')[cols[:1] + ['life_exp', 'hx', 'gdp', 'exp_gdp', 'res_gdp', 'res_both']].round(1).to_string())
print('TOP under\n', d.nsmallest(10, 'res_gdp')[cols[:1] + ['life_exp', 'hx', 'gdp', 'exp_gdp', 'res_gdp', 'res_both']].round(1).to_string())
print('over both\n', d.nlargest(10, 'res_both')[['Country Name', 'life_exp', 'hx', 'gdp', 'res_both', 'res_gdp']].round(1).to_string())
print('under both\n', d.nsmallest(10, 'res_both')[['Country Name', 'life_exp', 'hx', 'gdp', 'res_both', 'res_gdp']].round(1).to_string())

# robustness: rank stability across years for top/bottom
for yr in [2022, 2019]:
    x = res[yr].set_index('Country Code')
    top = d.nlargest(10, 'res_gdp')['Country Code']; bot = d.nsmallest(10, 'res_gdp')['Country Code']
    print(yr, 'top10 2023 still top20 in', yr, ':', int((x.loc[x.index.intersection(top), 'rank_gdp'] <= 20).sum()),
          '| bottom10 still bottom20:', int((x.loc[x.index.intersection(bot), 'rank_gdp'] > len(x) - 20).sum()),
          '| corr resid', np.corrcoef(d.set_index('Country Code').res_gdp.reindex(x.index).fillna(0), x.res_gdp)[0, 1].round(3))
# Rank-spearman of residuals across years
from scipy.stats import spearmanr
a = d.set_index('Country Code').res_gdp
for yr in [2022, 2019]:
    b = res[yr].set_index('Country Code').res_gdp; j = a.index.intersection(b.index)
    print('spearman resid 2023 vs', yr, spearmanr(a[j], b[j])[0].round(3))

# Viet Nam
v = d[d['Country Code'] == 'VNM'].iloc[0]
print('VNM 2023', v[cols].to_dict(), 'N', len(d))
for yr in [2022, 2019]:
    x = res[yr]; vv = x[x['Country Code'] == 'VNM'].iloc[0]; print('VNM', yr, vv[['life_exp', 'hx', 'gdp', 'res_gdp', 'rank_gdp', 'res_both', 'rank_both']].to_dict(), len(x))
# nhom thu nhap va so sanh
umi = d[d.IncomeGroup == 'Upper middle income']; print('UMI n', len(umi), 'VN rank in UMI by res_gdp', int((umi.res_gdp > v.res_gdp).sum()) + 1)
reg = d[d.Region == 'East Asia & Pacific']; print(reg.sort_values('res_gdp', ascending=False)[['Country Name', 'life_exp', 'hx', 'gdp', 'res_gdp']].round(1).to_string())
# peers: countries with spending near VN (0.7x - 1.4x)
peer = d[(d.hx > v.hx * 0.7) & (d.hx < v.hx * 1.4)]; print('peers by spend n', len(peer), 'VN le', v['life_exp'], 'peer median le', peer['life_exp'].median(), 'peer le pctile VN', (peer['life_exp'] < v['life_exp']).mean().round(2))
# nhom thu nhap: tuong quan trong nhom
print(d.groupby('IncomeGroup').apply(lambda s: pd.Series({'n': len(s), 'r_lnhx_le': np.corrcoef(s.ln_hx, s['life_exp'])[0, 1], 'median_hx': s.hx.median(), 'median_le': s['life_exp'].median()})).round(2))
# VN ranking among all: chi tieu y te rank
print('VN hx pctile', (d.hx < v.hx).mean().round(3), 'gdp pctile', (d.gdp < v.gdp).mean().round(3), 'le pctile', (d['life_exp'] < v['life_exp']).mean().round(3))
# bao nhieu USD them de +1 nam: gia tri slope
m1 = ols(d, ['ln_hx']); print('slope per doubling hx', m1.params['ln_hx'] * np.log(2))
m3 = ols(d, ['ln_hx', 'ln_gdp']); print('both: per doubling hx', m3.params['ln_hx'] * np.log(2), 'gdp', m3.params['ln_gdp'] * np.log(2))
# sensitivity: bo ngoai le tuoi tho thap do xung dot (<55)
dd = d[d['life_exp'] > 55]; print('excl le<=55 n', len(dd), 'R2 hx', ols(dd, ['ln_hx']).rsquared.round(3), 'slope per doubling', (ols(dd, ['ln_hx']).params['ln_hx'] * np.log(2)).round(2))
# VN xep hang khi dung ca hai kiem soat; kiem soat hx-only
d['res_hx'] = d['life_exp'] - ols(d, ['ln_hx']).fittedvalues; d['rank_hx'] = d.res_hx.rank(ascending=False).astype(int)
print('VN res_hx', d.loc[d['Country Code'] == 'VNM', ['res_hx', 'rank_hx']].values)
d.to_csv(f'{OUT}/data_2023_full.csv', index=False)
res_all = pd.concat(res.values()); res_all[cols + ['year']].to_csv(f'{OUT}/residuals_all_years.csv', index=False)
