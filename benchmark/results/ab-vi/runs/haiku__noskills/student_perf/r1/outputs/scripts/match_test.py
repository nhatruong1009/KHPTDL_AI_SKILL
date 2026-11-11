import pandas as pd

d1 = pd.read_csv('data/student-mat.csv', sep=';')
d2 = pd.read_csv('data/student-por.csv', sep=';')
base = ["school", "sex", "age", "address", "famsize", "Pstatus", "Medu", "Fedu",
        "Mjob", "Fjob", "reason", "nursery", "internet"]
extra_sets = {
    'base13': [],
    '+guardian,traveltime': ['guardian', 'traveltime'],
    '+guardian,traveltime,higher,romantic': ['guardian', 'traveltime', 'higher', 'romantic'],
    '+guardian,traveltime,higher,romantic,famrel,goout,health,freetime,studytime,Dalc,Walc': [
        'guardian', 'traveltime', 'higher', 'romantic', 'famrel', 'goout', 'health', 'freetime',
        'studytime', 'Dalc', 'Walc'],
}
for name, extra in extra_sets.items():
    keys = base + extra
    g1 = d1.groupby(keys).size().rename('n_mat')
    g2 = d2.groupby(keys).size().rename('n_por')
    j = pd.concat([g1, g2], axis=1).dropna()
    one_to_one = ((j.n_mat == 1) & (j.n_por == 1)).sum()
    print(name, 'matched keys:', len(j), 'rows matched mat/por:', j.n_mat.sum(), j.n_por.sum(),
          '1:1 groups:', one_to_one, 'max group sizes:', j.n_mat.max(), j.n_por.max())
