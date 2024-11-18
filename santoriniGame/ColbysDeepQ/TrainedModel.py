import torch as T
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F 
import numpy as np 
import random
#from collections import deque
from .DeepQ import *
from .environment import *
import copy
#from .Eval import *
#from functools import cache
#import multiprocessing
RED = (255, 0, 0)
BLUE = (0,0,255)

class TrainedModel(nn.Module):
	def __init__(self, input_dim, output_dim):
		super(TrainedModel, self).__init__()
		self.fc1 = nn.Linear(input_dim, 128)
		self.fc2 = nn.Linear(128, 128)
		self.fc3 = nn.Linear(128, output_dim)

	def forward(self, x):
		x = x.view(x.size(0), -1)
		x = F.relu(self.fc1(x))
		x = F.relu(self.fc2(x))
		return self.fc3(x)


class TrainedDQN:
	def __init__(self,game, own_color, opp_color, input_dim=50, output_dim=128, model_path="ColbysDeepQ/agent1_model.pth"):
		self.device = T.device("cuda" if T.cuda.is_available() else "cpu")
		self.model = TrainedModel(input_dim, output_dim).to(self.device)
		self.model.load_state_dict(T.load(model_path, map_location=self.device))
		self.model.eval()  # Set the model to evaluation mode
		self.game = game  # Reference to the Game object
		if own_color == (255,0,0):
			self.own_color = 'RED'
			self.opp_color = 'BLUE'
		else:
			self.own_color = 'BLUE'
			self.opp_color = 'RED'

	def get_action(self, state):
		"""Choose the best action based on the current state."""
		state_tensor = T.tensor(state, dtype=T.float32).unsqueeze(0).to(self.device)
		with T.no_grad():  # Disable gradient calculation for inference
			q_values = self.model(state_tensor)
		return T.argmax(q_values).item()

	def convert_board_to_state(self, old_board):
		state = np.zeros((5, 5, 2), dtype=np.int32)
		for row in range(5):
			for col in range(5):
				# Get the level of the tile
				tile_level = old_board.get_tile_level(row, col)
				state[row][col][1] = tile_level

				# Determine if a piece is present and who owns it
				piece = old_board.get_piece(row, col)
				if piece != None:

					if piece.color == RED:
						if self.own_color == 'RED':

							state[row][col][0] = 1  # Player's piece
						else:
							state[row][col][0] = -1  # Opponent's piece
					elif piece.color == BLUE:
						if self.own_color == 'BLUE':

							state[row][col][0] = 1  # Player's piece
						else:
							state[row][col][0] = -1  # Opponent's piece
					else:
						state[row][col][0] = 0  # No piece

		return state

	def convert_action_to_move(self, action_index, state):
		move = []

		piece_num, moveDir, buildDir = unflattenMove(action_index)

		p = 0
		row = None
		col = None
		for r in range(5):
			for c in range(5):
				if state[r][c][0] == 1:
					if p != piece_num:
						p += 1
					else:
						row = r
						col = c
						break
			if row != None:
				break



		move.append([row,col])

		match moveDir:
			case 0:
				row -= 1
			case 1:
				row -= 1
				col += 1
			case 2:
				col += 1
			case 3:
				row += 1
				col += 1
			case 4:
				row += 1
			case 5:
				row += 1
				col -= 1
			case 6:
				col -= 1
			case 7:
				row -= 1
				col -= 1

		move.append([row,col])

		match buildDir:
			case 0:
				row -= 1
			case 1:
				row -= 1
				col += 1
			case 2:
				col += 1
			case 3:
				row += 1
				col += 1
			case 4:
				row += 1
			case 5:
				row += 1
				col -= 1
			case 6:
				col -= 1
			case 7:
				row -= 1
				col -= 1

		move.append([row,col])

		return move





	def check_action_legality(self, action_index, state):
		#print("uh oh is state wrong?")
		#print(state,flush=True)
		legal, trash = checkMove(state,action_index)
		return legal

	def pick_random_move(self):
		return random.randrange(128)


	def make_move(self):
		state = self.convert_board_to_state(self.game.board)
		action = self.get_action(state)
		legal = self.check_action_legality(action,state)
		print(legal," 1 ",flush=True)
		while not legal:
			print(legal, " 2 ",flush=True)
			action = self.pick_random_move()
			legal = self.check_action_legality(action,state)
			print(legal, "3 ",flush=True)
		move = self.convert_action_to_move(action, state)
		self.game.select(move[0][0], move[0][1])
		self.game.select(move[1][0], move[1][1])
		self.game.select(move[2][0], move[2][1])	
		




