# -*- encoding: utf-8 -*-
"""
Unicode Chess — A terminal-based chess game with Unicode piece rendering.

A fully functional chess library with move generation, move validation,
and support for FEN notation.  Can be used standalone or as a backend for
a UCI engine (see engine.py).
"""

import os
import math
import time
import sys
import subprocess
import shutil
import traceback
from enum import IntEnum
from copy import deepcopy
from typing import List, Optional, Tuple, Dict

import numpy as np
import keyboard
from colorama import Fore, Back, Style, init

# Initialize colorama for cross-platform colour support
init()


class Board:
	"""Represents a chess board and manages game state.

	Attributes:
		squares: 8×8 numpy array holding piece objects or " " for empty.
		white_turn: True when it is White's move.
		kings: [black_king, white_king] references.
		checkmate / stalemate / draw: game-over flags.
	"""

	def __init__(self, fen: Optional[str] = None):
		self.squares = np.zeros((8, 8), dtype=Chess_piece)
		self.white_turn = True
		self.kings: List[Optional["King"]] = [None, None]  # [black, white]
		self.checkmate = False
		self.stalemate = False
		self.draw = False
		self.previous_fen: Optional[str] = None
		self.en_passant_pawn: Optional["Pawn"] = None
		self.half_move = 0
		self.full_move = 1
		self.fen_history: Dict[str, int] = {}
		self.move_history: List[str] = []  # stack of FEN strings for multi-undo
		self.dead_piece_count = {
			u'♛': 0,
			u'♜': 0,
			u'♝': 0,
			u'♞': 0,
			u'♟': 0,
			u'♚': 0,
			u'♕': 0,
			u'♖': 0,
			u'♗': 0,
			u'♘': 0,
			u'♙': 0,
			u'♔': 0,
		}

		if fen is not None:
			self.set_fen(fen)
		else:
			self.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

	# -----------------------------------------------------------------
	# Board copying
	# -----------------------------------------------------------------

	def board_copy(self) -> "Board":
		"""Return a deep copy of this board suitable for look-ahead."""
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
		new_board.move_history = self.move_history.copy()

		# Update references in copied pieces
		for row in range(8):
			for col in range(8):
				piece = new_board.squares[row][col]
				if isinstance(piece, Chess_piece):
					piece.update(new_board)
				if isinstance(piece, King):
					if piece.color == Color.BLACK:
						new_board.kings[0] = piece
					else:
						new_board.kings[1] = piece

		return new_board

	# -----------------------------------------------------------------
	# Display
	# -----------------------------------------------------------------

	def display(self, source_x: Optional[int] = None, source_y: Optional[int] = None):
		"""Render the board to the terminal.

		When *source_x* / *source_y* are given the selected piece is
		highlighted and its legal destinations are shown.
		"""
		w, h = shutil.get_terminal_size()
		mid = w // 2 - 34 // 2

		print("\033[2J\033[H", end="")
		print("\n")

		author = "𝓒𝓱𝓮𝓼𝓼 𝓫𝔂 𝓙𝓸𝓱𝓷 𝓔𝓵𝓲𝓪𝓭𝓮𝓼"
		print(author.center(w))
		print()

		# --- Captured white pieces (shown above board) ---
		captured_line = ""
		for pawn, count in self.dead_piece_count.items():
			if pawn in [u'♙', u'♖', u'♘', u'♗', u'♕']:
				captured_line += pawn * count
		if captured_line:
			print((mid - 5) * " " + captured_line)
		else:
			print()

		# --- Board rows ---
		only_start = False
		moves: List[Tuple[int, int]] = []

		if source_x is not None and source_y is not None:
			moves = [
				(m.dest_x, m.dest_y)
				for m in self.squares[source_x][source_y].legal_moves()
			]

		row_num = 8
		for i, row in enumerate(self.squares):
			cur_string = mid * " " + Fore.CYAN + str(row_num) + Style.RESET_ALL + " "

			for j, current in enumerate(row):
				if (i + j) % 2 == 0:
					bg_color = '\x1b[48;5;233m'  # dark grey
				else:
					bg_color = '\x1b[40m'  # black

				if i == source_x and j == source_y:
					cur_string += Back.LIGHTCYAN_EX + " " + str(current) + " " + Style.RESET_ALL
				elif (
					not only_start
					and source_x is not None
					and source_y is not None
					and (i, j) in moves
				):
					if isinstance(self.squares[i][j], Chess_piece):
						if self.squares[source_x][source_y].color != self.squares[i][j].color:
							cur_string += (
								Back.LIGHTRED_EX + " " + str(current) + " " + Style.RESET_ALL
							)
					else:
						cur_string += Back.CYAN + " " + str(current) + " " + Style.RESET_ALL
				else:
					cur_string += bg_color + " " + str(current) + " " + Style.RESET_ALL

			print(cur_string)
			row_num -= 1

		# --- Column letters ---
		letters = mid * " " + "  " + Fore.CYAN
		for letter in "abcdefgh":
			letters += " " + letter + " "
		letters += Style.RESET_ALL
		print(letters)

		# --- Captured black pieces (shown below board) ---
		captured_line = ""
		for pawn, count in self.dead_piece_count.items():
			if pawn in [u'♟', u'♜', u'♞', u'♝', u'♛']:
				captured_line += pawn * count
		if captured_line:
			print((mid - 5) * " " + captured_line)
		else:
			print()

		# --- Status line ---
		fen = self.get_fen()
		turn_label = (Fore.WHITE + "White" if self.white_turn else Fore.LIGHTBLACK_EX + "Black") + Style.RESET_ALL
		status = f"  Move {self.full_move}  ·  {turn_label} to play"

		# Check indicator
		if not self.is_game_over():
			current_king = self.kings[int(self.white_turn)]
			if current_king is not None:
				for piece in self.get_player_pieces(not self.white_turn):
					for sq in piece.attacked_squares():
						if (current_king.x, current_king.y) == (sq[0], sq[1]):
							status += Fore.RED + "  ⚠ CHECK" + Style.RESET_ALL
							break
					else:
						continue
					break

		print(Fore.LIGHTBLACK_EX + status.center(w) + Style.RESET_ALL + "\n")

		fen_line = f"FEN: {fen}"
		print(Fore.LIGHTBLACK_EX + fen_line.center(w) + Style.RESET_ALL + "\n")

	# -----------------------------------------------------------------
	# Notation helpers
	# -----------------------------------------------------------------

	def notation_to_coordinates(self, notation: str, is_rotated: bool) -> Tuple[int, int]:
		"""Convert algebraic notation (e.g. 'e4') to (row, col) indices."""
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

	def coordinates_to_notation(self, row: int, column: int, is_rotated: bool) -> str:
		"""Convert (row, col) indices to algebraic notation."""
		column_map = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
		if is_rotated:
			row = 0 + row
			column = column_map[7 - column]
		else:
			row = 7 - row
			column = column_map[column]
		
		return f"{column}{row+1}"

	# -----------------------------------------------------------------
	# FEN
	# -----------------------------------------------------------------

	def set_fen(self, fen: str):
		"""Set up the board from a FEN string."""
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

	def get_fen(self) -> str:
		"""Return the current position as a FEN string."""
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

	# -----------------------------------------------------------------
	# Piece queries
	# -----------------------------------------------------------------

	def get_player_pieces(self, color) -> List["Chess_piece"]:
		"""Return all pieces belonging to *color*."""
		pieces = []

		for row in range(8):
			for column in range(8):
				if(isinstance(self.squares[row][column], Chess_piece) and
					self.squares[row][column].color == color):

					pieces.append(self.squares[row][column])

		return pieces

	def all_legal_moves(self) -> List["Move"]:
		"""Return every legal move for the side to move."""
		return [move for piece in self.get_player_pieces(self.white_turn) for move in piece.legal_moves()]

	# -----------------------------------------------------------------
	# Move validation (interactive)
	# -----------------------------------------------------------------

	def is_move_valid(self, move):
		"""Validate a long-algebraic move string typed by the user.

		Returns a list ``[source_x, source_y, dest_x, dest_y, promotion]``
		on success, *None* for incomplete input, or raises
		:class:`InvalidMoveException`.
		"""
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

	def push(self, move: "Move"):
		"""Apply *move* to the board, advancing the game state."""
		self.move_history.append(self.get_fen())
		self.previous_fen = self.move_history[-1]

		if self.is_game_over():
			return

		w, h = shutil.get_terminal_size()

		self.squares[move.source_x][move.source_y].play_move(move)

		self.white_turn = not self.white_turn

		all_moves = self.all_legal_moves()
		if len(all_moves) == 0:
			pieces = self.get_player_pieces(not self.white_turn)
			for piece in pieces:
				for attack_move in piece.avail_moves():
					king = self.kings[self.white_turn]
					if (king.x, king.y) == (attack_move.dest_x, attack_move.dest_y):
						self.checkmate = True
						return

			self.stalemate = True
			return

		if self.half_move >= 50:
			# 50-move rule
			self.draw = True
			return

		current_fen = self.get_fen().split()
		# Ignore full-move / half-move clocks for repetition
		current_fen = " ".join(current_fen[:4])
		self.fen_history[current_fen] = self.fen_history.get(current_fen, 0) + 1

		if self.fen_history[current_fen] >= 3:
			# Three-fold repetition
			self.draw = True
			return

	def pop(self):
		"""Undo the last move (supports multiple undos via history)."""
		if self.move_history:
			prev = self.move_history.pop()
			self.checkmate = False
			self.stalemate = False
			self.draw = False
			self.set_fen(prev)
			self.previous_fen = self.move_history[-1] if self.move_history else None

	# -----------------------------------------------------------------
	# Perft (testing)
	# -----------------------------------------------------------------

	def recursion_test(self, depth: int) -> int:
		"""Count leaf nodes at *depth* (perft). Used for move-gen testing."""
		if(depth==0):
			return 1

		num_positions = 0

		pieces = self.get_player_pieces(self.white_turn)

		try:
			moves = [move for piece in pieces for move in piece.legal_moves()]
		except Exception as e:
			self.display()
			print("\r" + traceback.format_exc(), end= "")
			time.sleep(100)

		for move in moves:
			new_board = self.board_copy()

			# new_board.display(move.source_x, move.source_y)
			# time.sleep(0.01)
			new_board.push(move)
			# new_board.display(move.dest_x, move.dest_y)
			# time.sleep(0.01)

			num_positions += new_board.recursion_test(depth-1)

		return num_positions

	# -----------------------------------------------------------------
	# Game-over queries
	# -----------------------------------------------------------------

	def is_checkmate(self) -> bool:
		return self.checkmate

	def is_stalemate(self) -> bool:
		return self.stalemate

	def is_game_over(self) -> bool:
		return self.checkmate or self.stalemate or self.draw


class Color(IntEnum):
	BLACK = 0
	WHITE = 1

class Move:
	"""Represents a single move on the board."""

	def __init__(self, source_x, source_y, dest_x, dest_y, promotion=None):
		self.source_x = source_x
		self.source_y = source_y
		self.dest_x = dest_x
		self.dest_y = dest_y
		if promotion is not None:
			self.promotion = promotion

	def __repr__(self) -> str:
		cols = "abcdefgh"
		src = f"{cols[self.source_y]}{8 - self.source_x}"
		dst = f"{cols[self.dest_y]}{8 - self.dest_x}"
		promo = getattr(self, "promotion", "")
		return f"Move({src}{dst}{promo})"

	def __eq__(self, other):
		if not isinstance(other, Move):
			return NotImplemented
		return (
			self.source_x == other.source_x
			and self.source_y == other.source_y
			and self.dest_x == other.dest_x
			and self.dest_y == other.dest_y
			and getattr(self, "promotion", None) == getattr(other, "promotion", None)
		)

	def __hash__(self):
		return hash((self.source_x, self.source_y, self.dest_x, self.dest_y, getattr(self, "promotion", None)))


class Chess_piece:
	"""Base class for all chess pieces."""

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

	def __repr__(self) -> str:
		return f"{self.__class__.__name__}({self.fen_letter}, {self.x}, {self.y})"

	def update(self, board):
		self.board = board

	def is_enemy_piece(self, test_x, test_y):
		return self.board.squares[test_x][test_y]!=" " and self.board.squares[
			self.x][self.y].color!=self.board.squares[test_x][test_y].color 

	def is_pinned(self):
		piece_position = (self.x, self.y)

		my_king = self.board.kings[self.color]
		king_position = (my_king.x, my_king.y)

		# Get the direction from the piece to the king
		delta_file = king_position[0] - piece_position[0]
		delta_rank = king_position[1] - piece_position[1]

		# Check for diagonal pins (bishop or queen)
		if abs(delta_file) == abs(delta_rank):
			return self.is_pinned_diagonally(piece_position, king_position)

		# Check for orthogonal pins (rook or queen)
		if delta_file == 0 or delta_rank == 0:
			return self.is_pinned_orthogonally(piece_position, king_position)

		# No pin in other directions
		return False

	def is_pinned_diagonally(self, piece_position, king_position):
		delta_file = 1 if king_position[0] > piece_position[0] else -1
		delta_rank = 1 if king_position[1] > piece_position[1] else -1

		current_square = piece_position
		while current_square != king_position:
			current_square = (current_square[0] + delta_file, current_square[1] + delta_rank)

			# Check for a piece in the line
			if(isinstance(self.board.squares[current_square[0]][current_square[1]], Chess_piece)):
				# If the piece is a queen or bishop, it's a pin
				if(isinstance(self.board.squares[current_square[0]][current_square[1]], Queen) or
					isinstance(self.board.squares[current_square[0]][current_square[1]], Bishop)):
					return True
				else:
					break  # There's a piece blocking the line

		return False

	def is_pinned_orthogonally(self, piece_position, king_position):
		if king_position[0] == piece_position[0]:  # Same file
			delta_file = 0
			delta_rank = 1 if king_position[1] > piece_position[1] else -1
		else:  # Same rank
			delta_file = 1 if king_position[0] > piece_position[0] else -1
			delta_rank = 0

		current_square = piece_position
		while current_square != king_position:
			current_square = (current_square[0] + delta_file, current_square[1] + delta_rank)

			# Check for a piece in the line
			if(isinstance(self.board.squares[current_square[0]][current_square[1]], Chess_piece)):
				# If the piece is a queen or rook, it's a pin
				if(isinstance(self.board.squares[current_square[0]][current_square[1]], Queen) or
					isinstance(self.board.squares[current_square[0]][current_square[1]], Rook)):
					return True
				else:
					break  # There's a piece blocking the line

		return False

	def legal_moves(self):
		if(self.board.is_game_over()):
			return []

		moves = self.avail_moves()

		# if(self.is_pinned()):
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
	"""Pawn piece with en-passant, double-push, and promotion logic."""

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
			self.board.squares[self.x][self.y-1]==self.board.en_passant_pawn and move.dest_y==self.y-1):

			self.board.squares[self.x][self.y-1]=" "
	
		elif(all(0 <= value <= 7 for value in (self.y+1,)) and
			self.board.squares[self.x][self.y+1]==self.board.en_passant_pawn and move.dest_y==self.y+1):

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
	"""Rook piece with castling-rights tracking."""

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

	def avail_moves(self):
		values = [
			zip(reversed(range(0, self.x)), [self.y] * self.x),
			zip(range(self.x+1, 8), [self.y] * (8-self.x-1)),
			zip([self.x] * (self.y), reversed(range(0, self.y))),
			zip([self.x] * (8-self.y-1), range(self.y+1, 8))
		]
		
		moves = []
		for direction in values:
			for x, y in direction:
				if(self.board.squares[x][y] == " "):
					moves.append(Move(self.x, self.y, x, y))
				elif(self.board.squares[x][y].color != self.color):
					moves.append(Move(self.x, self.y, x, y))
					break
				else:
					break
		return moves

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
	"""Bishop piece — moves diagonally."""

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

	def avail_moves(self):
		values = [
			zip(reversed(range(0, self.x)), reversed(range(0, self.y))),
			zip(range(self.x+1, 8), range(self.y+1, 8)),
			zip(range(self.x+1, 8), reversed(range(0, self.y))),
			zip(reversed(range(0, self.x)), range(self.y+1, 8))
		]
		moves = []
		for direction in values:
			for x, y in direction:
				if(self.board.squares[x][y] == " "):
					moves.append(Move(self.x, self.y, x, y))
				elif(self.board.squares[x][y].color != self.color):
					moves.append(Move(self.x, self.y, x, y))
					break	
				else:
					break
		return moves

	def play_move(self, move):
		super().play_move(move)


class Knight(Chess_piece):
	"""Knight piece — L-shaped jumps."""
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
	"""Queen piece — combines Rook + Bishop movement."""
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
	"""King piece with castling logic."""
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
	"""Raised when the player enters an illegal or malformed move."""
	pass


# =====================================================================
# Interactive game loop
# =====================================================================

def print_help():
	"""Display available commands."""
	print(Fore.CYAN + "  Commands:" + Style.RESET_ALL)
	print("    e2e4     — move piece from e2 to e4 (k, b, q, r after move for promotion)")
	print("    undo     — take back the last move")
	print("    new      — start a new game")
	print("    perft N  — run perft to depth N")
	print("    help     — show this message")
	print("    quit     — exit the program")
	print()


def main():
	"""Run an interactive chess game in the terminal."""

	# # rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8
	# #for bug test after promotion and checks, recursion depths -> combinations
	# #1 -> 44
	# #2 -> 1486
	# #3 -> 62379
	# #4 -> 2103487
	# #5 -> 89941194

	board = Board("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8")
	board.display()
	print_help()

	while not board.is_game_over():
		turn = Fore.WHITE + "White" + Style.RESET_ALL if board.white_turn else Fore.LIGHTBLACK_EX + "Black" + Style.RESET_ALL
		try:
			user_input = input(f"  {turn}'s move: ").strip().lower()
		except (EOFError, KeyboardInterrupt):
			print("\n  Game ended.")
			return

		if not user_input:
			continue
		elif user_input == "quit":
			print("  Goodbye!")
			return
		elif user_input == "help":
			print_help()
			continue
		elif user_input == "undo":
			board.pop()
			board.display()
			continue
		elif user_input == "new":
			board = Board()
			board.display()
			continue
		elif user_input.startswith("perft"):
			parts = user_input.split()
			depth = int(parts[1]) if len(parts) > 1 else 3
			start = time.time()
			count = board.recursion_test(depth)
			elapsed = round(time.time() - start, 2)
			print(f"  Perft({depth}) = {count:,}  ({elapsed}s)")
			continue
		elif len(user_input) < 4:
			print(Fore.YELLOW + "  Enter a move like e2e4 (or type 'help')" + Style.RESET_ALL)
			continue

		try:
			# Check for inline promotion (e.g. "e7e8q")
			promotion_char = None
			move_str = user_input[:4]
			if len(user_input) >= 5 and user_input[4] in "qrbn":
				promotion_char = user_input[4]

			result = board.is_move_valid(move_str)
			if result is None:
				continue

			source_x, source_y, dest_x, dest_y, needs_promotion = result

			if needs_promotion:
				if promotion_char is None:
					while promotion_char not in ("q", "r", "b", "n"):
						promotion_char = input("  Promote to (q/r/b/n): ").strip().lower()
				result[4] = promotion_char

			move = Move(*result)
			board.push(move)
			board.display()

		except InvalidMoveException as e:
			msg = str(e).strip()
			if msg:
				print(Fore.YELLOW + "  " + msg + Style.RESET_ALL)

	# --- Game over messages ---
	board.display()
	if board.is_checkmate():
		winner = "Black" if board.white_turn else "White"
		print(Fore.GREEN + f"  ♚ Checkmate! {winner} wins!" + Style.RESET_ALL)
	elif board.is_stalemate():
		print(Fore.YELLOW + "  ½ Stalemate — the game is a draw." + Style.RESET_ALL)
	elif board.draw:
		if board.half_move >= 50:
			print(Fore.YELLOW + "  ½ Draw by 50-move rule." + Style.RESET_ALL)
		else:
			print(Fore.YELLOW + "  ½ Draw by three-fold repetition." + Style.RESET_ALL)


if __name__ == "__main__":
	main()


