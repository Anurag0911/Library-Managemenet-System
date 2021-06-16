from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
import json

# Importing the Model and the Database
from .models import Books, Members, Trans
from . import db

# For the Report Funtion
import requests
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt


# Adding to Routes
operations = Blueprint('operations', __name__)


# Funtions for the Editing of the Books And Members
# Books
@operations.route('/update_books<string:bookID>', methods=['GET', 'POST'])
@login_required
def update_books(bookID):
    # Handling the Post Method
    if request.method == 'POST':
        new_entry = request.form.get('new_entry')
        Column = request.form.get('flexRadioDefault')
        que = Books.query.filter_by(bookID=bookID)

        # Handling the Choice and passing the SQL query accordingly
        if Column == "title":
            que.update({Books.title: new_entry})
        elif Column == "stock":
            que.update({Books.stock: new_entry})
        elif Column == "publisher":
            que.update({Books.publisher: new_entry})
        elif Column == "authors":
            que.update({Books.authors: new_entry})
        else:
            flash("Some error occured")

        # commiting Update to the Database
        db.session.commit()
        flash('Book updated')
        return redirect(url_for("views.home"))

# Update
@operations.route('/update_member<string:memID>', methods=['GET', 'POST'])
@login_required
def update_member(memID):

    # Handling the Post Method
    if request.method == 'POST':
        new_entry = request.form.get('new_entry')
        Column = request.form.get('flexRadioDefault')
        que = Members.query.filter_by(memID=memID)

        # Handling the Choice and passing the SQL query accordingly
        if Column == "name":
            que.update({Members.name: new_entry})
        elif Column == "phone":
            que.update({Members.phone: new_entry})
        elif Column == "email":
            que.update({Members.email: new_entry})
        elif Column == "fine":
            que.update({Members.fine: new_entry})
        else:
            flash("Some error occured")

        # commiting Update to the Database
        db.session.commit()
        flash('Member Details updated')
        return redirect(url_for("views.members"))



# Report
@operations.route('/report', methods=['GET', 'POST'])
@login_required
def report():

    # Funtion for Top 10 Members and Books according to number of transactions
    trans = Trans.query.all()
    memfreq = {}
    bookfreq = {}
    for tran in trans:
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

    print("topbook")

    # Images for the Graphs
    # Top Memebers
    nam_tra = []
    num_tra = []
    for i in range(len(topmem)):
        print(topmem[i][0].name)
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
        print(topbook[i][0].title)
        nam_bok.append(topbook[i][0].bookID)
        num_bok.append(topbook[i][1])

    s = pd.Series(num_bok, nam_bok)
    fig, ax = plt.subplots()
    s.plot.bar()
    fig.savefig('manager/static/books')

    # Returning the Top 10 Members and books Along with User ID
    return render_template("report.html", user=current_user, topmem=topmem, topbook=topbook)




# Search
@operations.route('/search', methods=['GET', 'POST'])
@login_required
def search():

    # Taking all the Models
    books = Books.query.all()
    trans = Trans.query.all()
    members = Members.query.all()

    # Handling the POST reqest for the search term
    if request.method == 'POST':
        search_by = request.form.get('search')
        books = Books.query.filter(Books.title.like('%' + search_by + '%'))
        trans = Trans.query.filter(Trans.book_name.like('%' + search_by + '%'))
        members = Members.query.filter(Members.name.like('%' + search_by + '%'))

    # Returing the Search Results 
    return render_template("search.html", user=current_user, books=books, trans=trans, members=members)


# For Interacting with the API
@operations.route('/import_api', methods=['GET', 'POST'])
@login_required
def import_api():

    # Handling the POST Request for the search term
    if request.method == 'POST':
        search_by = request.form.get('search_by')
        search = request.form.get('search')
        stock = request.form.get('stock')
        data = request.form.get('data')

        # Making a Request for the required Request
        BASE = "https://frappe.io/api/method/frappe-library/json?"
        response = requests.patch(BASE + search_by + "=" + search)
        response = response.json()["message"]

        # Adding to the Database
        for book in response:
            bokID = book["bookID"]
            tile = book["title"]
            authors = book["authors"]
            isbn = book['isbn']
            publisher = book["title"]

            # if Books is Already present
            if (Books.query.filter_by(bookID=bokID).first() and Books.query.filter_by(title=tile).first()):
                print("Book is there")
                
            # if Books is Not present Adding them to the Database
            else:
                new_Book = Books(bookID=bokID, title=tile, authors=authors, isbn=isbn, publisher=publisher, stock=stock, data=data, user_id=current_user.id)
                db.session.add(new_Book)
                db.session.commit()
        
        # success Message
        flash('Added all the data!', category='success')

    return render_template("import_api.html", user=current_user)


# Funtions for Deletion
# Transactions
@operations.route('/trans/delete/<string:transID>', methods=['POST'])
# Funtions for the deletion of the Transaction
def delete_trans(transID):
    tran = Trans.query.get_or_404(transID)

    # Updating the Database
    db.session.delete(tran)
    db.session.commit()

    # Success Message
    flash('Transaction deleted.')
    return redirect(url_for("views.trans"))

# Books
@operations.route('/delete/<string:bookID>', methods=['POST'])
# Funtions for the deletion of the Book
def delete_books(bookID):

    # Book to Delete
    Book = Books.query.get_or_404(bookID)

    # Updating the Database
    db.session.delete(Book)
    db.session.commit()

    # Success Message
    flash('Book deleted.')
    return redirect(url_for("views.home"))

# Members
@operations.route('/members/delete/<string:memID>', methods=['POST'])
# Funtions for the deletion of the Member
def delete_member(memID):

    # Book to Delete
    Member = Members.query.get_or_404(memID)

    # Updating the Database
    db.session.delete(Member)
    db.session.commit()

    # Success Message
    flash('Member deleted.')
    return redirect(url_for("views.members"))
