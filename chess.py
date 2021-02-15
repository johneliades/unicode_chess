# -*- encoding: utf-8 -*-
import enum
import os
import math
import time
import subprocess
import curses
import numpy as np
global board
global white_turn
global fd

white_turn = True
fen_starting_position = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

class Color(enum.Enum):
	WHITE = 0
	BLACK = 1

class chess_piece:
	def __str__(self):
		return self.str

	def play_move(self, end_x, end_y):
		board[end_x][end_y] = board[self.x][self.y]
		board[self.x][self.y] = " "
		self.x = end_x
		self.y = end_y

class pawn(chess_piece):
	def __init__(self, color):
		self.color = color
		if(color == Color.WHITE):
			self.fen_letter = "P"
			self.str = u'♟'
		else:
			self.fen_letter = "p"
			self.str = u'♙'

	def avail_moves(self):
		moves = []

		start_x = self.x
		start_y = self.y

		if(board[start_x][start_y].color == Color.WHITE):
			direction = 1
			starting_row = 6
		else:
			direction = -1
			starting_row = 1

		if(board[start_x-1*direction][start_y]==" "):
			moves.append((start_x - 1*direction, start_y))
			if(board[start_x-2*direction][start_y]==" " 
				and start_x==starting_row):
				
				moves.append((start_x - 2*direction, start_y))

		if(board[start_x-1*direction][start_y-1]!=" " and
			board[start_x-1*direction][start_y-1].color!=board[start_x][start_y].color):

				moves.append((start_x-1*direction, start_y-1))

		if(board[start_x-1*direction][start_y+1]!=" " and
			board[start_x-1*direction][start_y+1].color!=board[start_x][start_y].color):

				moves.append((start_x-1*direction, start_y+1))

		return moves

	def play_move(self, end_x, end_y):
		super().play_move(end_x, end_y)

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
		start_x = self.x
		start_y = self.y

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
		start_x = self.x
		start_y = self.y

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
		start_x = self.x
		start_y = self.y

		moves = [(start_x+2,start_y+1), 
				(start_x-2,start_y+1), 
				(start_x+2,start_y-1), 
				(start_x-2,start_y-1), 
				(start_x+1,start_y+2), 
				(start_x-1,start_y+2), 
				(start_x+1,start_y-2), 
				(start_x-1,start_y-2)]
		
		for cur_move in reversed(moves):
			cur_x = cur_move[0]
			cur_y = cur_move[1]

			# Remove out of range moves
			try:
				board[cur_x][cur_y]
			except:
				moves.remove(cur_move)
				continue
	
			# Don't remove moves to empty cell
			try:
				# Remove moves on your pieces
				if board[cur_x][cur_y].color == board[start_x][start_y].color:
					moves.remove(cur_move)
			except:
				pass

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
		start_x = self.x
		start_y = self.y

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
		start_x = self.x
		start_y = self.y

		moves = [(start_x+1,start_y), 
				(start_x+1,start_y+1), 
				(start_x+1,start_y-1), 
				(start_x,start_y+1), 
				(start_x,start_y-1), 
				(start_x-1,start_y),
				(start_x-1,start_y+1), 
				(start_x-1,start_y-1)]
	
		for cur_move in reversed(moves):
			cur_x = cur_move[0]
			cur_y = cur_move[1]

			# Remove out of range moves
			try:
				board[cur_x][cur_y]
			except:
				moves.remove(cur_move)
				continue
	
			# Don't remove moves to empty cell
			try:
				# Remove moves on your pieces
				if board[cur_x][cur_y].color == board[start_x][start_y].color:
					moves.remove(cur_move)
			except:
				pass

		if(board[start_x][start_y].has_moved==False and 
			board[start_x][start_y-1]==" " and
			board[start_x][start_y-2]==" " and
			board[start_x][start_y-3]==" " and
			board[start_x][start_y-4]!=" " and
			board[start_x][start_y-4].color==board[start_x][start_y].color and
			board[start_x][start_y-4].has_moved==False):
	
			moves.append((start_x, start_y-2))

		if(board[start_x][start_y].has_moved==False and 
			board[start_x][start_y+1]==" " and
			board[start_x][start_y+2]==" " and
			board[start_x][start_y+3]!=" " and
			board[start_x][start_y+3].color==board[start_x][start_y].color and
			board[start_x][start_y+3].has_moved==False):
	
			moves.append((start_x, start_y+2))

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

	return fen

def init_board():
	global board
	
	board = np.zeros((8, 8), dtype = chess_piece) 

	row = 0
	column = 0

	for char in fen_starting_position.split()[0]:
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

			board[row][column].x = row
			board[row][column].y = column
			column+=1

def display_board(stdscr, start_x=None, start_y=None):
	global board

	h, w = stdscr.getmaxyx()

	stdscr.clear()

	author = "𝓒𝓱𝓮𝓼𝓼 𝓫𝔂 𝓙𝓸𝓱𝓷 𝓔𝓵𝓲𝓪𝓭𝓮𝓼"
	x = w//2 - len(author)//2
	y = 2
	try:
		stdscr.addstr(y, x, author)
	except curses.error:
		pass
	stdscr.refresh()

	total = dead_piece_count[u'♟'] + 3 *\
		(dead_piece_count[u'♞'] + dead_piece_count[u'♝']) +\
		5 * dead_piece_count[u'♜'] + 6 * dead_piece_count[u'♛']

	total = "Points: " + str(total)
	x = 4
	y = 5
	try:
		stdscr.addstr(y, x, total)
	except curses.error:
		pass

	stdscr.refresh()

	x = 4 + len(total) + 1
	for pawn, count in dead_piece_count.items():
		if pawn in [u'♟', u'♜', u'♞', u'♝', u'♛']:
			y = 5

			for i in range(count):
				stdscr.addstr(y, x, pawn)
				x += 2
			
	stdscr.refresh()

	row_num = 8

	curses.init_pair(1, curses.COLOR_WHITE, 233)
	curses.init_pair(2, curses.COLOR_WHITE, 240)
	curses.init_pair(3, curses.COLOR_WHITE, 23)
	curses.init_pair(4, curses.COLOR_WHITE, 45)
	curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)
	
	y = 7
	
	if(start_x!=None and start_y!=None):
		moves = board[start_x][start_y].avail_moves()

	white_cell = False
	for i, row in enumerate(board):
		x = w//2 - 34//2
		cur_string = str(row_num)
		try:
			stdscr.addstr(y, x, cur_string)
		except curses.error:
			pass
		stdscr.refresh()

		x+=2

		for j, current in enumerate(row):
			if(i==start_x and j==start_y):
				stdscr.attron(curses.color_pair(3))
				cur_string =  " " + str(current) + "  " 
				stdscr.addstr(y, x, cur_string)
				stdscr.attroff(curses.color_pair(3))
			elif(start_x!=None and start_y!=None and (i, j) in moves):
				try:
					if(board[start_x][start_y].color!=board[i][j].color):
						stdscr.attron(curses.color_pair(5))
						cur_string =  " " + str(current) + "  " 
						stdscr.addstr(y, x, cur_string)
						stdscr.attroff(curses.color_pair(5))					
				except:
					stdscr.attron(curses.color_pair(4))
					cur_string =  " " + str(current) + "  " 
					stdscr.addstr(y, x, cur_string)
					stdscr.attroff(curses.color_pair(4))
			elif(white_cell):
				stdscr.attron(curses.color_pair(1))
				cur_string =  " " + str(current) + "  " 
				try:
					stdscr.addstr(y, x, cur_string)
				except curses.error:
					pass
				stdscr.attroff(curses.color_pair(1))
			else:
				stdscr.attron(curses.color_pair(2))
				cur_string =  " " + str(current) + "  " 
				try:
					stdscr.addstr(y, x, cur_string)
				except curses.error:
					pass
				stdscr.attroff(curses.color_pair(2))
			
			x+=len(cur_string)

			stdscr.refresh()
			white_cell = not white_cell

		y+=1

		white_cell = not white_cell
		row_num -= 1

	letters = ""
	for letter in [u'\uff41', u'\uff42', u'\uff43', u'\uff44', u'\uff45', u'\uff46', u'\uff47', u'\uff48']:
		letters += letter + "  "

	letters += "    "

	x = w//2 - len(letters)//2
	try:
		stdscr.addstr(y, x, letters)
	except curses.error:
		pass

	total = dead_piece_count[u'♙'] + 3 *\
		(dead_piece_count[u'♘'] + dead_piece_count[u'♗']) +\
		5 * dead_piece_count[u'♖'] + 6 * dead_piece_count[u'♕']

	total = "Points: " + str(total)
	x = 4
	y += 2
	
	try:
		stdscr.addstr(y, x, total)
	except curses.error:
		pass
	stdscr.refresh()

	x = 4 + len(total) + 1
	for pawn, count in dead_piece_count.items():
		if pawn in [u'♙', u'♖', u'♘', u'♗', u'♕']:
			for i in range(count):
				stdscr.addstr(y, x, pawn)
				x += 2

	y+=2
	
	fen = calculate_fen()

	x = w//2 - len("FEN: " + fen)//2 - 3
	try:
		stdscr.addstr(y, x, "FEN: " + fen)
	except curses.error:
		pass

	stdscr.refresh()

def is_valid(stdscr, move):
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

	display_board(stdscr, start_x, start_y)

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

def move(stdscr):
	global white_turn

	h, w = stdscr.getmaxyx()

	move = []
	y=21
	i=0
	while(len(move)!=4):
		x = w//2 - len("***")//2 - 3
		try:
			stdscr.addstr(y, x, i * "*")
		except curses.error:
			pass
		stdscr.refresh()

		key = stdscr.getkey()
		if(key == 'KEY_BACKSPACE' or key == 'KEY_RESIZE'):
			if(i>0):
				i-=1
				move = move[:len(move)-1]

			display_board(stdscr)
	
			x = w//2 - 3//2 - 3
			
			try:
				stdscr.addstr(y, 0, w * " ")
			except curses.error:
				pass

			stdscr.refresh()

			continue
		elif(len(key)!=1):
			continue

		move.append(key)
		try:
			valid_move = is_valid(stdscr, move)
			stdscr.addstr(y, 0, w * " ")
			i+=1
		except InvalidMoveException as e:
			display_board(stdscr)

			x = w//2 - 3//2 - 3
			stdscr.addstr(y, 0, w * " ")
			stdscr.addstr(y, 4, str(e))
			stdscr.refresh()

			i=0
			move.clear()

	stdscr.refresh()

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

def main(stdscr):
	global fd

	curses.curs_set(0)

	while True:
		display_board(stdscr)
		move(stdscr)

init_board()
curses.wrapper(main)