# -*- encoding: utf-8 -*-
import enum
import os
import math
import time
import subprocess
import numpy as np
import shutil
import keyboard
from copy import copy, deepcopy
global board
global white_turn
global fd
from colorama import Fore, Back, Style

white_turn = True
fen_starting_position = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
#fen_starting_position = "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"
#for bug test after promotion and checks, recursion depths -> combinations
#1 -> 44
#2 -> 1486
#3 -> 62379
#4 -> 2103487
#5 -> 89941194

black_pieces = []
white_pieces = []

en_passant_pawn = None

debug = False

class Color(enum.Enum):
	WHITE = 0
	BLACK = 1

class chess_piece:
	def __str__(self):
		return self.str

	def is_pos_valid(self, values):
		return len([x for x in values if x>=0 and x<8]) == len(values)

	def is_enemy_piece(self, test_x, test_y):
		return board[test_x][test_y]!=" " and board[
			self.x][self.y].color!=board[test_x][test_y].color 

	def play_move(self, end_x, end_y):
		global en_passant_pawn

		try:
			black_pieces.remove(board[end_x][end_y])
		except:
			pass

		try:
			white_pieces.remove(board[end_x][end_y])
		except:
			pass

		board[end_x][end_y] = board[self.x][self.y]
		board[self.x][self.y] = " "
		self.x = end_x
		self.y = end_y
		en_passant_pawn=None

class pawn(chess_piece):
	def __init__(self, color):
		self.color = color
		if(color == Color.WHITE):
			self.fen_letter = "P"
			self.str = u'♟'
			self.direction = 1
			self.starting_row = 6
		else:
			self.fen_letter = "p"
			self.str = u'♙'
			self.direction = -1
			self.starting_row = 1

	def avail_moves(self):
		moves = []

		start_x = self.x
		start_y = self.y

		if(board[start_x-1*self.direction][start_y]==" "):
			moves.append((start_x - 1*self.direction, start_y))
			
			if(super().is_pos_valid((start_x-2*self.direction, start_y)) and
				board[start_x-2*self.direction][start_y]==" " and
				start_x==self.starting_row):
				
				moves.append((start_x - 2*self.direction, start_y))

		if(super().is_pos_valid((start_x-1*self.direction, start_y-1)) and
			board[start_x][start_y].is_enemy_piece(start_x-1*self.direction, start_y-1)):

				moves.append((start_x-1*self.direction, start_y-1))

		if(super().is_pos_valid((start_x-1*self.direction, start_y+1)) and
			board[start_x][start_y].is_enemy_piece(start_x-1*self.direction, start_y+1)):

				moves.append((start_x-1*self.direction, start_y+1))

		if(super().is_pos_valid((start_x, start_y-1)) and
			board[start_x][start_y].is_enemy_piece(start_x, start_y-1) and
			board[start_x][start_y-1]==en_passant_pawn):

				moves.append((start_x-1*self.direction, start_y-1))

		if(super().is_pos_valid((start_x, start_y+1)) and
			board[start_x][start_y].is_enemy_piece(start_x, start_y+1) and			
			board[start_x][start_y+1]==en_passant_pawn):

				moves.append((start_x-1*self.direction, start_y+1))

		return moves

	def play_move(self, end_x, end_y):
		global en_passant_pawn

		start_x = self.x

		if(super().is_pos_valid((self.y-1,)) and
			board[self.x][self.y-1]==en_passant_pawn and end_y==self.y-1):
			board[self.x][self.y-1]=" "
			try:
				black_pieces.remove(board[end_x][end_y])
			except:
				pass

			try:
				white_pieces.remove(board[end_x][end_y])
			except:
				pass
		elif(super().is_pos_valid((self.y+1,)) and
			board[self.x][self.y+1]==en_passant_pawn and end_y==self.y+1):
			board[self.x][self.y+1]=" "
			try:
				black_pieces.remove(board[end_x][end_y])
			except:
				pass

			try:
				white_pieces.remove(board[end_x][end_y])
			except:
				pass

		super().play_move(end_x, end_y)

		if(start_x-2*self.direction == end_x):
			en_passant_pawn=self

class rook(chess_piece):
	def __init__(self, color):
		self.color = color
		if(color == Color.WHITE):
			self.fen_letter = "R"
			self.str = u'♜'
		else:
			self.fen_letter = "r"
			self.str = u'♖'
		self.has_moved = False

	def avail_moves(self):
		moves = []
		for offset_x in reversed(range(0, self.x)):
			if(board[offset_x][self.y] == " "):
				moves.append((offset_x, self.y))
			elif(board[offset_x][self.y].color != board[self.x][self.y].color):
				moves.append((offset_x, self.y))
				break	
			else:
				break
		
		for offset_x in range(self.x+1, 8):
			if(board[offset_x][self.y] == " "):
				moves.append((offset_x, self.y))
			elif(board[offset_x][self.y].color != board[self.x][self.y].color):
				moves.append((offset_x, self.y))
				break	
			else:
				break

		for offset_y in reversed(range(0, self.y)):
			if(board[self.x][offset_y] == " "):
				moves.append((self.x, offset_y))
			elif(board[self.x][offset_y].color != board[self.x][self.y].color):
				moves.append((self.x, offset_y))
				break	
			else:
				break

		for offset_y in range(self.y+1, 8):
			if(board[self.x][offset_y] == " "):
				moves.append((self.x, offset_y))
			elif(board[self.x][offset_y].color != board[self.x][self.y].color):
				moves.append((self.x, offset_y))
				break	
			else:
				break

		return moves;

	def play_move(self, end_x, end_y):
		super().play_move(end_x, end_y)
		self.has_moved = True

class bishop(chess_piece):
	def __init__(self, color):
		self.color = color
		if(color == Color.WHITE):
			self.fen_letter = "B"
			self.str = u'♝'
		else:
			self.fen_letter = "b"
			self.str = u'♗'

	def avail_moves(self):
		moves = []
		for offset_x, offset_y in zip(reversed(range(0, self.x)), reversed(range(0, self.y))):
			if(board[offset_x][offset_y] == " "):
				moves.append((offset_x, offset_y))
			elif(board[offset_x][offset_y].color != board[self.x][self.y].color):
				moves.append((offset_x, offset_y))
				break	
			else:
				break
		
		for offset_x, offset_y in zip(range(self.x+1, 8), range(self.y+1, 8)):
			if(board[offset_x][offset_y] == " "):
				moves.append((offset_x, offset_y))
			elif(board[offset_x][offset_y].color != board[self.x][self.y].color):
				moves.append((offset_x, offset_y))
				break	
			else:
				break

		for offset_x, offset_y in zip(range(self.x+1, 8), reversed(range(0, self.y))):
			if(board[offset_x][offset_y] == " "):
				moves.append((offset_x, offset_y))
			elif(board[offset_x][offset_y].color != board[self.x][self.y].color):
				moves.append((offset_x, offset_y))
				break	
			else:
				break

		for offset_x, offset_y in zip(reversed(range(0, self.x)), range(self.y+1, 8)):
			if(board[offset_x][offset_y] == " "):
				moves.append((offset_x, offset_y))
			elif(board[offset_x][offset_y].color != board[self.x][self.y].color):
				moves.append((offset_x, offset_y))
				break	
			else:
				break

		return moves

	def play_move(self, end_x, end_y):
		super().play_move(end_x, end_y)

class knight(chess_piece):
	def __init__(self, color):
		self.color = color
		if(color == Color.WHITE):
			self.fen_letter = "N"
			self.str = u'♞'
		else:
			self.fen_letter = "n"
			self.str = u'♘'

	def avail_moves(self):
		moves = [(self.x+2, self.y+1), 
				(self.x-2, self.y+1), 
				(self.x+2, self.y-1), 
				(self.x-2, self.y-1), 
				(self.x+1, self.y+2), 
				(self.x-1, self.y+2), 
				(self.x+1, self.y-2), 
				(self.x-1, self.y-2)]
		
		for cur_move in reversed(moves):
			cur_x = cur_move[0]
			cur_y = cur_move[1]

			# Remove out of range moves
			if(not super().is_pos_valid((cur_x, cur_y))):
				moves.remove(cur_move)
				continue

			# Don't remove moves to empty cell
			if(board[cur_x][cur_y]==" "):
				continue

			# Remove moves on your pieces
			if board[cur_x][cur_y].color == board[self.x][ self.y].color:
				moves.remove(cur_move)

		return moves
	
	def play_move(self, end_x, end_y):
		super().play_move(end_x, end_y)

class queen(chess_piece):
	def __init__(self, color):
		self.color = color
		if(color == Color.WHITE):
			self.fen_letter = "Q"
			self.str = u'♛'
		else:
			self.fen_letter = "q"
			self.str = u'♕'

	def avail_moves(self):
		moves = []
		moves = rook.avail_moves(self)
		moves += bishop.avail_moves(self)

		return moves
	
	def play_move(self, end_x, end_y):
		super().play_move(end_x, end_y)

class king(chess_piece):
	def __init__(self, color):
		self.color = color
		if(color == Color.WHITE):
			self.fen_letter = "K"
			self.str = u'♚'
		else:
			self.fen_letter = "k"
			self.str = u'♔'
		self.has_moved = False

	def avail_moves(self):
		moves = [(self.x+1, self.y), 
				(self.x+1, self.y+1), 
				(self.x+1, self.y-1), 
				(self.x, self.y+1), 
				(self.x, self.y-1), 
				(self.x-1, self.y),
				(self.x-1, self.y+1), 
				(self.x-1, self.y-1)]
	
		for cur_move in reversed(moves):
			cur_x = cur_move[0]
			cur_y = cur_move[1]

			# Remove out of range moves
			if(not super().is_pos_valid((cur_x, cur_y))):
				moves.remove(cur_move)
				continue

			# Don't remove moves to empty cell
			if(board[cur_x][cur_y]==" "):
				continue

			# Remove moves on your pieces
			if board[cur_x][cur_y].color == board[self.x][self.y].color:
				moves.remove(cur_move)

		if(super().is_pos_valid((self.y-1, self.y-2, self.y-3, self.y-4)) and
			board[self.x][self.y].has_moved==False and 
			board[self.x][self.y-1]==" " and
			board[self.x][self.y-2]==" " and
			board[self.x][self.y-3]==" " and
			board[self.x][self.y-4]!=" " and
			board[self.x][self.y-4].color==board[self.x][self.y].color and
			board[self.x][self.y-4].has_moved==False):
	
			moves.append((self.x, self.y-2))

		if(super().is_pos_valid((self.y+1, self.y+2, self.y+3)) and
			board[self.x][self.y].has_moved==False and 
			board[self.x][self.y+1]==" " and
			board[self.x][self.y+2]==" " and
			board[self.x][self.y+3]!=" " and
			board[self.x][self.y+3].color==board[self.x][self.y].color and
			board[self.x][self.y+3].has_moved==False):
	
			moves.append((self.x, self.y+2))

		return moves
	
	def play_move(self, end_x, end_y):
		if(end_y==self.y-2):
			board[self.x][self.y-4].play_move(self.x, end_y+1)
		if(end_y==self.y+2):
			board[self.x][self.y+3].play_move(self.x, end_y-1)
		super().play_move(end_x, end_y)
		self.has_moved = True

class InvalidMoveException(Exception):
	pass

dead_piece_count = {
	u'♛' : 0,
	u'♜' : 0,
	u'♝' : 0,
	u'♞' : 0,
	u'♟' : 0,
	u'♕' : 0,
	u'♖' : 0,
	u'♗' : 0,
	u'♘' : 0,
	u'♙' : 0,
}

def calculate_fen():
	fen = ""
	empty_cells = 0

	for row in board:
		for current_cell in row:
			if(current_cell==" "):
				empty_cells+=1

			if(issubclass(type(current_cell), chess_piece)):
				if(empty_cells!=0):
					fen+=str(empty_cells)
					empty_cells=0
				fen+=current_cell.fen_letter

		if(empty_cells!=0):
			fen+=str(empty_cells)
			empty_cells=0
		
		fen+="/"

	fen = fen[:-1]

	if(white_turn):
		fen += " " + "w"
	else:
		fen += " " + "b"

	return fen

def init_board():
	global board
	global white_turn
	
	board = np.zeros((8, 8), dtype = chess_piece) 

	row = 0
	column = 0

	split_fen = fen_starting_position.split()
	position = split_fen[0]
	if(split_fen[1]=="w"):
		white_turn = True
	else:
		white_turn = False
	
	for char in position:
		if(char.isdigit()):
			for i in range(int(char)):
				board[row][column]=" "
				column+=1
		elif(char=="/"):
			row+=1
			column=0
		else:
			if(char == "r"):
				board[row][column] = rook(Color.BLACK)
			elif(char == "R"):
				board[row][column] = rook(Color.WHITE)
			elif(char == "n"):
				board[row][column] = knight(Color.BLACK)
			elif(char == "N"):
				board[row][column] =knight(Color.WHITE)
			elif(char == "b"):
				board[row][column] = bishop(Color.BLACK)
			elif(char == "B"):
				board[row][column] = bishop(Color.WHITE)
			elif(char == "q"):
				board[row][column] = queen(Color.BLACK)
			elif(char == "Q"):
				board[row][column] = queen(Color.WHITE)
			elif(char == "k"):
				board[row][column] = king(Color.BLACK)
			elif(char == "K"):
				board[row][column] = king(Color.WHITE)
			elif(char == "p"):
				board[row][column] = pawn(Color.BLACK)
			elif(char == "P"):
				board[row][column] = pawn(Color.WHITE)

			if(char.isupper()):
				white_pieces.append(board[row][column])
			else:
				black_pieces.append(board[row][column])

			board[row][column].x = row
			board[row][column].y = column
			column+=1

def display_board(start_x=None, start_y=None):
	global board

	w, h = shutil.get_terminal_size()
	mid = w//2 - 34//2

	print("\033[2J\033[H", end="")

	print("\n\n")

	author = "𝓒𝓱𝓮𝓼𝓼 𝓫𝔂 𝓙𝓸𝓱𝓷 𝓔𝓵𝓲𝓪𝓭𝓮𝓼"

	print(author.center(w))

	total = dead_piece_count[u'♟'] + 3 *\
		(dead_piece_count[u'♞'] + dead_piece_count[u'♝']) +\
		5 * dead_piece_count[u'♜'] + 6 * dead_piece_count[u'♛']

	total = (mid-10)*" " + "Points: " + str(total)

	print(total, end =" ")

	for pawn, count in dead_piece_count.items():
		if pawn in [u'♟', u'♜', u'♞', u'♝', u'♛']:
			for i in range(count):
				print(pawn, end="")

	print()

	row_num = 8
	
	if(start_x!=None and start_y!=None):
		moves = board[start_x][start_y].avail_moves()

	for i, row in enumerate(board):
		cur_string = mid*" " + str(row_num) + " "

		for j, current in enumerate(row):
			if (i + j) % 2 == 0:
				bg_color = '\x1b[48;5;233m'  # gray
			else:
				bg_color = '\x1b[40m'  # black

			if(i==start_x and j==start_y):
				cur_string += Back.LIGHTCYAN_EX + " " + str(current) + " " + Style.RESET_ALL
			elif(start_x!=None and start_y!=None and (i, j) in moves):
				try:
					if(board[start_x][start_y].color!=board[i][j].color):
						cur_string +=  Back.LIGHTRED_EX + " " + str(current) + " " + Style.RESET_ALL
				except:
					cur_string += Back.CYAN + " " + str(current) + " " + Style.RESET_ALL	
			else:
				cur_string += bg_color + " " + str(current) + " " + Style.RESET_ALL

		print(cur_string)

		row_num -= 1

	letters = mid*" " + "   "
	for letter in ["a", "b", "c", "d", "e", "f", "g", "h"]:
		letters += letter + "  "

	letters += "   "

	x = w//2 - len(letters)//2
	print(letters)

	total = dead_piece_count[u'♙'] + 3 *\
		(dead_piece_count[u'♘'] + dead_piece_count[u'♗']) +\
		5 * dead_piece_count[u'♖'] + 6 * dead_piece_count[u'♕']

	total = (mid-10)*" " + "Points: " + str(total)
	x = 4
	
	print(total, end =" ")

	x = 4 + len(total) + 1
	for pawn, count in dead_piece_count.items():
		if pawn in [u'♙', u'♖', u'♘', u'♗', u'♕']:
			for i in range(count):
				print(pawn, end="")
				x += 2

	print()

	fen = calculate_fen()

	x = w//2 - len("FEN: " + fen)//2 - 3
	print("\n" + (mid-15)*" " + "FEN: " + fen + "\n")

	if(debug):
		test = 23
		for piece in black_pieces:
			stdscr.addstr(test, 0, str(piece) + " " + str(piece.avail_moves()))
			test+=1

			stdscr.refresh()

		test = 23
		for piece in white_pieces:
			stdscr.addstr(test, w//2, str(piece) + " " + str(piece.avail_moves()))
			test+=1

			stdscr.refresh()

def is_move_valid(move):
	if(len(move)==0):
		return None

	move = [char for char in move]

	if(ord(move[0].upper()) not in range(ord('A'), ord('i'))):
		raise InvalidMoveException("Error: Give long algebraic notation")
	start_y = int(ord(move[0].upper()) - ord("A"))

	if(len(move)<2):
		return None
	
	try:
		int(move[1])
	except:
		raise InvalidMoveException("Error: Give long algebraic notation")
	
	if(int(move[1]) not in range(1, 9)):
		raise InvalidMoveException("Error: Give long algebraic notation")

	start_x = 8 - int(move[1])
	
	try:
		board[start_x][start_y]
	except:
		raise InvalidMoveException("Error: Give long algebraic notation")

	if(board[start_x][start_y]==" "):
		raise InvalidMoveException("Error: No piece there")

	if(white_turn and board[start_x][start_y].color!=Color.WHITE):
		raise InvalidMoveException("Error: White plays")
	elif(not white_turn and board[start_x][start_y].color!=Color.BLACK):
		raise InvalidMoveException("Error: Black plays")

	display_board(start_x, start_y)

	if(len(move)<3):
		return None

	if(ord(move[2].upper()) not in range(ord('A'), ord('i'))):
		raise InvalidMoveException("Error: Give long algebraic notation")
	end_y = int(ord(move[2].upper()) - ord("A"))

	if(len(move)<4):
		return None
	
	try:
		int(move[3])
	except:
		raise InvalidMoveException("Error: Give long algebraic notation")

	if(int(move[3]) not in range(1, 9)):
		raise InvalidMoveException("Error: Give long algebraic notation")

	end_x = 8 - int(move[3])

	try:
		board[end_x][end_y]
	except:
		raise InvalidMoveException("Error: Give long algebraic notation")

	if(start_x == end_x and start_y == end_y):
		raise InvalidMoveException(" ")

	if(board[end_x][end_y]!=" " and board[start_x][start_y].color == board[end_x][end_y].color):
		raise InvalidMoveException("Error: Can't move " + str(board[start_x][start_y]) + "  on " +\
			str(board[end_x][end_y]) + " (Your piece)")

	moves = board[start_x][start_y].avail_moves()
	if((end_x, end_y) not in moves):
		raise InvalidMoveException("Error: Can't move " + str(board[start_x][start_y]) 
			+ "  there")

	return [start_x, start_y, end_x, end_y]

def recursion_test(depth):
	global board
	global white_turn
	global white_pieces
	global black_pieces

	if(depth==0):
		return 1

	num_positions = 0

	moves = []

	white_pieces = []

	for row in board:
		for column in row:
			if(column!=" " and column.color==Color.WHITE):
				white_pieces.append(column)

	black_pieces = []

	for row in board:
		for column in row:
			if(column!=" " and column.color==Color.BLACK):
				black_pieces.append(column)

	try:
		if(white_turn):
			for piece in white_pieces:
				for move in piece.avail_moves():
					moves.append((piece.x, piece.y, move[0], move[1]))
		else:
			for piece in black_pieces:
				for move in piece.avail_moves():
					moves.append((piece.x, piece.y, move[0], move[1]))
	except:
		display_board()
		time.sleep(100)

	for move in moves:
		board2 = deepcopy(board)
		turn = deepcopy(white_turn)

		start_x, start_y, end_x, end_y = move

		board[start_x][start_y].play_move(end_x, end_y)
		white_turn = not white_turn

		display_board()
		time.sleep(0.01)
		num_positions += recursion_test(depth-1)

		board = deepcopy(board2)
		white_turn = deepcopy(turn)

	return num_positions

def move():
	global white_turn
	global board
	global white_pieces
	global black_pieces

	w, h = shutil.get_terminal_size()

	move = []
	y=21
	i=0

	move = ""
	while(len(move)!=4):
		event = keyboard.read_event()
		if event.event_type == keyboard.KEY_DOWN:
			move += event.name

		try:
			is_move_valid(move)
		except Exception as e:
			display_board()
			print("\r" + str(e), end= "")
			move = ""

	valid_move = is_move_valid(move)

	start_x = valid_move[0]
	start_y = valid_move[1]
	end_x = valid_move[2]
	end_y = valid_move[3]
	try:
		dead_piece_count[str(board[end_x][end_y])] += 1
	except KeyError:
		pass

	board[start_x][start_y].play_move(end_x, end_y)

	white_turn = not white_turn

	# move_count = recursion_test(1)
	# print(move_count)
	# time.sleep(100)

def main():
	global fd

	init_board()

	while True:
		display_board()
		move()

main()