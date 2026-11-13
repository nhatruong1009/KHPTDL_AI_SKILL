import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

O = '/root/.cache/skill-bench/runs/ab-vi/sonnet__noskills/worldbank_health/r1/workspace/outputs/'
d = pd.read_csv(O + 'data_2023.csv')


def ols(X, y):
    X = np.column_stack([np.ones(len(X)), X])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    return b, y - X @ b, X @ b


# mô hình chỉ theo thu nhập (trả lời "sau khi tính đến thu nhập")
b2, r2, p2 = ols(d[['lgdp']].values, d['LE'].values)
d['pred_inc'] = p2
d['resid_inc'] = r2
print('income-only coef', b2, 'R2', 1 - (r2 ** 2).sum() / ((d.LE - d.LE.mean()) ** 2).sum(), 'sd', r2.std(ddof=2))
d['rank_inc'] = d.resid_inc.rank(ascending=False).astype(int)
d['rank_inc_spend'] = d.resid.rank(ascending=False).astype(int)
d.sort_values('resid_inc', ascending=False).to_csv(O + 'residuals_2023.csv', index=False)
cols = ['Country Name', 'LE', 'he', 'gdp', 'pred_inc', 'resid_inc']
print(d.sort_values('resid_inc', ascending=False)[cols].head(10).round(1).to_string())
print(d.sort_values('resid_inc')[cols].head(10).round(1).to_string())
v = d[d['Country Code'] == 'VNM'].iloc[0]
print(v[cols + ['rank_inc', 'rank_inc_spend']])
print('n', len(d), 'share |res|>1sd', (d.resid_inc.abs() > d.resid_inc.std()).mean())
# nhóm thu nhập tương đương VN: thứ hạng trong upper-middle
um = d[d.IncomeGroup == 'Upper middle income']
print('UMIC n', len(um), 'VN rank', int(um.resid_inc.rank(ascending=False)[v.name]))
# nước chi tiêu thấp hơn VN nhưng sống lâu hơn?
print('LE > VN and he < VN:', d[(d.LE > v.LE) & (d.he < v.he)][['Country Name', 'LE', 'he']].round(1).to_string())
print('he<=VN and gdp>=VN count', len(d[(d.he < v.he)]), 'share he below VN', (d.he < v.he).mean())

plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.spines.top': False, 'axes.spines.right': False})
BL, GR, RD, OR = '#2a6fb0', '#b8bec6', '#c0392b', '#e08a1e'

# Biểu đồ 1: chi tiêu y tế vs tuổi thọ
fig, ax = plt.subplots(figsize=(9, 5.6))
ax.scatter(d.he, d.LE, s=22, color=GR, alpha=.85, linewidths=0)
xs = np.linspace(np.log(d.he.min()), np.log(d.he.max()), 100)
b1 = np.polyfit(np.log(d.he), d.LE, 1)
ax.plot(np.exp(xs), np.polyval(b1, xs), color=BL, lw=2)
ax.scatter([v.he], [v.LE], s=80, color=RD, zorder=5)
ax.annotate('Việt Nam', (v.he, v.LE), xytext=(8, -16), textcoords='offset points', color=RD, fontweight='bold')
for nm in ['United States', 'Japan', 'Nigeria', 'Maldives', 'Sri Lanka']:
    r = d[d['Country Name'] == nm]
    if len(r):
        r = r.iloc[0]
        ax.annotate(nm, (r.he, r.LE), xytext=(5, 4), textcoords='offset points', fontsize=8, color='#444')
ax.set_xscale('log')
ax.set_xticks([30, 100, 300, 1000, 3000, 10000])
ax.set_xticklabels(['30', '100', '300', '1.000', '3.000', '10.000'])
ax.set_xlabel('Chi tiêu y tế bình quân đầu người, 2023 (USD hiện hành, thang log)')
ax.set_ylabel('Tuổi thọ khi sinh (năm)')
ax.set_title('Chi tiêu y tế cao hơn đi cùng tuổi thọ cao hơn — nhưng lợi ích giảm dần', loc='left', fontsize=12, fontweight='bold')
ax.text(0.01, 0.02, 'Mỗi lần chi gấp đôi ≈ +2,5 năm tuổi thọ (chưa kiểm soát thu nhập). n = %d nước' % len(d), transform=ax.transAxes, fontsize=8.5, color='#555')
fig.tight_layout()
fig.savefig(O + 'chart1_chi_tieu_vs_tuoi_tho.png', dpi=150)
plt.close(fig)

# Biểu đồ 2: phần dư theo thu nhập
top = d.nlargest(8, 'resid_inc')
bot = d.nsmallest(8, 'resid_inc')
sel = pd.concat([top, bot])
if 'VNM' not in sel['Country Code'].values:
    sel = pd.concat([sel, d[d['Country Code'] == 'VNM']])
sel = sel.sort_values('resid_inc')
fig, ax = plt.subplots(figsize=(9, 6.6))
cl = [RD if c == 'VNM' else (BL if x > 0 else OR) for c, x in zip(sel['Country Code'], sel.resid_inc)]
ax.barh(sel['Country Name'].replace({'Viet Nam': 'Việt Nam', 'Naoero': 'Nauru'}), sel.resid_inc, color=cl)
for i, x in enumerate(sel.resid_inc):
    ax.text(x + (.3 if x > 0 else -.3), i, '%+.1f' % x, va='center', ha='left' if x > 0 else 'right', fontsize=8.5)
ax.axvline(0, color='#333', lw=.8)
ax.set_xlabel('Tuổi thọ thực tế trừ tuổi thọ kỳ vọng theo GDP/người PPP (năm), 2023')
ax.set_title('Vượt / dưới kỳ vọng nhiều nhất sau khi tính đến thu nhập', loc='left', fontsize=12, fontweight='bold')
ax.margins(x=.12)
fig.tight_layout()
fig.savefig(O + 'chart2_vuot_duoi_ky_vong.png', dpi=150)
plt.close(fig)

# Biểu đồ 3: tuổi thọ vs GDP với VN
fig, ax = plt.subplots(figsize=(9, 5.6))
ax.scatter(d.gdp, d.LE, s=22, color=GR, alpha=.85, linewidths=0)
xs = np.linspace(np.log(d.gdp.min()), np.log(d.gdp.max()), 100)
ax.plot(np.exp(xs), b2[0] + b2[1] * xs, color=BL, lw=2, label='Tuổi thọ kỳ vọng theo thu nhập')
ax.scatter([v.gdp], [v.LE], s=80, color=RD, zorder=5)
ax.annotate('Việt Nam (+%.1f năm)' % v.resid_inc, (v.gdp, v.LE), xytext=(-10, 14), textcoords='offset points', color=RD, fontweight='bold', ha='right')
ax.set_xscale('log')
ax.set_xticks([1000, 3000, 10000, 30000, 100000])
ax.set_xticklabels(['1.000', '3.000', '10.000', '30.000', '100.000'])
ax.set_xlabel('GDP bình quân đầu người PPP, 2023 (USD quốc tế hiện hành, thang log)')
ax.set_ylabel('Tuổi thọ khi sinh (năm)')
ax.set_title('Việt Nam sống lâu hơn mức kỳ vọng theo thu nhập', loc='left', fontsize=12, fontweight='bold')
ax.legend(frameon=False, loc='lower right')
fig.tight_layout()
fig.savefig(O + 'chart3_tuoi_tho_vs_gdp.png', dpi=150)
plt.close(fig)
