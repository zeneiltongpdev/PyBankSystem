from marshmallow import Schema, fields, validates, ValidationError
from decimal import Decimal

class UserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    email = fields.Email(required=True)

class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class AccountSchema(Schema):
    account_type = fields.Str(required=True)

    @validates('account_type')
    def validate_account_type(self, value):
        if value not in ['savings', 'checking']:
            raise ValidationError('Invalid account type')

class TransactionSchema(Schema):
    transaction_type = fields.Str(required=True)
    amount = fields.Decimal(required=True)
    description = fields.Str(required=True)
    to_account_id = fields.Str(required=False)

    @validates('transaction_type')
    def validate_transaction_type(self, value):
        if value not in ['deposit', 'withdrawal', 'transfer']:
            raise ValidationError('Invalid transaction type')

    @validates('amount')
    def validate_amount(self, value):
        if value <= Decimal('0'):
            raise ValidationError('Amount must be greater than 0')
