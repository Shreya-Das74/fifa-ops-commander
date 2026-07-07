"""
FIFA World Cup 2026 - Stadium Operations Security Engine
Manages input sanitization, HTML escaping, and prompt injection defense.
"""

import re
import html
from typing import List
from config import SecurityInjectionException

# Pre-compiled security rules
INJECTION_REGEXES: List[re.Pattern] = [
    re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"system\s+override", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+a", re.IGNORECASE),
    re.compile(r"act\s+as\s+a", re.IGNORECASE),
    re.compile(r"forget\s+(?:your\s+)?instructions", re.IGNORECASE),
    re.compile(r"developer\s+mode", re.IGNORECASE),
    re.compile(r"bypass\s+restrictions", re.IGNORECASE),
]


def sanitize_input(text: str) -> str:
    """Escapes HTML and filters malicious prompt injections.

    Args:
        text: Raw user input text.

    Returns:
        str: Sanitized clean string.

    Raises:
        ValueError: If query is empty or only whitespace.
        SecurityInjectionException: If injection signature is detected.
    """
    if not text or not text.strip():
        raise ValueError("Input query cannot be empty or whitespace only.")
    escaped = html.escape(text)
    clean_text = re.sub(r"<[^>]*>", "", escaped)
    for pattern in INJECTION_REGEXES:
        if pattern.search(clean_text):
            raise SecurityInjectionException("Security threat blocked: Prompt injection detected.")
    return clean_text


class SecuritySanitizer:
    """Handles text validation and security sanitization for command center inputs."""

    def __init__(self) -> None:
        """Initializes the sanitizer with pre-compiled regex safety rules."""
        self._injection_regexes: List[re.Pattern] = INJECTION_REGEXES

    def sanitize_input(self, text: str) -> str:
        """Sanitizes raw user input."""
        return sanitize_input(text)
