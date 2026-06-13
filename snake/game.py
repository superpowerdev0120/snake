"""Game engine: state, rules, and the main update loop."""

from dataclasses import dataclass
from enum import Enum, auto

from snake.ai import choose_direction
from snake.config import GameConfig, GridConfig
from snake.entities import Direction, Food, Snake
from snake.modes import GameMode


class GamePhase(Enum):
    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


@dataclass
class Player:
    snake: Snake
    name: str
    score: int = 0
    alive: bool = True
    is_ai: bool = False


@dataclass
class GameState:
    phase: str = GamePhase.READY
    winner: str | None = None


class Game:
    """Coordinates snakes, food, scoring, and win/lose rules."""

    def __init__(self, mode: GameMode, config: GameConfig | None = None) -> None:
        self.mode = mode
        self.config = config or GameConfig()
        self.state = GameState()
        self.players: list[Player] = []
        self.food = Food(self.config.grid)
        self._reset_entities()

    def _reset_entities(self) -> None:
        grid = self.config.grid
        self.players = self._create_players(grid)
        self.food = Food(grid)
        self.food.respawn(self._occupied_cells())

    def _create_players(self, grid: GridConfig) -> list[Player]:
        mid_y = grid.rows // 2

        if self.mode is GameMode.SOLO:
            return [
                Player(
                    snake=Snake(grid, start=(grid.cols // 2, mid_y), direction=Direction.RIGHT),
                    name="Player",
                )
            ]

        if self.mode is GameMode.TWO_PLAYER:
            return [
                Player(
                    snake=Snake(grid, start=(5, mid_y), direction=Direction.RIGHT),
                    name="Player 1",
                ),
                Player(
                    snake=Snake(grid, start=(grid.cols - 6, mid_y), direction=Direction.LEFT),
                    name="Player 2",
                ),
            ]

        return [
            Player(
                snake=Snake(grid, start=(5, mid_y), direction=Direction.RIGHT),
                name="You",
            ),
            Player(
                snake=Snake(grid, start=(grid.cols - 6, mid_y), direction=Direction.LEFT),
                name="Computer",
                is_ai=True,
            ),
        ]

    def _occupied_cells(self) -> set[tuple[int, int]]:
        occupied: set[tuple[int, int]] = set()
        for player in self.players:
            occupied.update(player.snake.body)
        return occupied

    def _alive_players(self) -> list[Player]:
        return [player for player in self.players if player.alive]

    def start(self) -> None:
        self.state.phase = GamePhase.RUNNING
        self.state.winner = None

    def pause(self) -> None:
        if self.state.phase is GamePhase.RUNNING:
            self.state.phase = GamePhase.PAUSED

    def resume(self) -> None:
        if self.state.phase is GamePhase.PAUSED:
            self.state.phase = GamePhase.RUNNING

    def restart(self) -> None:
        self._reset_entities()
        self.state = GameState(phase=GamePhase.RUNNING)

    def handle_direction(self, player_index: int, direction: Direction) -> None:
        if self.state.phase is GamePhase.READY:
            self.start()
        if self.state.phase is not GamePhase.RUNNING:
            return
        if player_index < 0 or player_index >= len(self.players):
            return
        player = self.players[player_index]
        if player.alive and not player.is_ai:
            player.snake.set_direction(direction)

    def update(self) -> None:
        if self.state.phase is not GamePhase.RUNNING:
            return

        self._update_ai_directions()

        for player in self._alive_players():
            player.snake.move()

        self._resolve_collisions()
        self._resolve_food()
        self._check_game_over()

    def _update_ai_directions(self) -> None:
        for player in self.players:
            if not player.alive or not player.is_ai:
                continue
            blocked = self._occupied_cells() - set(player.snake.body)
            direction = choose_direction(
                player.snake,
                self.food.position,
                blocked,
                self.config.grid,
            )
            player.snake.set_direction(direction)

    def _resolve_collisions(self) -> None:
        for player in self.players:
            if not player.alive:
                continue

            head = player.snake.head
            if self._is_out_of_bounds(head) or player.snake.collides_with_self():
                player.alive = False
                continue

            for other in self.players:
                if other is player or not other.alive:
                    continue
                if head in other.snake.body:
                    player.alive = False
                    break

    def _resolve_food(self) -> None:
        eaters = [
            player for player in self._alive_players() if player.snake.head == self.food.position
        ]
        if not eaters:
            return

        for player in eaters:
            player.snake.schedule_growth()
            player.score += 1
        self.food.respawn(self._occupied_cells())

    def _check_game_over(self) -> None:
        alive = self._alive_players()

        if self.mode is GameMode.SOLO:
            if not alive:
                self.state.phase = GamePhase.GAME_OVER
                self.state.winner = None
            return

        if len(alive) == 1:
            self.state.phase = GamePhase.GAME_OVER
            self.state.winner = alive[0].name
            return

        if not alive:
            self.state.phase = GamePhase.GAME_OVER
            self.state.winner = self._determine_winner()

    def _determine_winner(self) -> str:
        scores = sorted(self.players, key=lambda player: player.score, reverse=True)
        top_score = scores[0].score
        leaders = [player for player in scores if player.score == top_score]

        if len(leaders) == 1:
            return leaders[0].name
        return "Draw"

    def _is_out_of_bounds(self, cell: tuple[int, int]) -> bool:
        x, y = cell
        grid = self.config.grid
        return x < 0 or y < 0 or x >= grid.cols or y >= grid.rows

    @property
    def score(self) -> int:
        """Primary score for solo mode HUD compatibility."""
        return self.players[0].score if self.players else 0
