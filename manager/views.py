from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import json

from .models import Books, Members, Trans
from . import db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # result = Books.query.filter_by(bookID=1).first()
    # print(result.user_id)
    if request.method == 'POST':
        title = request.form.get('title')
        authors = request.form.get('authors')
        isbn = request.form.get('isbn')
        publisher = request.form.get('publisher')
        num_pages = request.form.get('num_pages')
        stock = request.form.get('stock')
        data = request.form.get('data')

        if len(title) < 1:
            flash('title is too short!', category='error')
        else:
            new_Book = Books(title=title, authors=authors, isbn=isbn, publisher=publisher,
                             num_pages=num_pages, stock=stock, data=data, user_id=current_user.id)
            db.session.add(new_Book)
            db.session.commit()
            flash('Book Added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/members', methods=['GET', 'POST'])
@login_required
def members():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        fine = request.form.get('fine')

        if len(name) < 1:
            flash('name is too short!', category='error')
        else:
            new_member = Members(name=name, phone=phone,
                                 email=email, fine=fine, user_id=current_user.id)
            db.session.add(new_member)
            db.session.commit()
            flash('Member Added!', category='success')

    return render_template("members.html", user=current_user)


@views.route('/trans', methods=['GET', 'POST'])
@login_required
def trans():

    if request.method == 'POST':
        book_name = request.form.get('book_name')
        mem_name = request.form.get('member_name')
        iss_date = request.form.get('iss_date')
        ret_date = request.form.get('ret_date')
        rent = request.form.get('rent')
        fine = request.form.get('fine')

        mem_id = Members.query.filter_by(memID=mem_name).first()
        book_id = Books.query.filter_by(bookID=book_name).first()

        mem_id.fine=str(int(fine) + int(mem_id.fine))
        book_id.stock=str(int(book_id.stock)-1)

        if len(iss_date) < 1:
            flash('name is too short!', category='error')
        elif int(mem_id.fine) > 500:
            flash('Member debt limit exeeded', category='error')
        elif int(book_id.stock) < 0:
            flash('book not in stock anymore', category='error')

        else:
            new_trans = Trans(transby=book_id, transfor=mem_id, member_name=mem_id.name, book_name=book_id.title,
                              iss_date=iss_date, ret_date=ret_date, rent=rent, fine=fine, user_id=current_user.id)
            db.session.add(new_trans)
            db.session.commit()
            flash('Transaction Added!', category='success')

    return render_template("trans.html", user=current_user)
