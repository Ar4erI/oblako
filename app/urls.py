from flask import request, jsonify, session, redirect, url_for
from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash

from app.models import Product, Category, product_schema, products_schema, OrderedProduct, Order, categories_schema
from app import app, db

from users.models import User, Role


# Routs
@app.route('/')
def all_categories():
    categories = Category.query.all()
    result = categories_schema.dump(categories)

    return jsonify(result)


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


@app.route('/product')
def all_products():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)

    return jsonify(result)


# Get Single Products
@app.route('/product/<id>')
def get_product(id):
    if Product.query.get_or_404(id):
        product = Product.query.get_or_404(id)
        return product_schema.jsonify(product)
    else:
        return 404


@app.route('/product/<int:id>/buy', methods=['POST'])
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
                ids = []
                for n in session['buyed_products']:
                    for id_ in n.keys():
                        ids.append(int(id_))
                if id in ids:
                    for n in session['buyed_products']:
                        for id_, qty_ in n.items():
                            if int(id_) == id:
                                qty_ += qty
                                new = {id_: qty_}
                                n.update(new)
                                session.modified = True
                            else:
                                pass
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
        if 'buyed_products' not in session:
            return {'msg': 'В корзине пока ничего нет!'}
        else:
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
        if 'buyed_products' not in session:
            return {'msg': 'В корзине пока ничего нет!'}
        else:
            selected_id = request.json['id']
            for n in session['buyed_products']:
                for id, qty in n.items():
                    if id == selected_id:
                        current = {id: qty}
                        session['buyed_products'].remove(current)
                        if session['buyed_products'].__len__() == 0:
                            session.pop('buyed_products', None)
                        session.modified = True
            return redirect(url_for('products_in_cart'))


@app.route('/product/cart/order', methods=['POST'])
def order_products_from_cart():
    phone = request.json['phone']
    name = request.json['name']
    second_name = request.json['second_name']
    address = request.json['address']
    email = request.json['email']
    delivery_type = request.json['delivery_type']
    pay_type = request.json['pay_type']

    if not User.query.filter_by(phone=phone).first():
        try:
            new_info = User(phone=phone, name=name, second_name=second_name, address=address, email=email,
                            delivery_type=delivery_type, pay_type=pay_type, orders=[])
            db.session.add(new_info)
            db.session.flush()
            db.session.commit()
        except:
            db.session.rollback()
            return {'msg': 'Ошибка добавления в Базу данных'}
    elif User.query.filter_by(phone=phone).first():
        user = User.query.filter_by(phone=phone).first()
        user.address = address
        user.delivery_type = delivery_type
        user.pay_type = pay_type
        try:
            db.session.flush()
            db.session.commit()
        except:
            db.session.rollback()
            return {'msg': 'Ошибка добавления в Базу данных'}
    else:
        pass
    if 'buyed_products' not in session:
        return {'msg': 'Вы не можете сделать пустой заказ!'}
    else:
        if current_user.get_id():
            user = User.query.get(current_user.get_id())
        else:
            user = User.query.filter_by(phone=phone).first_or_404()
            if user.name == name and user.second_name == second_name:
                login_user(user)
            else:
                return {'msg': 'Неверное имя пользователя или номер телефона, так как пользователь с таким номером '
                               'телефона уже существует!Попробуйте ввести те данные которые использовали при '
                               'регистрации или войти и изменить ваши данные.'}
        o = Order(user_id=user.id, products=[])
        try:
            db.session.add(o)
            db.session.flush()
            db.session.commit()
            order = Order.query.filter_by(user_id=user.id).order_by(Order.id.desc()).first_or_404()
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

        total = 0
        for p in order.products:
            total += p.price * p.qty
        order.total = total
        try:
            db.session.flush()
            db.session.commit()
        except:
            db.session.rollback()
            return {'msg': 'Ошибка добавления в Базу данных'}

        return jsonify(order.all_info_about_order())


@app.route('/create_all_for_db', methods=['POST'])
def create_db():
    pswd = request.json['pswd']
    if pswd == 'super secret key':
        db.create_all()
        role1 = Role('Admin', [])
        role2 = Role('Customer', [])
        category1 = Category('Табак', [])
        category2 = Category('Кальян', [])
        category3 = Category('Уголь', [])
        db.session.add(category1)
        db.session.add(category2)
        db.session.add(category3)
        db.session.add(role1)
        db.session.add(role2)
        db.session.commit()
        product1 = Product(manufacturer='JBR', name='JBR dragon berry',
                           description='JBR dragon berry (Драконья ягода) 100грамм', price=170, category_id=1)
        product2 = Product(manufacturer='JBR', name='Табак Jibiar California Sun',
                           description='Табак Jibiar California Sun (Дыня Лайм Лёд), 100 грамм', price=170,
                           category_id=1)
        product3 = Product(manufacturer='Daim', name='Daim Spiced Peach',
                           description='Daim Spiced Peach (Пряный Персик), 50 грамм', price=60,
                           category_id=1)
        product4 = Product(manufacturer='Daim', name='Daim Ice Blueberry',
                           description='Табак для кальяна Daim 50 грамм (Ice Blueberry)', price=60,
                           category_id=1)
        product5 = Product(manufacturer='Dark Side', name='Dark Side Code Cherry Medium',
                           description='Dark Side Code Cherry Medium (Дарксайд Вишня) 100грамм', price=460,
                           category_id=1)
        product6 = Product(manufacturer='Dark Side', name='Dark Side Space Dessert Medium',
                           description='Табак для кальяна Dark Side Space Dessert Medium (Спайс Десерт), 100 грамм',
                           price=460, category_id=1)
        user = User(phone='0674004659', name='Admin', second_name=generate_password_hash('password'), address='1',
                    email='1', delivery_type='1', pay_type='1', orders=[], role_id=2)
        product21 = Product(manufacturer='Amy', name='Кальян Amy Delux Unio 006.01 black',
                            description='Модель кальяна отличается стильным внешним видом, ведь в ней соединены '
                                        'интересный цвет, сталь и дерево. В комплексе недорогой кальян выглядит очень '
                                        'эффектно, поэтому его часто выбирают в качестве подарка, или для домашнего '
                                        'использования и дополнения красивым изделием интерьера.', price=2075, category_id=2)
        product22 = Product(manufacturer='Dumok', name='Кальян Dumok Hookah(Украина) AL-09 MINOR',
                            description='Качественный кальян с отличным внешним видом и передачей вкуса!',
                            price=2070, category_id=2)
        product31 = Product(manufacturer='Phoenix', name='Уголь Phoenix (Феникс) 1кг 72 кубика',
                            description='Отличный кокосовый уголь, содержащий натуральные компоненты. Достоинства его в'
                                        ' том, что он тлеет более одного часа, равномерно прогревая табак и не меняя '
                                        'его вкус. Соответственно, количество пепла - минимальное', price=100, category_id=3)
        product32 = Product(manufacturer='Panda', name='Кокосовый уголь Panda (Панда) 1кг 72шт.',
                            description='Высококачественный кокосовый уголь для кальяна, созданный из скорлупы '
                                        'кокосового ореха. В упаковке 1 килограмма содержится 72 крупных кубика угля, '
                                        'которые обеспечат вкусное и дымное курение кальяна без посторонних запахов и '
                                        'изменения вкуса.', price=125, category_id=3)
        db.session.add(user)
        db.session.add(product1)
        db.session.add(product2)
        db.session.add(product3)
        db.session.add(product4)
        db.session.add(product5)
        db.session.add(product6)
        db.session.add(product21)
        db.session.add(product22)
        db.session.add(product31)
        db.session.add(product32)
        db.session.commit()

        return {'msg': 'Успешное заполнение бд для тестов'}
