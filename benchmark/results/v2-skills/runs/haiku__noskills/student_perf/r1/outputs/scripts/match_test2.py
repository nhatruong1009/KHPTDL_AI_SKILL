import pandas as pd

d1 = pd.read_csv('data/student-mat.csv', sep=';')
d2 = pd.read_csv('data/student-por.csv', sep=';')
base = ["school", "sex", "age", "address", "famsize", "Pstatus", "Medu", "Fedu",
        "Mjob", "Fjob", "reason", "nursery", "internet"]
stable = ['guardian', 'traveltime', 'higher', 'romantic', 'famrel', 'goout', 'health', 'freetime', 'studytime']
for name, keys in [('base13+stable', base + stable), ('base13+guardian,traveltime', base + ['guardian', 'traveltime']),
                   ('base13+stable+failures', base + stable + ['failures'])]:
    g1 = d1.groupby(keys).size().rename('n_mat')
    g2 = d2.groupby(keys).size().rename('n_por')
    j = pd.concat([g1, g2], axis=1).dropna()
    print(name, 'groups:', len(j), 'mat rows:', int(j.n_mat.sum()), 'por rows:', int(j.n_por.sum()),
          '1:1 groups:', int(((j.n_mat == 1) & (j.n_por == 1)).sum()))
