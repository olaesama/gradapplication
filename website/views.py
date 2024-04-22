from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Trade, Stock, UserBalance
from . import db
import json


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')  
        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id) 
            db.session.add(new_note)  
            db.session.commit()
            flash('Note added!', category='success')


    user_balance = current_user.user_balance or UserBalance(user_id=current_user.id, balance=0.0)
    db.session.add(user_balance)
    db.session.commit()

    return render_template("home.html", user=current_user, abs=abs)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/trade', methods=['GET', 'POST'])
@login_required
def trade():
    if request.method == 'POST':
        stock_symbol = request.form.get('stock_symbol').upper()
        action = request.form.get('action')
        quantity = int(request.form.get('quantity'))

        stock = Stock.query.filter_by(symbol=stock_symbol).first()
        if not stock:
            stock = Stock(symbol=stock_symbol)
            db.session.add(stock)
            db.session.commit()

        user_balance = current_user.user_balance or UserBalance(user_id=current_user.id, balance=0.0)

        if action == 'buy':
            user_balance.balance -= quantity
        else:
            user_balance.balance += quantity

        db.session.add(user_balance)

        trade = Trade(user_id=current_user.id, stock_id=stock.id, action=action, quantity=quantity)
        db.session.add(trade)
        db.session.commit()
        flash('Trade successful!', category='success')

    return render_template('trade.html', user=current_user)

@views.route('/transactions')
@login_required
def transactions():
    trades = Trade.query.filter_by(user_id=current_user.id).all()
    return render_template('transactions.html', user=current_user, trades=trades, Stock=Stock)  
