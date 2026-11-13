import pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style='whitegrid')
O = 'outputs/revenue_2011_vs_2010/'
GREY, RED, GREEN, BLUE = '#9aa0a6', '#d1495b', '#2a9d8f', '#1f77b4'

# 1) Cầu nối doanh thu
b = pd.read_csv(O + 'bridge.csv')
lab = ['2010\n(1/1-8/12)', 'Khách 2010\nkhông quay lại', 'Khách cũ giữ lại:\nchi tiêu giảm',
       'Khách cũ quay lại\ntừ 12/2009', 'Khách mới\n2011', 'Giao dịch không\ncó Customer ID', '2011\n(1/1-8/12)']
v = b['giá trị'].values / 1e6
fig, ax = plt.subplots(figsize=(11, 5.5))
cum = 0
for i, x in enumerate(v):
    if i in (0, len(v) - 1):
        ax.bar(i, x, color=GREY); top = x; cum = x if i == 0 else cum
        ax.text(i, x + .05, f'{x:.2f}M', ha='center', fontweight='bold')
    else:
        ax.bar(i, x, bottom=cum, color=GREEN if x > 0 else RED)
        ax.text(i, max(cum, cum + x) + .05, f'{x:+.2f}M', ha='center')
        cum += x
ax.set_xticks(range(len(v))); ax.set_xticklabels(lab, fontsize=9)
ax.set_ylim(0, 10.5); ax.set_ylabel('Doanh thu thuần (triệu GBP)')
ax.set_title('Doanh thu thuần 2011 chỉ +2,9% so với 2010: khách mới (+1,44M) vừa đủ bù khách cũ bỏ đi và chi ít hơn', fontsize=11, loc='left')
fig.text(0.01, -0.02, 'Cùng kỳ 01/01-08/12 mỗi năm; đã bỏ trùng, bỏ mã phi hàng hoá. Nguồn: online_retail_II.xlsx', fontsize=8, color='gray')
for s in ['top', 'right']: ax.spines[s].set_visible(False)
fig.savefig(O + 'chart1_bridge.png', dpi=150, bbox_inches='tight'); plt.close()

# 2) Đóng góp theo thị trường
c = pd.read_csv(O + 'country_contrib.csv')
sel = pd.concat([c.head(6), c.tail(6)]).drop_duplicates('Country').sort_values('delta')
fig, ax = plt.subplots(figsize=(9, 6))
cols = [RED if x < 0 else GREEN for x in sel.delta]
ax.barh(sel.Country, sel.delta / 1e3, color=cols)
for y, (d_, p) in enumerate(zip(sel.delta, sel.pct)):
    ax.text(d_ / 1e3 + (3 if d_ > 0 else -3), y, f'{d_/1e3:+.0f}k ({p:+.0%})', va='center', ha='left' if d_ > 0 else 'right', fontsize=9)
ax.set_xlim(-130, 150); ax.axvline(0, color='k', lw=.8)
ax.set_xlabel('Thay đổi doanh thu thuần 2011 so với 2010 (nghìn GBP)')
ax.set_title('Úc (+106k), Pháp (+63k) kéo tăng; Ireland (-78k) và Đan Mạch (-27k) kéo giảm', fontsize=11, loc='left')
fig.text(0.01, -0.02, 'Cùng kỳ 01/01-08/12. Úc: 1 khách (12415) chiếm 124k/136k.', fontsize=8, color='gray')
for s in ['top', 'right']: ax.spines[s].set_visible(False)
fig.savefig(O + 'chart2_countries.png', dpi=150, bbox_inches='tight'); plt.close()

# 3) Giữ chân: chi tiêu TB theo nhóm
r = pd.read_csv(O + 'retention_stats.csv').iloc[0]
names = ['Khách mới 2011', 'Khách 2010\nkhông quay lại', 'Khách 2010 giữ lại\n(năm 2010)', 'Khách 2010 giữ lại\n(năm 2011)']
vals = [r['chi tiêu TB khách mới'], r['chi tiêu TB khách không quay lại (2010)'],
        r['chi tiêu TB khách giữ lại 2010'], r['chi tiêu TB khách giữ lại 2011']]
fig, ax = plt.subplots(figsize=(8.5, 5))
ax.bar(names, vals, color=[BLUE, GREY, GREEN, GREEN])
for i, x in enumerate(vals): ax.text(i, x + 40, f'{x:,.0f}', ha='center', fontweight='bold')
ax.set_ylabel('Chi tiêu thuần TB / khách (GBP)')
ax.set_title(f'Khách giữ lại chi gấp ~2,5 lần khách mới; chỉ {r["tỉ lệ giữ chân"]:.0%} khách 2010 quay lại 2011', fontsize=11, loc='left')
fig.text(0.01, -0.02, f'Giữ lại {int(r["khách giữ lại"]):,}/{int(r["khách 2010 (có ID)"]):,} khách; mới 2011: {int(r["khách mới 2011"]):,}. Chỉ khách có Customer ID.', fontsize=8, color='gray')
for s in ['top', 'right']: ax.spines[s].set_visible(False)
fig.savefig(O + 'chart3_retention.png', dpi=150, bbox_inches='tight'); plt.close()
