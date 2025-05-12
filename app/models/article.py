from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class TopStoriesArticleOut(BaseModel):
    title: str
    section: str
    url: Optional[HttpUrl] = None
    abstract: str
    published_date: datetime


TopStoriesResponse = List[TopStoriesArticleOut]


class ArticleSearchOut(BaseModel):
    headline: str
    snippet: str
    web_url: HttpUrl
    pub_date: datetime
