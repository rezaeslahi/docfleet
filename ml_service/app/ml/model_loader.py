import logging
import time
from typing import Any, Optional, Tuple

import mlflow
import mlflow.sklearn

from app.core.config import settings

logger = logging.getLogger(__name__)

# in-process cache
_CACHED_MODEL: Optional[Any] = None
_CACHED_VERSION: Optional[str] = None
_LAST_CHECK_TS: float = 0.0


def _model_uri() -> str:
    return f"models:/{settings.registered_model_name}@{settings.model_alias}"


def _current_alias_version() -> str:
    """
    Ask MLflow Registry: which model version does alias (e.g. 'champion') currently point to?
    """
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    client = mlflow.MlflowClient()
    mv = client.get_model_version_by_alias(settings.registered_model_name, settings.model_alias)
    # version is a string in MLflow APIs
    return str(mv.version)


def _should_check(now: float) -> bool:
    """
    Avoid hitting MLflow registry on every request.
    You can tune this (env var later). Default: check every 10 seconds.
    """
    global _LAST_CHECK_TS
    if now - _LAST_CHECK_TS >= 10.0:
        _LAST_CHECK_TS = now
        return True
    return False


def load_champion_model(force_reload: bool = False) -> Tuple[Any, str]:
    """
    Returns (model, version). Auto-reloads if alias version changed.
    """
    global _CACHED_MODEL, _CACHED_VERSION

    now = time.time()

    # First load, or explicit reload
    if _CACHED_MODEL is None or force_reload:
        version = _current_alias_version()
        uri = _model_uri()
        logger.info("loading_model uri=%s version=%s force=%s", uri, version, force_reload)
        _CACHED_MODEL = mlflow.sklearn.load_model(uri)
        _CACHED_VERSION = version
        logger.info("model_loaded uri=%s version=%s", uri, version)
        return _CACHED_MODEL, _CACHED_VERSION

    # Throttled check: does alias point to new version?
    if _should_check(now):
        try:
            current_version = _current_alias_version()
        except Exception as e:
            # If registry is temporarily unavailable, keep serving cached model
            logger.warning("model_version_check_failed err=%s cached_version=%s", e, _CACHED_VERSION)
            return _CACHED_MODEL, _CACHED_VERSION  # type: ignore

        if current_version != _CACHED_VERSION:
            uri = _model_uri()
            logger.info("alias_updated old=%s new=%s reloading uri=%s", _CACHED_VERSION, current_version, uri)
            _CACHED_MODEL = mlflow.sklearn.load_model(uri)
            _CACHED_VERSION = current_version
            logger.info("model_reloaded version=%s", _CACHED_VERSION)

    return _CACHED_MODEL, _CACHED_VERSION  # type: ignore
