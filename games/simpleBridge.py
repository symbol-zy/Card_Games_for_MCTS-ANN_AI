# A simplied version of the card game bridge, in which trumps are assigned randomly.

from math import *
import random, sys
from copy import deepcopy
from games.game import GameState

STARTCARD = 8

class Card:
	""" A playing card, with rank and suit.
		rank must be an integer between 2 and 14 inclusive (Jack=11, Queen=12, King=13, Ace=14)
		suit must be a string of length 1, one of 'C' (Clubs), 'D' (Diamonds), 'H' (Hearts) or 'S' (Spades)
	"""
	def __init__(self, rank, suit):
		if rank not in range(STARTCARD, 14+1):
			raise Exception("Invalid rank")
		if suit not in ['C', 'D', 'H', 'S']:
			raise Exception("Invalid suit")
		self.rank = rank
		self.suit = suit
	
	def __repr__(self):
		return "??23456789TJQKA"[self.rank] + self.suit
	
	def __eq__(self, other):
		return self.rank == other.rank and self.suit == other.suit

	def __ne__(self, other):
		return self.rank != other.rank or self.suit != other.suit

class SimpleBridgeState(GameState):
	""" A state of the game Knockout Whist.
		See http://www.pagat.com/whist/kowhist.html for a full description of the rules.
		For simplicity of implementation, this version of the game does not include the "dog's life" rule
		and the trump suit for each round is picked randomly rather than being chosen by one of the players. 
		Furthermove, at each round the player taking the least tricks is knocked out, instead of knocking out
		the player taking no tricks. At each new round, the player who won the last trick at the last round 
		takes the lead.
	"""
	def __init__(self, n = 4, m = 5):
		""" Initialise the game state. n is the number of players (from 2 to 4).
		"""
		self.numberOfPlayers = n
		self.playerToMove   = random.randint(1, n)
		self.tricksInRound  = m
		self.gameOver = False
		self.playerHands    = {p:[] for p in range(1, self.numberOfPlayers+1)}
		self.discards       = [] # Stores the cards that have been played already in this round
		self.currentTrick   = []
		self.trumpSuit      = None
		self.tricksTaken    = {} # Number of tricks taken by each player this round
		self.knockedOut     = {p:False for p in range(1, self.numberOfPlayers+1)}
		self.Deal()
	
	def Clone(self):
		""" Create a deep clone of this game state.
		"""
		st = SimpleBridgeState(self.numberOfPlayers)
		st.playerToMove = self.playerToMove
		st.tricksInRound = self.tricksInRound
		st.gameOver = self.gameOver
		st.playerHands  = deepcopy(self.playerHands)
		st.discards     = deepcopy(self.discards)
		st.currentTrick = deepcopy(self.currentTrick)
		st.trumpSuit    = self.trumpSuit
		st.tricksTaken  = deepcopy(self.tricksTaken)
		st.knockedOut   = deepcopy(self.knockedOut)
		return st
	
	def CloneAndRandomize(self, observer):
		""" Create a deep clone of this game state, randomizing any information not visible to the specified observer player.
		"""
		st = self.Clone()
		
		# The observer can see his own hand and the cards in the current trick, and can remember the cards played in previous tricks
		seenCards = st.playerHands[observer] + st.discards + [card for (player,card) in st.currentTrick]
		# The observer can't see the rest of the deck
		unseenCards = [card for card in st.GetCardDeck() if card not in seenCards]
		
		# Deal the unseen cards to the other players
		random.shuffle(unseenCards)
		for p in range(1, st.numberOfPlayers+1):
			if p != observer:
				# Deal cards to player p
				# Store the size of player p's hand
				numCards = len(self.playerHands[p])
				# Give player p the first numCards unseen cards
				st.playerHands[p] = unseenCards[ : numCards]
				# Remove those cards from unseenCards
				unseenCards = unseenCards[numCards : ]
		
		return st
	
	def GetCardDeck(self):
		""" Construct a standard deck of 52 cards.
		"""
		return [Card(rank, suit) for rank in range(STARTCARD, 14+1) for suit in ['C', 'D', 'H', 'S']]
	
	def Deal(self):
		""" Reset the game state for the beginning of a new round, and deal the cards.
		"""
		if self.gameOver:
			return

		self.discards = []
		self.currentTrick = []
		self.tricksTaken = {p:0 for p in range(1, self.numberOfPlayers+1)}
		
		# Construct a deck, shuffle it, and deal it to the players
		deck = self.GetCardDeck()
		random.shuffle(deck)
		for p in range(1, self.numberOfPlayers+1):
			self.playerHands[p] = deck[ : self.tricksInRound]
			deck = deck[self.tricksInRound : ]
		
		# Choose the trump suit for this round
		self.trumpSuit = random.choice(['C', 'D', 'H', 'S'])
	
	def GetNextPlayer(self, p):
		""" Return the player to the left of the specified player, skipping players who have been knocked out
		"""
		next = (p % self.numberOfPlayers) + 1
		# Skip any knocked-out players
		while next != p and self.knockedOut[next]:
			next = (next % self.numberOfPlayers) + 1
		return next
	
	def DoMove(self, move):
		""" Update a state by carrying out the given move.
			Must update playerToMove.
		"""
		# Store the played card in the current trick
		self.currentTrick.append((self.playerToMove, move))
		
		# Remove the card from the player's hand
		self.playerHands[self.playerToMove].remove(move)
		
		# Find the next player
		self.playerToMove = self.GetNextPlayer(self.playerToMove)
		
		# If the next player has already played in this trick, then the trick is over
		if any(True for (player, card) in self.currentTrick if player == self.playerToMove):
			# Sort the plays in the trick: those that followed suit (in ascending rank order), then any trump plays (in ascending rank order)
			(leader, leadCard) = self.currentTrick[0]
			suitedPlays = [(player, card.rank) for (player, card) in self.currentTrick if card.suit == leadCard.suit]
			trumpPlays  = [(player, card.rank) for (player, card) in self.currentTrick if card.suit == self.trumpSuit]
			sortedPlays = sorted(suitedPlays, key = lambda play : play[1]) + sorted(trumpPlays, key = lambda play : play[1])
			# The winning play is the last element in sortedPlays
			trickWinner = sortedPlays[-1][0]
			
			# Update the game state
			self.tricksTaken[trickWinner] += 1
			self.discards += [card for (player, card) in self.currentTrick]
			self.currentTrick = []
			self.playerToMove = trickWinner
			
			# If the next player's hand is empty, this round is over
			if self.playerHands[self.playerToMove] == []:
				self.gameOver = True				
				#knock out the players not taking the largest tricks
				if self.tricksTaken[1] + self.tricksTaken[3] < self.tricksTaken[2] + self.tricksTaken[4]:
					self.knockedOut[1] = True
					self.knockedOut[3] = True
				else:
					self.knockedOut[2] = True
					self.knockedOut[4] = True
				
				
				
	
	def GetMoves(self):
		""" Get all possible moves from this state.
		"""
		hand = self.playerHands[self.playerToMove]
		if self.currentTrick == []:
			# May lead a trick with any card
			return hand
		else:
			(leader, leadCard) = self.currentTrick[0]
			# Must follow suit if it is possible to do so
			cardsInSuit = [card for card in hand if card.suit == leadCard.suit]
			if cardsInSuit != []:
				return cardsInSuit
			else:
				# Can't follow suit, so can play any card
				return hand
	
	def GetResult(self, player):
		""" Get the game result from the viewpoint of player. 
		"""
		return 0 if (self.knockedOut[player]) else 1

	def GetTricks(self, player):
		""" Get the tricks taken by player. 
		"""
		return self.tricksTaken[player]

	
	def __repr__(self):
		""" Return a human-readable representation of the state
		"""

		#result  = "Cards %i" % self.tricksInRound
		result = "P%i" % self.playerToMove
		result += " : ["
		result += ",".join(("P%i:%s" % (player, card)) for (player, card) in self.currentTrick)
		result += "] | "
		if self.playerToMove == 1:
			playerhands = self.playerHands[self.playerToMove]
			Ccards = [card for card in playerhands if card.suit == 'C']
			Dcards = [card for card in playerhands if card.suit == 'D']
			Hcards = [card for card in playerhands if card.suit == 'H']
			Scards = [card for card in playerhands if card.suit == 'S']
			sortedCards = sorted(Ccards, key = lambda card : card.rank) + sorted(Dcards, key = lambda card : card.rank) \
						+ sorted(Hcards, key = lambda card : card.rank) + sorted(Scards, key = lambda card : card.rank)
			result += ",".join(str(card) for card in sortedCards)		
		result += " | Trump: %s" % self.trumpSuit
		result += " | Scores: %i" % self.tricksTaken[self.playerToMove]
		
		return result