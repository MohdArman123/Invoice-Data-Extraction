from fastapi import APIRouter, Depends, File, UploadFile, Response, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from services.invoice_service import (
    process_invoice_upload,
    get_invoice_by_id,
    get_all_invoices
)

invoiceRouter = APIRouter(
    prefix='/api/invoice/v1',
    tags=['Invoice Extraction']
)

@invoiceRouter.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_invoice(
    file: UploadFile = File(...),
    response: Response = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and extract invoice data from PDF or image file
    
    This endpoint accepts PDF or image files (PNG, JPG, JPEG) and extracts
    key invoice information including:
    - Invoice number
    - Invoice date
    - Amount
    - Due date
    
    The extracted data is saved to the database and returned in the response.
    
    Parameters:
    - file: UploadFile - PDF or image file containing invoice data
    - response: FastAPI Response object
    - db: Async SQLAlchemy session dependency
    
    Returns:
    - JSON response with extracted invoice data
    
    Developer Info:
    - Created By: Mohd Arman
    - Date: October 2025
    """
    return await process_invoice_upload(file, response, db)

@invoiceRouter.get("/{invoice_id}", status_code=status.HTTP_200_OK)
async def get_invoice(
    invoice_id: str,
    response: Response = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch a single invoice by ID
    
    This endpoint retrieves detailed information about a specific invoice
    using its unique identifier.
    
    Parameters:
    - invoice_id: str - UUID of the invoice
    - response: FastAPI Response object
    - db: Async SQLAlchemy session dependency
    
    Returns:
    - JSON response with invoice details
    
    Developer Info:
    - Created By: Mohd Arman
    - Date: October 2025
    """
    return await get_invoice_by_id(invoice_id, response, db)

@invoiceRouter.get("/", status_code=status.HTTP_200_OK)
async def list_invoices(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    response: Response = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all invoices with pagination
    
    This endpoint retrieves a paginated list of all invoices in the database.
    
    Parameters:
    - skip: int - Number of records to skip (default: 0)
    - limit: int - Maximum number of records to return (default: 100, max: 1000)
    - response: FastAPI Response object
    - db: Async SQLAlchemy session dependency
    
    Returns:
    - JSON response with list of invoices and total count
    
    Developer Info:
    - Created By: Mohd Arman
    - Date: October 2025
    """
    return await get_all_invoices(response, db, skip, limit)