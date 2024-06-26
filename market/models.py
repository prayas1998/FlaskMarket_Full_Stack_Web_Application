from market import db, bcrypt, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=1000)
    items = db.relationship('Item', backref='owned_user', lazy=True)

    def __repr__(self):
        return f'User {self.username}'

    @property  # Used here as a GETTER method
    def password(self):
        return self.password

    @password.setter # Used here as a SETTER method
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    @property
    def prettier_budget(self):
        if len(str(self.budget)) >= 4:
            return f'{str(self.budget)[:-3]},{str(self.budget)[-3:]}'
        else:
            return f'{str(self.budget)}'

    def can_purchase(self, item_obj):
        return self.budget >= item_obj.price

    def can_sell(self, item_obj):
        return item_obj in self.items   # As we have items columns in User this expression will let us know if the user is owner of item.


class Item(db.Model):  # Inheriting db.Model class to Item class to tell database that this will be created as a table.
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(length=1500), nullable=False, unique=True)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))  # https://prnt.sc/P0mXA4-geVEo

    def __repr__(self):
        return f'Item {self.name}'  # Otherwise the items will be shown as [<Item1>, <Item2>]

    def buy(self, user):
        self.owner = user.id
        user.budget -= self.price
        db.session.commit()

    def sell(self,user):
        self.owner = None
        user.budget += self.price
        db.session.commit()
