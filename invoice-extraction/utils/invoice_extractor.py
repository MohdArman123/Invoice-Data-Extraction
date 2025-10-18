import json
import pdfplumber
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from typing import Dict, Optional, Tuple
from config import settings
import os
import httpx

class InvoiceExtractor:
    """
    Extract invoice data from PDF or image files using LLM (Ollama)
    """
    
    def __init__(self):
        self.llm_base_url = settings.LLM_BASE_URL
        self.llm_model = settings.LLM_MODEL
        
        # LLM prompt template for invoice extraction
        self.extraction_prompt = """You are an expert invoice data extraction AI. Extract the following information from the invoice text below and return ONLY a valid JSON object with these exact keys:

- invoice_number: The invoice or bill number (string)
- invoice_date: The invoice or bill date (string)
- amount: The total amount due (number, no currency symbols)
- due_date: The payment due date (string)

If any field is not found, use null for that field.

Invoice Text:
{text}

Return ONLY the JSON object, no other text:"""

    def extract_text_from_pdf(self, file_path: str) -> Tuple[Optional[str], str]:
        """
        Extract text from PDF using pdfplumber (for text-based PDFs)
        Returns: (extracted_text, extraction_method)
        """
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if text.strip():
                return text, "text"
            else:
                # If no text found, try OCR
                return self.extract_with_ocr(file_path), "ocr"
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            # Fallback to OCR
            return self.extract_with_ocr(file_path), "ocr"

    def extract_with_ocr(self, file_path: str) -> Optional[str]:
        """
        Extract text from scanned PDF or image using pytesseract OCR
        """
        try:
            # Check if file is an image
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                img = Image.open(file_path)
                text = pytesseract.image_to_string(img)
                return text
            
            # For PDF, convert to images first
            poppler_path = settings.POPPLER_PATH if hasattr(settings, 'POPPLER_PATH') else None
            images = convert_from_path(file_path, poppler_path=poppler_path)
            
            text = ""
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
            
            return text if text.strip() else None
        except Exception as e:
            print(f"Error during OCR extraction: {e}")
            return None

    async def extract_with_llm(self, text: str) -> Dict:
        """
        Use Ollama LLM to extract invoice fields from text
        """
        try:
            # Truncate text if too long (keep first 3000 chars)
            if len(text) > 3000:
                text = text[:3000]
            
            # Prepare prompt
            prompt = self.extraction_prompt.format(text=text)
            
            print(f"Calling Ollama API at {self.llm_base_url} with model {self.llm_model}...")
            
            # Call Ollama API
            async with httpx.AsyncClient(timeout=120.0) as client:
                try:
                    response = await client.post(
                        f"{self.llm_base_url}/api/generate",
                        json={
                            "model": self.llm_model,
                            "prompt": prompt,
                            "stream": False,
                            "temperature": settings.LLM_TEMPERATURE,
                            "options": {
                                "num_predict": settings.LLM_MAX_TOKENS
                            }
                        }
                    )
                    
                    if response.status_code != 200:
                        print(f"LLM API Error: {response.status_code} - {response.text}")
                        return self._get_empty_extraction()
                    
                    result = response.json()
                    llm_output = result.get("response", "")
                    print(f"LLM Response received: {llm_output[:200]}...")
                    
                    # Parse JSON from LLM response
                    extracted_data = self._parse_llm_response(llm_output)
                    return extracted_data
                    
                except httpx.ConnectError as e:
                    print(f"Cannot connect to Ollama at {self.llm_base_url}. Is Ollama running?")
                    print(f"Error: {e}")
                    return self._get_empty_extraction()
                except httpx.TimeoutException as e:
                    print(f"Ollama request timed out: {e}")
                    return self._get_empty_extraction()
                
        except Exception as e:
            print(f"Error calling LLM: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return self._get_empty_extraction()

    def _parse_llm_response(self, llm_output: str) -> Dict:
        """
        Parse JSON from LLM response, handling potential formatting issues
        """
        try:
            # Try to find JSON object in response
            llm_output = llm_output.strip()
            
            # Remove markdown code blocks if present
            if llm_output.startswith("```"):
                lines = llm_output.split("\n")
                llm_output = "\n".join(lines[1:-1])
            
            # Find JSON object
            start_idx = llm_output.find("{")
            end_idx = llm_output.rfind("}") + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = llm_output[start_idx:end_idx]
                data = json.loads(json_str)
                
                # Validate and clean data
                return {
                    'invoice_number': data.get('invoice_number'),
                    'invoice_date': data.get('invoice_date'),
                    'amount': float(data.get('amount')) if data.get('amount') and data.get('amount') != 'null' else None,
                    'due_date': data.get('due_date'),
                }
            else:
                print(f"No JSON found in LLM response: {llm_output}")
                return self._get_empty_extraction()
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"LLM output was: {llm_output}")
            return self._get_empty_extraction()
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return self._get_empty_extraction()

    def _get_empty_extraction(self) -> Dict:
        """
        Return empty extraction result
        """
        return {
            'invoice_number': None,
            'invoice_date': None,
            'amount': None,
            'due_date': None,
        }

    async def extract_invoice_data(self, file_path: str, file_extension: str) -> Dict:
        """
        Main method to extract all invoice data from a file using LLM
        Returns a dictionary with extracted fields
        """
        # Step 1: Extract text based on file type
        if file_extension.lower() == '.pdf':
            text, method = self.extract_text_from_pdf(file_path)
        else:  # Image file
            text = self.extract_with_ocr(file_path)
            method = "ocr"
        
        if not text or not text.strip():
            return {
                'extracted_text': None,
                'extraction_method': None,
                'invoice_number': None,
                'invoice_date': None,
                'amount': None,
                'due_date': None,
            }
        
        # Step 2: Use LLM to extract structured data
        llm_extracted = await self.extract_with_llm(text)
        
        return {
            'extracted_text': text,
            'extraction_method': method,
            'invoice_number': llm_extracted['invoice_number'],
            'invoice_date': llm_extracted['invoice_date'],
            'amount': llm_extracted['amount'],
            'due_date': llm_extracted['due_date'],
        }

# import re
# import pdfplumber
# import pytesseract
# from PIL import Image
# from pdf2image import convert_from_path
# from typing import Dict, Optional, Tuple
# from config import settings
# import os

# class InvoiceExtractor:
#     """
#     Extract invoice data from PDF or image files using regex patterns
#     """
    
#     def __init__(self):
#         # Regex patterns for invoice data extraction
#         self.patterns = {
#             'invoice_number': [
#                 r'Invoice\s*#?\s*:?\s*([A-Z0-9-]+)',
#                 r'Invoice\s*Number\s*:?\s*([A-Z0-9-]+)',
#                 r'Bill\s*#?\s*:?\s*([A-Z0-9-]+)',
#                 r'Account\s*Number\s*:?\s*([A-Z0-9-]+)',
#                 r'#\s*([A-Z0-9-]{5,})',
#             ],
#             'invoice_date': [
#                 r'Invoice\s*Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
#                 r'Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
#                 r'Bill\s*Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
#                 r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
#             ],
#             'due_date': [
#                 r'Due\s*Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
#                 r'Payment\s*Due\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
#                 r'Due\s*By\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
#             ],
#             'amount': [
#                 r'Total\s*Amount\s*Due\s*:?\s*\$?\s*([\d,]+\.?\d*)',
#                 r'Amount\s*Due\s*:?\s*\$?\s*([\d,]+\.?\d*)',
#                 r'Total\s*:?\s*\$?\s*([\d,]+\.?\d*)',
#                 r'Balance\s*:?\s*\$?\s*([\d,]+\.?\d*)',
#                 r'Grand\s*Total\s*:?\s*\$?\s*([\d,]+\.?\d*)',
#             ],
#         }

#     def extract_from_pdf(self, file_path: str) -> Tuple[Optional[str], str]:
#         """
#         Extract text from PDF using pdfplumber
#         Returns: (extracted_text, extraction_method)
#         """
#         try:
#             text = ""
#             with pdfplumber.open(file_path) as pdf:
#                 for page in pdf.pages:
#                     page_text = page.extract_text()
#                     if page_text:
#                         text += page_text + "\n"
            
#             if text.strip():
#                 return text, "text"
#             else:
#                 # If no text found, try OCR
#                 return self.extract_with_ocr(file_path), "ocr"
#         except Exception as e:
#             print(f"Error extracting text from PDF: {e}")
#             # Fallback to OCR
#             return self.extract_with_ocr(file_path), "ocr"

#     def extract_with_ocr(self, file_path: str) -> Optional[str]:
#         """
#         Extract text from scanned PDF or image using pytesseract OCR
#         """
#         try:
#             # Check if file is an image
#             if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
#                 img = Image.open(file_path)
#                 text = pytesseract.image_to_string(img)
#                 return text
            
#             # For PDF, convert to images first
#             poppler_path = settings.POPPLER_PATH if hasattr(settings, 'POPPLER_PATH') else None
#             images = convert_from_path(file_path, poppler_path=poppler_path)
            
#             text = ""
#             for image in images:
#                 text += pytesseract.image_to_string(image) + "\n"
            
#             return text if text.strip() else None
#         except Exception as e:
#             print(f"Error during OCR extraction: {e}")
#             return None

#     def extract_field(self, text: str, field_name: str) -> Optional[str]:
#         """
#         Extract a specific field from text using regex patterns
#         """
#         patterns = self.patterns.get(field_name, [])
        
#         for pattern in patterns:
#             match = re.search(pattern, text, re.IGNORECASE)
#             if match:
#                 return match.group(1).strip()
        
#         return None

#     def extract_invoice_data(self, file_path: str, file_extension: str) -> Dict:
#         """
#         Main method to extract all invoice data from a file
#         Returns a dictionary with extracted fields
#         """
#         # Extract text based on file type
#         if file_extension.lower() == '.pdf':
#             text, method = self.extract_from_pdf(file_path)
#         else:  # Image file
#             text = self.extract_with_ocr(file_path)
#             method = "ocr"
        
#         if not text or not text.strip():
#             return {
#                 'extracted_text': None,
#                 'extraction_method': None,
#                 'invoice_number': None,
#                 'invoice_date': None,
#                 'amount': None,
#                 'due_date': None,
#             }
        
#         # Extract individual fields
#         invoice_number = self.extract_field(text, 'invoice_number')
#         invoice_date = self.extract_field(text, 'invoice_date')
#         due_date = self.extract_field(text, 'due_date')
#         amount_str = self.extract_field(text, 'amount')
        
#         # Convert amount to float
#         amount = None
#         if amount_str:
#             try:
#                 # Remove commas and convert to float
#                 amount = float(amount_str.replace(',', ''))
#             except ValueError:
#                 amount = None
        
#         return {
#             'extracted_text': text,
#             'extraction_method': method,
#             'invoice_number': invoice_number,
#             'invoice_date': invoice_date,
#             'amount': amount,
#             'due_date': due_date,
#         }