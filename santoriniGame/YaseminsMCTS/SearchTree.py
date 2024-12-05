import pickle
import math
import os

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

    def save_tree(self, filename='search_tree.pkl'):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, filename)
        with open(full_path, 'wb') as file:
            pickle.dump(self.root, file)

    def load_tree(self, filename='search_tree.pkl'):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, filename)
        try:
            with open(full_path, 'rb') as file:
                self.root = pickle.load(file)
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
            #print(f"{child.play} ")
            if child.play == play:
                return child
        return None

    def ucb1(self, exploration_param=1.41):
        if self.parent == None:
            return None
        # Calculate the Upper Confidence Bound (UCB1) score
        if self.matches == 0:
            return float('inf')  # Prefer unvisited nodes
        return (self.wins / self.matches) + exploration_param * math.sqrt(math.log(self.parent.matches) / self.matches)

    def backpropogate(self, win):
        if win:
            self.wins += 1
        self.matches += 1

        if self.parent != None:
            self.parent.backpropogate(win)