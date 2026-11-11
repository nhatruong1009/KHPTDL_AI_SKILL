"""Chi tiêu y tế vs tuổi thọ, có kiểm soát thu nhập. Chạy: python -I outputs/health_spend_life_expectancy/analysis.py"""
import numpy as np, pandas as pd
from pathlib import Path
from scipy import stats


class _Fit:
    def __init__(self, y, X, hc3=False):
        self.cols = list(X.columns); Xv = X.values.astype(float); yv = np.asarray(y, float)
        XtXi = np.linalg.inv(Xv.T @ Xv); b = XtXi @ Xv.T @ yv
        self.params = pd.Series(b, self.cols); self.fitted = Xv @ b; self.resid = pd.Series(yv - self.fitted, index=X.index)
        n, k = Xv.shape; self.rsquared = 1 - (self.resid ** 2).sum() / ((yv - yv.mean()) ** 2).sum()
        if hc3:
            h = np.einsum('ij,jk,ik->i', Xv, XtXi, Xv); u = self.resid.values / (1 - h)
            V = XtXi @ (Xv.T * u ** 2) @ Xv @ XtXi
        else:
            V = XtXi * (self.resid ** 2).sum() / (n - k)
        self.se = pd.Series(np.sqrt(np.diag(V)), self.cols); self.df = n - k
    def conf_int(self):
        t = stats.t.ppf(.975, self.df); return pd.DataFrame({0: self.params - t * self.se, 1: self.params + t * self.se})
    def predict(self, X): return pd.Series(X.values.astype(float) @ self.params.values, index=X.index)
    def summary_txt(self):
        return pd.DataFrame({'coef': self.params, 'se': self.se, 't': self.params / self.se}).round(3).to_string()


class sm:
    @staticmethod
    def add_constant(X): 
        X = X.copy(); X.insert(0, 'const', 1.0); return X
    @staticmethod
    def OLS(y, X): return _OLS(y, X)


class _OLS:
    def __init__(self, y, X): self.y, self.X = y, X
    def fit(self, cov_type=None): return _Fit(self.y, self.X, hc3=(cov_type == 'HC3'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

OUT = Path('outputs/health_spend_life_expectancy')
D = Path('data')
YEAR = '2023'  # năm mới nhất có đủ dữ liệu chi tiêu y tế


def load(sub, name):
    f = list((D / sub).glob('API_*'))[0]
    x = pd.read_csv(f, skiprows=4, encoding='utf-8-sig')
    return x.set_index('Country Code')


def meta():
    f = list((D / 'life_expectancy').glob('Metadata_Country*'))[0]
    return pd.read_csv(f, encoding='utf-8-sig').set_index('Country Code')


le = load('life_expectancy', 'le'); he = load('health_expenditure_per_capita', 'he'); gd = load('gdp_per_capita_ppp', 'gd')
m = meta()


def build(year):
    df = pd.DataFrame({'country': le['Country Name'], 'lifeexp': le[year], 'he': he[year], 'gdp': gd[year]})
    df = df.join(m[['Region', 'IncomeGroup']])
    df = df[df['Region'].notna()]  # loại các nhóm tổng hợp (khu vực, thu nhập...)
    n0 = len(df)
    df = df.dropna(subset=['lifeexp', 'he', 'gdp'])
    df['lhe'] = np.log(df.he); df['lgdp'] = np.log(df.gdp)
    return df, n0


df, n0 = build(YEAR)
print('Quốc gia/vùng lãnh thổ:', n0, '| đủ cả 3 chỉ số:', len(df))

# 1) Tương quan thô
r_raw, p_raw = stats.pearsonr(df.lhe, df.lifeexp)
rho, _ = stats.spearmanr(df.he, df.lifeexp)
r_inc, _ = stats.pearsonr(df.lgdp, df.lifeexp)
print(f'r(log HE, LE)={r_raw:.3f} p={p_raw:.1e}; Spearman={rho:.3f}; r(log GDP, LE)={r_inc:.3f}')

# 2) Mô hình
X1 = sm.add_constant(df[['lhe']]); m1 = sm.OLS(df.lifeexp, X1).fit()
X2 = sm.add_constant(df[['lgdp']]); m2 = sm.OLS(df.lifeexp, X2).fit()
X3 = sm.add_constant(df[['lgdp', 'lhe']]); m3 = sm.OLS(df.lifeexp, X3).fit(cov_type='HC3')
print('M1 LE~logHE R2=%.3f slope=%.2f' % (m1.rsquared, m1.params['lhe']))
print('M2 LE~logGDP R2=%.3f slope=%.2f' % (m2.rsquared, m2.params['lgdp']))
print('M3 LE~logGDP+logHE R2=%.3f' % sm.OLS(df.lifeexp, X3).fit().rsquared)
print(m3.summary_txt())
# tương quan riêng phần của logHE với LE sau khi loại logGDP
rl = sm.OLS(df.lifeexp, X2).fit().resid; rh = sm.OLS(df.lhe, X2).fit().resid
pr, pp = stats.pearsonr(rh, rl)
print(f'Tương quan riêng phần (HE|GDP) = {pr:.3f} p={pp:.2g}')
ci = m3.conf_int().loc['lhe'].values
print('Hệ số logHE (M3): %.2f, CI95 [%.2f, %.2f]; => +10%% chi tiêu ~ %+.2f năm' % (m3.params['lhe'], ci[0], ci[1], m3.params['lhe'] * np.log(1.1)))

# 3) Phần dư: tuổi thọ kỳ vọng theo thu nhập (M2) - kết quả chính
df['expected'] = m2.predict(X2); df['resid'] = df.lifeexp - df.expected
df['resid_se'] = df.resid / m2.resid.std(ddof=2)
df['expected_inc_he'] = sm.OLS(df.lifeexp, X3).fit().predict(X3)
df['resid_inc_he'] = df.lifeexp - df.expected_inc_he
df['rank_over'] = df.resid.rank(ascending=False).astype(int)
cols = ['country', 'IncomeGroup', 'lifeexp', 'he', 'gdp', 'expected', 'resid', 'resid_se', 'resid_inc_he', 'rank_over']
df.sort_values('resid', ascending=False)[cols].round(2).to_csv(OUT / 'residuals_all_countries.csv', index=False, encoding='utf-8-sig')
top = df.sort_values('resid', ascending=False)[cols].head(10).round(2)
bot = df.sort_values('resid')[cols].head(10).round(2)
top.to_csv(OUT / 'top10_over.csv', index=False, encoding='utf-8-sig'); bot.to_csv(OUT / 'top10_under.csv', index=False, encoding='utf-8-sig')
print(top.to_string()); print(bot.to_string())

# 4) Việt Nam
v = df.loc['VNM']
print('VNM:', v[cols].to_dict(), 'n=', len(df))
print('VNM hạng chi tiêu y tế/người (cao->thấp): %d; GDP: %d; tuổi thọ: %d' % (
    df.he.rank(ascending=False)['VNM'], df.gdp.rank(ascending=False)['VNM'], df.lifeexp.rank(ascending=False)['VNM']))
print('VNM hạng phần dư M3 (thu nhập + chi tiêu):', int(df.resid_inc_he.rank(ascending=False)['VNM']), 'resid', round(v.resid_inc_he, 2))
# so sánh nhóm thu nhập trung bình thấp/cao
for g in ['Lower middle income', 'Upper middle income']:
    s = df[df.IncomeGroup == g]
    print(g, len(s), 'resid VN percentile:', round((s.resid < v.resid).mean() * 100, 1), 'median he', s.he.median().round(0))
# lân cận thu nhập: ±25% GDP
nb = df[(df.gdp > v.gdp * .75) & (df.gdp < v.gdp * 1.25)]
print('Nước thu nhập tương đương (±25%% GDP): n=%d, LE trung vị %.1f, HE trung vị %.0f; VN LE %.1f HE %.0f' % (len(nb), nb.lifeexp.median(), nb.he.median(), v.lifeexp, v.he))
nb[['country', 'lifeexp', 'he', 'gdp', 'resid']].sort_values('resid', ascending=False).round(1).to_csv(OUT / 'vietnam_income_peers.csv', index=False, encoding='utf-8-sig')

# 5) Độ vững: bootstrap vị trí VN; năm 2019 (trước COVID); bỏ nước nhỏ (cần HE/GDP chung)
rng = np.random.default_rng(0); ranks = []; resids = []
for _ in range(2000):
    s = df.sample(len(df), replace=True, random_state=int(rng.integers(1e9)))
    mm = sm.OLS(s.lifeexp, sm.add_constant(s[['lgdp']])).fit()
    pv = df.lifeexp['VNM'] - (mm.params['const'] + mm.params['lgdp'] * df.lgdp['VNM'])
    allr = df.lifeexp - (mm.params['const'] + mm.params['lgdp'] * df.lgdp)
    ranks.append((allr > pv).sum() + 1); resids.append(pv)
print('Bootstrap VN: phần dư 95%% CI [%.2f, %.2f]; hạng 95%% CI [%d, %d]' % (*np.percentile(resids, [2.5, 97.5]), *np.percentile(ranks, [2.5, 97.5])))
d19, _ = build('2019')
m19 = sm.OLS(d19.lifeexp, sm.add_constant(d19[['lgdp']])).fit(); d19['resid'] = m19.resid
print('2019: n=%d, VN resid=%.2f, hạng %d' % (len(d19), d19.resid['VNM'], d19.resid.rank(ascending=False)['VNM']))
print('2019 top5:', d19.resid.sort_values(ascending=False).head(5).round(1).to_dict())
r19 = pd.concat([df.resid, d19.resid], axis=1, keys=['2023', '2019']).dropna()
print('Tương quan phần dư 2019 vs 2023: %.2f' % r19.corr().iloc[0, 1])
pd.DataFrame({'metric': ['n', 'r_raw', 'rho', 'r_gdp', 'partial_r', 'beta_logHE_M3', 'beta_lo', 'beta_hi', 'R2_M1', 'R2_M2', 'VN_resid', 'VN_rank', 'VN_boot_rank_lo', 'VN_boot_rank_hi'],
              'value': [len(df), r_raw, rho, r_inc, pr, m3.params['lhe'], ci[0], ci[1], m1.rsquared, m2.rsquared, v.resid, v.rank_over, np.percentile(ranks, 2.5), np.percentile(ranks, 97.5)]}).round(3).to_csv(OUT / 'summary_stats.csv', index=False)

# 6) Biểu đồ
fnames = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams['font.family'] = 'DejaVu Sans'
BLUE, GREY, RED, ORG = '#2a6f97', '#b8bec4', '#c0392b', '#e08a1e'

# Hình 1: chi tiêu y tế vs tuổi thọ
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(df.he, df.lifeexp, s=22, c=GREY, edgecolor='none')
xs = np.linspace(df.lhe.min(), df.lhe.max(), 100)
ax.plot(np.exp(xs), m1.params['const'] + m1.params['lhe'] * xs, c=BLUE, lw=2)
ax.scatter(v.he, v.lifeexp, s=90, c=RED, zorder=5); ax.annotate('Việt Nam', (v.he, v.lifeexp), xytext=(8, -16), textcoords='offset points', color=RED, fontweight='bold')
ax.set_xscale('log'); ax.set_xlabel('Chi tiêu y tế bình quân đầu người, %s (US$ hiện hành, thang log)' % YEAR); ax.set_ylabel('Tuổi thọ khi sinh (năm)')
ax.set_title('Nước chi y tế nhiều hơn thường sống thọ hơn (r = %.2f, n = %d)' % (r_raw, len(df)), loc='left', fontsize=12, fontweight='bold')
ax.spines[['top', 'right']].set_visible(False); fig.tight_layout(); fig.savefig(OUT / 'fig1_spend_vs_le.png', dpi=150); plt.close()

# Hình 2: tuổi thọ vs GDP, nhãn vượt/dưới kỳ vọng
fig, ax = plt.subplots(figsize=(10, 6.5))
ax.scatter(df.gdp, df.lifeexp, s=22, c=GREY, edgecolor='none')
xs = np.linspace(df.lgdp.min(), df.lgdp.max(), 100)
ax.plot(np.exp(xs), m2.params['const'] + m2.params['lgdp'] * xs, c=BLUE, lw=2, label='Tuổi thọ kỳ vọng theo thu nhập')
for sub, c in [(df.nlargest(6, 'resid'), '#1b7f5c'), (df.nsmallest(6, 'resid'), ORG)]:
    ax.scatter(sub.gdp, sub.lifeexp, s=40, c=c, zorder=4)
    for _, r in sub.iterrows():
        ax.annotate(r.country, (r.gdp, r.lifeexp), xytext=(4, 3), textcoords='offset points', fontsize=8, color=c)
ax.scatter(v.gdp, v.lifeexp, s=90, c=RED, zorder=5); ax.annotate('Việt Nam', (v.gdp, v.lifeexp), xytext=(-8, 12), textcoords='offset points', color=RED, fontweight='bold', ha='right')
ax.set_xscale('log'); ax.set_xlabel('GDP bình quân đầu người, PPP, %s (int-$ hiện hành, thang log)' % YEAR); ax.set_ylabel('Tuổi thọ khi sinh (năm)')
ax.set_title('Việt Nam sống thọ hơn %.1f năm so với mức kỳ vọng theo thu nhập' % v.resid, loc='left', fontsize=12, fontweight='bold')
ax.legend(frameon=False, loc='lower right'); ax.spines[['top', 'right']].set_visible(False); fig.tight_layout(); fig.savefig(OUT / 'fig2_income_adjusted.png', dpi=150); plt.close()

# Hình 3: top/bottom phần dư
sel = pd.concat([df.nlargest(10, 'resid'), df.nsmallest(10, 'resid')]).sort_values('resid')
fig, ax = plt.subplots(figsize=(8.5, 7))
colors = ['#1b7f5c' if r > 0 else ORG for r in sel.resid]
ax.barh(sel.country, sel.resid, color=colors)
ax.set_xlabel('Chênh lệch so với tuổi thọ kỳ vọng theo thu nhập (năm)'); ax.axvline(0, c='k', lw=.8)
ax.set_title('10 nước vượt và 10 nước dưới kỳ vọng nhiều nhất', loc='left', fontsize=12, fontweight='bold')
ax.spines[['top', 'right']].set_visible(False); fig.tight_layout(); fig.savefig(OUT / 'fig3_top_bottom.png', dpi=150); plt.close()
