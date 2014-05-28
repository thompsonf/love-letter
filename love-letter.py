class LoveLetter():
	#deck is a list of cards left in the deck
	deck = []

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

	def getAllUnprotectedPlayers(self):
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
		self.hands[player] = []

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
		self.notifyAll(player + " discards " + self.getCardStr(card))
		self.notifyAll(player + " guesses that " + name + "'s card is " + self.getCardStr(card))
		if self.hands[name] == [card]:
			self.notifyAll(player + " is correct! " + name + " is eliminated!")
		else:
			self.notifyAll(player + " is incorrect!")

	def priestAction(self, player):
		

	def baronAction(self, player):
		pass

	def handmaidAction(self, player):
		pass

	def princeAction(self, player):
		pass

	def kingAction(self, player):
		pass

	def countessAction(self, player):
		pass

	def princessAction(self, player):
		pass

	def discard(self, player, card):
		if card in self.hands[player]:
			#if 7 is in hand along with 5 or 6, 7 must be discarded
			if card != 7 and (5 in self.hands[player] or 6 in self.hands[player]) and 7 in self.hands[player]:
				self.notifyPlayer(player, "You must discard " + self.getCardStr(7))
			else:
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
					raise InvalidCardError
			#actually discard the card
			if self.hands[player][0] == card:
				self.hands[player] = [self.hands[player][1]]
			else:
				self.hands[player] = [self.hands[player][0]]
		else:
			self.notifyPlayer(player, "That card is not in your hand")