"""Tic-tac-toe board: moves, winner detection, end of game."""

from typing import List, Optional, Sequence, Tuple

X = "X"
O = "O"  # noqa: E741 - the symbol is called "O" on purpose
EMPTY = " "

WIN_LINES: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
)


def opponent(symbol: str) -> str:
    """Return the other player's symbol."""
    return O if symbol == X else X


class Board:
    """A 3x3 board stored as a flat list of 9 cells (index 0..8, row by row)."""

    def __init__(self, cells: Optional[Sequence[str]] = None) -> None:
        """Create a board, empty by default or copied from ``cells``."""
        if cells is None:
            self._cells: List[str] = [EMPTY] * 9
        else:
            if len(cells) != 9:
                raise ValueError("A board must have exactly 9 cells")
            self._cells = list(cells)

    @classmethod
    def from_moves(cls, moves: Sequence[int], first: str = X) -> "Board":
        """Build a board by playing ``moves`` alternately, starting with ``first``."""
        board = cls()
        symbol = first
        for move in moves:
            board.place(move, symbol)
            symbol = opponent(symbol)
        return board

    @property
    def cells(self) -> Tuple[str, ...]:
        """Read-only snapshot of the cells."""
        return tuple(self._cells)

    def copy(self) -> "Board":
        """Return an independent copy of the board."""
        return Board(self._cells)

    def is_empty_cell(self, index: int) -> bool:
        """Return True if ``index`` is a valid, free cell."""
        return 0 <= index < 9 and self._cells[index] == EMPTY

    def place(self, index: int, symbol: str) -> None:
        """Put ``symbol`` into a free cell."""
        if not self.is_empty_cell(index):
            raise ValueError(f"Cell {index} is not available")
        self._cells[index] = symbol

    def undo(self, index: int) -> None:
        """Clear a cell (used by the search to take a move back)."""
        self._cells[index] = EMPTY

    def empty_cells(self) -> List[int]:
        """Return the indices of free cells in ascending order."""
        return [i for i, cell in enumerate(self._cells) if cell == EMPTY]

    def winning_line(self) -> Optional[Tuple[int, int, int]]:
        """Return the three cells of the winning line, or None."""
        cells = self._cells
        for line in WIN_LINES:
            a, b, c = line
            if cells[a] != EMPTY and cells[a] == cells[b] == cells[c]:
                return line
        return None

    def winner(self) -> Optional[str]:
        """Return the winning symbol, or None if nobody has won."""
        line = self.winning_line()
        return None if line is None else self._cells[line[0]]

    def is_full(self) -> bool:
        """Return True if no free cells remain."""
        return EMPTY not in self._cells

    def is_draw(self) -> bool:
        """Return True if the board is full and nobody has won."""
        return self.is_full() and self.winner() is None

    def is_over(self) -> bool:
        """Return True if the game has ended (win or draw)."""
        return self.winner() is not None or self.is_full()

    def next_player(self) -> str:
        """Return who moves next, assuming X moves first."""
        x_count = self._cells.count(X)
        o_count = self._cells.count(O)
        return X if x_count <= o_count else O

    def __eq__(self, other: object) -> bool:
        """Boards are equal when their cells are equal."""
        return isinstance(other, Board) and self._cells == other._cells

    def __repr__(self) -> str:
        """Debug representation."""
        return f"Board({''.join(self._cells)!r})"
