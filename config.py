"""
Configuration management module for the FIFA World Cup 2026 Stadium Operations Assistant.
Loads variables from the environment and defines the core exception hierarchy.
"""

import os
from typing import Any
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


# ==========================================
# CUSTOM EXCEPTION HIERARCHY
# ==========================================

class OpsCommanderError(Exception):
    """Base exception class for all FIFA 2026 Ops Commander errors."""
    pass


class ConfigurationError(OpsCommanderError):
    """Exception raised when configuration parameters are invalid or missing."""
    pass


class SanitizationError(OpsCommanderError):
    """Exception raised when security filters detect potential malicious input."""
    pass


class APIConnectionError(OpsCommanderError):
    """Exception raised when external GenAI API calls fail or timeout."""
    pass


# ==========================================
# CONFIGURATION CONTAINER
# ==========================================

class Config:
    """Holds configuration parameters and exports validation helpers.

    Attributes:
        GEMINI_API_KEY (str): API credentials fetched from system environment.
        GEMINI_MODEL (str): AI model name targeting gemini-1.5-flash.
        APP_NAME (str): Main application branding string.
    """

    def __init__(self) -> None:
        """Initializes configuration properties."""
        self._gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self._gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self._app_name: str = "FIFA 2026 Ops Commander"

    @property
    def GEMINI_API_KEY(self) -> str:
        """Gets the configured Gemini API key.

        Returns:
            str: The active API key.
        """
        return self._gemini_api_key

    @property
    def GEMINI_MODEL(self) -> str:
        """Gets the configured Gemini Model name.

        Returns:
            str: Model identifier string.
        """
        return self._gemini_model

    @property
    def APP_NAME(self) -> str:
        """Gets the application branding title.

        Returns:
            str: Name of the application.
        """
        return self._app_name

    def is_api_configured(self) -> bool:
        """Checks if the Gemini API credentials are set and valid.

        Returns:
            bool: True if key is set, False if missing or default placeholder.
        """
        key = self._gemini_api_key
        if not key:
            return False
        stripped_key = key.strip()
        if stripped_key == "" or stripped_key == "your_gemini_api_key_here":
            return False
        return True


# Global configurations instance
config: Config = Config()
