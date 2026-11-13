"""Vẽ biểu đồ từ các CSV do analysis.py tạo. Chạy: python -I outputs/oulad_early_warning/charts.py"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O = 'outputs/oulad_early_warning'
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
COL = {'Pass': '#2a7f62', 'Fail': '#d1495b', 'Withdrawn': '#e09f3e'}

# 1
g = pd.read_csv(O + '/q1_weekly_by_outcome.csv'); t = pd.read_csv(O + '/q1_tests.csv')
fig, ax = plt.subplots(1, 3, figsize=(15, 4.5))
for o in ['Pass', 'Fail', 'Withdrawn']:
    s = g[g.label3 == o]
    ax[0].plot(s.week, s.clicks_median, marker='o', color=COL[o], label=o)
    ax[1].plot(s.week, s.active_days_median, marker='o', color=COL[o], label=o)
    z = t[t.metric == 'share_zero_clicks']
    ax[2].plot(z.week, z[o] * 100, marker='o', color=COL[o], label=o)
ax[0].set_title('Trung vị số lượt click mỗi tuần'); ax[1].set_title('Trung vị số ngày vào học mỗi tuần (tối đa 7)')
ax[2].set_title('Tỷ lệ sinh viên không click nào trong tuần (%)')
for a in ax: a.set_xlabel('Tuần'); a.set_xticks([1, 2, 3, 4]); a.legend(frameon=False)
ax[0].set_ylabel('Lượt click'); ax[1].set_ylabel('Ngày'); ax[2].set_ylabel('%')
fig.suptitle('Pass luôn tương tác nhiều nhất; Fail thấp nhất ngay từ tuần 1, Withdrawn nằm giữa', fontweight='bold')
fig.tight_layout(); fig.savefig(O + '/q1_tuong_tac_theo_nhom.png', dpi=140); plt.close()

# 2
q2 = pd.read_csv(O + '/q2_indicator_tests.csv').sort_values('cliffs_delta', key=abs).tail(18)
q2w = pd.read_csv(O + '/q2_by_week.csv')
fig, ax = plt.subplots(1, 2, figsize=(14, 5.5), gridspec_kw={'width_ratios': [1.3, 1]})
ax[0].barh(q2.indicator, q2.cliffs_delta, color=['#2a7f62' if v > 0 else '#d1495b' for v in q2.cliffs_delta])
ax[0].axvline(0, color='k', lw=.8); ax[0].axvline(.1, color='grey', ls=':'); ax[0].axvline(-.1, color='grey', ls=':')
ax[0].set_title('Mức khác biệt (Cliff\'s delta) giữa hoàn thành và không hoàn thành\n(dương = nhóm hoàn thành cao hơn; đường chấm = ngưỡng ±0,1)')
ax[0].set_xlabel("Cliff's delta")
for met, lab, c in [('clicks', 'Click trong tuần', '#4c78a8'), ('active_days', 'Ngày vào học trong tuần', '#e09f3e'),
                    ('cum_clicks', 'Click tích lũy', '#2a7f62'), ('cum_days', 'Ngày vào học tích lũy', '#7b4f9e')]:
    s = q2w[q2w.metric == met]
    ax[1].plot(s.week, s.cliffs_delta, marker='o', label=lab, color=c)
ax[1].set_xticks([1, 2, 3, 4]); ax[1].set_xlabel('Tuần'); ax[1].set_ylabel("Cliff's delta"); ax[1].set_ylim(0, .4)
ax[1].set_title('Khác biệt đã rõ từ tuần 1 và tăng nhẹ theo tuần'); ax[1].legend(frameon=False)
fig.tight_layout(); fig.savefig(O + '/q2_chi_bao_khac_biet.png', dpi=140); plt.close()

# 3
q3 = pd.read_csv(O + '/q3_model_metrics.csv'); pr = pd.read_csv(O + '/q3_pr_curve_test.csv')
fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
ax[0].plot(pr.recall * 100, pr.precision * 100, color='#4c78a8', lw=2, label='GradientBoosting (tập test 2014J)')
ax[0].axhline(37.8, color='grey', ls=':', label='Tỷ lệ nền 37,8%')
ax[0].axvline(70, color='#d1495b', ls='--', label='Mục tiêu bắt ≥70%')
ax[0].set_xlabel('Tỷ lệ sinh viên không hoàn thành được bắt (recall, %)'); ax[0].set_ylabel('Độ chính xác (precision, %)')
ax[0].set_title('Muốn bắt 70% thì chỉ khoảng một nửa số được gắn cờ là đúng'); ax[0].legend(frameon=False)
tt = q3[q3.split == 'test']; x = np.arange(len(tt)); wd = .38
ax[1].bar(x - wd / 2, tt.recall * 100, wd, label='Recall (%)', color='#2a7f62')
ax[1].bar(x + wd / 2, tt.precision * 100, wd, label='Precision (%)', color='#e09f3e')
for i, (a, b, au) in enumerate(zip(tt.recall, tt.precision, tt.auc)):
    ax[1].text(i - wd / 2, a * 100 + 1, f'{a*100:.0f}', ha='center'); ax[1].text(i + wd / 2, b * 100 + 1, f'{b*100:.0f}', ha='center')
    ax[1].text(i, 3, f'AUC {au:.2f}', ha='center', color='white', fontweight='bold')
ax[1].axhline(70, color='#d1495b', ls='--'); ax[1].set_xticks(x); ax[1].set_xticklabels(tt.model, rotation=10)
ax[1].set_title('Test với ngưỡng chọn trên validation (nhắm recall 70%)'); ax[1].set_ylim(0, 85); ax[1].legend(frameon=False, loc='upper center', ncol=2)
fig.tight_layout(); fig.savefig(O + '/q3_hieu_nang_mo_hinh.png', dpi=140); plt.close()

# 4
q4 = pd.read_csv(O + '/q4_topk.csv'); rules = ['Mô hình (điểm rủi ro)', 'Quy tắc: chưa nộp TMA1 rồi ít click', 'Quy tắc: ít click nhất', 'Ngẫu nhiên (TB 200 lần)']
cl = ['#4c78a8', '#2a7f62', '#e09f3e', '#b0b0b0']
fig, ax = plt.subplots(1, 2, figsize=(13, 4.8), sharey=True)
for a, mod in zip(ax, ['BBB', 'FFF']):
    s = q4[(q4['module'] == mod) & (q4.K == 200)]
    n = int(s.n_noncompleters.iloc[0])
    vals = [s[s.rule == r].hits.iloc[0] for r in rules]
    b = a.bar([r.replace(' (', '\n(').replace(': ', ':\n') for r in rules], vals, color=cl)
    for bi, v in zip(b, vals): a.text(bi.get_x() + bi.get_width() / 2, v + 2, f'{v:.0f}\n({v/200*100:.0f}%)', ha='center')
    a.set_title(f'{mod} 2014J: trúng bao nhiêu trong 200 người liên hệ\n(có {n} sinh viên không hoàn thành; 200 người chỉ phủ tối đa {200/n*100:.0f}%)')
    a.set_ylim(0, 230); a.tick_params(axis='x', labelsize=8)
ax[0].set_ylabel('Số sinh viên thực sự Fail/Withdrawn')
fig.tight_layout(); fig.savefig(O + '/q4_danh_sach_uu_tien_k200.png', dpi=140); plt.close()

# 5
q5 = pd.read_csv(O + '/q5_priority_list_with_explanations.csv')
lab = {'tma1': 'Bài TMA1 (chưa nộp/điểm thấp/muộn)', 'tuan': 'Hoạt động từng tuần thấp/giảm', 'kenh': 'Ít dùng nội dung chính',
       'cuoi': 'Lâu không vào học', 'highest_education_ord': 'Học vấn đầu vào thấp', 'tong': 'Tổng hoạt động thấp', 'studied_credits': 'Nhiều tín chỉ cùng lúc',
       'num_of_prev_attempts': 'Từng học lại', 'truoc': 'Ít hoạt động trước khóa'}
c = pd.concat([q5.top1, q5.top2, q5.top3]).value_counts()
c = c[c.index != ''].sort_values()
top1 = q5.top1.value_counts().reindex(c.index).fillna(0)
fig, ax = plt.subplots(figsize=(9, 4.8))
ax.barh([lab.get(i, i) for i in c.index], c.values, color='#b0c4de', label='Nằm trong 3 lý do hàng đầu')
ax.barh([lab.get(i, i) for i in c.index], top1.values, color='#4c78a8', label='Là lý do số 1')
ax.set_xlabel('Số sinh viên (trong 400 người ưu tiên của 2 module)'); ax.legend(frameon=False, loc='lower right')
ax.set_title('Lý do chính khiến sinh viên vào danh sách ưu tiên')
fig.tight_layout(); fig.savefig(O + '/q5_ly_do_uu_tien.png', dpi=140); plt.close()
print('ok')
