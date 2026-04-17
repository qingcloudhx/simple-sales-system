import pandas as pd

df = pd.read_excel('files/武汉赛维尔生物产品目录20260306.xlsx')
print('Columns:', df.columns.tolist())
print('Shape:', df.shape)
print('\nFirst 10 rows:')
print(df.head(10).to_string())
print('\nData types:')
print(df.dtypes.to_string())
