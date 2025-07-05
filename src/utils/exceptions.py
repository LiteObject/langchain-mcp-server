"""
Custom exceptions for the LangChain Documentation Server.
"""


class LangChainServiceError(Exception):
    """Base exception for LangChain service errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DocumentationNotFoundError(LangChainServiceError):
    """Raised when documentation is not found."""

    def __init__(self, message: str = "Documentation not found"):
        super().__init__(message, status_code=404)


class APIRateLimitError(LangChainServiceError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, message: str = "API rate limit exceeded"):
        super().__init__(message, status_code=429)


class ExternalAPIError(LangChainServiceError):
    """Raised when external API calls fail."""

    def __init__(self, message: str = "External API error"):
        super().__init__(message, status_code=502)


class ValidationError(LangChainServiceError):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=400)
