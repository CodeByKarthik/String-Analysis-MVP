from fastapi import APIRouter

from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    logger.info("Health check requested")
    return {"status": "ok"}
