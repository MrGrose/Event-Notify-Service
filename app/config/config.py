from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    llm_timeout_seconds: float = 10.0
    ollama_temperature: float = 0.1
    ollama_num_predict: int = 60

    path_event: str = "data/events.json"


settings = Settings()
