from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
import json
import requests
from collections import Counter

from .models import Books, Members, Trans
from . import db

operations = Blueprint('operations', __name__)


# Report
@operations.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    trans = Trans.query.all()
    memfreq = {}
    bookfreq = {}
    for tran in trans:
        mem = Members.query.filter_by(memID = tran.mem_id).first()
        book = Books.query.filter_by(bookID = tran.book_id).first()
        if mem in memfreq:
            memfreq[mem] += 1
        else:
            memfreq[mem] = 1
        
        if book in bookfreq:
            bookfreq[book] += 1
        else:
            bookfreq[book] = 1
    topmem = Counter(memfreq).most_common(10) 
    topbook = Counter(bookfreq).most_common(10)
    return render_template("report.html", user=current_user,topmem=topmem,topbook=topbook)

# search
@operations.route('/search', methods=['GET', 'POST'])
@login_required
def trans():
    books = Books.query.all()
    trans = Trans.query.all()
    members = Members.query.all()
    if request.method == 'POST':
        search_by = request.form.get('search')
        books = Books.query.filter(Books.title.like('%' + search_by + '%'))

        trans= Trans.query.filter(Trans.book_name.like('%' + search_by + '%'))
        members = Members.query.filter(
            Members.name.like('%' + search_by + '%'))

    return render_template("search.html", user=current_user, books=books, trans=trans, members=members)


# for the API
@operations.route('/import_api', methods=['GET', 'POST'])
@login_required
def import_api():
    # https://frappe.io/api/method/frappe-library/json?authors=j

    if request.method == 'POST':

        search_by = request.form.get('search_by')
        search = request.form.get('search')

        BASE = "https://frappe.io/api/method/frappe-library/json?"

        print(BASE + search_by + "=" + search)

        response = requests.patch(BASE + search_by + "=" + search)
        # print(response.json()["message"])
        response = response.json()["message"]
        # print(len(response))

        for book in response:
            bokID = book["bookID"]
            tile = book["title"]
            authors = book["authors"]
            isbn = book['isbn']
            publisher = book["title"]
            num_pages = "jslfkd"
            stock = "50"
            data = "book of this lib"
            print(book["bookID"])
            print(book["title"])

            if (Books.query.filter_by(bookID=bokID).first() and Books.query.filter_by(title=tile).first()):
                print("these is one ")
            else:
                new_Book = Books(bookID=bokID, title=tile, authors=authors, isbn=isbn, publisher=publisher,
                                 num_pages=num_pages, stock=stock, data=data, user_id=current_user.id)
                db.session.add(new_Book)
                db.session.commit()
        flash('Added all the data!', category='success')

    return render_template("import_api.html", user=current_user)


# Deletions

@operations.route('/trans/delete/<string:transID>', methods=['POST'])
def delete_trans(transID):
    tran = Trans.query.get_or_404(transID)
    db.session.delete(tran)
    db.session.commit()
    flash('Transaction deleted.')
    return redirect(url_for("views.trans"))


@operations.route('/delete/<string:bookID>', methods=['POST'])
def delete_books(bookID):
    Book = Books.query.get_or_404(bookID)
    db.session.delete(Book)
    db.session.commit()
    flash('Book deleted.')
    return redirect(url_for("views.home"))


@operations.route('/members/delete/<string:memID>', methods=['POST'])
def delete_member(memID):
    Member = Members.query.get_or_404(memID)
    db.session.delete(Member)
    db.session.commit()
    flash('Member deleted.')
    return redirect(url_for("views.members"))
