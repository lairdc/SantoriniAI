import random


class Eval:

	'''
	Used to evaluate a board, and can be given constants to alter the scoring
	'''

	#CONSTANTS:

	numNeighbors = [ 3, 5, 5, 5, 3
					 5, 8, 8, 8, 5
					 5, 8, 8, 8, 5
					 5, 8, 8, 8, 5
					 3, 5, 5, 5, 3 ]

	numDoubleNeghbors =   [ 9 , 12, 15, 12, 9 ,
							12, 16, 20, 16, 12,
							15, 20, 25, 20, 15,
							12, 16, 20, 16, 12,
							9, 12, 15, 12,  9  ]

	def __init__(self, board, a, b, c):
		self.board = board
		self.height_const_exp = a
		self.height_const_coeff = b
		self.final_const_coeff = c


	def eval():
		



