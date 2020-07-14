from flask import request, jsonify, url_for, redirect, session
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import Product, User, product_schema, products_schema, user_schema, ProductCart, product_cart_schema, products_cart_schema
from app import app, db

# Routs
@app.route('/<category>', methods=['GET', 'POST'])
def product_for_category(category):
    if request.method == 'GET':
        product = Product.query.filter_by(category_id=category)
        result = products_schema.dump(product)
    else:
        manufacturer = request.json['manufacturer']
        min_price = request.json['min_price']
        max_price = request.json['max_price']
        sort_by = request.json['sort_by']
        sort = request.json['sort']

        product = Product.query.filter_by(category_id=category)
        if manufacturer:
            product = product.filter_by(manufacturer=manufacturer)
        else:
            pass
        if min_price:
            product = product.filter(Product.price >= min_price)
        else:
            pass
        if max_price:
            product = product.filter(Product.price <= max_price)
        else:
            pass
        if sort_by == 'price':
            if sort == 'min_max':
                product = product.order_by(Product.price)
            elif sort == 'max_min':
                product = product.order_by(Product.price.desc())
        elif sort_by == 'manufacturer':
            if sort == 'min_max':
                product = product.order_by(Product.manufacturer)
            elif sort == 'max_min':
                product = product.order_by(Product.manufacturer.desc())
            pass
        result = products_schema.dump(product)

    return jsonify(result)

@app.route('/product', methods=['POST', 'GET'])
def all_products():
    if request.method == 'POST':
        manufacturer = request.json['manufacturer']
        name = request.json['name']
        description = request.json['description']
        price = request.json['price']
        category_id = request.json['category_id']

        new_product = Product(manufacturer, name, description, price, category_id)

        db.session.add(new_product)
        db.session.commit()

        return product_schema.jsonify(new_product)

    elif request.method == 'GET':
        all_products = Product.query.all()
        result = products_schema.dump(all_products)

        return jsonify(result)



# Get Single Products
@app.route('/product/<id>', methods=['GET', 'PUT', 'DELETE'])
def get_product(id):
    if request.method == 'GET':
        product = Product.query.get(id)
        return product_schema.jsonify(product)

    elif request.method == 'PUT':
        product = Product.query.get(id)

        manufacturer = request.json['manufacturer']
        name = request.json['name']
        description = request.json['description']
        price = request.json['price']
        category_id = request.json['category_id']

        product.manufacturer = manufacturer
        product.name = name
        product.description = description
        product.price = price
        product.category_id = category_id

        db.session.commit()

        return product_schema.jsonify(product)

    elif request.method == 'DELETE':
        product = Product.query.get(id)
        db.session.delete(product)
        db.session.commit()

        return product_schema.jsonify(product)

@app.route('/product/<id>/buy', methods=['POST', 'DELETE'])
def buy_product(id):
    pass

@app.route('/product/cart')
def products_in_cart():
    pass

@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = generate_password_hash(request.json['password'])

    new_user = User(username=username, password=password)

    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    user = User.query.filter_by(username=username).first()
    if check_password_hash(user.password, password):
        login_user(user)
        return {'msg': 'Вы успешно вошли!'}
    else:
        return {'msg': 'Произошла ошибка!'}

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('all_products'))
