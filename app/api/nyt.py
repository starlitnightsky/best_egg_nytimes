import asyncio
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.clients.nyt_client import NYTClient, get_nyt_client
from app.core.config import Settings, get_settings
from app.models.article import (
    ArticleSearchOut,
    TopStoriesArticleOut,
    TopStoriesResponse,
)

router = APIRouter(prefix="/nytimes", tags=["nytimes"])


@router.get(
    "/topstories",
    response_model=TopStoriesResponse,
    summary="Get two most recent articles from configured NYT sections",
)
async def top_stories(
    client: NYTClient = Depends(get_nyt_client),
    settings: Settings = Depends(get_settings),
) -> List[TopStoriesArticleOut]:
    try:
        tasks = [client.get_top_stories(section) for section in settings.top_sections]
        per_section = await asyncio.gather(*tasks)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"NYT API error: {exc}",
        ) from exc

    # Flatten, take two newest per section, return combined list sorted by datetime
    combined: List[TopStoriesArticleOut] = []
    for articles in per_section:
        combined.extend(sorted(articles, key=lambda a: a.published_date, reverse=True)[:2])

    return sorted(combined, key=lambda a: a.published_date, reverse=True)


@router.get(
    "/articlesearch",
    response_model=List[ArticleSearchOut],
    summary="Full‑text search of NYT articles with optional date range",
)
async def article_search(
    q: str = Query(..., min_length=2, description="Search query terms"),
    begin_date: date | None = Query(
        None,
        description="Filter results starting this date (YYYY‑MM‑DD)",
    ),
    end_date: date | None = Query(
        None,
        description="Filter results ending this date (YYYY‑MM‑DD)",
    ),
    client: NYTClient = Depends(get_nyt_client),
) -> List[ArticleSearchOut]:
    if begin_date and end_date and begin_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="begin_date cannot be after end_date",
        )
    try:
        return await client.search_articles(q, begin_date, end_date)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"NYT API error: {exc}",
        ) from exc
