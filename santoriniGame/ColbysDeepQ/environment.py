import copy
import numpy


'''
This file is to determine if the game has reached an end-state 
and to check that each chosen move is a legal move in the 
current game state
'''

INIT_STATE = 	[[[0,0],[0,0],[0,0],[0,0],[0,0]],
				 [[0,0],[1,0],[0,0],[1,0],[0,0]],
				 [[0,0],[0,0],[0,0],[0,0],[0,0]],
				 [[0,0],[-1,0],[0,0],[-1,0],[0,0]],
				 [[0,0],[0,0],[0,0],[0,0],[0,0]]]

def unflattenMove(action_index):
	# Identify the piece (0 or 1)
	piece_num = action_index // (8 * 8)
	
	# Calculate the flattened index within the 8x8 matrix
	flat_8x8_index = action_index % (8 * 8)
	
	# Determine moveDir and buildDir from the flattened 8x8 index
	moveDir = flat_8x8_index // 8
	buildDir = flat_8x8_index % 8
	
	return piece_num, moveDir, buildDir


def checkMove(state,action_index):
	'''
	This should take the flatted action matrix (2x8x8) and convert it to the 
	values: piece_num, moveDir, and buildDir
	and the current state matrix (2,5,5) and return the updated if its legal
	or false if it is not

	STATE:
	[0-4][0-4][0-1]
	row  col   level or piece

	ACTION:
	[0-1][0-7][0-7]
	 p#  mDir bDir
	'''
	oldState = copy.deepcopy(state)
	#turn action matrix into piece_num, moveDir, buildDir
	piece_num, moveDir, buildDir = unflattenMove(action_index)

	#print("p#: ", piece_num, "moveDir: ",moveDir, "buildDir: ", buildDir)

	#Checking for move legality
	p = 0
	row = None
	col = None
	for r in range(5):
		for c in range(5):
			if state[r][c][0] == 1:
				if p != piece_num:
					p += 1
				else:
					row = r
					col = c
					break
		if row != None:
			break


	oldRow = row
	oldCol = col
	match moveDir:
		case 0:
			row -= 1
		case 1:
			row -= 1
			col += 1
		case 2:
			col += 1
		case 3:
			row += 1
			col += 1
		case 4:
			row += 1
		case 5:
			row += 1
			col -= 1
		case 6:
			col -= 1
		case 7:
			row -= 1
			col -= 1

	if (0 <= row <= 4 and 0 <= col <= 4 and state[row][col][0] == 0 and
		state[row][col][1] != 4 and state[row][col][1] - state[oldRow][oldCol][1] < 2):
		
		state[oldRow][oldCol][0] = 0
		state[row][col][0] = 1
	else:
		return False, oldState

	#checking for build legality
	oldRow = row
	oldCol = col
	match buildDir:
		case 0:
			row -= 1
		case 1:
			row -= 1
			col += 1
		case 2:
			col += 1
		case 3:
			row += 1
			col += 1
		case 4:
			row += 1
		case 5:
			row += 1
			col -= 1
		case 6:
			col -= 1
		case 7:
			row -= 1
			col -= 1

	if 0 <= row <= 4 and 0 <= col <= 4 and state[row][col][1] < 4 and state[row][col][0] == 0:
		state[row][col][1] += 1
	else:
		return False, oldState

	return True, state


def checkEndState(state):
	piece1 = None
	piece2 = None
	piece3 = None
	piece4 = None
	for r in range(5):
		for c in range(5):
			if state[r][c][0] == 1:
				if state[r][c][1] == 3:
					return state[r][c][0]
				if piece1 == None:
					piece1 = (r,c)
				else:
					piece2 = (r,c)
			elif state[r][c][0] == -1:
				if state[r][c][1] == 3:
					return state[r][c][0]
				if piece3 == None:
					piece3 = (r,c)
				else:
					piece4 = (r,c)

	p1move = canMove(state,piece1)
	if not p1move:
		p2move = canMove(state,piece2)
		if not p2move:
			return -1

	p3move = canMove(state,piece3)
	if not p3move:
		p4move = canMove(state,piece4)
		if not p4move:
			return 1




	return 0

def canMove(state, piece):
	#print(state,flush=True)
	# Get the current row and column of the piece
	row, col = piece
	
	# Define all possible move directions (N, NE, E, SE, S, SW, W, NW)
	directions = [
		(-1, 0),  # North
		(-1, 1),  # Northeast
		(0, 1),   # East
		(1, 1),   # Southeast
		(1, 0),   # South
		(1, -1),  # Southwest
		(0, -1),  # West
		(-1, -1)  # Northwest
	]
	
	# Check each direction to see if there's a valid move
	for dr, dc in directions:
		new_row, new_col = row + dr, col + dc
		
		# Check that the new position is within bounds (5x5 grid)
		if 0 <= new_row < 5 and 0 <= new_col < 5:
			# Check if the square is unoccupied and the height difference is valid
			if (state[new_row][new_col][0] == 0 and  # No piece on the square
				state[new_row][new_col][1] - state[row][col][1] <= 1 and  # Height difference ≤ 1
				state[new_row][new_col][1] != 4):  # Not on a dome level
				return True  # Found a valid move
	
	# If no valid moves are found, return False
	return False

def flipState(state):
	for r in range(5):
		for c in range(5):
			if state[r][c][0] == 1:
				state[r][c][0] = -1
			elif state[r][c][0] == -1:
				state[r][c][0] = 1
	return state




