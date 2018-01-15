from games.simpleBridge import SimpleBridgeState
from MCTS.ISMCTS import ISMCTS


def getPlayerMove(state):
	while True:
		inp = input('Input your move: ')
		if len(inp) != 2:
			print("Wrong length!")
			continue
		rank = "??23456789TJQKA".index(inp[0])
		suit = inp[1]
		if rank in range(2, 14+1) and suit in ['C', 'D', 'H', 'S']:
			move = Card(rank, suit)
			if move in state.GetMoves():
				return move	
			else:
				print("The move is not valid!")
		else:
			print("No such card!")

def playGame(Round = 10):
	""" Play a sample game between two ISMCTS players.
	"""
	numofPlayers = 3
	numofCards = 10
	wins = [0 for p in range(1, numofPlayers+1)]
	for i in range(Round):
		state = SimpleBridgeState(numofPlayers, numofCards)
		while (state.GetMoves() != []):
			print(str(state))
			# Use different numbers of iterations (simulations, tree nodes) for different players
			if state.playerToMove == 1:
				m = getPlayerMove(state)
				ISMCTS(rootstate = state, numDeterm = 1000, numPredeterm = 1, playerType = 'tricks', verbose = False)
			else:
				m = ISMCTS(rootstate = state, numDeterm = 1000, numPredeterm = 1, playerType = 'tricks', verbose = False)
				print("[R" + str(i+1) + "] Player " + str(state.playerToMove)  + " move: " + str(m) + "\n")

			state.DoMove(m)
			#if state.playerHands[state.playerToMove] == []:
			#	state.Deal()

		
		someoneWon = False
		for p in range(1, state.numberOfPlayers + 1):
			if state.GetResult(p) > 0:
				wins[p-1] += 1
				print("Player " + str(p) + " wins with scores " + str(state.tricksTaken[p]) + "!")

		print("--------------------------------------------")
		print("[R" + str(i+1) + "] Winning counts: " + str(wins))
		print("--------------------------------------------\n") 



if __name__ == "__main__":
	playGame()