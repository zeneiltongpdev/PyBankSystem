from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

@dataclass
class User:
    id: str
    username: str
    password_hash: str
    email: str
    created_at: datetime = datetime.utcnow()

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
