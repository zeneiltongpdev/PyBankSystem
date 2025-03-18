from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app import db
from decimal import Decimal

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")

    def get_id(self):
        return str(self.id)

    def check_password(self, password):
        from utils import verify_password
        return verify_password(self.password_hash, password)

class Account(db.Model):
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    balance: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), default=Decimal('0'))
    account_type: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions_from = relationship("Transaction", 
                                   foreign_keys="Transaction.account_id",
                                   back_populates="account",
                                   cascade="all, delete-orphan")
    transactions_to = relationship("Transaction",
                                 foreign_keys="Transaction.to_account_id",
                                 back_populates="to_account")

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    transaction_type: Mapped[str] = mapped_column(String(20))
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    description: Mapped[str] = mapped_column(String(200))
    to_account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    account = relationship("Account", foreign_keys=[account_id], back_populates="transactions_from")
    to_account = relationship("Account", foreign_keys=[to_account_id], back_populates="transactions_to")