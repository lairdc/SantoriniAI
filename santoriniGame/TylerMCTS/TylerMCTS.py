import random
import math
from santoriniGame.pieces import Piece
from .DictBoard import *
from collections import defaultdict

ROWS = 5
COLS = 5
RED = (255, 0, 0)
BLUE = (0, 0, 255)


class Node:
    def __init__(self, board):
        self.board = board.copy()  # DictBoard
        self.children = []
        self.visits = 1
        self.wins = 0
        self.parent = None
        self.move = None

    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)

class TylerMCTS:
    def __init__(self, game, own_color: tuple[int, int, int], opp_color: tuple[int, int, int]):
        self.game = game
        self.own_color = own_color
        self.opp_color = opp_color
        self.root = Node(self.board_to_dict(game.board))


    def board_to_dict(self, old_board):
        # Converts current state of the board to DictBoard
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
        # Converts the string of color to tuple of color
        if str == 'RED':
            return RED
        else:
            return BLUE

    def tuple_to_str(self, color):
        # Converts the tuple of color to the string of the color
        if color == (255,0,0):
            return 'RED'
        else:
            return 'BLUE'

    def select(self, node):
        # Select node with highest UCT value
        best_child = max(node.children, key=lambda x: (x.wins / x.visits) + 2 * (math.log(node.visits) ** 0.5 / x.visits))
        return best_child

    def simulate_move(self, board, move):
        # Simulates moves on the DictBoard
        board_copy = board.copy()

        starting_pos, move_pos, build_pos = move

        color = board.tiles[starting_pos][1]  # Second value is the color

        # Update the piece's position in the pieces dict
        board_copy.pieces[color].remove(starting_pos)
        board_copy.pieces[color].append(move_pos)

        # Update the tile states
        board_copy.tiles[starting_pos] = (board.tiles[starting_pos][0], None)  # Clear color from starting position
        board_copy.tiles[move_pos] = (board.tiles[move_pos][0], color)  # Set color to the move position
        board_copy.tiles[build_pos] = (
        board.tiles[build_pos][0] + 1, board.tiles[build_pos][1])  # Increment build level
        if board.tiles[move_pos][0] == 3:
            return board_copy, True
        return board_copy, False

    def expand(self, node):
        # Create children for each possible move and build
        pieces = node.board.pieces[self.tuple_to_str(self.own_color)]
        for piece in pieces:
            moves = node.board.get_all_moves(piece)
            for move in moves:
                new_board, winner = self.simulate_move(node.board, move)
                child_node = Node(new_board)
                child_node.move = move
                node.add_child(child_node)

    def score_move(self, board, cur_x, cur_y, move_x, move_y):
        cur_level = board.get_tile_level(cur_x, cur_y)
        move_level = board.get_tile_level(move_x, move_y)
        diff = move_level - cur_level

        # Calculate score based on level difference
        score = 500 * diff if diff != 0 else 0

        return score

    def score_build(self, board, build_x, build_y):
        tile_level = board.get_tile_level(build_x, build_y)

        if board.opp_move(build_x, build_y, self.tuple_to_str(self.opp_color)) and tile_level == 2:
            # Prevent building to give opponent win
            return -50000
        else:
            # Build up
            if tile_level < 4:
                return 100 * tile_level


    def simulate(self, node):
        board_copy = node.board.copy()
        current_player = self.own_color
        while not board_copy.is_game_over():
            pieces = board_copy.pieces[self.tuple_to_str(current_player)]
            best_move = None
            best_score = float('-inf')
            for piece in pieces:
                all_moves = board_copy.get_all_moves(piece)
                for move in all_moves:
                    move_score = (self.score_move(board_copy, move[0][0], move[0][1], move[1][0], move[1][1])
                                  + self.score_build(board_copy, move[2][0], move[2][1]))
                    if move_score > best_score:
                        best_score = move_score
                        best_move = move
            if best_move:
                board_copy, winner = self.simulate_move(board_copy, best_move)
                if winner:
                    return 1 if current_player == self.own_color else -1
            current_player = self.opp_color if current_player == self.own_color else self.own_color
        return 0  # No winner

    '''
    Random Simulation
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
    '''

    def backpropagate(self, node, result):
        # Backpropagate results up the tree
        while node:
            node.visits += 1
            node.wins += result
            result = -result  # Alternate result for opponent
            node = node.parent

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

    def print_node(self, node, node_level):
        # Prints node information for debugging
        # print("Node Level: ", node_level, "  ")
        # print("RED: ", node.board.pieces['RED'], "  ","BLUE: ", node.board.pieces['BLUE'])
        # print("Wins: ", node.wins)
        # print("----------------------------------")
        node_level += 1
        for child in node.children:
            if child.wins > 0:
                self.print_node(child, node_level)

    def clear_tree(self):
        # Clears the children of the tree and sets the root node to the current state of the board
        self.root = Node(self.board_to_dict(self.game.board))


    def opp_can_move(self, board, opp_pieces, action_x, action_y):
        # Checks if the opponent can move to a given coordinate
        for piece in opp_pieces:
            valid_moves = self.game.board.get_valid_moves(piece)
            for move in valid_moves.keys():
                if move[0] == action_x and move[1] == action_y:
                    return True
        return False

    def get_priority_action(self, board):
        # Check if there is a winning move or can dome the opponents winning move
        action = None

        own_pieces = self.game.board.get_all_pieces(self.own_color)
        opp_pieces = self.game.board.get_all_pieces(self.opp_color)

        for i, piece in enumerate(own_pieces):
            cur_x, cur_y = piece.get_x(), piece.get_y()
            valid_moves = self.game.board.get_valid_moves(piece)

            for move in valid_moves:
                move_x, move_y = move
                can_win = False
                if board.get_tile_level(move_x, move_y) == 3:
                    can_win = True

                # Simulate the piece moving to the new location
                fake_piece = Piece(move_x, move_y, self.own_color)
                valid_builds = self.game.board.get_valid_builds(fake_piece)

                # Also consider building on the current position before moving
                valid_builds[(cur_x, cur_y)] = board.get_tile_level(cur_x, cur_y)

                for build in valid_builds:
                    build_x, build_y = build
                    if can_win:  # Winning move, build doesn't matter
                        action = [cur_x, cur_y, move_x, move_y, build_x, build_y]
                        break
                    elif self.opp_can_move(board, opp_pieces, build_x, build_y) and board.get_tile_level(build_x, build_y) == 3: # Dome opponent winning move
                        action = [cur_x, cur_y, move_x, move_y, build_x, build_y]
        return action

    def make_move(self, num_simulations=100):
        self.clear_tree()  # Clear tree
        action = self.get_priority_action(self.game.board)
        if action is None:  # Run MCTS
            # Run MCTS simulations
            for i in range(num_simulations):
                self.run_simulation()

            # No moves
            if not self.root.children:
                return
            # Select the child with the best win rate and highest visit count
            best_child = max(self.root.children, key=lambda child: (child.wins / child.visits, child.visits))
            # print("Best Child Wins: ", best_child.wins)
            self.print_node(self.root, 0)

            # action = [(piece_row,piece_col),(move_x,move_y),(build_x,build_y)]
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

        else:  # Do priority action
            piece_row, piece_col = action[0], action[1]
            move_x, move_y = action[2], action[3]
            build_x, build_y = action[4], action[5]

            if self.game.select(piece_row, piece_col):  # Select piece
                self.game._move(move_x, move_y)  # Move piece
                self.game._build(build_x, build_y)  # Build after move

        self.game.selected = None  # Deselect after move and build