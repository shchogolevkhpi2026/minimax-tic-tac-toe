"""Application flows (play, simulate, compare, menu) built on ``UserInterface``."""

import time
from typing import Callable

from tictactoe.core.board import O, X, Board, opponent
from tictactoe.core.game import Game, GameResult
from tictactoe.core.players import AIPlayer, HumanPlayer, Player
from tictactoe.modes.compare import compare_all
from tictactoe.modes.simulate import simulate_game, simulate_games
from tictactoe.settings import Settings
from tictactoe.ui.base import AbortGame, UserInterface
from tictactoe.ui.text import board_lines, table_lines

STEP_DELAY_SECONDS = 0.7
TITLE = "Tic-tac-toe minimax"


def on_off(value: bool) -> str:
    """Format a boolean as ON / OFF."""
    return "ON" if value else "OFF"


class App:
    """Ties the settings, the interface and the game modes together."""

    def __init__(self, ui: UserInterface, settings: Settings,
                 sleep: Callable[[float], None] = time.sleep) -> None:
        """Create the app; ``sleep`` can be replaced in tests."""
        self.ui = ui
        self.settings = settings
        self._sleep = sleep

    # ----- play -----------------------------------------------------------------

    def play(self, human_symbol: str, human_first: bool) -> GameResult:
        """Play one game of a human against the AI."""
        ai_symbol = opponent(human_symbol)
        ai = AIPlayer(self.settings.alpha_beta)
        players: dict = {human_symbol: HumanPlayer(self.ui), ai_symbol: ai}
        first = human_symbol if human_first else ai_symbol

        self.ui.begin_game(f"Play vs AI - alpha-beta {on_off(self.settings.alpha_beta)}")
        self.ui.show_message(f"You are {human_symbol}, AI is {ai_symbol}.")
        game = Game(players, first)
        self.ui.show_board(game.board)

        def after_move(symbol: str, move: int, player: Player) -> None:
            if player is ai and ai.last_result is not None:
                self.ui.show_search_stats(symbol, ai.last_result)
            self.ui.show_board(game.board)

        result = game.play(after_move)
        if result.winner == human_symbol:
            self.ui.show_message("You win!")
        elif result.winner == ai_symbol:
            self.ui.show_message("AI wins!")
        else:
            self.ui.show_message("It's a draw.")
        self.ui.pause()
        return result

    def play_interactive(self) -> None:
        """Ask for the symbol and the first player, then play."""
        symbol = (X, O)[self.ui.choose_option("Choose your symbol", ["X", "O"])]
        first = self.ui.choose_option("Who moves first?", ["Human", "AI"])
        self.play(symbol, human_first=first == 0)

    # ----- simulate -------------------------------------------------------------

    def simulate(self, games: int, x_alpha_beta: bool, o_alpha_beta: bool) -> None:
        """Run one visible game (``games == 1``) or a batch with a summary."""
        title = (f"AI X (alpha-beta {on_off(x_alpha_beta)}) vs "
                 f"AI O (alpha-beta {on_off(o_alpha_beta)})")
        if games == 1:
            self._simulate_visible(title, x_alpha_beta, o_alpha_beta)
            return

        summary = simulate_games(games, x_alpha_beta, o_alpha_beta)
        lines = [title, ""] + table_lines(
            ["X wins", "O wins", "Draws", "Total nodes", "Total time (ms)"],
            [[summary.x_wins, summary.o_wins, summary.draws,
              summary.total_nodes, f"{summary.total_ms:.1f}"]])
        self.ui.show_report(f"Simulation of {summary.games} games", lines)

    def _simulate_visible(self, title: str, x_alpha_beta: bool, o_alpha_beta: bool) -> None:
        self.ui.begin_game(title)
        board = Board()
        self.ui.show_board(board)

        def after_move(symbol: str, move: int, player: Player) -> None:
            board.place(move, symbol)
            self.ui.show_message(f"{symbol} -> cell {move + 1}")
            self.ui.show_board(board)
            if self.settings.delay:
                self._sleep(STEP_DELAY_SECONDS)

        result = simulate_game(x_alpha_beta, o_alpha_beta, on_move=after_move)
        self.ui.show_message("Draw." if result.winner is None else f"{result.winner} wins.")
        self.ui.pause()

    def simulate_interactive(self) -> None:
        """Ask for simulation options, then run it."""
        x_ab = self.ui.choose_option("Alpha-beta for X", ["On", "Off"]) == 0
        o_ab = self.ui.choose_option("Alpha-beta for O", ["On", "Off"]) == 0
        mode = self.ui.choose_option("Mode", ["One game, step by step", "Many games"])
        games = 1 if mode == 0 else self.ui.ask_int("Number of games", 1, 10000, 10)
        self.simulate(games, x_ab, o_ab)

    # ----- compare --------------------------------------------------------------

    def compare(self) -> bool:
        """Show the plain vs alpha-beta table for every position.

        Returns True if scores and moves agree everywhere.
        """
        all_ok = True
        lines = []
        for row in compare_all():
            lines += ["", f"=== {row.name} (to move: {row.player}) ===", ""]
            lines += board_lines(row.board) + [""]
            lines += table_lines(
                ["Mode", "Best move", "Score", "Nodes", "Time (ms)"],
                [[label, r.move + 1, r.score, r.nodes, f"{r.elapsed_ms:.2f}"]
                 for label, r in (("Minimax", row.plain), ("Alpha-beta", row.pruned))])
            lines.append(
                f"Node reduction: {row.reduction_percent:.1f}% | "
                f"scores equal: {'yes' if row.scores_match else 'NO'} | "
                f"moves equal: {'yes' if row.moves_match else 'NO'}")
            all_ok = all_ok and row.scores_match and row.moves_match
        lines += ["", "All positions: both modes give the same score and move."
                  if all_ok else "MISMATCH between modes found!"]
        self.ui.show_report("Compare alpha-beta", lines)
        return all_ok

    # ----- settings / menu ------------------------------------------------------

    def settings_menu(self) -> None:
        """Let the user toggle settings."""
        while True:
            choice = self.ui.choose_option("Settings", [
                f"Alpha-beta for Play: {on_off(self.settings.alpha_beta)} (toggle)",
                f"Delay in simulation: {on_off(self.settings.delay)} (toggle)",
                "Back",
            ])
            if choice == 0:
                self.settings.alpha_beta = not self.settings.alpha_beta
            elif choice == 1:
                self.settings.delay = not self.settings.delay
            else:
                return

    def run_menu(self) -> None:
        """Main interactive loop; Esc / q inside a screen returns to the menu."""
        actions = [self.play_interactive, self.simulate_interactive, self.compare,
                   self.settings_menu]
        while True:
            try:
                choice = self.ui.choose_option(
                    f"{TITLE}  [alpha-beta: {on_off(self.settings.alpha_beta)}, "
                    f"delay: {on_off(self.settings.delay)}]",
                    ["Play vs AI", "Simulate AI vs AI", "Compare alpha-beta",
                     "Settings", "Exit"])
            except AbortGame:
                return
            if choice == len(actions):
                self.ui.show_message("Bye!")
                return
            try:
                actions[choice]()
            except AbortGame:
                continue
