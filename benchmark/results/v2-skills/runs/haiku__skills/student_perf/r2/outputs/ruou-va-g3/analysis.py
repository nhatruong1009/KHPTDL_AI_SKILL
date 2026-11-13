"""Uống rượu (Dalc ngày thường, Walc cuối tuần) và điểm cuối kỳ G3.
Dữ liệu: student-mat.csv (Toán) + student-por.csv (Bồ Đào Nha), gộp theo học sinh.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent
KEYS = ['school', 'sex', 'age', 'address', 'famsize', 'Pstatus', 'Medu', 'Fedu',
        'Mjob', 'Fjob', 'reason', 'nursery', 'internet']  # theo student-merge.R / student.txt

# ---------- 1. Nạp & gộp ----------
mat = pd.read_csv(DATA / 'student-mat.csv', sep=';'); mat['subject'] = 'mat'
por = pd.read_csv(DATA / 'student-por.csv', sep=';'); por['subject'] = 'por'
df = pd.concat([mat, por], ignore_index=True)
# Nhóm học sinh: các bản ghi có cùng 13 khóa định danh là cùng một học sinh
df['sid'] = df.groupby(KEYS, sort=False).ngroup()
n_subj = df.groupby('sid')['subject'].nunique()
df['linked'] = df['sid'].map(n_subj) == 2

# ---------- 2. Cờ chất lượng ----------
df['G3_zero'] = df['G3'] == 0
df['G2_zero'] = df['G2'] == 0
df['is_por'] = (df['subject'] == 'por').astype(int)

qc = pd.DataFrame([
    ('bản ghi Toán', len(mat)),
    ('bản ghi Bồ Đào Nha', len(por)),
    ('số cặp khớp theo 13 khóa (merge)', int(pd.merge(mat, por, on=KEYS).shape[0])),
    ('số học sinh duy nhất (nhóm khóa)', df['sid'].nunique()),
    ('học sinh có mặt ở cả hai file', int(df.loc[df.linked, 'sid'].nunique())),
    ('bản ghi thuộc học sinh trùng', int(df['linked'].sum())),
    ('G3 = 0 (tổng)', int(df.G3_zero.sum())),
    ('G3 = 0 và vắng mặt = 0', int((df.G3_zero & (df.absences == 0)).sum())),
    ('G3 = 0 nhưng G2 > 0', int((df.G3_zero & (df.G2 > 0)).sum())),
    ('G2 = 0', int(df.G2_zero.sum())),
    ('G1 = 0', int((df.G1 == 0).sum())),
], columns=['chỉ_số', 'giá_trị'])
qc.to_csv(OUT / 'data_quality.csv', index=False)

# Mẫu chính: G3 > 0 (G3 = 0 coi là không hoàn thành/bỏ học, không phải điểm thật)
main = df[df.G3 > 0].copy().reset_index(drop=True)
adj = main[(main.G2 > 0) & (main.G1 > 0)].copy().reset_index(drop=True)

# ---------- 3. Mô tả ----------
rows = []
for col in ['Walc', 'Dalc']:
    for lvl, g in main.groupby(col):
        m = g.G3.mean(); se = g.G3.std() / np.sqrt(len(g))
        rows.append(dict(biến=col, mức=lvl, n=len(g), G3_trung_bình=m,
                         G3_độ_lệch=g.G3.std(), CI95_thấp=m - 1.96 * se, CI95_cao=m + 1.96 * se))
desc = pd.DataFrame(rows)
desc.to_csv(OUT / 'descriptives.csv', index=False)

# ---------- 4. Kiểm định & cỡ hiệu ứng (nhóm cao 4-5 vs thấp 1-2) ----------
def compare(d, col):
    lo = d[d[col].isin([1, 2])].G3; hi = d[d[col].isin([4, 5])].G3
    n1, n2 = len(hi), len(lo)
    pooled = np.sqrt(((n1 - 1) * hi.var() + (n2 - 1) * lo.var()) / (n1 + n2 - 2))
    diff = hi.mean() - lo.mean()
    U = stats.mannwhitneyu(hi, lo, alternative='two-sided')
    rbc = 2 * U.statistic / (n1 * n2) - 1   # <0: nhóm uống nhiều có G3 thấp hơn
    return dict(biến=col, n_cao=n1, n_thấp=n2, G3_cao=hi.mean(), G3_thấp=lo.mean(),
                chênh_lệch=diff, cohen_d=diff / pooled,
                rank_biserial=rbc, p_MannWhitney=U.pvalue)

tests = pd.DataFrame([compare(main, 'Walc'), compare(main, 'Dalc')])
tests.to_csv(OUT / 'tests_effect_sizes.csv', index=False)

rho = {}
for col in ['Walc', 'Dalc']:
    r, p = stats.spearmanr(main[col], main.G3)
    rho[col] = (r, p)
kw = stats.kruskal(*[g.G3.values for _, g in main.groupby('Walc')])

# ---------- 5. OLS với SE cụm theo học sinh ----------
def ols_cluster(d, y, xs, fe=('is_por',), cluster='sid'):
    d = d.reset_index(drop=True)
    X = np.column_stack([np.ones(len(d))] + [d[c].astype(float).values for c in list(xs) + list(fe)])
    Y = d[y].values.astype(float)
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ Y
    u = Y - X @ b
    n, k = X.shape
    G = d[cluster].nunique()
    meat = np.zeros((k, k))
    for _, idx in d.groupby(cluster).indices.items():
        s = X[idx].T @ u[idx]
        meat += np.outer(s, s)
    c = G / (G - 1) * (n - 1) / (n - k)
    V = c * XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(V))
    tcrit = stats.t.ppf(0.975, G - 1)
    names = ['const'] + list(xs) + list(fe)
    out = pd.DataFrame(dict(term=names, coef=b, se=se, ci_thấp=b - tcrit * se,
                            ci_cao=b + tcrit * se, p=2 * stats.t.sf(np.abs(b / se), G - 1),
                            n=n, cụm=G))
    return out

specs = []
def add(label, d, xs, y='G3', fe=('is_por',)):
    res = ols_cluster(d, y, xs, fe=fe)
    for x in xs:
        r = res[res.term == x].iloc[0]
        sd_x = d[x].std(); sd_y = d[y].std()
        specs.append(dict(mô_hình=label, biến=x, hệ_số=r.coef, CI_thấp=r.ci_thấp, CI_cao=r.ci_cao,
                          p=r.p, beta_chuẩn_hóa=r.coef * sd_x / sd_y, n=int(r.n), cụm=int(r.cụm)))

# Chính: tổng quan (không điều chỉnh G1/G2) và điều chỉnh G1+G2
add('CHÍNH: G3 ~ Walc (mẫu G3>0)', main, ['Walc'])
add('CHÍNH: G3 ~ Dalc (mẫu G3>0)', main, ['Dalc'])
add('CHÍNH: G3 ~ Walc + Dalc (mẫu G3>0)', main, ['Walc', 'Dalc'])
add('ĐIỀU CHỈNH G1+G2: G3 ~ Walc', adj, ['Walc', 'G1', 'G2'])
add('ĐIỀU CHỈNH G1+G2: G3 ~ Dalc', adj, ['Dalc', 'G1', 'G2'])
add('ĐIỀU CHỈNH G1+G2: G3 ~ Walc + Dalc', adj, ['Walc', 'Dalc', 'G1', 'G2'])
# Độ nhạy
add('ĐỘ NHẠY: giữ cả G3 = 0 (tổng quan) Walc', df.reset_index(drop=True), ['Walc'])
add('ĐỘ NHẠY: giữ cả G3 = 0 (tổng quan) Dalc', df.reset_index(drop=True), ['Dalc'])
add('ĐỘ NHẠY: giữ G3 = 0, điều chỉnh G1+G2 (G2>0, G1>0)',
    df[(df.G2 > 0) & (df.G1 > 0)].reset_index(drop=True), ['Walc', 'G1', 'G2'])
one = main[~((main.linked) & (main.subject == 'mat'))].copy()
add('ĐỘ NHẠY: mỗi học sinh một bản ghi, Walc', one, ['Walc'], fe=())
add('ĐỘ NHẠY: mỗi học sinh một bản ghi, Dalc', one, ['Dalc'], fe=())
add('THEO MÔN: chỉ Toán, Walc', main[main.subject == 'mat'], ['Walc'], fe=())
add('THEO MÔN: chỉ Bồ Đào Nha, Walc', main[main.subject == 'por'], ['Walc'], fe=())
add('THEO MÔN: chỉ Toán, Dalc', main[main.subject == 'mat'], ['Dalc'], fe=())
add('THEO MÔN: chỉ Bồ Đào Nha, Dalc', main[main.subject == 'por'], ['Dalc'], fe=())
models = pd.DataFrame(specs)
models.to_csv(OUT / 'models_ols_cluster.csv', index=False)

# ---------- 6. Biểu đồ ----------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
for ax, col, lab in [(axes[0], 'Walc', 'Cuối tuần (Walc)'), (axes[1], 'Dalc', 'Ngày thường (Dalc)')]:
    d = desc[desc.biến == col]
    ax.errorbar(d.mức, d.G3_trung_bình,
                yerr=[d.G3_trung_bình - d.CI95_thấp, d.CI95_cao - d.G3_trung_bình],
                fmt='o-', color='#1f4e79', capsize=4)
    for _, r in d.iterrows():
        ax.annotate(f"n={int(r.n)}", (r.mức, r.CI95_thấp), textcoords='offset points',
                    xytext=(0, -14), ha='center', fontsize=8, color='gray')
    ax.set_xlabel(f'Mức uống rượu {lab} (1 = thấp, 5 = cao)')
    ax.set_xticks([1, 2, 3, 4, 5]); ax.grid(alpha=0.3)
axes[0].set_ylabel('G3 trung bình (95% CI)')
wc = desc[desc.biến == 'Walc'].set_index('mức').G3_trung_bình
fig.suptitle(f"Chưa điều chỉnh điểm trước: uống rượu cuối tuần mức 5 có G3 thấp hơn mức 1 ({wc.loc[5]:.1f} so với {wc.loc[1]:.1f} điểm)", fontsize=11)
fig.tight_layout(); fig.savefig(OUT / 'chart_g3_theo_muc_ruou.png', dpi=150); plt.close(fig)

# Forest plot các ước lượng
f = models[models.biến.isin(['Walc', 'Dalc'])].copy().reset_index(drop=True)
fig, ax = plt.subplots(figsize=(10, 0.42 * len(f) + 1.5))
y = np.arange(len(f))[::-1]
ax.errorbar(f.hệ_số, y, xerr=[f.hệ_số - f.CI_thấp, f.CI_cao - f.hệ_số], fmt='o', color='#1f4e79', capsize=3)
ax.axvline(0, color='gray', ls='--')
ax.set_yticks(y); ax.set_yticklabels(f.mô_hình + ' | ' + f.biến, fontsize=7)
ax.set_xlabel('Hệ số: thay đổi G3 (điểm) khi mức uống rượu tăng 1 bậc')
ax.set_title("Chưa điều chỉnh G1, G2: uống nhiều đi kèm G3 thấp hơn ~0,3–0,6 điểm/bậc; khi điều chỉnh G1, G2 hiệu ứng gần 0", fontsize=10)
ax.grid(alpha=0.3, axis='x')
fig.tight_layout(); fig.savefig(OUT / 'chart_forest_ols.png', dpi=150); plt.close(fig)

# ---------- 7. In kết quả ----------
pd.set_option('display.width', 220); pd.set_option('display.max_columns', 20)
print(qc.to_string(index=False)); print()
print(desc.round(3).to_string(index=False)); print()
print(tests.round(4).to_string(index=False)); print()
print('Spearman:', {k: (round(v[0], 4), round(v[1], 4)) for k, v in rho.items()})
print('Kruskal Walc:', round(kw.statistic, 3), round(kw.pvalue, 4)); print()
print(models.round(4).to_string(index=False))
