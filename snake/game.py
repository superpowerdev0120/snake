"""Game engine: state, rules, and the main update loop."""

from dataclasses import dataclass
from enum import Enum, auto

from snake.config import GameConfig
from snake.entities import Direction, Food, Snake


class GamePhase(Enum):
    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


@dataclass
class GameState:
    score: int = 0
    phase: GamePhase = GamePhase.READY


class Game:
    """Coordinates snake, food, scoring, and win/lose rules."""

    def __init__(self, config: GameConfig | None = None) -> None:
        self.config = config or GameConfig()
        self.state = GameState()
        self.snake = Snake(self.config.grid)
        self.food = Food(self.config.grid)
        self._reset_entities()

    def _reset_entities(self) -> None:
        self.snake = Snake(self.config.grid)
        self.food = Food(self.config.grid)
        self.food.respawn(set(self.snake.body))

    def start(self) -> None:
        self.state = GameState(phase=GamePhase.RUNNING)

    def pause(self) -> None:
        if self.state.phase is GamePhase.RUNNING:
            self.state.phase = GamePhase.PAUSED

    def resume(self) -> None:
        if self.state.phase is GamePhase.PAUSED:
            self.state.phase = GamePhase.RUNNING

    def restart(self) -> None:
        self._reset_entities()
        self.state = GameState(phase=GamePhase.RUNNING)

    def handle_direction(self, direction: Direction) -> None:
        if self.state.phase is GamePhase.READY:
            self.start()
        if self.state.phase is not GamePhase.RUNNING:
            return
        self.snake.set_direction(direction)

    def update(self) -> None:
        if self.state.phase is not GamePhase.RUNNING:
            return

        self.snake.move()

        if self._is_out_of_bounds(self.snake.head) or self.snake.collides_with_self():
            self.state.phase = GamePhase.GAME_OVER
            return

        if self.snake.head == self.food.position:
            self.snake.schedule_growth()
            self.state.score += 1
            self.food.respawn(set(self.snake.body))

    def _is_out_of_bounds(self, cell: tuple[int, int]) -> bool:
        x, y = cell
        grid = self.config.grid
        return x < 0 or y < 0 or x >= grid.cols or y >= grid.rows
