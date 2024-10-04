# model.py
import torch
import torch.nn as nn
import torch.nn.functional as F


class DQN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

    def save_model(self, filepath):
        """Save the model weights to a file."""
        torch.save(self.state_dict(), filepath)
        print(f"Model weights saved to {filepath}")

    def load_model(self, filepath):
        """Load the model weights from a file."""
        self.load_state_dict(torch.load(filepath))
        print(f"Model weights loaded from {filepath}")
