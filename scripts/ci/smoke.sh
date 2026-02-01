#!/usr/bin/env bash
set -euo pipefail

GATEWAY_HEALTH="${GATEWAY_HEALTH:-http://localhost:8000/health}"
USER_HEALTH="${USER_HEALTH:-http://localhost:8001/health}"
DOCS_HEALTH="${DOCS_HEALTH:-http://localhost:8002/health}"
DOWNLOADER_HEALTH="${DOWNLOADER_HEALTH:-http://localhost:8003/health}"
ML_HEALTH="${ML_HEALTH:-http://localhost:8004/health}"
MLFLOW_URL="${MLFLOW_URL:-http://localhost:5000}"

echo "==> Waiting for services..."
./scripts/ci/wait_http.sh "$GATEWAY_HEALTH" 90
./scripts/ci/wait_http.sh "$USER_HEALTH" 90
./scripts/ci/wait_http.sh "$DOCS_HEALTH" 90
./scripts/ci/wait_http.sh "$DOWNLOADER_HEALTH" 90
./scripts/ci/wait_http.sh "$ML_HEALTH" 90
./scripts/ci/wait_http.sh "$MLFLOW_URL" 120 --head

echo "==> Install test deps..."
python -m pip install --upgrade pip
pip install -r ml_service/requirements.txt
pip install pytest requests

echo "==> Run smoke test..."
pytest -q tests/integration/test_search_smoke.py

echo "OK: smoke"
