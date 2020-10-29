# -*- encoding: utf-8 -*-
import enum
import board
import os
import math

class Color(enum.Enum):
    WHITE = 0
    BLACK = 1

class Piece(enum.Enum):
    EMPTY = enum.auto()
    PAWN = enum.auto()
    ROOK = enum.auto()
    KNIGHT = enum.auto()
    BISHOP = enum.auto()
    KING = enum.auto()
    QUEEN = enum.auto()

pawns = {
    (Color.WHITE, Piece.PAWN): u'♟',
    (Color.WHITE, Piece.ROOK): u'♜',
    (Color.WHITE, Piece.KNIGHT): u'♞',
    (Color.WHITE, Piece.BISHOP): u'♝',
    (Color.WHITE, Piece.KING): u'♚',
    (Color.WHITE, Piece.QUEEN): u'♛',
    (Color.BLACK, Piece.PAWN): u'♙',
    (Color.BLACK, Piece.ROOK): u'♖',
    (Color.BLACK, Piece.KNIGHT): u'♘',
    (Color.BLACK, Piece.BISHOP):  u'♗',
    (Color.BLACK, Piece.KING): u'♔',
    (Color.BLACK, Piece.QUEEN): u'♕',
    None: " ",
}

def init_board():
    return (
        [
            [
                (Color.WHITE, Piece.ROOK),
                (Color.WHITE, Piece.KNIGHT),
                (Color.WHITE, Piece.BISHOP),
                (Color.WHITE, Piece.QUEEN),
                (Color.WHITE, Piece.KING),
                (Color.WHITE, Piece.BISHOP),
                (Color.WHITE, Piece.KNIGHT),
                (Color.WHITE, Piece.ROOK),
            ],
            [(Color.WHITE, Piece.PAWN) for _ in range(8)],
            *[[None] * 8 for _ in range(4)],
            [(Color.BLACK, Piece.PAWN) for _ in range(8)],
            [
                (Color.BLACK, Piece.ROOK),
                (Color.BLACK, Piece.KNIGHT),
                (Color.BLACK, Piece.BISHOP),
                (Color.BLACK, Piece.QUEEN),
                (Color.BLACK, Piece.KING),
                (Color.BLACK, Piece.BISHOP),
                (Color.BLACK, Piece.KNIGHT),
                (Color.BLACK, Piece.ROOK),
            ],
        ]
    )

def display_board(b):
	os.system('cls' if os.name == 'nt' else 'clear')

	white_cell = True

	print()

	for row in b:
		columns = int(os.popen('stty size', 'r').read().split()[1]) - 8
		spaces = math.floor(columns/2) - 5
		for x in range(spaces):
			print(" ", end="")

		row_string = ""
		for current in row:
			if(white_cell):
				row_string += '\033[47m' + pawns[current] + " " + '\033[0m'
			else:
				row_string += '\033[40m' + pawns[current] + " " + '\033[0m'

			white_cell = not white_cell

		print(row_string)

		white_cell = not white_cell

	print()


b = init_board()
display_board(b)
