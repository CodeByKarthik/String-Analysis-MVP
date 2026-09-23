from nltk.tokenize import sent_tokenize  # type: ignore[import-untyped]

from backend.core.analysers.base import BaseAnalyser


class SentenceCountAnalyser(BaseAnalyser):
    name = "sentence_count"

    def analyse(self, text: str, **_) -> int:
        if not text.strip():
            return 0

        return len(sent_tokenize(text))
