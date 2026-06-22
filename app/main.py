from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI

from app.config import get_settings
from app.db import Base, engine
from app.providers.fixtures import FixtureListingProvider

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    from app import models as app_models

    _ = app_models
    Path("var").mkdir(exist_ok=True)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_title, lifespan=lifespan)


@app.get("/")
def read_root() -> dict[str, object]:
    provider = FixtureListingProvider(settings.fixture_html_path)
    fixture_exists = Path(settings.fixture_html_path).exists()
    sample_count = len(provider.fetch()) if fixture_exists else 0
    return {
        "name": settings.app_title,
        "status": "scaffolded",
        "supported_cities": ["Sofia", "Plovdiv", "Varna", "Burgas"],
        "provider": settings.listing_provider,
        "fixture_sample_count": sample_count,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
