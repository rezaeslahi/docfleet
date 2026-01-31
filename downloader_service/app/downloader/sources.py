from dataclasses import dataclass
from typing import List

@dataclass()
class SourceDoc():
    title: str
    url: str

# Small, public markdown/text files (GitHub raw)
SOURCES: List[SourceDoc] = [
SourceDoc(
title="GitHub Markdown Guide",
url="https://raw.githubusercontent.com/adam-p/markdown-here/master/README.md",
),
SourceDoc(
title="Python Requests README",
url="https://raw.githubusercontent.com/psf/requests/main/README.md",
),
SourceDoc(
title="FastAPI README",
url="https://raw.githubusercontent.com/tiangolo/fastapi/master/README.md",
),
SourceDoc(
title="httpx README",
url="https://raw.githubusercontent.com/encode/httpx/master/README.md",
),
SourceDoc(
title="Docker Compose README",
url="https://raw.githubusercontent.com/docker/compose/main/README.md",
),
]