# -*- encoding: utf-8 -*-
import os
import math
import time
import sys
import subprocess
import numpy as np
import shutil
import keyboard
import traceback
from enum import IntEnum
from copy import copy, deepcopy
from colorama import Fore, Back, Style

class BoardState:
	def __init__(self, board, white_turn, kings, 
		is_check, en_passant_pawn, half_move, full_move, dead_piece_count):
		
		self.board = board
		self.white_turn = white_turn
		self.kings = kings
		self.is_check = is_check
		self.en_passant_pawn = en_passant_pawn
		self.half_move = half_move
		self.full_move = full_move
		self.dead_piece_count = dead_piece_count

class Board:
	def __init__(self, fen = None):	
		self.board = np.zeros((8, 8), dtype = Chess_piece) 
		self.white_turn = True
		self.kings = [None, None] # kings[0] is black kings[1] is white
		self.is_check = False
		# self.is_checkmate = False
		# self.is_stalemate = False
		# self.is_draw = False
		self.previous_state = None
		self.en_passant_pawn = None
		self.half_move = 0
		self.full_move = 1
		self.dead_piece_count = {
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

		if(fen != None):
			self.set_fen(fen)
		else:
			self.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

	def undo_last_move(self):
		if self.previous_state is not None:
			# Restore the previous board state.
			self.board = self.previous_state.board
			self.white_turn = self.previous_state.white_turn
			self.kings = self.previous_state.kings
			self.is_check = self.previous_state.is_check
			self.en_passant_pawn = self.previous_state.en_passant_pawn
			self.half_move = self.previous_state.half_move
			self.full_move = self.previous_state.full_move
			self.dead_piece_count = self.previous_state.dead_piece_count
			self.previous_state = None  # Clear the previous state.

	def display(self, start_x=None, start_y=None):
		w, h = shutil.get_terminal_size()
		mid = w//2 - 34//2

		print("\033[2J\033[H", end="")

		print("\n\n")

		author = "𝓒𝓱𝓮𝓼𝓼 𝓫𝔂 𝓙𝓸𝓱𝓷 𝓔𝓵𝓲𝓪𝓭𝓮𝓼"

		print(author.center(w))

		print((mid-5)*" ", end = "")
		for pawn, count in self.dead_piece_count.items():
			if pawn in [u'♙', u'♖', u'♘', u'♗', u'♕']:
				for i in range(count):
					print(pawn, end="")

		print()

		row_num = 8
		
		if(start_x!=None and start_y!=None):
			moves = self.board[start_x][start_y].avail_moves()
			moves = [(x[0], x[1]) for x in moves]

		for i, row in enumerate(self.board):
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
						if(self.board[start_x][start_y].color!=self.board[i][j].color):
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
		for pawn, count in self.dead_piece_count.items():
			if pawn in [u'♟', u'♜', u'♞', u'♝', u'♛']:
				for i in range(count):
					print(pawn, end="")

		print()

		fen = self.get_fen()

		print("\n" + (mid-15)*" " + "FEN: " + fen + "\n")

	def notation_to_coordinates(self, notation, is_rotated):
		column_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
		column = column_map[notation[0]]
		row = int(notation[1])-1
		if is_rotated:
			column = 7 - column
			row = row
		else:
			column = column
			row = 7 - row
		
		return row, column

	def coordinates_to_notation(self, row, column, is_rotated):
		column_map = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
		if is_rotated:
			row = 0 + row
			column = column_map[7 - column]
		else:
			row = 7 - row
			column = column_map[column]
		
		return f"{column}{row+1}"

	def set_fen(self, fen):
		row = 0
		column = 0

		split_fen = fen.split()
		position = split_fen[0]
		if(split_fen[1]=="w"):
			self.white_turn = True
		else:
			self.white_turn = False

		for char in position:
			if(char.isdigit()):
				for i in range(int(char)):
					self.board[row][column]=" "
					column+=1
			elif(char=="/"):
				row+=1
				column=0
			else:
				if(char == "r"):
					self.board[row][column] = Rook(Color.BLACK, row, column, self)
				elif(char == "R"):
					self.board[row][column] = Rook(Color.WHITE, row, column, self)
				elif(char == "n"):
					self.board[row][column] = Knight(Color.BLACK, row, column, self)
				elif(char == "N"):
					self.board[row][column] = Knight(Color.WHITE, row, column, self)
				elif(char == "b"):
					self.board[row][column] = Bishop(Color.BLACK, row, column, self)
				elif(char == "B"):
					self.board[row][column] = Bishop(Color.WHITE, row, column, self)
				elif(char == "q"):
					self.board[row][column] = Queen(Color.BLACK, row, column, self)
				elif(char == "Q"):
					self.board[row][column] = Queen(Color.WHITE, row, column, self)
				elif(char == "k"):
					self.board[row][column] = King(Color.BLACK, row, column, self)
					self.kings[0] = self.board[row][column]
				elif(char == "K"):
					self.board[row][column] = King(Color.WHITE, row, column, self)
					self.kings[1] = self.board[row][column]
				elif(char == "p"):
					self.board[row][column] = Pawn(Color.BLACK, row, column, self)
				elif(char == "P"):
					self.board[row][column] = Pawn(Color.WHITE, row, column, self)

				column+=1

		if("Q" not in split_fen[2]):
			self.kings[1].can_castle_queenside = False
		if("K" not in split_fen[2]):
			self.kings[1].can_castle_kingside = False
		if("q" not in split_fen[2]):
			self.kings[0].can_castle_queenside = False
		if("k" not in split_fen[2]):
			self.kings[0].can_castle_kingside = False
		
		if(split_fen[3]!="-"):
			row, column = self.notation_to_coordinates(split_fen[3], False)
			if(isinstance(self.board[row+1][column], Pawn)):
				self.en_passant_pawn = self.board[row+1][column]
			if(isinstance(self.board[row-1][column], Pawn)):
				self.en_passant_pawn = self.board[row-1][column]

		self.half_move = int(split_fen[4])
		self.full_move = int(split_fen[5])

	def get_fen(self):
		fen = ""
		empty_cells = 0

		for row in self.board:
			for current_cell in row:
				if(current_cell==" "):
					empty_cells+=1

				if(issubclass(type(current_cell), Chess_piece)):
					if(empty_cells!=0):
						fen+=str(empty_cells)
						empty_cells=0
					fen+=current_cell.fen_letter

			if(empty_cells!=0):
				fen+=str(empty_cells)
				empty_cells=0
			
			fen+="/"

		fen = fen[:-1]

		fen += " "

		if(self.white_turn):
			fen += "w"
		else:
			fen += "b"

		fen += " "

		if(self.kings[1].can_castle_kingside):
			fen += "K"
		if(self.kings[1].can_castle_queenside):
			fen += "Q"
		if(self.kings[0].can_castle_kingside):
			fen += "k"
		if(self.kings[0].can_castle_queenside):
			fen += "q"
		if(not self.kings[1].can_castle_kingside and
			not self.kings[1].can_castle_queenside and
			not self.kings[0].can_castle_kingside and
			not self.kings[0].can_castle_queenside):

			fen += "-"

		fen += " "

		if(self.en_passant_pawn!=None):
			fen += self.coordinates_to_notation(
				self.en_passant_pawn.x + self.en_passant_pawn.direction, 
				self.en_passant_pawn.y, False) 
		else:
			fen += "-"

		fen += " "

		fen += str(self.half_move) + " " + str(self.full_move)

		return fen

	def get_pieces(self, color):
		pieces = []

		for row in range(8):
			for column in range(8):
				if(isinstance(self.board[row][column], Chess_piece) and
					self.board[row][column].color == color):

					pieces.append(self.board[row][column])

		return pieces

	def legal_moves(self):
		moves = []
		if(self.white_turn):
			for piece in self.get_pieces(self.color):
				for move in piece.avail_moves():
					if(len(move)==2):
						moves.append((piece.x, piece.y, move[0], move[1]))
					else:
						moves.append((piece.x, piece.y, move[0], move[1], move[2]))
		else:
			for piece in self.get_pieces(self.color):
				for move in piece.avail_moves():
					if(len(move)==2):
						moves.append((piece.x, piece.y, move[0], move[1]))
					else:
						moves.append((piece.x, piece.y, move[0], move[1], move[2]))

		return moves

	def is_move_valid(self, move):
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
			self.display()
			raise InvalidMoveException("Error: Give long algebraic notation")
		
		if(int(move[1]) not in range(1, 9)):
			self.display()
			raise InvalidMoveException("Error: Give long algebraic notation")

		start_x = 8 - int(move[1])
		
		try:
			self.board[start_x][start_y]
		except:
			self.display()
			raise InvalidMoveException("Error: Give long algebraic notation")

		if(self.board[start_x][start_y]==" "):
			self.display()
			raise InvalidMoveException("Error: No piece there")

		if(self.white_turn and self.board[start_x][start_y].color!=Color.WHITE):
			self.display()
			raise InvalidMoveException("Error: White plays")
		elif(not self.white_turn and self.board[start_x][start_y].color!=Color.BLACK):
			self.display()
			raise InvalidMoveException("Error: Black plays")

		self.display(start_x, start_y)

		if(len(move)<3):
			return None

		if(ord(move[2].upper()) not in range(ord('A'), ord('i'))):
			self.display()
			raise InvalidMoveException("Error: Give long algebraic notation")
		end_y = int(ord(move[2].upper()) - ord("A"))

		if(len(move)<4):
			return None
		
		try:
			int(move[3])
		except:
			self.display()
			raise InvalidMoveException("Error: Give long algebraic notation")

		if(int(move[3]) not in range(1, 9)):
			self.display()
			raise InvalidMoveException("Error: Give long algebraic notation")

		end_x = 8 - int(move[3])

		try:
			self.board[end_x][end_y]
		except:
			self.display()
			raise InvalidMoveException("Error: Give long algebraic notation")

		if(start_x == end_x and start_y == end_y):
			self.display()
			raise InvalidMoveException(" ")

		if(self.board[end_x][end_y]!=" " and self.board[start_x][start_y].color == self.board[end_x][end_y].color):
			self.display()
			raise InvalidMoveException("Error: Can't move " + str(self.board[start_x][start_y]) + "  on " +\
				str(self.board[end_x][end_y]) + " (Your piece)")

		moves = self.board[start_x][start_y].avail_moves()
		moves = [(x[0], x[1]) for x in moves]

		if((end_x, end_y) not in moves):
			self.display()
			raise InvalidMoveException("Error: Can't move " + str(self.board[start_x][start_y]) 
				+ "  there")

		promotion = None
		if(isinstance(self.board[start_x][start_y], Pawn) and (end_x==0 or end_x==7)):
			promotion = ""
			print("(q, r, b, n): ", end= "")
			sys.stdout.flush()
			while(promotion not in ["q", "r", "b", "n"]):
				event = keyboard.read_event()
				if event.event_type == keyboard.KEY_DOWN:
					promotion = event.name

		return [start_x, start_y, end_x, end_y, promotion]

	def push(self, valid_move):
		w, h = shutil.get_terminal_size()

		self.previous_state = BoardState(
			deepcopy(self.board),
			self.white_turn,
			self.kings[:],
			self.is_check,
			self.en_passant_pawn,
			self.half_move,
			self.full_move,
			deepcopy(self.dead_piece_count)
		)

		start_x = valid_move[0]
		start_y = valid_move[1]
		end_x = valid_move[2]
		end_y = valid_move[3]
		promotion = valid_move[4]

		if(promotion):
			self.board[start_x][start_y].play_move((end_x, end_y, promotion))
		else:
			self.board[start_x][start_y].play_move((end_x, end_y))

		self.white_turn = not self.white_turn

		color = self.board[end_x][end_y].color
		pieces = self.get_pieces(not color)
		for piece in pieces:
			for move in piece.avail_moves():
				king = self.kings[color]
				if((king.x, king.y) == (move[0], move[1])):
					self.undo_last_move()

	def recursion_test(self, depth):
		if(depth==0):
			return 1

		num_positions = 0

		moves = []

		if(self.white_turn):
			pieces = self.get_pieces(Color.WHITE)
		else:
			pieces = self.get_pieces(Color.BLACK)

		try:
			for piece in pieces:
				for move in piece.avail_moves():
					if(len(move)==2):
						moves.append((piece.x, piece.y, move[0], move[1]))
					else:
						moves.append((piece.x, piece.y, move[0], move[1], move[2]))
		except Exception as e:
			self.display()
			print("\r" + traceback.format_exc(), end= "")
			time.sleep(100)

		for move in moves:
			backup = BoardState(
				deepcopy(self.board),
				self.white_turn,
				self.kings[:],
				self.is_check,
				self.en_passant_pawn,
				self.half_move,
				self.full_move,
				deepcopy(self.dead_piece_count)
			)

			if(len(move)<5):
				move = move + (None,)
			self.push(move)

			self.display()
			time.sleep(0.01)
			num_positions += self.recursion_test(depth-1)

			self.board = backup.board
			self.white_turn = backup.white_turn
			self.kings = backup.kings
			self.is_check = backup.is_check
			self.en_passant_pawn = backup.en_passant_pawn
			self.half_move = backup.half_move
			self.full_move = backup.full_move
			self.dead_piece_count = backup.dead_piece_count
			self.previous_state = None  # Clear the previous state.

		return num_positions

class Color(IntEnum):
	BLACK = 0
	WHITE = 1

class Chess_piece:
	def __str__(self):
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

		return pieces[self.fen_letter]

	def boundary_check(self, values):
		return len([x for x in values if x>=0 and x<8]) == len(values)

	def is_enemy_piece(self, test_x, test_y):
		return self.board_class.board[test_x][test_y]!=" " and self.board_class.board[
			self.x][self.y].color!=self.board_class.board[test_x][test_y].color 

	def attacked_squares(self):
		return self.avail_moves()

	def play_move(self, end):
		end_x, end_y = end

		if(isinstance(self.board_class.board[end_x][end_y], Chess_piece)):
			self.board_class.dead_piece_count[str(self.board_class.board[end_x][end_y])] += 1

		self.board_class.half_move += 1
		if(isinstance(self.board_class.board[end_x][end_y], Chess_piece)):
			self.board_class.half_move = 0

		if(self.color == Color.BLACK):
			self.board_class.full_move += 1

		self.board_class.board[end_x][end_y] = self
		self.board_class.board[self.x][self.y] = " "
		self.x = end_x
		self.y = end_y
		self.board_class.en_passant_pawn=None

class Pawn(Chess_piece):
	def __init__(self, color, x, y, board):
		self.color = color
		self.x = x
		self.y = y
		self.board_class = board

		if(color == Color.WHITE):
			self.fen_letter = "P"
			self.direction = 1
			if(self.x == 6):
				self.has_moved = False
			else:
				self.has_moved = True
		else:
			self.fen_letter = "p"
			self.direction = -1
			if(self.x == 1):
				self.has_moved = False
			else:
				self.has_moved = True

	def __deepcopy__(self, memo):
		# Create a deep copy of the object.
		new_obj = Pawn(self.color, self.x, self.y, self.board_class)
		return new_obj

	def attacked_squares(self):
		squares = []

		squares.append((self.x-1*self.direction, self.y-1))
		squares.append((self.x-1*self.direction, self.y+1))

		return squares

	def avail_moves(self):
		moves = []

		start_x = self.x
		start_y = self.y

		# One step
		if(self.board_class.board[start_x-1*self.direction][start_y]==" "):
			if(start_x-1*self.direction==0 or start_x-1*self.direction==7):
				moves.append((start_x - 1*self.direction, start_y, "q"))
				moves.append((start_x - 1*self.direction, start_y, "r"))
				moves.append((start_x - 1*self.direction, start_y, "b"))
				moves.append((start_x - 1*self.direction, start_y, "n"))
			else:
				moves.append((start_x - 1*self.direction, start_y))

		# Two steps
		if(super().boundary_check((start_x-2*self.direction, start_y)) and
			self.board_class.board[start_x-1*self.direction][start_y]==" " and
			self.board_class.board[start_x-2*self.direction][start_y]==" " and
			self.has_moved == False):
			
			moves.append((start_x - 2*self.direction, start_y))

		# Kill piece left
		if(super().boundary_check((start_x-1*self.direction, start_y-1)) and
			self.board_class.board[start_x][start_y].is_enemy_piece(start_x-1*self.direction, start_y-1)):

			if(start_x-1*self.direction==0 or start_x-1*self.direction==7):
				moves.append((start_x - 1*self.direction, start_y-1, "q"))
				moves.append((start_x - 1*self.direction, start_y-1, "r"))
				moves.append((start_x - 1*self.direction, start_y-1, "b"))
				moves.append((start_x - 1*self.direction, start_y-1, "n"))
			else:
				moves.append((start_x-1*self.direction, start_y-1))

		# Kill piece right
		if(super().boundary_check((start_x-1*self.direction, start_y+1)) and
			self.board_class.board[start_x][start_y].is_enemy_piece(start_x-1*self.direction, start_y+1)):

			if(start_x-1*self.direction==0 or start_x-1*self.direction==7):
				moves.append((start_x - 1*self.direction, start_y+1, "q"))
				moves.append((start_x - 1*self.direction, start_y+1, "r"))
				moves.append((start_x - 1*self.direction, start_y+1, "b"))
				moves.append((start_x - 1*self.direction, start_y+1, "n"))
			else:
				moves.append((start_x-1*self.direction, start_y+1))

		# En passant left
		if(super().boundary_check((start_x, start_y-1)) and
			self.board_class.board[start_x][start_y].is_enemy_piece(start_x, start_y-1) and
			self.board_class.board[start_x][start_y-1]==self.board_class.en_passant_pawn):

				moves.append((start_x-1*self.direction, start_y-1))

		# En passant right
		if(super().boundary_check((start_x, start_y+1)) and
			self.board_class.board[start_x][start_y].is_enemy_piece(start_x, start_y+1) and			
			self.board_class.board[start_x][start_y+1]==self.board_class.en_passant_pawn):

				moves.append((start_x-1*self.direction, start_y+1))

		return moves

	def play_move(self, end, promotion=None):
		if(len(end)==2):
			end_x, end_y = end
		else:
			end_x, end_y, promotion = end

		if(super().boundary_check((self.y-1,)) and
			self.board_class.board[self.x][self.y-1]==self.board_class.en_passant_pawn and end_y==self.y-1):
			
			self.board_class.board[self.x][self.y-1]=" "
	
		elif(super().boundary_check((self.y+1,)) and
			self.board_class.board[self.x][self.y+1]==self.board_class.en_passant_pawn and end_y==self.y+1):
			
			self.board_class.board[self.x][self.y+1]=" "

		start_x = self.x

		super().play_move((end_x, end_y))

		if(end_x+2*self.direction == start_x):
			self.board_class.en_passant_pawn=self
		
		if(promotion!=None):
			if(promotion == "q"):
				self.board_class.board[end_x][end_y] = Queen(
					self.board_class.board[end_x][end_y].color, end_x, end_y, self.board_class)
			elif(promotion == "r"):
				self.board_class.board[end_x][end_y] = Rook(
					self.board_class.board[end_x][end_y].color, end_x, end_y, self.board_class)
			elif(promotion == "b"):
				self.board_class.board[end_x][end_y] = Bishop(
					self.board_class.board[end_x][end_y].color, end_x, end_y, self.board_class)
			elif(promotion == "n"):
				self.board_class.board[end_x][end_y] = Knight(
					self.board_class.board[end_x][end_y].color, end_x, end_y, self.board_class)

		self.has_moved = True
		self.board_class.half_move = 0

		for move in self.board_class.board[end_x][end_y].avail_moves():
			if(isinstance(self.board_class.board[move[0]][move[1]], King)):
				self.board_class.is_check = True

class Rook(Chess_piece):
	def __init__(self, color, x, y, board):
		self.color = color
		self.x = x
		self.y = y
		self.board_class = board
		if(color == Color.WHITE):	
			self.fen_letter = "R"
		else:
			self.fen_letter = "r"
		self.has_moved = False

	def __deepcopy__(self, memo):
		# Create a deep copy of the object.
		new_obj = Rook(self.color, self.x, self.y, self.board_class)
		return new_obj

	def avail_moves(self):
		moves = []
		for offset_x in reversed(range(0, self.x)):
			if(self.board_class.board[offset_x][self.y] == " "):
				moves.append((offset_x, self.y))
			elif(self.board_class.board[offset_x][self.y].color != self.color):
				moves.append((offset_x, self.y))
				break	
			else:
				break
		
		for offset_x in range(self.x+1, 8):
			if(self.board_class.board[offset_x][self.y] == " "):
				moves.append((offset_x, self.y))
			elif(self.board_class.board[offset_x][self.y].color != self.color):
				moves.append((offset_x, self.y))
				break	
			else:
				break

		for offset_y in reversed(range(0, self.y)):
			if(self.board_class.board[self.x][offset_y] == " "):
				moves.append((self.x, offset_y))
			elif(self.board_class.board[self.x][offset_y].color != self.color):
				moves.append((self.x, offset_y))
				break	
			else:
				break

		for offset_y in range(self.y+1, 8):
			if(self.board_class.board[self.x][offset_y] == " "):
				moves.append((self.x, offset_y))
			elif(self.board_class.board[self.x][offset_y].color != self.color):
				moves.append((self.x, offset_y))
				break	
			else:
				break

		return moves;

	def play_move(self, end):
		start_y = self.y
		end_x, end_y = end
		super().play_move((end_x, end_y))

		if(not self.has_moved and start_y == 0):
			self.board_class.kings[self.color].can_castle_queenside = False			
		if(not self.has_moved and start_y == 7):
			self.board_class.kings[self.color].can_castle_kingside = False

		self.has_moved = True

		for move in self.avail_moves():
			if(isinstance(self.board_class.board[move[0]][move[1]], King)):
				self.board_class.is_check = True

class Bishop(Chess_piece):
	def __init__(self, color, x, y, board):
		self.color = color
		self.x = x
		self.y = y
		self.board_class = board
		if(color == Color.WHITE):
			self.fen_letter = "B"
		else:
			self.fen_letter = "b"

	def __deepcopy__(self, memo):
		# Create a deep copy of the object.
		new_obj = Bishop(self.color, self.x, self.y, self.board_class)
		return new_obj

	def avail_moves(self):
		moves = []
		for offset_x, offset_y in zip(reversed(range(0, self.x)), reversed(range(0, self.y))):
			if(self.board_class.board[offset_x][offset_y] == " "):
				moves.append((offset_x, offset_y))
			elif(self.board_class.board[offset_x][offset_y].color != self.color):
				moves.append((offset_x, offset_y))
				break	
			else:
				break
		
		for offset_x, offset_y in zip(range(self.x+1, 8), range(self.y+1, 8)):
			if(self.board_class.board[offset_x][offset_y] == " "):
				moves.append((offset_x, offset_y))
			elif(self.board_class.board[offset_x][offset_y].color != self.color):
				moves.append((offset_x, offset_y))
				break	
			else:
				break

		for offset_x, offset_y in zip(range(self.x+1, 8), reversed(range(0, self.y))):
			if(self.board_class.board[offset_x][offset_y] == " "):
				moves.append((offset_x, offset_y))
			elif(self.board_class.board[offset_x][offset_y].color != self.color):
				moves.append((offset_x, offset_y))
				break	
			else:
				break

		for offset_x, offset_y in zip(reversed(range(0, self.x)), range(self.y+1, 8)):
			if(self.board_class.board[offset_x][offset_y] == " "):
				moves.append((offset_x, offset_y))
			elif(self.board_class.board[offset_x][offset_y].color != self.color):
				moves.append((offset_x, offset_y))
				break	
			else:
				break

		return moves

	def play_move(self, end):
		end_x, end_y = end

		super().play_move((end_x, end_y))

		for move in self.avail_moves():
			if(isinstance(self.board_class.board[move[0]][move[1]], King)):
				self.board_class.is_check = True

class Knight(Chess_piece):
	def __init__(self, color, x, y, board):
		self.color = color
		self.x = x
		self.y = y
		self.board_class = board
		if(color == Color.WHITE):
			self.fen_letter = "N"
		else:
			self.fen_letter = "n"

	def __deepcopy__(self, memo):
		# Create a deep copy of the object.
		new_obj = Knight(self.color, self.x, self.y, self.board_class)
		return new_obj

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
			if(not super().boundary_check((cur_x, cur_y))):
				moves.remove(cur_move)
				continue

			# Don't remove moves to empty cell
			if(self.board_class.board[cur_x][cur_y]==" "):
				continue

			# Remove moves on your pieces
			if self.board_class.board[cur_x][cur_y].color == self.board_class.board[self.x][ self.y].color:
				moves.remove(cur_move)

		return moves
	
	def play_move(self, end):
		end_x, end_y = end

		super().play_move((end_x, end_y))

		for move in self.avail_moves():
			if(isinstance(self.board_class.board[move[0]][move[1]], King)):
				self.board_class.is_check = True

class Queen(Chess_piece):
	def __init__(self, color, x, y, board):
		self.color = color
		self.x = x
		self.y = y
		self.board_class = board
		if(color == Color.WHITE):
			self.fen_letter = "Q"
		else:
			self.fen_letter = "q"

	def __deepcopy__(self, memo):
		# Create a deep copy of the object.
		new_obj = Queen(self.color, self.x, self.y, self.board_class)
		return new_obj

	def avail_moves(self):
		moves = []
		moves = Rook.avail_moves(self)
		moves += Bishop.avail_moves(self)

		return moves
	
	def play_move(self, end):
		end_x, end_y = end

		super().play_move((end_x, end_y))

		for move in self.avail_moves():
			if(isinstance(self.board_class.board[move[0]][move[1]], King)):
				self.board_class.is_check = True

class King(Chess_piece):
	def __init__(self, color, x, y, board):
		self.color = color
		self.x = x
		self.y = y
		self.board_class = board
		if(color == Color.WHITE):
			self.fen_letter = "K"
		else:
			self.fen_letter = "k"
		self.has_moved = False
		self.can_castle_kingside = True
		self.can_castle_queenside = True  
		self.in_check = False

	def __deepcopy__(self, memo):
		# Create a deep copy of the object.
		new_obj = King(self.color, self.x, self.y, self.board_class)
		return new_obj

	def attacked_squares(self):
		moves = [(self.x+1, self.y), 
				(self.x+1, self.y+1), 
				(self.x+1, self.y-1), 
				(self.x, self.y+1), 
				(self.x, self.y-1), 
				(self.x-1, self.y),
				(self.x-1, self.y+1), 
				(self.x-1, self.y-1)]

		return moves

	def avail_moves(self):
		moves = [(self.x+1, self.y), 
				(self.x+1, self.y+1), 
				(self.x+1, self.y-1), 
				(self.x, self.y+1), 
				(self.x, self.y-1), 
				(self.x-1, self.y),
				(self.x-1, self.y+1), 
				(self.x-1, self.y-1)]

		attacked_squares = set()
		for piece in self.board_class.get_pieces(not self.color):
			attacked_squares.update(set(piece.attacked_squares()))

		for cur_move in reversed(moves):
			cur_x = cur_move[0]
			cur_y = cur_move[1]

			# Remove out of range moves
			if(not super().boundary_check((cur_x, cur_y))):
				moves.remove(cur_move)
				continue

			# Don't remove moves to empty cell
			if(self.board_class.board[cur_x][cur_y]==" "):
				# Remove attacked squares
				if((cur_x, cur_y) in attacked_squares):
					moves.remove(cur_move)

				continue

			# Remove moves on your pieces
			if(self.board_class.board[cur_x][cur_y].color == self.color):
				moves.remove(cur_move)

		if(super().boundary_check((self.y-1, self.y-2, self.y-3, self.y-4)) and
			self.has_moved==False and 
			self.board_class.board[self.x][self.y-1]==" " and
			self.board_class.board[self.x][self.y-2]==" " and
			self.board_class.board[self.x][self.y-3]==" " and
			self.can_castle_queenside and
			(self.x, self.y) not in attacked_squares and			
			(self.x, self.y-1) not in attacked_squares and
			(self.x, self.y-2) not in attacked_squares and
			isinstance(self.board_class.board[self.x][self.y-4], Rook) and
			self.board_class.board[self.x][self.y-4].color==self.color and
			self.board_class.board[self.x][self.y-4].has_moved==False):
	
			moves.append((self.x, self.y-2))

		if(super().boundary_check((self.y+1, self.y+2, self.y+3)) and
			self.has_moved==False and 
			self.board_class.board[self.x][self.y+1]==" " and
			self.board_class.board[self.x][self.y+2]==" " and
			self.can_castle_kingside and
			(self.x, self.y) not in attacked_squares and			
			(self.x, self.y+1) not in attacked_squares and
			(self.x, self.y+2) not in attacked_squares and
			isinstance(self.board_class.board[self.x][self.y+3], Rook) and
			self.board_class.board[self.x][self.y+3].color==self.color and
			self.board_class.board[self.x][self.y+3].has_moved==False):
	
			moves.append((self.x, self.y+2))

		return moves

	def play_move(self, end):
		end_x, end_y = end

		if(end_y==self.y-2):
			# Not doing this
			# self.board_class.board[self.x][self.y-4].play_move((self.x, end_y+1))
			# to avoid calling the chess_piece play_move twice and mess
			# up the half_move full_move counters

			self.board_class.board[self.x][end_y+1] = self.board_class.board[self.x][self.y-4]
			self.board_class.board[self.x][self.y-4] = " "
			self.board_class.board[self.x][end_y+1].x = end_x
			self.board_class.board[self.x][end_y+1].y = end_y
		if(end_y==self.y+2):
			# Not doing this
			# self.board_class.board[self.x][self.y+3].play_move((self.x, end_y-1))
			# to avoid calling the chess_piece play_move twice and mess
			# up the half_move full_move counters
			
			self.board_class.board[self.x][end_y-1] = self.board_class.board[self.x][self.y+3]
			self.board_class.board[self.x][self.y+3] = " "
			self.board_class.board[self.x][end_y-1].x = end_x
			self.board_class.board[self.x][end_y-1].y = end_y

		super().play_move((end_x, end_y))

		self.has_moved = True
		self.can_castle_kingside = False
		self.can_castle_queenside = False

class InvalidMoveException(Exception):
	pass

def main():
	fen_test_position = "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"
	# rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8
	#for bug test after promotion and checks, recursion depths -> combinations
	#1 -> 44
	#2 -> 1486
	#3 -> 62379
	#4 -> 2103487
	#5 -> 89941194

	board = Board(fen_test_position)

	while True:
		# board.display()

		# move = ""
		# while(len(move)!=4):
		# 	event = keyboard.read_event()
		# 	if event.event_type == keyboard.KEY_DOWN:
		# 		move += event.name

		# 	try:
		# 		valid_move = board.is_move_valid(move)
		# 	except Exception as e:
		# 		# print("\r" + traceback.format_exc(), end= "")				
		# 		print("\r" + str(e), end= "")
		# 		move = ""

		# board.push(valid_move)

		move_count = board.recursion_test(2)
		print(move_count)
		time.sleep(100)

main()