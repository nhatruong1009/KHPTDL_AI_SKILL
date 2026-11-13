import pandas as pd, numpy as np
D = "data/"
w = pd.read_csv(D + "aq1_student_week.csv")
m = pd.read_csv(D + "aq3_model_table.csv")
d = pd.read_csv(D + "aq2_diagnostic_table.csv")
K = ['code_module', 'code_presentation', 'id_student']
# weekly consistency
ww = w.pivot_table(index=K, columns='week', values=['clicks', 'active_days'], aggfunc='sum')
ww.columns = [f"{a}_w{b}" for a, b in ww.columns]
ww = ww.reset_index()
x = d.merge(ww, on=K, suffixes=('', '_wk'))
for col in ['clicks_w1', 'clicks_w2', 'clicks_w3', 'clicks_w4', 'active_days_w1', 'active_days_w2', 'active_days_w3', 'active_days_w4']:
    print(col, "mismatch", (x[col] != x[col + '_wk']).sum() if col + '_wk' in x else 'na', "|", (x[col] - x[col.replace('clicks', 'clicks').replace('active', 'active')]).abs().sum() if False else '')
for cc in ['clicks_w1', 'clicks_w2', 'clicks_w3', 'clicks_w4']:
    wkcol = cc.replace('clicks', 'clicks') + '_wk'
print(pd.DataFrame({'d_w1': x.clicks_w1, 'wk_w1': x['clicks_w1_wk']}).head())
print("weeks: mismatch count w1..w4 ->",
      [(x[f'clicks_w{i}'] != x[f'clicks_w{i}_wk']).sum() for i in range(1, 5)])
print("clicks_0_28 vs sum weeks:", (x.clicks_0_28 != x[[f'clicks_w{i}' for i in range(1, 5)]].sum(axis=1)).sum())
print("clicks_0_28 vs wk sum:", (x.clicks_0_28 != x[[f'clicks_w{i}_wk' for i in range(1, 5)]].sum(axis=1)).sum())
print(d[['clicks_0_28', 'clicks_w1', 'clicks_w2', 'clicks_w3', 'clicks_w4', 'clicks_pre_start']].describe().T)
print("weekly rows per student:", w.groupby(K).size().value_counts().to_dict())
print("weeks in aq1:", sorted(w.week.unique()))
# leakage candidates: correlation with target
num = d.select_dtypes('number').drop(columns=['id_student', 'target_noncompletion'], errors='ignore')
cors = num.corrwith(d.target_noncompletion).sort_values()
print(cors.to_string())
print(pd.crosstab(d.tma1_score.isna(), d.tma1_submitted_by_d28))
print(pd.crosstab(d.tma1_days_before_deadline.isna(), d.tma1_submitted_by_d28))
print("tma1_on_time vs submitted", pd.crosstab(d.tma1_on_time, d.tma1_submitted_by_d28))
print(m.flag_high_activity.value_counts(), m.days_observable_0_28.value_counts().head())
print(d.days_observable_0_28.describe() if 'days_observable_0_28' in d else '')
print(pd.crosstab(d.flag_high_activity, d.target_noncompletion, normalize='index'))
print("model cols in diag not in model:", set(d.columns) - set(m.columns))
print("model vs diag feature equality:", all(np.allclose(m[c].fillna(-999), d[c].fillna(-999)) for c in m.columns if c not in ['code_module', 'code_presentation', 'split'] and np.issubdtype(m[c].dtype, np.number) and c in d))
