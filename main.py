"""Entry point for the Snake game."""

import sys

import pygame

from snake.config import DEFAULT_GAME_CONFIG
from snake.entities import Direction
from snake.game import Game, GamePhase
from snake.modes import GameMode
from snake.renderer import Renderer

P1_KEYS = {
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
}

P2_KEYS = {
    pygame.K_w: Direction.UP,
    pygame.K_s: Direction.DOWN,
    pygame.K_a: Direction.LEFT,
    pygame.K_d: Direction.RIGHT,
}

MODE_BY_KEY = {
    pygame.K_1: GameMode.SOLO,
    pygame.K_2: GameMode.TWO_PLAYER,
    pygame.K_3: GameMode.VS_COM,
}

MODE_ORDER = [GameMode.SOLO, GameMode.TWO_PLAYER, GameMode.VS_COM]


def run_menu(renderer: Renderer, clock: pygame.time.Clock, fps: int) -> GameMode | None:
    selected_index = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type != pygame.KEYDOWN:
                continue

            if event.key in MODE_BY_KEY:
                return MODE_BY_KEY[event.key]
            if event.key == pygame.K_UP:
                selected_index = (selected_index - 1) % len(MODE_ORDER)
            elif event.key == pygame.K_DOWN:
                selected_index = (selected_index + 1) % len(MODE_ORDER)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return MODE_ORDER[selected_index]

        renderer.draw_menu(MODE_ORDER[selected_index])
        pygame.display.flip()
        clock.tick(fps)


def run_game(mode: GameMode, screen: pygame.Surface, clock: pygame.time.Clock, fps: int) -> bool:
    """Run one match. Returns False when the app should quit."""
    config = DEFAULT_GAME_CONFIG
    game = Game(mode, config)
    renderer = Renderer(screen, config)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type != pygame.KEYDOWN:
                continue

            if event.key in P1_KEYS:
                game.handle_direction(0, P1_KEYS[event.key])
            elif event.key in P2_KEYS and mode is GameMode.TWO_PLAYER:
                game.handle_direction(1, P2_KEYS[event.key])
            elif event.key == pygame.K_p:
                if game.state.phase is GamePhase.RUNNING:
                    game.pause()
                elif game.state.phase is GamePhase.PAUSED:
                    game.resume()
            elif event.key == pygame.K_r and game.state.phase is GamePhase.GAME_OVER:
                game.restart()
            elif event.key == pygame.K_ESCAPE:
                return True

        game.update()
        renderer.draw(game)
        pygame.display.flip()
        clock.tick(fps)

    return True


def run() -> None:
    config = DEFAULT_GAME_CONFIG

    try:
        pygame.init()
        try:
            pygame.mixer.init(frequency=22050, size=-8, channels=1, buffer=512)
        except pygame.error:
            pass
        screen = pygame.display.set_mode((config.screen_width, config.screen_height))
    except pygame.error as exc:
        print(f"Unable to start display: {exc}")
        print("Run this game on a machine with a graphical desktop session.")
        sys.exit(1)

    pygame.display.set_caption(config.title)
    clock = pygame.time.Clock()

    renderer = Renderer(screen, config)

    while True:
        mode = run_menu(renderer, clock, config.fps)
        if mode is None:
            break

        continue_to_menu = run_game(mode, screen, clock, config.fps)
        if not continue_to_menu:
            break

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    run()
