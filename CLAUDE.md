# CLAUDE.md

## Purpose
Educational console tic-tac-toe with a minimax AI (optional alpha-beta pruning). Runs in Docker via Makefile. Runtime: stdlib only.

## Architecture rules
- `core/`, `ai/`, `modes/` never print and never read the console. All user interaction goes through `ui.base.UserInterface`.
- `HumanPlayer` gets input only via `UserInterface.ask_move`; never call `input()` or `curses` outside `ui/console.py` / `ui/curses_ui.py`. Text shared by interfaces lives in `ui/text.py`.
- No memoization in `minimax` — node counts of plain minimax and alpha-beta must stay comparable. Full tree from the empty board = 549 946 nodes (root counted); `tests/test_minimax.py` pins it.
- Scores are from the searching player's view: win `10 - depth`, loss `depth - 10`, draw `0`. Ties resolve to the smallest cell index.
- One `minimax` function serves both modes (`use_alpha_beta` flag); do not duplicate game rules.

## Commands
- `make check` (lint + tests) before every commit.
- `make build`, `make run`, `make play`, `make simulate`, `make compare`, `make shell`, `make clean`.

## Style
flake8 clean (max line 100), type hints, docstrings, English identifiers/comments/UI text. README is in Ukrainian.

## Extending
- **New mode:** put logic (no output) in `modes/<name>.py` returning data; add a flow in `app.py` that renders it via `UserInterface`; add a choice to `--mode` in `__main__.py` and a Makefile target; add tests in `tests/test_modes.py`.
- **New interface:** subclass `UserInterface` (see README), pass it to `App`. No core changes.
