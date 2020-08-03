from flask_login import UserMixin

from app import db, ma, login_manager


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

    def __init__(self, phone, name, second_name, address, email, delivery_type, pay_type, orders):
        self.phone = phone
        self.name = name
        self.second_name = second_name
        self.address = address
        self.email = email
        self.delivery_type = delivery_type
        self.pay_type = pay_type
        self.orders = orders


'''class User(db.Model, UserMixin):
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
        self.users = users'''


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'phone', 'name', 'second_name', 'address', 'email', 'delivery_type', 'pay_type')


# Init schema
user_schema = UserSchema()


# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
