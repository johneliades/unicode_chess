from chess import Board
import random

def uci():
	print("id name CustomEngine")
	print("id author johneliades")
	print("uciok")

def isready():
	print("readyok")

def evaluate_board(board):
	# Define piece values
	piece_values = {
		'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0,
		'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9, 'k': 0
	}

	score = 0

	for row in range(8):
		for col in range(8):
			piece = board.board[row][col]
			if(piece != " "):
				score += piece_values.get(piece.fen_letter, 0)
				
				length = len(piece.attacked_squares())
				if(piece.color == 1):
					score += length
				else:
					score -= length

	# Check if the game is in checkmate or stalemate
	if board.is_checkmate():
		if board.white_turn:
			score += -10000  # Black wins
		else:
			score += 10000  # White wins
	elif board.is_stalemate():
		score += 0  # Stalemate, a draw

	return score

def minimax(board, depth, maximizing_player):
	if depth == 0 or board.is_game_over():
		return evaluate_board(board)

	legal_moves = board.legal_moves()

	if maximizing_player:
		max_eval = float("-inf")
		for move in legal_moves:
			if(len(move)<5):
				move = move + (None,)

			new_board = board.board_copy()
			new_board.push(move)
			evalu = minimax(new_board, depth - 1, False)
			max_eval = max(max_eval, evalu)
		return max_eval
	else:
		min_eval = float("inf")
		for move in legal_moves:
			if(len(move)<5):
				move = move + (None,)

			new_board = board.board_copy()
			new_board.push(move)
			evalu = minimax(new_board, depth - 1, True)
			min_eval = min(min_eval, evalu)
		return min_eval

board = Board()

while True:
	try:
		command = input()
		parts = command.split()

		if parts[0] == "uci":
			uci()
		elif parts[0] == "isready":
			isready()
		elif parts[0] == "position":
			fen = parts[2] + " " + " ".join(parts[3:])
			board = Board(fen)
		elif parts[0] == "go":
			legal_moves = board.legal_moves()
			if legal_moves:
				best_move = None
				best_eval = float("-inf")
				for move in legal_moves:
					if(len(move)<5):
						move = move + (None,)
					new_board = board.board_copy()
					new_board.push(move)
					evalu = minimax(new_board, 1, False)
					if evalu > best_eval:
						best_eval = evalu
						best_move = move

				promotion = None
				if(len(best_move)!=4):
					start_x, start_y, end_x, end_y, promotion = best_move
				else:
					start_x, start_y, end_x, end_y = best_move

				start_square = board.coordinates_to_notation(start_x, start_y, False)
				end_square = board.coordinates_to_notation(end_x, end_y, False)
				if promotion:
					result = f"{start_square}{end_square}{promotion.lower()}"
				else:
					result = f"{start_square}{end_square}"

				print(f"bestmove {result}")
			else:
				print("bestmove (none)")

		elif parts[0] == "quit":
			break
	except KeyboardInterrupt:
		break
