#!/usr/bin/env bash
set -euo pipefail

# Configurable via env vars (nice for local + CI)
DOCS_URL="${DOCS_URL:-http://localhost:8002/document}"
DOCS_HEALTH_URL="${DOCS_HEALTH_URL:-http://localhost:8002/health}"
MLFLOW_URL="${MLFLOW_URL:-http://localhost:5000}"
MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI:-http://127.0.0.1:5000}"
ML_SERVICE_HEALTH_URL="${ML_SERVICE_HEALTH_URL:-http://localhost:8004/health}"
ML_REFRESH_URL="${ML_REFRESH_URL:-http://localhost:8004/model/refresh}"

SNAPSHOT_PATH="${SNAPSHOT_PATH:-ml_service/artifacts/docs_snapshot.json}"
TRAIN_CONFIG="${TRAIN_CONFIG:-config/train_ci.yaml}"
TRAIN_SCRIPT="${TRAIN_SCRIPT:-run_training.py}"

echo "==> Waiting for services..."
./scripts/ci/wait_http.sh "$DOCS_HEALTH_URL" 90
./scripts/ci/wait_http.sh "$ML_SERVICE_HEALTH_URL" 90
./scripts/ci/wait_http.sh "$MLFLOW_URL" 120 --head

echo "==> MLflow experiments list (sanity check)..."
curl -fsS http://localhost:5000/api/2.0/mlflow/experiments/list | head -c 200
echo


echo "==> Snapshot documents..."
mkdir -p "$(dirname "$SNAPSHOT_PATH")"
curl -fsS --retry 20 --retry-connrefused --retry-delay 1 --max-time 10 \
  "$DOCS_URL" > "$SNAPSHOT_PATH"

python -c "import json; print('docs_snapshot_count=', len(json.load(open('$SNAPSHOT_PATH'))))"

echo "==> Install ML dependencies..."
python -m pip install --upgrade pip
pip install -r ml_service/requirements.txt

echo "==> Train against MLflow tracking URI: $MLFLOW_TRACKING_URI"
export MLFLOW_TRACKING_URI="$MLFLOW_TRACKING_URI"

(
  cd ml_service
  python "$TRAIN_SCRIPT" --config "$TRAIN_CONFIG" --docs "artifacts/$(basename "$SNAPSHOT_PATH")"
)

echo "==> Refresh ML service to load latest champion..."
curl -fsS --retry 20 --retry-connrefused --retry-delay 1 --max-time 10 \
  -X POST "$ML_REFRESH_URL" >/dev/null

echo "OK: mlops_train_refresh"
