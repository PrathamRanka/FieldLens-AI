from .config import settings
class LLM:
    def __init__(self): self.client=None
    def generate(self, prompt: str) -> tuple[str,int,int]:
        if settings.llm_provider == "mock":
            return ("[DEVELOPMENT MOCK] I would answer this using the retrieved evidence. Configure Vertex AI to enable grounded Gemini responses.", 80, 35)
        from google import genai
        self.client = self.client or genai.Client(vertexai=True, project=settings.google_cloud_project, location=settings.google_cloud_location)
        response=self.client.models.generate_content(model=settings.gemini_model, contents=prompt)
        usage=getattr(response,"usage_metadata",None)
        inp=getattr(usage,"prompt_token_count",0) or 0
        out=getattr(usage,"candidates_token_count",0) or 0
        return (response.text or "No response generated.", inp, out)
llm=LLM()
