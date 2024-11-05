import torch as T
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque

class DeepQ(nn.Module):
    def __init__(self, model, target_model, memory_size=2000, gamma=0.95, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, learning_rate=0.001):
        super(DeepQ, self).__init__()
        self.model = model  # Neural network for the Q-function
        self.target_model = target_model  # Separate target network for stability
        self.memory = deque(maxlen=memory_size)
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)  # Optimizer for training the model
        self.loss_fn = nn.MSELoss()  # Mean squared error loss for Q-learning

    def remember(self, state, action, reward, next_state, done):
        """Store experiences in replay memory."""
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        """Select an action based on epsilon-greedy strategy."""
        if random.random() < self.epsilon:
            return random.randint(0, 63)  # Random action (assuming 8x8 flattened output space)
        state = T.tensor(state, dtype=T.float32).unsqueeze(0)
        q_values = self.model(state)  # Predict Q-values for all actions
        return T.argmax(q_values).item()  # Choose the action with the highest Q-value

    def train_on_batch(self, batch):
        """Train the model on a batch of experiences."""
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # Convert batch to tensors
        states = T.tensor(states, dtype=T.float32)
        actions = T.tensor(actions, dtype=T.int64)
        rewards = T.tensor(rewards, dtype=T.float32)
        next_states = T.tensor(next_states, dtype=T.float32)
        dones = T.tensor(dones, dtype=T.float32)

        # Compute Q-values for current states
        q_values = self.model(states)
        q_values = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)

        # Compute target Q-values for next states
        with T.no_grad():
            next_q_values = self.target_model(next_states).max(1)[0]
            targets = rewards + self.gamma * next_q_values * (1 - dones)

        # Compute loss and update model
        loss = self.loss_fn(q_values, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def replay(self, batch_size=32):
        """Sample a batch and train on it."""
        if len(self.memory) < batch_size:
            return
        batch = random.sample(self.memory, batch_size)
        self.train_on_batch(batch)

    def update_target_network(self):
        """Copy weights from the main model to the target model."""
        self.target_model.load_state_dict(self.model.state_dict())

    def decay_epsilon(self):
        """Decay epsilon after each training episode."""
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
