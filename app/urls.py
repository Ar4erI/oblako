from flask import request, jsonify, url_for, redirect, session
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import Product, User, product_schema, products_schema, OrderedProduct, Order
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
    if request.method == 'POST':
        session.permanent = True
        qty = request.json['qty']
        buyed_products = []

        if 'buyed_products' not in session:
            session['buyed_products'] = buyed_products
            product_in_cart = {id: qty}
            session['buyed_products'].append(product_in_cart)
            session.modified = True
        else:
            product_in_cart = {id: qty}
            session['buyed_products'].append(product_in_cart)
            session.modified = True
    return {'msg': 'Добавлено в корзину!'}


@app.route('/product/cart')
def products_in_cart():
    if 'buyed_products' not in session:
        return {'msg': 'В корзине пока ничего нет!'}
    else:
        products = []
        total = 0
        for n in session['buyed_products']:
            for id, qty in n.items():
                p = Product.query.get(id)
                product = {'id': id, 'manufacturer': p.manufacturer, 'name': p.name, 'description': p.description,
                           'price': p.price, 'qty': qty, 'category_id': p.category_id}
                products.append(product)
                total += p.price * qty
        totaly = {'total': total}
        products.append(totaly)
        return jsonify(products)


@app.route('/product/cart/order', methods=['POST'])
def order_products_from_cart():
    phone = request.json['phone']
    customer_name = request.json['customer_name']
    second_name = request.json['second_name']
    adress = request.json['adress']
    email = request.json['email']
    delivery_type = request.json['delivery_type']
    pay_type = request.json['pay_type']

    if not User.query.filter_by(phone=phone).first():
        new_info = User(phone=phone, name=customer_name, second_name=second_name, adress=adress, email=email,
                        delivery_type=delivery_type, pay_type=pay_type, orders=[])
        db.session.add(new_info)
        db.session.commit()
    else:
        pass
    if session['buyed_products'].__len__() > 0:
        u = User.query.filter_by(phone=phone).first()
        o = Order(user_id=u.id, products=[])
        db.session.add(o)
        db.session.commit()
        order = Order.query.filter_by(user_id=u.id).order_by(Order.id.desc()).first()

        for n in session['buyed_products']:
            for id, qty in n.items():
                product = Product.query.get(id)
                op = OrderedProduct(link_id=id, name=product.name, price=product.price, qty=qty, order_id=order.id)
                db.session.add(op)
                db.session.commit()
        session['buyed_products'] = []

        products_ = []
        total_ = 0
        for p in order.products:
            total_ += p.price * p.qty
            product = {'id': p.id, 'name': p.name, 'link_id': p.link_id, 'price': p.price, 'qty': p.qty}
            products_.append(product)
        order.total = total_
        db.session.commit()
        order_ = {'order_id': order.id, 'status': order.status, 'user_id': order.user_id, 'date': order.date,
                  'total': order.total}
        products_.insert(0, order_)
        return jsonify(products_)

    else:
        return {'msg': 'Вы не можете сделать пустой заказ!'}


'''@app.route('/product/orders')
def all_orders():
    all_products = OrderedProduct.query.all()

    return ordered_products_schema.jsonify(all_products)

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
    return redirect(url_for('all_products'))'''
