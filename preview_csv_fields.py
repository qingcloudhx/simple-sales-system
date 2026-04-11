import os
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(ROOT, 'files', '武汉赛维尔生物产品目录_corrected.csv')

if not os.path.exists(csv_path):
    print('CSV 文件不存在：', csv_path)
    raise SystemExit(1)

print('读取:', csv_path)
try:
    df = pd.read_csv(csv_path, dtype=str)
except Exception as e:
    print('读取CSV失败:', e)
    raise

print('列名：', df.columns.tolist())

cols = ['商品名', '项目', '货号', '品牌', '价格']
for c in cols:
    print(f"列 {c} 是否存在: {c in df.columns}")

print('\n前10行预览（按列）：')
print(df[cols].head(10).to_string(index=False))

print('\n每列示例类型和是否有空值:')
for c in cols:
    col = df[c] if c in df.columns else None
    if col is None:
        continue
    print(f"{c}: non-null count={col.notna().sum()}, sample values=", list(col.dropna().unique()[:5]))
