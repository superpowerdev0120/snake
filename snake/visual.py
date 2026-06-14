"""Shared visual helpers for polished 2.5D rendering."""

from __future__ import annotations

import random

import pygame


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))


def darken(color: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return lerp_color(color, (0, 0, 0), amount)


def lighten(color: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return lerp_color(color, (255, 255, 255), amount)


def draw_vertical_gradient(
    surface: pygame.Surface,
    top: tuple[int, int, int],
    bottom: tuple[int, int, int],
) -> None:
    width, height = surface.get_size()
    for y in range(height):
        t = y / max(height - 1, 1)
        pygame.draw.line(surface, lerp_color(top, bottom, t), (0, y), (width, y))


def draw_radial_disc(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    inner: tuple[int, int, int],
    outer: tuple[int, int, int],
) -> None:
    if radius <= 0:
        return
    for r in range(radius, 0, -1):
        t = r / radius
        color = lerp_color(inner, outer, t)
        pygame.draw.circle(surface, color, center, r)


def draw_sphere(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    base: tuple[int, int, int],
    outline: tuple[int, int, int] | None = None,
) -> None:
    if radius <= 1:
        return
    cx, cy = center
    draw_radial_disc(surface, center, radius, lighten(base, 0.28), darken(base, 0.38))
    if outline:
        pygame.draw.circle(surface, outline, center, radius + 1, 1)
    highlight = (cx - max(1, radius // 3), cy - max(1, radius // 3))
    pygame.draw.circle(surface, lighten(base, 0.48), highlight, max(2, radius // 3))


def draw_shadow(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    alpha: int = 55,
) -> None:
    shadow = pygame.Surface((radius * 4, radius * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, alpha), shadow.get_rect())
    rect = shadow.get_rect(center=(center[0], center[1] + radius // 2 + 1))
    surface.blit(shadow, rect)


def draw_rounded_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fill: tuple[int, int, int, int],
    border: tuple[int, int, int] | None = None,
    radius: int = 10,
) -> None:
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, fill, panel.get_rect(), border_radius=radius)
    if border:
        pygame.draw.rect(panel, (*border, 160), panel.get_rect(), width=1, border_radius=radius)
    surface.blit(panel, rect.topleft)


def draw_vignette(surface: pygame.Surface, strength: float = 0.55) -> None:
    width, height = surface.get_size()
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    cx, cy = width // 2, height // 2
    max_dist = (width * width + height * height) ** 0.5 * 0.5
    step = 6
    for y in range(0, height, step):
        for x in range(0, width, step):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            alpha = int(min(255, (dist / max_dist) * 255 * strength))
            if alpha > 0:
                pygame.draw.rect(overlay, (0, 0, 0, alpha), pygame.Rect(x, y, step, step))
    surface.blit(overlay, (0, 0))


def create_canvas_texture(size: int = 64) -> pygame.Surface:
    texture = pygame.Surface((size, size), pygame.SRCALPHA)
    rng = random.Random(11)
    base = (228, 230, 236)
    texture.fill((*base, 255))
    for y in range(size):
        for x in range(size):
            noise = rng.randint(-8, 8)
            color = (
                max(0, min(255, base[0] + noise)),
                max(0, min(255, base[1] + noise)),
                max(0, min(255, base[2] + noise)),
                255,
            )
            if (x + y) % 3 == 0:
                texture.set_at((x, y), color)
    for y in range(0, size, 3):
        alpha = 8 + (y % 6) * 2
        pygame.draw.line(texture, (180, 186, 198, alpha), (0, y), (size, y))
    return texture


def draw_canvas_lighting(
    surface: pygame.Surface,
    rect: pygame.Rect,
    bright: tuple[int, int, int],
    dark: tuple[int, int, int],
) -> None:
    if rect.width <= 0 or rect.height <= 0:
        return
    layer = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        t = y / max(rect.height - 1, 1)
        row = lerp_color(bright, dark, t * 0.55)
        pygame.draw.line(layer, (*row, 28), (0, y), (rect.width, y))
    for x in range(rect.width):
        t = x / max(rect.width - 1, 1)
        col = lerp_color(bright, dark, (1 - t) * 0.35)
        pygame.draw.line(layer, (*col, 16), (x, 0), (x, rect.height))
    surface.blit(layer, rect.topleft)


def draw_rope_line(
    surface: pygame.Surface,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int],
    shadow: tuple[int, int, int],
    highlight: tuple[int, int, int],
    width: int = 5,
) -> None:
    pygame.draw.line(surface, shadow, (start[0], start[1] + 1), (end[0], end[1] + 1), width + 2)
    pygame.draw.line(surface, color, start, end, width)
    mid = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2 - 1)
    pygame.draw.circle(surface, highlight, mid, max(2, width // 2))


def draw_sagged_rope(
    surface: pygame.Surface,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int],
    shadow: tuple[int, int, int],
    highlight: tuple[int, int, int],
    width: int = 5,
    sag: float = 4.0,
    segments: int = 10,
) -> None:
    points: list[tuple[int, int]] = []
    for i in range(segments + 1):
        t = i / segments
        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t + sag * 4 * t * (1 - t)
        points.append((int(x), int(y)))
    for i in range(len(points) - 1):
        draw_rope_line(surface, points[i], points[i + 1], color, shadow, highlight, width)


def draw_turnbuckle_pad(
    surface: pygame.Surface,
    center: tuple[int, int],
    base: tuple[int, int, int],
    dark: tuple[int, int, int],
    radius: int = 10,
) -> None:
    cx, cy = center
    draw_shadow(surface, center, radius, alpha=40)
    pygame.draw.circle(surface, dark, (cx + 1, cy + 2), radius + 1)
    draw_radial_disc(surface, center, radius, lighten(base, 0.12), darken(base, 0.35))
    pygame.draw.circle(surface, lighten(base, 0.25), (cx - 3, cy - 3), max(2, radius // 3))
    pygame.draw.arc(surface, darken(base, 0.2), pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2), 0.8, 2.4, 2)


def draw_metallic_post(
    surface: pygame.Surface,
    base: tuple[int, int],
    top: tuple[int, int],
    color: tuple[int, int, int],
    shine: tuple[int, int, int],
    width: int = 6,
) -> None:
    bx, by = base
    tx, ty = top
    pygame.draw.line(surface, darken(color, 0.45), (bx + 2, by + 2), (tx + 2, ty + 2), width + 1)
    pygame.draw.line(surface, color, base, top, width)
    pygame.draw.line(surface, shine, (bx - 1, by), (tx - 1, ty), max(2, width // 3))


def draw_ring_floor_shadow(
    surface: pygame.Surface,
    points: list[tuple[int, int]],
    alpha: int = 70,
) -> None:
    if len(points) < 3:
        return
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    shadow_points = [(x, y + 14) for x, y in points]
    layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(layer, (0, 0, 0, alpha), shadow_points)
    surface.blit(layer, (0, 0))
