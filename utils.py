from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal
from typing import Tuple
from models import Account, Transaction
from storage import storage

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)

def process_transaction(
    account: Account,
    transaction_type: str,
    amount: Decimal,
    description: str,
    to_account_id: str = None
) -> Tuple[bool, str]:
    if transaction_type == 'deposit':
        account.balance += amount
        return True, "Deposit successful"
    
    elif transaction_type == 'withdrawal':
        if account.balance >= amount:
            account.balance -= amount
            return True, "Withdrawal successful"
        return False, "Insufficient funds"
    
    elif transaction_type == 'transfer':
        if not to_account_id:
            return False, "Recipient account not specified"
        
        to_account = storage.get_account(to_account_id)
        if not to_account:
            return False, "Recipient account not found"
        
        if account.balance >= amount:
            account.balance -= amount
            to_account.balance += amount
            return True, "Transfer successful"
        return False, "Insufficient funds"
    
    return False, "Invalid transaction type"
