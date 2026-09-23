import uvicorn

from backend.config import settings
from backend.utils.logger import configure_logging, get_logger

logger = get_logger(__name__)


def main() -> None:
    configure_logging()
    logger.info("Starting backend API server")
    uvicorn.run(
        "backend.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )
