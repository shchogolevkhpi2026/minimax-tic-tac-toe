"""Application settings shared by the menu and command-line modes."""

from dataclasses import dataclass


@dataclass
class Settings:
    """Mutable user settings."""

    alpha_beta: bool = True
    delay: bool = True
