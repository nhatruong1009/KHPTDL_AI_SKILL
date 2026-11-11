"""Rượu & G3 (Toán + Bồ Đào Nha). Chạy từ thư mục gốc project: python outputs/alcohol_g3/analysis.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, pandas as pd
from scipy import stats
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from match import load, match

OUT = 'outputs/alcohol_g3/'
rng = np.random.default_rng(0)
m, p = load(); pr = match(m, p)

# ---------- 1. Bảng cấp học sinh (mỗi học sinh 1 dòng) ----------
m['subj'] = 'Toan'; p['subj'] = 'Van'
mm = m.set_index('mi'); pp = p.set_index('pi')
rows = []
for _, r in pr.iterrows():
    a, b = mm.loc[r.mi], pp.loc[r.pi]
    rows.append(dict(sid=f"B{int(r.mi)}_{int(r.pi)}", both=1, Dalc=(a.Dalc + b.Dalc) / 2, Walc=(a.Walc + b.Walc) / 2,
                     G3_mat=a.G3, G3_por=b.G3, sex=a.sex, age=a.age, school=a.school, address=a.address,
                     Medu=a.Medu, Fedu=a.Fedu, studytime=(a.studytime + b.studytime) / 2, goout=(a.goout + b.goout) / 2,
                     higher=a.higher, failures=(a.failures + b.failures) / 2))
for i, a in mm.iterrows():
    if i not in set(pr.mi):
        rows.append(dict(sid=f"M{i}", both=0, Dalc=a.Dalc, Walc=a.Walc, G3_mat=a.G3, G3_por=np.nan, sex=a.sex, age=a.age,
                         school=a.school, address=a.address, Medu=a.Medu, Fedu=a.Fedu, studytime=a.studytime,
                         goout=a.goout, higher=a.higher, failures=a.failures))
for i, a in pp.iterrows():
    if i not in set(pr.pi):
        rows.append(dict(sid=f"P{i}", both=0, Dalc=a.Dalc, Walc=a.Walc, G3_mat=np.nan, G3_por=a.G3, sex=a.sex, age=a.age,
                         school=a.school, address=a.address, Medu=a.Medu, Fedu=a.Fedu, studytime=a.studytime,
                         goout=a.goout, higher=a.higher, failures=a.failures))
S = pd.DataFrame(rows)
# G3 = 0 coi là đáng ngờ (không thi/bỏ học: toàn bộ có absences=0, G2 thường 0) -> NaN
S['G3_mat_v'] = S.G3_mat.where(S.G3_mat > 0); S['G3_por_v'] = S.G3_por.where(S.G3_por > 0)
S['G3_valid'] = S[['G3_mat_v', 'G3_por_v']].mean(axis=1)          # TB các môn hợp lệ
S['G3_all'] = S[['G3_mat', 'G3_por']].mean(axis=1)                # sensitivity: giữ số 0
S['any0'] = ((S.G3_mat == 0) | (S.G3_por == 0)).astype(int)
S['alc'] = (5 * S.Dalc + 2 * S.Walc) / 7                           # mức rượu trung bình tuần
S.to_csv(OUT + 'student_level.csv', index=False)

log = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); log.append(s)

P(f"Dòng thô: Toán {len(m)}, Văn {len(p)}; ghép đúng 1-1: {len(pr)} học sinh (R-merge cho 382 do ghép nhiều-nhiều trên khóa trùng)")
P(f"Học sinh duy nhất: {len(S)}; có G3=0 ở ≥1 môn: {S.any0.sum()}; G3 hợp lệ: {S.G3_valid.notna().sum()}")

def boot_ci(f, x, y, n=2000):
    idx = np.arange(len(x)); v = []
    for _ in range(n):
        s = rng.choice(idx, len(idx)); v.append(f(x[s], y[s]))
    return np.percentile(v, [2.5, 97.5])

def hedges(a, b):
    na, nb = len(a), len(b); sp = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    d = (a.mean() - b.mean()) / sp; J = 1 - 3 / (4 * (na + nb) - 9); g = d * J
    se = np.sqrt((na + nb) / (na * nb) + g ** 2 / (2 * (na + nb)))
    return g, g - 1.96 * se, g + 1.96 * se

def analyse(df, y, label):
    res = []
    for x in ['Dalc', 'Walc', 'alc']:
        d = df[[x, y]].dropna(); xv, yv = d[x].values, d[y].values
        rho, pv = stats.spearmanr(xv, yv); lo, hi = boot_ci(lambda a, b: stats.spearmanr(a, b)[0], xv, yv, 1000)
        groups = [g[y].values for _, g in d.groupby(x) if len(g) >= 5]
        H, pk = stats.kruskal(*groups); eps2 = (H - len(groups) + 1) / (len(d) - len(groups))
        # nhóm tương phản: thấp (=1 với Dalc; ≤2 với Walc/alc) vs cao (≥3 Dalc; ≥4 Walc; ≥3 alc)
        if x == 'Dalc': lowm, highm = d[x] == 1, d[x] >= 3
        elif x == 'Walc': lowm, highm = d[x] <= 2, d[x] >= 4
        else: lowm, highm = d[x] <= 1.5, d[x] >= 3
        lo_g, hi_g = d[lowm][y], d[highm][y]
        g, glo, ghi = hedges(hi_g, lo_g); t, pt = stats.ttest_ind(hi_g, lo_g, equal_var=False)
        u, pu = stats.mannwhitneyu(hi_g, lo_g)
        res.append(dict(tap=label, bien=x, n=len(d), spearman_rho=rho, rho_lo=lo, rho_hi=hi, p_spearman=pv,
                        kruskal_H=H, p_kruskal=pk, epsilon2=eps2, n_thap=len(lo_g), n_cao=len(hi_g),
                        mean_thap=lo_g.mean(), mean_cao=hi_g.mean(), diff=hi_g.mean() - lo_g.mean(),
                        hedges_g=g, g_lo=glo, g_hi=ghi, p_welch=pt, p_mannwhitney=pu))
    return res

def ols(df, y, x, ctrl, cat):
    d = df[[y, x] + ctrl + cat].dropna()
    X = pd.get_dummies(d[[x] + ctrl + cat], columns=cat, drop_first=True).astype(float)
    X.insert(0, 'const', 1.0); Y = d[y].values; Xv = X.values
    b = np.linalg.solve(Xv.T @ Xv, Xv.T @ Y); e = Y - Xv @ b
    H = Xv @ np.linalg.inv(Xv.T @ Xv) @ Xv.T; h = np.diag(H)
    XtXi = np.linalg.inv(Xv.T @ Xv); V = XtXi @ (Xv.T * (e / (1 - h))) @ (Xv.T * (e / (1 - h))).T @ XtXi  # HC3
    se = np.sqrt(np.diag(V)); k = list(X.columns).index(x); t = b[k] / se[k]
    pv = 2 * (1 - stats.t.cdf(abs(t), len(d) - Xv.shape[1]))
    sd_y, sd_x = Y.std(ddof=1), d[x].std(ddof=1)
    r2 = 1 - (e ** 2).sum() / ((Y - Y.mean()) ** 2).sum()
    return dict(bien=x, n=len(d), beta=b[k], ci_lo=b[k] - 1.96 * se[k], ci_hi=b[k] + 1.96 * se[k], p=pv,
                std_beta=b[k] * sd_x / sd_y, R2=r2)

# ---------- 2. Phân tích chính: cấp học sinh, G3 hợp lệ ----------
R = analyse(S, 'G3_valid', 'chinh: hoc sinh duy nhat, bo G3=0')
# ---------- 3. Độ nhạy ----------
R += analyse(S, 'G3_all', 'nhay: giu G3=0')
mat = m.assign(G3_v=m.G3.where(m.G3 > 0)); por = p.assign(G3_v=p.G3.where(p.G3 > 0))
mat['alc'] = (5 * mat.Dalc + 2 * mat.Walc) / 7; por['alc'] = (5 * por.Dalc + 2 * por.Walc) / 7
R += analyse(mat, 'G3_v', 'rieng Toan, bo G3=0'); R += analyse(por, 'G3_v', 'rieng Van, bo G3=0')
R += analyse(mat, 'G3', 'rieng Toan, giu G3=0'); R += analyse(por, 'G3', 'rieng Van, giu G3=0')
R = pd.DataFrame(R); R.to_csv(OUT + 'ket_qua_tuong_quan.csv', index=False)
P(R[['tap', 'bien', 'n', 'spearman_rho', 'rho_lo', 'rho_hi', 'p_spearman', 'epsilon2', 'p_kruskal', 'diff', 'hedges_g', 'g_lo', 'g_hi', 'p_welch']].round(4).to_string())

# ---------- 4. Hồi quy có kiểm soát (HC3) ----------
ctrl = ['age', 'Medu', 'Fedu', 'studytime', 'failures', 'goout']; cat = ['sex', 'school', 'address', 'higher']
RR = []
for x in ['Dalc', 'Walc']:
    for lab, df, y in [('hoc sinh, bo G3=0', S, 'G3_valid'), ('hoc sinh, giu G3=0', S, 'G3_all')]:
        r = ols(df, y, x, [], []); r['mo_hinh'] = lab + ' | tho'; RR.append(r)
        r = ols(df, y, x, ctrl, cat); r['mo_hinh'] = lab + ' | kiem soat'; RR.append(r)
# cả Dalc và Walc cùng mô hình
for lab, y in [('bo G3=0', 'G3_valid')]:
    d = S.copy(); d['Walc_'] = d.Walc
    X = d[[y, 'Dalc', 'Walc'] + ctrl + cat].dropna()
    Xd = pd.get_dummies(X.drop(columns=y), columns=cat, drop_first=True).astype(float); Xd.insert(0, 'c', 1.0)
    b = np.linalg.lstsq(Xd.values, X[y].values, rcond=None)[0]; e = X[y].values - Xd.values @ b
    XtXi = np.linalg.inv(Xd.values.T @ Xd.values); h = np.einsum('ij,jk,ik->i', Xd.values, XtXi, Xd.values)
    V = XtXi @ (Xd.values.T * (e / (1 - h))) @ (Xd.values.T * (e / (1 - h))).T @ XtXi; se = np.sqrt(np.diag(V))
    for nm in ['Dalc', 'Walc']:
        k = list(Xd.columns).index(nm); t = b[k] / se[k]
        RR.append(dict(bien=nm, n=len(X), beta=b[k], ci_lo=b[k] - 1.96 * se[k], ci_hi=b[k] + 1.96 * se[k],
                       p=2 * (1 - stats.t.cdf(abs(t), len(X) - Xd.shape[1])), std_beta=np.nan, R2=np.nan,
                       mo_hinh='hoc sinh, bo G3=0 | Dalc+Walc cung luc, kiem soat'))
RR = pd.DataFrame(RR); RR.to_csv(OUT + 'ket_qua_hoi_quy.csv', index=False)
P(RR.round(4).to_string())

# ---------- 5. G3=0 có liên quan rượu không (xác suất G3=0) ----------
Z = []
for x in ['Dalc', 'Walc']:
    for nm, df in [('Toan', m), ('Van', p)]:
        z = (df.G3 == 0).astype(int); lo, hi = (df[x] <= (1 if x == 'Dalc' else 2)), (df[x] >= (3 if x == 'Dalc' else 4))
        a = z[hi].sum(); b_ = hi.sum() - a; c = z[lo].sum(); d_ = lo.sum() - c
        OR, pf = stats.fisher_exact([[a, b_], [c, d_]])
        Z.append(dict(mon=nm, bien=x, ti_le_cao=a / hi.sum(), n_cao=hi.sum(), ti_le_thap=c / lo.sum(), n_thap=lo.sum(), OR=OR, p_fisher=pf))
Z = pd.DataFrame(Z); Z.to_csv(OUT + 'g3_bang_0_theo_ruou.csv', index=False); P(Z.round(4).to_string())
P('G3=0 : absences==0 ?', (m[m.G3 == 0].absences == 0).mean(), (p[p.G3 == 0].absences == 0).mean())

# ---------- 6. Biểu đồ ----------
plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
fig, ax = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for a_, x, t in [(ax[0], 'Dalc', 'Uống rượu ngày thường (Dalc)'), (ax[1], 'Walc', 'Uống rượu cuối tuần (Walc)')]:
    d = S[[x, 'G3_valid']].dropna(); d['lv'] = d[x].round().astype(int)
    g = d.groupby('lv').G3_valid.agg(['mean', 'std', 'count'])
    g['ci'] = 1.96 * g['std'] / np.sqrt(g['count'])
    a_.errorbar(g.index, g['mean'], yerr=g['ci'], fmt='o-', color='#1f5aa6', capsize=4, lw=2)
    for i, r in g.iterrows(): a_.annotate(f"n={int(r['count'])}", (i, r['mean']), textcoords='offset points', xytext=(0, 10), ha='center', fontsize=9)
    rr = R[(R.tap.str.startswith('chinh')) & (R.bien == x)].iloc[0]
    a_.set_title(f"{t}\nSpearman ρ = {rr.spearman_rho:.2f}, p {"< 0.001" if rr.p_spearman<0.001 else "= %.3f"%rr.p_spearman}; Hedges g = {rr.hedges_g:.2f}", fontsize=11)
    a_.set_xlabel('Mức độ (1 = rất thấp … 5 = rất cao)'); a_.set_xticks(range(1, 6))
ax[0].set_ylabel('G3 trung bình (±95% CI)')
fig.suptitle('Điểm G3 theo mức uống rượu (học sinh duy nhất, đã loại G3 = 0)', fontsize=13, fontweight='bold')
plt.tight_layout(); plt.savefig(OUT + 'g3_theo_ruou.png', dpi=150); plt.close()

# forest plot hedges g
F = R[R.bien.isin(['Dalc', 'Walc'])].copy(); F['nhan'] = F.tap + ' – ' + F.bien
F = F.iloc[::-1]
fig, ax = plt.subplots(figsize=(10, 6))
ax.errorbar(F.hedges_g, range(len(F)), xerr=[F.hedges_g - F.g_lo, F.g_hi - F.hedges_g], fmt='o', color='#1f5aa6', capsize=3)
ax.axvline(0, color='grey', ls='--'); ax.set_yticks(range(len(F))); ax.set_yticklabels(F.nhan, fontsize=9)
ax.set_xlabel('Hedges g (nhóm uống nhiều − nhóm uống ít) với 95% CI; âm = điểm thấp hơn')
ax.set_title('Effect size theo các cách xử lý dữ liệu', fontweight='bold'); plt.tight_layout()
plt.savefig(OUT + 'forest_hedges_g.png', dpi=150); plt.close()
open(OUT + 'log.txt', 'w').write('\n'.join(log))
