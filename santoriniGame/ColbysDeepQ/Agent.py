import torch as T 
import torch.nn as nn
import torch.nn.functional as F 
import torch.optim as optim
import numpy as np 
import random
from DeepQ import DeepQ

class Agent:
    def __init__(self, deep_q, action_size, batch_size=32):
        self.deep_q = deep_q
        self.action_size = action_size  # Number of possible actions
        self.batch_size = batch_size

    def act(self, state):
        # Epsilon-greedy policy for exploration and exploitation
        if np.random.rand() <= self.deep_q.epsilon:
            return random.randrange(self.action_size)  # Explore
        else:
            state = T.tensor(state, dtype=T.float32).unsqueeze(0)
            q_values = self.deep_q.model(state)  # Forward pass through the Q-network
            return T.argmax(q_values).item()  # Exploit best action

    def learn(self, state, action, reward, next_state, done):
        # Store the experience in replay memory
        self.deep_q.remember(state, action, reward, next_state, done)

        # Train on a batch if there are enough samples in memory
        if len(self.deep_q.memory) >= self.batch_size:
            self.deep_q.replay(batch_size=self.batch_size)

        # Decay epsilon if the episode has ended
        if done:
            self.deep_q.decay_epsilon()
