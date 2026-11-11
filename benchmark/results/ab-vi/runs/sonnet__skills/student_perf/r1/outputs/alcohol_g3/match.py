import pandas as pd, numpy as np
from scipy.optimize import linear_sum_assignment

K = "school sex age address famsize Pstatus Medu Fedu Mjob Fjob reason nursery internet".split()
# thuộc tính ổn định theo học sinh (không phụ thuộc môn) dùng để ghép một-một khi khóa trùng
S = "guardian traveltime studytime schoolsup famsup activities higher romantic famrel freetime goout health".split()


def load():
    m = pd.read_csv('data/student-mat.csv', sep=';')
    p = pd.read_csv('data/student-por.csv', sep=';')
    m['mi'] = range(len(m)); p['pi'] = range(len(p))
    return m, p


def match(m, p):
    pairs = []
    gp = p.groupby(K)
    for key, a in m.groupby(K):
        if key not in gp.groups:
            continue
        b = gp.get_group(key)
        sc = np.array([[(ra[S] == rb[S]).sum() for _, rb in b.iterrows()] for _, ra in a.iterrows()])
        r, c = linear_sum_assignment(-sc)
        for i, j in zip(r, c):
            pairs.append((a.iloc[i].mi, b.iloc[j].pi, sc[i, j], len(a) * len(b) > 1))
    return pd.DataFrame(pairs, columns=['mi', 'pi', 'score', 'ambig'])


if __name__ == '__main__':
    m, p = load(); pr = match(m, p)
    print(len(pr), pr.ambig.sum()); print(pr.score.value_counts().sort_index())
