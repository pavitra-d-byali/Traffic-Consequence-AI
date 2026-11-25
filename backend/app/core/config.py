from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    database_url: str = f"sqlite:///{(Path(__file__).resolve().parents[2] / 'traffic_consequence.db').as_posix()}"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    classifier_model: str = ""
    enable_huggingface: bool = False
    enable_sentence_transformers: bool = False
    frontend_origins: str = "http://localhost:5173"
    hotspot_radius_km: float = 1.0
    hotspot_min_reports: int = 2
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [x.strip() for x in self.frontend_origins.split(",") if x.strip()]

settings = Settings()
