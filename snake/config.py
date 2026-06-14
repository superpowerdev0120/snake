"""Game configuration and constants."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RingConfig:
    center_col: int = 15
    center_row: int = 15
    radius: float = 12.0


@dataclass(frozen=True)
class GridConfig:
    cols: int = 30
    rows: int = 30
    cell_size: int = 24
    ring: RingConfig = field(default_factory=RingConfig)


@dataclass(frozen=True)
class GameConfig:
    grid: GridConfig = field(default_factory=GridConfig)
    screen_width: int = 960
    screen_height: int = 720
    fps: int = 7
    title: str = "Snake 3D - Boxing Ring"


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
    background_top: tuple[int, int, int] = (8, 10, 18)
    background_bottom: tuple[int, int, int] = (18, 14, 24)
    arena_glow: tuple[int, int, int] = (42, 36, 58)
    seat_row: tuple[int, int, int] = (24, 22, 32)
    text: tuple[int, int, int] = (236, 238, 244)
    text_dim: tuple[int, int, int] = (148, 152, 168)
    menu_highlight: tuple[int, int, int] = (220, 186, 96)
    hud_panel: tuple[int, int, int, int] = (12, 14, 22, 215)
    hud_border: tuple[int, int, int] = (90, 96, 118)
    snake: tuple[int, int, int] = (46, 158, 82)
    snake_head: tuple[int, int, int] = (62, 196, 102)
    opponent_snake: tuple[int, int, int] = (48, 118, 210)
    opponent_head: tuple[int, int, int] = (78, 156, 232)
    food: tuple[int, int, int] = (208, 52, 48)
    outline: tuple[int, int, int] = (16, 24, 20)
    belly: tuple[int, int, int] = (168, 220, 176)
    eye_white: tuple[int, int, int] = (248, 248, 252)
    pupil: tuple[int, int, int] = (24, 28, 36)
    shine: tuple[int, int, int] = (190, 240, 200)
    tail: tuple[int, int, int] = (34, 118, 62)
    tail_tip: tuple[int, int, int] = (26, 92, 50)
    opponent_belly: tuple[int, int, int] = (168, 204, 238)
    opponent_tail: tuple[int, int, int] = (34, 92, 168)
    opponent_tail_tip: tuple[int, int, int] = (24, 72, 132)
    food_shine: tuple[int, int, int] = (255, 196, 188)
    food_stem: tuple[int, int, int] = (72, 48, 28)
    food_leaf: tuple[int, int, int] = (56, 132, 52)
    ring_skirt: tuple[int, int, int] = (28, 28, 34)
    ring_skirt_dark: tuple[int, int, int] = (14, 14, 18)
    ring_apron: tuple[int, int, int] = (228, 228, 234)
    ring_apron_shadow: tuple[int, int, int] = (176, 178, 188)
    ring_outline: tuple[int, int, int] = (96, 98, 108)
    ring_canvas_center: tuple[int, int, int] = (214, 216, 222)
    ring_canvas_edge: tuple[int, int, int] = (196, 200, 208)
    ring_canvas_line: tuple[int, int, int] = (148, 152, 162)
    ring_canvas_worn: tuple[int, int, int] = (186, 190, 198)
    ring_play_line: tuple[int, int, int] = (170, 176, 188)
    ring_floor: tuple[int, int, int] = (16, 18, 24)
    ring_rope_bottom: tuple[int, int, int] = (168, 28, 38)
    ring_rope_middle: tuple[int, int, int] = (228, 232, 238)
    ring_rope_top: tuple[int, int, int] = (36, 58, 132)
    ring_post: tuple[int, int, int] = (168, 172, 182)
    ring_post_shine: tuple[int, int, int] = (220, 224, 232)
    ring_pad: tuple[int, int, int] = (168, 28, 36)
    ring_pad_dark: tuple[int, int, int] = (108, 16, 22)
    ring_rope: tuple[int, int, int] = (176, 24, 34)
    ring_rope_shadow: tuple[int, int, int] = (88, 12, 18)
    ring_rope_highlight: tuple[int, int, int] = (228, 96, 102)
    ring_rope_tape: tuple[int, int, int] = (236, 236, 242)

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
            shine=(188, 218, 248),
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
