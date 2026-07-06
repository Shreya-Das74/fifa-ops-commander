"""
Configuration management module for the FIFA World Cup 2026 Stadium Operations Assistant.
Loads variables from environment or .env file and provides default fallback values.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Holds configuration parameters for the application."""
    
    # API Configurations
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Model Configurations
    # Defaulting to gemini-1.5-flash as it is fast, lightweight, and suitable for operations chat
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Application Configs
    APP_NAME = "FIFA 2026 Ops Commander"
    DEFAULT_PORT = int(os.getenv("PORT", "8501"))
    
    @classmethod
    def is_api_configured(cls) -> bool:
        """
        Check if the Gemini API key is configured.
        
        Returns:
            bool: True if configured, False otherwise.
        """
        return bool(cls.GEMINI_API_KEY and cls.GEMINI_API_KEY.strip() and cls.GEMINI_API_KEY != "your_gemini_api_key_here")

# Global configurations instance
config = Config()
