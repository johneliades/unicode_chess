# unicode_chess

A fully functional chess library for Python from scratch, with move generation, 
move validation, and support for common formats(like python-chess). Can be used 
in addition to https://github.com/johneliades/chess_cv to create a custom chess 
engine bot that plays online in order to find its ranking. E.g: engine.py

![Image of chess](https://github.com/johneliades/unicode_chess/blob/main/preview.png)

## Clone

Clone the repository locally by entering the following command:
```
git clone https://github.com/johneliades/unicode_chess.git
```
Or by clicking on the green "Clone or download" button on top and then 
decompressing the zip.

Windows
```
python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt && deactivate
```

Linux
```
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && deactivate
```

## Run

Then you can run:

```
.venv\Scripts\activate (or "source .venv/bin/activate" for linux)
pyinstaller --onefile engine.py
```

To create an engine.exe executable linked to the library that communicates
via the uci protocol with chess_cv(see above) to transfer the moves of
the bot to an online chess site like chess.com or lichess.org.

## Author

**Eliades John** - *Developer* - [Github](https://github.com/johneliades)
