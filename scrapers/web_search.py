"""Generic web search placeholder scraper."""

from __future__ import annotations

from typing import Any


def scrape_web_generic(query: str, location: str = "", max_results: int = 100) -> list[dict[str, Any]]:
    # Use an official search API in production, e.g. Google Custom Search, Bing Web Search, SerpAPI, etc.
    return []
