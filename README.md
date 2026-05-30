# Unicode Chess ♔

A fully functional chess library and terminal game written in Python from
scratch, featuring Unicode piece rendering, move generation, move validation,
and FEN support.

Can also be used as a backend for a custom UCI chess engine (see
[engine.py](engine.py)) that plays online via
[chess\_cv](https://github.com/johneliades/chess_cv).

![Preview](https://github.com/johneliades/unicode_chess/blob/main/preview.png)

## Features

- **Interactive terminal game** with coloured board, move highlighting, and
  captured-piece display
- **Full chess rules** — castling, en passant, pawn promotion, 50-move rule,
  three-fold repetition, stalemate & checkmate detection
- **FEN import / export** for loading and saving positions
- **Perft testing** to verify move-generation correctness
- **Multi-undo** support

## Setup

```bash
git clone https://github.com/johneliades/unicode_chess.git
cd unicode_chess
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Play

```bash
python chess.py
```

### In-game commands

| Command   | Description                       |
|-----------|-----------------------------------|
| `e2e4`    | Move piece from e2 to e4          |
| `e7e8q`   | Promote pawn to queen             |
| `undo`    | Take back the last move           |
| `fen`     | Print the current FEN string      |
| `new`     | Start a new game                  |
| `perft N` | Run perft to depth *N*            |
| `help`    | Show available commands           |
| `quit`    | Exit                              |

## UCI Engine

Build a standalone executable:

```bash
pyinstaller --onefile engine.py
```

The resulting `engine.exe` (or `engine` on Linux) speaks the UCI protocol and
can be connected to any UCI-compatible GUI or to
[chess\_cv](https://github.com/johneliades/chess_cv).

## Author

**Eliades John** — [GitHub](https://github.com/johneliades)
