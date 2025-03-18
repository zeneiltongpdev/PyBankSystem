from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from forms import LoginForm, RegisterForm, AccountForm, TransactionForm
from models import User, Account, Transaction
from storage import storage
from decimal import Decimal
from utils import process_transaction

# Blueprints
auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__)  # Remove url_prefix to allow root route

# Auth routes
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = storage.get_user_by_username(form.username.data)
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
            id='',
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        storage.create_user(user)
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
    accounts = storage.get_user_accounts(current_user.id)
    return render_template('dashboard.html', accounts=accounts)

@main.route('/accounts', methods=['GET', 'POST'])
@login_required
def accounts():
    form = AccountForm()
    if form.validate_on_submit():
        account = Account(
            id='',
            user_id=current_user.id,
            balance=Decimal('0'),
            account_type=form.account_type.data
        )
        storage.create_account(account)
        flash('Conta criada com sucesso!', 'success')
        return redirect(url_for('main.accounts'))

    accounts = storage.get_user_accounts(current_user.id)
    return render_template('accounts.html', accounts=accounts, form=form)

@main.route('/transactions/<account_id>', methods=['GET', 'POST'])
@login_required
def transactions(account_id):
    account = storage.get_account(account_id)
    if not account or account.user_id != current_user.id:
        flash('Conta não encontrada', 'danger')
        return redirect(url_for('main.accounts'))

    form = TransactionForm()
    if form.validate_on_submit():
        success, message = process_transaction(
            account,
            form.transaction_type.data,
            form.amount.data,
            form.description.data,
            form.to_account_id.data if form.transaction_type.data == 'transfer' else None
        )

        if success:
            transaction = Transaction(
                id='',
                account_id=account_id,
                transaction_type=form.transaction_type.data,
                amount=form.amount.data,
                description=form.description.data,
                to_account_id=form.to_account_id.data if form.transaction_type.data == 'transfer' else None
            )
            storage.create_transaction(transaction)
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('main.transactions', account_id=account_id))

    transactions = storage.get_account_transactions(account_id)
    return render_template('transactions.html', account=account, transactions=transactions, form=form)