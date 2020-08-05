from datetime import datetime

from app import db, ma


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manufacturer = db.Column(db.String(100))   # Производитель
    # availability = db.Column(db.Boolean)   # Наличие
    # photo # Фотография продукта
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __init__(self, manufacturer, name, description, price, category_id):
        self.manufacturer = manufacturer
        self.name = name
        self.description = description
        self.price = price
        self.category_id = category_id


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    products = db.relationship('Product', backref='category', lazy=True)

    def __init__(self, name, products):
        self.name = name
        self.products = products


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    products = db.relationship('OrderedProduct', backref='order', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(100), default='Новый')
    date = db.Column(db.DateTime, default=datetime.now())
    total = db.Column(db.Integer, default=0)

    def __init__(self, user_id, products):
        self.user_id = user_id
        self.products = products


class OrderedProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    qty = db.Column(db.Integer)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))

    def __init__(self, link_id, name, price, qty, order_id):
        self.name = name
        self.link_id = link_id
        self.price = price
        self.qty = qty
        self.order_id = order_id


# Model Schema
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'manufacturer', 'name', 'description', 'price', 'category_id')


class OrderSchema(ma.Schema):
    class Meta:
        fields = ('id', 'user_id')


class OrderedProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'link_id', 'name', 'price', 'qty', 'order_id')


class CategorySchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'products')


# Init schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
ordered_product_schema = OrderedProductSchema()
ordered_products_schema = OrderedProductSchema(many=True)
category_schema = CategorySchema()
