# Invoice Extraction API with LLM

A FastAPI-based REST API that extracts key invoice details from PDF and image files using **LLM (Ollama)** for intelligent data extraction.

## 🌟 Features

- **LLM-Powered Extraction**: Uses Ollama (free, local, open-source) for intelligent field extraction
- **PDF Text Extraction**: Uses `pdfplumber` for text-based PDFs
- **OCR Support**: Uses `pytesseract` for scanned PDFs/images
- **Smart Field Detection**: LLM understands context and extracts:
  - Invoice Number
  - Invoice Date
  - Amount
  - Due Date
- **PostgreSQL Database**: Stores extracted data using SQLAlchemy async ORM
- **100% Free & Open Source**: No paid APIs or external services

## 🏗️ Architecture

```
User uploads PDF/Image
         ↓
Extract text (pdfplumber/OCR)
         ↓
LLM analyzes text (Ollama)
         ↓
Structured JSON extraction
         ↓
Save to PostgreSQL
         ↓
Return JSON response
```

## 📋 Prerequisites

### 1. System Requirements

- **Python 3.9+**
- **PostgreSQL 12+**
- **Tesseract OCR** (for scanned documents)
- **Poppler** (for PDF to image conversion)
- **Ollama** (for LLM inference)

### 2. Install Ollama (Free LLM Runtime)

**Linux/macOS:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from: https://ollama.ai/download

**Pull the model:**
```bash
ollama pull llama3.2
# Alternatives: mistral, phi3, gemma2, llama2
```

**Verify Ollama is running:**
```bash
ollama list
curl http://localhost:11434/api/tags
```

### 3. Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
```

**macOS (using Homebrew):**
```bash
brew install tesseract poppler
```

**Windows:**
- Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Poppler: https://github.com/oschwartz10612/poppler-windows/releases/

## 🚀 Installation

### 1. Clone and Setup
```bash
git clone <repository-url>
cd invoice-extraction-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env .env.local
# Edit .env with your settings
```

### 3. Setup Database
```bash
# Create database
psql -U postgres
CREATE DATABASE invoice_db;
\q

# Run migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. Start Ollama (if not running)
```bash
ollama serve
```

### 5. Start the API
```bash
python main.py
```

API will be available at: **http://localhost:8000**

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### 1. Upload Invoice (LLM Extraction)
**POST** `/api/invoice/v1/upload`

Upload a PDF or image file for LLM-based extraction.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/invoice/v1/upload" \
  -F "file=@invoice.pdf"
```

**Response:**
```json
{
  "status": true,
  "message": "Invoice data extracted successfully",
  "code": "INV_001",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "invoice_number": "12345",
    "invoice_date": "12/11/2015",
    "amount": 150.50,
    "due_date": "01/10/2016",
    "file_name": "invoice.pdf",
    "extraction_method": "text",
    "created_at": "2025-10-18T10:30:00"
  }
}
```

### 2. Get Invoice by ID
**GET** `/api/invoice/v1/{invoice_id}`

### 3. List All Invoices
**GET** `/api/invoice/v1/?skip=0&limit=100`

### 4. Health Check
**GET** `/healthcheck`

## 🧪 Testing

### Test with Sample PDF
```bash
# Using curl
curl -X POST "http://localhost:8000/api/invoice/v1/upload" \
  -F "file=@Comcast Bill (1).pdf"

# Using Python
import requests

with open("Comcast Bill (1).pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/invoice/v1/upload",
        files={"file": f}
    )
    print(response.json())
```

## 🎯 Why LLM for Invoice Extraction?

### Traditional Regex Approach:
❌ Requires maintaining complex patterns  
❌ Breaks with layout changes  
❌ Can't handle variations  
❌ No contextual understanding  

### LLM Approach:
✅ Understands context naturally  
✅ Handles layout variations  
✅ Works with different formats  
✅ Self-corrects minor OCR errors  
✅ More accurate and maintainable  

## 🔧 LLM Models Comparison

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| llama3.2 | 2GB | Fast | High | General use (Recommended) |
| mistral | 4GB | Medium | High | Complex invoices |
| phi3 | 2.3GB | Fast | Medium | Quick processing |
| gemma2 | 5.5GB | Medium | Very High | Best accuracy |

Change model in `.env`:
```bash
LLM_MODEL=mistral  # or phi3, gemma2
```

## 📁 Project Structure

```
invoice-extraction-api/
│
├── alembic/                    # Database migrations
│   └── env.py
│
├── api_messages_and_codes/     # Response messages
│   └── invoice.py
│
├── db/
│   ├── models/
│   │   └── invoice.py         # Invoice model
│   └── session.py             # DB session
│
├── routes/
│   └── invoice_routes.py      # API endpoints
│
├── schemas/
│   └── invoice.py             # Pydantic schemas
│
├── services/
│   └── invoice_service.py     # Business logic
│
├── utils/
│   ├── invoice_extractor.py   # LLM extraction logic ⭐
│   └── log_handler.py         # Error handling
│
├── uploads/                    # Uploaded files
│
├── .env                        # Configuration
├── config.py                   # Settings
├── main.py                     # FastAPI app
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 🔍 How LLM Extraction Works

1. **Text Extraction**: Extract text from PDF/image using pdfplumber or OCR
2. **LLM Prompt**: Send text to Ollama with structured extraction prompt
3. **JSON Response**: LLM returns structured JSON with invoice fields
4. **Validation**: Parse and validate extracted data
5. **Storage**: Save to PostgreSQL database

### Example LLM Prompt:
```
You are an expert invoice data extraction AI. Extract:
- invoice_number
- invoice_date
- amount
- due_date

Invoice Text:
[extracted text here]

Return ONLY valid JSON.
```

## ⚙️ Configuration Options

### Adjust LLM Behavior (config.py):

```python
LLM_TEMPERATURE: float = 0.1    # Lower = more consistent
LLM_MAX_TOKENS: int = 1000      # Max response length
LLM_MODEL: str = "llama3.2"     # Model selection
```

## 🐛 Troubleshooting

### Ollama Not Running
```bash
# Start Ollama
ollama serve

# Check status
curl http://localhost:11434/api/tags
```

### Model Not Found
```bash
# Pull the model
ollama pull llama3.2

# List available models
ollama list
```

### Slow Extraction
- Use smaller model: `phi3` or `llama3.2`
- Reduce `LLM_MAX_TOKENS`
- Use GPU if available (Ollama auto-detects)

### Low Accuracy
- Use larger model: `mistral` or `gemma2`
- Increase OCR quality for scanned documents
- Adjust `LLM_TEMPERATURE` (try 0.0 for more deterministic)

## 🚀 Performance Tips

1. **GPU Acceleration**: Ollama automatically uses GPU if available
2. **Model Selection**: Start with `llama3.2` (good balance)
3. **Batch Processing**: Process multiple invoices asynchronously
4. **Caching**: Store extracted text to avoid re-processing

## 📈 Advantages of This Approach

✅ **100% Free & Open Source**  
✅ **Runs Locally** - No data sent to external APIs  
✅ **Privacy-Focused** - All data stays on your server  
✅ **Highly Accurate** - LLM understands context  
✅ **Easy to Extend** - Just modify the prompt  
✅ **No Rate Limits** - Process unlimited invoices  

## 🔐 Security & Privacy

- All processing happens locally
- No data sent to external services
- Files stored on your server
- Full control over data

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please ensure:
- LLM-based extraction is maintained
- Code follows existing structure
- Tests are included

## 💡 Future Enhancements

- [ ] Support for multi-page invoices
- [ ] Table extraction for line items
- [ ] Multi-language support
- [ ] Confidence scores
- [ ] Custom field extraction
- [ ] Batch processing API

## 📧 Contact

For issues or questions, open an issue on GitHub.

---

**Built with ❤️ using FastAPI, Ollama, and PostgreSQL**