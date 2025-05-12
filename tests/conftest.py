import pytest
import respx
from httpx import Response


@pytest.fixture
def respx_mock():
    """Yields a fresh respx router for each test."""
    with respx.mock(assert_all_called=False) as router:
        yield router


@pytest.fixture(autouse=True)
def _fastapi_settings_env(monkeypatch):
    # Provide dummy NYT_API_KEY so settings validate
    monkeypatch.setenv("NYT_API_KEY", "DUMMY_KEY")
