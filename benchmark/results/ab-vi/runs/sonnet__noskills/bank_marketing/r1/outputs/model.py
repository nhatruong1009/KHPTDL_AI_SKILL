import pandas as pd, numpy as np, sys
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.inspection import permutation_importance
from sklearn.model_selection import StratifiedKFold, cross_val_predict

df = pd.read_csv('data/bank-additional/bank-additional-full.csv', sep=';')
df['y'] = (df.y == 'yes').astype(int)
df['prev_contacted'] = (df.pdays != 999).astype(int)
df.loc[df.pdays == 999, 'pdays'] = np.nan
print(df.shape, df.y.mean(), 'dups', df.duplicated().sum())


def run(drop):
    X = df.drop(columns=['y'] + drop)
    y = df.y
    cat = [c for c in X if not pd.api.types.is_numeric_dtype(X[c])]
    num = [c for c in X if c not in cat]
    n = len(df)
    cut = int(n * 0.7)  # chronological split (file is ordered by date)
    tr = np.arange(n) < cut
    te = ~tr
    pre = ColumnTransformer([
        ('c', OneHotEncoder(handle_unknown='ignore'), cat),
        ('n', make_pipeline(SimpleImputer(strategy='constant', fill_value=0), StandardScaler()), num)])
    lr = make_pipeline(pre, LogisticRegression(max_iter=2000, C=0.5))
    Xg = X.copy()
    for c in cat:
        Xg[c] = Xg[c].astype('category')
    gb = HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=300,
                                        categorical_features='from_dtype', l2_regularization=1.0, random_state=0)
    out = {}
    yt = y[te].values
    for name, m, XX in [('LR', lr, X), ('GB', gb, Xg)]:
        m.fit(XX[tr], y[tr])
        p = m.predict_proba(XX[te])[:, 1]
        o = np.argsort(-p)
        r = {'auc': roc_auc_score(yt, p), 'ap': average_precision_score(yt, p)}
        for q in (10, 20, 30):
            k = int(len(p) * q / 100)
            r['recall@%d' % q] = yt[o[:k]].sum() / yt.sum()
            r['lift@%d' % q] = yt[o[:k]].mean() / yt.mean()
        out[name] = r
        if name == 'GB':
            out['_p'] = p
            out['_m'] = m
            out['_X'] = XX
    out['base_rate_test'] = yt.mean()
    out['base_rate_train'] = y[tr].mean()
    s = (df.loc[te, 'poutcome'] == 'success').astype(float) + 0.5 * df.loc[te, 'prev_contacted']
    out['rule'] = {'auc': roc_auc_score(yt, s), 'ap': average_precision_score(yt, s)}
    s2 = -df.loc[te, 'euribor3m']
    out['euribor_only'] = {'auc': roc_auc_score(yt, s2), 'ap': average_precision_score(yt, s2)}
    skf = StratifiedKFold(5, shuffle=True, random_state=0)
    pc = cross_val_predict(gb, Xg, y, cv=skf, method='predict_proba')[:, 1]
    out['cv_gb'] = {'auc': roc_auc_score(y, pc), 'ap': average_precision_score(y, pc)}
    m = out['_m']
    XX = out['_X']
    pi = permutation_importance(m, XX[te], y[te], scoring='roc_auc', n_repeats=5, random_state=0)
    imp = pd.Series(pi.importances_mean, index=XX.columns).sort_values(ascending=False)
    out['imp'] = imp
    return out


for label, drop in [('A_no_duration', ['duration']),
                    ('B_no_duration_no_campaign', ['duration', 'campaign']),
                    ('C_with_duration_ref', [])]:
    o = run(drop)
    print('\n==', label)
    for k in ('LR', 'GB', 'rule', 'euribor_only', 'cv_gb'):
        print(k, {a: round(b, 4) for a, b in o[k].items()})
    print('base', o['base_rate_train'], o['base_rate_test'])
    print(o['imp'].head(10).round(4))
    if label == 'A_no_duration':
        o['imp'].to_csv('outputs/importance.csv', header=['perm_auc_drop'])
        te_n = len(o['_p'])
        yt = df.y.values[-te_n:]
        p = o['_p']
        order = np.argsort(-p)
        d = pd.DataFrame({'y': yt[order]})
        d['decile'] = np.arange(len(d)) * 10 // len(d) + 1
        g = d.groupby('decile').y.agg(['size', 'sum', 'mean'])
        g['lift'] = g['mean'] / yt.mean()
        g['cum_recall'] = g['sum'].cumsum() / yt.sum()
        print(g.round(3))
        g.to_csv('outputs/decile_gain.csv')
        t = df.iloc[-te_n:].copy()
        t['p'] = p
        for c in ['poutcome', 'contact', 'month']:
            print(t.groupby(c).agg(n=('y', 'size'), yes=('y', 'mean'), pred=('p', 'mean')).round(3))
        print(df.groupby(pd.cut(df.euribor3m, [0, 1, 2, 4, 5])).y.agg(['size', 'mean']))
