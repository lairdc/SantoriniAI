import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque


# Key Steps for the DQN Algorithm

#1.	state representation: encode the board state into a format compatible with the neural network
#2.	action selection: use an epsilon greedy policy for exploration
#3.	experience replay: store transitions in memory and sample mini batches for training
#4.	Q-Learning with neural network: update Q-values using a neural network

class DQNSantoriniAgent:
    def __init__(self, game, own_color, opp_color, state_size=100, action_size=50, gamma=0.95, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, learning_rate=0.001, batch_size=32):
        self.game = game
        self.own_color = own_color
        self.opp_color = opp_color
        self.state_size = state_size
        self.action_size = action_size #possible actions
        self.gamma = gamma  #discount factor
        self.epsilon = epsilon  #exploration rate
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.memory = deque(maxlen=2000)

        self.model = self.build_model()
        self.target_model = self.build_model()
        self.update_target_model()

        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)

    def build_model(self):
        model = nn.Sequential(
            nn.Linear(self.state_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, self.action_size)
        )
        return model
    
    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon: #epsilon greedy action selection
            return random.randrange(self.action_size)  #random action
        state = torch.FloatTensor(state).unsqueeze(0)
        act_values = self.model(state)
        return torch.argmax(act_values).item()  #acction with highest Q value

    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        minibatch = random.sample(self.memory, self.batch_size)
        for state, action, reward, next_state, done in minibatch:
            state = torch.FloatTensor(state).unsqueeze(0)
            next_state = torch.FloatTensor(next_state).unsqueeze(0)
            target = reward
            if not done:
                target = reward + self.gamma * torch.max(self.target_model(next_state)[0]).item()
            target_f = self.model(state)
            target_f[0][action] = target
            self.optimizer.zero_grad()
            loss = nn.functional.mse_loss(self.model(state), target_f)
            loss.backward()
            self.optimizer.step()
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def get_cur_game_state(self):
        cur_game_state = []
        board = self.game.board
        for row in range(5):
            for col in range(5):
                level = board.get_tile_level(row, col)
                piece = board.get_piece(row, col)
                piece_present = 0
                if piece:
                    if piece.color == self.own_color:
                        piece_present = 1
                    elif piece.color == self.opp_color:
                        piece_present = 2
                cur_game_state.extend([row, col, level, piece_present])
        return cur_game_state
    
    def get_action_space(self):
        #create a simplified action space, for example:
        #action format: (piece_idx, move_direction, build_direction)
        return [(i, j, k) for i in range(2) for j in range(8) for k in range(8)]

    def step(self):
        #get the current state
        state = self.get_cur_game_state()
        #choose an action
        action = self.act(state)
        #execute the  action
        piece_idx, move_dir, build_dir = self.get_action_space()[action]
        piece = self.game.board.get_all_pieces(self.own_color)[piece_idx]
        #move and build
        move_result = self.game.board.move_piece_in_direction(piece, move_dir)
        build_result = self.game.board.build_in_direction(piece, build_dir)
        #check win conditions and assign reward
        reward = self.evaluate_reward(move_result, build_result)
        next_state = self.get_cur_game_state()
        done = self.game.is_game_over()
        #remember and replay
        self.remember(state, action, reward, next_state, done)
        self.replay()
        #update target model periodically
        if self.game.move_count % 10 == 0:
            self.update_target_model()
    
    def evaluate_reward(self, move_result, build_result):
        reward = 0
        if move_result == 'win':
            reward += 100
        elif build_result == 'block_opponent':
            reward += 20
        elif move_result == 'progress':
            reward += 10
        return reward