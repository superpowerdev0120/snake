"""Cartoon-style drawing for snakes and food."""

from __future__ import annotations

import math

import pygame

from snake.config import CartoonPalette
from snake.entities import Direction


def _cell_center(cell_size: int, x: int, y: int) -> tuple[int, int]:
    return (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2)


def _lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def _darken(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return (
        _lerp(color[0], 0, factor),
        _lerp(color[1], 0, factor),
        _lerp(color[2], 0, factor),
    )


def _segment_radius(cell_size: int, index: int, total: int) -> int:
    base = cell_size // 2 - 3
    if total == 1:
        return base + 2
    if index == 0:
        return base + 2
    if index == total - 1:
        return max(5, base - 5)
    progress = index / (total - 1)
    return max(base - 1, int(base - progress * 2))


def _draw_circle(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    fill: tuple[int, int, int],
    outline: tuple[int, int, int] | None = None,
    outline_width: int = 2,
) -> None:
    if outline and outline_width > 0:
        pygame.draw.circle(surface, outline, center, radius + outline_width)
    pygame.draw.circle(surface, fill, center, radius)


def _draw_shine(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int],
) -> None:
    shine_center = (center[0] - radius // 3, center[1] - radius // 3)
    shine_radius = max(2, radius // 4)
    pygame.draw.circle(surface, color, shine_center, shine_radius)


def _eye_offset(direction: Direction, radius: int) -> tuple[tuple[int, int], tuple[int, int]]:
    spacing = max(3, radius // 3)
    forward = max(2, radius // 3)
    if direction is Direction.UP:
        return ((-spacing, -forward), (spacing, -forward))
    if direction is Direction.DOWN:
        return ((-spacing, forward), (spacing, forward))
    if direction is Direction.LEFT:
        return ((-forward, -spacing), (-forward, spacing))
    return ((forward, -spacing), (forward, spacing))


def _draw_head(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    direction: Direction,
    palette: CartoonPalette,
) -> None:
    _draw_circle(surface, center, radius, palette.head, palette.outline)

    belly_rect = pygame.Rect(
        center[0] - radius // 2,
        center[1] - radius // 4,
        radius,
        radius // 2 + 2,
    )
    pygame.draw.ellipse(surface, palette.belly, belly_rect)

    for offset in _eye_offset(direction, radius):
        eye_center = (center[0] + offset[0], center[1] + offset[1])
        eye_radius = max(3, radius // 4)
        pygame.draw.circle(surface, palette.outline, eye_center, eye_radius + 1)
        pygame.draw.circle(surface, palette.eye_white, eye_center, eye_radius)
        pupil = (eye_center[0] + offset[0] // 3, eye_center[1] + offset[1] // 3)
        pygame.draw.circle(surface, palette.pupil, pupil, max(2, eye_radius // 2))

    _draw_shine(surface, center, radius, palette.shine)


def _draw_body_segment(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    palette: CartoonPalette,
    segment_index: int,
) -> None:
    shade = _darken(palette.body, 0.08 * (segment_index % 2))
    _draw_circle(surface, center, radius, shade, palette.outline, outline_width=1)
    belly_rect = pygame.Rect(
        center[0] - radius // 2,
        center[1],
        radius,
        radius // 2,
    )
    pygame.draw.ellipse(surface, palette.belly, belly_rect)
    if segment_index % 2 == 0:
        _draw_shine(surface, center, radius, palette.shine)


def _draw_tail(
    surface: pygame.Surface,
    center: tuple[int, int],
    previous: tuple[int, int] | None,
    radius: int,
    palette: CartoonPalette,
) -> None:
    _draw_circle(surface, center, radius, palette.tail, palette.outline, outline_width=1)

    if previous is None:
        return

    dx = center[0] - previous[0]
    dy = center[1] - previous[1]
    length = math.hypot(dx, dy) or 1
    tip = (
        int(center[0] + dx / length * radius * 0.9),
        int(center[1] + dy / length * radius * 0.9),
    )
    pygame.draw.circle(surface, palette.tail_tip, tip, max(3, radius // 2))


def _draw_connector(
    surface: pygame.Surface,
    start: tuple[int, int],
    end: tuple[int, int],
    start_radius: int,
    end_radius: int,
    color: tuple[int, int, int],
    outline: tuple[int, int, int],
) -> None:
    width = max(4, start_radius + end_radius - 2)
    pygame.draw.line(surface, outline, start, end, width + 2)
    pygame.draw.line(surface, color, start, end, width)


def draw_cartoon_snake(
    surface: pygame.Surface,
    body: list[tuple[int, int]],
    direction: Direction,
    palette: CartoonPalette,
    cell_size: int,
) -> None:
    if not body:
        return

    points = [_cell_center(cell_size, x, y) for x, y in body]
    total = len(points)
    radii = [_segment_radius(cell_size, index, total) for index in range(total)]

    for index in range(total - 1, 0, -1):
        _draw_connector(
            surface,
            points[index],
            points[index - 1],
            radii[index],
            radii[index - 1],
            palette.body,
            palette.outline,
        )

    if total == 1:
        _draw_head(surface, points[0], radii[0], direction, palette)
        return

    previous_point = points[-2] if total > 1 else None
    _draw_tail(surface, points[-1], previous_point, radii[-1], palette)

    for index in range(total - 2, 0, -1):
        _draw_body_segment(surface, points[index], radii[index], palette, index)

    _draw_head(surface, points[0], radii[0], direction, palette)


def draw_cartoon_food(
    surface: pygame.Surface,
    position: tuple[int, int],
    palette: CartoonPalette,
    cell_size: int,
) -> None:
    center = _cell_center(cell_size, *position)
    radius = cell_size // 2 - 4

    pygame.draw.circle(surface, palette.outline, center, radius + 2)
    pygame.draw.circle(surface, palette.food, center, radius)
    _draw_shine(surface, center, radius, palette.food_shine)

    stem_top = (center[0], center[1] - radius)
    stem_tip = (center[0] + 2, center[1] - radius - 5)
    pygame.draw.line(surface, palette.food_stem, stem_top, stem_tip, 3)
    leaf_center = (center[0] + 5, center[1] - radius - 4)
    pygame.draw.ellipse(surface, palette.food_leaf, pygame.Rect(leaf_center[0], leaf_center[1], 8, 5))
