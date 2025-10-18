#!/usr/bin/env python3
"""
Startup check script to verify all dependencies are working
"""
import sys
import subprocess
import os

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("  ⚠️  Warning: Python 3.9+ recommended")
        return False
    return True

def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed")
        return False

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✓ Tesseract OCR: {version}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("✗ Tesseract OCR is NOT installed or not in PATH")
        print("  Install: sudo apt-get install tesseract-ocr  # Ubuntu/Debian")
        print("          brew install tesseract                 # macOS")
        return False

def check_poppler():
    """Check if Poppler is installed"""
    try:
        result = subprocess.run(['pdfinfo', '-v'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 or 'pdfinfo' in result.stderr.lower():
            print("✓ Poppler (pdfinfo) is installed")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("✗ Poppler is NOT installed or not in PATH")
        print("  Install: sudo apt-get install poppler-utils  # Ubuntu/Debian")
        print("          brew install poppler                  # macOS")
        return False

def check_ollama():
    """Check if Ollama is installed and running"""
    import httpx
    try:
        # Check if ollama command exists
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ Ollama is installed: {result.stdout.strip()}")
        
        # Check if Ollama server is running
        try:
            response = httpx.get("http://localhost:11434/api/tags", timeout=5.0)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"✓ Ollama server is running")
                if models:
                    print(f"  Available models: {', '.join([m['name'] for m in models])}")
                else:
                    print("  ⚠️  No models installed. Run: ollama pull llama3.2")
                return True
            else:
                print("✗ Ollama server returned error")
                return False
        except httpx.ConnectError:
            print("✗ Ollama server is NOT running")
            print("  Start with: ollama serve")
            return False
            
    except FileNotFoundError:
        print("✗ Ollama is NOT installed")
        print("  Install: curl -fsSL https://ollama.ai/install.sh | sh")
        return False
    except subprocess.TimeoutExpired:
        print("✗ Ollama command timed out")
        return False

def check_database():
    """Check if PostgreSQL is accessible"""
    try:
        from config import settings
        import asyncpg
        import asyncio
        
        async def test_connection():
            try:
                conn = await asyncpg.connect(
                    host=settings.DATABASE_HOST,
                    port=settings.DATABASE_PORT,
                    user=settings.DATABASE_USER,
                    password=settings.DATABASE_PASSWORD,
                    database=settings.DATABASE_NAME,
                    timeout=5
                )
                await conn.close()
                return True
            except Exception as e:
                print(f"  Error: {e}")
                return False
        
        result = asyncio.run(test_connection())
        if result:
            print(f"✓ PostgreSQL connection successful")
            print(f"  Database: {settings.DATABASE_NAME}")
            return True
        else:
            print(f"✗ Cannot connect to PostgreSQL")
            print(f"  Host: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}")
            print(f"  Database: {settings.DATABASE_NAME}")
            return False
    except Exception as e:
        print(f"✗ Database check failed: {e}")
        return False

def check_env_file():
    """Check if .env file exists"""
    if os.path.exists('.env'):
        print("✓ .env file exists")
        return True
    else:
        print("✗ .env file NOT found")
        print("  Copy .env.example to .env and configure it")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("Invoice Extraction API - Setup Check")
    print("=" * 60)
    print()
    
    checks = []
    
    print("1. Python Environment")
    print("-" * 40)
    checks.append(check_python_version())
    print()
    
    print("2. Configuration")
    print("-" * 40)
    checks.append(check_env_file())
    print()
    
    print("3. Python Packages")
    print("-" * 40)
    checks.append(check_package('fastapi'))
    checks.append(check_package('sqlalchemy'))
    checks.append(check_package('pdfplumber'))
    checks.append(check_package('pytesseract'))
    checks.append(check_package('PIL', 'PIL'))
    checks.append(check_package('pdf2image'))
    checks.append(check_package('httpx'))
    print()
    
    print("4. System Dependencies")
    print("-" * 40)
    checks.append(check_tesseract())
    checks.append(check_poppler())
    print()
    
    print("5. LLM (Ollama)")
    print("-" * 40)
    checks.append(check_ollama())
    print()
    
    print("6. Database")
    print("-" * 40)
    checks.append(check_database())
    print()
    
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    print(f"Results: {passed}/{total} checks passed")
    print("=" * 60)
    
    if passed == total:
        print("\n✓ All checks passed! You're ready to go.")
        print("\nStart the API with: python main.py")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()