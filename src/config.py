import os
from functools import lru_cache


class Settings:
    @property
    @lru_cache()
    def app_name(self) -> str:
        return os.getenv("APP_NAME", "Blacklist API")
    
    @property
    @lru_cache()
    def db_url(self) -> str:
        rds_host = os.getenv("RDS_HOSTNAME")
        rds_user = os.getenv("RDS_USERNAME")
        rds_pass = os.getenv("RDS_PASSWORD")
        rds_db   = os.getenv("RDS_DB_NAME")
        rds_port = os.getenv("RDS_PORT", "5432")
        return f"postgresql+asyncpg://{rds_user}:{rds_pass}@{rds_host}:{rds_port}/{rds_db}"
    
    @property
    @lru_cache()
    def db_echo(self) -> bool:
        return os.getenv("DB_ECHO", "False").lower() == "true"
    
    @property
    @lru_cache()
    def auth_token(self) -> str:
        return os.getenv("AUTH_TOKEN", "bearer-token-static-2024")


settings = Settings()