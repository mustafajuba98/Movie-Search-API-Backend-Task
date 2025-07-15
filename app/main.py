from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.endpoints import movies
from app.core.exceptions import ServiceUnavailable


# cash imports 
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

from contextlib import asynccontextmanager



# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    Initializes the cache on startup and closes it on shutdown.
    """
    # Initialize cache
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    print("FastAPI Cache initialized with In-memory backend.")
    yield
    # yield top separates startup from shutdown logic 
    print("Closing FastAPI Cache.")
    FastAPICache.reset()

app = FastAPI(
    title="Movie Search API",
    description="An API to search for movies using multiple external providers. Made with love and FastAPI.",
    version="1.0.0",
    lifespan=lifespan # -- << --
)

@app.exception_handler(ServiceUnavailable)
async def service_unavailable_exception_handler(request: Request, exc: ServiceUnavailable):
    return JSONResponse(
        status_code=503,
        content={
            "message": f"The external service '{exc.service_name}' is currently unavailable.",
            "original_status_code": exc.status_code,
            "original_detail": exc.detail
        },
    )

@app.get("/", tags=["Root"])
async def read_root():
    """A welcome message for the API."""
    return {"message": "Welcome to the Movie Search API! Navigate to /docs for API documentation."}


app.include_router(movies.router, prefix="/movies", tags=["Movies"])