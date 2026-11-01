"""Tests for the board."""

import pytest

from tictactoe.core.board import EMPTY, WIN_LINES, Board, O, X


def test_there_are_eight_lines() -> None:
    assert len(WIN_LINES) == 8


@pytest.mark.parametrize("line", WIN_LINES)
@pytest.mark.parametrize("symbol", [X, O])
def test_winner_on_each_line(line, symbol) -> None:
    board = Board()
    for index in line:
        board.place(index, symbol)
    assert board.winner() == symbol
    assert board.is_over()


def test_draw() -> None:
    board = Board(list("XOXXOOOXX"))
    assert board.winner() is None
    assert board.is_full() and board.is_draw() and board.is_over()


def test_unfinished_game() -> None:
    board = Board.from_moves([0, 4])
    assert board.winner() is None
    assert not board.is_over()


def test_empty_cells() -> None:
    board = Board.from_moves([0, 4, 8])
    assert board.empty_cells() == [1, 2, 3, 5, 6, 7]


def test_place_on_taken_cell_fails() -> None:
    board = Board.from_moves([0])
    with pytest.raises(ValueError):
        board.place(0, O)


def test_undo_and_copy() -> None:
    board = Board.from_moves([0])
    clone = board.copy()
    board.undo(0)
    assert board.cells[0] == EMPTY
    assert clone.cells[0] == X


def test_next_player() -> None:
    assert Board().next_player() == X
    assert Board.from_moves([0]).next_player() == O
    assert Board.from_moves([0, 1]).next_player() == X


def test_wrong_size_rejected() -> None:
    with pytest.raises(ValueError):
        Board(["X"])


def test_winning_line() -> None:
    assert Board().winning_line() is None
    assert Board(list("XXXOO    ")).winning_line() == (0, 1, 2)
