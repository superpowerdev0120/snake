"""Pygame rendering for menus, the game board, and HUD."""

import pygame

from snake.config import Colors, GameConfig
from snake.game import Game, GamePhase
from snake.modes import GameMode


class Renderer:
    """Draws menus, the grid, snakes, food, and overlay text."""

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
        self._title_font = pygame.font.SysFont(None, 36)

    def draw_menu(self, selected: GameMode) -> None:
        self.screen.fill(self.colors.background)
        title = self._title_font.render("Snake", True, self.colors.text)
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 80))
        self.screen.blit(title, title_rect)

        subtitle = self._font.render("Select game mode", True, self.colors.text)
        subtitle_rect = subtitle.get_rect(center=(self.screen.get_width() // 2, 120))
        self.screen.blit(subtitle, subtitle_rect)

        options = [
            (GameMode.SOLO, "1 — 1 Player"),
            (GameMode.TWO_PLAYER, "2 — 2 Player"),
            (GameMode.VS_COM, "3 — Player vs Computer"),
        ]
        y = 170
        for mode, label in options:
            color = self.colors.menu_highlight if mode is selected else self.colors.text
            surface = self._font.render(label, True, color)
            rect = surface.get_rect(center=(self.screen.get_width() // 2, y))
            self.screen.blit(surface, rect)
            y += 36

        hint = self._font.render("Use Up/Down and Enter (or press 1/2/3)", True, self.colors.text)
        hint_rect = hint.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 40))
        self.screen.blit(hint, hint_rect)

    def draw(self, game: Game) -> None:
        self._draw_background()
        self._draw_grid()
        self._draw_food(game)
        self._draw_snakes(game)
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

    def _snake_colors(self, player_index: int) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        if player_index == 0:
            return self.colors.snake, self.colors.snake_head
        return self.colors.opponent_snake, self.colors.opponent_head

    def _draw_snakes(self, game: Game) -> None:
        for index, player in enumerate(game.players):
            if not player.alive:
                continue
            body_color, head_color = self._snake_colors(index)
            for segment_index, (x, y) in enumerate(player.snake.body):
                color = head_color if segment_index == 0 else body_color
                pygame.draw.rect(self.screen, color, self._cell_rect(x, y))

    def _draw_food(self, game: Game) -> None:
        x, y = game.food.position
        pygame.draw.rect(self.screen, self.colors.food, self._cell_rect(x, y))

    def _draw_hud(self, game: Game) -> None:
        if game.mode is GameMode.SOLO:
            score_text = self._font.render(f"Score: {game.score}", True, self.colors.text)
            self.screen.blit(score_text, (8, 8))
        else:
            scores = "  |  ".join(
                f"{player.name}: {player.score}" + ("" if player.alive else " (out)")
                for player in game.players
            )
            score_text = self._font.render(scores, True, self.colors.text)
            self.screen.blit(score_text, (8, 8))

        if game.state.phase is GamePhase.READY:
            self._draw_center_message(self._ready_message(game))
        elif game.state.phase is GamePhase.PAUSED:
            self._draw_center_message("Paused — press P to resume")
        elif game.state.phase is GamePhase.GAME_OVER:
            message = self._game_over_message(game)
            self._draw_center_message(message)

    def _ready_message(self, game: Game) -> str:
        if game.mode is GameMode.SOLO:
            return "Press an arrow key to start"
        if game.mode is GameMode.TWO_PLAYER:
            return "P1: Arrows  |  P2: WASD — press any move key to start"
        return "Arrows to move — press an arrow key to start"

    def _game_over_message(self, game: Game) -> str:
        if game.mode is GameMode.SOLO:
            return f"Game Over — Score: {game.score} — press R to restart"
        winner = game.state.winner or "Draw"
        return f"{winner} wins — press R to restart"

    def _draw_center_message(self, message: str) -> None:
        surface = self._font.render(message, True, self.colors.text)
        rect = surface.get_rect(
            center=(
                self.screen.get_width() // 2,
                self.screen.get_height() // 2,
            )
        )
        self.screen.blit(surface, rect)
