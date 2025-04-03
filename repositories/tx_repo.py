import uuid
import sqlalchemy
from typing import Optional, List
from datetime import datetime
from db import Database
from models import User, Wallet, Transaction
from validators import InputValidator
from utils import setup_logger


class TransactionRepository:
    """Repository for transaction operations with SQL Injection prevention"""
    
    logger = setup_logger("transaction_repo", log_file="logs/transaction_repo.log")
    
    def __init__(self, db: Database):
        """
        Initialize transaction repository
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def create_transaction(
        self,
        user_id: str,
        wallet_id: str,
        transaction_type: str,
        amount: float,
        fee: float = 0.0,
        destination_address: str = None,
    ) -> Transaction:
        """
        Creating a new transaction
        
        Args:
            user_id: User ID
            wallet_id: Wallet ID
            transaction_type: Transaction type (deposit, withdrawal, transfer)
            amount: Transaction amount
            fee: Transaction fee
            destination_address: Destination address for withdrawals
            
        Returns:
            Created transaction
        
        Raises:
            ValueError: If input validation fails
        """
        if not InputValidator.validate_uuid(user_id):
            TransactionRepository.logger.warning(f"Invalid user ID: {user_id}")
            raise ValueError("Invalid user ID format")
        
        if not InputValidator.validate_uuid(wallet_id):
            TransactionRepository.logger.warning(f"Invalid wallet ID: {wallet_id}")
            raise ValueError("Invalid wallet ID format")
        
        # Ensure allowed transaction type
        if transaction_type not in ['deposit', 'withdrawal', 'tranfer']:
            raise ValueError("Invalid transaction type")
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if fee < 0:
            raise ValueError("Fee cannot be negative")
        
        if transaction_type == 'withdrawal' and destination_address:
            # For withdrawals, validaate the destination address
            if not InputValidator.validate_crypto_address(destination_address):
                TransactionRepository.logger.warning(f"Invalid destination address: {destination_address}")
                raise ValueError("Invalid destination address format")
            
        transaction = Transaction(
            id=str(uuid.uuid4()),
            user_id=user_id,
            wallet_id=wallet_id,
            transaction_type=transaction_type,
            amount=amount,
            fee=fee,
            destination_address=destination_address,
            status='pending'
        )
        
        session = self.db.get_session()
        try:
            session.add(transaction)
            session.commit()
            return transaction
        except Exception as e:
            session.rollback()
            TransactionRepository.logger.error(f"Error creating transaction: {str(e)}")
            raise
        
    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """
        Get transaction by ID
        
        Args:   
            transaction_id: Transaction ID
            
        Returns:
            Transaction or None if not found
            
        Raises:
            ValueError: If transaction id is invalid
        """
        # Validate transaction ID
        if not InputValidator.validate_uuid(transaction_id):
            TransactionRepository.logger.warning(f"Invalid transaction ID: {transaction_id}")
            raise ValueError("Invalid transaction ID format")
        
        session = self.db.get_session()
        try:
            transaction = session.query(Transaction).filter(
                Transaction.id == transaction_id
            ).first()
            return transaction
        finally:
            session.close()
            
    def get_user_transactions(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        transaction_type: str = None,
        status: str = None
    ) -> List[Transaction]:
        """
        Get transactions for a user with filtering and pagination
        
        Args:
            user_id: User ID
            limit: Max number of results
            offset: Pagination offset
            transaction_type: Filter by transaction type
            status: Filter by status
        
        Returns:
            List of transactions
            
        Raises:
            ValueError: If user_id is invalid
        """
        if not InputValidator.validate_uuid(user_id):
            TransactionRepository.logger.warning(f"Invalid user ID: {user_id}")
            raise ValueError("Invalid user ID format")
        
        session = self.db.get_session()
        try:
            limit = min((1, limit), 100) # Between 1 and 100
            offset = max(0, offset) # Desfine offset
            
            query = session.query(Transaction).filter(Transaction.user_id == user_id)
            
            if transaction_type:
                if transaction_type in ['deposit', 'withdrawal', 'transfer']:
                    query = query.filter(Transaction.transaction_type == transaction_type)
                    
            if status:
                if status in ['pending', 'completed', 'failed']:
                    query = query.filter(Transaction.status == status)
                    
            transactions = query.order_by(Transaction.created_at.desc()).limit(limit).offset(offset).all()
            return transactions
        finally:
            session.close()
            
    def update_transaction_status(self, transaction_id: str, status: str, tx_hash: str = None) -> bool:
        """
        Update transaction status
        
        Args:
            transaction_id: Transaction ID
            status: New status value
            tx_hash: Blockchain transaction hash
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If transaction_id is invalid or status is invalid
        """
        # Validate inputs
        if not InputValidator.validate_uuid(transaction_id):
            TransactionRepository.logger.warning(f"Invalid transaction id: {transaction_id}")
            raise ValueError("Invalid transaction ID format")
        
        if status not in ['pending', 'completed', 'failed']:
            TransactionRepository.logger.warning(f"Invalid transaction status: {status}")
            raise ValueError("Invalid transaction status")
        
        session = self.db.get_session()
        try:
            transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not transaction:
                return False
            
            transaction.status = status
            if tx_hash:
                transaction.tx_hash = tx_hash
                
            transaction.updated_at = datetime.utcnow()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            TransactionRepository.logger.error(f"Error updating transaction status: {str(e)}")
            raise
        finally:
            session.close()
            
    def search_transactions(
        self,
        search_term: str,
        limit: int = 20,
        user_id: str = None
    ) -> List[Transaction]:
        """
        Search transactions
        
        Args:
            search_term: Search term (transaction hash, address, etc.)
            limit: Maximum number of results
            user_id: Optional user ID to restrict results
            
        Returns:
            List of matching transactions
        """
        # Sanitize search term
        search_term = InputValidator.sanitize_string(search_term)
        
        if not InputValidator.validate_uuid(user_id):
            TransactionRepository.logger.warning(f"Invalid user ID: {user_id}")
            raise ValueError("Invalid user ID format")
        
        # Validate and sanitize limit
        limit = min(max(1, limit), 100)
        
        session = self.db.get_session()
        try:
            query = session.query(Transaction)

            if user_id:
                query = query.filter(Transaction.user_id == user_id)
            else:
                return []
            
            query = query.filter(
                sqlalchemy.or_(
                    Transaction.id.ilike(f"%{search_term}%"),
                    Transaction.tx_hash.ilike(f"%{search_term}%"),
                    Transaction.desination_address.ilike(f"%{search_term}%")
                )
            )
            
            transactions = query.limit(limit).all()
            
            return transactions
        finally:
            session.close()