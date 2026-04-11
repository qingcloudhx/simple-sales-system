from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# 商品-标签关联表（多对多）
product_tags = db.Table('product_tags',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(120), unique=True, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    color = db.Column(db.String(20), default='primary')  # 标签颜色：primary/success/warning/danger/info
    products = db.relationship('Product', secondary=product_tags, back_populates='tags')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    # 新增字段：项目、货号、品牌
    project = db.Column(db.String(128), nullable=True)
    sku = db.Column(db.String(64), nullable=True)
    brand = db.Column(db.String(64), nullable=True)
    # 价格字段：销售价、成本价、市场价
    price = db.Column(db.Numeric(10, 2))  # 销售价
    cost_price = db.Column(db.Numeric(10, 2), nullable=True)  # 成本价
    market_price = db.Column(db.Numeric(10, 2), nullable=True)  # 市场价
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(1024))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category')
    tags = db.relationship('Tag', secondary=product_tags, back_populates='products')

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    type = db.Column(db.String(10))  # in/out
    amount = db.Column(db.Numeric(10, 2))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    product = db.relationship('Product')
    user = db.relationship('User')
    is_reversed = db.Column(db.Boolean, default=False)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(255))
    ts = db.Column(db.DateTime, default=datetime.now)
    user = db.relationship('User')
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=True)
    sale = db.relationship('Sale')