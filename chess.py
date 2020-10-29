# -*- encoding: utf-8 -*-
import enum
import os
import math
import time

global board

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
    global board

    board = (
        [
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
            [(Color.BLACK, Piece.PAWN) for _ in range(8)],
            *[[None] * 8 for _ in range(4)],
            [(Color.WHITE, Piece.PAWN) for _ in range(8)],
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
        ]
    )

def display_board(msg=""):
	global board

	os.system('cls' if os.name == 'nt' else 'clear')

	white_cell = True

	print()

	row_num = 8

	for row in board:
		columns = int(os.popen('stty size', 'r').read().split()[1]) - 16
		spaces = math.floor(columns/2) - 8
		for x in range(spaces):
			print(" ", end="")

		row_string = str(row_num) + " "
		for current in row:
			if(white_cell):
				row_string += '\033[47m' + " " + pawns[current] + "  " + '\033[0m'
			else:
				row_string += '\033[40m' + " " + pawns[current] + "  " + '\033[0m'

			white_cell = not white_cell

		print(row_string)

		white_cell = not white_cell
		row_num -= 1

	for x in range(spaces + 3):
		print(" ", end="")

	for letter in ["a", "b", "c", "d", "e", "f", "g", "h"]:
		print(letter, end="   ")

	print("\n")
	print(msg)
	print()


def is_valid(move):
	pass

def move():
	move = input(" Insert move in long algebraic notation: ")
   	
	move = [char for char in move]  
	if(len(move)!=4 or 
		ord(move[0]) not in range(ord('a'), ord('i')) or 
		ord(move[2]) not in range(ord('a'), ord('i')) or 
		int(move[1]) not in range(1, 9) or
		int(move[3]) not in range(1, 9)):
		
		return " Error: Not long algebraic notation (e.g. a2a4)"

	is_valid(move)

	return ""

def play():
	msg = ""
	while True:
		display_board(msg)
		msg = move()


init_board()
play()