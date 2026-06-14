"""Boxing-ring play area helpers."""

from snake.config import GridConfig


def apron_half(grid: GridConfig) -> float:
    return grid.ring.radius + 3.2


def is_in_ring(x: int, y: int, grid: GridConfig) -> bool:
    """True when the cell is inside the square ring canvas (playable area)."""
    if x < 0 or y < 0 or x >= grid.cols or y >= grid.rows:
        return False
    ring = grid.ring
    dx = abs(x - ring.center_col + 0.5)
    dy = abs(y - ring.center_row + 0.5)
    return dx <= ring.radius and dy <= ring.radius


def iter_ring_cells(grid: GridConfig) -> list[tuple[int, int]]:
    return [(x, y) for x in range(grid.cols) for y in range(grid.rows) if is_in_ring(x, y, grid)]
