from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from flask_login import UserMixin

@dataclass
class User(UserMixin):
    id: str
    username: str
    password_hash: str
    email: str
    created_at: datetime = datetime.utcnow()

    def get_id(self):
        return str(self.id)

    def check_password(self, password):
        from utils import verify_password
        return verify_password(self.password_hash, password)

@dataclass
class Account:
    id: str
    user_id: str
    balance: Decimal
    account_type: str
    created_at: datetime = datetime.utcnow()

@dataclass
class Transaction:
    id: str
    account_id: str
    transaction_type: str  # 'deposit', 'withdrawal', 'transfer'
    amount: Decimal
    description: str
    to_account_id: Optional[str] = None
    created_at: datetime = datetime.utcnow()