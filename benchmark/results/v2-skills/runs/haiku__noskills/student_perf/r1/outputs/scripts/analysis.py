"""Phân tích: uống rượu (Dalc/Walc) và điểm cuối kỳ G3 — môn Toán + Bồ Đào Nha.

Chạy: python3 -I outputs/scripts/analysis.py  (từ thư mục workspace)
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

OUT = 'outputs'
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20260111)

d_mat = pd.read_csv('data/student-mat.csv', sep=';')
d_por = pd.read_csv('data/student-por.csv', sep=';')
d_mat['subject'] = 'Toán'
d_por['subject'] = 'Bồ Đào Nha'

BASE13 = ["school", "sex", "age", "address", "famsize", "Pstatus", "Medu", "Fedu",
          "Mjob", "Fjob", "reason", "nursery", "internet"]
# Thuộc tính ổn định của học sinh (không phụ thuộc môn; không gồm Dalc/Walc, paid, absences, G*)
STABLE = BASE13 + ['guardian', 'traveltime', 'higher', 'romantic', 'famrel', 'goout',
                   'health', 'freetime', 'studytime']

# ---------------------------------------------------------------- 1. ghép học sinh
# Bước 1: khớp 1-1 trên 22 thuộc tính ổn định.
d_mat['rid'] = np.arange(len(d_mat))
d_por['rid'] = np.arange(len(d_por))
def unique_pairs(keys, a, b):
    ga = a.groupby(keys).filter(lambda x: len(x) == 1)
    gb = b.groupby(keys).filter(lambda x: len(x) == 1)
    return ga.merge(gb, on=keys, suffixes=('_m', '_p'))[['rid_m', 'rid_p']]

pairs1 = unique_pairs(STABLE, d_mat, d_por)
# Bước 2: các dòng còn lại, khớp 1-1 trên 13 thuộc tính nền (chỉ nhận cặp duy nhất).
rem_m = d_mat[~d_mat.rid.isin(pairs1.rid_m)]
rem_p = d_por[~d_por.rid.isin(pairs1.rid_p)]
pairs2 = unique_pairs(BASE13, rem_m, rem_p)
pairs = pd.concat([pairs1, pairs2], ignore_index=True)
n_pairs = len(pairs)

# Kiểm tra: cách ghép đơn giản của file R (13 khóa) cho bao nhiêu dòng?
r_style = d_mat.merge(d_por, on=BASE13)

print(f'Số dòng mat={len(d_mat)}, por={len(d_por)}')
print(f'Ghép bước 1 (22 thuộc tính, 1-1): {len(pairs1)}')
print(f'Ghép bước 2 (13 thuộc tính, 1-1 phần còn lại): {len(pairs2)}')
print(f'Tổng cặp học sinh ở cả hai file: {n_pairs}')
print(f'Ghép kiểu file R (13 khóa, không 1-1): {len(r_style)} dòng')

# Gán ID học sinh
d_mat['sid'] = None
d_por['sid'] = None
sid_counter = 0
mat_to_sid, por_to_sid = {}, {}
for _, r in pairs.iterrows():
    mat_to_sid[r.rid_m] = sid_counter
    por_to_sid[r.rid_p] = sid_counter
    sid_counter += 1
for rid in d_mat.rid:
    if rid not in mat_to_sid:
        mat_to_sid[rid] = sid_counter
        sid_counter += 1
for rid in d_por.rid:
    if rid not in por_to_sid:
        por_to_sid[rid] = sid_counter
        sid_counter += 1
d_mat['sid'] = d_mat.rid.map(mat_to_sid)
d_por['sid'] = d_por.rid.map(por_to_sid)
n_students = sid_counter
n_overlap = len(pairs)
print(f'Số học sinh duy nhất: {n_students} (trong đó {n_overlap} có mặt ở cả hai môn)')

# Mức uống rượu cấp học sinh: với học sinh có ở cả 2 file, lấy trung bình hai lần tự khai
both = pd.concat([d_mat[['sid', 'Dalc', 'Walc']], d_por[['sid', 'Dalc', 'Walc']]])
alc = both.groupby('sid')[['Dalc', 'Walc']].mean()
mism = pd.DataFrame({'Dalc_m': d_mat.set_index('sid').Dalc, 'Dalc_p': d_por.set_index('sid').Dalc,
                     'Walc_m': d_mat.set_index('sid').Walc, 'Walc_p': d_por.set_index('sid').Walc}).dropna()
print(f'Học sinh ở cả hai file có Dalc giống nhau: {(mism.Dalc_m == mism.Dalc_p).mean():.1%}; '
      f'Walc giống nhau: {(mism.Walc_m == mism.Walc_p).mean():.1%}')

# ---------------------------------------------------------------- 2. bảng dài (mỗi dòng = 1 học sinh x 1 môn)
long = pd.concat([d_mat, d_por], ignore_index=True)
long = long.join(alc, on='sid', rsuffix='_stu')
long['Dalc_s'] = long['Dalc_stu']
long['Walc_s'] = long['Walc_stu']
long['weekly'] = (5 * long.Dalc_s + 2 * long.Walc_s) / 7  # trung bình có trọng số theo số ngày trong tuần
long['por'] = (long.subject == 'Bồ Đào Nha').astype(int)
long['overlap'] = long.sid.map(long.groupby('sid').size()).eq(2)

# ---------------------------------------------------------------- 3. xử lý G3 đáng ngờ
long['G3_zero'] = long.G3.eq(0)
long['G3_zero_abs0'] = long.G3_zero & long.absences.eq(0)
print('\nG3 = 0:', int(long.G3_zero.sum()), 'dòng; trong đó absences = 0:', int(long.G3_zero_abs0.sum()))
print('G3 = 0 có G2 > 0:', int((long.G3_zero & long.G2.gt(0)).sum()))
print('Giá trị G3 thấp khác 0 (1-5):', long[(long.G3 > 0) & (long.G3 <= 5)][['subject', 'G1', 'G2', 'G3']].values.tolist())

main = long[~long.G3_zero].copy()
print(f'Mẫu chính (bỏ G3=0): {len(main)} dòng, {main.sid.nunique()} học sinh')


# ---------------------------------------------------------------- 4. công cụ thống kê
def cluster_ols(df, y, xcols):
    """OLS với SE cluster theo học sinh (CR1). Trả về dict hệ số, SE, p, CI."""
    X = np.column_stack([np.ones(len(df))] + [df[c].to_numpy(float) for c in xcols])
    Y = df[y].to_numpy(float)
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ X.T @ Y
    e = Y - X @ beta
    meat = np.zeros((X.shape[1], X.shape[1]))
    clusters = df.sid.to_numpy()
    for g in np.unique(clusters):
        idx = clusters == g
        s = X[idx].T @ e[idx]
        meat += np.outer(s, s)
    G, N, K = len(np.unique(clusters)), len(Y), X.shape[1]
    corr = G / (G - 1) * (N - 1) / (N - K)
    V = corr * XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(V))
    dfree = G - 1
    t = beta / se
    p = 2 * stats.t.sf(np.abs(t), dfree)
    tcrit = stats.t.ppf(0.975, dfree)
    names = ['const'] + xcols
    return pd.DataFrame({'term': names, 'coef': beta, 'se': se, 't': t, 'p': p,
                         'ci_low': beta - tcrit * se, 'ci_high': beta + tcrit * se, 'n': N, 'clusters': G})


def cluster_boot_spearman(df, xcol, ycol, B=1000):
    """Bootstrap theo cụm học sinh; xếp hạng một lần rồi dùng Pearson trên hạng (= Spearman)."""
    sids = df.sid.unique()
    idx_by = {s: np.where(df.sid.to_numpy() == s)[0] for s in sids}
    rx = stats.rankdata(df[xcol].to_numpy(float))
    ry = stats.rankdata(df[ycol].to_numpy(float))
    vals = []
    for _ in range(B):
        pick = rng.choice(sids, size=len(sids), replace=True)
        ii = np.concatenate([idx_by[s] for s in pick])
        a, b = rx[ii], ry[ii]
        if a.std() == 0 or b.std() == 0:
            continue
        vals.append(np.corrcoef(a, b)[0, 1])
    return np.nanpercentile(vals, [2.5, 97.5])


def cohen_d(a, b):
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    return (a.mean() - b.mean()) / sp


results = {}
rows = []

# (a) Tương quan Spearman (có bootstrap theo cụm học sinh)
for label, data in [('Mẫu chính (bỏ G3=0)', main), ('Gồm cả G3=0', long)]:
    for xcol, xname in [('Walc_s', 'Uống rượu cuối tuần (Walc)'), ('Dalc_s', 'Uống rượu ngày thường (Dalc)'),
                        ('weekly', 'Uống rượu trung bình tuần (có trọng số)')]:
        rho, p = stats.spearmanr(data[xcol], data.G3)
        lo, hi = cluster_boot_spearman(data, xcol, 'G3', B=1000)
        rows.append({'mẫu': label, 'biến': xname, 'spearman_rho': rho, 'rho_CI95_low': lo,
                     'rho_CI95_high': hi, 'p_spearman_(bỏ_qua_cụm)': p, 'n_dòng': len(data)})
spear = pd.DataFrame(rows)
spear.to_csv(f'{OUT}/spearman_results.csv', index=False)
print('\n', spear.round(4).to_string())

# (b) Hồi quy OLS cụm theo học sinh, có kiểm soát môn học
reg_rows = []
for label, data in [('Mẫu chính (bỏ G3=0)', main), ('Gồm cả G3=0', long)]:
    for xcol in ['Walc_s', 'Dalc_s', 'weekly']:
        m1 = cluster_ols(data, 'G3', [xcol, 'por'])
        m1['model'] = 'M1: G3 ~ uống rượu + môn'
        m2 = cluster_ols(data, 'G3', [xcol, 'por', 'G2', 'absences'])
        m2['model'] = 'M2: M1 + G2 + nghỉ học'
        for m in (m1, m2):
            m['mẫu'] = label
            m['biến_uống_rượu'] = xcol
            reg_rows.append(m)
reg = pd.concat(reg_rows, ignore_index=True)
reg.to_csv(f'{OUT}/regression_results.csv', index=False)
key = reg[reg.term.isin(['Walc_s', 'Dalc_s', 'weekly'])]
print('\n', key[['mẫu', 'model', 'biến_uống_rượu', 'coef', 'ci_low', 'ci_high', 'p', 'n', 'clusters']].round(4).to_string())

# (c) Hiệu ứng nhóm: uống nhiều (Walc>=4) so với ít (Walc<=2), Cohen d, Welch, Mann-Whitney
grp_rows = []
for label, data in [('Mẫu chính (bỏ G3=0)', main), ('Gồm cả G3=0', long)]:
    lo_g = data[data.Walc_s <= 2].G3
    hi_g = data[data.Walc_s >= 4].G3
    t, p_w = stats.ttest_ind(hi_g, lo_g, equal_var=False)
    u, p_u = stats.mannwhitneyu(hi_g, lo_g, alternative='two-sided')
    grp_rows.append({'mẫu': label, 'nhóm_ít (Walc<=2) n': len(lo_g), 'TB_G3_ít': lo_g.mean(),
                     'nhóm_nhiều (Walc>=4) n': len(hi_g), 'TB_G3_nhiều': hi_g.mean(),
                     'chênh_lệch (nhiều-ít)': hi_g.mean() - lo_g.mean(),
                     "Cohen_d (nhiều-ít)": cohen_d(hi_g, lo_g), 'p_Welch': p_w, 'p_MannWhitney': p_u})
grp = pd.DataFrame(grp_rows)
grp.to_csv(f'{OUT}/group_comparison.csv', index=False)
print('\n', grp.round(4).to_string())

# (d) Tách theo môn (OLS M2 có G2 và nghỉ học; SE cụm)
sub_rows = []
for subj, data in main.groupby('subject'):
    m = cluster_ols(data, 'G3', ['Walc_s'])
    m2 = cluster_ols(data, 'G3', ['Walc_s', 'G2', 'absences'])
    w = m[m.term == 'Walc_s'].iloc[0]
    w2 = m2[m2.term == 'Walc_s'].iloc[0]
    sub_rows.append({'môn': subj, 'n_dòng': len(data), 'hệ_số_Walc (M1)': w.coef, 'p_M1': w.p,
                     'hệ_số_Walc (M2)': w2.coef, 'p_M2': w2.p})
sub = pd.DataFrame(sub_rows)
sub.to_csv(f'{OUT}/subject_split.csv', index=False)
print('\n', sub.round(4).to_string())

# (e) Chỉ giữ học sinh chỉ có ở một file (không trùng)
single = main[~main.overlap]
m_single = cluster_ols(single, 'G3', ['Walc_s', 'por'])
print('\nChỉ học sinh không trùng (1 dòng/HS):', m_single[['term', 'coef', 'p']].round(4).to_string())

# (f) Thống kê mô tả theo mức Walc
desc = main.groupby('Walc_s').G3.agg(['count', 'mean', 'std', 'median']).round(2)
desc.to_csv(f'{OUT}/descriptive_by_walc.csv')
print('\n', desc.to_string())

# Lưu bảng dài để tái lập
keep = ['sid', 'subject', 'overlap', 'school', 'sex', 'age', 'G1', 'G2', 'G3', 'G3_zero', 'absences',
        'Dalc', 'Walc', 'Dalc_s', 'Walc_s', 'weekly', 'por']
long[keep].to_csv(f'{OUT}/long_clean.csv', index=False)

summary = {
    'n_mat': int(len(d_mat)), 'n_por': int(len(d_por)), 'n_pairs': int(n_pairs), 'n_students': int(n_students),
    'n_rows_long': int(len(long)), 'n_G3_zero': int(long.G3_zero.sum()), 'n_main': int(len(main)),
    'n_main_students': int(main.sid.nunique()), 'n_r_style_rows': int(len(r_style)),
}
with open(f'{OUT}/summary.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print('\nSUMMARY', summary)
