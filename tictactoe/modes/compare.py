"""Comparison of plain minimax and alpha-beta on fixed positions."""

from dataclasses import dataclass
from typing import List, Tuple

from tictactoe.ai.minimax import SearchResult, find_best_move
from tictactoe.core.board import Board


@dataclass
class ComparisonRow:
    """Both searches for one position."""

    name: str
    board: Board
    player: str
    plain: SearchResult
    pruned: SearchResult

    @property
    def reduction_percent(self) -> float:
        """How much fewer nodes alpha-beta visited, in percent."""
        return (1 - self.pruned.nodes / self.plain.nodes) * 100

    @property
    def scores_match(self) -> bool:
        """True if both modes returned the same score."""
        return self.plain.score == self.pruned.score

    @property
    def moves_match(self) -> bool:
        """True if both modes returned the same move."""
        return self.plain.move == self.pruned.move


def comparison_positions() -> List[Tuple[str, Board]]:
    """Return named positions used for the comparison (X always moves first)."""
    return [
        ("Empty board", Board()),
        ("After 1 move (X in corner)", Board.from_moves([0])),
        ("After 2 moves (X corner, O centre)", Board.from_moves([0, 4])),
        ("After 3 moves (X corners, O centre)", Board.from_moves([0, 4, 8])),
        ("Immediate win for X", Board.from_moves([0, 3, 1, 4])),
        ("O must block X", Board.from_moves([0, 4, 1])),
    ]


def compare_position(name: str, board: Board) -> ComparisonRow:
    """Run both searches for the player to move on ``board``."""
    player = board.next_player()
    plain = find_best_move(board, player, use_alpha_beta=False)
    pruned = find_best_move(board, player, use_alpha_beta=True)
    return ComparisonRow(name, board, player, plain, pruned)


def compare_all() -> List[ComparisonRow]:
    """Compare both modes on every standard position."""
    return [compare_position(name, board) for name, board in comparison_positions()]
