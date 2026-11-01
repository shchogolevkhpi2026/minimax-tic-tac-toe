"""Plain terminal implementation of the user interface (stdin / stdout)."""

from typing import Optional, Sequence

from tictactoe.ai.minimax import SearchResult
from tictactoe.core.board import Board
from tictactoe.ui.base import UserInterface
from tictactoe.ui.text import board_lines, table_lines


class ConsoleUI(UserInterface):
    """Reads from stdin and prints to stdout."""

    def show_board(self, board: Board) -> None:
        """Print the board; free cells show their numbers."""
        print("\n" + "\n".join(board_lines(board, numbered=True)) + "\n")

    def ask_move(self, symbol: str) -> str:
        """Prompt for a cell number."""
        return input(f"Your move ({symbol}), cell 1-9: ")

    def show_message(self, text: str) -> None:
        """Print a message."""
        print(text)

    def show_search_stats(self, symbol: str, result: SearchResult) -> None:
        """Print the AI move and search statistics."""
        print(f"AI ({symbol}) chose cell {result.move + 1} | score: {result.score} | "
              f"nodes: {result.nodes} | time: {result.elapsed_ms:.2f} ms")

    def show_table(self, title: str, headers: Sequence[str],
                   rows: Sequence[Sequence[object]]) -> None:
        """Print an aligned text table."""
        print(f"\n{title}")
        print("\n".join(table_lines(headers, rows)))

    def choose_option(self, title: str, options: Sequence[str]) -> int:
        """Show a numbered menu and return the 0-based choice."""
        print(f"\n{title}")
        for number, option in enumerate(options, start=1):
            print(f"  {number}. {option}")
        return self.ask_int("Choose", 1, len(options)) - 1

    def ask_int(self, prompt: str, minimum: int, maximum: int,
                default: Optional[int] = None) -> int:
        """Ask until an integer in range is entered (empty input = default)."""
        suffix = f" [{minimum}-{maximum}" + (f", default {default}]" if default else "]")
        while True:
            raw = input(f"{prompt}{suffix}: ").strip()
            if not raw and default is not None:
                return default
            try:
                value = int(raw)
            except ValueError:
                print("Please enter a whole number.")
                continue
            if minimum <= value <= maximum:
                return value
            print(f"The number must be between {minimum} and {maximum}.")

    def begin_game(self, title: str) -> None:
        """Print the game title."""
        print(f"\n=== {title} ===")

    def show_report(self, title: str, lines: Sequence[str]) -> None:
        """Print the report."""
        print(f"\n{title}")
        print("\n".join(lines))

    def pause(self) -> None:
        """Nothing to do: the console keeps its scrollback."""
