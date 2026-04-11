import sys
import os
import importlib.util

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

APP_FILE = os.path.join(ROOT, 'app-sqlite.py')
spec = importlib.util.spec_from_file_location('app_sqlite_mod', APP_FILE)
app_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_mod)

app = getattr(app_mod, 'app', None)
if app is None:
    print('无法在 app-sqlite.py 中找到 Flask 应用 (变量名 `app`)')
    raise SystemExit(1)

with app.app_context():
    from utils import import_products_csv
    from models import Product
    csv_path = os.path.join(ROOT, 'sample_products.csv')
    print('开始导入：', csv_path)
    ok = import_products_csv(csv_path)
    print('import_products_csv 返回:', ok)
    try:
        cnt = Product.query.count()
        print('当前商品总数:', cnt)
        print('最近导入的 5 条商品:')
        for p in Product.query.order_by(Product.id.desc()).limit(5).all():
            print(p.id, p.name, p.project, p.sku, p.brand, float(p.retail_price) if p.retail_price is not None else None)
    except Exception as e:
        print('查询商品时出错:', e)

print('脚本结束')
