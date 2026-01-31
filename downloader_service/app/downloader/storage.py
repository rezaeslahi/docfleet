import os
import aiofiles

async def save_file(dir:str, file_name:str, text:str)->dict:
    os.makedirs(dir,exist_ok=True)
    path = os.path.join(dir, file_name)
    async with aiofiles.open(path,"w",encoding="utf-8") as file:
        await file.write(text)
    # confirm it exists
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else -1
    return {"path": path, "exists": exists, "size_bytes": size}