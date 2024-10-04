# agent.py
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from model import DQN


class DQNAgent:
    def __init__(self, state_size, action_size, hidden_size=64, gamma=0.99, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, learning_rate=0.001, memory_size=2000, batch_size=64):
        self.state_size = state_size
        self.action_size = action_size
        self.hidden_size = hidden_size
        self.gamma = gamma  # Discount rate
        self.epsilon = epsilon  # Exploration rate
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.memory = deque(maxlen=memory_size)

        # Initialize the policy network and target network
        self.model = DQN(state_size, hidden_size, action_size)
        self.target_model = DQN(state_size, hidden_size, action_size)
        self.update_target_model()

        # Optimizer
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.loss_fn = nn.MSELoss()

    def update_target_model(self):
        """Update the target network with the current policy network weights."""
        self.target_model.load_state_dict(self.model.state_dict())

    def remember(self, state, action, reward, next_state, done):
        """Store a transition in memory."""
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        """Choose an action based on the epsilon-greedy strategy."""
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)  # Explore
        state = torch.FloatTensor(state).unsqueeze(0)
        q_values = self.model(state).detach().numpy()
        return np.argmax(q_values[0])  # Exploit

    def replay(self):
        """Train the agent using the replay buffer."""
        if len(self.memory) < self.batch_size:
            return  # Not enough samples to train

        # Sample a batch from memory
        minibatch = random.sample(self.memory, self.batch_size)

        for state, action, reward, next_state, done in minibatch:
            state = torch.FloatTensor(state).unsqueeze(0)
            next_state = torch.FloatTensor(next_state).unsqueeze(0)

            # Calculate Q values
            target = self.model(state).detach().clone()
            if done:
                target[0][action] = reward
            else:
                # Predict the future reward using the target model
                next_q_values = self.target_model(next_state).detach().max(1)[0]
                target[0][action] = reward + self.gamma * next_q_values

            # Update the model
            output = self.model(state)
            loss = self.loss_fn(output, target)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        # Decay epsilon for less exploration over time
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_checkpoint(self, filepath):
        """Save the entire training state to a checkpoint file."""
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'memory': list(self.memory),  # Convert deque to list for serialization
        }
        torch.save(checkpoint, filepath)
        print(f"Checkpoint saved to {filepath}")

    def load_checkpoint(self, filepath):
        """Load the training state from a checkpoint file."""
        checkpoint = torch.load(filepath)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.memory = deque(checkpoint['memory'], maxlen=self.memory.maxlen)  # Restore memory
        self.update_target_model()  # Make sure target model is updated
        print(f"Checkpoint loaded from {filepath}")
