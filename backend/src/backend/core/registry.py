from backend.core.analysers.base import BaseAnalyser
from backend.core.analysers.character_count import CharacterCountAnalyser
from backend.core.analysers.sentence_count import SentenceCountAnalyser
from backend.core.analysers.word_count import WordCountAnalyser
from backend.core.base_registry import BaseAnalyserRegistry

# ------ REGISTRY FACTORY ------
#
# Steps to add a new analyser:
# 1. Create a new class in app/analysers/ that inherits from BaseAnalyser.
# 2. Set the `name` attribute and implement `analyse()`.
# 3. Add the class to the _DEFAULT_ANALYSERS list below.
# 4. Add the name to the AnalysisType enum in app/schemas.py.

_DEFAULT_ANALYSERS: list[type[BaseAnalyser]] = [
    WordCountAnalyser,
    CharacterCountAnalyser,
    SentenceCountAnalyser,
    # --- Add new analysers above ---
]


def create_default_registry(
    analysers: list[type[BaseAnalyser]] | None = None,
) -> BaseAnalyserRegistry:
    """
    Creates a registry pre-populated with the default analysers.

    Parameters
    ----------
    analysers : optional list of analyser classes to register.
                Defaults to all built-in analysers.
    """
    registry = BaseAnalyserRegistry()

    for analyser_cls in analysers or _DEFAULT_ANALYSERS:
        registry.register(analyser_cls())

    return registry
