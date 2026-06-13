"""Simple AI for computer-controlled snakes."""

import random

from snake.config import GridConfig
from snake.entities import Direction, Snake


def _is_safe(
    head: tuple[int, int],
    direction: Direction,
    snake: Snake,
    blocked: set[tuple[int, int]],
    grid: GridConfig,
) -> bool:
    dx, dy = direction.delta
    x, y = head[0] + dx, head[1] + dy
    if x < 0 or y < 0 or x >= grid.cols or y >= grid.rows:
        return False
    if (x, y) in snake.body:
        return False
    if (x, y) in blocked:
        return False
    return True


def choose_direction(
    snake: Snake,
    food_position: tuple[int, int],
    blocked: set[tuple[int, int]],
    grid: GridConfig,
) -> Direction:
    """Pick a direction toward food, falling back to any safe move."""
    head = snake.head
    food_x, food_y = food_position
    candidates = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]

    safe_moves = [
        direction
        for direction in candidates
        if not direction.is_opposite(snake.direction)
        and _is_safe(head, direction, snake, blocked, grid)
    ]
    if not safe_moves:
        return snake.direction

    def distance(direction: Direction) -> int:
        dx, dy = direction.delta
        x, y = head[0] + dx, head[1] + dy
        return abs(x - food_x) + abs(y - food_y)

    best_distance = min(distance(direction) for direction in safe_moves)
    best_moves = [direction for direction in safe_moves if distance(direction) == best_distance]
    return random.choice(best_moves)
