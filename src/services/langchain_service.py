"""
Core service layer for LangChain documentation operations.

This module contains the shared business logic that can be used by both
the FastAPI server and the MCP server implementations.
"""
# pylint: disable=too-few-public-methods,too-many-arguments,too-many-positional-arguments
# pylint: disable=too-many-instance-attributes,line-too-long,use-maxsplit-arg,too-many-nested-blocks

import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, quote

import httpx
from bs4 import BeautifulSoup


# Configuration constants
LANGCHAIN_DOCS_BASE = "https://python.langchain.com"
GITHUB_API_BASE = "https://api.github.com/repos/langchain-ai/langchain"
REQUEST_TIMEOUT = 30


class DocSearchResult:
    """Model for documentation search results."""

    def __init__(self, title: str, url: str, summary: str, category: str, last_updated: Optional[str] = None):
        self.title = title
        self.url = url
        self.summary = summary
        self.category = category
        self.last_updated = last_updated

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "url": self.url,
            "summary": self.summary,
            "category": self.category,
            "last_updated": self.last_updated
        }


class APIReference:
    """Model for API reference information."""

    def __init__(self, class_name: str, module_path: str, description: str,
                 methods: List[str], parameters: Dict[str, Any],
                 examples: List[str], source_url: str):
        self.class_name = class_name
        self.module_path = module_path
        self.description = description
        self.methods = methods
        self.parameters = parameters
        self.examples = examples
        self.source_url = source_url

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "class_name": self.class_name,
            "module_path": self.module_path,
            "description": self.description,
            "methods": self.methods,
            "parameters": self.parameters,
            "examples": self.examples,
            "source_url": self.source_url
        }


class GitHubExample:
    """Model for GitHub code examples."""

    def __init__(self, filename: str, content: str, url: str, description: str):
        self.filename = filename
        self.content = content
        self.url = url
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "filename": self.filename,
            "content": self.content,
            "url": self.url,
            "description": self.description
        }


class TutorialInfo:
    """Model for tutorial information."""

    def __init__(self, title: str, description: str, url: str, category: str, topics: List[str]):
        self.title = title
        self.description = description
        self.url = url
        self.category = category
        self.topics = topics

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "category": self.category,
            "topics": self.topics
        }


class VersionInfo:
    """Model for version information."""

    def __init__(self, latest_version: str, description: str, author: str,
                 homepage: str, release_date: Optional[str], python_requires: str,
                 pypi_url: str, documentation_url: str):
        self.latest_version = latest_version
        self.description = description
        self.author = author
        self.homepage = homepage
        self.release_date = release_date
        self.python_requires = python_requires
        self.pypi_url = pypi_url
        self.documentation_url = documentation_url

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "latest_version": self.latest_version,
            "description": self.description,
            "author": self.author,
            "homepage": self.homepage,
            "release_date": self.release_date,
            "python_requires": self.python_requires,
            "pypi_url": self.pypi_url,
            "documentation_url": self.documentation_url
        }


class LangChainDocumentationService:
    """Core service for LangChain documentation operations."""

    def __init__(self):
        self.timeout = REQUEST_TIMEOUT

    async def fetch_url(self, url: str, timeout: int = None) -> Optional[str]:
        """
        Fetch content from a URL with error handling.

        Args:
            url: The URL to fetch
            timeout: Request timeout in seconds

        Returns:
            The response text or None if failed
        """
        if timeout is None:
            timeout = self.timeout

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except (httpx.RequestError, httpx.HTTPStatusError) as error:
            print(f"Error fetching {url}: {error}")
            return None

    async def fetch_json(self, url: str, timeout: int = None) -> Optional[Dict]:
        """
        Fetch JSON content from a URL with error handling.

        Args:
            url: The URL to fetch JSON from
            timeout: Request timeout in seconds

        Returns:
            The parsed JSON data or None if failed
        """
        if timeout is None:
            timeout = self.timeout

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as error:
            print(f"Error fetching JSON from {url}: {error}")
            return None

    def extract_text_content(self, html: str, max_length: int = 200) -> str:
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
        chunks = (phrase.strip()
                  for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text[:max_length] + "..." if len(text) > max_length else text

    def extract_class_info(self, file_content: str, class_name: str) -> tuple[str, List[str]]:
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

    def determine_category_from_path(self, path: str) -> str:
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

    async def search_documentation(self, query: str, limit: int = 10) -> List[DocSearchResult]:
        """
        Search through real LangChain documentation using site search.

        Args:
            query: The search term or phrase
            limit: Maximum number of results to return

        Returns:
            List of documentation search results from the official LangChain docs
        """
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
            content = await self.fetch_url(url)

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
                    description = self.extract_text_content(
                        str(first_p)) if first_p else ""

                category = self.determine_category_from_path(section_path)

                results.append(DocSearchResult(
                    title=title,
                    url=url,
                    summary=description,
                    category=category,
                    last_updated=datetime.now().strftime("%Y-%m-%d")
                ))

        return results[:limit]

    async def get_api_reference(self, class_name: str) -> APIReference:
        """
        Get real API reference for a LangChain class from GitHub source.

        Args:
            class_name: Name of the LangChain class (e.g., 'ChatOpenAI', 'LLMChain')

        Returns:
            Real API reference scraped from LangChain documentation or source code
        """
        # Search for the class in GitHub
        search_url = f"{GITHUB_API_BASE}/search/code?q={class_name}+language:python"
        search_results = await self.fetch_json(search_url)

        if not search_results or not search_results.get('items'):
            raise ValueError(
                f"Class '{class_name}' not found in LangChain repository")

        # Get the first relevant file
        file_info = search_results['items'][0]
        file_url = file_info['html_url']

        # Get raw file content
        raw_url = file_url.replace(
            'github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
        file_content = await self.fetch_url(raw_url)

        if not file_content:
            raise ValueError("Could not fetch source code")

        # Parse the Python file to extract class information
        description, methods = self.extract_class_info(
            file_content, class_name)

        # Get module path from file path
        module_path = file_info['path'].replace('/', '.').replace('.py', '')

        return APIReference(
            class_name=class_name,
            module_path=module_path,
            description=description or f"LangChain {class_name} class",
            methods=methods,
            parameters={},
            examples=[],
            source_url=file_url
        )

    async def get_github_examples(self, query: Optional[str] = None, limit: int = 5) -> List[GitHubExample]:
        """
        Get real code examples from the LangChain GitHub repository.

        Args:
            query: Optional search term to filter examples
            limit: Maximum number of examples to return

        Returns:
            List of real code examples from the LangChain repository
        """
        # Search for Python example files in the LangChain repository
        search_query = f"extension:py {query or 'example'}"
        search_url = f"{GITHUB_API_BASE}/search/code?q={quote(search_query)}"

        search_results = await self.fetch_json(search_url)

        if not search_results or not search_results.get('items'):
            return []

        examples = []

        for item in search_results['items'][:limit]:
            # Get raw file content
            raw_url = item['html_url'].replace(
                'github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
            content = await self.fetch_url(raw_url)

            # Only include reasonably sized files
            if content and len(content) < 5000:
                examples.append(GitHubExample(
                    filename=item['name'],
                    content=content,
                    url=item['html_url'],
                    description=f"Example from {item['path']}"
                ))

        return examples

    async def get_tutorials(self) -> List[TutorialInfo]:
        """
        Get real tutorials and guides from LangChain documentation.

        Returns:
            List of tutorials scraped from the official documentation
        """
        # Fetch the main tutorials page
        tutorials_url = f"{LANGCHAIN_DOCS_BASE}/docs/tutorials/"
        content = await self.fetch_url(tutorials_url)

        if not content:
            raise ValueError("Could not fetch tutorials page")

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

        return unique_tutorials[:10]  # Limit to 10 tutorials

    async def get_latest_version(self) -> VersionInfo:
        """
        Get the latest LangChain version information from PyPI.

        Returns:
            Latest version information from the official PyPI repository
        """
        pypi_url = "https://pypi.org/pypi/langchain/json"
        data = await self.fetch_json(pypi_url)

        if not data:
            raise ValueError("Could not fetch version information")

        info = data.get('info', {})
        releases = data.get('releases', {})

        # Get latest version
        latest_version = info.get('version', 'Unknown')

        # Get release information
        latest_release_info = releases.get(latest_version, [])
        upload_time = None
        if latest_release_info:
            upload_time = latest_release_info[0].get('upload_time_iso_8601')

        return VersionInfo(
            latest_version=latest_version,
            description=info.get('summary', ''),
            author=info.get('author', ''),
            homepage=info.get('home_page', ''),
            release_date=upload_time,
            python_requires=info.get('requires_python', ''),
            pypi_url="https://pypi.org/project/langchain/",
            documentation_url=LANGCHAIN_DOCS_BASE
        )

    async def search_api_reference(self, query: str, limit: int = 5) -> List[DocSearchResult]:
        """
        Search through LangChain API reference using the official search.

        Args:
            query: The search term or phrase for API reference
            limit: Maximum number of results to return

        Returns:
            List of API reference search results
        """
        # Use the official LangChain API reference search
        search_url = f"{LANGCHAIN_DOCS_BASE}/api_reference/search.html?q={quote(query)}"
        content = await self.fetch_url(search_url)

        if not content:
            # Fallback to general API reference page
            api_url = f"{LANGCHAIN_DOCS_BASE}/api_reference/"
            content = await self.fetch_url(api_url)

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
                                description = self.extract_text_content(
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

        return results
