"""Available game modes."""

from enum import Enum, auto


class GameMode(Enum):
    SOLO = auto()
    TWO_PLAYER = auto()
    VS_COM = auto()

    @property
    def label(self) -> str:
        labels = {
            GameMode.SOLO: "1 Player",
            GameMode.TWO_PLAYER: "2 Player",
            GameMode.VS_COM: "Player vs Computer",
        }
        return labels[self]
