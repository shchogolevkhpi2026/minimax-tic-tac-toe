"""Full-screen curses implementation: arrow-key menus, grid board, side panel."""

import curses
from typing import Dict, List, Optional, Sequence

from tictactoe.ai.minimax import SearchResult
from tictactoe.core.board import EMPTY, Board
from tictactoe.ui.base import AbortGame, UserInterface
from tictactoe.ui.text import table_lines

CELL_WIDTH = 7
CELL_HEIGHT = 3
BOARD_TOP = 2
BOARD_LEFT = 2
LOG_LINES = 8

ENTER_KEYS = {10, 13, curses.KEY_ENTER}
QUIT_KEYS = {ord("q"), ord("Q"), 27}
UP_KEYS = {curses.KEY_UP, ord("w"), ord("k")}
DOWN_KEYS = {curses.KEY_DOWN, ord("s"), ord("j")}
MOVES = {
    curses.KEY_UP: (-1, 0), ord("w"): (-1, 0),
    curses.KEY_DOWN: (1, 0), ord("s"): (1, 0),
    curses.KEY_LEFT: (0, -1), ord("a"): (0, -1),
    curses.KEY_RIGHT: (0, 1), ord("d"): (0, 1),
}

_COLOURS = {
    "x": curses.COLOR_CYAN,
    "o": curses.COLOR_MAGENTA,
    "win": curses.COLOR_GREEN,
    "title": curses.COLOR_CYAN,
    "ok": curses.COLOR_GREEN,
    "accent": curses.COLOR_YELLOW,
}
_MONO = {
    "plain": curses.A_NORMAL, "x": curses.A_BOLD, "o": curses.A_BOLD,
    "win": curses.A_BOLD | curses.A_REVERSE, "title": curses.A_BOLD,
    "ok": curses.A_BOLD, "accent": curses.A_BOLD, "dim": curses.A_DIM,
    "cursor": curses.A_REVERSE, "selected": curses.A_REVERSE,
}


def init_styles() -> Dict[str, int]:
    """Map style names to curses attributes, coloured when supported."""
    styles = dict(_MONO)
    if not curses.has_colors():
        return styles
    curses.start_color()
    background = curses.COLOR_BLACK
    try:
        curses.use_default_colors()
        background = -1
    except curses.error:
        pass
    for number, (name, colour) in enumerate(_COLOURS.items(), start=1):
        curses.init_pair(number, colour, background)
        styles[name] = curses.color_pair(number) | curses.A_BOLD
    return styles


def put(window, y: int, x: int, text: str, attr: int = 0) -> None:
    """Write text clipped to the window; never raises on small terminals."""
    height, width = window.getmaxyx()
    if not 0 <= y < height or not 0 <= x < width - 1:
        return
    try:
        window.addstr(y, x, text[:width - 1 - x], attr)
    except curses.error:
        pass


class CursesUI(UserInterface):
    """Keyboard-driven full-screen interface."""

    def __init__(self, screen) -> None:
        """Wrap a curses window (as given by ``curses.wrapper``)."""
        self.screen = screen
        self.styles = init_styles()
        self._board: Optional[Board] = None
        self._title = "Tic-tac-toe minimax"
        self._log: List[str] = []
        self._stats: List[str] = []
        self._cursor = 4
        self._footer = ""
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        screen.keypad(True)
        screen.timeout(-1)

    # ----- drawing ---------------------------------------------------------------

    def _draw(self, show_cursor: bool = False) -> None:
        self.screen.erase()
        put(self.screen, 0, 2, self._title, self.styles["title"])
        if self._board is not None:
            self._draw_board(self._board, show_cursor)
            self._draw_panel()
        put(self.screen, self.screen.getmaxyx()[0] - 1, 2, self._footer, self.styles["dim"])
        self.screen.refresh()

    def _draw_board(self, board: Board, show_cursor: bool) -> None:
        win = set(board.winning_line() or ())
        border = "+" + "+".join(["-" * CELL_WIDTH] * 3) + "+"
        for row in range(3):
            y = BOARD_TOP + row * (CELL_HEIGHT + 1)
            put(self.screen, y, BOARD_LEFT, border)
            for line in range(CELL_HEIGHT):
                for col in range(3):
                    self._draw_cell(board, y + 1 + line, col, row * 3 + col, line,
                                    win, show_cursor)
                put(self.screen, y + 1 + line, BOARD_LEFT, "|")
                put(self.screen, y + 1 + line,
                    BOARD_LEFT + 3 * (CELL_WIDTH + 1), "|")
        put(self.screen, BOARD_TOP + 3 * (CELL_HEIGHT + 1), BOARD_LEFT, border)

    def _draw_cell(self, board: Board, y: int, col: int, index: int, line: int,
                   win: set, show_cursor: bool) -> None:
        x = BOARD_LEFT + col * (CELL_WIDTH + 1)
        put(self.screen, y, x, "|")
        symbol = board.cells[index]
        centre = line == CELL_HEIGHT // 2
        if symbol == EMPTY:
            text, style = (str(index + 1) if centre else ""), self.styles["dim"]
        else:
            text = symbol if centre else ""
            style = self.styles["win" if index in win else symbol.lower()]
        if show_cursor and index == self._cursor:
            style = self.styles["cursor"]
        put(self.screen, y, x + 1, text.center(CELL_WIDTH), style)

    def _draw_panel(self) -> None:
        left = BOARD_LEFT + 3 * (CELL_WIDTH + 1) + 5
        y = BOARD_TOP
        if self._stats:
            put(self.screen, y, left, "Last AI move", self.styles["title"])
            for offset, text in enumerate(self._stats, start=1):
                put(self.screen, y + offset, left, "  " + text)
            y += len(self._stats) + 2
        put(self.screen, y, left, "Messages", self.styles["title"])
        for offset, text in enumerate(self._log[-LOG_LINES:], start=1):
            put(self.screen, y + offset, left, "  " + text)
        legend_y = BOARD_TOP + 3 * (CELL_HEIGHT + 1) + 2
        put(self.screen, legend_y, BOARD_LEFT + 2, " X ", self.styles["x"])
        put(self.screen, legend_y, BOARD_LEFT + 6, " O ", self.styles["o"])
        put(self.screen, legend_y, BOARD_LEFT + 10, "win line", self.styles["win"])

    # ----- UserInterface ---------------------------------------------------------

    def begin_game(self, title: str) -> None:
        """Clear the game screen and set its title."""
        self._title = title
        self._board = None
        self._log = []
        self._stats = []
        self._footer = ""
        self._draw()

    def show_board(self, board: Board) -> None:
        """Draw the board."""
        self._board = board.copy()
        self._draw()

    def ask_move(self, symbol: str) -> str:
        """Move the cursor with arrows / WASD and press Enter, or press 1-9."""
        self._footer = (f"You are {symbol}   arrows / WASD move   Enter place   "
                        "1-9 direct   q back")
        while True:
            self._draw(show_cursor=True)
            key = self.screen.getch()
            if key in QUIT_KEYS:
                raise AbortGame
            if key in ENTER_KEYS:
                return str(self._cursor + 1)
            if ord("1") <= key <= ord("9"):
                self._cursor = key - ord("1")
                return chr(key)
            if key in MOVES:
                d_row, d_col = MOVES[key]
                row = min(max(self._cursor // 3 + d_row, 0), 2)
                col = min(max(self._cursor % 3 + d_col, 0), 2)
                self._cursor = row * 3 + col

    def show_message(self, text: str) -> None:
        """Append to the message log."""
        self._log.extend(text.strip("\n").split("\n"))
        self._draw()

    def show_search_stats(self, symbol: str, result: SearchResult) -> None:
        """Show the AI move statistics in the side panel."""
        self._stats = [f"Player: {symbol}", f"Cell:   {result.move + 1}",
                       f"Score:  {result.score}", f"Nodes:  {result.nodes}",
                       f"Time:   {result.elapsed_ms:.2f} ms"]
        self._draw()

    def show_table(self, title: str, headers: Sequence[str],
                   rows: Sequence[Sequence[object]]) -> None:
        """Show a table on a report page."""
        self.show_report(title, table_lines(headers, rows))

    def show_report(self, title: str, lines: Sequence[str]) -> None:
        """Scrollable text page."""
        top = 0
        while True:
            height = max(self.screen.getmaxyx()[0] - 4, 1)
            self.screen.erase()
            put(self.screen, 0, 2, title, self.styles["title"])
            for offset, line in enumerate(lines[top:top + height]):
                put(self.screen, 2 + offset, 2, line)
            put(self.screen, self.screen.getmaxyx()[0] - 1, 2,
                "up/down scroll   PgUp/PgDn page   q / Enter back", self.styles["dim"])
            self.screen.refresh()
            key = self.screen.getch()
            limit = max(len(lines) - height, 0)
            if key in QUIT_KEYS or key in ENTER_KEYS:
                return
            if key in DOWN_KEYS:
                top = min(top + 1, limit)
            elif key in UP_KEYS:
                top = max(top - 1, 0)
            elif key == curses.KEY_NPAGE:
                top = min(top + height, limit)
            elif key == curses.KEY_PPAGE:
                top = max(top - height, 0)

    def choose_option(self, title: str, options: Sequence[str]) -> int:
        """Arrow-key menu; digits are shortcuts, q / Esc raises ``AbortGame``."""
        index = 0
        while True:
            self.screen.erase()
            put(self.screen, 0, 2, title, self.styles["title"])
            for number, option in enumerate(options):
                attr = self.styles["selected"] if number == index else 0
                put(self.screen, 2 + number, 4, f" {number + 1}. {option} ", attr)
            put(self.screen, self.screen.getmaxyx()[0] - 1, 2,
                f"up/down select   Enter choose   1-{len(options)} shortcut   q back",
                self.styles["dim"])
            self.screen.refresh()
            key = self.screen.getch()
            if key in QUIT_KEYS:
                raise AbortGame
            if key in ENTER_KEYS:
                return index
            if ord("1") <= key < ord("1") + len(options):
                return key - ord("1")
            if key in UP_KEYS:
                index = (index - 1) % len(options)
            elif key in DOWN_KEYS:
                index = (index + 1) % len(options)

    def ask_int(self, prompt: str, minimum: int, maximum: int,
                default: Optional[int] = None) -> int:
        """Type a number; Enter accepts (empty = default), Esc raises ``AbortGame``."""
        typed = ""
        error = ""
        hint = f"[{minimum}-{maximum}" + (f", default {default}]" if default else "]")
        while True:
            self.screen.erase()
            put(self.screen, 0, 2, prompt, self.styles["title"])
            put(self.screen, 2, 4, f"{hint}: {typed}_")
            put(self.screen, 4, 4, error, self.styles["accent"])
            put(self.screen, self.screen.getmaxyx()[0] - 1, 2,
                "type digits   Enter accept   Esc back", self.styles["dim"])
            self.screen.refresh()
            key = self.screen.getch()
            if key == 27:
                raise AbortGame
            if key in ENTER_KEYS:
                if not typed and default is not None:
                    return default
                if typed and minimum <= int(typed) <= maximum:
                    return int(typed)
                error = f"Enter a number from {minimum} to {maximum}."
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                typed = typed[:-1]
            elif ord("0") <= key <= ord("9") and len(typed) < 6:
                typed += chr(key)

    def pause(self) -> None:
        """Wait for a key press, keeping the final board visible."""
        self._footer = "Press any key to continue"
        self._draw()
        self.screen.getch()
        self._footer = ""
