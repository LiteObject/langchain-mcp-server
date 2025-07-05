"""
Pydantic models and schemas for API requests and responses.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel

# Import service models for conversion
from ..services.langchain_service import (
    DocSearchResult as ServiceDocSearchResult,
    APIReference as ServiceAPIReference,
    GitHubExample as ServiceGitHubExample,
    TutorialInfo as ServiceTutorialInfo,
    VersionInfo as ServiceVersionInfo,
)


class DocSearchResult(BaseModel):
    """Model for documentation search results."""
    title: str
    url: str
    summary: str
    category: str
    last_updated: Optional[str] = None

    @classmethod
    def from_service(cls, service_result: ServiceDocSearchResult) -> "DocSearchResult":
        """Convert from service model to API model."""
        return cls(
            title=service_result.title,
            url=service_result.url,
            summary=service_result.summary,
            category=service_result.category,
            last_updated=service_result.last_updated
        )


class APIReference(BaseModel):
    """Model for API reference information."""
    class_name: str
    module_path: str
    description: str
    methods: List[str]
    parameters: Dict[str, Any]
    examples: List[str]
    source_url: str

    @classmethod
    def from_service(cls, service_result: ServiceAPIReference) -> "APIReference":
        """Convert from service model to API model."""
        return cls(
            class_name=service_result.class_name,
            module_path=service_result.module_path,
            description=service_result.description,
            methods=service_result.methods,
            parameters=service_result.parameters,
            examples=service_result.examples,
            source_url=service_result.source_url
        )


class GitHubExample(BaseModel):
    """Model for GitHub code examples."""
    filename: str
    content: str
    url: str
    description: str

    @classmethod
    def from_service(cls, service_result: ServiceGitHubExample) -> "GitHubExample":
        """Convert from service model to API model."""
        return cls(
            filename=service_result.filename,
            content=service_result.content,
            url=service_result.url,
            description=service_result.description
        )


class TutorialInfo(BaseModel):
    """Model for tutorial information."""
    title: str
    url: str
    description: str
    difficulty: str
    estimated_time: str

    @classmethod
    def from_service(cls, service_result: ServiceTutorialInfo) -> "TutorialInfo":
        """Convert from service model to API model."""
        return cls(
            title=service_result.title,
            url=service_result.url,
            description=service_result.description,
            difficulty=service_result.difficulty,
            estimated_time=service_result.estimated_time
        )


class VersionInfo(BaseModel):
    """Model for version information."""
    latest_version: str
    description: str
    author: str
    homepage: str
    release_date: str
    python_requires: str
    pypi_url: str
    documentation_url: str

    @classmethod
    def from_service(cls, service_result: Any) -> "VersionInfo":
        """Convert from service model to API model."""
        def safe_str(val):
            return val if isinstance(val, str) and val is not None else ""
        return cls(
            latest_version=safe_str(
                getattr(service_result, "latest_version", "")),
            description=safe_str(getattr(service_result, "description", "")),
            author=safe_str(getattr(service_result, "author", "")),
            homepage=safe_str(getattr(service_result, "homepage", "")),
            release_date=safe_str(getattr(service_result, "release_date", "")),
            python_requires=safe_str(
                getattr(service_result, "python_requires", "")),
            pypi_url=safe_str(getattr(service_result, "pypi_url", "")),
            documentation_url=safe_str(
                getattr(service_result, "documentation_url", "")),
        )


class HealthResponse(BaseModel):
    """Model for health check response."""
    status: str
    service: str
    timestamp: str
    endpoints_available: int
    data_sources: List[str]
    features: List[str]
    architecture: str
