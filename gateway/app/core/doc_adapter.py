from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.core.config import settings


def _pick_text(doc: Dict[str, Any]) -> str:
    """
    Tolerant extractor: supports future schema changes.
    Prefer 'text', fallback to 'body', fallback to empty string.
    """
    if isinstance(doc.get("text"), str):
        return doc["text"]
    if isinstance(doc.get("body"), str):
        return doc["body"]
    return ""


def adapt_docs_for_ml(raw_docs: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Convert Document Service response to ML service schema:
    ML expects: {id:int, title:str, text:str, tags:list[str]}

    Also:
    - cap number of docs
    - truncate text
    - return metadata about truncation
    """
    limited = raw_docs[: settings.ml_max_docs_to_rank]

    truncated_count = 0
    adapted: List[Dict[str, Any]] = []

    for d in limited:
        doc_id = int(d.get("id"))
        title = str(d.get("title") or "")
        tags = d.get("tags") or []
        if not isinstance(tags, list):
            tags = []

        text = _pick_text(d)
        # include title + text in ML input, but keep separate fields for service contract
        if len(text) > settings.ml_max_text_chars:
            text = text[: settings.ml_max_text_chars]
            truncated_count += 1

        adapted.append(
            {
                "id": doc_id,
                "title": title,
                "text": text,
                "tags": [str(t) for t in tags if t is not None],
            }
        )

    meta = {
        "sent_to_ml": len(adapted),
        "truncated_docs": truncated_count,
        "max_docs_limit": settings.ml_max_docs_to_rank,
        "max_text_chars": settings.ml_max_text_chars,
    }
    return adapted, meta
