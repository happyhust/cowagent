"""
OpenAI compatibility layer for OpenAI SDK >= 2.0.

This module provides a unified import for OpenAI exceptions across the project.
"""

from openai import (
    OpenAIError,
    RateLimitError,
    APIError,
    APIConnectionError,
    AuthenticationError,
    APITimeoutError,
    BadRequestError,
    NotFoundError,
)

# Aliases for backward compatibility with code using old openai.error names
Timeout = APITimeoutError
InvalidRequestError = BadRequestError


# Provide a mock "error" module for any legacy code that imports openai.error
class _ErrorModule:
    OpenAIError = OpenAIError
    RateLimitError = RateLimitError
    APIError = APIError
    APIConnectionError = APIConnectionError
    AuthenticationError = AuthenticationError
    InvalidRequestError = InvalidRequestError
    Timeout = Timeout
    BadRequestError = BadRequestError
    APITimeoutError = APITimeoutError


error = _ErrorModule()

__all__ = [
    "error",
    "OpenAIError",
    "RateLimitError",
    "APIError",
    "APIConnectionError",
    "AuthenticationError",
    "InvalidRequestError",
    "Timeout",
    "BadRequestError",
    "APITimeoutError",
    "NotFoundError",
]
