import re, uuid
from pathlib import Path
from .db import connect
from .embeddings import embedder
from .config import settings

def extract_text(filename: str, raw: bytes) -> str:
    suffix=Path(filename).suffix.lower()
    if suffix in {".txt", ".md", ".csv", ".json"}: return raw.decode("utf-8", errors="replace")
    if suffix == ".pdf":
        from pypdf import PdfReader
        import io
        return "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(raw)).pages)
    raise ValueError("Supported file types: TXT, MD, CSV, JSON, PDF")

def chunk_text(text: str, size: int=900, overlap: int=120) -> list[str]:
    words=re.findall(r"\S+",text)
    if not words: return []
    chunks=[]; start=0
    while start < len(words):
        end=min(start+size,len(words)); chunks.append(" ".join(words[start:end]))
        if end==len(words): break
        start=end-overlap
    return chunks

def store_document(filename: str, mime: str, raw: bytes) -> str:
    text=extract_text(filename,raw)
    doc_id=str(uuid.uuid4()); chunks=chunk_text(text); storage_uri=None
    if settings.gcs_bucket:
        from google.cloud import storage
        client=storage.Client()
        blob=client.bucket(settings.gcs_bucket).blob(f"uploads/{doc_id}/{Path(filename).name}")
        blob.upload_from_string(raw, content_type=mime or "application/octet-stream")
        storage_uri=f"gs://{settings.gcs_bucket}/{blob.name}"
    with connect() as conn:
        conn.execute("INSERT INTO documents(id,filename,mime_type,storage_uri) VALUES(%s,%s,%s,%s)",(doc_id,filename,mime or "application/octet-stream",storage_uri))
        for i,chunk in enumerate(chunks):
            vec=embedder.embed(chunk)
            conn.execute("INSERT INTO chunks(document_id,chunk_index,content,embedding) VALUES(%s,%s,%s,%s)",(doc_id,i,chunk,vec))
    return doc_id

def retrieve(query: str, limit: int=5):
    vec=embedder.embed(query)
    with connect() as conn:
        rows=conn.execute("""SELECT c.id,c.content,d.filename,1-(c.embedding <=> %s::vector) AS score
          FROM chunks c JOIN documents d ON d.id=c.document_id ORDER BY c.embedding <=> %s::vector LIMIT %s""",(vec,vec,limit)).fetchall()
    return rows
