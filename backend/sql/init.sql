CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS documents (
 id UUID PRIMARY KEY, filename TEXT NOT NULL, mime_type TEXT NOT NULL,
 storage_uri TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS chunks (
 id BIGSERIAL PRIMARY KEY, document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
 chunk_index INT NOT NULL, content TEXT NOT NULL, embedding vector(768), metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE TABLE IF NOT EXISTS business_metrics (
 id BIGSERIAL PRIMARY KEY, team TEXT NOT NULL, metric TEXT NOT NULL,
 metric_value DOUBLE PRECISION NOT NULL, period DATE NOT NULL
);
INSERT INTO business_metrics(team,metric,metric_value,period) VALUES
 ('Platform','tickets_resolved',128,'2026-10-01'),('Platform','tickets_resolved',143,'2026-11-01'),
 ('Customer Success','tickets_resolved',96,'2026-10-01'),('Customer Success','tickets_resolved',111,'2026-11-01')
ON CONFLICT DO NOTHING;
