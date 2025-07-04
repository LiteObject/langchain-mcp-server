"""
LangChain Documentation FastAPI Server (Refactored)

This module provides a FastAPI application that serves real LangChain API reference and documentation
using the shared LangChainDocumentationService. This version is cleaner and uses the service layer
for both HTTP and MCP access patterns.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel

from langchain_service import (
    LangChainDocumentationService,
    DocSearchResult as ServiceDocSearchResult,
    APIReference as ServiceAPIReference,
    GitHubExample as ServiceGitHubExample,
    TutorialInfo as ServiceTutorialInfo,
    VersionInfo as ServiceVersionInfo
)

app = FastAPI(
    title="LangChain Documentation FastAPI Server",
    description="Real-time LangChain API reference and documentation service with MCP integration",
    version="1.0.0"
)

# Initialize the documentation service
doc_service = LangChainDocumentationService()


# Pydantic models for FastAPI responses
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
    description: str
    url: str
    category: str
    topics: List[str]

    @classmethod
    def from_service(cls, service_result: ServiceTutorialInfo) -> "TutorialInfo":
        """Convert from service model to API model."""
        return cls(
            title=service_result.title,
            description=service_result.description,
            url=service_result.url,
            category=service_result.category,
            topics=service_result.topics
        )


class VersionInfo(BaseModel):
    """Model for version information."""
    latest_version: str
    description: str
    author: str
    homepage: str
    release_date: Optional[str]
    python_requires: str
    pypi_url: str
    documentation_url: str

    @classmethod
    def from_service(cls, service_result: ServiceVersionInfo) -> "VersionInfo":
        """Convert from service model to API model."""
        return cls(
            latest_version=service_result.latest_version,
            description=service_result.description,
            author=service_result.author,
            homepage=service_result.homepage,
            release_date=service_result.release_date,
            python_requires=service_result.python_requires,
            pypi_url=service_result.pypi_url,
            documentation_url=service_result.documentation_url
        )


@app.get("/search",
         operation_id="search_langchain_docs",
         summary="Search real LangChain documentation",
         response_model=List[DocSearchResult])
async def search_documentation(
    query: str = Query(..., description="Search query for documentation"),
    limit: int = Query(
        10, ge=1, le=20, description="Maximum number of results")
) -> List[DocSearchResult]:
    """
    Search through real LangChain documentation using site search.

    Args:
        query: The search term or phrase
        limit: Maximum number of results to return

    Returns:
        List of documentation search results from the official LangChain docs

    Raises:
        HTTPException: If search fails or no results found
    """
    try:
        results = await doc_service.search_documentation(query, limit)
        return [DocSearchResult.from_service(result) for result in results]
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(error)}"
        ) from error


@app.get("/api-reference/{class_name}",
         operation_id="get_langchain_api_reference",
         summary="Get real API reference for LangChain class",
         response_model=APIReference)
async def get_api_reference(class_name: str) -> APIReference:
    """
    Get real API reference for a LangChain class from GitHub source.

    Args:
        class_name: Name of the LangChain class (e.g., 'ChatOpenAI', 'LLMChain')

    Returns:
        Real API reference scraped from LangChain documentation or source code

    Raises:
        HTTPException: If class not found or fetch fails
    """
    try:
        result = await doc_service.get_api_reference(class_name)
        return APIReference.from_service(result)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch API reference: {str(error)}"
        ) from error


@app.get("/examples/github",
         operation_id="get_github_examples",
         summary="Get real code examples from LangChain GitHub",
         response_model=List[GitHubExample])
async def get_github_examples(
    query: Optional[str] = Query(None, description="Search term for examples"),
    limit: int = Query(
        5, ge=1, le=10, description="Maximum number of examples")
) -> List[GitHubExample]:
    """
    Get real code examples from the LangChain GitHub repository.

    Args:
        query: Optional search term to filter examples
        limit: Maximum number of examples to return

    Returns:
        List of real code examples from the LangChain repository

    Raises:
        HTTPException: If GitHub API request fails
    """
    try:
        results = await doc_service.get_github_examples(query, limit)
        return [GitHubExample.from_service(result) for result in results]
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch GitHub examples: {str(error)}"
        ) from error


@app.get("/tutorials",
         operation_id="get_langchain_tutorials",
         summary="Get real LangChain tutorials from documentation",
         response_model=List[TutorialInfo])
async def get_tutorials() -> List[TutorialInfo]:
    """
    Get real tutorials and guides from LangChain documentation.

    Returns:
        List of tutorials scraped from the official documentation

    Raises:
        HTTPException: If tutorials page cannot be fetched
    """
    try:
        results = await doc_service.get_tutorials()
        return [TutorialInfo.from_service(result) for result in results]
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch tutorials: {str(error)}"
        ) from error


@app.get("/latest-version",
         operation_id="get_latest_langchain_version",
         summary="Get latest LangChain version from PyPI",
         response_model=VersionInfo)
async def get_latest_version() -> VersionInfo:
    """
    Get the latest LangChain version information from PyPI.

    Returns:
        Latest version information from the official PyPI repository

    Raises:
        HTTPException: If PyPI API request fails
    """
    try:
        result = await doc_service.get_latest_version()
        return VersionInfo.from_service(result)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch version info: {str(error)}"
        ) from error


@app.get("/search/api",
         operation_id="search_langchain_api",
         summary="Search LangChain API reference",
         response_model=List[DocSearchResult])
async def search_api_reference(
    query: str = Query(..., description="Search query for API reference"),
    limit: int = Query(5, ge=1, le=10, description="Maximum number of results")
) -> List[DocSearchResult]:
    """
    Search through LangChain API reference using the official search.

    Args:
        query: The search term or phrase for API reference
        limit: Maximum number of results to return

    Returns:
        List of API reference search results

    Raises:
        HTTPException: If search fails
    """
    try:
        results = await doc_service.search_api_reference(query, limit)
        return [DocSearchResult.from_service(result) for result in results]
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"API search failed: {str(error)}"
        ) from error


@app.get("/health",
         operation_id="health_check",
         summary="Health check endpoint")
def health_check() -> Dict[str, Any]:
    """
    Health check endpoint to verify the service is running.

    Returns:
        Service status and current timestamp
    """
    return {
        "status": "ok",
        "service": "LangChain Documentation FastAPI Server (Refactored)",
        "timestamp": datetime.now().isoformat(),
        "endpoints_available": 7,
        "data_sources": [
            "python.langchain.com",
            "github.com/langchain-ai/langchain",
            "pypi.org/project/langchain"
        ],
        "updated_sections": [
            "introduction",
            "tutorials",
            "how_to",
            "concepts",
            "integrations/providers",
            "api_reference"
        ],
        "architecture": "shared_service_layer",
        "mcp_server_available": True
    }


# Initialize FastApiMCP
mcp = FastApiMCP(
    app,
    name="LangChain Documentation FastAPI (Refactored)",
    description="Real-time LangChain API reference and documentation service with shared service layer"
)
mcp.mount()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
