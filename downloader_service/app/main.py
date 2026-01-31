import logging
from typing import Any, Dict, List, Optional


from fastapi import FastAPI, HTTPException, Query


from core.logging import setup_logging
from core.request_id import request_id_middleware
from downloader.download import download_many
from downloader.sources import SOURCES
import uvicorn

setup_logging()
logger = logging.getLogger(__name__)


app = FastAPI(title="DocFleet Downloader Service", version="0.1.0")
app.middleware("http")(request_id_middleware)




@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

@app.post("/download")
async def download(count:Optional[int]=None, include_text:Optional[bool] = True)->Dict[str,Any]:
    num = len(SOURCES)
    if count is not None:
        num = min(count,len(SOURCES))
    try:
        results = await download_many(SOURCES[:num],include_text=include_text)
        print(f"len of result = {len(results)}")
        print(results)
        print(type(results))
        print()
    except:
        raise HTTPException(status_code=500, detail="Some downloades faild")
    return {"count":len(results),"items":results}
    
def run_server():
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )

if __name__ == "__main__":
    run_server()