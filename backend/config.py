"""
Configuration module for the Legal Document Assistant backend.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    # GEMINI_MODEL = 'gemini-2.5-flash'
    GEMINI_MODEL = 'gemini-3-pro-preview'

    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_RUN_PORT', 5001))

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    @staticmethod
    def validate():
        """Validate required configuration."""
        if not Config.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set. "
                "Please set it in your .env file or environment variables."
            )


# Validate configuration on import
Config.validate()
