from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import json
from sqlalchemy.sql import func

# Importing Models and Databse Settings (SQLAlchemy)
from .models import Books, Members, Transactions
from . import db
# from manager import create_app.app

# Adding to Routes
views = Blueprint('views', __name__)


@views.route('/ajax_approach')
def ajax_approach():
    return render_template('ajax_approach.html',user=current_user)

@views.route("/ajaxfile",methods=["POST","GET"])
def ajaxfile():
    try:
        if request.method == 'POST':
            draw = request.form['draw'] 
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]
            totalRecords = db.session.query(func.count(Books.bookID)).scalar()
            totalRecordwithFilter = len(Books.query.filter(Books.title.like("%" + searchValue +"%")).all())
            if searchValue=='':
                books = Books.query.all()[row:rowperpage+row]
            else:
                books = Books.query.filter(Books.title.like("%" + searchValue +"%")).all()[row:rowperpage+row] 
            data = []
            for row in books:
                data.append({
                    'title': row.title,
                    'authors': row.authors,
                    'publisher': row.publisher,
                    'stock': row.stock,
                    'data': row.data,
                })
            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)
    except Exception as e:
        print(e)
    finally:
        db.session.commit()



# Dashboard
@views.route('/', methods=['GET'])
@login_required
def index():
    total_payment = db.session.query(func.sum(Transactions.payments).label("total_payment"))
    top_members = db.session.query(Members).order_by(Members.paid.desc())
    top_books = db.session.query(Books).order_by(Books.payments.desc())
    top_titles=[]
    top_payments=[]
    for i in top_books:
        top_titles.append(i.title)
        top_payments.append(i.payments)
    top_names=[]
    top_paids=[]
    for i in top_members:    
        top_names.append(i.name)
        top_paids.append(i.paid)
    return render_template("index.html",top_titles=json.dumps(top_titles),top_names=json.dumps(top_names),top_paids=json.dumps(top_paids),top_payments=json.dumps(top_payments), user=current_user, total_payment=total_payment,top_members=top_members,top_books=top_books)




# Books
@views.route('/books', methods=['GET'])
@login_required
def books():
    all_books = db.session.query(Books).order_by(Books.date.desc()).all()
    return render_template("books.html",user=current_user, books = all_books)


# Members
@views.route('/members', methods=['GET'])
@login_required
def members():
    return render_template("members.html", user=current_user)


# Tranctions
@views.route('/transactions', methods=['GET'])
@login_required
def transactions():
    return render_template("transactions.html", user=current_user)

