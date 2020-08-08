from flask_login import UserMixin

from app import db, ma, login_manager


def check_phone_in_db(phone):
    if User.query.filter_by(phone=phone).first():
        return True
    else:
        return False


def edit_and_check_phone(phone):
    if phone[0] == '0' and phone.__len__() == 10:
        phone = '+38' + phone
        return phone
    elif phone[0] == '8' and phone.__len__() == 11:
        phone = '+3' + phone
        return phone
    elif phone[0] == '3' and phone.__len__() == 12:
        phone = '+' + phone
        return phone
    elif phone[0] == '+' and phone[1] == '3' and phone[2] == '8' and phone[3] == '0' and phone.__len__() == 13:
        pass


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    phone = db.Column(db.String(12), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    second_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(50))
    delivery_type = db.Column(db.String(100), nullable=False)
    pay_type = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), default=1)

    def __init__(self, phone, name, second_name, address, email, delivery_type, pay_type, orders):
        self.phone = edit_and_check_phone(phone)
        self.name = name
        self.second_name = second_name
        self.address = address
        self.email = email
        self.delivery_type = delivery_type
        self.pay_type = pay_type
        self.orders = orders


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    users = db.relationship('User', backref='role', lazy=True)

    def __init__(self, name, users):
        self.name = name
        self.users = users


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'phone', 'name', 'second_name', 'address', 'email', 'delivery_type', 'pay_type')


# Init schema
user_schema = UserSchema()


# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
