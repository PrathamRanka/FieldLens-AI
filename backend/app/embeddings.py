import hashlib, math
from .config import settings
DIM=768
class Embedder:
    def embed(self, text: str) -> list[float]:
        if settings.embedding_provider == "vertex":
            from google import genai
            client=genai.Client(vertexai=True, project=settings.google_cloud_project, location=settings.google_cloud_location)
            result=client.models.embed_content(model=settings.embedding_model, contents=text)
            return list(result.embeddings[0].values)
        # Deterministic feature-hash vector for local tests only. Not semantic embeddings.
        vec=[0.0]*DIM
        for token in text.lower().split():
            h=int(hashlib.sha256(token.encode()).hexdigest()[:8],16)%DIM
            vec[h]+=1.0
        norm=math.sqrt(sum(x*x for x in vec)) or 1.0
        return [x/norm for x in vec]
embedder=Embedder()
