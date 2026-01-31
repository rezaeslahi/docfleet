from typing import List, Any
from httpx import AsyncClient, Timeout, HTTPStatusError
from core.config import settings
from .sources import SourceDoc, SOURCES
from asyncio import Semaphore,create_task, gather
from datetime import datetime, timezone
from downloader.storage import save_file
import uuid
import logging
import os

logger = logging.getLogger(__name__)

async def _fetch_text(sourceDoc: SourceDoc, client: AsyncClient)->str:
    logger.info("downloading title=%s", sourceDoc.title)
    resp = await client.get(sourceDoc.url)
    if resp.status_code != 200:
        raise HTTPStatusError(message="Error in downloading")
    return resp.text

def get_unique_file_name(sourceDoc: SourceDoc)->str:
    prefix = "file_"
    suffix = ".md"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    id = uuid.uuid4().hex[:8]
    name = f"{prefix}_{timestamp}_{id}_{suffix}"
    return name

async def perform_one_download(include_text:bool,sourceDoc: SourceDoc, semaphore: Semaphore, client: AsyncClient)->dict:
    async with semaphore:                
        # fetch text
        text = await _fetch_text(sourceDoc=sourceDoc, client=client)
        name = get_unique_file_name(sourceDoc)
        # save file on stotage        
        logger.info("CWD=%s", os.getcwd())
        logger.info("data_dir(raw)=%r abs=%r", settings.data_dir, os.path.abspath(settings.data_dir))
        res = await save_file(dir=settings.data_dir,file_name=name,text=text)
        res["title"] = sourceDoc.title
        res["url"] = sourceDoc.url
        if include_text:
            res["text"] = text
        return res
    pass

async def download_many(sources:List[SourceDoc], include_text:bool)->List[dict]:
    timeout = Timeout(settings.time_out)
    sem = Semaphore(settings.max_concurrency)
    async with AsyncClient(timeout=timeout) as client:
        tasks = [create_task(perform_one_download(include_text=include_text,sourceDoc=source_doc,semaphore=sem, client=client)) for source_doc in sources ]
        results = await gather(*tasks, return_exceptions=True)
        return results