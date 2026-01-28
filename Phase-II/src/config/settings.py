from pydantic_settings import BaseSettings
from typing import List, Optional
from urllib.parse import urlparse


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # Database settings
    NEON_DB_URL: str

    # Authentication settings
    BETTER_AUTH_SECRET: str
    BETTER_AUTH_URL: str = "http://localhost:8000"
    JWT_EXPIRATION_HOURS: int = 24

    # Application settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # CORS settings
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    # Redis settings (for token blacklisting)
    REDIS_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert the allowed origins string to a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        """Check if the environment is development."""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if the environment is production."""
        return self.ENVIRONMENT.lower() == "production"


# Create a single instance of settings
settings = Settings()


def get_settings() -> Settings:
    """
    Get the application settings instance.

    Returns:
        Settings: The application settings instance
    """
    return settings