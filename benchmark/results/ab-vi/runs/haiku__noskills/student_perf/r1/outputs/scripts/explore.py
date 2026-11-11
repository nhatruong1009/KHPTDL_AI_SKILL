import pandas as pd

d1 = pd.read_csv('data/student-mat.csv', sep=';')
d2 = pd.read_csv('data/student-por.csv', sep=';')
print(d1.shape, d2.shape)
print('NA', d1.isna().sum().sum(), d2.isna().sum().sum())
keys = ["school", "sex", "age", "address", "famsize", "Pstatus", "Medu", "Fedu",
        "Mjob", "Fjob", "reason", "nursery", "internet"]
for n, d in [('mat', d1), ('por', d2)]:
    print(n, 'dup keys:', d.duplicated(keys).sum())
    print(n, 'G3 dist:', d.G3.value_counts().sort_index().to_dict())
    print(n, 'G3==0:', (d.G3 == 0).sum(), 'G3==0&G2>0:', ((d.G3 == 0) & (d.G2 > 0)).sum(),
          'G3==0&absences==0:', ((d.G3 == 0) & (d.absences == 0)).sum())
    print(n, 'Dalc', d.Dalc.value_counts().sort_index().to_dict(),
          'Walc', d.Walc.value_counts().sort_index().to_dict())
m = d1.merge(d2, on=keys, suffixes=('_m', '_p'))
print('merged', len(m))
for c in ['Dalc', 'Walc', 'G1', 'G2', 'G3', 'absences', 'famrel', 'goout', 'health', 'freetime', 'failures', 'studytime', 'higher', 'romantic', 'paid']:
    print(c, 'agree', round((m[c + '_m'] == m[c + '_p']).mean(), 3))
print('max matches per key in mat:', d1.merge(d2, on=keys).groupby(keys).size().max())
print(m[(m.G3_m == 0) | (m.G3_p == 0)][['G1_m', 'G2_m', 'G3_m', 'absences_m', 'G1_p', 'G2_p', 'G3_p', 'absences_p', 'Dalc_m', 'Walc_m', 'Dalc_p', 'Walc_p']].to_string())
