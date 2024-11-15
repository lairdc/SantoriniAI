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




#SKELETON CODE
import torch as T
import random
from environment import *
from Agent import Agent
from DeepQ import DeepQ
import copy

def train_agents(num_episodes):
	# Step 1: Initialize the agents and their models
	input_dim = 5 * 5 * 2  # Update according to your board size and representation
	output_dim = 8 * 8 * 2  # Update to match the number of possible moves in your game

	
	agent1 = Agent(deep_q=DeepQ(input_dim=input_dim, output_dim=output_dim),action_size=output_dim)
	agent2 = Agent(deep_q=DeepQ(input_dim=input_dim, output_dim=output_dim),action_size=output_dim)

	print("Agents initialized", flush=True)
	
	# Step 2: Start the training loop for a given number of episodes
	for episode in range(num_episodes):
		print(f"Episode {episode + 1} / {num_episodes}", flush=True)
		
		# Reset the game (initialize the environment)
		done = False
		state = copy.deepcopy(INIT_STATE)  # Assuming this resets and returns the initial state
		
		# Initialize the rewards for the agents
		total_reward1 = 0
		total_reward2 = 0
		
		# Step 3-7: Both agents play the game, one after the other
		while not done:
			# Step 3: Agent 1 makes a move
			action1, new_state1 = agent1.act(state)
			reward1 = calculate_reward(state)
			agent1.learn(state, action1, reward1, new_state1, done)
			state = new_state1  # Update state to the new one after agent 1's move

			# Step 4: Check if the game ends after Agent 1's move
			winner = checkEndState(state)
			if winner != 0: 
				done = True
			
			total_reward1 += reward1
				
			state = flipState(state)
			# Step 5: Agent 2 makes a move
			action2, new_state2 = agent2.act(state)
			reward2 = calculate_reward(state)
			agent2.learn(state, action2, reward2, new_state2, done)
			state = new_state2  # Update state to the new one after agent 2's move

			# Step 6: Check if the game ends after Agent 2's move
			winner = checkEndState(state)
			if winner != 0: 
				done = True
			
			total_reward2 += reward2

			state = flipState(state)
		
		# After each game (episode) ends, call the models to update
		agent1.deep_q.update_target_network()
		agent2.deep_q.update_target_network()
		
		
		# Optionally: Print out rewards or game status here if desired
		print(f"Total reward for Agent 1: {total_reward1}", flush=True)
		print(f"Total reward for Agent 2: {total_reward2}", flush=True)
	
	# Save trained models
	T.save(agent1.deep_q.model.state_dict(), "agent1_model.pth")
	T.save(agent2.deep_q.model.state_dict(), "agent2_model.pth")

def calculate_reward(state):
	"""Calculate rewards based on the game state after an action."""
	reward = 0
	
	# Example: Reward function logic based on the game mechanics
	winner = checkEndState(state)
	if winner == 0:
		reward += -1  # A large positive reward if the agent wins
	elif winner == 1:
		reward += 100  # A large negative reward if the agent loses
	elif winner == -1:
		reward += -100  # Negative reward for each step to encourage quicker games
		
	# Add more rules for intermediate rewards if necessary
	return reward

if __name__ == "__main__":
	train_agents(num_episodes=1000)
