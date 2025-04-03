import re
import uuid
from utils.logger import setup_logger

class InputValidator:
    """Input validation utilities to prevent SQL injections"""
    
    # Initialize the logger for this class
    logger = setup_logger(logger_name="input_validator")
    
    @staticmethod
    def validate_uuid(value: str) -> bool:
        """
        Validate a UUID string
        
        Args:
            value: UUID string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            uuid.UUID(value) # Try converting to UUID
            return True
        except ValueError:
            return False
        
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email formats
        
        Args:
            email: Email to validate
        
        Returns:
            True if valid, False otherwise
        """    
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        valid_email = bool(re.match(pattern, email))
        
        return valid_email
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validate username format
        
        Args:
            username: Username to validate

        Returns;
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._-]{3,50}$'
        valid_uname = bool(re.match(pattern, username))
        
        return valid_uname
    
    @staticmethod
    def validate_crypto_address(address: str, currency: str = None) -> bool:
        """
        Validate cryptocurrency address format
        
        Args:
            address: Crypto address to validate
            currency: Currency code (BTC, ETH, etc.)
        
        Returns:
            True if valid, False otherwise
        """
        # Currency specific patterns
        patterns = {
            'BTC': r'^(bc1|[13])[a-zA-H-HJ-NP-Z0-9]{25,39}$',
            'ETH': r'^0x[a-fA-F0-9]{40}$',
            'LTC': r'^[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}$',
            'DOGE': r'^D{1}[5-9A-HJ-NP-U]{1}[1-9A-HJ-NP-Za-km-z]{32}$',
            'XRP': r'^r[0-9a-zA-Z]{24,34}$'
        }
        
        # If currency is specified, check that specific pattern
        if currency and currency in patterns:
            return bool(re.match(patterns[currency], address))
        
        # Otherwise check all patterns
        for pattern in patterns.values():
            if re.match(pattern, address):
                return True 
            
        return False
    
    @staticmethod   
    def sanitize_string(value: str) -> str:
        """
        Sanitize a string by removing dangerous characters
        Note: This is a very basic sanitization func example. 
              In practice, use parameterized queries, and other things 
              like sanitization are used as defense-in-depth.
              
        Args:
            value: String to sanitize
        
        Returns:
            Sanitized string
        """
        # Remove SQL injection characters
        sanitized = re.sub(r"[';\"\\]", '', value)
        return sanitized