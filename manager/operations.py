from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
import json


# Importing the Model and the Database
from .models import Books, Members, Transactions
from . import db

# For the Report Funtion
import requests
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt

operations = Blueprint('operations', __name__)


# Transactions
@operations.route('/add_transactions', methods=['GET', 'POST'])
@login_required
def add_transactions():
    """Function for adding transactions/Issuing Books
    Parameters
    ----------
    Handles :
        request for addtion of transactions
    
    fine:
        adds the fine to previous Value
        checks if fine is more than 500

    stock:
        checks if books Stock is present
        Subtracts 1 book from the book

    Returns
    -------
    Transactions template
    """
    if request.method == 'POST':
        book_name = request.form.get('book_name')
        mem_name = request.form.get('member_name')
        iss_date = request.form.get('iss_date')
        ret_date = request.form.get('ret_date')
        paid = request.form.get('rent')
        fine = request.form.get('fine')

        mem_id = Members.query.filter_by(memID=mem_name).first()
        book_id = Books.query.filter_by(bookID=book_name).first()

        mem_id.fine = str(int(fine) + int(mem_id.fine))
        mem_id.paid = str(int(paid) + int(mem_id.paid))
        book_id.stock = str(int(book_id.stock)-1)
        book_id.payments = str(int(paid)+int(book_id.payments))

        if int(mem_id.fine) > 500:
            flash('Member debt limit exeeded', category='error')
        elif int(book_id.stock) <= 0:
            flash('book not in stock anymore', category='error')
        else:
            new_transactions = Transactions(transby=book_id, transfor=mem_id, member_name=mem_id.name, book_name=book_id.title,
                                     iss_date=iss_date, ret_date=ret_date, payments=paid, fine=fine, user_id=current_user.id)
            db.session.add(new_transactions)
            db.session.commit()
            flash('Transaction Added!', category='success')
    return render_template("add_transactions.html", user=current_user)


# Members
@operations.route('/add_members', methods=['GET', 'POST'])
@login_required
def add_members():
    """Function for adding transactions/ Issuing Books
    Parameters
    ----------
    Handles :
        request for addtion of transactions
    
    fine:
        adds the fine to previous Value
        checks if fine is more than 500

    stock:
        checks if books Stock is present
        Subtracts 1 book from the book

    Returns
    -------
    Transactions template
    """
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        fine = request.form.get('fine')
        paid = request.form.get('fine')

        new_member = Members(name=name, phone=phone, email=email, fine=fine, paid=paid, user_id=current_user.id)
        db.session.add(new_member)
        db.session.commit()

        flash('Member Added!', category='success')

    return render_template("add_members.html", user=current_user)


# Books
@operations.route('/add_books', methods=['GET', 'POST'])
@login_required
def books():
    if request.method == 'POST':
        title = request.form.get('title')
        authors = request.form.get('authors')
        isbn = request.form.get('isbn')
        publisher = request.form.get('publisher')
        stock = request.form.get('stock')
        data = request.form.get('data')
        payments = 0


        new_Book = Books(title=title, authors=authors, isbn=isbn,
                         publisher=publisher, stock=stock, data=data, user_id=current_user.id)
        db.session.add(new_Book)
        db.session.commit()

        flash('Book Added!', category='success')

    return render_template("add_books.html", user=current_user)


# Funtions for the Editing of the Books And Members
# Books
@operations.route('/update_books<string:bookID>', methods=['GET', 'POST'])
@login_required
def update_books(bookID):
    if request.method == 'POST':
        new_entry = request.form.get('new_entry')
        Column = request.form.get('flexRadioDefault')
        que = Books.query.filter_by(bookID=bookID)
        if Column == "title":
            que.update({Books.title: new_entry})
        elif Column == "stock":
            que.update({Books.stock: new_entry})
        elif Column == "publisher":
            que.update({Books.publisher: new_entry})
        elif Column == "authors":
            que.update({Books.authors: new_entry})
        elif Column == "payment":
            que.update({Books.payments: new_entry})
        else:
            flash("Some error occured")
        db.session.commit()
        flash('Book updated')
        return redirect(url_for("views.books"))

# Update
@operations.route('/update_member<string:memID>', methods=['GET', 'POST'])
@login_required
def update_member(memID):
    if request.method == 'POST':
        new_entry = request.form.get('new_entry')
        Column = request.form.get('flexRadioDefault')
        que = Members.query.filter_by(memID=memID)

        if Column == "name":
            que.update({Members.name: new_entry})
        elif Column == "phone":
            que.update({Members.phone: new_entry})
        elif Column == "email":
            que.update({Members.email: new_entry})
        elif Column == "fine":
            que.update({Members.fine: new_entry})
        elif Column == "paid":
            que.update({Members.paid: new_entry})
        else:
            flash("Some error occured")

        db.session.commit()
        flash('Member Details updated')
        return redirect(url_for("views.members"))


# Report
@operations.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    transactions = Transactions.query.all()
    memfreq = {}
    bookfreq = {}
    for tran in transactions:
        mem = Members.query.filter_by(memID=tran.mem_id).first()
        book = Books.query.filter_by(bookID=tran.book_id).first()
        if mem in memfreq:
            memfreq[mem] += 1
        else:
            memfreq[mem] = 1

        if book in bookfreq:
            bookfreq[book] += 1
        else:
            bookfreq[book] = 1

    # Filtering the top 10 Members and Books
    topmem = Counter(memfreq).most_common(10)
    topbook = Counter(bookfreq).most_common(10)

    # Images for the Graphs
    # Top Memebers
    nam_tra = []
    num_tra = []
    for i in range(len(topmem)):
        nam_tra.append(topmem[i][0].memID)
        num_tra.append(topmem[i][1])
    s = pd.Series(num_tra, nam_tra)
    fig, ax = plt.subplots()
    s.plot.bar()
    fig.savefig('manager/static/members')

    # Top Books
    nam_bok = []
    num_bok = []
    for i in range(len(topbook)):
        nam_bok.append(topbook[i][0].bookID)
        num_bok.append(topbook[i][1])

    s = pd.Series(num_bok, nam_bok)
    fig, ax = plt.subplots()
    s.plot.bar()
    fig.savefig('manager/static/books')

    return render_template("report.html", user=current_user, topmem=topmem, topbook=topbook)


# Search
@operations.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    books = Books.query.all()
    transactions = Transactions.query.all()
    members = Members.query.all()

    if request.method == 'POST':
        search_by = request.form.get('search')
        books = Books.query.filter(Books.title.like('%' + search_by + '%'))
        transactions = Transactions.query.filter(
            Transactions.book_name.like('%' + search_by + '%'))
        members = Members.query.filter(
            Members.name.like('%' + search_by + '%'))

    return render_template("search.html", user=current_user, books=books, transactions=transactions, members=members)


# For Interacting with the API
@operations.route('/import_api', methods=['GET', 'POST'])
@login_required
def import_api():
    if request.method == 'POST':
        search_by = request.form.get('search_by')
        search = request.form.get('search')
        stock = request.form.get('stock')
        data = request.form.get('data')

        BASE = "https://frappe.io/api/method/frappe-library/json?"
        response = requests.patch(BASE + search_by + "=" + search)
        response = response.json()["message"]

        for book in response:
            bokID = book["bookID"]
            tile = book["title"]
            authors = book["authors"]
            isbn = book['isbn']
            publisher = book["title"]

            if (Books.query.filter_by(bookID=bokID).first() and Books.query.filter_by(title=tile).first()):
                print("Book is there")
            else:
                new_Book = Books(bookID=bokID, title=tile, authors=authors, isbn=isbn,
                                 publisher=publisher, stock=stock, data=data, payments=0, user_id=current_user.id)
                db.session.add(new_Book)
                db.session.commit()

        flash('Added all the data!', category='success')

    return render_template("import_api.html", user=current_user)


# Funtions for Deletion
# Transactions
@operations.route('/transactions/delete/<string:transID>', methods=['POST'])
def delete_transactions(transID):
    tran = Transactions.query.get_or_404(transID)
    db.session.delete(tran)
    db.session.commit()
    flash('Transaction deleted.')
    return redirect(url_for("views.transactions"))

# Books
@operations.route('/delete/<string:bookID>', methods=['POST'])
def delete_books(bookID):
    Book = Books.query.get_or_404(bookID)
    db.session.delete(Book)
    db.session.commit()
    flash('Book deleted.')
    return redirect(url_for("views.home"))

# Members
@operations.route('/members/delete/<string:memID>', methods=['POST'])
def delete_member(memID):
    Member = Members.query.get_or_404(memID)
    db.session.delete(Member)
    db.session.commit()
    flash('Member deleted.')
    return redirect(url_for("views.members"))
