# information set MCTS
# 01.15.2018 by Symbol 


from math import *
import random, sys
from copy import deepcopy
from games.game import GameState


class Node:
	""" A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
	"""
	def __init__(self, move = None, parent = None, playerJustMoved = None, playerType = 'tricks'):
		self.move = move # the move that got us to this node - "None" for the root node
		self.parentNode = parent # "None" for the root node
		self.childNodes = []
		self.wins = 0
		self.tricks = 0
		self.trickValue = 0
		self.visits = 0
		self.avails = 1
		self.playerJustMoved = playerJustMoved # the only part of the state that the Node needs later
		self.playerType = playerType
	
	def GetUntriedMoves(self, legalMoves):
		""" Return the elements of legalMoves for which this node does not have children.
		"""
		
		# Find all moves for which this node *does* have children
		triedMoves = [child.move for child in self.childNodes]
		
		# Return all moves that are legal but have not been tried yet
		return [move for move in legalMoves if move not in triedMoves]
		
	def UCBSelectChild(self, legalMoves, exploration = 0.7):
		""" Use the UCB1 formula to select a child node, filtered by the given list of legal moves.
			exploration is a constant balancing between exploitation and exploration, with default value 0.7 (approximately sqrt(2) / 2)
		"""
		
		# Filter the list of children by the list of legal moves
		legalChildren = [child for child in self.childNodes if child.move in legalMoves]
		
		# Get the child with the highest UCB score
		if self.playerType == 'tricks':
			s = max(legalChildren, key = lambda c: float(c.trickValue)/float(c.visits) +  0.5 * sqrt(log(c.avails)/float(c.visits)))
		elif self.playerType == 'wins':
			s = max(legalChildren, key = lambda c: float(c.wins)/float(c.visits) + exploration * sqrt(log(c.avails)/float(c.visits)))
		else: 
			raise Exception("Invalid player type!")

		# Update availability counts -- it is easier to do this now than during backpropagation
		for child in legalChildren:
			child.avails += 1
		
		# Return the child selected above
		return s
	
	def AddChild(self, m, p):
		""" Add a new child node for the move m.
			Return the added child node
		"""
		n = Node(move = m, parent = self, playerJustMoved = p)
		self.childNodes.append(n)
		return n
	
	def Update(self, terminalState):
		""" Update this node - increment the visit count by one, and increase the win count by the result of terminalState for self.playerJustMoved.
		"""
		self.visits += 1
		if self.playerJustMoved is not None:
			self.wins += terminalState.GetResult(self.playerJustMoved)
			tricks = terminalState.GetTricks(self.playerJustMoved)
			self.tricks += tricks
			self.trickValue += float(tricks)/float(terminalState.tricksInRound + 1)

	def __repr__(self):
		return "[M:%s W/S/V/A: %.3f/%.1f/%4i/%4i]" % (self.move, float(self.wins)/float(self.visits), float(self.tricks)/float(self.visits), self.visits, self.avails)

	def TreeToString(self, indent):
		""" Represent the tree as a string, for debugging purposes.
		"""
		s = self.IndentString(indent) + str(self)
		for c in self.childNodes:
			s += c.TreeToString(indent+1)
		return s

	def IndentString(self,indent):
		s = "\n"
		for i in range (1,indent+1):
			s += "| "
		return s

	def ChildrenToString(self):
		s = ""
		for c in self.childNodes:
			s += str(c) + "\n"
		return s


def ISMCTS(rootstate, numDeterm, numPredeterm, playerType, verbose = False):
	""" Conduct an ISMCTS search for itermax iterations starting from rootstate.
		Return the best move from the rootstate.
	"""

	rootnode = Node(playerType = playerType)
	
	for i in range(numDeterm):
		
		
		# Determinize
		rootstate = rootstate.CloneAndRandomize(rootstate.playerToMove)
		

		for j in range(numPredeterm):
			node = rootnode
			state = rootstate.Clone()
			# Select
			while state.GetMoves() != [] and node.GetUntriedMoves(state.GetMoves()) == []: # node is fully expanded and non-terminal
				node = node.UCBSelectChild(state.GetMoves())
				state.DoMove(node.move)

			# Expand
			untriedMoves = node.GetUntriedMoves(state.GetMoves())
			if untriedMoves != []: # if we can expand (i.e. state/node is non-terminal)
				m = random.choice(untriedMoves) 
				player = state.playerToMove
				state.DoMove(m)
				node = node.AddChild(m, player) # add child and descend tree

			# Simulate
			if  playerType == 'tricks':
				while state.GetMoves() != []: # while state is non-terminal in a round
					state.DoMove(random.choice(state.GetMoves()))
			elif playerType == 'wins':
				while state.gameOver is False:
					#if state.playerHands[state.playerToMove] == []:
						#state.Deal()
					state.DoMove(random.choice(state.GetMoves()))

			# Backpropagate
			while node != None: # backpropagate from the expanded node and work back to the root node
				node.Update(state)
				node = node.parentNode

	# Output some information about the tree - can be omitted
	if rootstate.playerToMove == 1:
		if (verbose): print(rootnode.TreeToString(0))
		else: print(rootnode.ChildrenToString())

	return max(rootnode.childNodes, key = lambda c: c.visits).move # return the move that was most visited