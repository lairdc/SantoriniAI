import pickle
import math

class SearchTree:
    def __init__(self):
        self.root = TreeNode()
        self.current = self.root

    def move_current(self, node):
        self.current = self.node

    def get_current(self):
        return self.current

    def save_tree(self, filename='search_tree.pkl'):
        with open(filename, 'wb') as file:
            pickle.dump(self.root, file)

    def load_tree(self, filename='search_tree.pkl'):
        try:
            with open(filename, 'rb') as file:
                self.root = pickle.load(file)
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

    def ucb1(self, exploration_param=1.41):
        if parent == None:
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