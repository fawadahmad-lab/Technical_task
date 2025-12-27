import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    NOMIC_API_KEY = os.getenv("NOMIC_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    
    # Paths
    UPLOAD_DIR = "uploads"
    VECTOR_STORE_DIR = "vector_store"
    DB_PATH = "database.db"
    
    # Allowed file types
    ALLOWED_EXTENSIONS = ['.pdf', '.png', '.jpg', '.jpeg']
    
    # Validation
    @classmethod
    def validate_environment(cls):
        if not cls.NOMIC_API_KEY:
            print("WARNING: NOMIC_API_KEY not found in .env file")
            print("Embeddings will use fallback local model")
        return True

settings = Settings()