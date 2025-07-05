"""
LangChain Documentation MCP Server

Native MCP server implementation using the official Python SDK.
Provides LangChain documentation access through the Model Context Protocol.
"""

import asyncio
import json
from typing import Any, Dict, List

import mcp.server.stdio
from mcp import types
from mcp.server import Server
from mcp.server.models import InitializationOptions

from ..services.langchain_service import LangChainDocumentationService


# Initialize the MCP server
server = Server("langchain-docs")

# Initialize the documentation service
doc_service = LangChainDocumentationService()


@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """
    List available LangChain documentation resources.

    Returns:
        List of available resources that can be read
    """
    return [
        types.Resource(
            uri="langchain://docs",
            name="LangChain Documentation",
            description="Official LangChain documentation and guides",
            mimeType="application/json"
        ),
        types.Resource(
            uri="langchain://api-reference",
            name="LangChain API Reference",
            description="Complete API reference for LangChain classes and functions",
            mimeType="application/json"
        ),
        types.Resource(
            uri="langchain://tutorials",
            name="LangChain Tutorials",
            description="Step-by-step tutorials and learning resources",
            mimeType="application/json"
        ),
        types.Resource(
            uri="langchain://examples",
            name="LangChain Code Examples",
            description="Real code examples from the LangChain GitHub repository",
            mimeType="application/json"
        ),
        types.Resource(
            uri="langchain://version",
            name="LangChain Version Info",
            description="Latest version information and release details",
            mimeType="application/json"
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """
    Read a specific LangChain documentation resource.

    Args:
        uri: The resource URI to read

    Returns:
        The resource content as a string
    """
    if uri == "langchain://docs":
        # Return general documentation overview
        return json.dumps({
            "description": "LangChain Documentation Access",
            "available_sections": [
                "introduction",
                "tutorials",
                "how_to",
                "concepts",
                "integrations",
                "api_reference"
            ],
            "usage": "Use the search_docs tool to search through documentation",
            "base_url": "https://python.langchain.com"
        }, indent=2)

    if uri == "langchain://api-reference":
        return json.dumps({
            "description": "LangChain API Reference",
            "usage": "Use the get_api_reference tool with a class name",
            "examples": ["ChatOpenAI", "LLMChain", "VectorStoreRetriever"],
            "github_source": "https://github.com/langchain-ai/langchain"
        }, indent=2)

    if uri == "langchain://tutorials":
        tutorials = await doc_service.get_tutorials()
        return json.dumps({
            "description": "LangChain Tutorials and Guides",
            "tutorials": [tutorial.to_dict() for tutorial in tutorials]
        }, indent=2)

    if uri == "langchain://examples":
        return json.dumps({
            "description": "LangChain Code Examples",
            "usage": "Use the get_github_examples tool to fetch real examples",
            "repository": "https://github.com/langchain-ai/langchain"
        }, indent=2)

    if uri == "langchain://version":
        version_info = await doc_service.get_latest_version()
        return json.dumps({
            "description": "LangChain Version Information",
            "version_info": version_info.to_dict()
        }, indent=2)

    raise ValueError(f"Unknown resource URI: {uri}")


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List available LangChain documentation tools.

    Returns:
        List of tools that can be called
    """
    return [
        types.Tool(
            name="search_docs",
            description="Search through LangChain documentation for specific topics",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for documentation"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="search_api_reference",
            description="Search specifically through LangChain API reference documentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for API reference"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 5)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_api_reference",
            description="Get detailed API reference for a specific LangChain class",
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": ("Name of the LangChain class "
                                        "(e.g., 'ChatOpenAI', 'LLMChain')")
                    }
                },
                "required": ["class_name"]
            }
        ),
        types.Tool(
            name="get_github_examples",
            description="Get real code examples from the LangChain GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Optional search term to filter examples"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of examples (default: 5)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="get_tutorials",
            description="Get available LangChain tutorials and learning resources",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get_latest_version",
            description="Get the latest LangChain version information from PyPI",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


async def _handle_search_docs(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle search_docs tool call."""
    query = arguments["query"]
    limit = arguments.get("limit", 10)

    results = await doc_service.search_documentation(query, limit)

    if not results:
        return [types.TextContent(
            type="text",
            text=f"No documentation found for query: '{query}'"
        )]

    # Format results for display
    formatted_results = []
    for result in results:
        formatted_results.append(
            f"**{result.title}** ({result.category})\n"
            f"URL: {result.url}\n"
            f"Summary: {result.summary}\n"
        )

    return [types.TextContent(
        type="text",
        text=f"Found {len(results)} documentation results for '{query}':\n\n" +
             "\n---\n".join(formatted_results)
    )]


async def _handle_search_api_reference(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle search_api_reference tool call."""
    query = arguments["query"]
    limit = arguments.get("limit", 5)

    results = await doc_service.search_api_reference(query, limit)

    if not results:
        return [types.TextContent(
            type="text",
            text=f"No API reference found for query: '{query}'"
        )]

    # Format results for display
    formatted_results = []
    for result in results:
        formatted_results.append(
            f"**{result.title}**\n"
            f"URL: {result.url}\n"
            f"Description: {result.summary}\n"
        )

    return [types.TextContent(
        type="text",
        text=f"Found {len(results)} API reference results for '{query}':\n\n" +
             "\n---\n".join(formatted_results)
    )]


async def _handle_get_api_reference(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle get_api_reference tool call."""
    class_name = arguments["class_name"]

    try:
        api_ref = await doc_service.get_api_reference(class_name)

        methods_text = ", ".join(
            api_ref.methods) if api_ref.methods else "No methods found"

        response = (
            f"**{api_ref.class_name}** API Reference\n\n"
            f"**Module:** {api_ref.module_path}\n"
            f"**Description:** {api_ref.description}\n"
            f"**Methods:** {methods_text}\n"
            f"**Source:** {api_ref.source_url}\n"
        )

        return [types.TextContent(type="text", text=response)]

    except ValueError as e:
        return [types.TextContent(
            type="text",
            text=f"Error getting API reference for '{class_name}': {str(e)}"
        )]


async def _handle_get_github_examples(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle get_github_examples tool call."""
    query = arguments.get("query")
    limit = arguments.get("limit", 5)

    examples = await doc_service.get_github_examples(query, limit)

    if not examples:
        search_term = f" for '{query}'" if query else ""
        return [types.TextContent(
            type="text",
            text=f"No code examples found{search_term}"
        )]

    # Format examples for display
    formatted_examples = []
    for example in examples:
        # Truncate content if too long
        content = example.content
        if len(content) > 500:
            content = content[:500] + \
                "...\n\n[Content truncated - see full example at URL]"

        formatted_examples.append(
            f"**{example.filename}**\n"
            f"Description: {example.description}\n"
            f"URL: {example.url}\n"
            f"```python\n{content}\n```"
        )

    search_info = f" for '{query}'" if query else ""
    return [types.TextContent(
        type="text",
        text=f"Found {len(examples)} code examples{search_info}:\n\n" +
             "\n\n---\n\n".join(formatted_examples)
    )]


async def _handle_get_tutorials(arguments: Dict[str, Any]) -> List[types.TextContent]:  # pylint: disable=unused-argument
    """Handle get_tutorials tool call."""
    tutorials = await doc_service.get_tutorials()

    if not tutorials:
        return [types.TextContent(
            type="text",
            text="No tutorials found"
        )]

    # Format tutorials for display
    formatted_tutorials = []
    for tutorial in tutorials:
        formatted_tutorials.append(
            f"**{tutorial.title}** ({tutorial.category})\n"
            f"Description: {tutorial.description}\n"
            f"URL: {tutorial.url}\n"
            f"Topics: {', '.join(tutorial.topics)}"
        )

    return [types.TextContent(
        type="text",
        text=f"Found {len(tutorials)} LangChain tutorials:\n\n" +
             "\n\n---\n\n".join(formatted_tutorials)
    )]


async def _handle_get_latest_version(arguments: Dict[str, Any]) -> List[types.TextContent]:  # pylint: disable=unused-argument
    """Handle get_latest_version tool call."""
    version_info = await doc_service.get_latest_version()

    response = (
        f"**LangChain Version Information**\n\n"
        f"**Latest Version:** {version_info.latest_version}\n"
        f"**Description:** {version_info.description}\n"
        f"**Author:** {version_info.author}\n"
        f"**Homepage:** {version_info.homepage}\n"
        f"**Python Requirements:** {version_info.python_requires}\n"
        f"**PyPI URL:** {version_info.pypi_url}\n"
        f"**Documentation:** {version_info.documentation_url}\n"
    )

    if version_info.release_date:
        response += f"**Release Date:** {version_info.release_date}\n"

    return [types.TextContent(type="text", text=response)]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Handle tool calls for LangChain documentation operations.

    Args:
        name: The name of the tool to call
        arguments: Arguments for the tool

    Returns:
        List of text content responses
    """
    try:
        # Use a dictionary to map tool names to handler functions
        handlers = {
            "search_docs": _handle_search_docs,
            "search_api_reference": _handle_search_api_reference,
            "get_api_reference": _handle_get_api_reference,
            "get_github_examples": _handle_get_github_examples,
            "get_tutorials": _handle_get_tutorials,
            "get_latest_version": _handle_get_latest_version,
        }

        if name in handlers:
            return await handlers[name](arguments)

        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

    except Exception as e:  # pylint: disable=broad-exception-caught
        return [types.TextContent(
            type="text",
            text=f"Error calling tool '{name}': {str(e)}"
        )]


async def main():
    """Main entry point for the MCP server."""
    # Initialize options can be set here if needed
    options = InitializationOptions(
        server_name="langchain-docs",
        server_version="1.0.0"
    )

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            options
        )


if __name__ == "__main__":
    asyncio.run(main())
