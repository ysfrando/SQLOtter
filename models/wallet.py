import uuid
from datetime import datetime
from models import Base
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class Wallet(Base):
    """Wallet model for crypto exchange user wallets"""
    __tablename__ = 'wallets'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    currency = Column(String(10), nullable=False) # BTC, ETH, etc.
    address = Column(String(255), nullable=False)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet")
    
    def __repr__(self):
        return f"<Wallet(id='{self.id}', user_id='{self.user_id}', currency='{self.currency}', balance='{self.balance}')>"