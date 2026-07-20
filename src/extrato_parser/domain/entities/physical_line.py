from dataclasses import dataclass

from .word import Word


@dataclass
class PhysicalLine:
    words: list[Word]
    page: int
    top: float

    @property
    def text(self) -> str:
        return " ".join(word.text for word in sorted(self.words, key=lambda item: item.x0))
