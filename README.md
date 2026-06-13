# Snake

A classic Snake game built with Python and Pygame.

## Project structure

```
snake/
├── main.py                 # Entry point — event loop and wiring
├── requirements.txt
└── snake/
    ├── config.py           # Grid size, FPS, colors
    ├── game.py             # Game rules, state, scoring
    ├── renderer.py         # Pygame drawing (grid, snake, food, HUD)
    └── entities/
        ├── snake.py        # Snake movement, growth, self-collision
        └── food.py         # Food spawn / respawn
```

## Architecture

| Layer | Module | Responsibility |
|-------|--------|----------------|
| **Entry** | `main.py` | Pygame init, input mapping, main loop |
| **Config** | `config.py` | Tunable constants (grid, speed, colors) |
| **Engine** | `game.py` | Game phases, score, collision rules, updates |
| **Entities** | `entities/` | Snake and Food behavior |
| **View** | `renderer.py` | All drawing; no game logic |

Data flows in one direction each frame:

```
Input → Game.handle_direction() / pause / restart
Game.update() → state changes
Renderer.draw(game) → screen
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| Arrow keys | Move / start |
| P | Pause / resume |
| R | Restart after game over |

## Next steps

- Add high-score persistence (`storage/` module)
- Add unit tests for `Snake`, `Food`, and `Game` logic
- Add sound effects and menu screen
