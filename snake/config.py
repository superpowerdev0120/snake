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
class CartoonPalette:
    head: tuple[int, int, int]
    body: tuple[int, int, int]
    belly: tuple[int, int, int]
    tail: tuple[int, int, int]
    tail_tip: tuple[int, int, int]
    outline: tuple[int, int, int]
    shine: tuple[int, int, int]
    eye_white: tuple[int, int, int]
    pupil: tuple[int, int, int]
    food: tuple[int, int, int]
    food_shine: tuple[int, int, int]
    food_stem: tuple[int, int, int]
    food_leaf: tuple[int, int, int]


@dataclass(frozen=True)
class Colors:
    background: tuple[int, int, int] = (28, 48, 38)
    grid: tuple[int, int, int] = (36, 58, 46)
    snake: tuple[int, int, int] = (88, 196, 102)
    snake_head: tuple[int, int, int] = (118, 220, 128)
    opponent_snake: tuple[int, int, int] = (82, 168, 255)
    opponent_head: tuple[int, int, int] = (130, 196, 255)
    food: tuple[int, int, int] = (255, 92, 92)
    text: tuple[int, int, int] = (248, 244, 230)
    menu_highlight: tuple[int, int, int] = (255, 214, 96)
    outline: tuple[int, int, int] = (24, 36, 28)
    belly: tuple[int, int, int] = (196, 236, 176)
    eye_white: tuple[int, int, int] = (255, 255, 255)
    pupil: tuple[int, int, int] = (30, 30, 40)
    shine: tuple[int, int, int] = (220, 255, 210)
    tail: tuple[int, int, int] = (62, 150, 78)
    tail_tip: tuple[int, int, int] = (48, 120, 62)
    opponent_belly: tuple[int, int, int] = (196, 228, 255)
    opponent_tail: tuple[int, int, int] = (58, 130, 220)
    opponent_tail_tip: tuple[int, int, int] = (42, 98, 180)
    food_shine: tuple[int, int, int] = (255, 210, 210)
    food_stem: tuple[int, int, int] = (92, 58, 36)
    food_leaf: tuple[int, int, int] = (88, 180, 72)

    def player_palette(self, player_index: int) -> CartoonPalette:
        if player_index == 0:
            return CartoonPalette(
                head=self.snake_head,
                body=self.snake,
                belly=self.belly,
                tail=self.tail,
                tail_tip=self.tail_tip,
                outline=self.outline,
                shine=self.shine,
                eye_white=self.eye_white,
                pupil=self.pupil,
                food=self.food,
                food_shine=self.food_shine,
                food_stem=self.food_stem,
                food_leaf=self.food_leaf,
            )
        return CartoonPalette(
            head=self.opponent_head,
            body=self.opponent_snake,
            belly=self.opponent_belly,
            tail=self.opponent_tail,
            tail_tip=self.opponent_tail_tip,
            outline=self.outline,
            shine=(210, 236, 255),
            eye_white=self.eye_white,
            pupil=self.pupil,
            food=self.food,
            food_shine=self.food_shine,
            food_stem=self.food_stem,
            food_leaf=self.food_leaf,
        )

    def food_palette(self) -> CartoonPalette:
        return self.player_palette(0)


DEFAULT_GAME_CONFIG = GameConfig()
DEFAULT_COLORS = Colors()
