from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import json

# Importing Models and Databse Settings (SQLAlchemy)
from .models import Books, Members, Trans
from . import db

# Adding to Routes
views = Blueprint('views', __name__)

# Books
@views.route('/', methods=['GET', 'POST'])
@login_required

# Funtion for the Home page Showing a List of all the booKs
def home():

    # Handling the Post request for the Addition of books to the Database
    if request.method == 'POST':
        title = request.form.get('title')
        authors = request.form.get('authors')
        isbn = request.form.get('isbn')
        publisher = request.form.get('publisher')
        payments = request.form.get('payments')
        stock = request.form.get('stock')
        data = request.form.get('data')

        # Query For the Database
        new_Book = Books(title=title, authors=authors, isbn=isbn, publisher=publisher, num_pages=num_pages, stock=stock, data=data, user_id=current_user.id)
        db.session.add(new_Book)
        db.session.commit()

        # Success message
        flash('Book Added!', category='success')
    
    # Returning a User ID to access Books.
    return render_template("home.html", user=current_user)

# Members
@views.route('/members', methods=['GET', 'POST'])
@login_required

# Funtion for the Addition of members 
def members():

    # handling the POST request from the member form
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        fine = request.form.get('fine')
        paid = request.form.get('fine')

    
        # Query For the Database
        new_member = Members(name=name, phone=phone,email=email, fine=fine,paid=paid, user_id=current_user.id)
        db.session.add(new_member)
        db.session.commit()

        # Success message
        flash('Member Added!', category='success')

    
    # Returning a User ID to access Books.
    return render_template("members.html", user=current_user)

# Transactions 
@views.route('/trans', methods=['GET', 'POST'])
@login_required

# Funtion for the Addition of members 
def trans():

    # Handling the POST request
    if request.method == 'POST':
        book_name = request.form.get('book_name')
        mem_name = request.form.get('member_name')
        iss_date = request.form.get('iss_date')
        ret_date = request.form.get('ret_date')
        paid = request.form.get('rent')
        fine = request.form.get('fine')

        # Getting the Members and Books for Debt and StocK verifications respectively
        mem_id = Members.query.filter_by(memID=mem_name).first()
        book_id = Books.query.filter_by(bookID=book_name).first()

        # Numbers to be verified 
        mem_id.fine=str(int(fine) + int(mem_id.fine))
        mem_id.paid=str(int(paid) + int(mem_id.paid))
        book_id.stock=str(int(book_id.stock)-1)
        book_id.payments=str(int(paid)+int(book_id.payments))

        # The Debt must not be more than 500
        if int(mem_id.fine) > 500:
            flash('Member debt limit exeeded', category='error')

        # Making sure Stock is there
        elif int(book_id.stock) <= 0:
            flash('book not in stock anymore', category='error')

        else:
            # Query For the Database
            new_trans = Trans(transby=book_id, transfor=mem_id, member_name=mem_id.name, book_name=book_id.title, iss_date=iss_date, ret_date=ret_date, payments=paid, fine=fine, user_id=current_user.id)
            db.session.add(new_trans)
            db.session.commit()

            # Success message
            flash('Transaction Added!', category='success')

    # Returning a User ID to access Books.
    return render_template("trans.html", user=current_user)
