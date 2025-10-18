import os
from typing import Optional
from uuid import UUID
from fastapi import Response, status, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.invoice import Invoice
from utils.invoice_extractor import InvoiceExtractor
from utils.log_handler import handle_db_exceptions, prepare_response
from api_messages_and_codes.invoice import api_messages, api_codes
from config import settings

# Initialize invoice extractor
extractor = InvoiceExtractor()

async def process_invoice_upload(
    file: UploadFile,
    response: Response,
    db: AsyncSession
) -> dict:
    """
    Process uploaded invoice file and extract data
    
    Args:
        file: Uploaded file object
        response: FastAPI Response object
        db: Database session
    
    Returns:
        dict: Response with extracted invoice data
    """
    try:
        # Validate file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return await prepare_response(
                False,
                api_messages.INVALID_FILE_TYPE,
                api_codes.INVALID_FILE_TYPE
            )
        
        # Create uploads directory if it doesn't exist
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        
        # Save uploaded file temporarily
        file_path = os.path.join(settings.UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            
            # Check file size
            if len(content) > settings.MAX_UPLOAD_SIZE:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return await prepare_response(
                    False,
                    api_messages.FILE_TOO_LARGE,
                    api_codes.FILE_TOO_LARGE
                )
            
            buffer.write(content)
        
        # Extract invoice data
        extracted_data = await extractor.extract_invoice_data(file_path, file_extension)
        print(f"Extracted text: {extracted_data['extracted_text'][:500]}...")  # Log first 500 chars
        print(f"Extraction method: {extracted_data['extraction_method']}")
        # Check if text was extracted
        if not extracted_data['extracted_text']:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return await prepare_response(
                False,
                api_messages.NO_TEXT_EXTRACTED,
                api_codes.NO_TEXT_EXTRACTED
            )
        
        # Save to database
        new_invoice = Invoice(
            invoice_number=extracted_data['invoice_number'],
            invoice_date=extracted_data['invoice_date'],
            amount=extracted_data['amount'],
            due_date=extracted_data['due_date'],
            file_name=file.filename,
            file_path=file_path,
            extracted_text=extracted_data['extracted_text'],
            extraction_method=extracted_data['extraction_method']
        )
        
        db.add(new_invoice)
        await db.commit()
        await db.refresh(new_invoice)
        
        # Prepare response data
        response_data = {
            'id': str(new_invoice.id),
            'invoice_number': new_invoice.invoice_number,
            'invoice_date': new_invoice.invoice_date,
            'amount': new_invoice.amount,
            'due_date': new_invoice.due_date,
            'file_name': new_invoice.file_name,
            'extraction_method': new_invoice.extraction_method,
            'created_at': new_invoice.created_at
        }
        
        response.status_code = status.HTTP_201_CREATED
        return await prepare_response(
            True,
            api_messages.INVOICE_EXTRACTED_SUCCESS,
            api_codes.INVOICE_EXTRACTED_SUCCESS,
            data=response_data
        )
    
    except Exception as error:
        # Clean up file if error occurs
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        # if os.path.exists(file_path):
        #     os.remove(file_path)
        return await handle_db_exceptions(error, response)

async def get_invoice_by_id(
    invoice_id: str,
    response: Response,
    db: AsyncSession
) -> dict:
    """
    Fetch a single invoice by ID
    
    Args:
        invoice_id: UUID of the invoice
        response: FastAPI Response object
        db: Database session
    
    Returns:
        dict: Response with invoice data
    """
    try:
        # Validate UUID
        try:
            uuid_obj = UUID(invoice_id)
        except ValueError:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return await prepare_response(
                False,
                "Invalid invoice ID format",
                api_codes.INVOICE_NOT_FOUND
            )
        
        # Query database
        result = await db.execute(
            select(Invoice).where(Invoice.id == uuid_obj)
        )
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            response.status_code = status.HTTP_404_NOT_FOUND
            return await prepare_response(
                False,
                api_messages.INVOICE_NOT_FOUND,
                api_codes.INVOICE_NOT_FOUND
            )
        
        # Prepare response data
        response_data = {
            'id': str(invoice.id),
            'invoice_number': invoice.invoice_number,
            'invoice_date': invoice.invoice_date,
            'amount': invoice.amount,
            'due_date': invoice.due_date,
            'file_name': invoice.file_name,
            'extraction_method': invoice.extraction_method,
            'created_at': invoice.created_at
        }
        
        return await prepare_response(
            True,
            api_messages.INVOICE_FETCH_SUCCESS,
            api_codes.INVOICE_FETCH_SUCCESS,
            data=response_data
        )
    
    except Exception as error:
        return await handle_db_exceptions(error, response)

async def get_all_invoices(
    response: Response,
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> dict:
    """
    Fetch all invoices with pagination
    
    Args:
        response: FastAPI Response object
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        dict: Response with list of invoices
    """
    try:
        # Get total count
        count_result = await db.execute(select(Invoice))
        total = len(count_result.scalars().all())
        
        # Get paginated invoices
        result = await db.execute(
            select(Invoice)
            .order_by(Invoice.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        invoices = result.scalars().all()
        
        # Prepare response data
        invoices_data = [
            {
                'id': str(invoice.id),
                'invoice_number': invoice.invoice_number,
                'invoice_date': invoice.invoice_date,
                'amount': invoice.amount,
                'due_date': invoice.due_date,
                'file_name': invoice.file_name,
                'extraction_method': invoice.extraction_method,
                'created_at': invoice.created_at
            }
            for invoice in invoices
        ]
        
        return await prepare_response(
            True,
            api_messages.INVOICES_LIST_SUCCESS,
            api_codes.INVOICES_LIST_SUCCESS,
            data=invoices_data,
            total=total
        )
    
    except Exception as error:
        return await handle_db_exceptions(error, response)

# import os
# from typing import Optional
# from uuid import UUID
# from fastapi import Response, status, UploadFile
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from db.models.invoice import Invoice
# from utils.invoice_extractor import InvoiceExtractor
# from utils.log_handler import handle_db_exceptions, prepare_response
# from api_messages_and_codes.invoice import api_messages, api_codes
# from config import settings

# # Initialize invoice extractor
# extractor = InvoiceExtractor()

# async def process_invoice_upload(
#     file: UploadFile,
#     response: Response,
#     db: AsyncSession
# ) -> dict:
#     """
#     Process uploaded invoice file and extract data
    
#     Args:
#         file: Uploaded file object
#         response: FastAPI Response object
#         db: Database session
    
#     Returns:
#         dict: Response with extracted invoice data
#     """
#     try:
#         # Validate file extension
#         file_extension = os.path.splitext(file.filename)[1].lower()
#         if file_extension not in settings.ALLOWED_EXTENSIONS:
#             response.status_code = status.HTTP_400_BAD_REQUEST
#             return await prepare_response(
#                 False,
#                 api_messages.INVALID_FILE_TYPE,
#                 api_codes.INVALID_FILE_TYPE
#             )
        
#         # Create uploads directory if it doesn't exist
#         os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        
#         # Save uploaded file temporarily
#         file_path = os.path.join(settings.UPLOAD_FOLDER, file.filename)
#         with open(file_path, "wb") as buffer:
#             content = await file.read()
            
#             # Check file size
#             if len(content) > settings.MAX_UPLOAD_SIZE:
#                 response.status_code = status.HTTP_400_BAD_REQUEST
#                 return await prepare_response(
#                     False,
#                     api_messages.FILE_TOO_LARGE,
#                     api_codes.FILE_TOO_LARGE
#                 )
            
#             buffer.write(content)
        
#         # Extract invoice data
#         extracted_data = extractor.extract_invoice_data(file_path, file_extension)
        
#         # Check if text was extracted
#         if not extracted_data['extracted_text']:
#             response.status_code = status.HTTP_400_BAD_REQUEST
#             return await prepare_response(
#                 False,
#                 api_messages.NO_TEXT_EXTRACTED,
#                 api_codes.NO_TEXT_EXTRACTED
#             )
        
#         # Save to database
#         new_invoice = Invoice(
#             invoice_number=extracted_data['invoice_number'],
#             invoice_date=extracted_data['invoice_date'],
#             amount=extracted_data['amount'],
#             due_date=extracted_data['due_date'],
#             file_name=file.filename,
#             file_path=file_path,
#             extracted_text=extracted_data['extracted_text'],
#             extraction_method=extracted_data['extraction_method']
#         )
        
#         db.add(new_invoice)
#         await db.commit()
#         await db.refresh(new_invoice)
        
#         # Prepare response data
#         response_data = {
#             'id': str(new_invoice.id),
#             'invoice_number': new_invoice.invoice_number,
#             'invoice_date': new_invoice.invoice_date,
#             'amount': new_invoice.amount,
#             'due_date': new_invoice.due_date,
#             'file_name': new_invoice.file_name,
#             'extraction_method': new_invoice.extraction_method,
#             'created_at': new_invoice.created_at
#         }
        
#         response.status_code = status.HTTP_201_CREATED
#         return await prepare_response(
#             True,
#             api_messages.INVOICE_EXTRACTED_SUCCESS,
#             api_codes.INVOICE_EXTRACTED_SUCCESS,
#             data=response_data
#         )
    
#     except Exception as error:
#         # Clean up file if error occurs
#         if os.path.exists(file_path):
#             os.remove(file_path)
#         return await handle_db_exceptions(error, response)

# async def get_invoice_by_id(
#     invoice_id: str,
#     response: Response,
#     db: AsyncSession
# ) -> dict:
#     """
#     Fetch a single invoice by ID
    
#     Args:
#         invoice_id: UUID of the invoice
#         response: FastAPI Response object
#         db: Database session
    
#     Returns:
#         dict: Response with invoice data
#     """
#     try:
#         # Validate UUID
#         try:
#             uuid_obj = UUID(invoice_id)
#         except ValueError:
#             response.status_code = status.HTTP_400_BAD_REQUEST
#             return await prepare_response(
#                 False,
#                 "Invalid invoice ID format",
#                 api_codes.INVOICE_NOT_FOUND
#             )
        
#         # Query database
#         result = await db.execute(
#             select(Invoice).where(Invoice.id == uuid_obj)
#         )
#         invoice = result.scalar_one_or_none()
        
#         if not invoice:
#             response.status_code = status.HTTP_404_NOT_FOUND
#             return await prepare_response(
#                 False,
#                 api_messages.INVOICE_NOT_FOUND,
#                 api_codes.INVOICE_NOT_FOUND
#             )
        
#         # Prepare response data
#         response_data = {
#             'id': str(invoice.id),
#             'invoice_number': invoice.invoice_number,
#             'invoice_date': invoice.invoice_date,
#             'amount': invoice.amount,
#             'due_date': invoice.due_date,
#             'file_name': invoice.file_name,
#             'extraction_method': invoice.extraction_method,
#             'created_at': invoice.created_at
#         }
        
#         return await prepare_response(
#             True,
#             api_messages.INVOICE_FETCH_SUCCESS,
#             api_codes.INVOICE_FETCH_SUCCESS,
#             data=response_data
#         )
    
#     except Exception as error:
#         return await handle_db_exceptions(error, response)

# async def get_all_invoices(
#     response: Response,
#     db: AsyncSession,
#     skip: int = 0,
#     limit: int = 100
# ) -> dict:
#     """
#     Fetch all invoices with pagination
    
#     Args:
#         response: FastAPI Response object
#         db: Database session
#         skip: Number of records to skip
#         limit: Maximum number of records to return
    
#     Returns:
#         dict: Response with list of invoices
#     """
#     try:
#         # Get total count
#         count_result = await db.execute(select(Invoice))
#         total = len(count_result.scalars().all())
        
#         # Get paginated invoices
#         result = await db.execute(
#             select(Invoice)
#             .order_by(Invoice.created_at.desc())
#             .offset(skip)
#             .limit(limit)
#         )
#         invoices = result.scalars().all()
        
#         # Prepare response data
#         invoices_data = [
#             {
#                 'id': str(invoice.id),
#                 'invoice_number': invoice.invoice_number,
#                 'invoice_date': invoice.invoice_date,
#                 'amount': invoice.amount,
#                 'due_date': invoice.due_date,
#                 'file_name': invoice.file_name,
#                 'extraction_method': invoice.extraction_method,
#                 'created_at': invoice.created_at
#             }
#             for invoice in invoices
#         ]
        
#         return await prepare_response(
#             True,
#             api_messages.INVOICES_LIST_SUCCESS,
#             api_codes.INVOICES_LIST_SUCCESS,
#             data=invoices_data,
#             total=total
#         )
    
#     except Exception as error:
#         return await handle_db_exceptions(error, response)