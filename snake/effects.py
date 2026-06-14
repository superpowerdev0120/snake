"""Screen effects and simple synthesized sounds."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame


def _make_tone(frequency: float, duration: float, volume: float = 0.35) -> pygame.mixer.Sound | None:
    try:
        sample_rate = 22050
        count = max(1, int(sample_rate * duration))
        samples = bytearray()
        for i in range(count):
            t = i / sample_rate
            envelope = 1.0 - (i / count) ** 1.4
            wave = math.sin(2 * math.pi * frequency * t)
            value = int(127 * volume * envelope * wave)
            samples.append(max(0, min(255, 128 + value)))
        return pygame.mixer.Sound(buffer=bytes(samples))
    except pygame.error:
        return None


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: int
    max_life: int
    color: tuple[int, int, int]
    radius: int


class EffectManager:
    """Particles, pulses, and short sounds for game moments."""

    def __init__(self) -> None:
        self._particles: list[Particle] = []
        self._pulse_x = 0.0
        self._pulse_y = 0.0
        self._pulse_radius = 0.0
        self._pulse_max = 0.0
        self._pulse_color = (255, 210, 90)
        self._banner_text = ""
        self._banner_timer = 0
        self._pop_text = ""
        self._pop_x = 0.0
        self._pop_y = 0.0
        self._pop_timer = 0
        self._rng = random.Random()
        self._start_sound = _make_tone(660, 0.12, 0.28)
        self._bell_sound = _make_tone(880, 0.18, 0.32)
        self._eat_sound = _make_tone(520, 0.08, 0.25)

    def trigger_start(self, x: float, y: float) -> None:
        self._pulse_x = x
        self._pulse_y = y
        self._pulse_radius = 8
        self._pulse_max = 180
        self._pulse_color = (255, 210, 90)
        self._banner_text = "FIGHT!"
        self._banner_timer = 28
        self._spawn_burst(x, y, count=28, speed=4.5, colors=[(255, 220, 120), (255, 255, 255), (220, 186, 96)])
        self._play(self._bell_sound)
        self._play(self._start_sound)

    def trigger_eat(self, x: float, y: float) -> None:
        self._pop_text = "+1"
        self._pop_x = x
        self._pop_y = y
        self._pop_timer = 18
        self._spawn_burst(
            x,
            y,
            count=16,
            speed=3.2,
            colors=[(240, 70, 70), (255, 210, 90), (255, 255, 255), (88, 180, 72)],
        )
        self._play(self._eat_sound)

    def _spawn_burst(
        self,
        x: float,
        y: float,
        count: int,
        speed: float,
        colors: list[tuple[int, int, int]],
    ) -> None:
        for _ in range(count):
            angle = self._rng.random() * math.tau
            velocity = speed * (0.5 + self._rng.random())
            self._particles.append(
                Particle(
                    x=x,
                    y=y,
                    vx=math.cos(angle) * velocity,
                    vy=math.sin(angle) * velocity,
                    life=16 + int(self._rng.random() * 10),
                    max_life=26,
                    color=self._rng.choice(colors),
                    radius=2 + int(self._rng.random() * 3),
                )
            )

    def _play(self, sound: pygame.mixer.Sound | None) -> None:
        if sound is not None:
            sound.play()

    def update(self) -> None:
        if self._pulse_radius > 0:
            self._pulse_radius += 8
            if self._pulse_radius > self._pulse_max:
                self._pulse_radius = 0

        if self._banner_timer > 0:
            self._banner_timer -= 1

        if self._pop_timer > 0:
            self._pop_timer -= 1
            self._pop_y -= 0.6

        alive: list[Particle] = []
        for particle in self._particles:
            particle.life -= 1
            if particle.life <= 0:
                continue
            particle.x += particle.vx
            particle.y += particle.vy
            particle.vy += 0.08
            particle.vx *= 0.96
            alive.append(particle)
        self._particles = alive

    def draw(self, surface: pygame.Surface, banner_font: pygame.font.Font, pop_font: pygame.font.Font) -> None:
        fx = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        if self._pulse_radius > 0:
            alpha = max(0, int(120 * (1 - self._pulse_radius / max(self._pulse_max, 1))))
            pygame.draw.circle(
                fx,
                (*self._pulse_color, alpha),
                (int(self._pulse_x), int(self._pulse_y)),
                int(self._pulse_radius),
                4,
            )

        for particle in self._particles:
            alpha = int(255 * (particle.life / particle.max_life))
            pygame.draw.circle(
                fx,
                (*particle.color, alpha),
                (int(particle.x), int(particle.y)),
                particle.radius,
            )

        surface.blit(fx, (0, 0))

        if self._banner_timer > 0:
            text = banner_font.render(self._banner_text, True, (255, 240, 210))
            shadow = banner_font.render(self._banner_text, True, (0, 0, 0))
            rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 70))
            surface.blit(shadow, shadow.get_rect(center=(rect.centerx + 2, rect.centery + 2)))
            surface.blit(text, rect)

        if self._pop_timer > 0:
            pop = pop_font.render(self._pop_text, True, (255, 240, 210))
            pop_shadow = pop_font.render(self._pop_text, True, (0, 0, 0))
            rect = pop.get_rect(center=(int(self._pop_x), int(self._pop_y)))
            surface.blit(pop_shadow, pop_shadow.get_rect(center=(rect.centerx + 1, rect.centery + 1)))
            surface.blit(pop, rect)
