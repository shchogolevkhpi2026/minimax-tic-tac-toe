"""AI vs AI simulations. Pure logic: nothing is printed."""

from dataclasses import dataclass
from typing import Optional

from tictactoe.core.board import O, X
from tictactoe.core.game import Game, GameResult, MoveCallback
from tictactoe.core.players import AIPlayer


@dataclass
class SimulationSummary:
    """Aggregate result of several simulated games."""

    games: int = 0
    x_wins: int = 0
    o_wins: int = 0
    draws: int = 0
    total_nodes: int = 0
    total_ms: float = 0.0


def simulate_game(x_alpha_beta: bool, o_alpha_beta: bool, first: str = X,
                  on_move: Optional[MoveCallback] = None) -> GameResult:
    """Play one AI vs AI game."""
    players = {X: AIPlayer(x_alpha_beta), O: AIPlayer(o_alpha_beta)}
    return Game(players, first).play(on_move)


def simulate_games(games: int, x_alpha_beta: bool, o_alpha_beta: bool,
                   first: str = X) -> SimulationSummary:
    """Play ``games`` AI vs AI games and aggregate wins, nodes and time."""
    summary = SimulationSummary()
    for _ in range(games):
        x_player, o_player = AIPlayer(x_alpha_beta), AIPlayer(o_alpha_beta)
        result = Game({X: x_player, O: o_player}, first).play()
        summary.games += 1
        if result.winner == X:
            summary.x_wins += 1
        elif result.winner == O:
            summary.o_wins += 1
        else:
            summary.draws += 1
        summary.total_nodes += x_player.total_nodes + o_player.total_nodes
        summary.total_ms += x_player.total_ms + o_player.total_ms
    return summary
