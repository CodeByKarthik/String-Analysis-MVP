from typing import Any

from backend.common.exceptions import (
    AnalyserNotFoundError,
    AnalysisExecutionError,
    DuplicateAnalyserError,
)
from backend.core.analysers.base import BaseAnalyser
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class BaseAnalyserRegistry:
    """
    Registry for text analysers.
    Handles registration, lookup, and execution.
    """

    def __init__(self) -> None:
        self._analysers: dict[str, BaseAnalyser] = {}

    @property
    def available(self) -> list[str]:
        """Returns a list of registered analyser names."""
        return list(self._analysers.keys())

    def register(self, analyser: BaseAnalyser) -> None:
        """
        Registers a new analyser. Raises DuplicateAnalyserError
        if an analyser with the same name already exists.
        """
        if analyser.name in self._analysers:
            raise DuplicateAnalyserError(
                f"An analyser named '{analyser.name}' is already registered."
            )
        self._analysers[analyser.name] = analyser
        logger.info("Analyser registered: '%s'", analyser.name)

    def run(
        self,
        analyser_name: str,
        text: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """
        Runs a named analyser against the given text.
        Raises AnalyserNotFoundError if the analyser is not registered.
        Raises AnalysisExecutionError if the analyser itself fails.
        """
        analyser = self._get(analyser_name)
        logger.info("Running analyser: '%s'", analyser_name)
        try:
            return analyser.analyse(text, **(params or {}))
        except Exception as exc:
            raise AnalysisExecutionError(
                f"Analyser '{analyser_name}' failed: {exc}"
            ) from exc

    def _get(self, name: str) -> BaseAnalyser:
        if name not in self._analysers:
            available = ", ".join(self._analysers.keys())
            raise AnalyserNotFoundError(
                f"Analyser '{name}' not found. Available: [{available}]"
            )
        return self._analysers[name]
