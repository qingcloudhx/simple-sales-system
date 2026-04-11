import pandas as pd
import re
from models import db, Product, Category

def import_products_csv(file):
    df = pd.read_csv(file)
    # 1. 检查列名是否完全匹配（忽略空格和大小写，但严格匹配文字）
    required_columns = ['中文名称', '销售价', '库存', '分类']
    # 可选列：英文名称、项目、货号、品牌、成本价、市场价、图片链接
    
    optional_columns = ['英文名称', '项目', '货号', '品牌', '成本价', '市场价', '图片链接']
    # 清洗列名（去除前后空格）
    def normalize_col_name(c):
        if c is None:
            return ''
        s = str(c).strip()
        return s

    original_cols = list(df.columns)
    normalized_map = {}
    for c in original_cols:
        normalized = normalize_col_name(c)
        normalized_map[normalized] = c

    # 检查必需列（用标准化名匹配）
    missing_columns = [col for col in required_columns if col not in normalized_map]
    if missing_columns:
        print(f"缺少必填列：{missing_columns}")
        return False  # 明确返回失败
    
    # 记录成功导入的商品数量
    success_count = 0
    
    for idx, row in df.iterrows():
        row_num = idx + 1
        # 2. 清洗字段值（去除前后空格）
        prod_name = str(row.get('中文名称', '')).strip()
        # 使用 normalized_map 查找实际列名，兼容列头格式
        def get_raw(col_name):
            actual = normalized_map.get(col_name)
            if actual is None:
                return None
            return row.get(actual)

        # 为了兼容 pandas 的 NaN，需要用 pd.isna 判断并统一为空字符串
        raw_english_name = get_raw('英文名称')
        raw_price = get_raw('销售价')
        raw_cost_price = get_raw('成本价')
        raw_market_price = get_raw('市场价')
        raw_stock = get_raw('库存')
        raw_category = get_raw('分类')
        raw_project = get_raw('项目')
        raw_sku = get_raw('货号')
        raw_brand = get_raw('品牌')
        raw_image = get_raw('图片链接')

        english_name = None if raw_english_name is None or pd.isna(raw_english_name) else str(raw_english_name).strip()
        price_str = '' if raw_price is None or pd.isna(raw_price) else str(raw_price).strip()
        cost_price_str = '' if raw_cost_price is None or pd.isna(raw_cost_price) else str(raw_cost_price).strip()
        market_price_str = '' if raw_market_price is None or pd.isna(raw_market_price) else str(raw_market_price).strip()
        stock_str = '' if raw_stock is None or pd.isna(raw_stock) else str(raw_stock).strip()
        category_name = '' if raw_category is None or pd.isna(raw_category) else str(raw_category).strip()
        project = None if raw_project is None or pd.isna(raw_project) else str(raw_project).strip()
        sku = None if raw_sku is None or pd.isna(raw_sku) else str(raw_sku).strip()
        brand = None if raw_brand is None or pd.isna(raw_brand) else str(raw_brand).strip()
        image_link = '' if raw_image is None or pd.isna(raw_image) else str(raw_image).strip()
        
        # 3. 严格检查空值（包括空字符串和纯空格）
        if not prod_name:
            print(f"第{row_num}行：中文名称为空或仅含空格")
            continue
        if not price_str:
            print(f"第{row_num}行：销售价为空或仅含空格")
            continue
        if not stock_str:
            print(f"第{row_num}行：库存为空或仅含空格")
            continue
        if not category_name:
            print(f"第{row_num}行：分类为空或仅含空格")
            category_name = "未分类"  # 分类为空时设为默认
        
        # 4. 验证数值格式
        def extract_number(s):
            if s is None or s == '':
                return None
            # 查找字符串中的第一个数字序列，允许小数和千位分隔符
            m = re.search(r"[-+]?[0-9]+(?:[,\.][0-9]+)?", s)
            if not m:
                return None
            num = m.group(0).replace(',', '')
            return num

        price_num = extract_number(price_str)
        cost_price_num = extract_number(cost_price_str) if cost_price_str else None
        market_price_num = extract_number(market_price_str) if market_price_str else None
        try:
            if price_num is None:
                raise ValueError('无法解析销售价')
            price = float(price_num)
            cost_price = float(cost_price_num) if cost_price_num else None
            market_price = float(market_price_num) if market_price_num else None
            # 有时 stock_str 可能是浮点形式（如 '120.0'），先将其转为 float 再转为 int
            stock = int(float(stock_str))
        except Exception:
            print(f"第{row_num}行：价格或库存格式错误（销售价：{price_str}，库存：{stock_str}）")
            continue
        
        # 5. 处理分类
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            # 如果分类不存在，创建新分类
            category = Category(name=category_name)
            db.session.add(category)
            db.session.flush()  # 立即获取新分类的ID
        
        # 6. 创建或更新商品
        # 检查是否已存在同名商品
        existing_product = Product.query.filter_by(name=prod_name).first()
        if existing_product:
            # 更新现有商品
            existing_product.english_name = english_name if english_name else None
            existing_product.price = price
            existing_product.cost_price = cost_price
            existing_product.market_price = market_price
            existing_product.stock = stock
            existing_product.category_id = category.id
            if image_link:
                existing_product.image = image_link
            if project is not None and project != '':
                existing_product.project = project
            if sku is not None and sku != '':
                existing_product.sku = sku
            if brand is not None and brand != '':
                existing_product.brand = brand
            print(f"第{row_num}行：更新商品 '{prod_name}' (英文名={english_name}, 项目={project}, 货号={sku}, 品牌={brand})")
        else:
            # 创建新商品
            product = Product(
                name=prod_name,
                english_name=english_name if english_name else None,
                price=price,
                cost_price=cost_price,
                market_price=market_price,
                stock=stock,
                category_id=category.id,
                image=image_link if image_link else None,
                project=project if project else None,
                sku=sku if sku else None,
                brand=brand if brand else None
            )
            db.session.add(product)
            print(f"第{row_num}行：创建商品 '{prod_name}' (英文名={english_name}, 项目={project}, 货号={sku}, 品牌={brand})")
        
        success_count += 1
    
    try:
        db.session.commit()
        print(f"成功导入/更新 {success_count} 个商品")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"提交到数据库时出错: {e}")
        return False
