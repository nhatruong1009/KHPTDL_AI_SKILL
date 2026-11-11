import pandas as pd
s=pd.read_csv('outputs/rev/segment.csv');pd.set_option('display.width',200);print(s.round(0).to_string())
