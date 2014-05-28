import random

class LoveLetter():
	#deck is a list of cards left in the deck
	deck = []

	#some cards are removed at the beginning of the game
	removedCards = []

	#discard maps players to the cards they've
	#discarded so far
	discard = {}

	#players is an ordered list of player names
	#with order being the turn order
	players = []

	#playerSockets maps player names to ways to contact them
	playerSockets = {}

	#hands lists the cards in each player's hand
	#if no card is in hand (hands[player] == []), the player's turn
	#will be skipped (he/she is out of the round)
	hands = {}

	#score lists the number of affection tokens owned by each player
	score = {}

	#player whose turn is next
	self.curPlayerIdx = 0

	def discardHand(self, player):
		self.notifyAll(player + " discards " + self.getCardStr(self.hands[player][0]))
		self.discard[player].append(self.hands[player][0])
		self.hands[player] = []

	def getAllOtherUnprotectedPlayers(self, player):
		return [p for p in self.players if p != player and self.isUnprotected(p)]

	def getAllUnprotectedPlayers(self, player):
		return [p for p in self.players if self.isUnprotected(p)]

	def isUnprotected(self, player):
		if len(discard[player] > 0):
			return discard[p][-1] != 4
		else:
			return True

	def getAllRemainingPlayers(self):
		return [p for p in self.players if not self.isEliminated(player)]

	def isEliminated(self, player):
		return len(self.hands[player]) == 0

	def getCardStr(self, card):
		cardNames = ["Guard Odette",
		"Priest Tomas",
		"Baron Talus",
		"Handmaid Susannah",
		"Prince Arnaud",
		"King Arnaud IV",
		"Countess Wilhelmina",
		"Princess Annette"]
		return str(card) + ': ' + cardNames[card - 1]

	def eliminatePlayer(self, player):
		self.discardHand(self, player)

	def requestPlayerName(self, player, request, allowSelf):
		while True:
			self.notifyPlayer(player, request)
			name = self.requestInput(player).strip()
			if not allowSelf and name == player:
				self.notifyPlayer(player, "You can't enter your own name!")
			elif name not in self.players:
				self.notifyPlayer(player, "That player is not in the game!")
			elif name not in self.getAllRemainingPlayers():
				self.notifyPlayer(player, "That player has already been eliminated!")
			elif name not in self.getAllUnprotectedPlayers():
				self.notifyPlayer(player, "That player is protected by the handmaid!")
			else:
				return name

	def requestCard(self, player, request):
		while True:
			self.notifyPlayer(player, request):
			card = self.requestInput(player).strip()
			if not card.isdigit() or int(card) < 1 or int(card) > 8:
				self.notifyPlayer(player, "Please enter an integer between 1 and 8")
			else:
				return int(card)

	def guardAction(self, player):
		name = requestPlayerName(player, "Whose card will you guess?", False)
		card = requestCard(player, "Which card will you guess?")
		self.notifyAll(player + " guesses that " + name + "'s card is " + self.getCardStr(card))
		if self.hands[name] == [card]:
			self.notifyAll(player + " is correct! " + name + " is eliminated!")
			self.eliminatePlayer(name)
		else:
			self.notifyAll(player + " is incorrect!")

	def priestAction(self, player):
		name = requestPlayerName(player, "Whose hand will you look at?", False)
		self.notifyAll(player + " looks at " + name + "'s hand")
		self.notifyPlayer(player, name + " has a " + self.getCardStr(self.hands[name][0]))

	def baronAction(self, player):
		name = requestPlayerName(player, "Whose card will you compare yours with?", False)
		self.notifyAll(player + " compares cards with " + name)
		if self.hands[player] < self.hands[name]:
			self.notifyAll(name + " wins! " + player + " is eliminated!")
			self.eliminatePlayer(player)
		elif self.hands[name] < self.hands[player]:
			self.notifyAll(player + " wins! " + name + " is eliminated!")
			self.eliminatePlayer(name)
		else:
			self.notifyAll("It's a tie! Both players remain in the game.")

	def handmaidAction(self, player):
		self.notifyAll(player + " is protected until the his/her next turn.")

	def princeAction(self, player):
		name = requestPlayerName(player, "Chose who will discard his/her hand and draw a new card.", True)
		self.notifyAll(player + " chooses " + name + " to discard his/her hand and draw a new card.")
		self.discardHand(name)
		#still need to draw a new card

	def kingAction(self, player):
		name = requestPlayerName(player, "With whom will you swap hands?", False)
		self.notifyAll(player + " swaps hands with " + name)
		curHand = self.hands[player]
		self.hands[player] = self.hands[name]
		self.hands[name] = curHand

	def countessAction(self, player):
		self.notifyAll(self.getCardStr(7) + " has no action.")

	def princessAction(self, player):
		self.notifyAll(player + " is eliminated from the game!")
		self.eliminatePlayer(player)

	def discardAction(self, player, card):
		if card in self.hands[player]:
			#if 7 is in hand along with 5 or 6, 7 must be discarded
			if card != 7 and (5 in self.hands[player] or 6 in self.hands[player]) and 7 in self.hands[player]:
				self.notifyPlayer(player, "You must discard " + self.getCardStr(7))
			else:
				if card < 1 or card > 8:
					raise InvalidCardError

				self.notifyAll(player + " discards " + self.getCardStr(card))
				#actually discard the card
				if self.hands[player][0] == card:
					self.hands[player] = [self.hands[player][1]]
				else:
					self.hands[player] = [self.hands[player][0]]

				if self.getAllOtherUnprotectedPlayers(player) == [] and card in [1,2,3,6]:
					self.notifyAll("All other active players are protected by the handmaid, so the card has no effect.")
					return
				if card == 1:
					self.guardAction(player)
				elif card == 2:
					self.priestAction(player)
				elif card == 3:
					self.baronAction(player)
				elif card == 4:
					self.handmaidAction(player)
				elif card == 5:
					self.princeAction(player)
				elif card == 6:
					self.kingAction(player)
				elif card == 7:
					self.countessAction(player)
				elif card == 8:
					self.princessAction(player)
		else:
			self.notifyPlayer(player, "That card is not in your hand")

	#returns the name of the round winner
	def startRound(self, prevWinner):
		self.deck = [1]*5 + [2,2,3,3,4,4,5,5,6,7,8]
		random.shuffle(self.deck)
		if len(self.players) == 2:
			self.removedCards = [self.deck.pop() for i in range(3)]
		else:
			self.removedCards = [self.deck.pop()]

		curPlayerIdx = prevWinner

		for p in players:
			self.hands[p] = self.deck.pop()

		while len(self.deck) > 0:
			self.takeTurn(players[curPlayerIdx])
			if len(self.getAllRemainingPlayers()) == 1:
				return self.getAllRemainingPlayers()[0]
			#determine the index of the next player
			while True:
				curPlayerIdx = (curPlayerIdx + 1) % len(self.players)
				if not self.isEliminated(self.players[curPlayerIdx]):
					break

		#determine the winner by who has the highest card. If there is a tie,
		#determine winner by sum of discarded numbers
		scoreList = [self.hands[p][0] for p in self.players if len(self.hands[p]) > 0 else 0]
		maxScore = max(scoreList)
		maxPlayers = [idx for idx, score in enumerate(maxScore) if score == maxScore]
		if len(maxPlayers) == 1:
			return self.players[maxPlayers[0]]
		else:
			#we're just gonna assume that it's impossible for the sum of
			#discarded cards to be equal for two players, since that's what
			#the official rules do
			curMax = 0
			curName = ""
			for idx in maxPlayers:
				name = self.players[idx]
				discardedScore = sum(self.discard[name])
				if discardedScore > curMax:
					curMax = discardedScore
					curName = name
			return name