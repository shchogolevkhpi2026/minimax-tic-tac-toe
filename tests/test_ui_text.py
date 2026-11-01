"""Tests for the plain-text renderers."""

from tictactoe.core.board import Board
from tictactoe.ui.text import board_lines, table_lines


def test_board_lines_numbered_and_dotted() -> None:
    board = Board.from_moves([0])
    assert board_lines(board, numbered=True)[0] == " X | 2 | 3"
    assert board_lines(board)[0] == " X | . | ."


def test_table_lines_alignment() -> None:
    lines = table_lines(["A", "Long"], [[1, 2], [333, 4]])
    assert lines == ["A   | Long", "----+-----", "1   | 2", "333 | 4"]
