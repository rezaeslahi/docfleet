import os
import requests
import pytest


@pytest.mark.integration
def test_search_smoke():
    base = os.environ.get("GATEWAY_BASE_URL", "http://localhost:8000")
    r = requests.get(f"{base}/search", params={"query": "fastapi async", "n": 3}, timeout=15)
    r.raise_for_status()
    data = r.json()
    assert "results" in data and len(data["results"]) > 0
    assert "score" in data["results"][0]
