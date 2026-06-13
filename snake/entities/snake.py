"""Snake entity: movement, growth, and collision with itself."""

from enum import Enum, auto

from snake.config import GridConfig


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    @property
    def delta(self) -> tuple[int, int]:
        deltas = {
            Direction.UP: (0, -1),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
            Direction.RIGHT: (1, 0),
        }
        return deltas[self]

    def is_opposite(self, other: "Direction") -> bool:
        return (
            (self is Direction.UP and other is Direction.DOWN)
            or (self is Direction.DOWN and other is Direction.UP)
            or (self is Direction.LEFT and other is Direction.RIGHT)
            or (self is Direction.RIGHT and other is Direction.LEFT)
        )


class Snake:
    """A snake on the grid, represented as an ordered list of cell positions."""

    def __init__(
        self,
        grid: GridConfig,
        start: tuple[int, int] | None = None,
        direction: Direction = Direction.RIGHT,
    ) -> None:
        center = (grid.cols // 2, grid.rows // 2)
        origin = start or center
        self._body: list[tuple[int, int]] = [origin]
        self._direction = direction
        self._grow_pending = 0

    @property
    def body(self) -> list[tuple[int, int]]:
        return list(self._body)

    @property
    def head(self) -> tuple[int, int]:
        return self._body[0]

    @property
    def direction(self) -> Direction:
        return self._direction

    def set_direction(self, direction: Direction) -> None:
        if direction.is_opposite(self._direction):
            return
        self._direction = direction

    def schedule_growth(self, segments: int = 1) -> None:
        self._grow_pending += segments

    def move(self) -> None:
        dx, dy = self._direction.delta
        head_x, head_y = self.head
        new_head = (head_x + dx, head_y + dy)
        self._body.insert(0, new_head)

        if self._grow_pending > 0:
            self._grow_pending -= 1
        else:
            self._body.pop()

    def collides_with_self(self) -> bool:
        return self.head in self._body[1:]
