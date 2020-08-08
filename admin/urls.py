from flask import request, jsonify
from flask_login import login_required, current_user

from . import admin

from app.models import Product, Category, Order, category_schema, product_schema

from app import db

from users.models import User


@admin.route('/category', methods=['POST'])
@login_required
def create_category():
    name = request.json['name']
    try:
        c = Category(name=name, products=[])

        db.session.add(c)
        db.session.flush()
        db.session.commit()

        return category_schema.jsonify(c)
    except:
        db.session.rollback()
        return {'msg': 'Ошибка добавления в Базу данных'}


@admin.route('/product', methods=['POST'])
@login_required
def create_product():
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


@admin.route('/product/<id>', methods=['PUT', 'DELETE'])
@login_required
def change_product():
    if request.method == 'PUT':
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
            db.session.flush()
            db.session.commit()

            return product_schema.jsonify(product)

        except:
            db.session.rollback()

            return {'msg': 'Ошибка удаления'}


@admin.route('/orders', methods=['GET', 'POST'])
@login_required
def all_orders():
    if request.method == 'GET':
        orders = Order.query.all()

        orders_ = []

        for order in orders:
            orders_.append(order.all_info_about_order())

        return jsonify(orders_)

    elif request.method == 'POST':
        user_id = request.json('user_id')
        orders = Order.query.filter_by(user_id=user_id)

        orders_ = []

        for order in orders:
            orders_.append(order.all_info_about_order())

        return jsonify(orders_)


@admin.route('/order/<id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def change_order(id):
    order = Order.query.get(id)
    if request.method == 'GET':

        return jsonify(order.all_info_about_order())

    elif request.method == 'PUT':
        status = request.json['status']
        try:
            order.status = status
            db.session.flush()
            db.session.commit()

            return jsonify(order.all_info_about_order())
        except:
            db.session.rollback()

            return {'msg': 'Не удалось изменить!'}

    elif request.method == 'DELETE':
        try:
            db.session.delete(order)
            db.session.flush()
            db.session.commit()
            orders = Order.query.all()

            orders_ = []

            for order in orders:
                orders_.append(order.all_info_about_order())

            return jsonify(orders_)

        except:
            db.session.rollback()

            return {'msg': 'Ошибка удаления'}


@admin.before_request
def before_request():
    if User.query.get_or_404(current_user.get_id()).role_id == 2:
        pass
    else:
        return 404
