import pandas as pd

D = "data/"
TEXT_COLS = {"school", "sex", "address", "famsize", "Pstatus", "Mjob", "Fjob", "reason",
             "guardian", "schoolsup", "famsup", "paid", "activities", "nursery", "higher",
             "internet", "romantic"}


def load(f):
    df = pd.read_csv(D + f, sep=";", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    df = df.apply(lambda s: s.str.strip().str.strip('"'))
    for c in df.columns:
        if c not in TEXT_COLS:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


mat = load("student-mat.csv")
por = load("student-por.csv")
for n, d in [("mat", mat), ("por", por)]:
    print(n, d.shape, "nulls:", int(d.isna().sum().sum()), "dups:", int(d.duplicated().sum()))
    print(d[["G1", "G2", "G3", "Dalc", "Walc"]].describe().round(2).to_string())
    print("G3==0:", int((d.G3 == 0).sum()), " G3==0 & G2>0:", int(((d.G3 == 0) & (d.G2 > 0)).sum()))
    print("G3 low values:", d.G3.value_counts().sort_index().head(6).to_dict())
    print("Dalc dist:", d.Dalc.value_counts().sort_index().to_dict(),
          "Walc dist:", d.Walc.value_counts().sort_index().to_dict())

keys = ["school", "sex", "age", "address", "famsize", "Pstatus", "Medu", "Fedu",
        "Mjob", "Fjob", "reason", "nursery", "internet"]
print("key dups mat:", int(mat.duplicated(keys).sum()), "por:", int(por.duplicated(keys).sum()))
m = mat.merge(por, on=keys, suffixes=("_mat", "_por"))
print("merged rows:", len(m))
for c in ["Dalc", "Walc", "G1", "G2", "G3", "guardian", "famrel", "absences", "studytime", "paid", "failures", "goout"]:
    print("agreement", c, round((m[c + "_mat"] == m[c + "_por"]).mean(), 3))
