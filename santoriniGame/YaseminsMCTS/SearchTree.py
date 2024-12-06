import json
import os
import math

class SearchTree:
    def __init__(self):
        self.root = TreeNode()
        self.current = self.root

    def move_current(self, node):
        self.current = node

    def get_current(self):
        return self.current

    def reset(self):
        self.current = self.root

    def save_tree(self, filename='search_tree.json'):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, filename)
        with open(full_path, 'w') as file:
            json.dump(self.root.to_dict(), file)

    def load_tree(self, filename='search_tree.json'):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, filename)
        try:
            with open(full_path, 'r') as file:
                data = json.load(file)
                self.root = TreeNode.from_dict(data)
                self.current = self.root
        except FileNotFoundError:
            # Load an empty tree if no saved data exists
            self.root = TreeNode()
            self.current = self.root


class TreeNode:
    def __init__(self, play=None, parent=None):
        self.play = play
        self.parent = parent
        self.children = []
        self.wins = 0
        self.matches = 0

    def add_child(self, child_node):
        self.children.append(child_node)

    def get_child(self, play):
        for child in self.children:
            if child.play == play:
                return child
        return None

    def ucb1(self, exploration_param=1.41):
        if self.parent is None:
            return None
        # Calculate the Upper Confidence Bound (UCB1) score
        if self.matches == 0:
            return float('inf')  # Prefer unvisited nodes
        return (self.wins / self.matches) + exploration_param * math.sqrt(math.log(self.parent.matches) / self.matches)

    def backpropogate(self, win):
        if win:
            self.wins += 1
        self.matches += 1

        if self.parent is not None:
            self.parent.backpropogate(win)

    # Convert the TreeNode into a serializable dictionary
    def to_dict(self):
        return {
            "play": self.play,
            "wins": self.wins,
            "matches": self.matches,
            "children": [child.to_dict() for child in self.children]
        }

    # Reconstruct the TreeNode from a dictionary
    @staticmethod
    def from_dict(data, parent=None):
        node = TreeNode(play=data["play"], parent=parent)
        node.wins = data["wins"]
        node.matches = data["matches"]
        for child_data in data["children"]:
            child = TreeNode.from_dict(child_data, parent=node)
            node.children.append(child)
        return node
