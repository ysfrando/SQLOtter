import uuid
from datetime import datetime
from models import Base
from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class Transaction(Base):
    """Transaction model for crypto exchange transactions between users"""
    __tablename__ = 'transactions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    wallet_id = Column(String(36), ForeignKey('wallets.id'), nullable=False)
    transaction_type = Column(String(20), nullable=False) # deposit, withdrawal, transfer
    amount = Column(Float, nullable=False)
    fee = Column(Float, default=0.0)
    desination_address = Column(String(255), nullable=True) # For withdrawals
    tx_hash = Column(String(255), nullable=True) # Blockchain transaction hash
    status = Column(String(255), default='pending') # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    wallet = relationship("Wallet", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id='{self.id}', type='{self.transaction_type}', amount='{self.amount}', status='{self.status}')>"

    