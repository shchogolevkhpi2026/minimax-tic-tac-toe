"""Tests for minimax and alpha-beta."""

import random

import pytest

from tictactoe.ai.minimax import find_best_move
from tictactoe.core.board import Board, O, X
from tictactoe.modes.compare import comparison_positions

# Game tree size from the empty board: the root and every position reached by
# legal play are counted, and play stops at won or full boards.
FULL_TREE_NODES = 549_946


@pytest.fixture(scope="module")
def empty_board_results():
    board = Board()
    return (find_best_move(board, X, use_alpha_beta=False),
            find_best_move(board, X, use_alpha_beta=True))


def test_takes_winning_move() -> None:
    board = Board.from_moves([0, 3, 1, 4])  # X: 0,1  O: 3,4
    for use_ab in (False, True):
        result = find_best_move(board, X, use_ab)
        assert result.move == 2
        assert result.score == 9


def test_prefers_faster_win() -> None:
    board = Board(["X", "X", " ", "O", "O", " ", "X", " ", "O"])
    # O also threatens cell 5, but X wins first with cell 2.
    result = find_best_move(board, X)
    assert result.move == 2
    assert result.score == 9


def test_blocks_opponent_win() -> None:
    board = Board.from_moves([0, 4, 1])  # X threatens 2
    for use_ab in (False, True):
        assert find_best_move(board, O, use_ab).move == 2


def test_lost_position_scores_depth_minus_ten() -> None:
    # X threatens both 2 and 6; X wins at depth 2 whatever O does.
    board = Board(["X", "X", " ", "X", "O", " ", " ", " ", "O"])
    for use_ab in (False, True):
        assert find_best_move(board, O, use_ab).score == -8


def test_alpha_beta_matches_on_comparison_positions() -> None:
    for _, board in comparison_positions():
        player = board.next_player()
        plain = find_best_move(board, player, False)
        pruned = find_best_move(board, player, True)
        assert plain.score == pruned.score
        assert plain.move == pruned.move


def test_alpha_beta_matches_on_random_positions() -> None:
    rng = random.Random(12345)
    checked = 0
    while checked < 60:
        board = Board()
        symbol = X
        for _ in range(rng.randint(2, 8)):
            if board.is_over():
                break
            board.place(rng.choice(board.empty_cells()), symbol)
            symbol = O if symbol == X else X
        if board.is_over():
            continue
        player = board.next_player()
        plain = find_best_move(board, player, False)
        pruned = find_best_move(board, player, True)
        assert (plain.score, plain.move) == (pruned.score, pruned.move)
        checked += 1


def test_alpha_beta_visits_far_fewer_nodes(empty_board_results) -> None:
    plain, pruned = empty_board_results
    assert pruned.nodes < plain.nodes / 10


def test_full_tree_size(empty_board_results) -> None:
    plain, _ = empty_board_results
    assert plain.nodes == FULL_TREE_NODES


def test_empty_board_is_a_draw(empty_board_results) -> None:
    plain, pruned = empty_board_results
    assert plain.score == pruned.score == 0
    assert plain.move == pruned.move == 0


def test_search_does_not_modify_board() -> None:
    board = Board.from_moves([0, 4])
    before = board.cells
    find_best_move(board, X)
    assert board.cells == before


def test_finished_game_rejected() -> None:
    with pytest.raises(ValueError):
        find_best_move(Board(list("XXXOO    ")), O)
