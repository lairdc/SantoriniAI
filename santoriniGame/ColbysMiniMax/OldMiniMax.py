import random
import copy
from santoriniGame.constants import *

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


class OldMiniMax:
	def __init__(self, game, own_color, opp_color):
		self.game = game  # Reference to the Game object
		#self.board = Board() SHOULD IMPLEMENT
		if own_color == RED:
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

	def evaluate_board(self, board, is_maximizing_player): #TODO: this score evaluation is shit
		'''
		Do need old board so it knows when its jumping down
		Also use exponential so 1 -> 2 is worth more than 0 -> 1
		'''
		score = 0

		for row in range(ROWS):
			for col in range(COLS):
				tile = (row, col, board.tiles[(row,col)][0], board.tiles[(row,col)][1])
				score += self.evaluate_tile(tile)
		return score

	def evaluate_tile(self, tile): #TODO: this score evaluation
		score = 0
		row, col, level, piece_present = tile

		if piece_present == self.opp_color:  # Opponent's piece present
			score -= (level * 10)
			if level == 3:
				score -= 10000
		elif piece_present == self.own_color:  # Bot's own piece present
			score += (level * 100)
			if level == 3:
				score += 100000
		else:  # No piece present
			if level == 4:
				score += 25
			else:
				score += level * 25

		#print(f"random")
		return score + random.randint(-10,10)

	def minimax(self, board, depth, alpha, beta, is_maximizing_player):
	    #print(f"minimax is called {depth} {is_maximizing_player}")

	    if depth <= 0 or self.game_over(board):
	        return self.evaluate_board(board, is_maximizing_player)

	    if is_maximizing_player:  # Bot's turn (Maximizing)
	        max_score = float('-inf')
	        for child in self.get_children(board, self.own_color):
	            score = self.minimax(child, depth - 1, alpha, beta, False)
	            max_score = max(max_score, score)
	            alpha = max(alpha, score)  # Update alpha with the best option so far

	            # Prune if beta is less than or equal to alpha (beta cutoff)
	            if beta <= alpha:
	                break  # No need to explore further
	        return max_score
	    else:  # Opponent's turn (Minimizing)
	        min_score = float('inf')
	        for child in self.get_children(board, self.opp_color):
	            score = self.minimax(child, depth - 1, alpha, beta, True)
	            min_score = min(min_score, score)
	            beta = min(beta, score)  # Update beta with the best option so far

	            # Prune if beta is less than or equal to alpha (alpha cutoff)
	            if beta <= alpha:
	                break  # No need to explore further
	        return min_score


	def game_over(self, board): #TODO: must fix
		own_pieces = board.pieces[self.own_color]
		opp_pieces = board.pieces[self.opp_color]
		
		for piece in own_pieces:
			if board.tiles[piece][0] == 3:
				return True
		for piece in opp_pieces:
			if board.tiles[piece][0] == 3:
				return True
		return False

	def get_children(self, board, turn): #TODO: update to new board structure not finished
		children = []
		pieces = board.pieces[turn]

		for piece in pieces:
			moves = board.get_all_moves(piece)
			for move in moves:
				new_board = self.simulate_move(board,move)

				children.append(new_board)

					
		return children 

	def find_best_move(self, board,color):

		best_score = float('-inf')
		best_move = None

		#finding all possible moves this turn
		pieces = board.pieces[color]
		for piece in pieces:
			moves = board.get_all_moves(piece)

			for move in moves:
				new_board = self.simulate_move(board,move)
				score = self.minimax(new_board, 1,float('-inf'),float('inf'), False) #DEPTH

				if score > best_score:
					best_score = score
					best_move = move
		return best_move

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

		return board_copy


	def make_move(self): #TODO: maybe need to update
		#can be made more efficient by not remaking the board each turn
		board = self.board_to_dict(self.game.board)


		move = self.find_best_move(board,self.own_color)
		#print(f"move: {move[0][0]} {move[0][1]} {move[1][0]} {move[1][1]} {move[2][0]} {move[2][1]}")
		self.game.select(move[0][0], move[0][1])
		self.game.select(move[1][0], move[1][1])
		self.game.select(move[2][0], move[2][1])


	def board_to_dict(self,old_board):
		dict_board = self.DictBoard()
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

	class DictBoard:
		def __init__(self): #CHANGE SO BOARD IS SET TO DEFAULT START
			self.tiles = {}
			self.pieces = {

			'RED': [],
			'BLUE': []
			}

		def copy(self):
			return copy.deepcopy(self)

		def get_moves(self, piece: tuple):
			moves = []
			row, col = piece
			directions = [
				(-1, -1), (-1, 0), (-1, 1),  # Top-left, top, top-right
				(0, -1),         (0, 1),     # Left,         , right
				(1, -1), (1, 0), (1, 1)      # Bottom-left, bottom, bottom-right
			]


			for d in directions:
				#d = directions[index]
				new_row = row + d[0]
				new_col = col + d[1]
				if 0 <= new_row <= 4 and 0 <= new_col <= 4:
					if self.tiles[(new_row,new_col)][0] != 4 and self.tiles[(new_row,new_col)][0] <= self.tiles[(row,col)][0] + 1 and self.tiles[(new_row,new_col)][1] == None:
						moves.append((new_row,new_col))

			return moves

		def get_builds(self, piece: tuple, starting_pos: tuple):

			builds = []
			row, col = piece
			directions = [
				(-1, -1), (-1, 0), (-1, 1),  # Top-left, top, top-right
				(0, -1),         (0, 1),     # Left,         , right
				(1, -1), (1, 0), (1, 1)      # Bottom-left, bottom, bottom-right
			]

			chosen_directions = [random.randint(0,7),random.randint(0,7)]

			for index in chosen_directions:
				d = directions[index]
				new_row = row + d[0]
				new_col = col + d[1]
				if 0 <= new_row <= 4 and 0 <= new_col <= 4:
					if self.tiles[(new_row, new_col)][0] != 4 and (self.tiles[(new_row, new_col)][1] == None or self.tiles[(new_row, new_col)][1] == starting_pos):
						builds.append((new_row,new_col))

			return builds

		def get_all_moves(self, piece: tuple):
			all_moves = []
			starting_row, starting_col = piece

			# Get all valid moves for the piece
			valid_moves = self.get_moves(piece)

			for move in valid_moves:
				move_row, move_col = move

				# Get all valid builds after moving
				valid_builds = self.get_builds(move, (starting_row, starting_col))

				for build in valid_builds:
					build_row, build_col = build

					# Append the starting position, move, and build to the all_moves list
					all_moves.append([(starting_row, starting_col), (move_row, move_col), (build_row, build_col)])

			return all_moves
