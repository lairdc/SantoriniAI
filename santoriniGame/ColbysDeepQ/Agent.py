import torch as T 
import torch.nn as nn
import torch.nn.functional as F 
import torch.optim as optim
import numpy as np 
import random
from DeepQ import DeepQ
from environment import *

class Agent:
    def __init__(self, deep_q, action_size, batch_size=32):
        self.deep_q = deep_q #deepQ class
        self.action_size = action_size  # Number of possible actions
        self.batch_size = batch_size #batch size - 

    def act(self, state):
        
        # Epsilon-greedy policy for exploration and exploitation
        count = 0
        while True:
            count += 1
            if count == 10000:
                print("stuck!")
                print(state,flush=True)
                return -1, state
            if np.random.rand() <= self.deep_q.epsilon:
                move = random.randrange(self.action_size)  # Explore
            else:
                model_input = T.tensor(state, dtype=T.float32).unsqueeze(0)
                q_values = self.deep_q.model(model_input)  # Forward pass through the Q-network

                move = T.argmax(q_values).item()  # Exploit best action

            #print("Chosen move: ", move, flush=True)
            legal, newState = checkMove(state,move)
            if legal:
                #print("Acted",flush=True)
                return move, newState
            '''else:
                print(state,flush=True)'''

    def learn(self, state, action, reward, next_state, done):

        # Store the experience in replay memory
        self.deep_q.remember(state, action, reward, next_state, done)

        # Train on a batch if there are enough samples in memory
        if len(self.deep_q.memory) >= self.batch_size:
            #print("Learning", flush = True)
            self.deep_q.replay(batch_size=self.batch_size)
            #print("Learnt",flush = True)

        # Decay epsilon if the episode has ended
        if done:
            print("Decay Epsilon", flush = True)
            self.deep_q.decay_epsilon()
