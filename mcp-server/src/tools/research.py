"""Research MCP tools — web search and URL content extraction.

- web_search: search via Tavily or Brave API
- fetch_url: fetch URL content, extract text via html2text

Reference: reference/obsidian-productivity-agent/backend_agent_api/tools.py
"""

import json
import logging

import html2text
import httpx

from src.server import brave_api_key, mcp, tavily_api_key

logger = logging.getLogger(__name__)

MAX_FETCH_CHARS = 5000


@mcp.tool()
async def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for information on a topic.

    Args:
        query: Search query.
        max_results: Number of results to return (default 5).
    """
    try:
        if tavily_api_key:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    json={"api_key": tavily_api_key, "query": query, "max_results": max_results},
                )
                resp.raise_for_status()
                return json.dumps(resp.json())

        if brave_api_key:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    params={"q": query, "count": max_results},
                    headers={"X-Subscription-Token": brave_api_key},
                )
                resp.raise_for_status()
                return json.dumps(resp.json())

        return json.dumps(
            {"error": "No search API key configured. Set TAVILY_API_KEY or BRAVE_API_KEY."}
        )

    except httpx.HTTPStatusError as e:
        return json.dumps(
            {"error": f"Search API returned {e.response.status_code}: {e.response.text}"}
        )
    except Exception as e:
        return json.dumps({"error": f"Web search failed: {e}"})


@mcp.tool()
async def fetch_url(url: str) -> str:
    """Fetch a web page and extract its text content.

    Args:
        url: The URL to fetch.
    """
    try:
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": "Athena/0.1 (research assistant)"},
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        if "html" in content_type:
            converter = html2text.HTML2Text()
            converter.ignore_links = False
            converter.ignore_images = True
            text = converter.handle(resp.text)
        else:
            text = resp.text[:2000]

        if len(text) > MAX_FETCH_CHARS:
            text = text[:MAX_FETCH_CHARS] + "\n\n[... truncated]"

        return json.dumps({"url": url, "content": text})

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"URL returned {e.response.status_code}"})
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch URL: {e}"})
