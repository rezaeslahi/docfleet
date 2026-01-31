import logging

from .config import settings


def setup_logging() -> None:
    # Simple, production-ish structured style (key=value)
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="ts=%(asctime)s level=%(levelname)s service=user-service msg=%(message)s",
    )
