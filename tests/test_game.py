"""Tests for the game controller and players."""

import random
from typing import List, Optional, Sequence

import pytest

from tictactoe.ai.minimax import SearchResult
from tictactoe.core.board import Board, O, X
from tictactoe.core.game import Game
from tictactoe.core.players import AIPlayer, HumanPlayer, RandomPlayer
from tictactoe.ui.base import UserInterface


class FakeUI(UserInterface):
    """Feeds scripted answers and records messages."""

    def __init__(self, answers: Sequence[str]) -> None:
        self.answers = list(answers)
        self.messages: List[str] = []

    def show_board(self, board: Board) -> None:
        pass

    def ask_move(self, symbol: str) -> str:
        return self.answers.pop(0)

    def show_message(self, text: str) -> None:
        self.messages.append(text)

    def show_search_stats(self, symbol: str, result: SearchResult) -> None:
        pass

    def show_table(self, title, headers, rows) -> None:
        pass

    def begin_game(self, title: str) -> None:
        pass

    def show_report(self, title, lines) -> None:
        pass

    def pause(self) -> None:
        pass

    def choose_option(self, title: str, options: Sequence[str]) -> int:
        return 0

    def ask_int(self, prompt: str, minimum: int, maximum: int,
                default: Optional[int] = None) -> int:
        return minimum


def test_human_rejects_bad_input_then_accepts() -> None:
    board = Board.from_moves([0])
    ui = FakeUI(["abc", "", "0", "10", "1", "5"])
    move = HumanPlayer(ui).choose_move(board, O)
    assert move == 4
    assert len(ui.messages) == 5  # five rejections


def test_human_accepts_valid_input_with_spaces() -> None:
    ui = FakeUI([" 9 "])
    assert HumanPlayer(ui).choose_move(Board(), X) == 8
    assert ui.messages == []


def test_game_turn_order_and_result() -> None:
    ui = FakeUI(["1", "4", "2", "5", "3"])
    game = Game({X: HumanPlayer(ui), O: HumanPlayer(ui)})
    result = game.play()
    assert result.winner == X
    assert [m for _, m in result.moves] == [0, 3, 1, 4, 2]


def test_second_player_can_start() -> None:
    game = Game({X: RandomPlayer(random.Random(1)), O: RandomPlayer(random.Random(2))},
                first=O)
    assert game.play_turn()[0] == O


@pytest.mark.parametrize("x_ab", [True, False])
@pytest.mark.parametrize("o_ab", [True, False])
@pytest.mark.parametrize("first", [X, O])
def test_ai_vs_ai_is_always_a_draw(x_ab, o_ab, first) -> None:
    game = Game({X: AIPlayer(x_ab), O: AIPlayer(o_ab)}, first)
    assert game.play().winner is None


@pytest.mark.parametrize("ai_symbol", [X, O])
def test_ai_never_loses_to_random(ai_symbol) -> None:
    rng = random.Random(2024)
    other = O if ai_symbol == X else X
    for game_number in range(200):
        first = X if game_number % 2 == 0 else O
        players = {ai_symbol: AIPlayer(True), other: RandomPlayer(rng)}
        result = Game(players, first).play()
        assert result.winner != other
