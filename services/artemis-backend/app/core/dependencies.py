"""Global FastAPI dependencies for dependency injection."""

from typing import Annotated

from fastapi import Depends
from supabase import Client

from app.core.config import Settings, get_settings
from app.core.database import get_supabase_client

# Type alias for settings dependency
SettingsDep = Annotated[Settings, Depends(get_settings)]

# Type alias for database dependency
DatabaseDep = Annotated[Client | None, Depends(get_supabase_client)]


def get_settings_dep() -> Settings:
    """Dependency to get application settings."""
    return get_settings()


def get_db() -> Client | None:
    """Dependency to get Supabase client."""
    return get_supabase_client()
