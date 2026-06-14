"""Polished 3D boxing-ring renderer."""

from __future__ import annotations

import math

import pygame

from snake.config import CartoonPalette, Colors, GameConfig, GridConfig
from snake.effects import EffectManager
from snake.entities import Direction
from snake.game import Game, GamePhase
from snake.modes import GameMode
from snake.ring import apron_half
from snake.visual import (
    create_canvas_texture,
    darken,
    draw_canvas_lighting,
    draw_rope_line,
    draw_rounded_panel,
    draw_shadow,
    draw_sphere,
    draw_turnbuckle_pad,
    draw_vertical_gradient,
    draw_vignette,
    lighten,
)


class RingCamera:
    """Flat top-down camera — equal width and height scale, no perspective tilt."""

    def __init__(self, screen_width: int, screen_height: int, grid: GridConfig) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        ring_half = apron_half(grid)
        ring_size = ring_half * 2
        self.ppu = min(
            (screen_width * 0.82) / ring_size,
            (screen_height * 0.62) / ring_size,
        )
        self.cx = screen_width // 2
        self.cy = int(screen_height * 0.54)
        self.scale = self.ppu

    def project(self, wx: float, wy: float, wz: float) -> tuple[float, float, float]:
        sx = self.cx + wx * self.ppu
        sy = self.cy + wz * self.ppu
        return sx, sy, self.scale

    def entity_radius(self, scale: float, factor: float = 1.0) -> int:
        return max(5, int(scale * 0.36 * factor))


class Ring3DRenderer:
    """Draws snakes and food on a cinematic boxing ring."""

    def __init__(self, screen: pygame.Surface, config: GameConfig, colors: Colors | None = None) -> None:
        self.screen = screen
        self.config = config
        self.colors = colors or Colors()
        self.camera = RingCamera(config.screen_width, config.screen_height, config.grid)
        self._font = pygame.font.SysFont("dejavusans", 22)
        self._title_font = pygame.font.SysFont("dejavusans", 42, bold=True)
        self._small_font = pygame.font.SysFont("dejavusans", 16)
        self._label_font = pygame.font.SysFont("dejavusans", 13)
        self._banner_font = pygame.font.SysFont("dejavusans", 54, bold=True)
        self._pop_font = pygame.font.SysFont("dejavusans", 24, bold=True)
        self._cell_scale = 1.0
        self._canvas_texture = create_canvas_texture()
        self._effects = EffectManager()
        self._scene_surface = self._build_scene_surface()

    def draw_menu(self, selected: GameMode) -> None:
        self.screen.blit(self._scene_surface, (0, 0))
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((6, 8, 14, 150))
        self.screen.blit(overlay, (0, 0))

        cx = self.config.screen_width // 2
        shadow = self._title_font.render("SNAKE 3D", True, (0, 0, 0))
        title = self._title_font.render("SNAKE 3D", True, self.colors.menu_highlight)
        self.screen.blit(shadow, shadow.get_rect(center=(cx + 2, 72)))
        self.screen.blit(title, title.get_rect(center=(cx, 70)))

        subtitle = self._font.render("Professional Boxing Ring Arena", True, self.colors.text_dim)
        self.screen.blit(subtitle, subtitle.get_rect(center=(cx, 112)))

        options = [
            (GameMode.SOLO, "1   Solo Bout"),
            (GameMode.TWO_PLAYER, "2   Tag Team (2 Players)"),
            (GameMode.VS_COM, "3   Vs Computer"),
        ]
        y = 170
        for mode, label in options:
            active = mode is selected
            panel_w, panel_h = 420, 34
            panel = pygame.Rect(cx - panel_w // 2, y - panel_h // 2, panel_w, panel_h)
            if active:
                draw_rounded_panel(
                    self.screen,
                    panel,
                    (24, 28, 42, 210),
                    self.colors.menu_highlight,
                    8,
                )
            color = self.colors.menu_highlight if active else self.colors.text_dim
            prefix = "> " if active else "   "
            surface = self._font.render(prefix + label, True, color)
            self.screen.blit(surface, surface.get_rect(center=(cx, y)))
            y += 42

        hint = self._small_font.render("Arrow keys + Enter   |   Press 1 / 2 / 3", True, self.colors.text_dim)
        self.screen.blit(hint, hint.get_rect(center=(cx, self.config.screen_height - 28)))

    def draw(self, game: Game) -> None:
        self._handle_events(game)
        self._effects.update()
        self.screen.blit(self._scene_surface, (0, 0))
        self._draw_food(game)
        self._draw_snakes(game)
        self._draw_hud(game)
        self._effects.draw(self.screen, self._banner_font, self._pop_font)

    def _handle_events(self, game: Game) -> None:
        ring = game.config.grid.ring
        for event in game.consume_events():
            if event.kind == "start":
                sx, sy = self._cell_center_screen(ring.center_col + 0.5, ring.center_row + 0.5, game.config.grid)
                self._effects.trigger_start(sx, sy)
            elif event.kind == "eat" and event.cell is not None:
                sx, sy = self._cell_center_screen(event.cell[0] + 0.5, event.cell[1] + 0.5, game.config.grid)
                self._effects.trigger_eat(sx, sy)

    def _cell_center_screen(self, gx: float, gy: float, grid: GridConfig) -> tuple[float, float]:
        sx, sy, _ = self._project(*self._grid_to_world(gx, gy, grid, 0.0))
        return sx, sy

    def _grid_to_world(self, gx: float, gy: float, grid: GridConfig, lift: float = 0.0) -> tuple[float, float, float]:
        ring = grid.ring
        wx = (gx - ring.center_col) * self._cell_scale
        wz = (gy - ring.center_row) * self._cell_scale
        return wx, lift, wz

    def _project(self, wx: float, wy: float, wz: float) -> tuple[float, float, float]:
        return self.camera.project(wx, wy, wz)

    def _build_scene_surface(self) -> pygame.Surface:
        surface = pygame.Surface((self.config.screen_width, self.config.screen_height))
        draw_vertical_gradient(surface, self.colors.background_top, self.colors.background_bottom)
        self._draw_arena(surface)
        self._draw_venue_floor(surface)
        self._draw_ring_platform(surface)
        self._draw_canvas(surface)
        self._draw_posts_and_ropes(surface)
        draw_vignette(surface, strength=0.38)
        return surface

    def _apron_half(self) -> float:
        return apron_half(self.config.grid)

    def _canvas_half(self) -> float:
        return self.config.grid.ring.radius + 0.15

    def _rope_half(self) -> float:
        return self.config.grid.ring.radius + 0.55

    def _draw_arena(self, surface: pygame.Surface) -> None:
        width = self.config.screen_width
        height = self.config.screen_height

        glow = pygame.Surface((width, height // 2), pygame.SRCALPHA)
        for y in range(glow.get_height()):
            alpha = int(28 * (1 - y / max(glow.get_height() - 1, 1)))
            color = (*self.colors.arena_glow, alpha)
            pygame.draw.line(glow, color, (0, y), (width, y))
        surface.blit(glow, (0, 0))

        for tier in range(7):
            y = 28 + tier * 32
            inset = tier * 18
            tone = darken(self.colors.seat_row, tier * 0.05)
            pygame.draw.rect(surface, tone, pygame.Rect(inset, y, width - inset * 2, 22))
            pygame.draw.line(surface, lighten(tone, 0.08), (inset, y), (width - inset, y), 1)
            pygame.draw.line(surface, darken(tone, 0.2), (inset, y + 21), (width - inset, y + 21), 1)

        for x in range(60, width, 140):
            light = pygame.Surface((100, 36), pygame.SRCALPHA)
            pygame.draw.ellipse(light, (255, 244, 220, 14), light.get_rect())
            surface.blit(light, (x - 50, 12))

    def _draw_venue_floor(self, surface: pygame.Surface) -> None:
        half = self._apron_half() + 1.4
        floor_points, _, _ = self._square_points(half)
        glow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        expanded = [
            (x + (x - self.camera.cx) * 0.04, y + (y - self.camera.cy) * 0.04)
            for x, y in floor_points
        ]
        pygame.draw.polygon(glow, (*self.colors.ring_floor, 180), expanded)
        pygame.draw.polygon(surface, self.colors.ring_floor, floor_points)
        pygame.draw.polygon(surface, darken(self.colors.ring_floor, 0.12), floor_points, 1)

    def _ring_corners(self, half_size: float) -> list[tuple[float, float, float]]:
        return [
            (-half_size, 0.0, -half_size),
            (half_size, 0.0, -half_size),
            (half_size, 0.0, half_size),
            (-half_size, 0.0, half_size),
        ]

    def _draw_ring_platform(self, surface: pygame.Surface) -> None:
        half = self._apron_half()
        outer, _, _ = self._square_points(half)
        apron, _, _ = self._square_points(half - 0.28)

        pygame.draw.polygon(surface, self.colors.ring_skirt, outer)
        pygame.draw.polygon(surface, self.colors.ring_apron, apron)
        pygame.draw.polygon(surface, self.colors.ring_outline, apron, 2)

        canvas_edge, _, _ = self._square_points(self._canvas_half())
        pygame.draw.polygon(surface, darken(self.colors.ring_apron, 0.1), canvas_edge, 2)

    def _square_points(self, half_size: float) -> tuple[list[tuple[int, int]], float, float]:
        corners = self._ring_corners(half_size)
        points = [(int(x), int(y)) for x, y, _ in (self._project(c[0], 0.0, c[2]) for c in corners)]
        center_sx = sum(p[0] for p in points) / 4
        center_sy = sum(p[1] for p in points) / 4
        return points, center_sx, center_sy

    def _circle_points(self, grid: GridConfig, radius_scale: float = 1.0) -> tuple[list[tuple[int, int]], float, float]:
        ring = grid.ring
        steps = 80
        points: list[tuple[int, int]] = []
        center_sx = 0.0
        center_sy = 0.0
        for i in range(steps):
            angle = (i / steps) * math.tau
            gx = ring.center_col + math.cos(angle) * ring.radius * radius_scale
            gy = ring.center_row + math.sin(angle) * ring.radius * radius_scale
            sx, sy, _ = self._project(*self._grid_to_world(gx, gy, grid, 0.0))
            points.append((int(sx), int(sy)))
            center_sx += sx
            center_sy += sy
        return points, center_sx / steps, center_sy / steps

    def _draw_canvas(self, surface: pygame.Surface) -> None:
        grid = self.config.grid
        canvas_points, center_sx, center_sy = self._square_points(self._canvas_half())
        if len(canvas_points) < 3:
            return

        canvas_layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(canvas_layer, (*self.colors.ring_canvas_edge, 255), canvas_points)

        min_x = min(p[0] for p in canvas_points)
        max_x = max(p[0] for p in canvas_points)
        min_y = min(p[1] for p in canvas_points)
        max_y = max(p[1] for p in canvas_points)
        canvas_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

        tex_size = max(canvas_rect.width, canvas_rect.height)
        texture = pygame.transform.smoothscale(self._canvas_texture, (tex_size, tex_size))
        tex_rect = texture.get_rect(center=(int(center_sx), int(center_sy)))
        canvas_layer.blit(texture, tex_rect)
        draw_canvas_lighting(
            canvas_layer,
            canvas_rect,
            lighten(self.colors.ring_canvas_center, 0.06),
            darken(self.colors.ring_canvas_edge, 0.08),
        )

        play_square, _, _ = self._square_points(self.config.grid.ring.radius)
        pygame.draw.polygon(canvas_layer, (*self.colors.ring_play_line, 140), play_square, 2)

        inner_square, _, _ = self._square_points(self._canvas_half() * 0.72)
        pygame.draw.polygon(canvas_layer, (*self.colors.ring_canvas_line, 90), inner_square, 1)

        center = (int(center_sx), int(center_sy))
        outer_r = max(8, int(min(canvas_rect.width, canvas_rect.height) * 0.16))
        inner_r = max(4, outer_r // 3)
        pygame.draw.circle(canvas_layer, (*self.colors.ring_canvas_line, 160), center, outer_r, 1)
        pygame.draw.circle(canvas_layer, (*self.colors.ring_canvas_line, 110), center, inner_r, 1)
        pygame.draw.line(
            canvas_layer,
            (*self.colors.ring_canvas_worn, 80),
            (center[0] - outer_r, center[1]),
            (center[0] + outer_r, center[1]),
            1,
        )
        pygame.draw.line(
            canvas_layer,
            (*self.colors.ring_canvas_worn, 80),
            (center[0], center[1] - outer_r),
            (center[0], center[1] + outer_r),
            1,
        )

        corner_colors = [
            self.colors.ring_pad,
            self.colors.ring_rope_top,
            self.colors.ring_pad,
            self.colors.ring_rope_top,
        ]
        for point, color in zip(canvas_points, corner_colors):
            pygame.draw.circle(canvas_layer, (*darken(color, 0.15), 100), point, 5)
            pygame.draw.circle(canvas_layer, (*color, 140), point, 3)

        surface.blit(canvas_layer, (0, 0))

    def _draw_posts_and_ropes(self, surface: pygame.Surface) -> None:
        rope_specs = (
            (0.00, self.colors.ring_rope_bottom, 5),
            (0.14, self.colors.ring_rope_middle, 4),
            (0.28, self.colors.ring_rope_bottom, 4),
            (0.42, self.colors.ring_rope_top, 4),
        )

        for inset, color, width in rope_specs:
            self._draw_rope_square(surface, self._rope_half() - inset, color, width)

        corners, _, _ = self._square_points(self._rope_half())
        corner_colors = [
            self.colors.ring_pad,
            self.colors.ring_rope_top,
            self.colors.ring_pad,
            self.colors.ring_rope_top,
        ]
        for point, pad_color in zip(corners, corner_colors):
            draw_turnbuckle_pad(surface, point, pad_color, darken(pad_color, 0.35), radius=8)

    def _draw_rope_square(
        self,
        surface: pygame.Surface,
        half_size: float,
        color: tuple[int, int, int],
        width: int,
    ) -> None:
        points, _, _ = self._square_points(half_size)
        shadow = darken(color, 0.45)
        highlight = lighten(color, 0.22)
        for i in range(4):
            j = (i + 1) % 4
            draw_rope_line(surface, points[i], points[j], color, shadow, highlight, width)
            if color == self.colors.ring_rope_middle:
                mid = ((points[i][0] + points[j][0]) // 2, (points[i][1] + points[j][1]) // 2)
                tape_w = max(10, int(math.hypot(points[j][0] - points[i][0], points[j][1] - points[i][1]) * 0.07))
                tape_rect = pygame.Rect(0, 0, tape_w, 3)
                tape_rect.center = mid
                pygame.draw.rect(surface, self.colors.ring_rope_tape, tape_rect, border_radius=1)

    def _draw_snakes(self, game: Game) -> None:
        segments: list[tuple[float, int, tuple[float, float, float], int, CartoonPalette, Direction | None, bool]] = []

        for player_index, player in enumerate(game.players):
            if not player.alive:
                continue
            palette = self.colors.player_palette(player_index)
            body = player.snake.body
            total = len(body)
            for index, (gx, gy) in enumerate(body):
                world = self._grid_to_world(gx + 0.5, gy + 0.5, game.config.grid, 0.0)
                _, _, scale = self._project(*world)
                segments.append((world[2], world[0], index, world, total, palette, player.snake.direction if index == 0 else None, index == 0))

        segments.sort(key=lambda item: (item[0], item[1], item[2]))

        for _, _, index, world, total, palette, direction, is_head in segments:
            self._draw_segment(world, index, total, palette, direction, is_head)

    def _draw_segment(
        self,
        world: tuple[float, float, float],
        index: int,
        total: int,
        palette: CartoonPalette,
        direction: Direction | None,
        is_head: bool,
    ) -> None:
        sx, sy, scale = self._project(*world)
        radius = self.camera.entity_radius(scale, 1.0 if is_head else 0.9)
        if index == total - 1 and total > 1:
            radius = max(4, radius - 1)

        color = palette.head if is_head else palette.tail if index == total - 1 and total > 1 else palette.body
        center = (int(sx), int(sy))
        draw_shadow(self.screen, center, radius, alpha=48)
        draw_sphere(self.screen, center, radius, color, palette.outline)

        if is_head and direction is not None:
            self._draw_head_eyes(center[0], center[1], radius, direction, palette)

    def _draw_head_eyes(
        self,
        sx: int,
        sy: int,
        radius: int,
        direction: Direction,
        palette: CartoonPalette,
    ) -> None:
        spacing = max(2, radius // 3)
        forward = max(2, radius // 3)
        if direction is Direction.UP:
            offsets = [(-spacing, -forward), (spacing, -forward)]
        elif direction is Direction.DOWN:
            offsets = [(spacing, forward), (-spacing, forward)]
        elif direction is Direction.LEFT:
            offsets = [(-forward, -spacing), (-forward, spacing)]
        else:
            offsets = [(forward, -spacing), (forward, spacing)]

        for ox, oy in offsets:
            ex, ey = sx + ox, sy + oy
            eye_r = max(2, radius // 4)
            pygame.draw.circle(self.screen, palette.outline, (ex, ey), eye_r + 1)
            pygame.draw.circle(self.screen, palette.eye_white, (ex, ey), eye_r)
            pygame.draw.circle(self.screen, palette.pupil, (ex + ox // 3, ey + oy // 3), max(1, eye_r // 2))

    def _draw_food(self, game: Game) -> None:
        palette = self.colors.food_palette()
        gx, gy = game.food.position
        wx, wy, wz = self._grid_to_world(gx + 0.5, gy + 0.5, game.config.grid, 0.0)
        sx, sy, scale = self._project(wx, wy, wz)
        radius = self.camera.entity_radius(scale, 0.78)
        center = (int(sx), int(sy))

        draw_shadow(self.screen, center, radius, alpha=44)
        draw_sphere(self.screen, center, radius, palette.food, darken(palette.food, 0.5))
        shine = (center[0] - radius // 3, center[1] - radius // 3)
        pygame.draw.circle(self.screen, palette.food_shine, shine, max(2, radius // 4))

        stem_top = (center[0], center[1] - radius)
        stem_tip = (center[0], center[1] - radius - 5)
        pygame.draw.line(self.screen, palette.food_stem, stem_top, stem_tip, 2)
        pygame.draw.ellipse(self.screen, palette.food_leaf, pygame.Rect(center[0] + 2, center[1] - radius - 6, 7, 4))

    def _draw_hud(self, game: Game) -> None:
        panel_rect = pygame.Rect(14, 12, 290, 62)
        draw_rounded_panel(self.screen, panel_rect, self.colors.hud_panel, self.colors.hud_border, 10)

        if game.mode is GameMode.SOLO:
            score = self._font.render(f"Score  {game.score}", True, self.colors.text)
            self.screen.blit(score, (28, 20))
        else:
            scores = "    ".join(
                f"{player.name}: {player.score}" + ("" if player.alive else "  KO")
                for player in game.players
            )
            score = self._small_font.render(scores, True, self.colors.text)
            self.screen.blit(score, (28, 20))

        label = self._label_font.render("BOXING RING  •  CHAMPIONSHIP", True, self.colors.text_dim)
        self.screen.blit(label, (28, 46))

        if game.state.phase is GamePhase.READY:
            self._draw_center_message(self._ready_message(game))
        elif game.state.phase is GamePhase.PAUSED:
            self._draw_center_message("PAUSED  —  Press P to resume")
        elif game.state.phase is GamePhase.GAME_OVER:
            self._draw_center_message(self._game_over_message(game))

    def _ready_message(self, game: Game) -> str:
        if game.mode is GameMode.SOLO:
            return "Press arrow keys to enter the ring"
        if game.mode is GameMode.TWO_PLAYER:
            return "P1: Arrows   •   P2: WASD"
        return "Arrows to move"

    def _game_over_message(self, game: Game) -> str:
        if game.mode is GameMode.SOLO:
            return f"Knocked Out  —  Score {game.score}  —  Press R"
        winner = game.state.winner or "Draw"
        return f"{winner} Wins  —  Press R"

    def _draw_center_message(self, message: str) -> None:
        surface = self._font.render(message, True, self.colors.text)
        rect = surface.get_rect(center=(self.config.screen_width // 2, self.config.screen_height // 2 - 20))
        panel = pygame.Rect(rect.x - 28, rect.y - 16, rect.width + 56, rect.height + 32)
        draw_rounded_panel(self.screen, panel, (10, 12, 20, 225), self.colors.hud_border, 12)
        self.screen.blit(surface, rect)
