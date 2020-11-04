# -*- encoding: utf-8 -*-
import enum
import os
import math
import time

global board
global white_turn

white_turn = True

class Color(enum.Enum):
	WHITE = 0
	BLACK = 1

class pawn:
	def __init__(self, color):
		self.color = color

	def __str__(self):
		if(self.color == Color.WHITE):
			return u'♟'
		else:
			return u'♙'

	def avail_moves(self, start_x, start_y, end_x, end_y):
		moves = []

		for offset_x in range(0, 9):
			for offset_y in range(0, 9):
				moves.append((offset_x, offset_y))

		return moves

class rook:
	def __init__(self, color):
		self.color = color

	def __str__(self):
		if(self.color == Color.WHITE):
			return u'♜'
		else:
			return u'♖'

	def avail_moves(self, start_x, start_y, end_x, end_y):
		moves = []
		for offset_x in reversed(range(0, start_x)):
			if(board[offset_x][start_y] == " "):
				moves.append((offset_x, start_y))
			elif(board[offset_x][start_y].color != board[start_x][start_y].color):
				moves.append((offset_x, start_y))
				break	
			else:
				break
		
		for offset_x in range(start_x+1, 8):
			if(board[offset_x][start_y] == " "):
				moves.append((offset_x, start_y))
			elif(board[offset_x][start_y].color != board[start_x][start_y].color):
				moves.append((offset_x, start_y))
				break	
			else:
				break

		for offset_y in reversed(range(0, start_y)):
			if(board[start_x][offset_y] == " "):
				moves.append((start_x, offset_y))
			elif(board[start_x][offset_y].color != board[start_x][start_y].color):
				moves.append((start_x, offset_y))
				break	
			else:
				break

		for offset_y in range(start_y+1, 8):
			if(board[start_x][offset_y] == " "):
				moves.append((start_x, offset_y))
			elif(board[start_x][offset_y].color != board[start_x][start_y].color):
				moves.append((start_x, offset_y))
				break	
			else:
				break

		return moves;

class bishop:
	def __init__(self, color):
		self.color = color

	def __str__(self):
		if(self.color == Color.WHITE):
			return u'♝'
		else:
			return u'♗'

	def avail_moves(self, start_x, start_y, end_x, end_y):
		moves = []
		for offset_x, offset_y in zip(reversed(range(0, start_x)), reversed(range(0, start_y))):
			if(board[offset_x][offset_y] == " "):
				moves.append((offset_x, offset_y))
			elif(board[offset_x][offset_y].color != board[start_x][start_y].color):
				moves.append((offset_x, offset_y))
				break	
			else:
				break
		
		for offset_x, offset_y in zip(range(start_x+1, 8), range(start_y+1, 8)):
			if(board[offset_x][offset_y] == " "):
				moves.append((offset_x, offset_y))
			elif(board[offset_x][offset_y].color != board[start_x][start_y].color):
				moves.append((offset_x, offset_y))
				break	
			else:
				break

		for offset_x, offset_y in zip(range(start_x+1, 8), reversed(range(0, start_y))):
			if(board[offset_x][offset_y] == " "):
				moves.append((offset_x, offset_y))
			elif(board[offset_x][offset_y].color != board[start_x][start_y].color):
				moves.append((offset_x, offset_y))
				break	
			else:
				break

		for offset_x, offset_y in zip(reversed(range(0, start_x)), range(start_y+1, 8)):
			if(board[offset_x][offset_y] == " "):
				moves.append((offset_x, offset_y))
			elif(board[offset_x][offset_y].color != board[start_x][start_y].color):
				moves.append((offset_x, offset_y))
				break	
			else:
				break

		return moves

class knight:
	def __init__(self, color):
		self.color = color

	def __str__(self):
		if(self.color == Color.WHITE):
			return u'♞'
		else:
			return u'♘'

	def avail_moves(self, x, y, end_x, end_y):
		moves = [(x+2,y+1), (x-2,y+1), (x+2,y-1), (x-2,y-1), (x+1,y+2), (x-1,y+2), (x+1,y-2), (x-1,y-2)]

		return moves

class queen:
	def __init__(self, color):
		self.color = color

	def __str__(self):
		if(self.color == Color.WHITE):
			return u'♛'
		else:
			return u'♕'

	def avail_moves(self, start_x, start_y, end_x, end_y):
		moves = []
		moves = rook.avail_moves(self, start_x, start_y, end_x, end_y)
		moves += bishop.avail_moves(self, start_x, start_y, end_x, end_y)

		return moves

class king:
	def __init__(self, color):
		self.color = color

	def __str__(self):
		if(self.color == Color.WHITE):
			return u'♚'
		else:
			return u'♔'

	def avail_moves(self, x, y, end_x, end_y):
		moves = [(x+1,y), (x+1,y+1), (x+1,y-1), (x,y+1), (x,y-1), (x-1,y), (x-1,y+1), (x-1,y-1)]

		return moves

class InvalidMoveException(Exception):
	pass

dead_piece_count = {
	u'♟' : 0,
	u'♜' : 0,
	u'♞' : 0,
	u'♝' : 0,
	u'♛' : 0,
	u'♙' : 0,
	u'♖' : 0,
	u'♘' : 0,
	u'♗' : 0,
	u'♕' : 0,
}

def init_board():
	global board

	board = (
		[
			[
				rook(Color.BLACK),
				knight(Color.BLACK),
				bishop(Color.BLACK),
				queen(Color.BLACK),
				king(Color.BLACK),
				bishop(Color.BLACK),
				knight(Color.BLACK),
				rook(Color.BLACK),
			],
			[pawn(Color.BLACK) for _ in range(8)],
			*[[" "] * 8 for _ in range(4)],
			[pawn(Color.WHITE) for _ in range(8)],
			[
				rook(Color.WHITE),
				knight(Color.WHITE),
				bishop(Color.WHITE),
				queen(Color.WHITE),
				king(Color.WHITE),
				bishop(Color.WHITE),
				knight(Color.WHITE),
				rook(Color.WHITE),
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

	total = dead_piece_count[u'♟'] + 3 *\
		(dead_piece_count[u'♞'] + dead_piece_count[u'♝']) +\
		5 * dead_piece_count[u'♜'] + 6 * dead_piece_count[u'♛']

	print(" Points: " + str(total), end=" ")

	for pawn, count in dead_piece_count.items():
		if pawn in [u'♟', u'♜', u'♞', u'♝', u'♛']:
			print(count * pawn, end="")

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
				row_string += '\033[47m' + "▏" + str(current) + "  " + '\033[0m'
			else:
				row_string += '\033[40m' + "▏" + str(current) + "  " + '\033[0m'

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

	total = dead_piece_count[u'♙'] + 3 *\
		(dead_piece_count[u'♘'] + dead_piece_count[u'♗']) +\
		5 * dead_piece_count[u'♖'] + 6 * dead_piece_count[u'♕']

	print(" Points: " + str(total), end=" ")

	for pawn, count in dead_piece_count.items():
		if pawn in [u'♙', u'♖', u'♘', u'♗', u'♕']:
			print(count * pawn, end="")

	print("\n")

	print(error)
	print()

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

	if(board[start_x][start_y]==" "):
		raise InvalidMoveException(" No piece there")

	if(white_turn and board[start_x][start_y].color!=Color.WHITE
		or not white_turn and board[start_x][start_y].color!=Color.BLACK):
		raise InvalidMoveException(" Wrong player")

	if(start_x == end_x and start_y == end_y):
		raise InvalidMoveException(" Can't move " + str(board[start_x][start_y]) + "  in same location")

	if(board[end_x][end_y]!=" " and board[start_x][start_y].color == board[end_x][end_y].color):
		raise InvalidMoveException(" Can't move " + str(board[start_x][start_y]) + "  on " +\
			str(board[end_x][end_y]) + " (Your piece)")

	moves = board[start_x][start_y].avail_moves(start_x, start_y, end_x, end_y)
	if((end_x, end_y) not in moves):
		raise InvalidMoveException(" Can't move " + str(board[start_x][start_y]) + "  there")

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
		dead_piece_count[str(board[end_x][end_y])] += 1
	except KeyError:
		pass

	board[end_x][end_y] = board[start_x][start_y]
	board[start_x][start_y] = " "

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