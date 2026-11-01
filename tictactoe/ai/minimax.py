"""Minimax search with optional alpha-beta pruning.

Scores are always from the point of view of the player the move is searched
for (the maximizer): a win is ``WIN_SCORE - depth``, a loss is
``depth - WIN_SCORE`` and a draw is 0. The search tree is never stored and no
memoization is used, so node counts of the two modes are directly comparable.
"""

import time
from dataclasses import dataclass
from typing import Optional

from tictactoe.core.board import Board, opponent

WIN_SCORE = 10
INF = float("inf")


@dataclass(frozen=True)
class SearchResult:
    """Outcome of a root search."""

    move: int
    score: int
    nodes: int
    elapsed_ms: float


class NodeCounter:
    """Mutable counter of visited nodes shared by the recursive calls."""

    def __init__(self) -> None:
        """Start from zero."""
        self.nodes = 0


def minimax(
    board: Board,
    depth: int,
    maximizing: bool,
    player: str,
    alpha: float = -INF,
    beta: float = INF,
    use_alpha_beta: bool = False,
    counter: Optional[NodeCounter] = None,
) -> int:
    """Return the score of ``board`` for ``player``.

    ``maximizing`` tells whose turn it is: ``player`` (True) or the opponent.
    Every call, including the first one, counts as one visited node.
    """
    if counter is not None:
        counter.nodes += 1

    winner = board.winner()
    if winner is not None:
        return WIN_SCORE - depth if winner == player else depth - WIN_SCORE
    if board.is_full():
        return 0

    symbol = player if maximizing else opponent(player)
    best = -INF if maximizing else INF
    for move in board.empty_cells():
        board.place(move, symbol)
        score = minimax(board, depth + 1, not maximizing, player,
                        alpha, beta, use_alpha_beta, counter)
        board.undo(move)
        if maximizing:
            best = max(best, score)
            alpha = max(alpha, best)
        else:
            best = min(best, score)
            beta = min(beta, best)
        if use_alpha_beta and beta <= alpha:
            break
    return int(best)


def find_best_move(board: Board, player: str, use_alpha_beta: bool = True) -> SearchResult:
    """Search for the best move of ``player`` on ``board``.

    Among moves with equal score the one with the smallest index wins, so the
    result is deterministic and identical with and without pruning. The root
    counts as one node. The board is left unchanged.
    """
    if board.is_over():
        raise ValueError("Cannot search on a finished game")

    started = time.perf_counter()
    counter = NodeCounter()
    counter.nodes += 1  # the root node

    alpha = -INF
    best_move = -1
    best_score = -INF
    for move in board.empty_cells():
        board.place(move, player)
        score = minimax(board, 1, False, player, alpha, INF, use_alpha_beta, counter)
        board.undo(move)
        if score > best_score:
            best_score, best_move = score, move
            if use_alpha_beta:
                alpha = best_score

    elapsed_ms = (time.perf_counter() - started) * 1000
    return SearchResult(best_move, int(best_score), counter.nodes, elapsed_ms)
