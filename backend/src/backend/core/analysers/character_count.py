from backend.core.analysers.base import BaseAnalyser


class CharacterCountAnalyser(BaseAnalyser):
    name = "character_count"

    def analyse(self, text: str, include_spaces: bool = True, **_) -> int:
        return len(text) if include_spaces else len(text.replace(" ", ""))
