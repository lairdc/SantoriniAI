import random



ROWS = 5
COLS = 5


class Eval:


	'''
	Used to evaluate a board, and can be given constants to alter the scoring
	'''

	#CONSTANTS:

	numNeigbors = [[3, 5, 5, 5, 3], [5, 8, 8, 8, 5],[5, 8, 8, 8, 5],[5, 8, 8, 8, 5], [3, 5, 5, 5, 3]]

	numDoubleNeghbors = [[9 , 12, 15, 12, 9 ], [12, 16, 20, 16, 12], [15, 20, 25, 20, 15], [12, 16, 20, 16, 12], [9, 12, 15, 12,  9 ]]

	def __init__(self, board, own_color):
		self.board = board
		self.good_color = own_color
		self.height_const_exp = 1
		self.height_const_coeff = 2
		self.final_const_coeff = 3


	def eval(self):
		score = 0

		for row in range(ROWS):
			for col in range(COLS):
				tile = (row, col, self.board.tiles[(row,col)][0], self.board.tiles[(row,col)][1])
				score += self.eval_tile(tile)

		return score

	def eval_tile(self, tile): 
		score = 0
		row, col, level, piece_present = tile

		if piece_present == self.good_color: #add score
			score += (level * numDoubleNeigbors)
			if level == 3:
				score += 100000
		elif piece_present != None: #subtract score
			score -= (level * numDoubleNeigbors)
			if level == 3:
				score -= 100000
		else:
			if level == 4:
				score += (numNeigbors)
			else:
				score += (level * numNeigbors)

		return score

		



