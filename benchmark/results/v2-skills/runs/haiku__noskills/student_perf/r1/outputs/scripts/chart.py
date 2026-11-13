import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv('outputs/long_clean.csv')
main = df[~df.G3_zero]
rows = []
for lvl, g in main.groupby('Walc_s'):
    rows.append({'lvl': int(round(lvl)), 'n': len(g), 'mean': g.G3.mean(),
                 'se': g.G3.std(ddof=1) / np.sqrt(len(g))})
t = pd.DataFrame(rows)

fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
ax.errorbar(t.lvl, t['mean'], yerr=1.96 * t.se, fmt='o-', color='#1f4e79',
            ecolor='#7f9fbf', capsize=4, lw=2)
for _, r in t.iterrows():
    ax.annotate(f"n={r.n}", (r.lvl, r['mean']), textcoords='offset points', xytext=(0, 9),
                ha='center', fontsize=8, color='#444')
ax.set_xticks(t.lvl)
ax.set_xticklabels(['1\nrất ít', '2', '3', '4', '5\nrất nhiều'])
ax.set_xlabel('Mức uống rượu cuối tuần (Walc, 1–5)')
ax.set_ylabel('Điểm cuối kỳ G3 (trung bình, KTC 95%)')
ax.set_title('Điểm G3 giảm theo mức uống rượu cuối tuần\n(Toán + Bồ Đào Nha, bỏ G3 = 0; mỗi cặp học sinh–môn là một quan sát)',
             fontsize=10)
ax.grid(alpha=0.3)
ax.set_ylim(9, 14)
fig.tight_layout()
fig.savefig('outputs/chart_g3_by_walc.png')
print(t.round(2).to_string())
