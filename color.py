"""Simplify color handling into a dict and a method."""
from enum import Enum

import colored


class Color(Enum):
    """Various color identifiers."""

    VIP = "magenta_3a"
    TRUSTED = "chartreuse_2b"
    HEALTHY = "green_1"
    HIGHLIGHT = "yellow_1"
    UNHEALTHY = "light_goldenrod_1"
    SICK = "red_3a"
    NOTICE = "yellow_3a"
    BLUE = "sky_blue_3"
    HEADER = "light_sky_blue_3a"
    HEADERBG = "deep_pink_4c"
    ERROR = "red_3a"

    def __str__(self) -> str:
        return str(self.value)


def style(text, color_enum, wrap_formatting=True) -> str:
    """Manage the color codes for special texts."""
    color_char = colored.fg(color_enum.value)
    text = color_char + str(text)
    if wrap_formatting:
        text += reset()
    return text


def reset() -> str:
    """Return the default reset character to undo formatting."""
    return colored.attr(0)
