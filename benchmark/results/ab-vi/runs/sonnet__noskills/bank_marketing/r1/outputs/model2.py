import pandas as pd, numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.inspection import permutation_importance

df = pd.read_csv('data/bank-additional/bank-additional-full.csv', sep=';')
df['y'] = (df.y == 'yes').astype(int)
df['prev_contacted'] = (df.pdays != 999).astype(int)
df.loc[df.pdays == 999, 'pdays'] = np.nan
y = df.y
macro = ['emp.var.rate', 'cons.price.idx', 'cons.conf.idx', 'euribor3m', 'nr.employed']
base_drop = ['y', 'duration']


def gbm():
    return HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=300,
                                          categorical_features='from_dtype', l2_regularization=1.0, random_state=0)


def prep(X):
    X = X.copy()
    for c in X:
        if not pd.api.types.is_numeric_dtype(X[c]):
            X[c] = X[c].astype('category')
    return X


def lrm(X):
    cat = [c for c in X if not pd.api.types.is_numeric_dtype(X[c])]
    num = [c for c in X if c not in cat]
    pre = ColumnTransformer([('c', OneHotEncoder(handle_unknown='ignore'), cat),
                             ('n', make_pipeline(SimpleImputer(strategy='constant', fill_value=0), StandardScaler()), num)])
    return make_pipeline(pre, LogisticRegression(max_iter=2000, C=0.5))


def topk(yt, p, q=0.2):
    o = np.argsort(-p)
    k = int(len(p) * q)
    return yt[o[:k]].mean() / yt.mean()


def rep(name, yt, p):
    print('%-45s AUC=%.3f PR-AUC=%.3f lift@10=%.2f lift@20=%.2f' % (name, roc_auc_score(yt, p), average_precision_score(yt, p), topk(yt, p, .1), topk(yt, p, .2)))


sets = {
    'full (no duration)': [c for c in df if c not in base_drop],
    'no macro': [c for c in df if c not in base_drop + macro],
    'no macro + euribor3m': [c for c in df if c not in base_drop + [m for m in macro if m != 'euribor3m']],
}
print('### Random stratified 5-fold CV (all 41188 rows)')
skf = StratifiedKFold(5, shuffle=True, random_state=0)
rule = (df.poutcome == 'success').astype(float) + 0.5 * df.prev_contacted
rep('majority/random (no info)', y.values, np.full(len(y), 0.1126) + np.random.RandomState(0).rand(len(y)) * 1e-6)
rep('rule: poutcome=success / prev contacted', y.values, rule.values)
rep('single: -euribor3m', y.values, -df.euribor3m.values)
cvres = {}
for k, cols in sets.items():
    X = df[cols]
    for nm, m, XX in [('GB', gbm(), prep(X)), ('LR', lrm(X), X)]:
        p = cross_val_predict(m, XX, y, cv=skf, method='predict_proba')[:, 1]
        rep('%s | %s' % (nm, k), y.values, p)
        cvres[(nm, k)] = p

print('\n### Forward-chaining time splits (train on past, test on next block) , GB full')
n = len(df)
blocks = np.linspace(0, n, 6).astype(int)
X = prep(df[sets['full (no duration)']])
for i in range(2, 5):
    tr = np.arange(n) < blocks[i]
    te = (np.arange(n) >= blocks[i]) & (np.arange(n) < blocks[i + 1])
    for nm, cols in [('full', sets['full (no duration)']), ('no macro', sets['no macro'])]:
        XX = prep(df[cols])
        XX = XX.loc[:, XX[tr].notna().any()]
        m = gbm().fit(XX[tr], y[tr])
        p = m.predict_proba(XX[te])[:, 1]
        rep('block %d (rate %.3f, train rate %.3f) %s' % (i, y[te].mean(), y[tr].mean(), nm), y[te].values, p)
    rep('   -euribor3m only', y[te].values, -df.euribor3m[te].values)

print('\n### Permutation importance (random CV holdout 25%), GB full no duration, AUC drop')
rs = np.random.RandomState(1)
idx = rs.permutation(n)
te = idx[: n // 4]
tr = idx[n // 4:]
X = prep(df[sets['full (no duration)']])
m = gbm().fit(X.iloc[tr], y.iloc[tr])
p = m.predict_proba(X.iloc[te])[:, 1]
rep('holdout 25%', y.iloc[te].values, p)
pi = permutation_importance(m, X.iloc[te], y.iloc[te], scoring='roc_auc', n_repeats=8, random_state=0)
imp = pd.Series(pi.importances_mean, index=X.columns).sort_values(ascending=False)
sd = pd.Series(pi.importances_std, index=X.columns)[imp.index]
out = pd.DataFrame({'auc_drop': imp, 'sd': sd})
print(out.round(4))
out.to_csv('outputs/importance_random_holdout.csv')
# decile table on random-CV GB full
p = cvres[('GB', 'full (no duration)')]
o = np.argsort(-p)
d = pd.DataFrame({'y': y.values[o]})
d['decile'] = np.arange(n) * 10 // n + 1
g = d.groupby('decile').y.agg(['size', 'sum', 'mean'])
g['lift'] = g['mean'] / y.mean()
g['cum_recall'] = g['sum'].cumsum() / y.sum()
print(g.round(3))
g.to_csv('outputs/decile_gain_cv.csv')
np.save('outputs/cv_pred.npy', p)
# marginal rates
for c in ['poutcome', 'contact', 'job', 'month']:
    print(df.groupby(c).y.agg(['size', 'mean']).round(3).sort_values('mean', ascending=False))
print(df.groupby(pd.cut(df.age, [0, 25, 30, 40, 50, 60, 100])).y.agg(['size', 'mean']).round(3))
print(df.groupby(pd.cut(df.euribor3m, [0, 1, 2, 4, 5])).y.agg(['size', 'mean']).round(3))
print(df.groupby('prev_contacted').y.agg(['size', 'mean']).round(3))
