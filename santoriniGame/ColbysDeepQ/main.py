'''
GOALS:
Create two agents:
	-Each agent should have a slightly different batch size, so their Networks are updated at staggered times and dont get stuck in a loop or learn the same strategies

Have the two agents train on each other:
	-Needs to have some sort of environment to check that the agents chosen move is valid (not moving off the board or building where it cant, etc)
		-What should happen when it picks an invalid move, pick its next choice? move randomly? 
	-Have the agents play games over and over.
	-Ability to extract the final parameters of the two agents
	-Ability to take a 'good' agent and have it play on the actual board

'''