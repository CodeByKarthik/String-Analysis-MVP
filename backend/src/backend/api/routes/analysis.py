import time
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from prometheus_client import Counter

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

analysis_requests_total = Counter(
    "analysis_requests_total",
    "Total number of analysis requests processed",
    labelnames=("status",),
)

_registry = create_default_registry()


@router.get("/analysers")
def list_analysers() -> dict[str, list[str]]:
    return {"available": _registry.available}


@router.post("/analyse", response_model=AnalysisResponse)
def analyse(
    request: Request,
    payload: AnalysisRequest,
    analyses: list[AnalysisType] = Query(...),  # noqa: B008
    include_spaces: bool = True,
) -> AnalysisResponse:
    request_id = request.state.request_id
    start = time.perf_counter()

    results: dict[str, Any] = {}
    for analysis in analyses:
        try:
            results[analysis.value] = _registry.run(
                analysis.value,
                payload.text,
                params={"include_spaces": include_spaces},
            )
        except AnalyserNotFoundError as exc:
            analysis_requests_total.labels(status="error").inc()
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        except AnalysisExecutionError as exc:
            analysis_requests_total.labels(status="error").inc()
            logger.exception("Analysis failed for request_id=%s", request_id)
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    analysis_requests_total.labels(status="success").inc()

    return AnalysisResponse(
        results=results,
        metadata={
            "request_id": request_id,
            "input_length": len(payload.text),
            "processing_time_ms": round((time.perf_counter() - start) * 1000, 2),
        },
    )
