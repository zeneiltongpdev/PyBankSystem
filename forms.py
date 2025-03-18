from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User, Account

class LoginForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class RegisterForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[
        DataRequired(),
        Length(min=3, max=20)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm = PasswordField(
        'Confirmar Senha',
        validators=[
            DataRequired(),
            EqualTo('password', message='As senhas devem ser iguais')
        ]
    )
    submit = SubmitField('Registrar')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Este nome de usuário já está em uso')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Este email já está em uso')

class AccountForm(FlaskForm):
    account_type = SelectField(
        'Tipo de Conta',
        choices=[
            ('savings', 'Poupança'),
            ('checking', 'Corrente')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Criar Conta')

class TransactionForm(FlaskForm):
    transaction_type = SelectField(
        'Tipo de Transação',
        choices=[
            ('deposit', 'Depósito'),
            ('withdrawal', 'Saque'),
            ('transfer', 'Transferência')
        ],
        validators=[DataRequired()]
    )
    amount = DecimalField('Valor', validators=[DataRequired()])
    description = StringField('Descrição', validators=[DataRequired()])
    to_account_number = StringField('Número da Conta de Destino (apenas para transferências)')
    submit = SubmitField('Realizar Transação')

    def validate_to_account_number(self, field):
        if self.transaction_type.data == 'transfer':
            if not field.data:
                raise ValidationError('Número da conta de destino é obrigatório para transferências')
            account = Account.query.filter_by(account_number=field.data).first()
            if not account:
                raise ValidationError('Conta de destino não encontrada')