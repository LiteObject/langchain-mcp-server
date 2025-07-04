"""
LangChain Documentation MCP Server

This module provides a FastAPI application that serves real LangChain API reference and documentation
by fetching data from official LangChain sources. It includes endpoints for searching documentation,
getting API references, examples, and tutorials from live sources.
Uses FastApiMCP for Model Context Protocol integration.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, quote
import hashlib
import json

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Query
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel

app = FastAPI(
    title="LangChain Documentation MCP Server",
    description="Real-time LangChain API reference and documentation service",
    version="1.0.0"
)

# Configuration constants
LANGCHAIN_DOCS_BASE = "https://python.langchain.com"
GITHUB_API_BASE = "https://api.github.com/repos/langchain-ai/langchain"
REQUEST_TIMEOUT = 30
CACHE_TTL = 300  # 5 minutes

# In-memory cache
cache_store: Dict[str, Dict[str, Any]] = {}


class DocSearchResult(BaseModel):
    """Model for documentation search results."""
    title: str
    url: str
    summary: str
    category: str
    last_updated: Optional[str] = None


class APIReference(BaseModel):
    """Model for API reference information."""
    class_name: str
    module_path: str
    description: str
    methods: List[str]
    parameters: Dict[str, Any]
    examples: List[str]
    source_url: str


class GitHubExample(BaseModel):
    """Model for GitHub code examples."""
    filename: str
    content: str
    url: str
    description: str


class TutorialInfo(BaseModel):
    """Model for tutorial information."""
    title: str
    description: str
    url: str
    category: str
    topics: List[str]


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


async def fetch_url(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[str]:
    """
    Fetch content from a URL with error handling.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds

    Returns:
        The response text or None if failed

    Raises:
        httpx.RequestError: For network-related errors
        httpx.HTTPStatusError: For HTTP error responses
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except (httpx.RequestError, httpx.HTTPStatusError) as error:
        print(f"Error fetching {url}: {error}")
        return None


async def fetch_json(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[Dict]:
    """
    Fetch JSON content from a URL with error handling.

    Args:
        url: The URL to fetch JSON from
        timeout: Request timeout in seconds

    Returns:
        The parsed JSON data or None if failed

    Raises:
        httpx.RequestError: For network-related errors
        httpx.HTTPStatusError: For HTTP error responses
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except (httpx.RequestError, httpx.HTTPStatusError) as error:
        print(f"Error fetching JSON from {url}: {error}")
        return None


def get_cache_key(*args) -> str:
    """Generate cache key from arguments."""
    key_data = json.dumps(args, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


def get_cached_response(cache_key: str) -> Optional[Any]:
    """Get cached response if not expired."""
    if cache_key in cache_store:
        cached_data = cache_store[cache_key]
        if datetime.now() < cached_data['expires_at']:
            return cached_data['data']
        else:
            del cache_store[cache_key]
    return None


def set_cached_response(cache_key: str, data: Any, ttl: int = CACHE_TTL) -> None:
    """Cache response with TTL."""
    cache_store[cache_key] = {
        'data': data,
        'expires_at': datetime.now() + timedelta(seconds=ttl)
    }


def extract_text_content(html: str, max_length: int = 200) -> str:
    """
    Extract clean text content from HTML.

    Args:
        html: The HTML content to parse
        max_length: Maximum length of extracted text

    Returns:
        Clean text content, truncated if necessary
    """
    if not html:
        return ""

    soup = BeautifulSoup(html, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)

    return text[:max_length] + "..." if len(text) > max_length else text


def extract_class_info(file_content: str, class_name: str) -> tuple[str, List[str]]:
    """
    Extract class information from Python source code.

    Args:
        file_content: The Python source code
        class_name: Name of the class to extract info for

    Returns:
        Tuple of (description, methods list)
    """
    description = ""
    methods = []

    # Extract class definition and methods using regex
    class_pattern = rf'class {class_name}\([^)]*\):'
    class_match = re.search(class_pattern, file_content)

    if class_match:
        # Extract docstring
        docstring_pattern = r'"""(.*?)"""'
        docstring_match = re.search(
            docstring_pattern, file_content[class_match.end():], re.DOTALL)
        if docstring_match:
            description = docstring_match.group(1).strip()

        # Extract method names
        method_pattern = r'def (\w+)\(self'
        method_matches = re.findall(
            method_pattern, file_content[class_match.start():])
        methods = [
            method for method in method_matches if not method.startswith('_')]

    return description, methods


def determine_category_from_path(path: str) -> str:
    """
    Determine content category based on URL path.

    Args:
        path: The URL path

    Returns:
        The determined category
    """
    category_map = {
        "introduction": "Introduction",
        "tutorials": "Tutorials",
        "how_to": "How-To Guides",
        "concepts": "Concepts",
        "integrations": "Integrations",
        "providers": "Providers",
        "api_reference": "API Reference",
        "chat": "Chat Models",
        "llms": "LLMs",
        "chains": "Chains",
        "agents": "Agents",
        "memory": "Memory",
        "retrievers": "Retrievers",
        "embeddings": "Embeddings"
    }

    for keyword, category in category_map.items():
        if keyword in path.lower():
            return category

    return "General"


@app.get("/search",
         operation_id="search_langchain_docs",
         summary="Search real LangChain documentation",
         response_model=List[DocSearchResult])
async def search_documentation(
    query: str = Query(..., description="Search query for documentation"),
    limit: int = Query(
        10, ge=1, le=20, description="Maximum number of results")
) -> List[DocSearchResult]:
    # Check cache first
    cache_key = get_cache_key("search_docs", query, limit)
    cached_result = get_cached_response(cache_key)
    if cached_result:
        return cached_result
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
        # Define sections to search through (updated with latest LangChain structure)
        sections_to_search = [
            "/docs/introduction/",
            "/docs/tutorials/",
            "/docs/how_to/",
            "/docs/concepts/",
            "/docs/integrations/providers/",
            "/api_reference/"
        ]

        results = []

        for section_path in sections_to_search:
            if len(results) >= limit:
                break

            url = urljoin(LANGCHAIN_DOCS_BASE, section_path)
            content = await fetch_url(url)

            if content and query.lower() in content.lower():
                soup = BeautifulSoup(content, 'html.parser')
                title_tag = soup.find('title')
                title = title_tag.text if title_tag else section_path.split(
                    '/')[-1].replace('_', ' ').title()

                # Extract description from meta description or first paragraph
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    description = meta_desc.get('content', '')
                else:
                    first_p = soup.find('p')
                    description = extract_text_content(
                        str(first_p)) if first_p else ""

                category = determine_category_from_path(section_path)

                results.append(DocSearchResult(
                    title=title,
                    url=url,
                    summary=description,
                    category=category,
                    last_updated=datetime.now().strftime("%Y-%m-%d")
                ))

        results = results[:limit]
        set_cached_response(cache_key, results)
        return results

    except (httpx.RequestError, httpx.HTTPStatusError) as error:
        raise HTTPException(
            status_code=500, detail=f"Search failed: {str(error)}") from error


@app.get("/api-reference/{class_name}",
         operation_id="get_langchain_api_reference",
         summary="Get real API reference for LangChain class",
         response_model=APIReference)
async def get_api_reference(class_name: str) -> APIReference:
    # Check cache first
    cache_key = get_cache_key("api_reference", class_name)
    cached_result = get_cached_response(cache_key)
    if cached_result:
        return APIReference(**cached_result)
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
        # Search for the class in GitHub
        search_url = f"{GITHUB_API_BASE}/search/code?q={class_name}+language:python"
        search_results = await fetch_json(search_url)

        if not search_results or not search_results.get('items'):
            raise HTTPException(
                status_code=404,
                detail=f"Class '{class_name}' not found in LangChain repository"
            )

        # Get the first relevant file
        file_info = search_results['items'][0]
        file_url = file_info['html_url']

        # Get raw file content
        raw_url = file_url.replace(
            'github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
        file_content = await fetch_url(raw_url)

        if not file_content:
            raise HTTPException(
                status_code=500, detail="Could not fetch source code")

        # Parse the Python file to extract class information
        description, methods = extract_class_info(file_content, class_name)

        # Get module path from file path
        module_path = file_info['path'].replace('/', '.').replace('.py', '')

        result = APIReference(
            class_name=class_name,
            module_path=module_path,
            description=description or f"LangChain {class_name} class",
            methods=methods,
            parameters={},
            examples=[],
            source_url=file_url
        )
        set_cached_response(cache_key, result.dict())
        return result

    except HTTPException as http_error:
        raise http_error
    except (httpx.RequestError, httpx.HTTPStatusError) as error:
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
    # Check cache first
    cache_key = get_cache_key("github_examples", query, limit)
    cached_result = get_cached_response(cache_key)
    if cached_result:
        return cached_result
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
        # Search for Python example files in the LangChain repository
        search_query = f"extension:py {query or 'example'}"
        search_url = f"{GITHUB_API_BASE}/search/code?q={quote(search_query)}"

        search_results = await fetch_json(search_url)

        if not search_results or not search_results.get('items'):
            return []

        examples = []

        for item in search_results['items'][:limit]:
            # Get raw file content
            raw_url = item['html_url'].replace(
                'github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
            content = await fetch_url(raw_url)

            # Only include reasonably sized files
            if content and len(content) < 5000:
                examples.append(GitHubExample(
                    filename=item['name'],
                    content=content,
                    url=item['html_url'],
                    description=f"Example from {item['path']}"
                ))

        set_cached_response(cache_key, examples)
        return examples

    except (httpx.RequestError, httpx.HTTPStatusError) as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch GitHub examples: {str(error)}"
        ) from error


@app.get("/tutorials",
         operation_id="get_langchain_tutorials",
         summary="Get real LangChain tutorials from documentation",
         response_model=List[TutorialInfo])
async def get_tutorials() -> List[TutorialInfo]:
    # Check cache first
    cache_key = get_cache_key("tutorials")
    cached_result = get_cached_response(cache_key)
    if cached_result:
        return cached_result
    """
    Get real tutorials and guides from LangChain documentation.

    Returns:
        List of tutorials scraped from the official documentation

    Raises:
        HTTPException: If tutorials page cannot be fetched
    """
    try:
        # Fetch the main tutorials page
        tutorials_url = f"{LANGCHAIN_DOCS_BASE}/docs/tutorials/"
        content = await fetch_url(tutorials_url)

        if not content:
            raise HTTPException(
                status_code=500, detail="Could not fetch tutorials page")

        soup = BeautifulSoup(content, 'html.parser')
        tutorials = []

        # Find tutorial links (updated for new structure)
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/docs/') and any(
                keyword in href for keyword in ['tutorials', 'concepts', 'introduction', 'how_to', 'integrations']
            ):
                title = link.text.strip()
                if title and len(title) > 3:
                    full_url = urljoin(LANGCHAIN_DOCS_BASE, href)

                    # Determine category from URL (updated categories)
                    category = "General"
                    if "introduction" in href:
                        category = "Introduction"
                    elif "tutorial" in href:
                        category = "Tutorials"
                    elif "how_to" in href:
                        category = "How-To Guides"
                    elif "concepts" in href:
                        category = "Concepts"
                    elif "integrations" in href:
                        category = "Integrations"

                    tutorials.append(TutorialInfo(
                        title=title,
                        description=f"LangChain tutorial: {title}",
                        url=full_url,
                        category=category,
                        topics=[category.lower().replace(" ", "_")]
                    ))

        # Remove duplicates
        seen_urls = set()
        unique_tutorials = []
        for tutorial in tutorials:
            if tutorial.url not in seen_urls:
                seen_urls.add(tutorial.url)
                unique_tutorials.append(tutorial)

        result = unique_tutorials[:10]  # Limit to 10 tutorials
        set_cached_response(cache_key, result)
        return result

    except (httpx.RequestError, httpx.HTTPStatusError) as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch tutorials: {str(error)}"
        ) from error


@app.get("/latest-version",
         operation_id="get_latest_langchain_version",
         summary="Get latest LangChain version from PyPI",
         response_model=VersionInfo)
async def get_latest_version() -> VersionInfo:
    # Check cache first
    cache_key = get_cache_key("latest_version")
    cached_result = get_cached_response(cache_key)
    if cached_result:
        return VersionInfo(**cached_result)
    """
    Get the latest LangChain version information from PyPI.

    Returns:
        Latest version information from the official PyPI repository

    Raises:
        HTTPException: If PyPI API request fails
    """
    try:
        pypi_url = "https://pypi.org/pypi/langchain/json"
        data = await fetch_json(pypi_url)

        if not data:
            raise HTTPException(
                status_code=500, detail="Could not fetch version information")

        info = data.get('info', {})
        releases = data.get('releases', {})

        # Get latest version
        latest_version = info.get('version', 'Unknown')

        # Get release information
        latest_release_info = releases.get(latest_version, [])
        upload_time = None
        if latest_release_info:
            upload_time = latest_release_info[0].get('upload_time_iso_8601')

        result = VersionInfo(
            latest_version=latest_version,
            description=info.get('summary', ''),
            author=info.get('author', ''),
            homepage=info.get('home_page', ''),
            release_date=upload_time,
            python_requires=info.get('requires_python', ''),
            pypi_url="https://pypi.org/project/langchain/",
            documentation_url=LANGCHAIN_DOCS_BASE
        )
        set_cached_response(cache_key, result.dict())
        return result

    except (httpx.RequestError, httpx.HTTPStatusError) as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch version info: {str(error)}"
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
        "service": "LangChain Documentation MCP Server (Live Data)",
        "timestamp": datetime.now().isoformat(),
        "endpoints_available": 8,
        "cache_entries": len(cache_store),
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
        ]
    }


@app.delete("/cache",
           operation_id="clear_cache",
           summary="Clear response cache")
def clear_cache() -> Dict[str, Any]:
    """
    Clear all cached responses.

    Returns:
        Cache clear status
    """
    cleared_count = len(cache_store)
    cache_store.clear()
    return {
        "status": "cleared",
        "cleared_entries": cleared_count,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/search/api",
         operation_id="search_langchain_api",
         summary="Search LangChain API reference",
         response_model=List[DocSearchResult])
async def search_api_reference(
    query: str = Query(..., description="Search query for API reference"),
    limit: int = Query(5, ge=1, le=10, description="Maximum number of results")
) -> List[DocSearchResult]:
    # Check cache first
    cache_key = get_cache_key("search_api", query, limit)
    cached_result = get_cached_response(cache_key)
    if cached_result:
        return cached_result
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
        # Use the official LangChain API reference search
        search_url = f"{LANGCHAIN_DOCS_BASE}/api_reference/search.html?q={quote(query)}"
        content = await fetch_url(search_url)

        if not content:
            # Fallback to general API reference page
            api_url = f"{LANGCHAIN_DOCS_BASE}/api_reference/"
            content = await fetch_url(api_url)

        results = []

        if content:
            soup = BeautifulSoup(content, 'html.parser')

            # Look for API reference links and items
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.text.strip()

                if (href.startswith('/api_reference/') or 'api_reference' in href) and text:
                    if query.lower() in text.lower() or query.lower() in href.lower():
                        full_url = urljoin(LANGCHAIN_DOCS_BASE, href)

                        # Extract parent element for context
                        parent = link.parent
                        description = ""
                        if parent:
                            desc_text = parent.get_text().strip()
                            if len(desc_text) > len(text):
                                description = extract_text_content(
                                    desc_text, 150)

                        results.append(DocSearchResult(
                            title=text,
                            url=full_url,
                            summary=description or f"API reference for {text}",
                            category="API Reference",
                            last_updated=datetime.now().strftime("%Y-%m-%d")
                        ))

                        if len(results) >= limit:
                            break

        set_cached_response(cache_key, results)
        return results

    except (httpx.RequestError, httpx.HTTPStatusError) as error:
        raise HTTPException(
            status_code=500,
            detail=f"API search failed: {str(error)}"
        ) from error


# Initialize FastApiMCP
mcp = FastApiMCP(
    app,
    name="LangChain Documentation MCP (Live)",
    description="Real-time LangChain API reference and documentation service fetching live data from official sources"
)
mcp.mount()
