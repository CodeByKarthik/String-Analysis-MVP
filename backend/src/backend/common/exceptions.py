class AnalyserError(Exception):
    """Base exception for analyser errors."""


class DuplicateAnalyserError(AnalyserError):
    """Raised when registering an analyser name that already exists."""


class AnalyserNotFoundError(AnalyserError):
    """Raised when an unknown analyser is requested."""


class AnalysisExecutionError(AnalyserError):
    """Raised when an analyser fails during execution."""
