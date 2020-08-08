from flask import request, redirect, url_for, jsonify
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash

from . import users
from .models import User, user_schema, check_phone_in_db

from app import db

from app.models import Order


@users.route('/login', methods=['POST'])
def login():
    name = request.json['name']
    phone = request.json['phone']

    user = User.query.filter_by(name=name).first_or_404()
    if user.role_id == 2:
        if check_password_hash(user.second_name, phone):
            login_user(user)
            return {'msg': 'Вы успешно вошли!'}
        else:
            return {'msg': 'Неверное имя пользователя или номер телефона'}
    else:
        if user.phone == phone:
            login_user(user)
            return {'msg': 'Вы успешно вошли!'}
        else:
            return {'msg': 'Неверное имя пользователя или номер телефона'}


@users.route('/orders')
@login_required
def all_orders():
    user_id = current_user.get_id()
    orders = Order.query.filter_by(user_id=user_id)

    orders_ = []

    for order in orders:
        orders_.append(order.all_info_about_order())

    return jsonify(orders_)


@users.route('/register', methods=['POST'])
def register():
    phone = request.json['phone']
    name = request.json['name']
    second_name = request.json['second_name']
    address = request.json['address']
    email = request.json['email']
    delivery_type = request.json['delivery_type']
    pay_type = request.json['pay_type']
    if check_phone_in_db(phone):
        return jsonify(
            {'msg': 'Пользователь с таким номером телефона уже существует. Возможно вы уже зарегистрированы так '
                    'как система автоматически регистрирует пользователя при оформлении заказа.Попробуйте войти.'})
    else:
        pass
    try:
        new_info = User(phone=phone, name=name, second_name=second_name, address=address, email=email,
                        delivery_type=delivery_type, pay_type=pay_type, orders=[])
        db.session.add(new_info)
        db.session.flush()
        db.session.commit()

        return {'msg': 'Вы успешно зарегистрировались!'}

    except:
        db.session.rollback()
        return {'msg': 'Ошибка добавления в Базу данных'}


@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('all_products'))


@users.route('/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    if request.method == 'GET':
        return user_schema.jsonify(current_user)
    elif request.method == 'PUT':
        phone = request.json['phone']
        name = request.json['name']
        second_name = request.json['second_name']
        address = request.json['address']
        email = request.json['email']
        delivery_type = request.json['delivery_type']
        pay_type = request.json['pay_type']

        try:
            current_user.phone = phone
            current_user.name = name
            current_user.second_name = second_name
            current_user.address = address
            current_user.email = email
            current_user.delivery_type = delivery_type
            current_user.pay_type = pay_type
            db.session.flush()
            db.session.commit()
            return user_schema.jsonify(current_user)

        except:
            db.session.rollback()
            return {'msg': 'Ошибка добавления в Базу данных'}
