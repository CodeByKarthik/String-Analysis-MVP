from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AnalysisType(str, Enum):
    """
    Enumeration of available analysis types.

    Attributes:
        WORD_COUNT (str): Analysis type for counting words.
        CHARACTER_COUNT (str): Analysis type for counting characters.
        SENTENCE_COUNT (str): Analysis type for counting sentences.
    """

    WORD_COUNT = "word_count"
    CHARACTER_COUNT = "character_count"
    SENTENCE_COUNT = "sentence_count"


class AnalysisRequest(BaseModel):
    """
    Request model for text analysis.

    Attributes:
        text (str): The text to be analysed.
    """

    text: str = Field(..., min_length=1, max_length=100, description="Text to analyse")


class AnalysisResponse(BaseModel):
    """
    Response model for text analysis.

    Attributes:
        results (dict[str, Any]): The analysis results.
        metadata (dict[str, Any]): Metadata related to the analysis request.
    """

    results: dict[str, Any]
    metadata: dict[str, Any]
