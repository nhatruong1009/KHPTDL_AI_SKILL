import os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.dirname(__file__)
d = pd.read_csv(f'{OUT}/data_2023_full.csv')
v = d[d['Country Code'] == 'VNM'].iloc[0]
plt.rcParams.update({'axes.spines.top': False, 'axes.spines.right': False, 'font.size': 10})
GREY, BLUE, RED, ORG = '#b8b8b8', '#1f77b4', '#d62728', '#ff7f0e'

# Chart 1: chi tieu y te vs tuoi tho
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(d.hx, d.life_exp, s=22, c=GREY, alpha=.8)
b = np.polyfit(d.ln_hx, d.life_exp, 1); xs = np.logspace(np.log10(d.hx.min()), np.log10(d.hx.max()), 100)
ax.plot(xs, b[1] + b[0] * np.log(xs), c=BLUE, lw=2)
ax.scatter(v.hx, v.life_exp, s=90, c=RED, zorder=5); ax.annotate(f'Việt Nam ({v.life_exp:.1f} tuổi; {v.hx:.0f} US$)', (v.hx, v.life_exp), xytext=(v.hx * 1.5, v.life_exp - 9), arrowprops=dict(arrowstyle='-', color=RED), color=RED, fontweight='bold')
ax.set_xscale('log'); ax.set_xlabel('Chi tiêu y tế bình quân đầu người, 2023 (US$ hiện hành, thang log)'); ax.set_ylabel('Tuổi thọ trung bình khi sinh (năm)')
ax.set_title('Chi tiêu y tế cao hơn đi cùng tuổi thọ cao hơn, nhưng lợi ích tăng chậm dần\n(mỗi lần chi gấp đôi: +2,5 năm tuổi thọ, tương quan; R² = 0,69)', loc='left', fontsize=11, fontweight='bold')
ax.text(0, -0.13, f'Nguồn: World Bank WDI, WHO GHED. n = {len(d)} quốc gia/vùng lãnh thổ có đủ dữ liệu 2023.', transform=ax.transAxes, fontsize=8, color='#555')
fig.savefig(f'{OUT}/chart1_spend_vs_life.png', dpi=150, bbox_inches='tight'); plt.close()

# Chart 2: thu nhap vs tuoi tho, dánh dau vuot/duoi ky vong
fig, ax = plt.subplots(figsize=(10, 6.5))
ax.scatter(d.gdp, d.life_exp, s=22, c=GREY, alpha=.8)
b = np.polyfit(d.ln_gdp, d.life_exp, 1); xs = np.logspace(np.log10(d.gdp.min()), np.log10(d.gdp.max()), 100)
ax.plot(xs, b[1] + b[0] * np.log(xs), c=BLUE, lw=2, label='Tuổi thọ kỳ vọng theo thu nhập')
top = d.nlargest(6, 'res_gdp'); bot = d.nsmallest(6, 'res_gdp')
vi = {'Solomon Islands': 'Quần đảo Solomon', 'Jordan': 'Jordan', 'Lebanon': 'Liban', 'Malawi': 'Malawi', 'Maldives': 'Maldives', 'Vanuatu': 'Vanuatu',
      'Nigeria': 'Nigeria', 'Naoero': 'Nauru', 'Equatorial Guinea': 'Guinea Xích đạo', 'Guyana': 'Guyana', 'Chad': 'Chad', 'Eswatini': 'Eswatini'}
ax.scatter(top.gdp, top.life_exp, s=45, c=ORG, label='Vượt kỳ vọng nhiều nhất'); ax.scatter(bot.gdp, bot.life_exp, s=45, c='#7b3294', label='Dưới kỳ vọng nhiều nhất')
for _, r in pd.concat([top, bot]).iterrows():
    ax.annotate(vi.get(r['Country Name'], r['Country Name']), (r.gdp, r.life_exp), xytext=(4, 4), textcoords='offset points', fontsize=8)
ax.scatter(v.gdp, v.life_exp, s=100, c=RED, zorder=5); ax.annotate(f'Việt Nam: +{v.res_gdp:.1f} năm', (v.gdp, v.life_exp), xytext=(v.gdp * 1.4, v.life_exp - 7), arrowprops=dict(arrowstyle='-', color=RED), color=RED, fontweight='bold')
ax.set_xscale('log'); ax.set_xlabel('GDP bình quân đầu người, 2023 (PPP, US$ quốc tế hiện hành, thang log)'); ax.set_ylabel('Tuổi thọ trung bình khi sinh (năm)')
ax.set_title('Sau khi tính đến thu nhập, Việt Nam sống thọ hơn kỳ vọng khoảng 1,9 năm\n(Nigeria thấp hơn kỳ vọng 15,3 năm; Quần đảo Solomon cao hơn 7,2 năm)', loc='left', fontsize=11, fontweight='bold')
ax.legend(frameon=False, loc='lower right')
ax.text(0, -0.12, f'Nguồn: World Bank WDI. n = {len(d)}. Kỳ vọng = hồi quy tuổi thọ theo ln(GDP PPP/người).', transform=ax.transAxes, fontsize=8, color='#555')
fig.savefig(f'{OUT}/chart2_over_under.png', dpi=150, bbox_inches='tight'); plt.close()

# Chart 3: thanh nhung nuoc vuot / duoi ky vong (top 10 moi phia + VN)
sel = pd.concat([d.nlargest(10, 'res_gdp'), d[d['Country Code'] == 'VNM'], d.nsmallest(10, 'res_gdp')]).sort_values('res_gdp')
fig, ax = plt.subplots(figsize=(8, 8))
cols = [RED if c == 'VNM' else (ORG if x > 0 else '#7b3294') for c, x in zip(sel['Country Code'], sel.res_gdp)]
labs = [vi.get(n, {'Cabo Verde': 'Cabo Verde', 'Nicaragua': 'Nicaragua', 'Sri Lanka': 'Sri Lanka', 'Tajikistan': 'Tajikistan', 'Viet Nam': 'Việt Nam', "Cote d'Ivoire": "Côte d'Ivoire", 'South Africa': 'Nam Phi', 'Lesotho': 'Lesotho', 'Brunei Darussalam': 'Brunei'}.get(n, n)) for n in sel['Country Name']]
ax.barh(labs, sel.res_gdp, color=cols)
for i, x in enumerate(sel.res_gdp): ax.text(x + (.2 if x > 0 else -.2), i, f'{x:+.1f}', va='center', ha='left' if x > 0 else 'right', fontsize=8)
ax.axvline(0, c='k', lw=.8); ax.set_xlabel('Chênh lệch tuổi thọ thực tế so với kỳ vọng theo thu nhập (năm)'); ax.set_xlim(-18, 10)
ax.set_title('10 nước vượt và 10 nước dưới kỳ vọng nhiều nhất, 2023', loc='left', fontweight='bold')
fig.text(0.01, 0.01, f'Nguồn: World Bank WDI. n = {len(d)}.', fontsize=8, color='#555')
fig.savefig(f'{OUT}/chart3_residual_ranking.png', dpi=150, bbox_inches='tight'); plt.close()
