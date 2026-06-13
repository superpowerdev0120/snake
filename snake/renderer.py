"""Pygame rendering for the game board and HUD."""

import pygame

from snake.config import Colors, GameConfig
from snake.game import Game, GamePhase


class Renderer:
    """Draws the grid, snake, food, and overlay text."""

    def __init__(
        self,
        screen: pygame.Surface,
        config: GameConfig,
        colors: Colors | None = None,
    ) -> None:
        self.screen = screen
        self.config = config
        self.colors = colors or Colors()
        self._font = pygame.font.SysFont(None, 24)

    def draw(self, game: Game) -> None:
        self._draw_background()
        self._draw_grid()
        self._draw_food(game)
        self._draw_snake(game)
        self._draw_hud(game)

    def _draw_background(self) -> None:
        self.screen.fill(self.colors.background)

    def _draw_grid(self) -> None:
        cell = self.config.grid.cell_size
        width = self.config.grid.cols * cell
        height = self.config.grid.rows * cell

        for x in range(0, width, cell):
            pygame.draw.line(self.screen, self.colors.grid, (x, 0), (x, height))
        for y in range(0, height, cell):
            pygame.draw.line(self.screen, self.colors.grid, (0, y), (width, y))

    def _cell_rect(self, x: int, y: int) -> pygame.Rect:
        cell = self.config.grid.cell_size
        return pygame.Rect(x * cell, y * cell, cell, cell)

    def _draw_snake(self, game: Game) -> None:
        for index, (x, y) in enumerate(game.snake.body):
            color = self.colors.snake_head if index == 0 else self.colors.snake
            pygame.draw.rect(self.screen, color, self._cell_rect(x, y))

    def _draw_food(self, game: Game) -> None:
        x, y = game.food.position
        pygame.draw.rect(self.screen, self.colors.food, self._cell_rect(x, y))

    def _draw_hud(self, game: Game) -> None:
        score_text = self._font.render(f"Score: {game.state.score}", True, self.colors.text)
        self.screen.blit(score_text, (8, 8))

        if game.state.phase is GamePhase.READY:
            self._draw_center_message("Press an arrow key to start")
        elif game.state.phase is GamePhase.PAUSED:
            self._draw_center_message("Paused")
        elif game.state.phase is GamePhase.GAME_OVER:
            self._draw_center_message("Game Over — press R to restart")

    def _draw_center_message(self, message: str) -> None:
        surface = self._font.render(message, True, self.colors.text)
        rect = surface.get_rect(
            center=(
                self.screen.get_width() // 2,
                self.screen.get_height() // 2,
            )
        )
        self.screen.blit(surface, rect)
