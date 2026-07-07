import sys
from pydantic import ValidationError
from milestone1.phase0.settings import load_settings

def check_environment():
    print("Running system checks...")
    
    # Check Python version
    py_version = sys.version_info
    print(f"Python version: {py_version.major}.{py_version.minor}.{py_version.micro}")
    if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 11):
        print("❌ Error: Python 3.11 or higher is required.")
        return False
    print("✅ Python version is compatible.")
    
    # Check Settings (.env variables)
    try:
        settings = load_settings()
        if not settings.groq_api_key or settings.groq_api_key == "your_groq_api_key_here":
            print("❌ Error: GROQ_API_KEY is not set correctly in the environment or .env file.")
            return False
        print("✅ GROQ_API_KEY is configured.")
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return False
        
    print("✅ Environment is fully configured and ready.")
    return True
