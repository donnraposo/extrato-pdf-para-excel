from ...domain.entities import PhysicalLine, Word


class WordLineGrouper:
    def __init__(self, tolerance: float = 3.0) -> None:
        self._tolerance = tolerance

    def group(self, words: list[Word]) -> list[PhysicalLine]:
        lines: list[PhysicalLine] = []
        for word in sorted(words, key=lambda item: (item.page, item.top, item.x0)):
            target = next(
                (line for line in reversed(lines) if line.page == word.page and abs(line.top - word.top) <= self._tolerance),
                None,
            )
            if target is None:
                lines.append(PhysicalLine([word], word.page, word.top))
            else:
                target.words.append(word)
                target.top = sum(item.top for item in target.words) / len(target.words)
        for line in lines:
            line.words.sort(key=lambda item: item.x0)
        return lines
