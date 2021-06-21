from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Variable for the user ID
user = 'user.id'

class Members(db.Model):
    """This class defines the table for information of Members"""
    memID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    phone = db.Column(db.String(150))
    email = db.Column(db.String(150))
    paid = db.Column(db.Integer)
    fine = db.Column(db.Integer)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey(user))
    trans = db.relationship('Transactions', backref='transfor')


class Books(db.Model):
    """This class defines the table for information of Books"""
    bookID = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    authors = db.Column(db.String(150))
    isbn = db.Column(db.String(150))
    publisher = db.Column(db.String(150))
    payments = db.Column(db.Integer)
    stock = db.Column(db.Integer)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey(user))
    trans = db.relationship('Transactions', backref='transby')


class Transactions(db.Model):
    """This class defines the table for information of Transactions"""
    transID = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.bookID'))
    mem_id = db.Column(db.Integer, db.ForeignKey('members.memID'))
    member_name = db.Column(db.String(150))
    book_name = db.Column(db.String(150))
    iss_date = db.Column(db.String(150))
    ret_date = db.Column(db.String(150))
    payments = db.Column(db.Integer)
    fine = db.Column(db.Integer)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey(user))


class User(db.Model, UserMixin):
    """This class defines the table information regarding The User"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    Books = db.relationship('Books')
    Members = db.relationship('Members')
    Transactions = db.relationship('Transactions')
