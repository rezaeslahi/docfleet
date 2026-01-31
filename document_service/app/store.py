# This is a temporary in-memoory database for ddcuments
from threading import Lock
from typing import List, Dict, Tuple, Optional
from .models import Document, DocumentCreate
from itertools import islice

class DocumentStore():
    # we need a dict for docs
    # we need a lock
    # there should be an id manager as well
    # there should be some functions
    doc_global_id = 1
    def __init__(self):
        self._lock = Lock()
        self._docs: Dict[int,Document] = {}
        self._seed()
    
    def _seed(self):
        seed: List[Tuple[str, str, str, List[str]]] = [
            ("Intro to Offshore Wind", "Offshore wind projects involve site assessment, metocean data, and foundation design.", "", ["wind", "offshore", "intro"]),
            ("Metocean Basics", "Metocean combines meteorological and oceanographic data used for marine engineering.", "", ["metocean", "data"]),
            ("UXO Identification", "Unexploded ordnance (UXO) risk assessment is critical in offshore construction surveys.", "", ["uxo", "risk"]),
            ("FastAPI Async Patterns", "FastAPI supports async endpoints; use httpx.AsyncClient for non-blocking HTTP calls.", "", ["fastapi", "async"]),
            ("Microservices 101", "Microservices split a system into independently deployable services communicating over HTTP APIs.", "", ["microservices", "architecture"]),
            ("TF-IDF Retrieval", "TF-IDF with cosine similarity is a strong baseline for document retrieval and ranking.", "", ["ml", "tfidf", "retrieval"]),
            ("Logging & Observability", "Structured logs and request IDs help trace requests across distributed services.", "", ["observability", "logging"]),
            ("Twelve-Factor Config", "Store config in environment variables; keep services stateless for portability.", "", ["config", "12factor"]),
            ("Docker Compose Networking", "Compose creates a network so services can reach each other by service name.", "", ["docker", "compose"]),
            ("API Gateway Pattern", "A gateway orchestrates calls to backend services and provides a single public entrypoint.", "", ["gateway", "api"]),
        ]
        for title,text,url,tags in seed:
            doc_create = DocumentCreate(title=title,text=text,url=url or None,tags=tags)
            self.create_document(doc_create)
        pass

    def create_document(self,doc: DocumentCreate)->Document:
        with self._lock:
            id = DocumentStore.doc_global_id
            DocumentStore.doc_global_id += 1
            new_doc = Document(id=id, title=doc.title, text=doc.text,source_url=doc.source_url,tags=doc.tags)
            self._docs[id] = new_doc
            return new_doc
        
    def list_documents(self,first_n: Optional[int]=None)->List[Document]:
        
        if first_n is None:
            return list(self._docs.values())
        else:            
            return list(islice(self._docs.values(),first_n))
    
    def get_doc(self,doc_id:int)->Document:
        return self._docs[doc_id]
    
    def ingest_many(self, docs: List[DocumentCreate])->List[Document]:
        newly_stored: List[Document]=[]
        for doc in docs:
            self.create_document(doc)
            newly_stored.append(doc)
        return newly_stored
doc_store = DocumentStore()
