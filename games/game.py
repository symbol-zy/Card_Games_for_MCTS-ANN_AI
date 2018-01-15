# Abstact GameState class
# 01.15.2018 by Symbol 


from math import *
import random, sys
from copy import deepcopy

class GameState:
	""" A state of the game, i.e. the game board. These are the only functions which are
		absolutely necessary to implement ISMCTS in any imperfect information game,
		although they could be enhanced and made quicker, for example by using a 
		GetRandomMove() function to generate a random move during rollout.
		By convention the players are numbered 1, 2, ..., self.numberOfPlayers.
	"""
	def __init__(self):
		self.numberOfPlayers = 2
		self.playerToMove = 1
	
	def GetNextPlayer(self, p):
		""" Return the player to the left of the specified player
		"""
		return (p % self.numberOfPlayers) + 1
	
	def Clone(self):
		""" Create a deep clone of this game state.
		"""
		st = GameState()
		st.playerToMove = self.playerToMove
		return st
	
	def CloneAndRandomize(self, observer):
		""" Create a deep clone of this game state, randomizing any information not visible to the specified observer player.
		"""
		return self.Clone()
	
	def DoMove(self, move):
		""" Update a state by carrying out the given move.
			Must update playerToMove.
		"""
		self.playerToMove = self.GetNextPlayer(self.playerToMove)
		
	def GetMoves(self):
		""" Get all possible moves from this state.
		"""
		raise NotImplementedException()
	
	def GetResult(self, player):
		""" Get the game result from the viewpoint of player. 
		"""
		raise NotImplementedException()

	def __repr__(self):
		""" Don't need this - but good style.
		"""
		pass