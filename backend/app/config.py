from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "local"
    app_api_key: str = "change-me"
    llm_provider: str = "mock"
    embedding_provider: str = "mock"
    google_cloud_project: str = ""
    google_cloud_location: str = "us-central1"
    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "text-embedding-005"
    database_url: str = "postgresql://fieldlens:fieldlens@localhost:5432/fieldlens"
    db_password: str = ""
    gcs_bucket: str = ""
    max_upload_mb: int = 10
    allowed_origins: str = "http://localhost:3000"
    input_usd_per_1m_tokens: float = 0.30
    output_usd_per_1m_tokens: float = 2.50
    otel_exporter_otlp_endpoint: str = ""
settings = Settings()
