from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "GenAI Chatbot Experimentation Hub"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot_experiments"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    GROQ_API_KEY: str = ""
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_MODEL_BASELINE: str = "llama3-70b-8192"
    GROQ_MODEL_FINETUNED: str = "llama3-70b-8192"
    GROQ_MAX_TOKENS: int = 1024
    GROQ_TEMPERATURE: float = 0.7
    GROQ_TIMEOUT_SECONDS: int = 60

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    RAG_TOP_K: int = 5
    RAG_CHUNK_SIZE: int = 512
    RAG_CHUNK_OVERLAP: int = 64

    HALLUCINATION_ENTAILMENT_THRESHOLD: float = 0.9
    HALLUCINATION_CONTRADICTION_TOLERANCE: float = 0.0
    HALLUCINATION_MODEL: str = "cross-encoder/nli-deberta-v3-base"
    HALLUCINATION_SCORE_ENABLED: bool = True

    STATS_CHISQ_ALPHA: float = 0.05
    STATS_TTEST_ALPHA: float = 0.05

    FEEDBACK_RESOLUTION_THRESHOLD: int = 4

    EXPERIMENT_DEFAULT_TRAFFIC_SPLIT: float = 0.5
    ASSIGNMENT_SALT: str = "experiment-v1-salt"

    SEED_DOCUMENTS_DIR: str = "seed_data/documents/"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
