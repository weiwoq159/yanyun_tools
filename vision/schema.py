from dataclasses import dataclass


@dataclass(slots=True)
class TemplateMatchResult:
    name: str
    found: bool
    score: float
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def center(self) -> tuple[int, int]:
        return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2
