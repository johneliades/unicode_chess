# -*- encoding: utf-8 -*-
import enum
import os
import math
import time
import sys
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
#fen_starting_position = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
fen_starting_position = "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"
#for bug test after promotion and checks, recursion depths -> combinations
#1 -> 44
#2 -> 1486
#3 -> 62379
#4 -> 2103487
#5 -> 89941194

pieces = {
	'P': '♙',
	'N': '♘',
	'B': '♗',
	'R': '♖',
	'Q': '♕',
	'K': '♔',
	'p': '♟',
	'n': '♞',
	'b': '♝',
	'r': '♜',
	'q': '♛',
	'k': '♚',
}

black_pieces = []
white_pieces = []

en_passant_pawn = None

debug = False

class Color(enum.Enum):
	WHITE = 0
	BLACK = 1

class chess_piece:
	def __str__(self):
		return pieces[self.fen_letter]

	def limit_check(self, values):
		return len([x for x in values if x>=0 and x<8]) == len(values)

	def is_enemy_piece(self, test_x, test_y):
		return board[test_x][test_y]!=" " and board[
			self.x][self.y].color!=board[test_x][test_y].color 

	def play_move(self, end):
		global en_passant_pawn
		global white_pieces
		global black_pieces
		global dead_piece_count

		end_x, end_y = end

		if(board[end_x][end_y] in white_pieces):
			white_pieces.remove(board[end_x][end_y])

		if(board[end_x][end_y] in black_pieces):
			black_pieces.remove(board[end_x][end_y])

		if(isinstance(board[end_x][end_y], chess_piece)):
			dead_piece_count[str(board[end_x][end_y])] += 1

		board[end_x][end_y] = board[self.x][self.y]
		board[self.x][self.y] = " "
		self.x = end_x
		self.y = end_y
		en_passant_pawn=None

class pawn(chess_piece):
	def __init__(self, color, x, y):
		global white_pieces
		global black_pieces

		self.color = color
		self.has_moved = False
		if(color == Color.WHITE):
			self.fen_letter = "P"
			self.direction = 1
			white_pieces.append(self)
		else:
			self.fen_letter = "p"
			self.direction = -1
			black_pieces.append(self)
		self.x = x
		self.y = y

	def avail_moves(self):
		moves = []

		start_x = self.x
		start_y = self.y

		# One step
		if(board[start_x-1*self.direction][start_y]==" "):
			if(start_x-1*self.direction==0 or start_x-1*self.direction==7):
				moves.append((start_x - 1*self.direction, start_y, "q"))
				moves.append((start_x - 1*self.direction, start_y, "r"))
				moves.append((start_x - 1*self.direction, start_y, "b"))
				moves.append((start_x - 1*self.direction, start_y, "n"))
			else:
				moves.append((start_x - 1*self.direction, start_y))

		# Two steps
		if(super().limit_check((start_x-2*self.direction, start_y)) and
			board[start_x-2*self.direction][start_y]==" " and
			self.has_moved == False):
			
			moves.append((start_x - 2*self.direction, start_y))

		# Kill piece left
		if(super().limit_check((start_x-1*self.direction, start_y-1)) and
			board[start_x][start_y].is_enemy_piece(start_x-1*self.direction, start_y-1)):

			if(start_x-1*self.direction==0 or start_x-1*self.direction==7):
				moves.append((start_x - 1*self.direction, start_y-1, "q"))
				moves.append((start_x - 1*self.direction, start_y-1, "r"))
				moves.append((start_x - 1*self.direction, start_y-1, "b"))
				moves.append((start_x - 1*self.direction, start_y-1, "n"))
			else:
				moves.append((start_x-1*self.direction, start_y-1))

		# Kill piece right
		if(super().limit_check((start_x-1*self.direction, start_y+1)) and
			board[start_x][start_y].is_enemy_piece(start_x-1*self.direction, start_y+1)):

			if(start_x-1*self.direction==0 or start_x-1*self.direction==7):
				moves.append((start_x - 1*self.direction, start_y+1, "q"))
				moves.append((start_x - 1*self.direction, start_y+1, "r"))
				moves.append((start_x - 1*self.direction, start_y+1, "b"))
				moves.append((start_x - 1*self.direction, start_y+1, "n"))
			else:
				moves.append((start_x-1*self.direction, start_y+1))

		# En passant left
		if(super().limit_check((start_x, start_y-1)) and
			board[start_x][start_y].is_enemy_piece(start_x, start_y-1) and
			board[start_x][start_y-1]==en_passant_pawn):

				moves.append((start_x-1*self.direction, start_y-1))

		# En passant right
		if(super().limit_check((start_x, start_y+1)) and
			board[start_x][start_y].is_enemy_piece(start_x, start_y+1) and			
			board[start_x][start_y+1]==en_passant_pawn):

				moves.append((start_x-1*self.direction, start_y+1))

		return moves

	def play_move(self, end, promotion=None):
		global en_passant_pawn
		global white_pieces
		global black_pieces

		if(len(end)==2):
			end_x, end_y = end
		else:
			end_x, end_y, promotion = end

		if(super().limit_check((self.y-1,)) and
			board[self.x][self.y-1]==en_passant_pawn and end_y==self.y-1):
			
			board[self.x][self.y-1]=" "
	
		elif(super().limit_check((self.y+1,)) and
			board[self.x][self.y+1]==en_passant_pawn and end_y==self.y+1):
			
			board[self.x][self.y+1]=" "

		if(promotion!=None):
			if(board[self.x][self.y].color == Color.WHITE):
				if(self in white_pieces):
					white_pieces.remove(self)
			else:
				if(self in black_pieces):
					black_pieces.remove(self)

		super().play_move((end_x, end_y))
		
		if(promotion!=None):
			if(promotion == "q"):
				board[end_x][end_y] = queen(board[end_x][end_y].color, end_x, end_y)
			elif(promotion == "r"):
				board[end_x][end_y] = rook(board[end_x][end_y].color, end_x, end_y)
			elif(promotion == "b"):
				board[end_x][end_y] = bishop(board[end_x][end_y].color, end_x, end_y)
			elif(promotion == "n"):
				board[end_x][end_y] = knight(board[end_x][end_y].color, end_x, end_y)

		if(end_x-2*self.direction == end_x):
			en_passant_pawn=self

		self.has_moved = True

		for move in board[end_x][end_y].avail_moves():
			if(isinstance(board[move[0]][move[1]], king)):
				board[move[0]][move[1]].in_check = True

class rook(chess_piece):
	def __init__(self, color, x, y):
		global white_pieces
		global black_pieces

		self.color = color
		if(color == Color.WHITE):
			self.fen_letter = "R"
			white_pieces.append(self)
		else:
			self.fen_letter = "r"
			black_pieces.append(self)
		self.has_moved = False
		self.x = x
		self.y = y

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

	def play_move(self, end):
		end_x, end_y = end
		super().play_move((end_x, end_y))
		self.has_moved = True

		for move in board[self.x][self.y].avail_moves():
			if(isinstance(board[move[0]][move[1]], king)):
				board[move[0]][move[1]].in_check = True

class bishop(chess_piece):
	def __init__(self, color, x, y):
		global white_pieces
		global black_pieces

		self.color = color
		if(color == Color.WHITE):
			self.fen_letter = "B"
			white_pieces.append(self)
		else:
			self.fen_letter = "b"
			black_pieces.append(self)
		self.x = x
		self.y = y

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

	def play_move(self, end):
		end_x, end_y = end

		super().play_move((end_x, end_y))

		for move in board[self.x][self.y].avail_moves():
			if(isinstance(board[move[0]][move[1]], king)):
				board[move[0]][move[1]].in_check = True

class knight(chess_piece):
	def __init__(self, color, x, y):
		global white_pieces
		global black_pieces

		self.color = color
		if(color == Color.WHITE):
			self.fen_letter = "N"
			white_pieces.append(self)
		else:
			self.fen_letter = "n"
			black_pieces.append(self)
		self.x = x
		self.y = y

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
			if(not super().limit_check((cur_x, cur_y))):
				moves.remove(cur_move)
				continue

			# Don't remove moves to empty cell
			if(board[cur_x][cur_y]==" "):
				continue

			# Remove moves on your pieces
			if board[cur_x][cur_y].color == board[self.x][ self.y].color:
				moves.remove(cur_move)

		return moves
	
	def play_move(self, end):
		end_x, end_y = end

		super().play_move((end_x, end_y))

		for move in board[self.x][self.y].avail_moves():
			if(isinstance(board[move[0]][move[1]], king)):
				board[move[0]][move[1]].in_check = True

class queen(chess_piece):
	def __init__(self, color, x, y):
		global white_pieces
		global black_pieces

		self.color = color
		if(color == Color.WHITE):
			self.fen_letter = "Q"
			white_pieces.append(self)
		else:
			self.fen_letter = "q"
			black_pieces.append(self)
		self.x = x
		self.y = y

	def avail_moves(self):
		moves = []
		moves = rook.avail_moves(self)
		moves += bishop.avail_moves(self)

		return moves
	
	def play_move(self, end):
		end_x, end_y = end

		super().play_move((end_x, end_y))

		for move in board[self.x][self.y].avail_moves():
			if(isinstance(board[move[0]][move[1]], king)):
				board[move[0]][move[1]].in_check = True

class king(chess_piece):
	def __init__(self, color, x, y):
		global white_pieces
		global black_pieces

		self.color = color
		if(color == Color.WHITE):
			self.fen_letter = "K"
			white_pieces.append(self)
		else:
			self.fen_letter = "k"
			black_pieces.append(self)
		self.has_moved = False
		self.in_check = False
		self.x = x
		self.y = y

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
			if(not super().limit_check((cur_x, cur_y))):
				moves.remove(cur_move)
				continue

			# Don't remove moves to empty cell
			if(board[cur_x][cur_y]==" "):
				continue

			# Remove moves on your pieces
			if board[cur_x][cur_y].color == board[self.x][self.y].color:
				moves.remove(cur_move)

		if(super().limit_check((self.y-1, self.y-2, self.y-3, self.y-4)) and
			board[self.x][self.y].has_moved==False and 
			board[self.x][self.y-1]==" " and
			board[self.x][self.y-2]==" " and
			board[self.x][self.y-3]==" " and
			board[self.x][self.y-4]!=" " and
			board[self.x][self.y-4].color==board[self.x][self.y].color and
			board[self.x][self.y-4].has_moved==False):
	
			moves.append((self.x, self.y-2))

		if(super().limit_check((self.y+1, self.y+2, self.y+3)) and
			board[self.x][self.y].has_moved==False and 
			board[self.x][self.y+1]==" " and
			board[self.x][self.y+2]==" " and
			board[self.x][self.y+3]!=" " and
			board[self.x][self.y+3].color==board[self.x][self.y].color and
			board[self.x][self.y+3].has_moved==False):
	
			moves.append((self.x, self.y+2))

		return moves
	
	def play_move(self, end):
		end_x, end_y = end

		if(end_y==self.y-2):
			board[self.x][self.y-4].play_move((self.x, end_y+1))
		if(end_y==self.y+2):
			board[self.x][self.y+3].play_move((self.x, end_y-1))
		super().play_move((end_x, end_y))
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
				board[row][column] = rook(Color.BLACK, row, column)
			elif(char == "R"):
				board[row][column] = rook(Color.WHITE, row, column)
			elif(char == "n"):
				board[row][column] = knight(Color.BLACK, row, column)
			elif(char == "N"):
				board[row][column] = knight(Color.WHITE, row, column)
			elif(char == "b"):
				board[row][column] = bishop(Color.BLACK, row, column)
			elif(char == "B"):
				board[row][column] = bishop(Color.WHITE, row, column)
			elif(char == "q"):
				board[row][column] = queen(Color.BLACK, row, column)
			elif(char == "Q"):
				board[row][column] = queen(Color.WHITE, row, column)
			elif(char == "k"):
				board[row][column] = king(Color.BLACK, row, column)
			elif(char == "K"):
				board[row][column] = king(Color.WHITE, row, column)
			elif(char == "p"):
				board[row][column] = pawn(Color.BLACK, row, column)
			elif(char == "P"):
				board[row][column] = pawn(Color.WHITE, row, column)

			column+=1

def display_board(start_x=None, start_y=None):
	global board

	total_white = dead_piece_count[u'♙'] + 3 *\
		(dead_piece_count[u'♘'] + dead_piece_count[u'♗']) +\
		5 * dead_piece_count[u'♖'] + 9 * dead_piece_count[u'♕']

	total_black = dead_piece_count[u'♟'] + 3 *\
		(dead_piece_count[u'♞'] + dead_piece_count[u'♝']) +\
		5 * dead_piece_count[u'♜'] + 9 * dead_piece_count[u'♛']

	w, h = shutil.get_terminal_size()
	mid = w//2 - 34//2

	print("\033[2J\033[H", end="")

	print("\n\n")

	author = "𝓒𝓱𝓮𝓼𝓼 𝓫𝔂 𝓙𝓸𝓱𝓷 𝓔𝓵𝓲𝓪𝓭𝓮𝓼"

	print(author.center(w))

	print((mid-5)*" ", end = "")
	if(total_white>total_black):
		print(total_white-total_black, end =" ")

	for pawn, count in dead_piece_count.items():
		if pawn in [u'♙', u'♖', u'♘', u'♗', u'♕']:
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

	print(letters)
	
	print((mid-5)*" ", end = "")
	if(total_black>total_white):
		print(total_black-total_white, end = " ")

	for pawn, count in dead_piece_count.items():
		if pawn in [u'♟', u'♜', u'♞', u'♝', u'♛']:
			for i in range(count):
				print(pawn, end="")

	print()

	fen = calculate_fen()

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
	global dead_piece_count

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
					if(len(move)==2):
						moves.append((piece.x, piece.y, move[0], move[1]))
					else:
						moves.append((piece.x, piece.y, move[0], move[1], move[2]))
		else:
			for piece in black_pieces:
				for move in piece.avail_moves():
					if(len(move)==2):
						moves.append((piece.x, piece.y, move[0], move[1]))
					else:
						moves.append((piece.x, piece.y, move[0], move[1], move[2]))

	except:
		display_board()
		time.sleep(100)

	for move in moves:
		board2 = deepcopy(board)
		turn = deepcopy(white_turn)
		dead_piece_count2 = deepcopy(dead_piece_count)

		if(len(move)==4):
			start_x, start_y, end_x, end_y = move
		else:
			start_x, start_y, end_x, end_y, promotion = move

		board[start_x][start_y].play_move(tuple(move[2:]))
		white_turn = not white_turn

		display_board()
		time.sleep(0.01)
		num_positions += recursion_test(depth-1)

		board = deepcopy(board2)
		white_turn = deepcopy(turn)
		dead_piece_count = deepcopy(dead_piece_count2)

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

	if(isinstance(board[start_x][start_y], pawn) and (end_x==0 or end_x==7)):
		promotion = ""
		print("(q, r, b, n): ", end= "")
		sys.stdout.flush()
		while(promotion not in ["q", "r", "b", "n"]):
			event = keyboard.read_event()
			if event.event_type == keyboard.KEY_DOWN:
				promotion = event.name
		board[start_x][start_y].play_move((end_x, end_y, promotion))
	else:
		board[start_x][start_y].play_move((end_x, end_y))

	white_turn = not white_turn

	# move_count = recursion_test(2)
	# print(move_count)
	# time.sleep(100)

def main():
	global fd

	init_board()

	while True:
		display_board()
		move()

main()