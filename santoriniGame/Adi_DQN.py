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

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Modified to use device
        self.model = self.build_model().to(self.device)
        self.target_model = self.build_model().to(self.device)
        self.update_target_model()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        # Added Huber loss
        self.loss_fn = nn.HuberLoss()
        # Added training step counter
        self.training_steps = 0
        self.update_target_frequency = 100

    def build_model(self):
        # Enhanced network architecture
        model = nn.Sequential(
            nn.Linear(self.state_size, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, self.action_size)
        )
        return model
    
    def update_target_model(self):
        for target_param, param in zip(self.target_model.parameters(), self.model.parameters()):
            target_param.data.copy_(param.data)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon: #epsilon greedy action selection
            valid_actions = self.get_valid_actions()
            return random.randrange(self.action_size)  #random action
        state = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            act_values = self.model(state)
        # Added valid action filtering
        valid_actions = self.get_valid_actions()
        valid_q_values = act_values[0][valid_actions]
        return valid_actions[torch.argmax(valid_q_values).item()]

    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        
        # Enhanced batch processing
        minibatch = random.sample(self.memory, self.batch_size)
        states = torch.FloatTensor([data[0] for data in minibatch]).to(self.device)
        actions = torch.LongTensor([data[1] for data in minibatch]).to(self.device)
        rewards = torch.FloatTensor([data[2] for data in minibatch]).to(self.device)
        next_states = torch.FloatTensor([data[3] for data in minibatch]).to(self.device)
        dones = torch.FloatTensor([data[4] for data in minibatch]).to(self.device)

        current_q_values = self.model(states).gather(1, actions.unsqueeze(1))
        with torch.no_grad():
            next_q_values = self.target_model(next_states).max(1)[0]
        target_q_values = rewards + (1 - dones) * self.gamma * next_q_values

        loss = self.loss_fn(current_q_values.squeeze(), target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        # Added gradient clipping
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
        self.optimizer.step()

        # Added periodic target update
        self.training_steps += 1
        if self.training_steps % self.update_target_frequency == 0:
            self.update_target_model()

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
        height_differences = self.calculate_height_differences()
        distances_to_center = self.calculate_distances_to_center()
        cur_game_state.extend(height_differences)
        cur_game_state.extend(distances_to_center)
        return cur_game_state
    
    #helper
    def calculate_height_differences(self):
        differences = []
        board = self.game.board
        own_pieces = board.get_all_pieces(self.own_color)
        for piece in own_pieces:
            row, col = piece.position
            level = board.get_tile_level(row, col)
            adjacent_levels = []
            for dr, dc in [(0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)]:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 5 and 0 <= new_col < 5:
                    adjacent_levels.append(board.get_tile_level(new_row, new_col))
            differences.extend([level - adj for adj in adjacent_levels])
        return differences
    
    #helper
    def calculate_distances_to_center(self):
        distances = []
        board = self.game.board
        center_row, center_col = 2, 2
        own_pieces = board.get_all_pieces(self.own_color)
        for piece in own_pieces:
            row, col = piece.position
            distance = abs(row - center_row) + abs(col - center_col)
            distances.append(distance)
        return distances

    def get_valid_actions(self):
        valid_actions = []
        pieces = self.game.board.get_all_pieces(self.own_color)
        for piece_idx, piece in enumerate(pieces):
            row, col = piece.position
            for move_dir in range(8):
                new_row, new_col = self.get_new_position(row, col, move_dir)
                if self.is_valid_move(new_row, new_col):
                    for build_dir in range(8):
                        build_row, build_col = self.get_new_position(new_row, new_col, build_dir)
                        if self.is_valid_build(build_row, build_col):
                            action_idx = piece_idx * 64 + move_dir * 8 + build_dir
                            valid_actions.append(action_idx)
        return valid_actions
    

    def get_new_position(self, row, col, direction):
        directions = [(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]
        dr, dc = directions[direction]
        return row + dr, col + dc
    

    def is_valid_move(self, row, col):
        return (0 <= row < 5 and 0 <= col < 5 and 
                self.game.board.get_tile_level(row, col) < 4 and 
                not self.game.board.get_piece(row, col))

    # Added helper function for action validation
    def is_valid_build(self, row, col):
        return (0 <= row < 5 and 0 <= col < 5 and 
                self.game.board.get_tile_level(row, col) < 4 and 
                not self.game.board.get_piece(row, col))

    def evaluate_reward(self, move_result, build_result):
        reward = 0
        if move_result == 'win':
            reward += 100
        elif build_result == 'block_opponent':
            reward += 20
        elif move_result == 'progress':
            reward += 10
            
        # Added additional reward components
        state = self.get_cur_game_state()
        height_reward = sum(self.calculate_height_differences()) * 2
        center_penalty = sum(self.calculate_distances_to_center()) * -1
        reward += height_reward + center_penalty
        
        return reward

    def get_action_space(self):
        #create a simplified action space, for example:
        #action format: (piece_idx, move_direction, build_direction)
        return [(i, j, k) for i in range(2) for j in range(8) for k in range(8)]

    def step(self):
        state = self.get_cur_game_state()
        action = self.act(state)
        # Modified action unpacking for new action space
        piece_idx = action // 64
        move_dir = (action % 64) // 8
        build_dir = action % 8
        
        piece = self.game.board.get_all_pieces(self.own_color)[piece_idx]
        move_result = self.game.board.move_piece_in_direction(piece, move_dir)
        build_result = self.game.board.build_in_direction(piece, build_dir)
        
        reward = self.evaluate_reward(move_result, build_result)
        next_state = self.get_cur_game_state()
        done = self.game.is_game_over()
        
        self.remember(state, action, reward, next_state, done)
        self.replay()
    


