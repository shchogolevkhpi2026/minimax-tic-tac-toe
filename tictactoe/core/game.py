"""Game controller: turn order and result."""

from dataclasses import dataclass, field
from typing import Callable, List, Mapping, Optional, Tuple

from tictactoe.core.board import Board, X, opponent
from tictactoe.core.players import Player

MoveCallback = Callable[[str, int, Player], None]


@dataclass
class GameResult:
    """Final result of a game; ``winner`` is None for a draw."""

    winner: Optional[str]
    moves: List[Tuple[str, int]] = field(default_factory=list)


class Game:
    """Runs a game between two players keyed by their symbols."""

    def __init__(self, players: Mapping[str, Player], first: str = X,
                 board: Optional[Board] = None) -> None:
        """Set up players (``{"X": ..., "O": ...}``) and who moves first."""
        self.players = dict(players)
        self.board = board if board is not None else Board()
        self.current = first
        self.moves: List[Tuple[str, int]] = []

    def is_over(self) -> bool:
        """Return True if the game has ended."""
        return self.board.is_over()

    def play_turn(self) -> Tuple[str, int]:
        """Let the current player move; return ``(symbol, cell index)``."""
        symbol = self.current
        player = self.players[symbol]
        move = player.choose_move(self.board, symbol)
        self.board.place(move, symbol)
        self.moves.append((symbol, move))
        self.current = opponent(symbol)
        return symbol, move

    def play(self, on_move: Optional[MoveCallback] = None) -> GameResult:
        """Play to the end, calling ``on_move(symbol, move, player)`` after each move."""
        while not self.is_over():
            symbol, move = self.play_turn()
            if on_move is not None:
                on_move(symbol, move, self.players[symbol])
        return GameResult(self.board.winner(), list(self.moves))
