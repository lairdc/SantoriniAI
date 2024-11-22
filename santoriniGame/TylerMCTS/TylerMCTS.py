

import random
import math
from santoriniGame.pieces import Piece
from .DictBoard import *
from collections import defaultdict

ROWS = 5
COLS = 5
RED = (255, 0, 0)
BLUE = (0, 0, 255)


# Node class used by the MCTS class. Stores a copy of the board, visits, wins, parent, move set, and children Nodes
class Node:
    def __init__(self, board):
        self.board = board.copy()
        self.children = []
        self.visits = 1
        self.wins = 0
        self.parent = None
        self.move = None

    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)


# Class in charge of simulating, expanding and backpropagated different move possibilities stored in Nodes
class TylerMCTS:
    def __init__(self, game, own_color: tuple[int, int, int], opp_color: tuple[int, int, int]):
        self.game = game
        self.own_color = own_color
        self.opp_color = opp_color
        self.root = Node(self.board_to_dict(game.board))

    def board_to_dict(self, old_board):
        dict_board = DictBoard()
        # key is coordinate tuple (0,0) or (2,3) etc
        # value is tuple of (tile level, piece) example: (1, None) or (2, "RED")
        for row in range(ROWS):
            for col in range(COLS):
                tile_level = old_board.get_tile_level(row, col)
                piece = old_board.get_piece(row, col)
                if piece:
                    if piece.color == RED:
                        piece_info = 'RED'
                        dict_board.pieces['RED'].append((row, col))
                    else:
                        piece_info = 'BLUE'
                        dict_board.pieces['BLUE'].append((row, col))
                else:
                    piece_info = None

                dict_board.tiles[(row, col)] = (tile_level, piece_info)

        return dict_board

    def str_to_color(self, str):
        if str == 'RED':
            return RED
        else:
            return BLUE

    def tuple_to_str(self, color):
        if color == (255,0,0):
            return 'RED'
        else:
            return 'BLUE'

    # Selects the best Node from the MCTS tree
    def select(self, node):
        # Select node with highest UCT value
        best_child = max(node.children, key=lambda x: (x.wins / x.visits) + 2 * (math.log(node.visits) ** 0.5 / x.visits))
        return best_child

    # Evaluates a potential move possibility & returns true/false if a winning move or not
    def simulate_move(self, board, move):
        board_copy = board.copy()

        starting_pos, move_pos, build_pos = move

        color = board.tiles[starting_pos][1]  # Second value is the color

        # Update the piece's position in the pieces dict
        board_copy.pieces[color].remove(starting_pos)
        board_copy.pieces[color].append(move_pos)

        # Update the tile states
        board_copy.tiles[starting_pos] = (board.tiles[starting_pos][0], None)  # Clear color from starting position
        board_copy.tiles[move_pos] = (board.tiles[move_pos][0], color)  # Set color to the move position

        print("\nTILE : ", board_copy.tiles[build_pos])
        board_copy.tiles[build_pos] = (board.tiles[build_pos][0] + 1, board.tiles[build_pos][1]) # Increment build level
        if board.tiles[move_pos][0] == 3:
            return board_copy, True
        return board_copy, False

    # Given a node, generates children nodes (different possibilities)
    def expand(self, node):
        # Create children for each possible move and build
        if node.children:  # Already expanded
            return
        pieces = node.board.pieces[self.tuple_to_str(self.own_color)]
        for piece in pieces:
            moves = node.board.get_all_moves(piece)
            for move in moves:
                new_board, winner = self.simulate_move(node.board, move)
                child_node = Node(new_board)
                child_node.move = move
                node.add_child(child_node)
                return  # Expand only one child

    # Given a node, updates the win score for that node.
    def simulate(self, node):
        # Simulate by playing random moves until the game ends
        board_copy = node.board.copy()
        # Set the starting player to the current player's color
        current_player = self.own_color
        while not board_copy.is_game_over():
            # Get all pieces of the current player
            pieces = board_copy.pieces[self.tuple_to_str(current_player)]
            if not pieces:
                # If the current player has no pieces, they lose
                return -1 if current_player == self.own_color else 1

            # Choose a random piece and move
            piece = random.choice(pieces)
            all_moves = board_copy.get_all_moves(piece)
            if not all_moves:
                # If no valid moves for the current player, they lose
                return -1 if current_player == self.own_color else 1

            # Randomly select a move and simulate it
            move = random.choice(all_moves)
            board_copy, winner = self.simulate_move(board_copy, move)

            # If the move results in a win, return the appropriate result
            if winner:
                return 1 if current_player == self.own_color else -1

            # Alternate turns
            current_player = self.opp_color if current_player == self.own_color else self.own_color

        # Check the result after the game ends
        result_color = self.str_to_color(board_copy.result())
        if result_color is None:
            # No winner (e.g., draw)
            return 0
        elif result_color == self.own_color:
            return 1
        else:
            return -1

    # Given a node, updates the number of visits for the node & helps update the total wins of node's children.
    def backpropagate(self, node, result):
        # Backpropagate results up the tree
        while node:
            node.visits += 1
            node.wins += result
            result = -result  # Alternate result for opponent
            node = node.parent

    # Runs all the MCTS stages
    def run_simulation(self):
        # Run one iteration of MCTS
        node = self.root

        # Selection
        while node.children:
            node = self.select(node)

        # Expansion
        if node.visits > 0 and not node.children:
            self.expand(node)

        # Simulation
        if node.children:
            node = random.choice(node.children)
        result = self.simulate(node)

        # Backpropagation
        self.backpropagate(node, result)

    # Given a node, prints the node first, and then prints only children nodes with positive wins
    def print_node(self, node, node_level):

        print("Node Level: ", node_level, "  ")
        print("RED: ", node.board.pieces['RED'], "  ","BLUE: ", node.board.pieces['BLUE'])
        print("RED Level: ", node.board.tiles[node.board.pieces['RED'][0]][0], " ", node.board.tiles[node.board.pieces['RED'][0]][0])
        print("BLUE Level: ", node.board.tiles[node.board.pieces['BLUE'][0]][0], " ", node.board.tiles[node.board.pieces['BLUE'][0]][0])
        print("Wins: ", node.wins)
        print("Visits: ", node.visits)
        print("Score: ", node.wins/node.visits)
        print("----------------------------------")
        node_level += 1
        for child in node.children:
            if child.wins > 0:
                self.print_node(child, node_level)

    # Clears the MCTS tree
    def clear_tree(self):
        self.root = Node(self.board_to_dict(self.game.board))

    # Selects the best move after completing MCTS
    def make_move(self, num_simulations=100):
        self.clear_tree()  # Clear tree

        # Run MCTS simulations
        for i in range(num_simulations):
            self.run_simulation()

        # No moves
        if not self.root.children:
            return
        # Select the child with the best win rate and highest visit count
        best_child = max(self.root.children, key=lambda child: (child.wins / child.visits, child.visits))
        print("Best Child: ")
        for child in self.root.children:
            self.print_node(child, 0)

        action = best_child.move
        if action is None:
            return

        # Unpack the move information
        move_x, move_y = action[1]
        build_x, build_y = action[2]

        # Execute the move on the game board
        piece_row, piece_col = action[0]  # Starting position of the piece
        if self.game.select(piece_row, piece_col):  # Select piece
            self.game._move(move_x, move_y)  # Move piece
            self.game._build(build_x, build_y)  # Build after move

        self.game.selected = None  # Deselect after move and build
