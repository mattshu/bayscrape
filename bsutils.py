"""Contains various utility functions."""
import os
import string


def get_input() -> str:
    """Get user input."""
    print("-")
    text = input(": ").lower()
    print("-")
    return text


def output(text):
    """Wrap the default print method for future formatting."""
    print(f"| {text}")


def get_terminal_width() -> int:
    """Return width of terminal."""
    default_max_width = 120
    try:
        return os.get_terminal_size().columns
    except OSError:
        return default_max_width


def strip_unicode(text) -> str:
    """Return filtered text that should be viewable on most terminals."""
    return "".join(
        filter(lambda readable: readable in set(string.printable), text),
    )
