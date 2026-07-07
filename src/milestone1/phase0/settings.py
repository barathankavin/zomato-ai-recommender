from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from milestone1.phase0.paths import PROJECT_ROOT

class Settings(BaseSettings):
    groq_api_key: str = Field(default="", description="Groq API Key")
    groq_model: str = Field(default="llama-3.3-70b-versatile", description="Groq Model")
    hf_token: str = Field(default="", description="HuggingFace API Token (optional)")

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

def load_settings() -> Settings:
    return Settings()
