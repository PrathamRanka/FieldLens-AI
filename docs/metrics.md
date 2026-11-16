# LLM metrics and evaluation

FieldLens reports request latency, token counts when supplied by the provider, estimated tokens/sec, and estimated USD cost using configurable rates. Confirm actual model pricing and usage metadata for the selected region/model. Do not use estimates as billing figures.

Suggested evaluation dimensions:
- Retrieval recall@k on a labelled question/document set.
- Citation precision: proportion of cited passages that support the answer.
- Groundedness / faithfulness: factual claims supported by retrieved evidence.
- Answer relevance and completeness, reviewed by human raters.
- Safety: prompt injection resistance, data leakage, and refusal correctness.
- Performance: p50/p95 latency, throughput, error rate, tokens/request, cost/request.

The included evaluation script uses keyword coverage only as a smoke-test proxy. It is not a substitute for a labelled evaluation set or human review.
