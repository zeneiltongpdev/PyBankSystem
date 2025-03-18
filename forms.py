from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from storage import storage

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
        if storage.get_user_by_username(field.data):
            raise ValidationError('Este nome de usuário já está em uso')

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
    to_account_id = StringField('Conta de Destino (apenas para transferências)')
    submit = SubmitField('Realizar Transação')
