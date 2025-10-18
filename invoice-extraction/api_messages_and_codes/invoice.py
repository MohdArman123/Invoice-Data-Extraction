# API Response Messages
class ApiMessages:
    INVOICE_EXTRACTED_SUCCESS = "Invoice data extracted successfully"
    INVOICE_FETCH_SUCCESS = "Invoice fetched successfully"
    INVOICES_LIST_SUCCESS = "Invoices list fetched successfully"
    INVOICE_NOT_FOUND = "Invoice not found"
    INVALID_FILE_TYPE = "Invalid file type. Only PDF and image files are allowed"
    FILE_TOO_LARGE = "File size exceeds maximum allowed size"
    EXTRACTION_FAILED = "Failed to extract data from invoice"
    INTERNAL_SERVER_ERROR = "Internal server error occurred"
    NO_TEXT_EXTRACTED = "No text could be extracted from the file"

# API Response Codes
class ApiCodes:
    INVOICE_EXTRACTED_SUCCESS = "INV_001"
    INVOICE_FETCH_SUCCESS = "INV_002"
    INVOICES_LIST_SUCCESS = "INV_003"
    INVOICE_NOT_FOUND = "INV_404"
    INVALID_FILE_TYPE = "INV_400_01"
    FILE_TOO_LARGE = "INV_400_02"
    EXTRACTION_FAILED = "INV_500_01"
    INTERNAL_SERVER_ERROR = "ERR_500"
    NO_TEXT_EXTRACTED = "INV_400_03"

api_messages = ApiMessages()
api_codes = ApiCodes()