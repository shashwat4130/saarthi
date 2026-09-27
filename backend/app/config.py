from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SAARTHI"
    DATABASE_PATH: str = "data/saarthi.db"
    POLICIES_PATH: str = "policies.json"
    AUDIT_HMAC_SECRET: str = "saarthi-hackathon-secure-secret-key-2026"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()