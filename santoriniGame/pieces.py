import pygame

from constants import *


class Piece:
	PADDING = 15
	BORDER = 2

	def __init__(self, row: int, col: int, color: tuple[int, int, int]):
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
	def get_x(self):
		return self.row

	def get_y(self):
		return self.col

	def draw(self, win: pygame.SurfaceType):
		pygame.draw.circle(win, self.color, (self.x, self.y), PIECE_SIZE)

	def move(self, row: int, col: int, level: int):
		self.row = row
		self.col = col
		self.level = level
		self.calc_pos()

	def __repr__(self):
		return str(self.color)

