"""Food entity: spawn and respawn on the grid."""

import random

from snake.config import GridConfig
from snake.ring import iter_ring_cells


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
        free_cells = [cell for cell in iter_ring_cells(self._grid) if cell not in blocked]
        if not free_cells:
            raise RuntimeError("No free cells available for food")
        self._position = random.choice(free_cells)
