from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AnalysisType(str, Enum):
    WORD_COUNT = "word_count"
    CHARACTER_COUNT = "character_count"
    SENTENCE_COUNT = "sentence_count"


class AnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=100, description="Text to analyse")


class AnalysisResponse(BaseModel):
    results: dict[str, Any]
    metadata: dict[str, Any]
