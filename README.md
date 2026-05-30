# Unicode Chess ♔

A fully functional chess library and terminal game written in Python from
scratch, featuring Unicode piece rendering, move generation, move validation,
and FEN support.

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
| `undo`    | Take back the last move           |
| `new`     | Start a new game                  |
| `perft N` | Run perft to depth *N*            |
| `help`    | Show available commands           |
| `quit`    | Exit                              |

## Author

**Eliades John** — [GitHub](https://github.com/johneliades)
