from backend.core.analysers.base import BaseAnalyser


class WordCountAnalyser(BaseAnalyser):
    name = "word_count"

    def analyse(self, text: str, **_) -> int:
        return len(text.split())
