import logging
from typing import Any, Dict, List

import arxiv

logger = logging.getLogger(__name__)

_client = arxiv.Client()


def search_arxiv(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search arXiv and return a list of paper summaries.

    Falls back to an empty list (never raises) so callers can treat
    "no results" and "search failed" the same way.
    """
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        results = []
        for result in _client.results(search):
            results.append(
                {
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "abstract": result.summary,
                    "url": result.entry_id,
                    "published": result.published.isoformat() if result.published else None,
                }
            )

        if not results:
            logger.warning("No arXiv results found for query: %s", query)

        return results

    except Exception as exc:
        logger.error("arXiv search failed for query %r: %s", query, exc)
        return []
