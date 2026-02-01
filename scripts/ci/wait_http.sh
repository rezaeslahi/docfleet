#!/usr/bin/env bash
set -euo pipefail

# Wait until an HTTP endpoint returns success (2xx/3xx).
# Usage:
#   ./scripts/ci/wait_http.sh "http://localhost:8001/health" 60
#   ./scripts/ci/wait_http.sh "http://localhost:5000" 120 --head

URL="${1:-}"
TIMEOUT_SECONDS="${2:-60}"
MODE="${3:-}" # optional: --head

if [[ -z "$URL" ]]; then
  echo "ERROR: URL is required"
  exit 2
fi

start="$(date +%s)"
while true; do
  if [[ "$MODE" == "--head" ]]; then
    if curl -fsSI --max-time 5 "$URL" >/dev/null 2>&1; then
      echo "OK: $URL"
      exit 0
    fi
  else
    if curl -fsS --max-time 5 "$URL" >/dev/null 2>&1; then
      echo "OK: $URL"
      exit 0
    fi
  fi

  now="$(date +%s)"
  elapsed=$((now - start))
  if (( elapsed >= TIMEOUT_SECONDS )); then
    echo "ERROR: timed out after ${TIMEOUT_SECONDS}s waiting for $URL"
    exit 1
  fi

  sleep 1
done
