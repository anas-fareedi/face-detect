from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb+srv://anasfareedi786786_db_user:TpGRTZWdnQFfYA1M@cluster0.cm5w936.mongodb.net/?appName=Cluster0"
    DATABASE_NAME: str = "face_recognition_db"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:5500", "http://127.0.0.1:5500"]
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Face Recognition API"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
