import torch as T
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
import torch.nn as nn
import torch.nn.functional as F
from DeepQ import DeepQ
import environment


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
    def __init__(self,game, own_color, opp_color, input_dim=50, output_dim=128, model_path="agent1_model.pth"):
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

	def reset(self):
		self.game = None
		self.board = None
		self.own_color = None
		self.opp_color = None

    def get_action(self, state):
        """Choose the best action based on the current state."""
        state_tensor = T.tensor(state, dtype=T.float32).unsqueeze(0).to(self.device)
        with T.no_grad():  # Disable gradient calculation for inference
            q_values = self.model(state_tensor)
        return T.argmax(q_values).item()

    def convert_board_to_state(self, board):
        """Convert the game board into the appropriate input state."""
        # TODO: Implement logic based on how the board is represented
        pass

    def convert_action_to_move(self, action_index):
        """Convert action index into game-specific move details."""
        # TODO: Implement logic based on your game's action encoding
        pass

    def check_action_legality(self, action_index, state):
    	pass

    def pick_random_legal_move(self, state):


    def make_move():



