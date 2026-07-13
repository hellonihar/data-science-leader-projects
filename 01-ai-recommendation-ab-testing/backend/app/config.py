from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/recommendation_ab"
    redis_url: str = "redis://localhost:6379/0"
    model_registry_path: str = "../ml/model_registry"
    experiment_traffic_split_default: float = 0.5
    min_sample_size: int = 100
    confidence_level: float = 0.95

    class Config:
        env_file = ".env"


settings = Settings()
