"""Players: abstract base, human (via UserInterface), AI and random."""

import random
from abc import ABC, abstractmethod
from typing import List, Optional

from tictactoe.ai.minimax import SearchResult, find_best_move
from tictactoe.core.board import Board
from tictactoe.ui.base import UserInterface


class Player(ABC):
    """Something that can pick a move for a given symbol."""

    @abstractmethod
    def choose_move(self, board: Board, symbol: str) -> int:
        """Return the 0-based index of the chosen free cell."""


def parse_move(text: str, board: Board) -> int:
    """Convert user text ("1".."9") into a free cell index.

    Raises ``ValueError`` with a user-friendly message on bad input.
    """
    text = text.strip()
    if not text.lstrip("-").isdigit():
        raise ValueError("Please enter a number from 1 to 9.")
    number = int(text)
    if not 1 <= number <= 9:
        raise ValueError("The number must be between 1 and 9.")
    if not board.is_empty_cell(number - 1):
        raise ValueError(f"Cell {number} is already taken.")
    return number - 1


class HumanPlayer(Player):
    """A human who enters moves through a ``UserInterface``."""

    def __init__(self, ui: UserInterface) -> None:
        """Remember the interface used for input and error messages."""
        self._ui = ui

    def choose_move(self, board: Board, symbol: str) -> int:
        """Ask until a valid move is entered."""
        while True:
            try:
                return parse_move(self._ui.ask_move(symbol), board)
            except ValueError as error:
                self._ui.show_message(str(error))


class AIPlayer(Player):
    """Minimax player; remembers search statistics."""

    def __init__(self, use_alpha_beta: bool = True) -> None:
        """Choose whether the search uses alpha-beta pruning."""
        self.use_alpha_beta = use_alpha_beta
        self.last_result: Optional[SearchResult] = None
        self.total_nodes = 0
        self.total_ms = 0.0

    def choose_move(self, board: Board, symbol: str) -> int:
        """Run the search and return its best move."""
        result = find_best_move(board, symbol, self.use_alpha_beta)
        self.last_result = result
        self.total_nodes += result.nodes
        self.total_ms += result.elapsed_ms
        return result.move


class RandomPlayer(Player):
    """Plays a uniformly random free cell."""

    def __init__(self, rng: Optional[random.Random] = None) -> None:
        """Use ``rng`` for reproducible games."""
        self._rng = rng or random.Random()

    def choose_move(self, board: Board, symbol: str) -> int:
        """Pick a random free cell."""
        free: List[int] = board.empty_cells()
        return self._rng.choice(free)
