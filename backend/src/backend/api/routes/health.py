from fastapi import APIRouter

from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """
    Perform a health check for the API.

    Returns:
        dict[str, str]: A dictionary containing the health status.
    """
    logger.info("Health check requested")
    return {"status": "ok"}
