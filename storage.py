from typing import Dict, List, Optional
from models import User, Account, Transaction
from app import db

class Storage:
    def create_user(self, user: User) -> User:
        db.session.add(user)
        db.session.commit()
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        return User.query.filter_by(username=username).first()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return User.query.get(user_id)

    def create_account(self, account: Account) -> Account:
        db.session.add(account)
        db.session.commit()
        return account

    def get_account(self, account_id: str) -> Optional[Account]:
        return Account.query.get(account_id)

    def get_user_accounts(self, user_id: str) -> List[Account]:
        return Account.query.filter_by(user_id=user_id).all()

    def create_transaction(self, transaction: Transaction) -> Transaction:
        db.session.add(transaction)
        db.session.commit()
        return transaction

    def get_account_transactions(self, account_id: str) -> List[Transaction]:
        return Transaction.query.filter(
            (Transaction.account_id == account_id) | 
            (Transaction.to_account_id == account_id)
        ).all()

# Initialize global storage
storage = Storage()