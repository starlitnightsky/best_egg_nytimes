from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def _fake_topstories_payload(section: str):
    return {
        "results": [
            {
                "title": f"Title {i} {section}",
                "section": section,
                "url": f"https://nytimes.com/{section}/{i}",
                "abstract": f"Abstract {i}",
                "published_date": (datetime.utcnow()).isoformat(),
            }
            for i in range(5)
        ]
    }


def test_topstories(respx_mock):
    # Mock five section calls
    base = "https://api.nytimes.com/svc/topstories/v2"
    for section in ["arts", "food", "movies", "travel", "science"]:
        respx_mock.get(f"{base}/{section}.json").mock(
            return_value=Response(200, json=_fake_topstories_payload(section)),
        )

    resp = client.get("/nytimes/topstories")
    assert resp.status_code == 200
    data = resp.json()
    # 5 sections × 2 items each
    assert len(data) == 10
    # Ensure keys exist
    assert {"title", "section", "url", "abstract", "published_date"} <= data[0].keys()


def test_article_search(respx_mock):
    respx_mock.get("https://api.nytimes.com/svc/search/v2/articlesearch.json").mock(
        return_value=Response(
            200,
            json={
                "response": {
                    "docs": [
                        {
                            "headline": {"main": "Bitcoin surges"},
                            "snippet": "Crypto news …",
                            "web_url": "https://nytimes.com/crypto",
                            "pub_date": datetime.utcnow().isoformat(),
                        }
                    ]
                }
            },
        )
    )

    resp = client.get("/nytimes/articlesearch?q=bitcoin")
    assert resp.status_code == 200
    assert resp.json()[0]["headline"] == "Bitcoin surges"


@pytest.mark.parametrize(
    "querystring",
    ["", "q=1", "begin_date=2025-01-01&end_date=2024-01-01&q=test"],
)
def test_bad_requests(querystring):
    resp = client.get(f"/nytimes/articlesearch?{querystring}")
    assert resp.status_code in (400, 422)
