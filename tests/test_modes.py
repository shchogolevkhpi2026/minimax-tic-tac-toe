"""Tests for the simulate and compare modes and the CLI."""

from tictactoe.__main__ import main
from tictactoe.core.board import Board, X
from tictactoe.modes.compare import compare_all, compare_position
from tictactoe.modes.simulate import simulate_game, simulate_games


def test_compare_rows_agree() -> None:
    rows = compare_all()
    assert len(rows) >= 6
    for row in rows:
        assert row.scores_match
        assert row.moves_match
        assert row.pruned.nodes <= row.plain.nodes
        assert 0 <= row.reduction_percent < 100


def test_compare_win_and_block_positions() -> None:
    win = compare_position("win", Board.from_moves([0, 3, 1, 4]))
    assert win.plain.move == 2 and win.plain.score == 9
    block = compare_position("block", Board.from_moves([0, 4, 1]))
    assert block.plain.move == 2


def test_simulate_games_are_draws() -> None:
    summary = simulate_games(3, True, True)
    assert (summary.games, summary.draws) == (3, 3)
    assert summary.x_wins == summary.o_wins == 0
    assert summary.total_nodes > 0


def test_simulate_game_reports_moves() -> None:
    seen = []
    result = simulate_game(True, True, X, on_move=lambda s, m, p: seen.append((s, m)))
    assert seen == result.moves


def test_cli_compare_exit_code(capsys) -> None:
    assert main(["--mode", "compare"]) == 0
    assert "Node reduction" in capsys.readouterr().out


def test_cli_simulate_summary(capsys) -> None:
    assert main(["--mode", "simulate", "--games", "2"]) == 0
    assert "Draws" in capsys.readouterr().out


def test_cli_console_play_quits_cleanly(monkeypatch, capsys) -> None:
    answers = iter(["x", "5", "1", "9", "3", "2", "4", "6", "7", "8"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    assert main(["--ui", "console", "--mode", "play"]) == 0
    assert "Please enter a number" in capsys.readouterr().out
