"""Entry point for the Snake game."""

import sys

import pygame

from snake.config import DEFAULT_GAME_CONFIG
from snake.entities import Direction
from snake.game import Game, GamePhase
from snake.renderer import Renderer

KEY_TO_DIRECTION = {
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
}


def run() -> None:
    config = DEFAULT_GAME_CONFIG
    grid = config.grid

    pygame.init()
    screen = pygame.display.set_mode((grid.cols * grid.cell_size, grid.rows * grid.cell_size))
    pygame.display.set_caption(config.title)
    clock = pygame.time.Clock()

    game = Game(config)
    renderer = Renderer(screen, config)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in KEY_TO_DIRECTION:
                    game.handle_direction(KEY_TO_DIRECTION[event.key])
                elif event.key == pygame.K_p:
                    if game.state.phase is GamePhase.RUNNING:
                        game.pause()
                    elif game.state.phase is GamePhase.PAUSED:
                        game.resume()
                elif event.key == pygame.K_r and game.state.phase is GamePhase.GAME_OVER:
                    game.restart()

        game.update()
        renderer.draw(game)
        pygame.display.flip()
        clock.tick(config.fps)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    run()
