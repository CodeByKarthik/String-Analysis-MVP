import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query
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
    """
    List all available analysers in the registry.

    Returns:
        dict[str, list[str]]: A dictionary containing
        the list of available analysers.
    """
    return {"available": _registry.available}


@router.post("/analyse", response_model=AnalysisResponse)
def analyse(
    request: AnalysisRequest,
    analyses: list[AnalysisType] = Query(...),  # noqa: B008
    include_spaces: bool = True,
) -> AnalysisResponse:
    """
    Analyse the given text using the specified analysis types.

    Args:
        - request (AnalysisRequest): The analysis request containing
        the text to be analysed.
        - analyses (list[AnalysisType]): A list of analysis
        types to perform.
        - include_spaces (bool, optional): Whether to include
        spaces in the analysis. Defaults to True.

    Returns:
        AnalysisResponse: The response containing the analysis results and metadata.
    """
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
            "input_length": len(request.text),
            "processing_time_ms": round((time.perf_counter() - start) * 1000, 2),
        },
    )
