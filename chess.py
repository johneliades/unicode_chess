# -*- encoding: utf-8 -*-
import enum
import os
import math
import time
import subprocess
import curses

global board
global white_turn
global fd

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

	def avail_moves(self, start_x, start_y):
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

	def avail_moves(self, start_x, start_y):
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

	def avail_moves(self, start_x, start_y):
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

	def avail_moves(self, x, y):
		moves = [(x+2,y+1), (x-2,y+1), (x+2,y-1), (x-2,y-1), (x+1,y+2), (x-1,y+2), (x+1,y-2), (x-1,y-2)]
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
				if board[cur_x][cur_y].color == board[x][y].color:
					moves.remove(cur_move)
			except:
				pass

		return moves

class queen:
	def __init__(self, color):
		self.color = color

	def __str__(self):
		if(self.color == Color.WHITE):
			return u'♛'
		else:
			return u'♕'

	def avail_moves(self, start_x, start_y):
		moves = []
		moves = rook.avail_moves(self, start_x, start_y)
		moves += bishop.avail_moves(self, start_x, start_y)

		return moves

class king:
	def __init__(self, color):
		self.color = color

	def __str__(self):
		if(self.color == Color.WHITE):
			return u'♚'
		else:
			return u'♔'

	def avail_moves(self, x, y):
		moves = [(x+1,y), (x+1,y+1), (x+1,y-1), (x,y+1), (x,y-1), (x-1,y), (x-1,y+1), (x-1,y-1)]
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
				if board[cur_x][cur_y].color == board[x][y].color:
					moves.remove(cur_move)
			except:
				pass

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

def display_board(stdscr, start_x=None, start_y=None):
	global board

	h, w = stdscr.getmaxyx()

	stdscr.clear()

	author = "𝓒𝓱𝓮𝓼𝓼 𝓫𝔂 𝓙𝓸𝓱𝓷 𝓔𝓵𝓲𝓪𝓭𝓮𝓼"
	x = w//2 - len(author)//2
	y = h//2 - 10
	stdscr.addstr(y, x, author)
	stdscr.refresh()

	total = dead_piece_count[u'♟'] + 3 *\
		(dead_piece_count[u'♞'] + dead_piece_count[u'♝']) +\
		5 * dead_piece_count[u'♜'] + 6 * dead_piece_count[u'♛']

	total = "Points: " + str(total)
	x = 4
	y = 5
	stdscr.addstr(y, x, total)
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
		moves = board[start_x][start_y].avail_moves(start_x, start_y)

	white_cell = True
	for i, row in enumerate(board):
		x = w//2 - 34//2
		cur_string = str(row_num)
		stdscr.addstr(y, x, cur_string)
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
				stdscr.addstr(y, x, cur_string)
				stdscr.attroff(curses.color_pair(1))
			else:
				stdscr.attron(curses.color_pair(2))
				cur_string =  " " + str(current) + "  " 
				stdscr.addstr(y, x, cur_string)
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
	stdscr.addstr(y, x, letters)

	total = dead_piece_count[u'♙'] + 3 *\
		(dead_piece_count[u'♘'] + dead_piece_count[u'♗']) +\
		5 * dead_piece_count[u'♖'] + 6 * dead_piece_count[u'♕']

	total = "Points: " + str(total)
	x = 4
	y += 2
	stdscr.addstr(y, x, total)
	stdscr.refresh()

	x = 4 + len(total) + 1
	for pawn, count in dead_piece_count.items():
		if pawn in [u'♙', u'♖', u'♘', u'♗', u'♕']:
			for i in range(count):
				stdscr.addstr(y, x, pawn)
				x += 2

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

	if(white_turn and board[start_x][start_y].color!=Color.WHITE):
		raise InvalidMoveException("Error: White plays")

	if(not white_turn and board[start_x][start_y].color!=Color.BLACK):
		raise InvalidMoveException("Error: Black plays")

	if(start_x == end_x and start_y == end_y):
		raise InvalidMoveException("Error: Can't move " + str(board[start_x][start_y]) 
			+ "  in same location")

	if(board[end_x][end_y]!=" " and board[start_x][start_y].color == board[end_x][end_y].color):
		raise InvalidMoveException("Error: Can't move " + str(board[start_x][start_y]) + "  on " +\
			str(board[end_x][end_y]) + " (Your piece)")

	moves = board[start_x][start_y].avail_moves(start_x, start_y)
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
		stdscr.addstr(y, x, i * "*")
		stdscr.refresh()

		key = stdscr.getkey()
		if(key == 'KEY_BACKSPACE'):
			if(i>0):
				i-=1
				move = move[:len(move)-1]

			display_board(stdscr)
	
			x = w//2 - 3//2 - 3
			stdscr.addstr(y, x, 4 * " ")
			stdscr.refresh()

			continue

		move.append(key)
		try:
			valid_move = is_valid(stdscr, move)
			i+=1
		except InvalidMoveException as e:
			display_board(stdscr)
			stdscr.addstr(19, 4, str(e))

			x = w//2 - 3//2 - 3
			stdscr.addstr(y, x, 4 * " ")
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

	board[end_x][end_y] = board[start_x][start_y]
	board[start_x][start_y] = " "

	white_turn = not white_turn

def main(stdscr):
	global fd

	curses.curs_set(0)

	while True:
		display_board(stdscr)
		move(stdscr)

init_board()
curses.wrapper(main)