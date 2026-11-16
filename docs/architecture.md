# Architecture and engineering decisions

## Request lifecycle
1. FastAPI authenticates the caller and validates request shape.
2. LangGraph routes to RAG or analytics based on request mode and lightweight intent rules.
3. RAG embeds the query, retrieves top-k pgvector chunks, and passes bounded evidence to Gemini.
4. Analytics uses a read-only, allowlisted SQL template. The SQL guard rejects mutation verbs, multiple statements, and non-allowlisted tables.
5. A reflection node records a quality-check step. The response includes request ID, sources, and latency/cost telemetry.

## Agent patterns
- **ReAct-style tool use:** explicit observe/retrieve/answer steps; no unconstrained shell or arbitrary API tools.
- **Self-reflection:** a bounded post-generation check node. Upgrade to a second-model critique with a measured quality/cost trade-off.
- **Hierarchical delegation:** optional CrewAI example separates research, analysis, and review roles.
- **Google ADK:** optional tool-bounded agent example for a Google-native agent runtime.

## Retrieval algorithm
The index uses cosine similarity over vector embeddings and returns top-k passages. Chunking uses a fixed token-like word window with overlap. For production, compare chunking strategies, add metadata filters, hybrid BM25/vector retrieval, reranking, and document-level access control.

## Security boundaries
The demo API key is not a user identity system. Add OIDC/IAP, tenant-scoped document ACLs, malware scanning, signed upload URLs, rate limits, audit retention, and secrets rotation before production use. Retrieved documents are untrusted input. The model has no arbitrary shell, network, or write-capable database tool.
