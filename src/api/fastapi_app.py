"""
FastAPI application with all routes and endpoints.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query

from ..config.settings import settings
from ..config.logging import get_logger
from ..services.langchain_service import LangChainDocumentationService
from ..models.schemas import (
    DocSearchResult,
    APIReference,
    GitHubExample,
    TutorialInfo,
    VersionInfo,
    HealthResponse,
)
from ..utils.exceptions import (
    LangChainServiceError,
    DocumentationNotFoundError,
)
from ..utils.helpers import validate_max_results

logger = get_logger(__name__)


@asynccontextmanager
def lifespan(app: FastAPI):
    logger.info("Starting %s v%s", settings.app_name, settings.version)
    logger.info("Debug mode: %s", settings.debug)
    yield
    logger.info("Shutting down application")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Real-time LangChain API reference and documentation service",
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan,
)

# Initialize the documentation service
doc_service = LangChainDocumentationService()


@app.exception_handler(LangChainServiceError)
async def langchain_service_exception_handler(_request, exc: LangChainServiceError):
    """Handle LangChain service exceptions."""
    logger.error("LangChain service error: %s", exc.message)
    raise HTTPException(status_code=exc.status_code, detail=exc.message)


@app.get("/health", response_model=HealthResponse, summary="Health check endpoint")
def health_check() -> HealthResponse:
    """
    Health check endpoint to verify the service is running.

    Returns:
        Service status and current timestamp
    """
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        timestamp=datetime.now().isoformat(),
        endpoints_available=7,
        data_sources=[
            "python.langchain.com",
            "github.com/langchain-ai/langchain",
            "pypi.org/project/langchain"
        ],
        features=[
            "documentation_search",
            "api_reference_lookup",
            "github_examples",
            "tutorials",
            "version_info"
        ],
        architecture="shared_service_layer"
    )


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
        max_results = validate_max_results(max_results)
        logger.info("Searching documentation for query: %s", query)

        results = await doc_service.search_documentation(query, max_results)

        logger.info("Found %d results for query: %s", len(results), query)
        return [DocSearchResult.from_service(result) for result in results]

    except Exception as e:
        logger.error("Search failed for query '%s': %s", query, str(e))
        raise HTTPException(
            status_code=500, detail=f"Search failed: {str(e)}") from e


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
        max_results = validate_max_results(max_results)
        logger.info("Searching API reference for query: %s", query)

        results = await doc_service.search_api_reference(query, max_results)

        logger.info(
            "Found %d API reference results for query: %s", len(results), query)
        return [DocSearchResult.from_service(result) for result in results]

    except Exception as e:
        logger.error("API search failed for query '%s': %s", query, str(e))
        raise HTTPException(
            status_code=500, detail=f"API search failed: {str(e)}") from e


@app.get("/api-reference/{class_name}",
         response_model=APIReference,
         summary="Get detailed API reference for a specific class")
async def get_api_reference(class_name: str) -> APIReference:
    """
    Get detailed API reference information for a specific LangChain class.

    Returns comprehensive information including methods, parameters,
    examples, and source code links.
    """
    try:
        logger.info("Getting API reference for class: %s", class_name)

        result = await doc_service.get_api_reference(class_name)
        if result is None:
            raise DocumentationNotFoundError(
                f"API reference for '{class_name}' not found")

        logger.info("Retrieved API reference for class: %s", class_name)
        return APIReference.from_service(result)

    except DocumentationNotFoundError:
        raise
    except Exception as e:
        logger.error(
            "Failed to get API reference for '%s': %s", class_name, str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to get API reference: {str(e)}") from e


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
        max_results = validate_max_results(max_results)
        logger.info("Getting GitHub examples for topic: %s", topic)

        results = await doc_service.get_github_examples(topic, max_results)

        logger.info("Found %d GitHub examples for topic: %s",
                    len(results), topic)
        return [GitHubExample.from_service(result) for result in results]

    except Exception as e:
        logger.error(
            "Failed to get GitHub examples for '%s': %s", topic, str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to get GitHub examples: {str(e)}") from e


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
        max_results = validate_max_results(max_results)
        logger.info("Getting tutorials (difficulty: %s)", difficulty)

        results = await doc_service.get_tutorials()

        # Filter by difficulty if specified
        if difficulty:
            results = [r for r in results if hasattr(
                r, "difficulty") and r.difficulty and difficulty.lower() in r.difficulty.lower()]

        # Limit results if max_results is specified
        if max_results:
            results = results[:max_results]

        logger.info("Found %d tutorials", len(results))
        return [TutorialInfo.from_service(result) for result in results]

    except Exception as e:
        logger.error("Failed to get tutorials: %s", str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to get tutorials: {str(e)}") from e


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
        logger.info("Getting latest LangChain version")

        result = await doc_service.get_latest_version()

        logger.info("Retrieved version info: %s", getattr(
            result, "latest_version", "unknown"))
        return VersionInfo.from_service(result)

    except Exception as e:
        logger.error("Failed to get version info: %s", str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to get version info: {str(e)}") from e
