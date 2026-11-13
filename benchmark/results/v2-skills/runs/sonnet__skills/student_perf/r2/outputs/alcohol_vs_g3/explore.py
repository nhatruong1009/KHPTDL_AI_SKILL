import pandas as pd
m=pd.read_csv('data/student-mat.csv',sep=';');p=pd.read_csv('data/student-por.csv',sep=';')
keys="school sex age address famsize Pstatus Medu Fedu Mjob Fjob reason nursery internet".split()
print('dup keys',m.duplicated(keys).sum(),p.duplicated(keys).sum(),'full dup',m.duplicated().sum(),p.duplicated().sum())
j=m.merge(p,on=keys,suffixes=('_m','_p'))
print('merge rows',len(j),'unique key groups',j.groupby(keys).ngroups)
extra=['guardian','romantic','famrel','freetime','goout','Dalc','Walc','health','traveltime','studytime','higher']
j2=m.merge(p,on=keys+extra,suffixes=('_m','_p'));print('stricter merge',len(j2))
for c in ['guardian','traveltime','studytime','failures','schoolsup','famsup','activities','higher','romantic','famrel','freetime','goout','Dalc','Walc','health']:
    print(c,round((j[c+'_m']==j[c+'_p']).mean(),3))
for d in (m,p):
    print('G3==0',(d.G3==0).sum(),'G3==0&G2>0',((d.G3==0)&(d.G2>0)).sum(),'G2==0',(d.G2==0).sum())
print(m[m.G3==0][['G1','G2','G3','absences','failures']].describe().loc[['count','mean','min','max']])
print(p[p.G3==0][['G1','G2','G3','absences','failures']])
print(m.G3.value_counts().sort_index().to_dict());print(p.G3.value_counts().sort_index().to_dict())
print(m.Dalc.value_counts().to_dict(),m.Walc.value_counts().to_dict(),p.Dalc.value_counts().to_dict(),p.Walc.value_counts().to_dict())
