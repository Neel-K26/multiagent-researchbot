import logging
from typing import Any, Dict, List

from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search the web via DuckDuckGo and return title/url/snippet dicts.

    Falls back to an empty list (never raises) so callers can treat
    "no results" and "search failed" the same way.
    """
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))

        results = [
            {
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "snippet": item.get("body", ""),
            }
            for item in raw_results
        ]

        if not results:
            logger.warning("No web results found for query: %s", query)

        return results

    except Exception as exc:
        logger.error("Web search failed for query %r: %s", query, exc)
        return []
