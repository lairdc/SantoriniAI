'''This file needs to facilitate the following:
-Create two new, untrained Agents and their respective models
-Have them play santorini over and over for a certain number of episodes (games)
	-Ensure after each game the environment (board) is reset
	-call Agent's learn() after each episode (when a game ends)
	-After each move calculate a reward
		-Check after each move if the game has reached an endstate and provide a large pos or neg reward
ORDER OF EVENTS:
1. Create agent one and two
2. Start a new game of santorini
3. Agent one makes a move (act())
4. Calculate Agent ones reward
5. Call Agents learn() to train
6. Repeat 3-5 for Agent two
7. Repeat 3-6 until reaching an endstate
8.train models
9.Start over at step 2 and repeat over and over.

'''

'''
KNOWN BUGS:
-Coesnt properly recognize a win (only when it cause no valid moves left)
	-Temp fix with Agent's act() return -1 if it can find a move
	-Actual issue probably lays in main
-Sometimes an agent moves twice and doesnt build
	-Probably lies in environment.py
	-Make sure environemnt properly handles all actions
		-Maybe simulate & manually check them?? ugh


-When Deep-Q picks worng move, always have it pick randomly
'''


#SKELETON CODE
import torch as T
import random
from environment import *
from Agent import Agent
from DeepQ import DeepQ
import copy

def train_agents(num_episodes):
	loss_hist = []
	gameNum = 0
	# Step 1: Initialize the agents and their models
	input_dim = 5 * 5 * 2  # Update according to your board size and representation
	output_dim = 8 * 8 * 2  # Update to match the number of possible moves in your game
	wins1 = 0
	wins2 = 0
	
	agent1 = Agent(deep_q=DeepQ(input_dim=input_dim, output_dim=output_dim),action_size=output_dim)
	agent2 = Agent(deep_q=DeepQ(input_dim=input_dim, output_dim=output_dim),action_size=output_dim)

	print("Agents initialized", flush=True)

	with open("training_stats.txt", "w") as stats_file:
		stats_file.write("GameNum,TurnNum,Reward1,Reward2\n") 
	
		# Step 2: Start the training loop for a given number of episodes
		for episode in range(num_episodes):
			print(f"Episode {episode + 1} / {num_episodes}", flush=True)
			print("Epsilon1: ", agent1.deep_q.epsilon, "Epsilon2: ", agent2.deep_q.epsilon, flush=True)
			
			# Reset the game (initialize the environment)
			gameNum += 1
			turnNum = 0
			done = False
			state = copy.deepcopy(INIT_STATE)  # Assuming this resets and returns the initial state
			oldState = copy.deepcopy(INIT_STATE)
			# Initialize the rewards for the agents
			total_reward1 = 0
			total_reward2 = 0
			
			# Step 3-7: Both agents play the game, one after the other
			#print("Pre episode state: \n", state, flush=True)
			while not done:
				turnNum += 1
				# Step 3: Agent 1 makes a move
				#print("Passing this state to agent1: ",state,flush=True)
				action1, new_state1 = agent1.act(state)
				reward1 = calculate_reward(new_state1,state)
				winner = checkEndState(new_state1)
				#print(new_state1,flush=True)
				#print(winner, reward1,flush=True)

				#print("Agent 1 reward: ",reward1,flush=True)

				if gameNum % 1000 == 0:
					stats_file.write(f"{gameNum},{turnNum},{reward1},0\n")
					stats_file.flush()


				if winner != 0: 
					w = 1
					done = True
					reward2 -= reward1
					if action1 != -1:
						loss = agent1.learn(state, action1, reward1, new_state1, done)
						loss_hist.append(loss)
						loss = agent2.learn(state, action2, reward2, new_state2, done)
						loss_hist.append(loss)

					total_reward1 += reward1
					break



				loss = agent1.learn(state, action1, reward1, new_state1, done)
				loss_hist.append(loss)

				state = new_state1  # Update state to the new one after agent 1's move
				total_reward1 += reward1
					
				state = flipState(state)
				#print(state,flush=True)
				#print("Passing this state to agent2: ",state,flush=True)
				action2, new_state2 = agent2.act(state)
				reward2 = calculate_reward(new_state2,state)
				winner = checkEndState(new_state2)
				#print(new_state2,flush=True)
				#print(action2,flush=True)

				#print("Agent 2 reward: ",reward2,flush=True)

				if gameNum % 1000 == 0:
					stats_file.write(f"{gameNum},{turnNum},{reward2},0\n")
					stats_file.flush()


				if winner != 0: 
					w = 2
					done = True
					reward2 -= reward1
					if action2 != -1:
						loss = agent1.learn(state, action1, reward1, new_state1, done)
						loss_hist.append(loss)

						loss = agent2.learn(state, action2, reward2, new_state2, done)
						loss_hist.append(loss)

					total_reward2 += reward2
					break

				loss = agent2.learn(state, action2, reward2, new_state2, done)
				loss_hist.append(loss)

				state = new_state2  # Update state to the new one after agent 2's move
				total_reward2 += reward2

				state = flipState(state)

			
			if w == 1:
				wins1 += 1
			else:
				wins2 += 1

			avg_reward1 = total_reward1 / turnNum
			avg_reward2 = total_reward2 / turnNum
			if gameNum % 50 == 0:
				stats_file.write(f"Game {gameNum}: AvgReward1={avg_reward1:.2f}, AvgReward2={avg_reward2:.2f}, Turns={turnNum}\n")
				stats_file.flush()
				# After each game (episode) ends, call the models to update
				#print("Post episode state: \n", state, flush=True)
				#print("Epsiode over, updating agent1",flush=True)
				agent1.deep_q.update_target_network()
				#print("Epsiode over, updating agent1",flush=True)
				agent2.deep_q.update_target_network()

			
			# Optionally: Print out rewards or game status here if desired
			print(f"Total reward for Agent 1: {total_reward1}", flush=True)
			print(f"Total reward for Agent 2: {total_reward2}", flush=True)
	
	# Save trained models
	print("Agent 1 Wins: ", wins1, flush = True)
	print("Agent 2 Wins: ", wins2, flush = True)
	T.save(agent1.deep_q.model.state_dict(), "agent1_model.pth")
	T.save(agent2.deep_q.model.state_dict(), "agent2_model.pth")


	# Create the plot
	plt.figure(figsize=(10, 6))
	plt.plot(loss_history, label='Loss')

	# Add labels, title, and legend
	plt.xlabel('Training Step')
	plt.ylabel('Loss')
	plt.title('Loss Over Time')
	plt.legend()
	plt.grid()

	# Show the plot
	plt.show()

def calculate_reward(state,oldState):
	"""Calculate rewards based on the game state after an action."""
	reward = 0
	
	# Example: Reward function logic based on the game mechanics
	winner = checkEndState(state)
	if winner == 0:
		reward += calc_height_diff(state,oldState)
	elif winner == 1:
		reward += 100  # A large negative reward if the agent loses
		return reward
	elif winner == -1:
		reward += -100  # Negative reward for each step to encourage quicker games
		return reward

	if canWin(state,-1):
		reward -= 100
	if canWin(state,1):
		reward += 50
		
	# Add more rules for intermediate rewards if necessary
	return reward

def calc_height_diff(newState,oldState):
	oldHeight = 0
	newHeight = 0
	for r in range(5):
		for c in range(5):
			if oldState[r][c][0] == 1:
				oldHeight += oldState[r][c][1]
			if newState[r][c][0] == 1:
				newHeight += newState[r][c][1]


	return (newHeight - oldHeight) * 20 + (newHeight) * 2

def canWin(state,player):
	for r in range(5):
		for c in range(5):
			if state[r][c][0] == player and state[r][c][1] == 2:
				for i in range(8):
					row = r
					col = c
					match i:
						case 0:
							row -= 1
							if 0 <= row <= 4 and 0 <= col <= 4 and state[row][col][1] == 3:
								return True
						case 1:
							row -= 1
							col += 1
							if 0 <= row <= 4 and 0 <= col <= 4 and state[row][col][1] == 3:
								return True
						case 2:
							col += 1
							if 0 <= row <= 4 and 0 <= col <= 4 and state[row][col][1] == 3:
								return True
						case 3:
							row += 1
							col += 1
							if 0 <= row <= 4 and 0 <= col <= 4 and state[row][col][1] == 3:
								return True
						case 4:
							row += 1
							if 0 <= row <= 4 and 0 <= col <= 4 and state[row][col][1] == 3:
								return True
						case 5:
							row += 1
							col -= 1
							if 0 <= row <= 4 and 0 <= col <= 4 and state[row][col][1] == 3:
								return True
						case 6:
							col -= 1
							if 0 <= row <= 4 and 0 <= col <= 4 and state[row][col][1] == 3:
								return True
						case 7:
							row -= 1
							col -= 1
							if 0 <= row <= 4 and 0 <= col <= 4 and state[row][col][1] == 3:
								return True
	return False


if __name__ == "__main__":
	train_agents(num_episodes=1000)
