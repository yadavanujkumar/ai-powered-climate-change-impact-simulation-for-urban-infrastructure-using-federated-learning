import os
import json
from pydantic import BaseSettings, Field, SecretStr, validator

class Settings(BaseSettings):
    # Environment type: dev, staging, or production
    ENV: str = Field(..., env='ENV')
    
    # Database configuration
    DB_HOST: str = Field(..., env='DB_HOST')
    DB_PORT: int = Field(5432, env='DB_PORT')  # Default PostgreSQL port
    DB_USER: str = Field(..., env='DB_USER')
    DB_PASSWORD: SecretStr = Field(..., env='DB_PASSWORD')
    DB_NAME: str = Field(..., env='DB_NAME')

    # Redis configuration for caching
    REDIS_HOST: str = Field(..., env='REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='REDIS_PORT')  # Default Redis port
    REDIS_PASSWORD: SecretStr = Field('', env='REDIS_PASSWORD')  # Optional

    # API settings
    API_URL: str = Field(..., env='API_URL')
    API_TIMEOUT: int = Field(30, env='API_TIMEOUT')  # Timeout in seconds

    # Federated Learning settings
    FL_SERVER_URL: str = Field(..., env='FL_SERVER_URL')
    FL_TIMEOUT: int = Field(60, env='FL_TIMEOUT')  # Timeout for federated learning requests

    # Security settings
    SECRET_KEY: SecretStr = Field(..., env='SECRET_KEY')  # Used for JWT or other security mechanisms
    ALLOWED_HOSTS: list = Field(default_factory=lambda: ['localhost'], env='ALLOWED_HOSTS')

    # Performance tuning
    WORKERS: int = Field(4, env='WORKERS')  # Number of worker processes
    MAX_CONNECTIONS: int = Field(100, env='MAX_CONNECTIONS')  # Max DB connections

    # Resource limits
    RESOURCE_LIMITS: dict = Field(default_factory=lambda: {
        "cpu": "2",
        "memory": "4Gi"
    })

    @validator('ENV')
    def validate_env(cls, v):
        if v not in ['dev', 'staging', 'prod']:
            raise ValueError('Invalid environment. Must be one of: dev, staging, prod.')
        return v

    class Config:
        env_file = ".env"  # Load environment variables from .env file
        env_file_encoding = 'utf-8'

# Load settings
settings = Settings()

# Example usage
if __name__ == "__main__":
    print(json.dumps(settings.dict(), indent=4, default=str))  # Print settings for debugging