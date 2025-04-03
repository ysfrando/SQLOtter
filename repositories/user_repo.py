import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from db import Database
from models import User, Wallet, Transaction
from validators import InputValidator
from utils import setup_logger

class UserRepository:
    """Repository for user operations with SQL Injection prevention"""
    logger = setup_logger("user_repo", log_file="logs/user_repo.log")
    
    def __init__(self, db: Database):
        """
        Initialize user repository
        
        Args:
            db: Database instance
        """
        self.db = db
        
    def create_user(self, email: str, username: str, password_hash: str) -> User:
        """
        Create a new user
        
        Args:
            email: User email
            username: Username
            password_hash: Hashed password
        
        Returns:
            Create user
            
        Raises:
            ValueError: If input validation fails
        """
        # Validate inputs 
        if not InputValidator.validate_email(email):
            UserRepository.logger.warning(f"Invalid email format: {email}")
            raise ValueError("Invalid email format")

        if not InputValidator.validate_username(username):
            UserRepository.logger.warning(f"Invalid username: {username}")
            raise ValueError("Invalid username format") 
        
        # Create a user with SQLAlchemy (safe from SQLi)
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            username=username,
            password_hash=password_hash
        )
        
        session = self.db.get_session()
        try:
            session.add(user)
            session.commit()
            return user
        except Exception as e:
            session.rollback()
            UserRepository.logger.error(f"Error creating user: {str(e)}")
            raise
        finally:
            session.close()
            
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
        
        Returns:
            User or None if not found
            
        Raises
            ValueError: If user_id is invalid
        """
        if not InputValidator.validate_uuid(user_id):
            UserRepository.logger.warning(f"Invalid user ID: {user_id}")
            raise ValueError("Invalid user ID format")
        
        session = self.db.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            return user
        finally:
            session.close()
            
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: User's email
            
        Returns:
            Email or None if not found
        
        Raises:
            ValueError: If email is invalid
        """
        if not InputValidator.validate_email(email):
            UserRepository.logger.warning(f"Invalid email format: {email}")
            raise ValueError("Invalid email format")
        
        session = self.db.get_session()
        try:
            email = session.query(User).filter(User.email == email).first()
            return email
        finally:
            session.close()
    
    def search_users(self, search_term: str, limit: int = 10) -> List[User]:
        """
        Search users by username or email   
        
        Args:
            search_term: Search term
            limit: Max number of results
            
        Returns:
            List of matching users
        """
        # Sanitize search term
        search_term = InputValidator.sanitize_string(search_term)
        
        session = self.db.get_session()
        
        # Limit max results returned
        limit = min(max(1, limit), 100) # Between 1 and 100
        
        try:
            query = session.query(User).filter(
                User.username.ilike(f"%{search_term}%"),
                User.email.ilike(f"%{search_term}%")
            ).limit(limit)
            return query.all()
        finally:
            session.close()
            
    def update_user(self, user_id: str, fields: Dict[str, Any]) -> bool:
        """
        Update user fields
        
        Args:
            user_id: User ID
            fields: Dictionary of fields to update
        
        Returns:
            True if successul, False otherwise
            
        Raises:
            ValueError: If user_id is invalid or fields are invalid
        """
        # Validate user id
        if not InputValidator.validate_uuid(user_id):
            UserRepository.logger.warning(f"Invalid user ID: {user_id}")
            raise ValueError("Invalid user ID format")
        
        # Validate fields
        allowed_fields = {'email', 'username', 'is_active', 'is_verified'}
        update_data = {}
        
        for field, value in fields.items():
            if field not in allowed_fields:
                continue
            
            if field == 'email' and not InputValidator.validate_email(value):
                UserRepository.logger.warning(f"Invalid email address: {value}")
                raise ValueError("Invalid email format")
    
            if field == 'username' and not InputValidator.validate_username(value):
                UserRepository.logger.warning(f"Invalid username: {value}")
                raise ValueError("Invalid username format") 
            
            update_data[field] = value  
            
        if not update_data:
            return False
        
        session = self.db.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            for field, value in update_data.items():
                setattr(user, field, value)
                
            user.updated_at = datetime.utcnow()
            session.commit()
        except Exception as e:
            session.rollback()
            UserRepository.logger.error(f"Error updating user: {str(e)}")
        finally:
            session.close()