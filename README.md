# tic-tac-toe-minimax

Console Tic-Tac-Toe (3×3) with an AI based on the **minimax** algorithm with optional **alpha-beta pruning**. An educational project (AI methods lab). Python standard library only; runs in Docker through a Makefile.

## Minimax in brief

The game tree is searched recursively and never stored: a move is placed, the position is evaluated, the move is undone.

- **Maximizer**: the player the move is searched for; picks the move with the highest score.
- **Minimizer**: the opponent; picks the move with the lowest score.
- **Score** (always from the maximizer's point of view) accounts for depth: win `10 - depth`, loss `depth - 10`, draw `0`. The AI therefore wins as fast as possible and loses as late as possible.
- Among moves with equal score the one with the **smallest index** is chosen. The choice is deterministic, so the modes with and without pruning return the same move.

**Alpha-beta:** `alpha` is the best score the maximizer is already guaranteed, `beta` the same for the minimizer. When `beta <= alpha`, the remaining moves of the node cannot affect the result and are skipped. The root score does not change, while the node count drops by an order of magnitude. It is the same `minimax` function with a `use_alpha_beta` flag.

**Node counting:** every call is counted, including the root; the search stops at won or full boards. Plain minimax from the empty board visits exactly **549,946** nodes (pinned by a test). There is no memoization, so the comparison is fair.

## Interface

In a terminal the program opens a full-screen curses UI: arrow-key menus (Enter to choose, digits as shortcuts, `q`/Esc to go back), a grid board with colours and a side panel with the last AI move (cell, score, nodes, time) and messages. During a game move the cursor with arrows / WASD and press Enter, or press `1`-`9`. Reports (compare, batch simulation) open in a scrollable page. Use `--ui console` (or `UI=console` in `make`) for the plain text interface; it is also selected automatically when not attached to a terminal. `make simulate` and `make compare` use the console interface by default (`REPORT_UI=curses` to change) so the output stays in the terminal.

## Project structure

```
tictactoe/
  __main__.py        # entry point, argparse
  app.py             # flows (play / simulate / compare / menu) on top of UserInterface
  settings.py        # settings (alpha-beta, delay)
  core/              # board.py, game.py, players.py: no output, no console
  ai/minimax.py      # minimax / alpha-beta, SearchResult
  modes/             # simulate.py, compare.py: logic without output
  ui/                # base.py (UserInterface), console.py, curses_ui.py, text.py (shared rendering)
tests/               # pytest
```

## Requirements

Docker, Docker Compose, make.

## Makefile commands

| Command | Action |
|---|---|
| `make help` | list commands |
| `make build` | build the image |
| `make run` | interactive menu |
| `make play` | play vs AI: `make play AB=off FIRST=ai SYMBOL=O` |
| `make simulate` | simulation: `make simulate GAMES=100 AB=on`; one step-by-step game: `GAMES=1`, no delay: `NODELAY=1` |
| `make compare` | alpha-beta comparison table |
| `make test` | pytest with coverage |
| `make lint` | flake8 |
| `make check` | lint + test |
| `make shell` | bash in the container |
| `make clean` | stop containers, remove `__pycache__` |

Without Make: `python -m tictactoe --mode play|simulate|compare [--alpha-beta on|off] [--games N] [--first human|ai] [--symbol X|O] [--no-delay] [--ui auto|console|curses]`. With no arguments the interactive menu starts.

## Example `make compare` output

```
=== Immediate win for X (to move: X) ===

 X | X | .
---+---+---
 O | O | .
---+---+---
 . | . | .

Results
Mode       | Best move | Score | Nodes | Time (ms)
-----------+-----------+-------+-------+----------
Minimax    | 3         | 9     | 157   | 0.16
Alpha-beta | 3         | 9     | 36    | 0.04
Node reduction: 77.1% | scores equal: yes | moves equal: yes
```

On the empty board: 549,946 nodes vs 20,866 (−96.2%).

## Tests and linter

```
make test    # pytest + coverage
make lint    # flake8 (max-line-length = 100)
make check   # both
```

## Adding a new interface (GUI, web)

1. Subclass `tictactoe.ui.base.UserInterface` and implement `begin_game`, `show_board`, `ask_move`, `show_message`, `show_search_stats`, `show_table`, `show_report`, `choose_option`, `ask_int`, `pause`. Raise `AbortGame` when the user leaves a screen.
2. Pass it to `App(ui, Settings())` instead of `ConsoleUI` and call `run_menu()` or a single mode.
3. The core (`core`, `ai`, `modes`) needs no changes.
