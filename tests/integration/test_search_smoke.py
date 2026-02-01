import os
import requests


def test_search_smoke():
    base = os.environ.get("GATEWAY_BASE_URL", "http://localhost:8000")
    url = f"{base}/search"

    r = requests.get(
        url,
        params={"query": "fastapi async", "n": 3},
        timeout=15,
    )
    r.raise_for_status()

    data = r.json()
    assert "results" in data, f"Missing 'results' key. keys={list(data.keys())}"
    assert len(data["results"]) > 0, "No results returned"
    assert "score" in data["results"][0], "No score field in first result"
