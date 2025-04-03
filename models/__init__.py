from .user import User
from .wallet import Wallet
from .transaction import Transaction
from sqlalchemy.orm import declarative_base
Base = declarative_base()  # Define Base once here