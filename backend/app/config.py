from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB
    mongodb_url: str
    mongodb_db_name: str
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str
    # jwt_expire_minutes: int
    
    # SendGrid
    sendgrid_api_key: str
    sendgrid_from_email: str

    # PineCone
    pinecone_api_key: str
    pinecone_environment: str

    class Config:
        env_file = ".env"

settings = Settings()