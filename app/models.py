from flask_login import UserMixin

from app import db, ma, login_manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    users = db.relationship('User', backref='role', lazy=True)

    def __init__(self, name, users):
        self.name = name
        self.users = users


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

class ProductCart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.Integer)

    def __init__(self, id, qty):
        self.id = id
        self.qty = qty

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    products = db.relationship('Product', backref='category', lazy=True)

    def __init__(self, name, products):
        self.name = name
        self.products = products


# Model Schema
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'manufacturer', 'name', 'description', 'price', 'category_id')

class ProductCartSchema(ma.Schema):
    class Meta:
        fields = ('id', 'qty')

class CategorySchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'products')


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password', 'role_id')

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Init schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
product_cart_schema = ProductCartSchema()
products_cart_schema = ProductCartSchema(many=True)
user_schema = UserSchema()
