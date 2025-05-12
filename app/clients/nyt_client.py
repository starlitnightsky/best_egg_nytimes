import asyncio
from datetime import date
from typing import Any, Dict, List
import logging

import httpx
from fastapi import Depends

from app.core.config import Settings, get_settings
from app.models.article import (
    ArticleSearchOut,
    TopStoriesArticleOut,
)

logger = logging.getLogger(__name__)

class NYTClient:
    """Thin async wrapper around the NY Times APIs we need."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: httpx.AsyncClient | None = None

    # --------------------------------------------------------------------- #
    # Context‑manager helpers so FastAPI can lifespan‑manage a single client
    # --------------------------------------------------------------------- #
    async def __aenter__(self) -> "NYTClient":
        self._client = httpx.AsyncClient(
            base_url=self._settings.nyt_base_url,
            timeout=self._settings.timeout_seconds,
            params={"api-key": self._settings.nyt_api_key},
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        if self._client is not None:
            await self._client.aclose()

    # -------------------------- Public methods --------------------------- #
    async def get_top_stories(self, section: str) -> List[TopStoriesArticleOut]:
        if self._client is None:  # pragma: no cover
            raise RuntimeError("NYTClient must be used within an async‑context")

        try:
            resp = await self._client.get(f"/topstories/v2/{section}.json")
            resp.raise_for_status()
            data = resp.json().get("results", [])
            
            logger.info(f"NYT API response for section {section}: {data}")
            
            articles = []
            for item in data:
                try:
                    article = TopStoriesArticleOut(
                        title=item["title"],
                        section=item["section"],
                        url=item.get("url") if item.get("url") else None,
                        abstract=item["abstract"],
                        published_date=item["published_date"],
                    )
                    articles.append(article)
                except Exception as e:
                    logger.error(f"Error processing article: {item}, Error: {str(e)}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching top stories for section {section}: {str(e)}")
            raise

    async def search_articles(
        self,
        q: str,
        begin_date: date | None = None,
        end_date: date | None = None,
    ) -> List[ArticleSearchOut]:
        if self._client is None:  # pragma: no cover
            raise RuntimeError("NYTClient must be used within an async‑context")

        params: Dict[str, Any] = {"q": q}
        if begin_date:
            params["begin_date"] = begin_date.strftime("%Y%m%d")
        if end_date:
            params["end_date"] = end_date.strftime("%Y%m%d")

        resp = await self._client.get("/search/v2/articlesearch.json", params=params)
        resp.raise_for_status()
        data = resp.json()["response"]["docs"]

        return [
            ArticleSearchOut(
                headline=item["headline"]["main"],
                snippet=item["snippet"],
                web_url=item["web_url"],
                pub_date=item["pub_date"],
            )
            for item in data
        ]


# ----------------- FastAPI dependency that yields a shared client ---------------- #
async def get_nyt_client(
    settings: Settings = Depends(get_settings),
) -> NYTClient:
    async with NYTClient(settings) as client:
        yield client
