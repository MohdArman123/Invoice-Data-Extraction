from fastapi import FastAPI
from config import settings
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from routes.invoice_routes import invoiceRouter
import os

# Create FastAPI application
app = FastAPI(
    title="Invoice Extraction API",
    description="Extract invoice data from PDF and image files using OCR and text extraction",
    version="1.0.0",
    debug=settings.DEBUG
)

# Include routers
app.include_router(invoiceRouter)

@app.get("/healthcheck", tags=["Health Check"])
async def health_check():
    """
    Health check endpoint to verify the service is running
    """
    return {
        "status": True,
        "message": "Invoice Extraction API is up and running"
    }

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory on startup
@app.on_event("startup")
async def startup_event():
    """
    Initialize application resources on startup
    """
    # Create uploads folder if it doesn't exist
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    print(f"✓ Uploads directory created: {settings.UPLOAD_FOLDER}")
    print(f"✓ Invoice Extraction API started on port {settings.APP_PORT}")

if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(settings.APP_PORT),
        log_level="info",
        reload=True
    )