from sqlalchemy import Column, String, DateTime, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from db.session import Base
from uuid import uuid4

def utc_now():
    """Return current UTC timestamp"""
    return datetime.utcnow()

class Invoice(Base):
    """
    Invoice model to store extracted invoice data
    """
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Extracted fields
    invoice_number = Column(String(100), nullable=True, index=True)
    invoice_date = Column(String(50), nullable=True)
    amount = Column(Float, nullable=True)
    due_date = Column(String(50), nullable=True)
    
    # Additional metadata
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    extracted_text = Column(Text, nullable=True)  # Store full extracted text
    extraction_method = Column(String(50), nullable=True)  # 'text' or 'ocr'
    
    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    def __repr__(self):
        return f"<Invoice(id={self.id}, invoice_number={self.invoice_number}, amount={self.amount})>"