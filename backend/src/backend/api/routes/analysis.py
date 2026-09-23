import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from backend.common.exceptions import AnalyserNotFoundError, AnalysisExecutionError
from backend.core.registry import create_default_registry
from backend.schema.analysis_schema import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisType,
)
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

_registry = create_default_registry()


@router.get("/analysers")
def list_analysers() -> dict[str, list[str]]:
    return {"available": _registry.available}


@router.post("/analyse", response_model=AnalysisResponse)
def analyse(
    request: AnalysisRequest,
    analyses: list[AnalysisType] = Query(...),  # noqa: B008
    include_spaces: bool = True,
) -> AnalysisResponse:
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    results: dict[str, Any] = {}
    for analysis in analyses:
        try:
            results[analysis.value] = _registry.run(
                analysis.value,
                request.text,
                params={"include_spaces": include_spaces},
            )
        except AnalyserNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except AnalysisExecutionError as exc:
            logger.exception("Analysis failed for request_id=%s", request_id)
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return AnalysisResponse(
        results=results,
        metadata={
            "request_id": request_id,
            "input_length": len(request.text),
            "processing_time_ms": round((time.perf_counter() - start) * 1000, 2),
        },
    )
