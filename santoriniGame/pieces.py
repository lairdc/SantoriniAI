import pygame
from constants import *

class Piece:
	PADDING = 15
	BORDER = 2

	def __init__(self,row,col,color):
		self.row = row
		self.col = col
		self.color = color
		self.level = 0

		self.x = 0
		self.y = 0
		self.calc_pos()

	def calc_pos(self):
		self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
		self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

	def draw(self, win):
		radius = SQUARE_SIZE//2 - self.PADDING
		pygame.draw.circle(win, self.color, (self.x, self.y), radius)

	def move(self,row,col,level):
		self.row = row
		self.col = col
		self.level = level
		self.calc_pos()

	def __repr__(self):
		return str(self.color)


