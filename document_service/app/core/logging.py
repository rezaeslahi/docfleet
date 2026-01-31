import logging

from .config import settings


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="ts=%(asctime)s level=%(levelname)s service=document-service msg=%(message)s",
    )