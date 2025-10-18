import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str
    DEBUG: bool

    # Database Configuration
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    # Application Configuration
    APP_PORT: str
    BASE_URL: str

    # File Upload Configuration
    MAX_UPLOAD_SIZE: int
    ALLOWED_EXTENSIONS: list
    UPLOAD_FOLDER: str

    # OCR Configuration (for scanned PDFs)
    TESSERACT_PATH: str
    POPPLER_PATH: str

    # LLM Configuration - Using Ollama (Free, Local, Open-Source)
    LLM_BASE_URL: str
    LLM_MODEL: str
    LLM_TEMPERATURE: float
    LLM_MAX_TOKENS: int

    # Response Codes
    INTERNAL_SERVER_ERROR_CODE: str

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()