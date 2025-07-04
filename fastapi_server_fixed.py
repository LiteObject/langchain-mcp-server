"""
Fixed LangChain Documentation FastAPI Server

This module provides a FastAPI application that serves real LangChain API reference and documentation
using the shared LangChainDocumentationService. This version fixes the MCP integration issue.
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
    version: str
    release_date: str
    python_requires: str
    homepage: str
    repository: str

    @classmethod
    def from_service(cls, service_result: ServiceVersionInfo) -> "VersionInfo":
        """Convert from service model to API model."""
        return cls(
            version=service_result.version,
            release_date=service_result.release_date,
            python_requires=service_result.python_requires,
            homepage=service_result.homepage,
            repository=service_result.repository
        )


# API Endpoints

@app.get("/search",
         response_model=List[DocSearchResult],
         summary="Search LangChain documentation")
async def search_documentation(
    query: str = Query(...,
                       description="Search query for LangChain documentation"),
    max_results: int = Query(
        10, ge=1, le=50, description="Maximum number of results to return")
) -> List[DocSearchResult]:
    """
    Search through LangChain documentation with the given query.

    This endpoint searches through the official LangChain documentation
    and returns relevant results with titles, URLs, summaries, and categories.
    """
    try:
        results = await doc_service.search_documentation(query, max_results)
        return [DocSearchResult.from_service(result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/search/api",
         response_model=List[DocSearchResult],
         summary="Search API reference documentation")
async def search_api_documentation(
    query: str = Query(...,
                       description="Search query for LangChain API reference"),
    max_results: int = Query(
        10, ge=1, le=50, description="Maximum number of results to return")
) -> List[DocSearchResult]:
    """
    Search specifically through LangChain API reference documentation.

    This endpoint focuses on API reference materials, including class
    documentation, method descriptions, and parameter information.
    """
    try:
        results = await doc_service.search_api_reference(query, max_results)
        return [DocSearchResult.from_service(result) for result in results]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"API search failed: {str(e)}")


@app.get("/api-reference/{class_name}",
         response_model=APIReference,
         summary="Get detailed API reference for a specific class")
async def get_api_reference(
    class_name: str,
) -> APIReference:
    """
    Get detailed API reference information for a specific LangChain class.

    Returns comprehensive information including methods, parameters,
    examples, and source code links.
    """
    try:
        result = await doc_service.get_api_reference(class_name)
        if result is None:
            raise HTTPException(
                status_code=404, detail=f"API reference for '{class_name}' not found")
        return APIReference.from_service(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get API reference: {str(e)}")


@app.get("/examples/github",
         response_model=List[GitHubExample],
         summary="Get code examples from GitHub")
async def get_github_examples(
    topic: str = Query(...,
                       description="Topic or concept to find examples for"),
    max_results: int = Query(
        5, ge=1, le=20, description="Maximum number of examples to return")
) -> List[GitHubExample]:
    """
    Get real code examples from the LangChain GitHub repository.

    This endpoint searches through the official LangChain repository
    to find practical code examples related to the specified topic.
    """
    try:
        results = await doc_service.get_github_examples(topic, max_results)
        return [GitHubExample.from_service(result) for result in results]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get GitHub examples: {str(e)}")


@app.get("/tutorials",
         response_model=List[TutorialInfo],
         summary="Get LangChain tutorials and guides")
async def get_tutorials(
    difficulty: Optional[str] = Query(
        None, description="Filter by difficulty level"),
    max_results: int = Query(
        10, ge=1, le=30, description="Maximum number of tutorials to return")
) -> List[TutorialInfo]:
    """
    Get LangChain tutorials and learning guides.

    This endpoint provides access to official tutorials, guides,
    and learning materials from the LangChain documentation.
    """
    try:
        results = await doc_service.get_tutorials(difficulty, max_results)
        return [TutorialInfo.from_service(result) for result in results]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get tutorials: {str(e)}")


@app.get("/latest-version",
         response_model=VersionInfo,
         summary="Get latest LangChain version information")
async def get_latest_version() -> VersionInfo:
    """
    Get the latest LangChain version and release information.

    This endpoint fetches current version information from PyPI,
    including version number, release date, and requirements.
    """
    try:
        result = await doc_service.get_latest_version()
        return VersionInfo.from_service(result)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get version info: {str(e)}")


@app.get("/health")
def health_check() -> Dict[str, Any]:
    """
    Health check endpoint to verify the service is running.

    Returns:
        Service status and current timestamp
    """
    return {
        "status": "ok",
        "service": "LangChain Documentation FastAPI Server (Fixed)",
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


# Initialize FastApiMCP - moved to after all endpoints are defined
try:
    mcp = FastApiMCP(
        app,
        name="LangChain Documentation FastAPI (Fixed)",
        description="Real-time LangChain API reference and documentation service with shared service layer"
    )
    mcp.mount()
except Exception as e:
    print(f"Warning: MCP mounting failed: {e}")
    print("Server will continue without MCP integration")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
