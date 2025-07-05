"""
Utility helper functions.
"""

import hashlib
import re
from datetime import datetime
from typing import Any, Optional
from urllib.parse import quote, urljoin


def generate_cache_key(*args: Any) -> str:
    """
    Generate a cache key from arguments.

    Args:
        *args: Arguments to include in the cache key

    Returns:
        SHA-256 hash of the arguments
    """
    key_string = "|".join(str(arg) for arg in args)
    return hashlib.sha256(key_string.encode()).hexdigest()


def sanitize_query(query: str) -> str:
    """
    Sanitize a search query.

    Args:
        query: Raw search query

    Returns:
        Sanitized query string
    """
    # Remove special characters but keep spaces and basic punctuation
    sanitized = re.sub(r'[^\w\s\-_.,!?]', '', query)
    # Normalize whitespace
    sanitized = ' '.join(sanitized.split())
    return sanitized.strip()


def build_url(base: str, path: str, **params: Any) -> str:
    """
    Build a URL with parameters.

    Args:
        base: Base URL
        path: URL path
        **params: Query parameters

    Returns:
        Complete URL with parameters
    """
    url = urljoin(base, path)

    if params:
        query_params = []
        for key, value in params.items():
            if value is not None:
                query_params.append(f"{key}={quote(str(value))}")

        if query_params:
            url += "?" + "&".join(query_params)

    return url


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format a datetime as ISO string.

    Args:
        dt: Datetime to format (defaults to now)

    Returns:
        ISO formatted datetime string
    """
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def validate_max_results(max_results: int, default: int = 10, maximum: int = 50) -> int:
    """
    Validate and clamp max_results parameter.

    Args:
        max_results: Requested max results
        default: Default value if invalid
        maximum: Maximum allowed value

    Returns:
        Validated max_results value
    """
    if max_results <= 0:
        return default
    return min(max_results, maximum)
