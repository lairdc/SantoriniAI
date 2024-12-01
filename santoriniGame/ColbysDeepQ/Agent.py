import torch as T 
import torch.nn as nn
import torch.nn.functional as F 
import torch.optim as optim
import numpy as np 
import random
from DeepQ import DeepQ
from environment import *

class Agent:
    def __init__(self, deep_q, action_size, batch_size=64):
        self.deep_q = deep_q #deepQ class
        self.action_size = action_size  # Number of possible actions
        self.batch_size = batch_size #batch size - 

    def act(self, state):
        #IF model picks illegal move, punish it, and gointo just picking randomly
        # Epsilon-greedy policy for exploration and exploitation
        count = 0
        legal = True
        while True:
            r = np.random.rand()
            if count > 1000:
                print("houston we have a problemo", flush=True)
            if r <= self.deep_q.epsilon or not legal:
                move = random.randrange(self.action_size)  # Explore
            else:
                model_input = T.tensor(self.normalize_state(state), dtype=T.float32).unsqueeze(0)
                q_values = self.deep_q.model(model_input)  # Forward pass through the Q-network

                move = T.argmax(q_values).item()  # Exploit best action

            #print("Chosen move: ", move, flush=True)
            legal, newState = checkMove(state,move)
            if legal:
                #print("Acted",flush=True)
                return move, newState
            elif count == 0 and not r <= self.deep_q.epsilon:
                count += 1
                print("Adding illegal move")
                self.deep_q.remember(state, move, -20, state, False)

            '''else:
                print(state,flush=True)'''

    def learn(self, state, action, reward, next_state, done):
        loss = None
        # Store the experience in replay memory
        self.deep_q.remember(state, action, reward, next_state, done)

        # Train on a batch if there are enough samples in memory
        if len(self.deep_q.memory) >= self.batch_size:
            #print("Learning", flush = True)
            loss = self.deep_q.replay(batch_size=self.batch_size)
            #print("Learnt",flush = True)

        # Decay epsilon if the episode has ended
        if done:
            #print("Decay Epsilon", flush = True)
            self.deep_q.decay_epsilon()

        if loss is not None:
            return loss

    def normalize_state(self,state):
        normalized_state = []
        for row in state:
            normalized_row = [[piece, level / 4.0] for piece, level in row]
            normalized_state.append(normalized_row)
        return normalized_state
