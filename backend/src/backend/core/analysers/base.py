from abc import ABC, abstractmethod
from typing import Any


class BaseAnalyser(ABC):
    """Abstract base for all text analysers."""

    name: str

    @abstractmethod
    def analyse(self, text: str, **params: Any) -> Any:
        """Run the analysis on the given text."""
        ...
