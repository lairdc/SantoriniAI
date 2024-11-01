import random
import copy
from .Eval import *
from .DictBoard import *
from functools import cache
import multiprocessing


'''
THOUGHTS:

1. Very cool to see it thinking a little bit, will always jump to level 3 when it can, even blocks opp sometimes
2. Dont know why it gets stuck sometimes, theory is all moves are equal value, and doesn't pick one

PERFORMANCE/EFFICIENCY

1. Very very taxing just to calculate with one depth, even alpha-beta pruning wouldnt speed up much, because depth is so low
2. If i can have it try to calculate better moves first, pruning would be more effiecent
3. Rough math of # of calculations be turn: 2 Workers * 9 Moves * 9 Builds = 162 possible moves
	25 tiles * 162 moves = 4050 Calls to evaluate_tile per turn.
	Even a depth of one is crazy:
	162 moves * 162 Moves = 26000 different boards to evaluate
4. Ways to improve:
	-Caching, shouldnt be too hard, similar to DP, but havent done anything like it in a while, nor on this scale
	-alpha-beta pruning, until i can get depth to be around 3+, might not be super efficient
	-Prioritize moves with a higher chance of being 'good' first, like boards where pieces are already on high levels
	-This could take a lot of refactoring but maybe, calculate all moves first, take the top ~10% or something and only look at those move's builds!!
	-Multithreading?!?!
	-


'''

DEPTH = 2
ROWS = 5
COLS = 5
RED = (255, 0, 0)

class ColbysMiniMax:
	def __init__(self, game, own_color, opp_color):
		self.game = game  # Reference to the Game object
		#self.board = Board() SHOULD IMPLEMENT
		if own_color == (255,0,0):
			self.own_color = 'RED'
			self.opp_color = 'BLUE'
		else:
			self.own_color = 'BLUE'
			self.opp_color = 'RED'

	def reset(self):
		self.game = None
		self.board = None
		self.own_color = None
		self.opp_color = None


	def minimax(self, board, depth, alpha, beta, is_maximizing_player):
	    #print(f"minimax is called {depth} {is_maximizing_player}")

	    if depth <= 0 or self.game_over(board):
	        return Eval(board,self.own_color).eval()

	    if is_maximizing_player:  # Bot's turn (Maximizing)
	        max_score = float('-inf')

	        for child in self.organize_children(self.get_children(board, self.own_color),board,self.own_color):
	            score = self.minimax(child, depth - 1, alpha, beta, False)
	            max_score = max(max_score, score)
	            alpha = max(alpha, score)  # Update alpha with the best option so far

	            # Prune if beta is less than or equal to alpha (beta cutoff)
	            if beta <= alpha:
	                break  # No need to explore further
	        return max_score
	    else:  # Opponent's turn (Minimizing)
	        min_score = float('inf')
	        for child in self.organize_children(self.get_children(board, self.opp_color), board, self.opp_color):
	            score = self.minimax(child, depth - 1, alpha, beta, True)
	            min_score = min(min_score, score)
	            beta = min(beta, score)  # Update beta with the best option so far

	            # Prune if beta is less than or equal to alpha (alpha cutoff)
	            if beta <= alpha:
	                break  # No need to explore further
	        return min_score


	def organize_children(self, children, board, turn):
		# Organize children to evaluate better moves first
		better = []
		okay = []
		bad = []

		# Cache old levels once
		old_pieces = board.pieces[turn]
		old_levels = [board.tiles[p][0] for p in old_pieces]

		for c in children:

			new_pieces = c.pieces[turn]
			new_levels = [c.tiles[p][0] for p in new_pieces]

		
			if new_levels[0] > old_levels[0] or new_levels[1] > old_levels[1]:
				better.append(c)
			elif new_levels[0] == old_levels[0] and new_levels[1] == old_levels[1]:
				if (random.randint(0,2) == 1):
					okay.append(c)
			else:
				if (random.randint(0,3) == 1):
					bad.append(c)

		return better + okay + bad


	def game_over(self,board):
		own_pieces = board.pieces[self.own_color]
		opp_pieces = board.pieces[self.opp_color]
		
		for piece in own_pieces:
			if board.tiles[piece][0] == 3:
				return self.own_color
		for piece in opp_pieces:
			if board.tiles[piece][0] == 3:
				return self.opp_color
		return None


	def get_children(self, board, turn): 
		#returns: a list of ordered boards with the ones most 'game-changing' 
		#first so pruning is better
		children = []
		pieces = board.pieces[turn]

		for piece in pieces:
			moves = board.get_all_moves(piece)
			for move in moves:
				new_board, winner, add = self.simulate_move(board,move)
				if winner:
					children = [new_board]
					return children
				elif add:
					children.append(new_board)

		return children

	def get_depth(self, board):
		total_level = 0
		for r in range(ROWS):
			for c in range(COLS):
				total_level += board.tiles[(r,c)][0]

		if total_level <= 10:
			depth = 2
		elif total_level <= 40:
			depth = 3
		else:
			depth = 5

		return depth


	def find_best_move(self, board, color):
		'''
		THis function should find all of the possible moves for the current board,
		call minimax on them, and track which move is the best.
		'''

		best_score = float("-inf")
		best_move = None

		#first find all moves:

		pieces = board.pieces[color]
		for piece in pieces:
			moves = board.get_all_moves(piece)

			for move in moves:
				new_board, trash1, trash2 = self.simulate_move(board,move)
				if self.winning_board(new_board):
					return move
				score = self.minimax(new_board, self.get_depth(board), float('-inf'),float('inf'), False)

				if score > best_score:
					best_score = score 
					best_move = move 
		return best_move

	def winning_board(self, new_board):
		if new_board.tiles[new_board.pieces[self.own_color][0]][0] == 3 or new_board.tiles[new_board.pieces[self.own_color][1]][0] == 3:
			return True
		return False

	def simulate_move(self, board, move):
		board_copy = board.copy()

		starting_pos, move_pos, build_pos = move



		color = board.tiles[starting_pos][1]  # Second value is the color

		# Update the piece's position in the pieces dict
		board_copy.pieces[color].remove(starting_pos)
		board_copy.pieces[color].append(move_pos)

		# Update the tile states
		board_copy.tiles[starting_pos] = (board.tiles[starting_pos][0], None)  # Clear color from starting position
		board_copy.tiles[move_pos] = (board.tiles[move_pos][0], color)  # Set color to the move position
		board_copy.tiles[build_pos] = (board.tiles[build_pos][0] + 1, board.tiles[build_pos][1])  # Increment build level
		if (board.tiles[move_pos][0] == 3):
					return (board_copy,True, True)
		elif (board.tiles[move_pos][0] == 1 or board.tiles[move_pos][0] == 0) and random.randint(0,1) == 1:
			return board_copy, False, True
		return board_copy, False, False 


	def make_move(self): #TODO: maybe need to update
		#can be made more efficient by not remaking the board each turn
		board = self.board_to_dict(self.game.board)


		move = self.find_best_move(board,self.own_color)
		#print(f"move: {move[0][0]} {move[0][1]} {move[1][0]} {move[1][1]} {move[2][0]} {move[2][1]}")
		self.game.select(move[0][0], move[0][1])
		self.game.select(move[1][0], move[1][1])
		self.game.select(move[2][0], move[2][1])	


	def board_to_dict(self,old_board):
		dict_board = DictBoard()
		#key is coordinate tuple (0,0) or (2,3) etc
		#value is tuple of (tile level, piece) example: (1, None) or (2, "RED")
		for row in range(ROWS):
			for col in range(COLS):
				tile_level = old_board.get_tile_level(row, col)
				piece = old_board.get_piece(row, col)
				if piece:
					if piece.color == RED:
						piece_info = 'RED'
						dict_board.pieces['RED'].append((row,col))
					else:
						piece_info = 'BLUE'
						dict_board.pieces['BLUE'].append((row,col))
				else:
					piece_info = None
				
				dict_board.tiles[(row,col)] = (tile_level, piece_info)

		return dict_board








					






