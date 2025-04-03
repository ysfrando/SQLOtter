import uuid
from typing import Optional, List
from datetime import datetime
from db import Database
from models import Wallet
from validators import InputValidator
from utils import setup_logger

class WalletRepository:
    """Repository for wallet operations with SQL Injection prevention"""
    
    logger = setup_logger("wallet_repo", log_file="logs/wallet_repo.log")
    
    def __init__(self, db: Database):
        """
        Initialize wallet repository
        
        Args:
            db: Database instance
        """
        self.db = db
        
    def create_wallet(
        self,
        user_id: str,
        currency: str,
        address: str
    ) -> Wallet:
        """
        Create a new wallet
        
        Args:
            user_id: User ID
            currency: Currency code (BTC, ETH, etc.)
            address: Cryptocurrency address
            
        Returns:
            Created wallet
        
        Raises:
            ValueError: If input validation fails
        """ 
        # Validate inputs
        if not InputValidator.validate_uuid(user_id):
            WalletRepository.logger.warning(f"Invalid user ID: {user_id}")
            raise ValueError("Invalid user ID format")
        
        if not InputValidator.validate_crypto_address(address, currency):
            WalletRepository.logger.warning(f"Invalid {currency} address format")
            raise ValueError("Invalid crypto address")
        
        # Create wallet using SQLAlchemy (safe from SQL injection)
        wallet = Wallet(
            id=str(uuid.uuid4()),
            user_id=user_id,
            currency=currency,
            address=address,
            balance=0.0
        )

        session = self.db.get_session()
        try:
            session.add(wallet)
            session.commit()
            return wallet
        except Exception as e:
            session.rollback()        
            WalletRepository.logger.error(f"Error creating wallet: {str(e)}")
            raise
        finally:
            session.close()
        
    def get_wallet_by_id(self, wallet_id: str) -> Optional[Wallet]:
        """
        Get wallet by ID
        
        Args:
            wallet_id: Wallet ID
            
        Returns:
            Wallet or None if not found
            
        Raises:
            ValueError: If wallet_id is invalid
        """
        # Validate wallet ID
        if not InputValidator.validate_uuid(wallet_id):
            WalletRepository.logger.warning(f"Invalid wallet ID: {wallet_id}")
            raise ValueError("Invalid wallet ID format")
        
        session = self.db.get_session()
        try:
            wallet = session.query(Wallet).filter(Wallet.id == wallet_id).first()
            return wallet
        finally:
            session.close()
            
    def get_user_wallets(self, user_id: str) -> List[Wallet]:
        """
        Get all wallets for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of wallets associated with user_id
            
        Raises:
            ValueError: If the user_id is invalid
        """
        # Validate user ID
        if not InputValidator.validate_uuid(user_id):
            WalletRepository.logger.warning(f"Invalid user ID: {user_id}")
            raise ValueError("Invalid user ID format")
        
        
        session = self.db.get_session()
        try:
            wallets = session.query(Wallet).filter(Wallet.user_id == user_id).all()
            return wallets
        finally:
            session.close()
            
        
    def update_wallet_balance(self, wallet_id: str, new_balance: float) -> bool:
        """
        Update wallet balance
        
        Args:
            wallet_id: Wallet ID
            new_balance: New balance value
        
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If wallet_id is invalid or balance is negative
        """
        # Validate inputs
        if not InputValidator.validate_uuid(wallet_id):
            WalletRepository.logger.warning(f"Invalid wallet ID: {wallet_id}")
            raise ValueError("Invalid wallet ID format")
        
        if new_balance < 0:
            raise ValueError("Balance cannot be negative")
        
        session = self.db.get_session()
        try:
            wallet = session.query(Wallet).filter(Wallet.id == wallet_id).first()
            if not wallet:
                raise False

            wallet.balance = new_balance
            wallet.updated_at = datetime.utcnow()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            WalletRepository.logger.error(f"Error updating wallet balance: {str(e)}")
            return False
        finally:
            session.close()