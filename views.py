from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from forms import LoginForm, RegisterForm, AccountForm, TransactionForm
from models import User, Account, Transaction
from storage import storage
from decimal import Decimal
from utils import process_transaction
from app import db
import random
import string

# Blueprints
auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__)  # Remove url_prefix to allow root route

def generate_account_number():
    """Gera um número de conta único com 8 dígitos"""
    while True:
        # Gera um número de conta de 8 dígitos
        account_number = ''.join(random.choices(string.digits, k=8))
        # Verifica se já existe
        if not Account.query.filter_by(account_number=account_number).first():
            return account_number

# Auth routes
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Usuário ou senha inválidos', 'danger')
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash('Registro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema', 'info')
    return redirect(url_for('auth.login'))

# Main routes
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', accounts=accounts)

@main.route('/accounts', methods=['GET', 'POST'])
@login_required
def accounts():
    form = AccountForm()
    if form.validate_on_submit():
        account = Account(
            account_number=generate_account_number(),
            user_id=current_user.id,
            balance=Decimal('0'),
            account_type=form.account_type.data
        )
        db.session.add(account)
        db.session.commit()
        flash('Conta criada com sucesso!', 'success')
        return redirect(url_for('main.accounts'))

    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('accounts.html', accounts=accounts, form=form)

@main.route('/transactions/<int:account_id>', methods=['GET', 'POST'])
@login_required
def transactions(account_id):
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.id:
        flash('Conta não encontrada', 'danger')
        return redirect(url_for('main.accounts'))

    form = TransactionForm()
    if form.validate_on_submit():
        success, message = process_transaction(
            account,
            form.transaction_type.data,
            form.amount.data,
            form.description.data,
            form.to_account_number.data if form.transaction_type.data == 'transfer' else None
        )

        if success:
            transaction = Transaction(
                account_id=account_id,
                transaction_type=form.transaction_type.data,
                amount=form.amount.data,
                description=form.description.data,
                to_account_id=Account.query.filter_by(account_number=form.to_account_number.data).first().id
                if form.transaction_type.data == 'transfer' and form.to_account_number.data
                else None
            )
            db.session.add(transaction)
            db.session.commit()
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('main.transactions', account_id=account_id))

    transactions = Transaction.query.filter(
        (Transaction.account_id == account_id) | 
        (Transaction.to_account_id == account_id)
    ).all()
    return render_template('transactions.html', account=account, transactions=transactions, form=form)