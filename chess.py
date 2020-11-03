# -*- encoding: utf-8 -*-
import enum
import os
import math
import time

global board
global white_turn

white_turn = True

class InvalidMoveException(Exception):
	pass

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

pieces = {
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
   	(None, None): " ",
}

dead_piece_count = {
    (Color.WHITE, Piece.QUEEN): 0,
    (Color.WHITE, Piece.ROOK): 0,
    (Color.WHITE, Piece.BISHOP): 0,
    (Color.WHITE, Piece.KNIGHT): 0,
    (Color.WHITE, Piece.PAWN): 0,     
    (Color.BLACK, Piece.QUEEN): 0,
    (Color.BLACK, Piece.ROOK): 0,
    (Color.BLACK, Piece.BISHOP):  0,
    (Color.BLACK, Piece.KNIGHT): 0,
    (Color.BLACK, Piece.PAWN): 0,
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
            *[[(None, None)] * 8 for _ in range(4)],
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

def display_board(error=""):
	global board

	os.system('cls' if os.name == 'nt' else 'clear')

	white_cell = True

	author = "𝓒𝓱𝓮𝓼𝓼 𝓫𝔂 𝓙𝓸𝓱𝓷 𝓔𝓵𝓲𝓪𝓭𝓮𝓼"
	author = author.center(int(os.popen('stty size', 'r').read().split()[1]))

	print()

	print(author)

	print()

	total = dead_piece_count[(Color.WHITE, Piece.PAWN)] + 3 *\
		(dead_piece_count[(Color.WHITE, Piece.KNIGHT)] + dead_piece_count[(Color.WHITE, Piece.BISHOP)]) +\
		5 * dead_piece_count[(Color.WHITE, Piece.ROOK)] + 6 * dead_piece_count[(Color.WHITE, Piece.QUEEN)]

	print(" Points: " + str(total), end=" ")

	for pawn in dead_piece_count:
		if(pawn[0] == Color.WHITE):
			print(dead_piece_count[pawn] * (" " + pieces[pawn]), end="")

	print("\n")

	row_num = 8

	for row in board:
		columns = int(os.popen('stty size', 'r').read().split()[1]) - 16
		spaces = math.floor(columns/2) - 8
		for x in range(spaces):
			print(" ", end="")

		row_string = str(row_num) + " "
		for current in row:
			if(white_cell):
				row_string += '\033[47m' + "▏" + pieces[current] + "  " + '\033[0m'
			else:
				row_string += '\033[40m' + "▏" + pieces[current] + "  " + '\033[0m'

			white_cell = not white_cell

		row_string += "▏"

		print(row_string)

		white_cell = not white_cell
		row_num -= 1

	for x in range(spaces + 3):
		print(" ", end="")

	for letter in [u'\uff41', u'\uff42', u'\uff43', u'\uff44', u'\uff45', u'\uff46', u'\uff47', u'\uff48']:
		print(letter, end="  ")

	print("\n")

	total = dead_piece_count[(Color.BLACK, Piece.PAWN)] + 3 *\
		(dead_piece_count[(Color.BLACK, Piece.KNIGHT)] + dead_piece_count[(Color.BLACK, Piece.BISHOP)]) +\
		5 * dead_piece_count[(Color.BLACK, Piece.ROOK)] + 6 * dead_piece_count[(Color.BLACK, Piece.QUEEN)]

	print(" Points: " + str(total), end=" ")

	for pawn in dead_piece_count:
		if(pawn[0] == Color.BLACK):
			print(dead_piece_count[pawn] * (" " + pieces[pawn]), end="")

	print("\n")

	print(error)
	print()

def pawn_moves():
	pass

def rook_moves(start_x, start_y, end_x, end_y):
	moves = []
	for offset_x in reversed(range(0, start_x)):
		if(board[offset_x][start_y] == (None, None)):
			moves.append((offset_x, start_y))
		elif(board[offset_x][start_y][0] != board[start_x][start_y][0]):
			moves.append((offset_x, start_y))
			break	
		else:
			break
	
	for offset_x in range(start_x+1, 8):
		if(board[offset_x][start_y] == (None, None)):
			moves.append((offset_x, start_y))
		elif(board[offset_x][start_y][0] != board[start_x][start_y][0]):
			moves.append((offset_x, start_y))
			break	
		else:
			break

	for offset_y in reversed(range(0, start_y)):
		if(board[start_x][offset_y] == (None, None)):
			moves.append((start_x, offset_y))
		elif(board[start_x][offset_y][0] != board[start_x][start_y][0]):
			moves.append((start_x, offset_y))
			break	
		else:
			break

	for offset_y in range(start_y+1, 8):
		if(board[start_x][offset_y] == (None, None)):
			moves.append((start_x, offset_y))
		elif(board[start_x][offset_y][0] != board[start_x][start_y][0]):
			moves.append((start_x, offset_y))
			break	
		else:
			break

	return moves;

def bishop_moves(start_x, start_y, end_x, end_y):
	moves = []
	for offset_x, offset_y in zip(reversed(range(0, start_x)), reversed(range(0, start_y))):
		if(board[offset_x][offset_y] == (None, None)):
			moves.append((offset_x, offset_y))
		elif(board[offset_x][offset_y][0] != board[start_x][start_y][0]):
			moves.append((offset_x, offset_y))
			break	
		else:
			break
	
	for offset_x, offset_y in zip(range(start_x+1, 8), range(start_y+1, 8)):
		if(board[offset_x][offset_y] == (None, None)):
			moves.append((offset_x, offset_y))
		elif(board[offset_x][offset_y][0] != board[start_x][start_y][0]):
			moves.append((offset_x, offset_y))
			break	
		else:
			break

	for offset_x, offset_y in zip(range(start_x+1, 8), reversed(range(0, start_y))):
		if(board[offset_x][offset_y] == (None, None)):
			moves.append((offset_x, offset_y))
		elif(board[offset_x][offset_y][0] != board[start_x][start_y][0]):
			moves.append((offset_x, offset_y))
			break	
		else:
			break

	for offset_x, offset_y in zip(reversed(range(0, start_x)), range(start_y+1, 8)):
		if(board[offset_x][offset_y] == (None, None)):
			moves.append((offset_x, offset_y))
		elif(board[offset_x][offset_y][0] != board[start_x][start_y][0]):
			moves.append((offset_x, offset_y))
			break	
		else:
			break

	return moves

def knight_moves(x, y):
	moves = [(x+2,y+1), (x-2,y+1), (x+2,y-1), (x-2,y-1), (x+1,y+2), (x-1,y+2), (x+1,y-2), (x-1,y-2)]

	return moves

def queen_moves(start_x, start_y, end_x, end_y):
	moves = []
	moves = rook_moves(start_x, start_y, end_x, end_y)
	moves += bishop_moves(start_x, start_y, end_x, end_y)

	return moves

def king_moves(x, y):
	moves = [(x+1,y), (x+1,y+1), (x+1,y-1), (x,y+1), (x,y-1), (x-1,y), (x-1,y+1), (x-1,y-1)]

	return moves

def is_valid(move):
	move = [char for char in move]

	if(len(move)!=4 or
		ord(move[0].upper()) not in range(ord('A'), ord('i')) or 
		ord(move[2].upper()) not in range(ord('A'), ord('i')) or 
		int(move[1]) not in range(1, 9) or
		int(move[3]) not in range(1, 9)):
		
		raise InvalidMoveException(" Error: Not long algebraic notation (e.g. a2a4)")
	
	try:
		int(move[1])
		int(move[3])
	except ValueError:
		raise InvalidMoveException(" Error: Not long algebraic notation (e.g. a2a4)")

	move[0] = int(ord(move[0].upper()) - ord("A"))
	move[1] = 8 - int(move[1])
	move[2] = int(ord(move[2].upper()) - ord("A"))
	move[3] = 8 - int(move[3])

	start_x = move[1]
	start_y = move[0]
	end_x = move[3]
	end_y = move[2]

	if(board[start_x][start_y]==(None, None)):
		raise InvalidMoveException(" No piece there")

	if(white_turn and board[start_x][start_y][0]!=Color.WHITE
		or not white_turn and board[start_x][start_y][0]!=Color.BLACK):
		raise InvalidMoveException(" Wrong player")

	if(start_x == end_x and start_y == end_y):
		raise InvalidMoveException(" Can't move " + pieces[board[start_x][start_y]] + "  in same location")

	if(board[start_x][start_y][0] == board[end_x][end_y][0]):
		raise InvalidMoveException(" Can't move " + pieces[board[start_x][start_y]] + "  on " +\
			pieces[board[end_x][end_y]] + " (Your piece)")

	if(board[start_x][start_y][1] == Piece.PAWN):
		pass
	elif(board[start_x][start_y][1] == Piece.ROOK):
		moves = rook_moves(start_x, start_y, end_x, end_y)
		if((end_x, end_y) not in moves):
			raise InvalidMoveException(" Can't move " + pieces[board[start_x][start_y]] + "  there")

	elif(board[start_x][start_y][1] == Piece.KNIGHT):
		moves = knight_moves(start_x, start_y)
		if((end_x, end_y) not in moves):
			raise InvalidMoveException(" Can't move " + pieces[board[start_x][start_y]] + "  there")

	elif(board[start_x][start_y][1] == Piece.BISHOP):
		moves = bishop_moves(start_x, start_y, end_x, end_y)
		if((end_x, end_y) not in moves):
			raise InvalidMoveException(" Can't move " + pieces[board[start_x][start_y]] + "  there")
		
	elif(board[start_x][start_y][1] == Piece.QUEEN):
		moves = queen_moves(start_x, start_y, end_x, end_y)
		if((end_x, end_y) not in moves):
			raise InvalidMoveException(" Can't move " + pieces[board[start_x][start_y]] + "  there")

	elif(board[start_x][start_y][1] == Piece.KING):
		moves = king_moves(start_x, start_y)
		if((end_x, end_y) not in moves):
			raise InvalidMoveException(" Can't move " + pieces[board[start_x][start_y]] + "  there")

	return [start_x, start_y, end_x, end_y]

def move():
	global white_turn

	if(white_turn):
		move = input(" Insert move in long algebraic notation (White plays): ")
	else:
		move = input(" Insert move in long algebraic notation (Black plays): ")		
	
	move = is_valid(move)
	
	start_x = move[0]
	start_y = move[1]
	end_x = move[2]
	end_y = move[3]

	try:
		dead_piece_count[board[end_x][end_y]] += 1
	except KeyError:
		pass

	board[end_x][end_y] = board[start_x][start_y]
	board[start_x][start_y] = (None, None)

	white_turn = not white_turn

def play():
	msg = ""
	while True:
		display_board(msg)
		msg = ""

		try:
			move()
		except InvalidMoveException as e:
			msg = e

init_board()
play()