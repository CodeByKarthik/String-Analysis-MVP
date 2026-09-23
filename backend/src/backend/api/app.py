from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from backend.api.middleware import RequestResponseLoggingMiddleware
from backend.api.routes.analysis import router as analysis_router
from backend.api.routes.health import router as health_router
from backend.config import settings
from backend.utils.logger import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

app = FastAPI(title="String Analysis Backend", version=settings.app_version)
app.add_middleware(RequestResponseLoggingMiddleware)

Instrumentator().instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)

app.include_router(health_router)
app.include_router(analysis_router)

logger.info("FastAPI app initialized")
