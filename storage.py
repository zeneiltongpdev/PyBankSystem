from typing import Dict, List, Optional
from models import User, Account, Transaction
import uuid

class Storage:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.accounts: Dict[str, Account] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.username_to_user: Dict[str, User] = {}

    def create_user(self, user: User) -> User:
        user.id = str(uuid.uuid4())
        self.users[user.id] = user
        self.username_to_user[user.username] = user
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.username_to_user.get(username)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def create_account(self, account: Account) -> Account:
        account.id = str(uuid.uuid4())
        self.accounts[account.id] = account
        return account

    def get_account(self, account_id: str) -> Optional[Account]:
        return self.accounts.get(account_id)

    def get_user_accounts(self, user_id: str) -> List[Account]:
        return [acc for acc in self.accounts.values() if acc.user_id == user_id]

    def create_transaction(self, transaction: Transaction) -> Transaction:
        transaction.id = str(uuid.uuid4())
        self.transactions[transaction.id] = transaction
        return transaction

    def get_account_transactions(self, account_id: str) -> List[Transaction]:
        return [
            trans for trans in self.transactions.values()
            if trans.account_id == account_id or trans.to_account_id == account_id
        ]

# Initialize global storage
storage = Storage()
