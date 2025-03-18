from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized
from models import User, Account, Transaction
from schemas import UserSchema, LoginSchema, AccountSchema, TransactionSchema
from storage import storage
from utils import hash_password, verify_password, process_transaction
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

def initialize_routes(api):
    # Create namespaces
    auth_ns = api.namespace('auth', description='Operações de autenticação')
    account_ns = api.namespace('accounts', description='Operações de conta')
    transaction_ns = api.namespace('transactions', description='Operações de transação')

    # Add namespaces explicitly to the API
    api.add_namespace(auth_ns)
    api.add_namespace(account_ns)
    api.add_namespace(transaction_ns)

    logger.info("Namespaces registrados: auth, accounts, transactions")

    # Define models for swagger documentation
    user_model = api.model('User', {
        'username': fields.String(required=True, description='Nome de usuário'),
        'password': fields.String(required=True, description='Senha'),
        'email': fields.String(required=True, description='Email')
    })

    login_model = api.model('Login', {
        'username': fields.String(required=True, description='Nome de usuário'),
        'password': fields.String(required=True, description='Senha')
    })

    account_model = api.model('Account', {
        'account_type': fields.String(required=True, description='Tipo de conta (savings/checking)',
                                    enum=['savings', 'checking'])
    })

    transaction_model = api.model('Transaction', {
        'transaction_type': fields.String(required=True,
                                        description='Tipo de transação (deposit/withdrawal/transfer)',
                                        enum=['deposit', 'withdrawal', 'transfer']),
        'amount': fields.Float(required=True, description='Valor da transação'),
        'description': fields.String(required=True, description='Descrição da transação'),
        'to_account_id': fields.String(required=False, description='ID da conta de destino (para transferências)')
    })

    @auth_ns.route('/register')
    class Register(Resource):
        @api.expect(user_model)
        @api.response(201, 'Usuário registrado com sucesso')
        @api.response(400, 'Dados inválidos')
        def post(self):
            try:
                data = UserSchema().load(api.payload)
                if storage.get_user_by_username(data['username']):
                    raise BadRequest('Nome de usuário já existe')

                user = User(
                    id='',  # Will be set by storage
                    username=data['username'],
                    password_hash=hash_password(data['password']),
                    email=data['email']
                )
                storage.create_user(user)
                return {'message': 'Usuário registrado com sucesso'}, 201
            except Exception as e:
                logger.error(f"Erro no registro: {str(e)}")
                raise BadRequest(str(e))

    @auth_ns.route('/login')
    class Login(Resource):
        @api.expect(login_model)
        @api.response(200, 'Login realizado com sucesso')
        @api.response(401, 'Credenciais inválidas')
        def post(self):
            try:
                data = LoginSchema().load(api.payload)
                user = storage.get_user_by_username(data['username'])

                if not user or not verify_password(user.password_hash, data['password']):
                    raise Unauthorized('Credenciais inválidas')

                access_token = create_access_token(identity=user.id)
                return {'access_token': access_token}, 200
            except Exception as e:
                logger.error(f"Erro no login: {str(e)}")
                raise Unauthorized(str(e))

    @account_ns.route('')
    class AccountList(Resource):
        @jwt_required()
        @api.expect(account_model)
        @api.response(201, 'Conta criada com sucesso')
        @api.response(400, 'Dados inválidos')
        def post(self):
            try:
                user_id = get_jwt_identity()
                data = AccountSchema().load(api.payload)

                account = Account(
                    id='',  # Will be set by storage
                    user_id=user_id,
                    balance=Decimal('0'),
                    account_type=data['account_type']
                )
                storage.create_account(account)
                return {'message': 'Conta criada com sucesso', 'account_id': account.id}, 201
            except Exception as e:
                logger.error(f"Erro na criação da conta: {str(e)}")
                raise BadRequest(str(e))

        @jwt_required()
        @api.response(200, 'Lista de contas')
        def get(self):
            try:
                user_id = get_jwt_identity()
                accounts = storage.get_user_accounts(user_id)
                return [{
                    'id': acc.id,
                    'type': acc.account_type,
                    'balance': str(acc.balance)
                } for acc in accounts], 200
            except Exception as e:
                logger.error(f"Erro na listagem de contas: {str(e)}")
                raise BadRequest(str(e))

    @transaction_ns.route('/<account_id>')
    class TransactionResource(Resource):
        @jwt_required()
        @api.expect(transaction_model)
        @api.response(200, 'Transação realizada com sucesso')
        @api.response(400, 'Dados inválidos ou saldo insuficiente')
        @api.response(404, 'Conta não encontrada')
        def post(self, account_id):
            try:
                user_id = get_jwt_identity()
                account = storage.get_account(account_id)

                if not account or account.user_id != user_id:
                    raise NotFound('Conta não encontrada')

                data = TransactionSchema().load(api.payload)
                success, message = process_transaction(
                    account,
                    data['transaction_type'],
                    Decimal(str(data['amount'])),
                    data['description'],
                    data.get('to_account_id')
                )

                if not success:
                    raise BadRequest(message)

                transaction = Transaction(
                    id='',  # Will be set by storage
                    account_id=account_id,
                    transaction_type=data['transaction_type'],
                    amount=Decimal(str(data['amount'])),
                    description=data['description'],
                    to_account_id=data.get('to_account_id')
                )
                storage.create_transaction(transaction)

                return {
                    'message': message,
                    'transaction_id': transaction.id,
                    'new_balance': str(account.balance)
                }, 200
            except Exception as e:
                logger.error(f"Erro na transação: {str(e)}")
                if isinstance(e, NotFound):
                    raise
                raise BadRequest(str(e))

        @jwt_required()
        @api.response(200, 'Lista de transações')
        @api.response(404, 'Conta não encontrada')
        def get(self, account_id):
            try:
                user_id = get_jwt_identity()
                account = storage.get_account(account_id)

                if not account or account.user_id != user_id:
                    raise NotFound('Conta não encontrada')

                transactions = storage.get_account_transactions(account_id)
                return [{
                    'id': t.id,
                    'type': t.transaction_type,
                    'amount': str(t.amount),
                    'description': t.description,
                    'created_at': t.created_at.isoformat(),
                    'to_account_id': t.to_account_id
                } for t in transactions], 200
            except Exception as e:
                logger.error(f"Erro na listagem de transações: {str(e)}")
                if isinstance(e, NotFound):
                    raise
                raise BadRequest(str(e))

    # Log registered routes
    logger.info("Rotas registradas:")
    for rule in api.app.url_map.iter_rules():
        logger.info(f"  {rule.endpoint}: {rule.rule}")