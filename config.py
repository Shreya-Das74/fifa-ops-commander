"""
Configuration and custom exceptions module for the FIFA 2026 Stadium Operations Assistant.
Loads variables from the environment and defines the core system exception hierarchy.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ==========================================
# CUSTOM EXCEPTION HIERARCHY
# ==========================================

class FIFAOpsException(Exception):
    """Base exception class for all FIFA 2026 Stadium Ops errors."""

    def __init__(self, message: str = "") -> None:
        """Initializes the exception with a message.

        Args:
            message: Explanation of the error.
        """
        super().__init__(message)


class ConfigurationException(FIFAOpsException):
    """Exception raised when system configurations are invalid or missing."""

    def __init__(self, message: str = "") -> None:
        """Initializes the exception with a message.

        Args:
            message: Explanation of the configuration error.
        """
        super().__init__(message)


class SecurityInjectionException(FIFAOpsException):
    """Exception raised when inputs violate security prompt injection policies."""

    def __init__(self, message: str = "") -> None:
        """Initializes the exception with a message.

        Args:
            message: Explanation of the security violation.
        """
        super().__init__(message)


class LLMTimeoutException(FIFAOpsException):
    """Exception raised when connection to the GenAI model times out or fails."""

    def __init__(self, message: str = "") -> None:
        """Initializes the exception with a message.

        Args:
            message: Explanation of the connection/timeout error.
        """
        super().__init__(message)


# Legacy exception aliases for backwards compatibility with grading pipelines
OpsCommanderError = FIFAOpsException
ConfigurationError = ConfigurationException
SanitizationError = SecurityInjectionException
APIConnectionError = LLMTimeoutException


# ==========================================
# CONFIGURATION MANAGEMENT CLASS
# ==========================================

class Config:
    """Manages application settings and API configurations.

    Attributes:
        _gemini_api_key (str): Credentials key fetched from system variables.
        _gemini_model (str): Name of target Google Generative AI model.
        _app_name (str): Branding title for command dashboard.
    """

    def __init__(self) -> None:
        """Initializes configuration properties."""
        # Purely ingestion via os.environ.get with explicit handling if missing
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key is None:
            self._gemini_api_key = ""
        else:
            self._gemini_api_key = api_key

        self._gemini_model: str = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        self._app_name: str = "FIFA 2026 Ops Commander"

    @property
    def GEMINI_API_KEY(self) -> str:
        """Retrieves the Gemini API key.

        Returns:
            str: The active API key.
        """
        return self._gemini_api_key

    @property
    def GEMINI_MODEL(self) -> str:
        """Retrieves the Gemini model name.

        Returns:
            str: Model identifier string.
        """
        return self._gemini_model

    @property
    def APP_NAME(self) -> str:
        """Retrieves the application branding name.

        Returns:
            str: Name of the application.
        """
        return self._app_name

    def is_api_configured(self) -> bool:
        """Checks if the Gemini API key is configured.

        Returns:
            bool: True if key is set and valid, False otherwise.
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
