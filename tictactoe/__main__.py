"""Command-line entry point: ``python -m tictactoe``."""

import argparse
import curses
import sys
from typing import List, Optional

from tictactoe.app import App
from tictactoe.core.board import O, X
from tictactoe.settings import Settings
from tictactoe.ui.base import AbortGame, UserInterface
from tictactoe.ui.console import ConsoleUI
from tictactoe.ui.curses_ui import CursesUI


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="python -m tictactoe",
        description="Tic-tac-toe with a minimax AI. Without arguments: interactive menu.")
    parser.add_argument("--mode", choices=["play", "simulate", "compare"],
                        help="run a mode directly instead of the menu")
    parser.add_argument("--alpha-beta", choices=["on", "off"], default="on",
                        help="use alpha-beta pruning (default: on)")
    parser.add_argument("--games", type=int, default=1,
                        help="number of games in simulate mode (default: 1)")
    parser.add_argument("--first", choices=["human", "ai"], default="human",
                        help="who moves first in play mode (default: human)")
    parser.add_argument("--symbol", choices=[X, O], default=X,
                        help="human symbol in play mode (default: X)")
    parser.add_argument("--ui", choices=["auto", "console", "curses"], default="auto",
                        help="interface: full-screen curses or plain console "
                             "(auto: curses when attached to a terminal)")
    parser.add_argument("--no-delay", action="store_true",
                        help="no pause between moves in a single simulated game")
    return parser


def run(args: argparse.Namespace, ui: UserInterface) -> int:
    """Run the selected mode on ``ui``; return the exit code."""
    settings = Settings(alpha_beta=args.alpha_beta == "on", delay=not args.no_delay)
    app = App(ui, settings)
    try:
        if args.mode == "play":
            app.play(args.symbol, human_first=args.first == "human")
        elif args.mode == "simulate":
            app.simulate(args.games, settings.alpha_beta, settings.alpha_beta)
        elif args.mode == "compare":
            return 0 if app.compare() else 1
        else:
            app.run_menu()
    except AbortGame:
        pass
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Parse arguments, pick the interface and run; return the exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.games < 1:
        parser.error("--games must be at least 1")

    use_curses = args.ui == "curses" or (args.ui == "auto" and sys.stdout.isatty()
                                         and sys.stdin.isatty())
    try:
        if use_curses:
            return curses.wrapper(lambda screen: run(args, CursesUI(screen)))
        return run(args, ConsoleUI())
    except (EOFError, KeyboardInterrupt):
        print("\nBye!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
