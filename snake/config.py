"""Game configuration and constants."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GridConfig:
    cols: int = 20
    rows: int = 20
    cell_size: int = 24


@dataclass(frozen=True)
class GameConfig:
    grid: GridConfig = GridConfig()
    fps: int = 10
    title: str = "Snake"


@dataclass(frozen=True)
class Colors:
    background: tuple[int, int, int] = (18, 18, 18)
    grid: tuple[int, int, int] = (30, 30, 30)
    snake: tuple[int, int, int] = (76, 175, 80)
    snake_head: tuple[int, int, int] = (129, 199, 132)
    opponent_snake: tuple[int, int, int] = (66, 165, 245)
    opponent_head: tuple[int, int, int] = (100, 181, 246)
    food: tuple[int, int, int] = (244, 67, 54)
    text: tuple[int, int, int] = (240, 240, 240)
    menu_highlight: tuple[int, int, int] = (255, 193, 7)


DEFAULT_GAME_CONFIG = GameConfig()
DEFAULT_COLORS = Colors()
