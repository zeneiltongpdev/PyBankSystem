from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal
from typing import Tuple
from models import Account

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)

def process_transaction(
    account: Account,
    transaction_type: str,
    amount: Decimal,
    description: str,
    to_account_number: str = None
) -> Tuple[bool, str]:
    if transaction_type == 'deposit':
        account.balance += amount
        return True, "Depósito realizado com sucesso"

    elif transaction_type == 'withdrawal':
        if account.balance >= amount:
            account.balance -= amount
            return True, "Saque realizado com sucesso"
        return False, "Saldo insuficiente"

    elif transaction_type == 'transfer':
        if not to_account_number:
            return False, "Número da conta de destino não especificado"

        to_account = Account.query.filter_by(account_number=to_account_number).first()
        if not to_account:
            return False, "Conta de destino não encontrada"

        if account.balance >= amount:
            account.balance -= amount
            to_account.balance += amount
            return True, "Transferência realizada com sucesso"
        return False, "Saldo insuficiente"

    return False, "Tipo de transação inválido"