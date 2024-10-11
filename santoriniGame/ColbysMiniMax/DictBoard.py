import random
import copy



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

		for d in directions:
			#d = directions[index]
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