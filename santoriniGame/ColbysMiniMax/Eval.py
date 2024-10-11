import random
import copy
from .DictBoard import *


ROWS = 5
COLS = 5
DIRECTIONS = [
				(-1, -1), (-1, 0), (-1, 1),  # Top-left, top, top-right
				(0, -1),         (0, 1),     # Left,         , right
				(1, -1), (1, 0), (1, 1)      # Bottom-left, bottom, bottom-right
			]

class Eval:


	'''
	Used to evaluate a board, and can be given constants to alter the scoring
	'''

	def __init__(self, board, own_color):
		self.board = board
		self.good_color = own_color
		if own_color == "RED":
			self.opp_color = "BLUE"
		else:
			self.opp_color = "RED"

		
		self.height_const_exp = 1
		self.height_const_coeff = 2
		self.final_const_coeff = 3
		self.numNeighbors = [[3, 5, 5, 5, 3], [5, 8, 8, 8, 5],[5, 8, 8, 8, 5],[5, 8, 8, 8, 5], [3, 5, 5, 5, 3]]
		self.numDoubleNeighbors = [[9 , 12, 15, 12, 9 ], [12, 16, 20, 16, 12], [15, 20, 25, 20, 15], [12, 16, 20, 16, 12], [9, 12, 15, 12,  9 ]]


	def eval(self):
		score = 0

		for row in range(ROWS):
			for col in range(COLS):
				tile = (row, col, self.board.tiles[(row,col)][0], self.board.tiles[(row,col)][1])
				score += self.eval_tile(tile)

		if self.opp_can_win():
			score -= 50000

		return score

	def eval_tile(self,tile): 
		score = 0
		row, col, level, piece_present = tile

		if piece_present == self.good_color: #add score
			score += (level * self.numDoubleNeighbors[row][col])
			if level == 3:
				score += 100000
		elif piece_present != None: #subtract score
			score -= (level * self.numDoubleNeighbors[row][col])
			if level == 3:
				score -= 100000
		else:
			if level == 4:
				score += (self.numNeighbors[row][col])
			else:
				score += (level * self.numNeighbors[row][col])

		return score * random.uniform(.95, 1.05)

	def opp_can_win(self):
		pieces = self.board.pieces[self.opp_color]

		for piece in pieces:
			if self.board.tiles[piece][0] == 2:
				for d in DIRECTIONS:
					row = piece[0] + d[0]
					col = piece[0] + d[1]
					if 0 <= row <= 4 and 0 <= col < 4:
						if (self.board.tiles[(row,col)] == 3):
							return True

		return False

