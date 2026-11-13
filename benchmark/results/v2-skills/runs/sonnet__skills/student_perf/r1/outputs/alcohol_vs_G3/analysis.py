import pandas as pd, numpy as np, scipy.stats as st
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
O = 'outputs/alcohol_vs_G3/'
m = pd.read_csv('data/student-mat.csv', sep=';'); p = pd.read_csv('data/student-por.csv', sep=';')
K = ["school","sex","age","address","famsize","Pstatus","Medu","Fedu","Mjob","Fjob","reason","nursery","internet"]
# 1) Nhận diện học sinh: khóa 13 thuộc tính theo student-merge.R + số thứ tự trong nhóm trùng khóa => ghép 1-1 (tránh nhân dòng)
for d in (m, p):
    d['dup'] = d.groupby(K).cumcount()
K2 = K + ['dup']
b = m.merge(p, on=K2, suffixes=('_m', '_p'), how='outer', indicator=True)
print('ghep 1-1:', (b._merge == 'both').sum(), 'chi Toan', (b._merge == 'left_only').sum(),
      'chi Bo', (b._merge == 'right_only').sum(), 'so hoc sinh duy nhat', len(b))
s = b[K2].copy()
for c in ['Dalc','Walc','G1','G2','G3','absences']:
    s[c+'_m'] = b[c+'_m']; s[c+'_p'] = b[c+'_p']
s['in_both'] = (b._merge == 'both') * 1
# rượu: trung bình hai file nếu có cả hai (cùng bảng hỏi)
s['Dalc'] = s[['Dalc_m','Dalc_p']].mean(axis=1); s['Walc'] = s[['Walc_m','Walc_p']].mean(axis=1)
s['alc'] = (5*s.Dalc + 2*s.Walc) / 7
# 2) G3 đáng ngờ: G3==0
for d, n in ((m, 'Toan'), (p, 'Bo')):
    z = d[d.G3 == 0]; print(n, 'G3=0:', len(z), 'absences==0:', (z.absences == 0).sum(), 'G2>0:', (z.G2 > 0).sum())
s['G3_main'] = s[['G3_m','G3_p']].where(s[['G3_m','G3_p']] > 0).mean(axis=1)   # chính: bỏ G3=0
s['G3_all'] = s[['G3_m','G3_p']].mean(axis=1)                                   # nhạy cảm: giữ G3=0
s['G1'] = s[['G1_m','G1_p']].mean(axis=1)
s['sexM'] = (s.sex == 'M') * 1
s.to_csv(O+'student_level.csv', index=False)

def cohen(a, b_):
    sp = np.sqrt(((len(a)-1)*a.var(ddof=1) + (len(b_)-1)*b_.var(ddof=1)) / (len(a)+len(b_)-2))
    return (a.mean()-b_.mean()) / sp
class Fit: pass
def ols_fit(df, y, xs, robust=True):
    X = pd.get_dummies(df[xs], drop_first=True).astype(float); X.insert(0, 'const', 1.0)
    Y = df[y].values.astype(float); A = X.values; n, k = A.shape
    XtXi = np.linalg.inv(A.T @ A); beta = XtXi @ A.T @ Y; res = Y - A @ beta
    h = np.einsum('ij,jk,ik->i', A, XtXi, A)
    if robust:   # HC3
        meat = A.T @ (A * ((res/(1-h))**2)[:, None]); cov = XtXi @ meat @ XtXi
    else:
        cov = XtXi * (res @ res) / (n-k)
    se = np.sqrt(np.diag(cov)); pv = 2*st.t.sf(abs(beta/se), n-k); q = st.t.ppf(.975, n-k)
    f = Fit(); nm = list(X.columns); f.params = pd.Series(beta, nm); f.pvalues = pd.Series(pv, nm)
    f.lo = pd.Series(beta-q*se, nm); f.hi = pd.Series(beta+q*se, nm)
    f.r2 = 1 - (res @ res) / ((Y-Y.mean()) @ (Y-Y.mean())); f.n = n
    return f
rng = np.random.default_rng(0)
def boot(a, b_, n=3000):
    r = [cohen(pd.Series(rng.choice(a, len(a))), pd.Series(rng.choice(b_, len(b_)))) for _ in range(n)]
    return np.percentile(r, [2.5, 97.5])
rows = []
def run(df, y, x, label, pop):
    d = df[[y, x]].dropna(); rho, pv = st.spearmanr(d[x], d[y])
    low = d[d[x] < 2][y]; hi = d[d[x] >= 3][y]   # thấp = 1 ; cao >= 3
    dd = cohen(hi, low); ci = boot(hi.values, low.values)
    ols = ols_fit(d, y, [x], robust=False)
    rows.append(dict(quan_the=pop, ket_qua=y, muc_uong=label, n=len(d), n_thap=len(low), n_cao=len(hi), spearman_rho=rho, p_spearman=pv,
        TB_thap=low.mean(), TB_cao=hi.mean(), chenh=hi.mean()-low.mean(), cohen_d=dd, d_CI_lo=ci[0], d_CI_hi=ci[1],
        p_MannWhitney=st.mannwhitneyu(hi, low).pvalue, he_so_OLS_moi_bac=ols.params[x],
        OLS_CI_lo=ols.lo[x], OLS_CI_hi=ols.hi[x], p_OLS=ols.pvalues[x]))
for x, l in (('Dalc','Dalc'), ('Walc','Walc'), ('alc','Gop 5:2')):
    run(s, 'G3_main', x, l, 'Hoc sinh duy nhat, bo G3=0 (CHINH)')
    run(s, 'G3_all', x, l, 'Hoc sinh duy nhat, giu G3=0 (nhay cam)')
for sub, d in (('Toan', m), ('Bo', p)):
    d = d[d.G3 > 0]
    for x in ('Dalc', 'Walc'):
        run(d, 'G3', x, x, f'Rieng mon {sub}, G3>0')
r = pd.DataFrame(rows); r.round(4).to_csv(O+'ket_qua_hieu_ung.csv', index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
print(r.round(3).to_string())
d = s.dropna(subset=['G3_main']).copy()
print('n hoc sinh G3 hop le:', len(d), '/', len(s))
base = ['Dalc','Walc']; cv = ['sexM','age','school','address','Medu','Fedu','in_both']
mods = {'tho': base, 'hieu chinh': base+cv, 'hieu chinh + G1 (do nhay)': base+cv+['G1']}
out = []
for k, xs in mods.items():
    fit = ols_fit(d, 'G3_main', xs)
    for v in ('Dalc', 'Walc'):
        out.append(dict(mo_hinh=k, bien=v, he_so=fit.params[v], CI_lo=fit.lo[v], CI_hi=fit.hi[v], p=fit.pvalues[v], R2=fit.r2, n=fit.n))
o = pd.DataFrame(out); o.round(4).to_csv(O+'hoi_quy.csv', index=False); print(o.round(4))
# Kruskal
for x in ('Dalc', 'Walc'):
    gs = [g.G3_main.values for _, g in d.groupby(d[x].round())]
    H, pk = st.kruskal(*gs); eta = (H - len(gs) + 1) / (len(d) - len(gs)); print(x, 'Kruskal p=', pk, 'eta2_H=', eta)
t = []
for x in ('Dalc', 'Walc'):
    for lv, g in d.groupby(d[x].round()):
        a = g.G3_main; se = a.std(ddof=1) / np.sqrt(len(a))
        t.append(dict(bien=x, muc=int(lv), n=len(a), TB_G3=a.mean(), CI_lo=a.mean()-1.96*se, CI_hi=a.mean()+1.96*se))
t = pd.DataFrame(t); t.round(3).to_csv(O+'G3_theo_muc.csv', index=False); print(t.round(2))
fig, ax = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
for a, x, l in zip(ax, ('Dalc', 'Walc'), ('ngày thường (Dalc)', 'cuối tuần (Walc)')):
    g = t[t.bien == x]
    a.errorbar(g.muc, g.TB_G3, yerr=[g.TB_G3-g.CI_lo, g.CI_hi-g.TB_G3], fmt='o-', color='#2a6f97', capsize=4)
    for _, q in g.iterrows():
        a.annotate(f'n={q.n}', (q.muc, q.CI_lo-0.3), ha='center', fontsize=8)
    a.set_xlabel(f'Mức uống rượu {l} (1=rất thấp, 5=rất cao)'); a.grid(alpha=.3)
ax[0].set_ylabel('G3 trung bình (thang 20, bỏ G3=0) ± 95% CI')
fig.suptitle('Học sinh uống nhiều hơn có G3 thấp hơn nhẹ (chênh khoảng 1 điểm trên thang 20)', fontsize=11)
fig.tight_layout(); fig.savefig(O+'g3_theo_muc_ruou.png', dpi=130)
