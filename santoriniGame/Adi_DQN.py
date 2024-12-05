import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import os
import pygame


class Bot:
    def __init__(self, game, own_color: tuple[int, int, int], opp_color: tuple[int, int, int], use_dqn=False):
        self.game = game
        self.own_color = own_color
        self.opp_color = opp_color
        
        if use_dqn:
            self.agent = DQNSantoriniAgent(
                game=game,
                own_color=own_color,
                opp_color=opp_color,
                state_size=118,
                action_size=128
            )
            self.agent.load_model('santorini_model.pth')
            self.use_dqn = True
        else:
            self.use_dqn = False

    def make_move(self):
        if self.use_dqn:
            self.agent.step()
        else:
            self._make_random_move()

    def _make_random_move(self):
        own_pieces = self.game.board.get_all_pieces(self.own_color)
        if not own_pieces:
            return

        piece = random.choice(own_pieces)
        valid_moves = self.game.board.get_valid_moves(piece)

        if valid_moves:
            move = random.choice(list(valid_moves))
            row, col = move
            if self.game.select(piece.row, piece.col):
                self.game._move(row, col)
                
                valid_builds = self.game.board.get_valid_builds(self.game.selected)
                if valid_builds:
                    build = random.choice(list(valid_builds))
                    build_row, build_col = build
                    self.game._build(build_row, build_col)
                self.game.selected = None

    def get_cur_game_state(self):
        curGameState = []
        for row in range(5):
            for col in range(5):
                level = self.game.board.get_tile_level(row, col)
                piece = self.game.board.get_piece(row, col)
                piece_present = 0
                if piece:
                    if piece.color == self.own_color:
                        piece_present = 1
                    elif piece.color == self.opp_color:
                        piece_present = 2
                curGameState.extend([row, col, level, piece_present])
        return curGameState


# Key Steps for the DQN Algorithm

#1.	state representation: encode the board state into a format compatible with the neural network
#2.	action selection: use an epsilon greedy policy for exploration
#3.	experience replay: store transitions in memory and sample mini batches for training
#4.	Q-Learning with neural network: update Q-values using a neural network

class DQNSantoriniAgent:
    def __init__(self, game, own_color, opp_color, state_size=118, action_size=50, gamma=0.95, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, learning_rate=0.001, batch_size=32):
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
        
        #batch processing
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
        # gradient clipping
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
        self.optimizer.step()

        #periodic target update
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
            row, col = piece.row, piece.col
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
            row, col = piece.row, piece.col
            distance = abs(row - center_row) + abs(col - center_col)
            distances.append(distance)
        return distances

    def get_valid_actions(self):
        valid_actions = []
        pieces = self.game.board.get_all_pieces(self.own_color)
        for piece_idx, piece in enumerate(pieces):
            row, col = piece.row, piece.col
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

    

    def get_action_space(self):
        #create a simplified action space, for example:
        #action format: (piece_idx, move_direction, build_direction)
        return [(i, j, k) for i in range(2) for j in range(8) for k in range(8)]

    def step(self):
        print(f"AI making move... Epsilon: {self.epsilon:.4f}, Training steps: {self.training_steps}")
        state = self.get_cur_game_state()
        action = self.act(state)
        piece_idx = action // 64
        move_dir = (action % 64) // 8
        build_dir = action % 8
        
        own_pieces = self.game.board.get_all_pieces(self.own_color)
        if not own_pieces or piece_idx >= len(own_pieces):
            return
            
        piece = own_pieces[piece_idx]
        
        if not self.game.select(piece.row, piece.col):
            return
            
        new_row = piece.row + [-1, -1, 0, 1, 1, 1, 0, -1][move_dir]
        new_col = piece.col + [0, 1, 1, 1, 0, -1, -1, -1][move_dir]
        
        if not self.game._move(new_row, new_col):
            self.game.selected = None
            return
        
        build_row = new_row + [-1, -1, 0, 1, 1, 1, 0, -1][build_dir]
        build_col = new_col + [0, 1, 1, 1, 0, -1, -1, -1][build_dir]
        if 0 <= build_row < 5 and 0 <= build_col < 5:
            self.game._build(build_row, build_col)
        
        #self.game._build(build_row, build_col)
        self.game.selected = None
        
        reward = self.evaluate_reward()
        next_state = self.get_cur_game_state()
        done = self.game.game_over is not None
        
        self.remember(state, action, reward, next_state, done)
        self.replay()

        # Save model if game is over (we have a winner)
        if done:
            self.save_model()

    def evaluate_reward(self):
        reward = 0
        # Win/Loss zrewards
        if self.game.game_over == self.own_color:
            return 100  #immediate win is best reward
        elif self.game.game_over == self.opp_color:
            return -100  #immediate loss is worst reward
        board = self.game.board
        own_pieces = board.get_all_pieces(self.own_color)
        opp_pieces = board.get_all_pieces(self.opp_color)
        for piece in own_pieces:
            row, col = piece.row, piece.col
            current_level = board.get_tile_level(row, col)
            reward += current_level * 5  # More points for being higher
            #extra reward for being on level 2 (one move away from winning)
            if current_level == 2:
                reward += 10
            #check for potential winning moves
            for dr, dc in [(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 5 and 0 <= new_col < 5:
                    if board.get_tile_level(new_row, new_col) == 3:
                        if not board.get_piece(new_row, new_col):
                            reward += 15
        #penalize for opponent's good positions
        for piece in opp_pieces:
            row, col = piece.row, piece.col
            opp_level = board.get_tile_level(row, col)  
            #penalize for opponent height
            reward -= opp_level * 3
            #extra penalty if opponent is on level 2
            if opp_level == 2:
                reward -= 8
            #check if opponent has potential winning moves
            for dr, dc in [(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 5 and 0 <= new_col < 5:
                    if board.get_tile_level(new_row, new_col) == 3:
                        if not board.get_piece(new_row, new_col):
                            reward -= 15  #big penalty if opponent can win
        #strategic position rewards
        center_control = 0
        center_positions = [(2,2), (1,2), (2,1), (2,3), (3,2)]
        for row, col in center_positions:
            piece = board.get_piece(row, col)
            if piece and piece.color == self.own_color:
                center_control += 1
            elif piece and piece.color == self.opp_color:
                center_control -= 1
        reward += center_control * 2  #reward for controlling center
        #reeward for keeping workers close to each other
        if len(own_pieces) == 2:
            p1_row, p1_col = own_pieces[0].row, own_pieces[0].col
            p2_row, p2_col = own_pieces[1].row, own_pieces[0].col
            distance = abs(p1_row - p2_row) + abs(p1_col - p2_col)
            if distance <= 2:  #workers supporting each other
                reward += 5
        return reward
    
    def save_model(self, filename='santorini_model.pth'):
        """Save the model, optimizer state, and memory"""
        try:
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'target_model_state_dict': self.target_model.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'epsilon': self.epsilon,
                'memory': list(self.memory),
                'training_steps': self.training_steps
            }, filename)
            print(f"=== Model Saved Successfully ===")
            print(f"Saved to: {filename}")
            print(f"Training steps: {self.training_steps}")
            print(f"Current epsilon: {self.epsilon:.4f}")
            print(f"Memory size: {len(self.memory)}\n")
        except Exception as e:
            print(f"Error saving model: {e}")

    def load_model(self, filename='santorini_model.pth'):
        """Load the model if it exists"""
        if os.path.exists(filename):
            print(f"\n=== Loading Existing Model ===")
            try:
                checkpoint = torch.load(filename)
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.target_model.load_state_dict(checkpoint['target_model_state_dict'])
                self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
                self.epsilon = checkpoint['epsilon']
                self.memory = deque(checkpoint['memory'], maxlen=2000)
                self.training_steps = checkpoint['training_steps']
                print(f"Model loaded successfully!")
                print(f"Loaded training steps: {self.training_steps}")
                print(f"Loaded epsilon: {self.epsilon:.4f}")
                print(f"Loaded memory size: {len(self.memory)}\n")
            except Exception as e:
                print(f"Error loading model: {e}\n")
        else:
            print("\n=== No existing model found, starting fresh ===\n")


from game import Game

def train_dqn_bot(num_episodes=1000):
    pygame.init()  # Initialize pygame
    win = pygame.Surface((800, 800))  # Create a dummy surface
    game = Game(win)
    bot = Bot(game, own_color=(255, 0, 0), opp_color=(0, 0, 255), use_dqn=True)
    opponent = Bot(game, own_color=(0, 0, 255), opp_color=(255, 0, 0), use_dqn=False)
    
    for episode in range(num_episodes):
        game.reset()
        done = False
        while not done:
            bot.make_move()
            if game.game_over is not None:
                done = True
                continue
            opponent.make_move()
            if game.game_over is not None:
                done = True
        print(f"Episode {episode+1}/{num_episodes} completed")

if __name__ == "__main__":
    train_dqn_bot()