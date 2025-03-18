from flask_restx import Resource, Namespace
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized
from models import User, Account, Transaction
from schemas import UserSchema, LoginSchema, AccountSchema, TransactionSchema
from storage import storage
from utils import hash_password, verify_password, process_transaction
import logging

logger = logging.getLogger(__name__)

def initialize_routes(api):
    # Create namespaces
    auth_ns = api.namespace('auth', description='Authentication operations')
    account_ns = api.namespace('accounts', description='Account operations')
    transaction_ns = api.namespace('transactions', description='Transaction operations')

    @auth_ns.route('/register')
    class Register(Resource):
        @api.expect(api.model('RegisterUser', UserSchema().fields))
        def post(self):
            try:
                data = UserSchema().load(api.payload)
                if storage.get_user_by_username(data['username']):
                    raise BadRequest('Username already exists')

                user = User(
                    id='',  # Will be set by storage
                    username=data['username'],
                    password_hash=hash_password(data['password']),
                    email=data['email']
                )
                storage.create_user(user)
                return {'message': 'User registered successfully'}, 201
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                raise BadRequest(str(e))

    @auth_ns.route('/login')
    class Login(Resource):
        @api.expect(api.model('LoginUser', LoginSchema().fields))
        def post(self):
            try:
                data = LoginSchema().load(api.payload)
                user = storage.get_user_by_username(data['username'])
                
                if not user or not verify_password(user.password_hash, data['password']):
                    raise Unauthorized('Invalid credentials')

                access_token = create_access_token(identity=user.id)
                return {'access_token': access_token}, 200
            except Exception as e:
                logger.error(f"Login error: {str(e)}")
                raise Unauthorized(str(e))

    @account_ns.route('')
    class AccountList(Resource):
        @jwt_required()
        @api.expect(api.model('CreateAccount', AccountSchema().fields))
        def post(self):
            try:
                user_id = get_jwt_identity()
                data = AccountSchema().load(api.payload)
                
                account = Account(
                    id='',  # Will be set by storage
                    user_id=user_id,
                    balance=0,
                    account_type=data['account_type']
                )
                storage.create_account(account)
                return {'message': 'Account created successfully', 'account_id': account.id}, 201
            except Exception as e:
                logger.error(f"Account creation error: {str(e)}")
                raise BadRequest(str(e))

        @jwt_required()
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
                logger.error(f"Account retrieval error: {str(e)}")
                raise BadRequest(str(e))

    @transaction_ns.route('/<account_id>')
    class TransactionResource(Resource):
        @jwt_required()
        @api.expect(api.model('CreateTransaction', TransactionSchema().fields))
        def post(self, account_id):
            try:
                user_id = get_jwt_identity()
                account = storage.get_account(account_id)
                
                if not account or account.user_id != user_id:
                    raise NotFound('Account not found')

                data = TransactionSchema().load(api.payload)
                success, message = process_transaction(
                    account,
                    data['transaction_type'],
                    data['amount'],
                    data['description'],
                    data.get('to_account_id')
                )

                if not success:
                    raise BadRequest(message)

                transaction = Transaction(
                    id='',  # Will be set by storage
                    account_id=account_id,
                    transaction_type=data['transaction_type'],
                    amount=data['amount'],
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
                logger.error(f"Transaction error: {str(e)}")
                raise BadRequest(str(e))

        @jwt_required()
        def get(self, account_id):
            try:
                user_id = get_jwt_identity()
                account = storage.get_account(account_id)
                
                if not account or account.user_id != user_id:
                    raise NotFound('Account not found')

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
                logger.error(f"Transaction retrieval error: {str(e)}")
                raise BadRequest(str(e))
