import pandas as pd, numpy as np, matplotlib, json
matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score, average_precision_score, precision_score, recall_score, confusion_matrix
OUT = 'outputs/oulad-early-warning/'
K = ['code_module', 'code_presentation', 'id_student']
m = pd.read_csv('data/aq3_model_table.csv')
aud = pd.read_csv('data/aq3_audit_attributes.csv')
Y = 'target_noncompletion'

# ---------- feature timing audit
audit = [
    ('clicks_w1..w4, active_days_w1..w4, clicks_0_28, active_days_0_28, n_sites, clicks_<loại>_0_28, clicks_change, days_since_last_active_d28', 'ngày 1-28 (log VLE)', 'GIỮ', 'tính từ log đến hết ngày 28'),
    ('clicks_pre_start, active_days_pre_start', 'trước ngày 0', 'GIỮ', 'biết trước ngày 28'),
    ('tma1_submitted_by_d28, tma1_on_time, tma1_days_before_deadline', 'khi nộp bài, <= ngày 28', 'GIỮ', 'chỉ gồm bài nộp trong 28 ngày; tma1_on_time=0 gộp cả "chưa nộp"'),
    ('tma1_score', 'ngày chấm điểm - KHÔNG có trong dữ liệu', 'LOẠI khỏi mô hình chính (chỉ chạy độ nhạy)', 'không kiểm chứng được điểm đã được công bố trước ngày 28 hay chưa'),
    ('registration_lead_days, late_registration_1_28, days_observable_0_28', 'khi đăng ký (<= ngày 28)', 'GIỮ', 'ngày đăng ký đã biết'),
    ('num_of_prev_attempts, studied_credits, seen_in_earlier_presentation', 'trước/lúc đăng ký', 'GIỮ', 'lịch sử đăng ký'),
    ('flag_high_activity', 'định nghĩa không có tài liệu', 'LOẠI', 'dẫn xuất từ clicks (trùng lặp), không rõ cách tạo'),
    ('highest_education_ord', 'lúc đăng ký', 'LOẠI', 'thuộc tính nền tảng cá nhân - tránh dùng ra quyết định về người'),
    ('gender, age_band, disability, imd_band, region (aq3_audit_attributes)', 'lúc đăng ký', 'CHỈ DÙNG KIỂM TOÁN SAI SỐ THEO NHÓM', 'thuộc tính nhạy cảm'),
    ('flag_withdrawn_no_unreg_date, flag_unreg_date_not_withdrawn', 'sau kết quả', 'LOẠI', 'rò rỉ kết quả'),
    ('final_result, label3, date_unregistration', 'sau ngày 28', 'LOẠI', 'là kết quả'),
]
pd.DataFrame(audit, columns=['feature', 'biết khi nào', 'quyết định', 'lý do']).to_csv(OUT + 'feature_timing_audit.csv', index=False)

base = ['clicks_w1', 'clicks_w2', 'clicks_w3', 'clicks_w4', 'active_days_w1', 'active_days_w2', 'active_days_w3', 'active_days_w4',
        'clicks_0_28', 'active_days_0_28', 'n_sites_0_28', 'clicks_change_w1_w4', 'days_since_last_active_d28',
        'clicks_pre_start', 'active_days_pre_start', 'no_vle_activity_0_28',
        'clicks_homepage_0_28', 'clicks_oucontent_0_28', 'clicks_resource_0_28', 'clicks_subpage_0_28',
        'clicks_forumng_0_28', 'clicks_quiz_0_28', 'clicks_url_0_28',
        'tma1_submitted_by_d28', 'tma1_on_time', 'tma1_days_before_deadline',
        'num_of_prev_attempts', 'studied_credits', 'registration_lead_days', 'seen_in_earlier_presentation',
        'late_registration_1_28', 'days_observable_0_28']
cntcols = [c for c in base if c.startswith('clicks_') and c != 'clicks_change_w1_w4'] + \
          ['n_sites_0_28', 'active_days_pre_start']


def prep(df, extra=()):
    X = df[base + list(extra)].copy()
    for c in cntcols:
        X[c] = np.log1p(X[c])
    X['tma1_days_before_deadline'] = X['tma1_days_before_deadline'].fillna(0)  # chưa nộp -> 0, đã có cờ tma1_submitted
    X['registration_lead_days'] = X['registration_lead_days'].fillna(X['registration_lead_days'].median())
    return X


tr, va, te = [m[m.split == s].reset_index(drop=True) for s in ['train', 'validation', 'test']]
print('split sizes/base rate', [(len(x), round(x[Y].mean(), 3)) for x in (tr, va, te)])


def models():
    return {
        'Dummy (tỷ lệ nền)': DummyClassifier(strategy='prior'),
        'Logistic': Pipeline([('imp', SimpleImputer(strategy='median')), ('sc', StandardScaler()),
                              ('m', LogisticRegression(C=0.1, class_weight='balanced', max_iter=2000, random_state=42))]),
        'HistGB': HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200, l2_regularization=1.0,
                                                  class_weight='balanced', random_state=42),
    }


def thr_for_recall(y, s, target=0.70):
    # ngưỡng cao nhất (ít cờ nhất) mà recall >= target trên tập chọn ngưỡng
    o = np.argsort(-s)
    cum = np.cumsum(y[o]) / y.sum()
    i = np.searchsorted(cum, target)
    return s[o][i]


def evaluate(extra=(), tag='main'):
    Xtr, Xva, Xte = prep(tr, extra), prep(va, extra), prep(te, extra)
    rows = []
    fitted = {}
    for n, mod in models().items():
        mod.fit(Xtr, tr[Y])
        fitted[n] = mod
        sva, ste = mod.predict_proba(Xva)[:, 1], mod.predict_proba(Xte)[:, 1]
        t = thr_for_recall(va[Y].values, sva) if n != 'Dummy (tỷ lệ nền)' else 0.5
        for nm, yy, s in [('validation', va[Y].values, sva), ('test', te[Y].values, ste)]:
            pred = (s >= t).astype(int)
            rows.append({'variant': tag, 'model': n, 'set': nm, 'AUC': roc_auc_score(yy, s), 'PR_AUC': average_precision_score(yy, s),
                         'threshold(val, recall>=70%)': t, 'recall': recall_score(yy, pred), 'precision': precision_score(yy, pred, zero_division=0),
                         'flag_rate': pred.mean(), 'base_rate': yy.mean()})
    return pd.DataFrame(rows), fitted, (Xtr, Xva, Xte)


res, fitted, (Xtr, Xva, Xte) = evaluate()
res_s, _, _ = evaluate(extra=['tma1_score'], tag='nhạy: +tma1_score (chưa kiểm chứng thời điểm)')
allres = pd.concat([res, res_s])
allres.to_csv(OUT + 'q3_model_metrics.csv', index=False)
print(allres.round(3).to_string())

# chọn model theo validation AUC (ưu tiên Logistic nếu chênh <= 0.01 vì giải thích được)
v = res[(res.set == 'validation') & (res.model != 'Dummy (tỷ lệ nền)')].set_index('model').AUC
best = 'Logistic' if v['Logistic'] >= v.max() - 0.01 else v.idxmax()
print('chosen', best, v.to_dict())
mod = fitted[best]
sva = mod.predict_proba(Xva)[:, 1]
ste = mod.predict_proba(Xte)[:, 1]
t = thr_for_recall(va[Y].values, sva)
te['score'] = ste
va['score'] = sva
te['flag_thr'] = (ste >= t).astype(int)
cm = confusion_matrix(te[Y], te.flag_thr)
print('test confusion at val-threshold', cm.tolist())
pd.DataFrame(cm, index=['thực: hoàn thành', 'thực: không HT'], columns=['dự báo: không cờ', 'dự báo: cờ']).to_csv(OUT + 'q3_confusion_test.csv')
# thêm: ngưỡng cần để đạt đúng 70% trên test (chỉ để báo cáo, KHÔNG dùng để chọn)
t_oracle = thr_for_recall(te[Y].values, ste)
print('threshold giữ recall 70% trên test (oracle)', t_oracle, 'flag rate', (ste >= t_oracle).mean())
# bootstrap CI cho recall/precision tại ngưỡng validation
rng = np.random.default_rng(42)
bs = []
for _ in range(500):
    i = rng.integers(0, len(te), len(te))
    yy, pp = te[Y].values[i], te.flag_thr.values[i]
    bs.append((recall_score(yy, pp), precision_score(yy, pp), roc_auc_score(yy, ste[i])))
bs = np.array(bs)
ci = pd.DataFrame({'metric': ['recall', 'precision', 'AUC'], 'lo': np.percentile(bs, 2.5, 0), 'hi': np.percentile(bs, 97.5, 0)})
ci.to_csv(OUT + 'q3_test_ci.csv', index=False)
print(ci)

# kiểm toán theo nhóm nhạy cảm (test, cùng ngưỡng)
a = te.merge(aud, on=K)
au = []
for col in ['gender', 'age_band', 'disability', 'imd_band', 'region']:
    for g, x in a.groupby(col):
        if x[Y].sum() < 20:
            continue
        au.append({'attr': col, 'group': g, 'n': len(x), 'noncomp_rate': x[Y].mean(), 'recall': recall_score(x[Y], x.flag_thr),
                   'flag_rate': x.flag_thr.mean(), 'FPR': ((x.flag_thr == 1) & (x[Y] == 0)).sum() / max((x[Y] == 0).sum(), 1)})
au = pd.DataFrame(au)
au.to_csv(OUT + 'q3_fairness_audit_test.csv', index=False)
print(au.round(3).to_string())

# ---------- Q4: top-K trong từng module-kỳ
rules = {
    'Mô hình': lambda x: x.score,
    'Quy tắc: ít ngày hoạt động nhất': lambda x: -x.active_days_0_28 - x.clicks_0_28 * 1e-6,
    'Quy tắc: ít click nhất': lambda x: -x.clicks_0_28,
    'Quy tắc: chưa nộp TMA1, rồi ít click': lambda x: (1 - x.tma1_submitted_by_d28) * 1e6 - x.clicks_0_28,
}
cap_rows = []
lists = {}
for setname, df in [('validation', va), ('test', te)]:
    for K_ in [100, 200, 300]:
        for rn, f in rules.items():
            for (mo, pr), x in df.groupby(['code_module', 'code_presentation']):
                sc = f(x)
                top = x.loc[sc.sort_values(ascending=False).index[:K_]]
                npos = x[Y].sum()
                cap_rows.append({'set': setname, 'K': K_, 'rule': rn, 'mod_pres': mo + pr, 'n_students': len(x), 'n_noncomp': npos,
                                 'base_rate': x[Y].mean(), 'hits': top[Y].sum(), 'precision@K': top[Y].mean(), 'recall': top[Y].sum() / npos,
                                 'lift': top[Y].mean() / x[Y].mean(), 'max_possible_recall': min(K_, npos) / npos})
                if rn == 'Mô hình' and K_ == 200 and setname == 'test':
                    lists[(mo, pr)] = top
cap = pd.DataFrame(cap_rows)
cap.to_csv(OUT + 'q4_capacity_results.csv', index=False)
print(cap[(cap.set == 'test') & (cap.K == 200)].round(3).to_string())
agg = cap.groupby(['set', 'K', 'rule']).agg(n_students=('n_students', 'sum'), n_noncomp=('n_noncomp', 'sum'), hits=('hits', 'sum')).reset_index()
agg['precision'] = agg.hits / (agg.K * 2)
agg['recall'] = agg.hits / agg.n_noncomp
agg['base'] = agg.n_noncomp / agg.n_students
agg.to_csv(OUT + 'q4_capacity_pooled.csv', index=False)
print(agg.round(3).to_string())
# kích thước danh sách cần để đạt recall 70% mỗi module-kỳ (test), xếp theo mô hình
need = []
for (mo, pr), x in te.groupby(['code_module', 'code_presentation']):
    o = x.sort_values('score', ascending=False)
    cum = o[Y].cumsum() / o[Y].sum()
    k70 = int((cum >= 0.7).values.argmax() + 1)
    need.append({'mod_pres': mo + pr, 'n_students': len(x), 'n_noncomp': int(x[Y].sum()), 'k_for_70pct_recall': k70})
need = pd.DataFrame(need)
need.to_csv(OUT + 'q4_list_size_for_70pct_recall.csv', index=False)
print(need)

# ---------- Q5: đóng góp từng đặc trưng (logistic: coef * (x - mean train) trên thang chuẩn hoá)
if best == 'Logistic':
    sc = mod.named_steps['sc']
    lr = mod.named_steps['m']
    imp = mod.named_steps['imp']
    Xt = pd.DataFrame(sc.transform(imp.transform(Xte)), columns=Xte.columns)
    contrib = Xt * lr.coef_[0]
    coef = pd.DataFrame({'feature': Xte.columns, 'coef_std': lr.coef_[0]}).sort_values('coef_std', key=abs, ascending=False)
    coef.to_csv(OUT + 'q3_logistic_coefficients.csv', index=False)
    print(coef.head(15))
    # nhóm đặc trưng dễ hiểu cho cố vấn
    groups = {
        'Lượng tương tác (click) với học liệu online': ['clicks_w1', 'clicks_w2', 'clicks_w3', 'clicks_w4', 'clicks_0_28', 'n_sites_0_28',
                                                         'clicks_homepage_0_28', 'clicks_oucontent_0_28', 'clicks_resource_0_28', 'clicks_subpage_0_28',
                                                         'clicks_forumng_0_28', 'clicks_quiz_0_28', 'clicks_url_0_28', 'no_vle_activity_0_28'],
        'Số ngày vào học / mức đều đặn': ['active_days_w1', 'active_days_w2', 'active_days_w3', 'active_days_w4', 'active_days_0_28'],
        'Gần đây ngừng vào học / xu hướng giảm': ['days_since_last_active_d28', 'clicks_change_w1_w4'],
        'Mức độ chuẩn bị trước khi khóa bắt đầu': ['clicks_pre_start', 'active_days_pre_start', 'registration_lead_days', 'late_registration_1_28', 'days_observable_0_28'],
        'Bài nộp TMA1 (có nộp / đúng hạn)': ['tma1_submitted_by_d28', 'tma1_on_time', 'tma1_days_before_deadline'],
        'Lịch sử học (đã học lại, số tín chỉ)': ['num_of_prev_attempts', 'studied_credits', 'seen_in_earlier_presentation'],
    }
    gc = pd.DataFrame({g: contrib[cols].sum(axis=1) for g, cols in groups.items()})
    gc.index = te.index
    names_feat = {
        'clicks_w1': 'ít click ở tuần 1', 'clicks_w2': 'ít click ở tuần 2', 'clicks_w3': 'ít click ở tuần 3', 'clicks_w4': 'ít click ở tuần 4',
    }
    # top-3 nhóm đóng góp tăng rủi ro, cho danh sách top-200 theo module-kỳ
    outl = []
    for (mo, pr), top in lists.items():
        for idx, r in top.iterrows():
            g = gc.loc[idx].sort_values(ascending=False)
            f = contrib.loc[idx].sort_values(ascending=False)
            outl.append({'code_module': mo, 'code_presentation': pr, 'id_student': r.id_student, 'risk_score': r.score,
                         'rank_in_module_presentation': 0, 'actual_noncompletion': r[Y],
                         'driver1': g.index[0], 'driver1_contrib': g.iloc[0], 'driver2': g.index[1], 'driver2_contrib': g.iloc[1],
                         'driver3': g.index[2], 'driver3_contrib': g.iloc[2],
                         'top_feature': f.index[0], 'clicks_0_28': r.clicks_0_28, 'active_days_0_28': r.active_days_0_28,
                         'tma1_submitted_by_d28': r.tma1_submitted_by_d28, 'days_since_last_active_d28': r.days_since_last_active_d28,
                         'clicks_w4': r.clicks_w4, 'clicks_w1': r.clicks_w1})
    L = pd.DataFrame(outl).sort_values(['code_module', 'code_presentation', 'risk_score'], ascending=[True, True, False])
    L['rank_in_module_presentation'] = L.groupby(['code_module', 'code_presentation']).cumcount() + 1


    def sentence(r):
        parts = []
        for k in (1, 2, 3):
            if r[f'driver{k}_contrib'] <= 0.05:
                continue
            d_ = r[f'driver{k}']
            if d_.startswith('Lượng tương tác'):
                parts.append(f'chỉ có {int(r.clicks_0_28)} lượt click trong 28 ngày đầu (thấp so với phần lớn sinh viên)')
            elif d_.startswith('Số ngày'):
                parts.append(f'chỉ vào học {int(r.active_days_0_28)} ngày trong 28 ngày đầu')
            elif d_.startswith('Gần đây'):
                parts.append(f'đã {int(r.days_since_last_active_d28)} ngày chưa vào học tính đến ngày 28 (tuần 4 chỉ {int(r.clicks_w4)} click)')
            elif d_.startswith('Mức độ chuẩn bị'):
                parts.append('ít chuẩn bị/tiếp cận học liệu trước khi khóa bắt đầu')
            elif d_.startswith('Bài nộp'):
                parts.append('chưa nộp hoặc nộp trễ bài TMA1' if r.tma1_submitted_by_d28 == 0 else 'nộp bài TMA1 sát hạn hoặc trễ')
            else:
                parts.append('có tiền sử học lại hoặc tải tín chỉ cao')
        if not parts:
            return 'Không có yếu tố nổi bật; điểm rủi ro cao do kết hợp nhiều dấu hiệu nhỏ.'
        s = 'Sinh viên được ưu tiên chủ yếu vì ' + '; '.join(parts[:3]) + '.'
        return s + ' Đây là dấu hiệu liên quan đến nguy cơ bỏ học/trượt, không chắc chắn là nguyên nhân; nên liên hệ hỏi thăm khó khăn.'


    L['explanation_vi'] = L.apply(sentence, axis=1)
    L.to_csv(OUT + 'q4_q5_priority_list_test_2014J.csv', index=False)
    print(L.groupby(['code_module', 'driver1']).size())
    print(L.head(3).T)
    # đóng góp trung bình theo nhóm trong list
    L.groupby('driver1').size().rename('n_students_driver1').to_csv(OUT + 'q5_driver1_counts.csv')
else:
    print('chosen model not logistic; skip contrib')

# ---------- charts
sns.set_theme(style='whitegrid')
fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
from sklearn.metrics import roc_curve, precision_recall_curve
for n in ['Logistic', 'HistGB']:
    s_ = fitted[n].predict_proba(Xte)[:, 1]
    fpr, tpr, _ = roc_curve(te[Y], s_)
    ax[0].plot(fpr, tpr, label=f'{n} (AUC={roc_auc_score(te[Y], s_):.3f})', lw=2)
ax[0].plot([0, 1], [0, 1], 'k--', lw=.8, label='Ngẫu nhiên')
ax[0].set_xlabel('Tỷ lệ báo động nhầm'); ax[0].set_ylabel('Recall (bắt được sinh viên không hoàn thành)')
ax[0].set_title('Dự báo từ dữ liệu ngày 0-28 tốt hơn ngẫu nhiên rõ rệt\nnhưng chỉ ở mức vừa phải (tập test 2014J)', fontsize=11)
ax[0].legend()
tt = allres[(allres.variant == 'main') & (allres.set == 'test') & (allres.model == best)]
ax[1].bar(['Recall', 'Precision', 'Tỷ lệ nền'], [tt.recall.iloc[0], tt.precision.iloc[0], tt.base_rate.iloc[0]], color=['#e76f51', '#2a9d8f', '#aaaaaa'])
ax[1].axhline(0.7, color='k', ls='--', lw=1)
ax[1].text(2.45, 0.71, 'Mục tiêu recall 70%', ha='right', fontsize=9)
for i, vv in enumerate([tt.recall.iloc[0], tt.precision.iloc[0], tt.base_rate.iloc[0]]):
    ax[1].text(i, vv + .01, f'{vv:.0%}', ha='center')
ax[1].set_ylim(0, 1); ax[1].set_title(f'Test với ngưỡng chọn trên validation: flag {tt.flag_rate.iloc[0]:.0%} sinh viên', fontsize=11)
for a_ in ax: a_.spines[['top', 'right']].set_visible(False)
plt.tight_layout(); plt.savefig(OUT + 'q3_model_performance.png', dpi=150, bbox_inches='tight'); plt.close()

c = cap[(cap.set == 'test') & (cap.K == 200)]
pv = c.pivot(index='mod_pres', columns='rule', values='precision@K')
fig, ax = plt.subplots(figsize=(9, 4.8))
pv = pv[['Mô hình', 'Quy tắc: ít ngày hoạt động nhất', 'Quy tắc: ít click nhất', 'Quy tắc: chưa nộp TMA1, rồi ít click']]
pv.plot.bar(ax=ax, color=['#e76f51', '#9aa5b1', '#b8c0c8', '#d5dade'], rot=0)
for i, mp in enumerate(pv.index):
    ax.hlines(c[c.mod_pres == mp].base_rate.iloc[0], i - .4, i + .4, color='k', ls='--')
ax.set_ylabel('Tỷ lệ trúng trong 200 sinh viên được liên hệ'); ax.set_xlabel('')
ax.set_title('Top-200 theo mô hình trúng khoảng 4/5 là sinh viên sẽ không hoàn thành\n(đường đứt: tỷ lệ nền của module-kỳ; test 2014J)', fontsize=11)
ax.set_ylim(0, 1); ax.legend(fontsize=8, loc='lower right'); ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout(); plt.savefig(OUT + 'q4_top200_precision.png', dpi=150, bbox_inches='tight'); plt.close()
