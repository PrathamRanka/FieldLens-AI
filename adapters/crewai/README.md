# CrewAI adapter (optional)

The main application uses LangGraph. This directory is an optional CrewAI proof-of-concept for hierarchical delegation. Install the dev extra (`pip install -e '.[dev]'`) and set `OPENAI_API_KEY` only if you choose an OpenAI-backed CrewAI model. For a Vertex AI model, configure the provider integration supported by the CrewAI version you install. API compatibility changes quickly, so pin and test versions before claiming this adapter is integrated into the deployed service.

`crew.py` defines a researcher, analyst, and reviewer with explicit task boundaries. It is intentionally a separate executable example rather than a runtime dependency of the API.
