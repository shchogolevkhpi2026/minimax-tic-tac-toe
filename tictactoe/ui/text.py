"""Plain-text rendering shared by the interfaces."""

from typing import List, Sequence

from tictactoe.core.board import EMPTY, Board

SEPARATOR = "---+---+---"


def board_lines(board: Board, numbered: bool = False) -> List[str]:
    """Render the board; free cells show their number or a dot."""
    cells = [cell if cell != EMPTY else (str(i + 1) if numbered else ".")
             for i, cell in enumerate(board.cells)]
    rows = [" " + " | ".join(cells[i:i + 3]) for i in (0, 3, 6)]
    return [rows[0], SEPARATOR, rows[1], SEPARATOR, rows[2]]


def table_lines(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> List[str]:
    """Render an aligned text table (header, rule, rows)."""
    text_rows = [[str(value) for value in row] for row in rows]
    widths = [max(len(h), *(len(r[i]) for r in text_rows))
              for i, h in enumerate(headers)]
    lines = [" | ".join(h.ljust(w) for h, w in zip(headers, widths)).rstrip(),
             "-+-".join("-" * w for w in widths)]
    lines += [" | ".join(v.ljust(w) for v, w in zip(row, widths)).rstrip()
              for row in text_rows]
    return lines
