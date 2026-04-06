from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Model settings
    model_name: str = "distilgpt2"
    default_max_new_tokens: int = 50
    default_temperature: float = 0.0

    # Batching settings
    max_batch_size: int = 8
    batch_timeout_ms: float = 50.0
    max_sequence_length: int = 256

    # Caching settings
    cache_ttl_seconds: int = 3600
    cache_max_entries: int = 100
    enable_cache: bool = True

    # Server settings
    host: str = "127.0.0.1"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
