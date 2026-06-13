"""Food entity: spawn and respawn on the grid."""

import random

from snake.config import GridConfig


class Food:
    """A single food item at a grid cell."""

    def __init__(self, grid: GridConfig) -> None:
        self._grid = grid
        self._position: tuple[int, int] = (0, 0)
        self.respawn()

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    def respawn(self, occupied: set[tuple[int, int]] | None = None) -> None:
        blocked = occupied or set()
        free_cells = [
            (x, y)
            for x in range(self._grid.cols)
            for y in range(self._grid.rows)
            if (x, y) not in blocked
        ]
        if not free_cells:
            raise RuntimeError("No free cells available for food")
        self._position = random.choice(free_cells)
