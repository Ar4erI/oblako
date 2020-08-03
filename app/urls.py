from flask import request, jsonify, session, redirect, url_for

from app.models import Product, product_schema, products_schema, OrderedProduct, Order
from app import app, db

from users.models import User


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

        try:
            new_product = Product(manufacturer, name, description, price, category_id)

            db.session.add(new_product)
            db.session.flush()
            db.session.commit()

            return product_schema.jsonify(new_product)
        except:
            db.session.rollback()
            return {'msg': 'Ошибка добавления в Базу данных'}

    elif request.method == 'GET':
        all_products = Product.query.all()
        result = products_schema.dump(all_products)

        return jsonify(result)


# Get Single Products
@app.route('/product/<id>', methods=['GET', 'PUT', 'DELETE'])
def get_product(id):
    if request.method == 'GET':
        product = Product.query.get_or_404(id)
        return product_schema.jsonify(product)

    elif request.method == 'PUT':
        product = Product.query.get_or_404(id)

        manufacturer = request.json['manufacturer']
        name = request.json['name']
        description = request.json['description']
        price = request.json['price']
        category_id = request.json['category_id']

        try:
            product.manufacturer = manufacturer
            product.name = name
            product.description = description
            product.price = price
            product.category_id = category_id

            db.session.commit()

            return product_schema.jsonify(product)

        except:
            db.session.rollback()
            return {'msg': 'Ошибка добавления в Базу данных'}

    elif request.method == 'DELETE':
        product = Product.query.get_or_404(id)
        try:
            db.session.delete(product)
            db.session.commit()

            return product_schema.jsonify(product)
        except:
            db.session.rollback()
            return {'msg': 'Ошибка удаления'}


@app.route('/product/<id>/buy', methods=['POST'])
def buy_product(id):
    if Product.query.get_or_404(id):
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
    else:
        return 404


@app.route('/product/cart', methods=['GET', 'PUT', 'DELETE'])
def products_in_cart():
    if request.method == 'GET':
        if 'buyed_products' not in session:
            return {'msg': 'В корзине пока ничего нет!'}
        else:
            products = []
            total = 0
            for n in session['buyed_products']:
                for id, qty in n.items():
                    p = Product.query.get_or_404(id)
                    product = {'id': id, 'manufacturer': p.manufacturer, 'name': p.name, 'description': p.description,
                           'price': p.price, 'qty': qty, 'category_id': p.category_id}
                    products.append(product)
                    total += p.price * qty
            totaly = {'total': total}
            products.append(totaly)
            return jsonify(products)
    elif request.method == 'PUT':
        selected_id = request.json['id']
        changed_qty = request.json['qty']
        for n in session['buyed_products']:
            for id, qty in n.items():
                if id == selected_id:
                    new = {selected_id: changed_qty}
                    n.update(new)
                    session.modified = True
        return redirect(url_for('products_in_cart'))
    elif request.method == 'DELETE':
        selected_id = request.json['id']
        for n in session['buyed_products']:
            for id, qty in n.items():
                if id == selected_id:
                    current = {id: qty}
                    session['buyed_products'].remove(current)
                    session.modified = True
        return redirect(url_for('products_in_cart'))





@app.route('/product/cart/order', methods=['POST'])
def order_products_from_cart():
    phone = request.json['phone']
    customer_name = request.json['customer_name']
    second_name = request.json['second_name']
    address = request.json['address']
    email = request.json['email']
    delivery_type = request.json['delivery_type']
    pay_type = request.json['pay_type']

    if not User.query.filter_by(phone=phone).first():
        try:
            new_info = User(phone=phone, name=customer_name, second_name=second_name, address=address, email=email,
                        delivery_type=delivery_type, pay_type=pay_type, orders=[])
            db.session.add(new_info)
            db.session.flush()
            db.session.commit()
        except:
            db.session.rollback()
            return {'msg': 'Ошибка добавления в Базу данных'}
    else:
        pass
    if 'buyed_products' in session:
        u = User.query.filter_by(phone=phone).first_or_404()
        o = Order(user_id=u.id, products=[])
        try:
            db.session.add(o)
            db.session.flush()
            db.session.commit()
            order = Order.query.filter_by(user_id=u.id).order_by(Order.id.desc()).first_or_404()
        except:
            db.session.rollback()
            return {'msg': 'Ошибка добавления в Базу данных'}

        for n in session['buyed_products']:
            for id, qty in n.items():
                product = Product.query.get_or_404(id)
                try:
                    op = OrderedProduct(link_id=id, name=product.name, price=product.price, qty=qty, order_id=order.id)
                    db.session.add(op)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                    return {'msg': 'Ошибка добавления в Базу данных'}
        session.pop('buyed_products', None)

        products_ = []
        total_ = 0
        for p in order.products:
            total_ += p.price * p.qty
            product = {'id': p.id, 'name': p.name, 'link_id': p.link_id, 'price': p.price, 'qty': p.qty}
            products_.append(product)
        order.total = total_
        try:
            db.session.flush()
            db.session.commit()
        except:
            db.session.rollback()
            return {'msg': 'Ошибка добавления в Базу данных'}
        order_ = {'order_id': order.id, 'status': order.status, 'user_id': order.user_id, 'date': order.date,
                  'total': order.total}
        products_.insert(0, order_)
        return jsonify(products_)

    else:
        return {'msg': 'Вы не можете сделать пустой заказ!'}
