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
        self.game = game  #reference to the Game object
        self.own_color = own_color
        self.opp_color = opp_color
        self.state_size = state_size  #size of the encoded board state
        self.action_size = action_size  #number of possible actions
        self.gamma = gamma  #discount factor
        self.epsilon = epsilon  #exploration rate
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.memory = deque(maxlen=2000)
        
        #Neural networks
        self.model = self.build_model()
        self.target_model = self.build_model()
        self.update_target_model()
        
        #optimizer
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
