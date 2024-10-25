import random
import copy
from .DictBoard import *
import math
import sys


ROWS = 5
COLS = 5
DIRECTIONS = [
				(-1, -1), (-1, 0), (-1, 1),  # Top-left, top, top-right
				(0, -1),         (0, 1),     # Left,         , right
				(1, -1), (1, 0), (1, 1)      # Bottom-left, bottom, bottom-right
			]
LEVEL_VALUES = [0,10,20,50,1]
A = 30
B = 1 
C = 1
D = 1


class Eval:


	'''
	Used to evaluate a board, and can be given constants to alter the scoring


	Things to do:
	1. Only reward building a level if it is accessible
	2. Reward moving up, punish moving down
	3. Reward being in center
	4. Punish building level accessible by opponent
	5. 
	'''

	def __init__(self, board, own_color):
		self.board = board
		self.own_color = own_color
		if own_color == "RED":
			self.opp_color = "BLUE"
		else:
			self.opp_color = "RED"

		
		self.height_const_exp = 1
		self.height_const_coeff = 2
		self.final_const_coeff = 3


	def eval(self):
		'''
		l
		FORMULAS:
		score = total_levels *(sum for all pieces: (2(level) * pos1) + sum for all tiles: (level * pos1) * accessibility + (level * pos2) * pieces_dist)
		METRICS:
		overall:
			total_level: sum of all levels

		tile specific:
			accessibility(a): + if reachable by self, - if reachable by opp
			level: + if higher, (small plus if 4, level 1 is more valuable than 4)
			pos1: higher if center, lower if edges (use numNeighbors)
			pos2: higher if center, lower if edges (use numDoubleNeighbors)
			pieces_dist(d): pos if more self, neg if more opp
			opp_can_win: very neg if true, 0 if not true (only for level 3s)

		LEVEL VALUES:
			0 = 0
			1 = 10
			2 = 20
			3 = 50
			4 = 5




		1. Only reward building a level if it is accessible
		2. Reward moving up, punish moving down
		3. Reward being in center
		4. Punish building level accessible by opponent
		5. Be able to access as many tiles as possible and limit number of tiles opp can access
		'''
		
		total_level = 0
		a_score = 0
		d_score = 0
		own1 = self.board.pieces[self.own_color][0]
		own2 = self.board.pieces[self.own_color][1]
		opp1 = self.board.pieces[self.opp_color][0]
		opp2 = self.board.pieces[self.opp_color][1]
		p_score = self.score_piece(own1)
		p_score += self.score_piece(own2)
		p_score -= self.score_piece(opp1)
		p_score -= self.score_piece(opp2)

		r_score = self.accessible_tiles(own1,own2)
		r_score -= self.accessible_tiles(opp1,opp2)



		for r in range(ROWS):
			for c in range(COLS):
				tile = (r,c)
				level = self.board.tiles[tile][0]
				total_level += level
				a = self.accessibility_mulitplier(own1, own2, opp1, opp2, tile)
				d = self.closest_piece(own1, own2, opp1, opp2, tile)
				a_score += (LEVEL_VALUES[level] * a)
				d_score += d

		if self.opp_can_win():
			return -50000



		"""
		p_score should try to maximize height of own pieces and minimize height of opps esp in center (-600,600)
		a_score prioritze builds that the player can access but the opponent cant - (-300,300) usually (-100,100)
		d_score should try to develop buildings away from the opponent and near itself 
		r_score should try to keep as many tiles modifiable by self and as few modifiable by opp

		THOUGHTS:
		maybe stuff like r_score and d_score shouldn't take into account the oppenents stats? and instead just maximize it self 

		p_score: -650 to 450, hovers around -50 to 50
		a_score: -350 to 350, hovers around -40 to 40
		d_score: -50 to  50,  hovers around -10 to 10
		r_score: -20 to  20,  hovers around 0 until late game
		"""
		#normalizing metrics to about a min/max of +/-10:
		if (p_score != 0):
			p_score = p_score/70
		if (a_score != 0):
			a_score = a_score/35
		if (d_score != 0):
			d_score = d_score/6
		if (r_score != 0):
			r_score = r_score/2

		#the r_score should be more important at higher values, and less important at low values:
		r_score = 0.00045 * (r_score ** 5)
		with open("ColbysMiniMax/score_metrics.txt", "a") as f:
			f.write(f"p_score: {A * p_score}\n")
			f.write(f"a_score: {B * a_score}\n")
			f.write(f"d_score: {C * d_score}\n")
			f.write(f"r_score: {D * r_score}\n\n\n")
		sys.stdout.flush()
		return (A * p_score) + (B * a_score) + (C * d_score) + (D * r_score) * random.uniform(.95,1.05)



	def accessible_tiles(self, piece1, piece2):
		all_moves = self.board.get_all_moves(piece1)
		all_moves += self.board.get_all_moves(piece2)
		accessible_list = [moves[2] for moves in all_moves if len(moves) > 2]

		return len(set(accessible_list))



	def score_piece(self, piece):

		level = self.board.tiles[piece][0]
		if level == 3:
			print(f"yup i can win")
			return 100000
		return LEVEL_VALUES[level]



	def accessibility_mulitplier(self, own1, own2, opp1, opp2, tile):
		if tile == own1 or tile == own2 or tile == opp1 or tile == opp2:
			return 0
		pieces = [own1,own2,opp1,opp2]
		m = 0
		level = self.board.tiles[tile][0]
		if level == 4:
			return 0
		r = tile[0]
		c = tile[1]
		for d in DIRECTIONS:
			r = tile[0]
			c = tile[0]
			r += d[0]
			c += d[1]
			if 0 <= r <= 4 and 0 <= c <= 4:
				if (r,c) in pieces[0:2]:
					if self.board.tiles[(r,c)][0] + 1 >= level:
						m += 0.30 

				elif (r,c) in pieces[2:4]:
					if self.board.tiles[(r,c)][0] + 1 >= level:
						m -= 0.20

		return m

	def closest_piece(self, own1, own2, opp1, opp2, tile):
		dist = 0

		dist += self.dist(own1,tile)
		dist += self.dist(own2,tile)
		dist -= self.dist(opp1,tile)
		dist -= self.dist(opp2,tile)

		return -dist

	def dist(self, p1, p2):

		r1,c1 = p1 
		r2,c2 = p2

		return math.sqrt((r1 - r2)**2 + (c1 - c2)**2)

		




	def opp_can_win(self):
		pieces = self.board.pieces[self.opp_color]

		for piece in pieces:
			if self.board.tiles[piece][0] == 2:
				for d in DIRECTIONS:
					row = piece[0] + d[0]
					col = piece[1] + d[1]
					if 0 <= row <= 4 and 0 <= col < 4:
						if (self.board.tiles[(row,col)] == 3):
							return True

		return False

