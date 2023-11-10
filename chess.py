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
import time
from enum import IntEnum
from copy import deepcopy
from colorama import Fore, Back, Style

class Board:
	def __init__(self, fen = None):	
		self.squares = np.zeros((8, 8), dtype = Chess_piece) 
		self.white_turn = True
		self.kings = [None, None] # kings[0] is black kings[1] is white
		self.checkmate = False
		self.stalemate = False
		self.draw = False
		self.previous_fen = None
		self.en_passant_pawn = None
		self.half_move = 0
		self.full_move = 1
		self.fen_history = {}
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

	def board_copy(self):
		new_board = Board()
		new_board.squares = deepcopy(self.squares)
		new_board.white_turn = self.white_turn
		new_board.checkmate = self.checkmate
		new_board.stalemate = self.stalemate
		new_board.draw = self.draw
		new_board.en_passant_pawn = self.en_passant_pawn
		new_board.half_move = self.half_move
		new_board.full_move = self.full_move
		new_board.dead_piece_count = self.dead_piece_count.copy()
		new_board.fen_history = self.fen_history.copy()

		# Update references in copied pieces
		for row in range(8):
			for col in range(8):
				piece = new_board.squares[row][col]
				if(isinstance(piece, Chess_piece)):
					piece.update(new_board)

				if(isinstance(piece, King)):
					if(piece.color == Color.BLACK):
						new_board.kings[0] = piece
					else:
						new_board.kings[1] = piece

		return new_board

	def display(self, source_x=None, source_y=None):
		w, h = shutil.get_terminal_size()
		mid = w//2 - 34//2

		only_start = False

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
		
		if(source_x!=None and source_y!=None):
			moves = self.squares[source_x][source_y].legal_moves()
			moves = [(move.dest_x, move.dest_y) for move in moves]

		for i, row in enumerate(self.squares):
			cur_string = mid*" " + str(row_num) + " "

			for j, current in enumerate(row):
				if (i + j) % 2 == 0:
					bg_color = '\x1b[48;5;233m'  # gray
				else:
					bg_color = '\x1b[40m'  # black

				if(i==source_x and j==source_y):
					cur_string += Back.LIGHTCYAN_EX + " " + str(current) + " " + Style.RESET_ALL
				elif(not only_start and source_x!=None and source_y!=None and (i, j) in moves):
					if(isinstance(self.squares[i][j], Chess_piece)):
						if(self.squares[source_x][source_y].color!=self.squares[i][j].color):
							cur_string += \
								Back.LIGHTRED_EX + " " + str(current) + " " + Style.RESET_ALL
					else:
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
					self.squares[row][column]=" "
					column+=1
			elif(char=="/"):
				row+=1
				column=0
			else:
				if(char == "r"):
					self.squares[row][column] = Rook(Color.BLACK, row, column, self)
				elif(char == "R"):
					self.squares[row][column] = Rook(Color.WHITE, row, column, self)
				elif(char == "n"):
					self.squares[row][column] = Knight(Color.BLACK, row, column, self)
				elif(char == "N"):
					self.squares[row][column] = Knight(Color.WHITE, row, column, self)
				elif(char == "b"):
					self.squares[row][column] = Bishop(Color.BLACK, row, column, self)
				elif(char == "B"):
					self.squares[row][column] = Bishop(Color.WHITE, row, column, self)
				elif(char == "q"):
					self.squares[row][column] = Queen(Color.BLACK, row, column, self)
				elif(char == "Q"):
					self.squares[row][column] = Queen(Color.WHITE, row, column, self)
				elif(char == "k"):
					self.squares[row][column] = King(Color.BLACK, row, column, self)
					self.kings[0] = self.squares[row][column]
				elif(char == "K"):
					self.squares[row][column] = King(Color.WHITE, row, column, self)
					self.kings[1] = self.squares[row][column]
				elif(char == "p"):
					self.squares[row][column] = Pawn(Color.BLACK, row, column, self)
				elif(char == "P"):
					self.squares[row][column] = Pawn(Color.WHITE, row, column, self)

				column+=1

		if("Q" not in split_fen[2]):
			self.kings[1].can_castle_queenside = False
		if("K" not in split_fen[2]):
			self.kings[1].can_castle_kingside = False
		if("q" not in split_fen[2]):
			self.kings[0].can_castle_queenside = False
		if("k" not in split_fen[2]):
			self.kings[0].can_castle_kingside = False
		
		if(len(split_fen)>=4 and split_fen[3]!="-"):
			row, column = self.notation_to_coordinates(split_fen[3], False)
			if(isinstance(self.squares[row+1][column], Pawn)):
				self.en_passant_pawn = self.squares[row+1][column]
			if(isinstance(self.squares[row-1][column], Pawn)):
				self.en_passant_pawn = self.squares[row-1][column]

		if(len(split_fen)>=5):
			self.half_move = int(split_fen[4])
		if(len(split_fen)==6):
			self.full_move = int(split_fen[5])

	def get_fen(self):
		fen = ""
		empty_cells = 0

		for row in self.squares:
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

	def get_player_pieces(self, color):
		pieces = []

		for row in range(8):
			for column in range(8):
				if(isinstance(self.squares[row][column], Chess_piece) and
					self.squares[row][column].color == color):

					pieces.append(self.squares[row][column])

		return pieces

	def all_legal_moves(self):
		return [move for piece in self.get_player_pieces(self.white_turn) for move in piece.legal_moves()]

	def is_move_valid(self, move):
		if(len(move)==0):
			return None

		move = [char for char in move]

		if(ord(move[0].upper()) not in range(ord('A'), ord('i'))):
			raise InvalidMoveException("Error: Give long algebraic notation")
		source_y = int(ord(move[0].upper()) - ord("A"))

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

		source_x = 8 - int(move[1])
		
		try:
			self.squares[source_x][source_y]
		except:
			self.display()
			raise InvalidMoveException("Error: Give long algebraic notation")

		if(self.squares[source_x][source_y]==" "):
			self.display()
			raise InvalidMoveException("Error: No piece there")

		if(self.white_turn and self.squares[source_x][source_y].color!=Color.WHITE):
			self.display()
			raise InvalidMoveException("Error: White plays")
		elif(not self.white_turn and self.squares[source_x][source_y].color!=Color.BLACK):
			self.display()
			raise InvalidMoveException("Error: Black plays")

		self.display(source_x, source_y)

		if(len(move)<3):
			return None

		if(ord(move[2].upper()) not in range(ord('A'), ord('i'))):
			self.display()
			raise InvalidMoveException("Error: Give long algebraic notation")
		dest_y = int(ord(move[2].upper()) - ord("A"))

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

		dest_x = 8 - int(move[3])

		try:
			self.squares[dest_x][dest_y]
		except:
			self.display()
			raise InvalidMoveException("Error: Give long algebraic notation")

		if(source_x == dest_x and source_y == dest_y):
			self.display()
			raise InvalidMoveException(" ")

		if(self.squares[dest_x][dest_y]!=" " and self.squares[source_x][source_y].color == self.squares[dest_x][dest_y].color):
			self.display()
			raise InvalidMoveException("Error: Can't move " + str(self.squares[source_x][source_y]) + "  on " +\
				str(self.squares[dest_x][dest_y]) + " (Your piece)")

		moves = self.squares[source_x][source_y].legal_moves()
		moves = [(move.dest_x, move.dest_y) for move in moves]

		if((dest_x, dest_y) not in moves):
			self.display()
			raise InvalidMoveException("Error: Can't move " + str(self.squares[source_x][source_y]) 
				+ "  there")

		promotion = False
		if(isinstance(self.squares[source_x][source_y], Pawn) and (dest_x==0 or dest_x==7)):
			promotion = True

		return [source_x, source_y, dest_x, dest_y, promotion]

	def push(self, move):
		self.previous_fen = self.get_fen()
		
		if(self.is_game_over()):
			return

		w, h = shutil.get_terminal_size()

		self.squares[move.source_x][move.source_y].play_move(move)

		self.white_turn = not self.white_turn

		all_moves = self.all_legal_moves()
		if(len(all_moves)==0):
			pieces = self.get_player_pieces(not self.white_turn)
			for piece in pieces:
				for attack_move in piece.avail_moves():
					king = self.kings[self.white_turn]
					if((king.x, king.y) == (attack_move.dest_x, attack_move.dest_y)):
						self.checkmate = True
						return

			self.stalemate = True
			return

		if(self.half_move>=50):
			# 50 Move rule
			self.draw = True
			return

		current_fen = self.get_fen().split()
		# Ignore full move half move
		current_fen = " ".join(current_fen[:4])
		self.fen_history[current_fen] = self.fen_history.get(current_fen, 0) + 1

		if(self.fen_history[current_fen] >= 3):
			# Threefold Rep
			self.draw = True
			return

	def pop(self):
		if(self.previous_fen):
			self.set_fen(self.previous_fen)
			self.previous_fen = None

	def recursion_test(self, depth):
		if(depth==0):
			return 1

		num_positions = 0

		pieces = self.get_player_pieces(self.white_turn)

		moves = [move for piece in pieces for move in piece.legal_moves()]

		for move in moves:
			new_board = self.board_copy()

			# new_board.display(move.source_x, move.source_y)
			# time.sleep(0.01)
			new_board.push(move)
			# new_board.display(move.dest_x, move.dest_y)
			# time.sleep(0.01)

			num_positions += new_board.recursion_test(depth-1)

		return num_positions

	def is_checkmate(self):
		return self.checkmate

	def is_stalemate(self):
		return self.stalemate

	def is_game_over(self):
		if(self.checkmate or self.stalemate or self.draw):
			return True
		else:
			return False

class Color(IntEnum):
	BLACK = 0
	WHITE = 1

class Move:
	def __init__(self, source_x, source_y, dest_x, dest_y, promotion=None):
		self.source_x = source_x
		self.source_y = source_y
		self.dest_x = dest_x
		self.dest_y = dest_y
		if(promotion!=None):
			self.promotion = promotion

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

	def update(self, board):
		self.board = board

	def is_enemy_piece(self, test_x, test_y):
		return self.board.squares[test_x][test_y]!=" " and self.board.squares[
			self.x][self.y].color!=self.board.squares[test_x][test_y].color 

	def legal_moves(self):
		if(self.board.is_game_over()):
			return []

		moves = self.avail_moves()
		for move in reversed(moves):
			new_board = self.board.board_copy()

			new_board.squares[self.x][self.y].play_move(move)

			pieces = new_board.get_player_pieces(not self.color)
			for piece in pieces:
				if(isinstance(piece, King)):
					continue

				for attack_move in piece.attacked_squares():
					king = new_board.kings[self.color]
					if((king.x, king.y) == (attack_move[0], attack_move[1])):
						if move in moves:
							moves.remove(move)

		return moves

	def play_move(self, move):
		dest_x, dest_y = move.dest_x, move.dest_y

		if(isinstance(self.board.squares[dest_x][dest_y], Chess_piece)):
			self.board.dead_piece_count[str(self.board.squares[dest_x][dest_y])] += 1

		self.board.half_move += 1
		if(isinstance(self.board.squares[dest_x][dest_y], Chess_piece)):
			self.board.half_move = 0

		if(self.color == Color.BLACK):
			self.board.full_move += 1

		self.board.squares[dest_x][dest_y] = self
		self.board.squares[self.x][self.y] = " "
		self.x = dest_x
		self.y = dest_y
		self.board.en_passant_pawn=None

class Pawn(Chess_piece):
	def __init__(self, color, x, y, board):
		self.color = color
		self.x = x
		self.y = y
		self.board = board

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

	def attacked_squares(self):
		squares = []

		squares.append((self.x-1*self.direction, self.y-1))
		squares.append((self.x-1*self.direction, self.y+1))

		return squares

	def avail_moves(self):
		moves = []

		# One step
		if(self.board.squares[self.x-1*self.direction][self.y]==" "):
			if(self.x-1*self.direction==0 or self.x-1*self.direction==7):
				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y, "q"))
				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y, "r"))
				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y, "b"))
				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y, "n"))
			else:
				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y))

		# Two steps
		if(all(0 <= value <= 7 for value in (self.x-2*self.direction, self.y)) and
			self.board.squares[self.x-1*self.direction][self.y]==" " and
			self.board.squares[self.x-2*self.direction][self.y]==" " and
			self.has_moved == False):

			moves.append(Move(self.x, self.y, self.x - 2*self.direction, self.y))

		# Kill piece left
		if(all(0 <= value <= 7 for value in (self.x-1*self.direction, self.y-1)) and
			self.board.squares[self.x][self.y].is_enemy_piece(self.x-1*self.direction, self.y-1)):

			if(self.x-1*self.direction==0 or self.x-1*self.direction==7):
				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y-1, "q"))
				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y-1, "r"))
				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y-1, "b"))
				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y-1, "n"))
			else:
				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y-1))

		# Kill piece right
		if(all(0 <= value <= 7 for value in (self.x-1*self.direction, self.y+1)) and
			self.board.squares[self.x][self.y].is_enemy_piece(self.x-1*self.direction, self.y+1)):

			if(self.x-1*self.direction==0 or self.x-1*self.direction==7):
				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y+1, "q"))
				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y+1, "r"))
				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y+1, "b"))
				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y+1, "n"))
			else:
				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y+1))

		# En passant left
		if(all(0 <= value <= 7 for value in (self.x, self.y-1)) and
			self.board.squares[self.x][self.y].is_enemy_piece(self.x, self.y-1) and
			self.board.squares[self.x][self.y-1]==self.board.en_passant_pawn):

				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y-1))

		# En passant right
		if(all(0 <= value <= 7 for value in (self.x, self.y+1)) and
			self.board.squares[self.x][self.y].is_enemy_piece(self.x, self.y+1) and			
			self.board.squares[self.x][self.y+1]==self.board.en_passant_pawn):

				moves.append(Move(self.x, self.y, self.x - 1*self.direction, self.y+1))

		return moves

	def play_move(self, move):

		if(all(0 <= value <= 7 for value in (self.y-1,)) and
			self.board.squares[self.x][self.y-1]==self.board.en_passant_pawn and dest_y==self.y-1):
			
			self.board.squares[self.x][self.y-1]=" "
	
		elif(all(0 <= value <= 7 for value in (self.y+1,)) and
			self.board.squares[self.x][self.y+1]==self.board.en_passant_pawn and dest_y==self.y+1):
			
			self.board.squares[self.x][self.y+1]=" "

		super().play_move(move)

		if(move.dest_x+2*self.direction == move.source_x):
			self.board.en_passant_pawn=self
		
		if(hasattr(move, 'promotion')):
			if(move.promotion == "q"):
				self.board.squares[move.dest_x][move.dest_y] = Queen(
					self.board.squares[move.dest_x][move.dest_y].color, 
						move.dest_x, move.dest_y, self.board)
			elif(move.promotion == "r"):
				self.board.squares[move.dest_x][move.dest_y] = Rook(
					self.board.squares[move.dest_x][move.dest_y].color, 
					move.dest_x, move.dest_y, self.board)
			elif(move.promotion == "b"):
				self.board.squares[move.dest_x][move.dest_y] = Bishop(
					self.board.squares[move.dest_x][move.dest_y].color, 
					move.dest_x, move.dest_y, self.board)
			elif(move.promotion == "n"):
				self.board.squares[move.dest_x][move.dest_y] = Knight(
					self.board.squares[move.dest_x][move.dest_y].color, 
					move.dest_x, move.dest_y, self.board)

		self.has_moved = True
		self.board.half_move = 0

class Rook(Chess_piece):
	def __init__(self, color, x, y, board):
		self.color = color
		self.x = x
		self.y = y
		self.board = board
		if(color == Color.WHITE):	
			self.fen_letter = "R"
		else:
			self.fen_letter = "r"
		self.has_moved = False

	def attacked_squares(self):
		return [(move.dest_x, move.dest_y) for move in self.avail_moves()]

		# values = [
		# 	# ↑
		# 	zip(reversed(range(0, self.x)), [self.y] * self.x),
		# 	# ↓ 
		# 	zip(range(self.x+1, 8), [self.y] * (8-self.x-1)),
		# 	# ←
		# 	zip([self.x] * (self.y), reversed(range(0, self.y))),
		# 	# → 
		# 	zip([self.x] * (8-self.y-1), range(self.y+1, 8))
		# ]

		# squares = []
		# for direction in values:
		# 	for x, y in direction:
		# 		if(self.board.squares[x][y] == " "):
		# 			squares.append((self.x, self.y, x, y))
		# 		elif(self.board.squares[x][y].color != self.color):
		# 			squares.append((self.x, self.y, x, y))
		# 			break
		# 		else:
		# 			break

		# return squares

	def avail_moves(self):
		values = [
			# ↑
			zip(reversed(range(0, self.x)), [self.y] * self.x),
			# ↓ 
			zip(range(self.x+1, 8), [self.y] * (8-self.x-1)),
			# ←
			zip([self.x] * (self.y), reversed(range(0, self.y))),
			# → 
			zip([self.x] * (8-self.y-1), range(self.y+1, 8))
		]

		vertical_pieces = []
		first_half = []
		for direction in values[:2]:
			for x, y in direction:
				if(self.board.squares[x][y] == " "):
					first_half.append(Move(self.x, self.y, x, y))
				elif(self.board.squares[x][y].color != self.color):
					first_half.append(Move(self.x, self.y, x, y))
					vertical_pieces.append(self.board.squares[x][y])
					break
				else:
					vertical_pieces.append(self.board.squares[x][y])
					break

		unique_classes = set()
		for piece in vertical_pieces:
			unique_classes.add(type(piece))	

		# Only this diagonal available cause of discovered check
		if((King in unique_classes and Queen in unique_classes or
			King in unique_classes and Rook in unique_classes) and
			vertical_pieces[0].color!=vertical_pieces[1].color):

			return first_half

		vertical_pieces = []
		second_half = []
		for direction in values[2:]:
			for x, y in direction:
				if(self.board.squares[x][y] == " "):
					second_half.append(Move(self.x, self.y, x, y))
				elif(self.board.squares[x][y].color != self.color):
					second_half.append(Move(self.x, self.y, x, y))
					vertical_pieces.append(self.board.squares[x][y])
					break
				else:
					vertical_pieces.append(self.board.squares[x][y])
					break

		unique_classes = set()
		for piece in vertical_pieces:
			unique_classes.add(type(piece))	

		# Only this diagonal available cause of discovered check
		if((King in unique_classes and Queen in unique_classes or
			King in unique_classes and Rook in unique_classes) and
			vertical_pieces[0].color!=vertical_pieces[1].color):

			return second_half

		return first_half + second_half

	def play_move(self, move):
		source_y = move.source_y
		dest_x, dest_y = move.dest_x, move.dest_y
		super().play_move(move)

		if(not self.has_moved and source_y == 0):
			self.board.kings[self.color].can_castle_queenside = False		
		if(not self.has_moved and source_y == 7):
			self.board.kings[self.color].can_castle_kingside = False

		self.has_moved = True

class Bishop(Chess_piece):
	def __init__(self, color, x, y, board):
		self.color = color
		self.x = x
		self.y = y
		self.board = board
		if(color == Color.WHITE):
			self.fen_letter = "B"
		else:
			self.fen_letter = "b"

	def attacked_squares(self):
		return [(move.dest_x, move.dest_y) for move in self.avail_moves()]

		# values = [
		# 	# ↖
		# 	zip(reversed(range(0, self.x)), reversed(range(0, self.y))),
		# 	# ↘
		# 	zip(range(self.x+1, 8), range(self.y+1, 8)),
		# 	# ↙ 
		# 	zip(range(self.x+1, 8), reversed(range(0, self.y))),
		# 	# ↗
		# 	zip(reversed(range(0, self.x)), range(self.y+1, 8))
		# ]

		# attacked_squares = []
		# for direction in values:
		# 	for x, y in direction:
		# 		if(self.board.squares[x][y] == " " or
		# 			isinstance(self.board.squares[x][y], King)):

		# 			attacked_squares.append((self.x, self.y, x, y))
		# 		elif(self.board.squares[x][y].color != self.color):
		# 			attacked_squares.append((self.x, self.y, x, y))
		# 			break	
		# 		else:
		# 			break

		# return attacked_squares

	def avail_moves(self):
		values = [
			# ↖
			zip(reversed(range(0, self.x)), reversed(range(0, self.y))),
			# ↘
			zip(range(self.x+1, 8), range(self.y+1, 8)),
			# ↙ 
			zip(range(self.x+1, 8), reversed(range(0, self.y))),
			# ↗
			zip(reversed(range(0, self.x)), range(self.y+1, 8))
		]

		diagonal_pieces = []
		first_half = []
		for direction in values[:2]:
			for x, y in direction:
				if(self.board.squares[x][y] == " "):
					first_half.append(Move(self.x, self.y, x, y))
				elif(self.board.squares[x][y].color != self.color):
					first_half.append(Move(self.x, self.y, x, y))
					diagonal_pieces.append(self.board.squares[x][y])
					break	
				else:
					diagonal_pieces.append(self.board.squares[x][y])
					break

		unique_classes = set()
		for piece in diagonal_pieces:
			unique_classes.add(type(piece))	

		# Only this diagonal available cause of discovered check
		if((King in unique_classes and Queen in unique_classes or
			King in unique_classes and Bishop in unique_classes) and
			diagonal_pieces[0].color!=diagonal_pieces[1].color):

			return first_half

		diagonal_pieces = []
		second_half = []
		for direction in values[2:]:
			for x, y in direction:
				if(self.board.squares[x][y] == " "):
					second_half.append(Move(self.x, self.y, x, y))
				elif(self.board.squares[x][y].color != self.color):
					second_half.append(Move(self.x, self.y, x, y))
					diagonal_pieces.append(self.board.squares[x][y])
					break	
				else:
					diagonal_pieces.append(self.board.squares[x][y])
					break

		unique_classes = set()
		for piece in diagonal_pieces:
			unique_classes.add(type(piece))	

		# Only this diagonal available cause of discovered check
		if((King in unique_classes and Queen in unique_classes or
			King in unique_classes and Bishop in unique_classes) and
			diagonal_pieces[0].color!=diagonal_pieces[1].color):

			return second_half

		return first_half + second_half

	def play_move(self, move):
		super().play_move(move)

class Knight(Chess_piece):
	def __init__(self, color, x, y, board):
		self.color = color
		self.x = x
		self.y = y
		self.board = board
		if(color == Color.WHITE):
			self.fen_letter = "N"
		else:
			self.fen_letter = "n"

	def attacked_squares(self):
		return [(move.dest_x, move.dest_y) for move in self.avail_moves()]

	def avail_moves(self):
		moves = [(self.x+2, self.y+1), 
				(self.x-2, self.y+1), 
				(self.x+2, self.y-1), 
				(self.x-2, self.y-1), 
				(self.x+1, self.y+2), 
				(self.x-1, self.y+2), 
				(self.x+1, self.y-2), 
				(self.x-1, self.y-2)]

		moves = [
			Move(self.x, self.y, x, y) for x, y in reversed(moves) 
			
			# If every move is in chessboard 
			if all(0 <= value <= 7 for value in (x, y)) and (
				# and destination square empty
				not isinstance(self.board.squares[x][y], Chess_piece) or

				# or destination square enemy piece
				self.board.squares[self.x][self.y].is_enemy_piece(x, y)
			)
		]

		return moves

	def play_move(self, move):
		super().play_move(move)

class Queen(Chess_piece):
	def __init__(self, color, x, y, board):
		self.color = color
		self.x = x
		self.y = y
		self.board = board
		if(color == Color.WHITE):
			self.fen_letter = "Q"
		else:
			self.fen_letter = "q"

	def attacked_squares(self):
		return Rook.attacked_squares(self) + Bishop.attacked_squares(self)

	def avail_moves(self):
		return Rook.avail_moves(self) + Bishop.avail_moves(self)
	
	def play_move(self, move):
		super().play_move(move)

class King(Chess_piece):
	def __init__(self, color, x, y, board):
		self.color = color
		self.x = x
		self.y = y
		self.board = board
		if(color == Color.WHITE):
			self.fen_letter = "K"
		else:
			self.fen_letter = "k"
		self.has_moved = False
		self.can_castle_kingside = True
		self.can_castle_queenside = True  
		self.in_check = False

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
		for piece in self.board.get_player_pieces(not self.color):
			attacked_squares.update(set(piece.attacked_squares()))

		if(all(0 <= value <= 7 for value in (self.y-1, self.y-2, self.y-3, self.y-4)) and
			self.has_moved==False and 
			self.board.squares[self.x][self.y-1]==" " and
			self.board.squares[self.x][self.y-2]==" " and
			self.board.squares[self.x][self.y-3]==" " and
			self.can_castle_queenside and
			(self.x, self.y) not in attacked_squares and			
			(self.x, self.y-1) not in attacked_squares and
			(self.x, self.y-2) not in attacked_squares and
			isinstance(self.board.squares[self.x][self.y-4], Rook) and
			self.board.squares[self.x][self.y-4].color==self.color and
			self.board.squares[self.x][self.y-4].has_moved==False):

			moves.append((self.x, self.y-2))

		if(all(0 <= value <= 7 for value in (self.y+1, self.y+2, self.y+3)) and
			self.has_moved==False and 
			self.board.squares[self.x][self.y+1]==" " and
			self.board.squares[self.x][self.y+2]==" " and
			self.can_castle_kingside and
			(self.x, self.y) not in attacked_squares and			
			(self.x, self.y+1) not in attacked_squares and
			(self.x, self.y+2) not in attacked_squares and
			isinstance(self.board.squares[self.x][self.y+3], Rook) and
			self.board.squares[self.x][self.y+3].color==self.color and
			self.board.squares[self.x][self.y+3].has_moved==False):
	
			moves.append((self.x, self.y+2))

		moves = [
			Move(self.x, self.y, x, y) for x, y in reversed(moves) 
			
			# If every move is in chessboard
			if all(0 <= value <= 7 for value in (x, y)) and 
			(
				# and destination square empty
				not isinstance(self.board.squares[x][y], Chess_piece) or

				# or destination square enemy piece
				self.board.squares[self.x][self.y].is_enemy_piece(x, y)
			) and (x, y) not in attacked_squares
			# and not threatened
		]

		return moves

	def play_move(self, move):
		dest_x, dest_y = move.dest_x, move.dest_y

		if(dest_y==self.y-2):
			self.board.squares[self.x][self.y-4].play_move(Move(self.x, self.y-4, self.x, dest_y+1))

		if(dest_y==self.y+2):
			self.board.squares[self.x][self.y+3].play_move(Move(self.x, self.y+4, self.x, dest_y-1))

		# Not calling super to avoid calling the chess_piece play_move twice 
		# and mess up the half_move full_move counters
		# super().play_move((dest_x, dest_y))
 
		self.board.squares[dest_x][dest_y] = self
		self.board.squares[self.x][self.y] = " "
		self.x = dest_x
		self.y = dest_y

		self.has_moved = True
		self.can_castle_kingside = False
		self.can_castle_queenside = False

class InvalidMoveException(Exception):
	pass

def main():
	# rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8
	#for bug test after promotion and checks, recursion depths -> combinations
	#1 -> 44
	#2 -> 1486
	#3 -> 62379
	#4 -> 2103487
	#5 -> 89941194

	board = Board("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8")

	# while True:
	# 	board.display()

	# 	check_move = ""
	# 	while(True):
	# 		event = keyboard.read_event()
	# 		if event.event_type == keyboard.KEY_DOWN:
	# 			check_move += event.name

	# 		try:
	# 			move = board.is_move_valid(check_move)
	# 			if(move == None):
	# 				continue
				
	# 			if(len(move)==5):
	# 				if(move[4]):
	# 					promotion = ""
	# 					print("(q, r, b, n): ", end= "")
	# 					sys.stdout.flush()
	# 					while(promotion not in ["q", "r", "b", "n"]):
	# 						event = keyboard.read_event()
	# 						if event.event_type == keyboard.KEY_DOWN:
	# 							promotion = event.name
	# 					move[4] = promotion
	# 				move = Move(*move)
	# 				break
	# 		except Exception as e:
	# 			# print("\r" + traceback.format_exc(), end= "")				
	# 			print("\r" + str(e), end= "")
	# 			check_move = ""

	# 	board.push(move)

	start_time = time.time()
	move_count = board.recursion_test(2)
	print(str(move_count) + "/1486, ", round(time.time() - start_time, 1), "s")

main()