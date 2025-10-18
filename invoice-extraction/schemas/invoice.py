from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class InvoiceExtractResponse(BaseModel):
    """Response model for extracted invoice data"""
    id: str
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    amount: Optional[float] = None
    due_date: Optional[str] = None
    file_name: str
    extraction_method: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class InvoiceListResponse(BaseModel):
    """Response model for listing invoices"""
    status: bool
    message: str
    code: Optional[str] = None
    data: list[InvoiceExtractResponse]
    total: int

class InvoiceDetailResponse(BaseModel):
    """Response model for single invoice details"""
    status: bool
    message: str
    code: Optional[str] = None
    data: InvoiceExtractResponse

class UploadResponse(BaseModel):
    """Response model for file upload"""
    status: bool
    message: str
    code: Optional[str] = None
    data: Optional[InvoiceExtractResponse] = None