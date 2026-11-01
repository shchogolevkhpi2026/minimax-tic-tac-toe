"""Abstract user interface. Core and modes talk to the user only through it."""

from abc import ABC, abstractmethod
from typing import Optional, Sequence

from tictactoe.ai.minimax import SearchResult
from tictactoe.core.board import Board


class AbortGame(Exception):
    """Raised by an interface when the user leaves the current screen."""


class UserInterface(ABC):
    """Everything the application needs from a front end (console, GUI, web)."""

    @abstractmethod
    def show_board(self, board: Board) -> None:
        """Display the board."""

    @abstractmethod
    def ask_move(self, symbol: str) -> str:
        """Return the raw move text typed by the human playing ``symbol``."""

    @abstractmethod
    def show_message(self, text: str) -> None:
        """Display an informational message."""

    @abstractmethod
    def show_search_stats(self, symbol: str, result: SearchResult) -> None:
        """Display what the AI chose and what the search cost."""

    @abstractmethod
    def show_table(self, title: str, headers: Sequence[str],
                   rows: Sequence[Sequence[object]]) -> None:
        """Display tabular data."""

    @abstractmethod
    def choose_option(self, title: str, options: Sequence[str]) -> int:
        """Let the user pick one option; return its 0-based index."""

    @abstractmethod
    def ask_int(self, prompt: str, minimum: int, maximum: int,
                default: Optional[int] = None) -> int:
        """Ask for an integer in ``[minimum, maximum]``."""

    @abstractmethod
    def begin_game(self, title: str) -> None:
        """Start a fresh game screen (clears board, log and statistics)."""

    @abstractmethod
    def show_report(self, title: str, lines: Sequence[str]) -> None:
        """Display a multi-line text report and let the user read it."""

    @abstractmethod
    def pause(self) -> None:
        """Give the user time to read before the screen changes."""
