import random
import socket

HOST = ""
PORT = 8888

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

    #affectionTokens lists the number of affection tokens owned by each player
    affectionTokens = {}

    def addPlayer(self, name, conn):
        self.players.append(name.lower())
        self.playerSockets[name.lower()] = conn

    def notifyPlayer(self, player, msg):
        self.playerSockets[player].send((msg + '\n').encode())

    def notifyAll(self, msg):
        for player in self.players:
            self.notifyPlayer(player, msg)

    def notifyGameState(self, player):
        dashStr = "-----------------------------------"
        affTokStr = "Affection tokens: " + ', '.join([p + ':' + str(self.affectionTokens[p]) for p in self.players])
        deckStr = "Cards in deck: " + str(len(self.deck))
        remPlayerStr = "Remaining players: " + ', '.join(self.getAllRemainingPlayers())
        discardStr = "Discards: " + ', '.join([p+':'+''.join([str(c) for c in self.discard[p]]) for p in self.players])
        handStr = "Your hand: " + ', '.join([self.getCardStr(c) for c in self.hands[player]])

        notifyStr = '\n'.join([dashStr, affTokStr, deckStr, remPlayerStr, discardStr, handStr])
        self.notifyPlayer(player, notifyStr)

    def notifyAllGameState(self):
        for player in self.players:
            self.notifyGameState(player)

    def discardHand(self, player):
        self.notifyAll(player + " discards " + self.getCardStr(self.hands[player][0]))
        self.discard[player].append(self.hands[player][0])
        self.hands[player] = []

    def getAllOtherUnprotectedPlayers(self, player):
        return [p for p in self.players if p != player and self.isUnprotected(p)]

    def getAllUnprotectedPlayers(self):
        return [p for p in self.players if self.isUnprotected(p)]

    def isUnprotected(self, player):
        if len(self.discard[player]) > 0:
            return self.discard[player][-1] != 4
        else:
            return True

    def getAllRemainingPlayers(self):
        return [p for p in self.players if not self.isEliminated(p)]

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
        self.discardHand(player)

    def requestInput(self, player):
        return self.playerSockets[player].recv(1024).decode()

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
            self.notifyPlayer(player, request)
            card = self.requestInput(player).strip()
            if not card.isdigit() or int(card) < 1 or int(card) > 8:
                self.notifyPlayer(player, "Please enter an integer between 1 and 8")
            else:
                return int(card)

    def guardAction(self, player):
        name = self.requestPlayerName(player, "Whose card will you guess?", False)
        card = self.requestCard(player, "Which card will you guess?")
        self.notifyAll(player + " guesses that " + name + "'s card is " + self.getCardStr(card))
        if self.hands[name] == [card]:
            self.notifyAll(player + " is correct! " + name + " is eliminated!")
            self.eliminatePlayer(name)
        else:
            self.notifyAll(player + " is incorrect!")

    def priestAction(self, player):
        name = self.requestPlayerName(player, "Whose hand will you look at?", False)
        self.notifyAll(player + " looks at " + name + "'s hand")
        self.notifyPlayer(player, name + " has a " + self.getCardStr(self.hands[name][0]))

    def baronAction(self, player):
        name = self.requestPlayerName(player, "Whose card will you compare yours with?", False)
        self.notifyAll(player + " compares cards with " + name)
        self.notifyPlayer(player, name + " has a " + self.getCardStr(self.hands[name][0]))
        self.notifyPlayer(name, player + " has a " + self.getCardStr(self.hands[player][0]))
        if self.hands[player][0] < self.hands[name][0]:
            self.notifyAll(name + " wins! " + player + " is eliminated!")
            self.eliminatePlayer(player)
        elif self.hands[name][0] < self.hands[player][0]:
            self.notifyAll(player + " wins! " + name + " is eliminated!")
            self.eliminatePlayer(name)
        else:
            self.notifyAll("It's a tie! Both players remain in the game.")

    def handmaidAction(self, player):
        self.notifyAll(player + " is protected until the his/her next turn.")

    def princeAction(self, player):
        name = self.requestPlayerName(player, "Who will discard his/her hand and draw a new card?", True)
        self.notifyAll(player + " chooses " + name + " to discard his/her hand and draw a new card.")
        self.discardHand(name)
        if self.discard[name][-1] == 8:
            self.eliminatePlayer(name)
        else:
            if len(self.deck) > 0:
                self.hands[name] = [self.deck.pop()]
            else:
                self.hands[name] = [self.removedCards.pop()]

    def kingAction(self, player):
        name = self.requestPlayerName(player, "With whom will you swap hands?", False)
        self.notifyAll(player + " swaps hands with " + name)
        curHand = self.hands[player]
        self.hands[player] = self.hands[name]
        self.hands[name] = curHand

    def countessAction(self, player):
        self.notifyAll(self.getCardStr(7) + " has no action.")

    def princessAction(self, player):
        self.notifyAll(player + " is eliminated from the game!")
        self.eliminatePlayer(player)

    def takeTurn(self, player):
        self.hands[player].append(self.deck.pop())
        self.notifyAllGameState()
        self.notifyAll(player + "'s turn")
        while True:
            card = self.requestCard(player, "Which card will you play?")
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
                    self.discard[player].append(card)

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
                    return
            else:
                self.notifyPlayer(player, "That card is not in your hand.")

    #returns the name of the round winner
    def startRound(self, prevWinner):
        self.deck = [1]*5 + [2,2,3,3,4,4,5,5,6,7,8]
        self.discard = {p:[] for p in self.players}
        random.shuffle(self.deck)
        if len(self.players) == 2:
            self.removedCards = [self.deck.pop() for i in range(3)]
        else:
            self.removedCards = [self.deck.pop()]

        curPlayerIdx = prevWinner

        for p in self.players:
            self.hands[p] = [self.deck.pop()]

        while len(self.deck) > 0:
            self.takeTurn(self.players[curPlayerIdx])
            if len(self.getAllRemainingPlayers()) == 1:
                return self.getAllRemainingPlayers()[0]
            #determine the index of the next player
            while True:
                curPlayerIdx = (curPlayerIdx + 1) % len(self.players)
                if not self.isEliminated(self.players[curPlayerIdx]):
                    break

        #determine the winner by who has the highest card. If there is a tie,
        #determine winner by sum of discarded numbers
        scoreList = [(self.hands[p][0], p) for p in self.players if len(self.hands[p]) > 0]
        maxScore, player = max(scoreList)
        maxPlayers = [p for s, p in scoreList if s == maxScore]
        if len(maxPlayers) == 1:
            return self.players[maxPlayers[0]]
        else:
            #we're just gonna assume that it's impossible for the sum of
            #discarded cards to be equal for two players, since that's what
            #the official rules do
            curMax = 0
            curName = ""
            for p in maxPlayers:
                discardedScore = sum(self.discard[p])
                if discardedScore > curMax:
                    curMax = discardedScore
                    curName = p
            return curName

    def playGame(self):
        random.shuffle(self.players)
        #determine number of affection tokens required to win
        if len(self.players) == 2:
            winningScore = 7
        elif len(self.players) == 3:
            winningScore = 5
        elif len(self.players) == 4:
            winningScore = 4
        else:
            raise TooManyPlayersError
        for p in self.players:
            self.affectionTokens[p] = 0

        prevWinner = 0
        while self.affectionTokens[self.players[prevWinner]] < winningScore:
            winnerName = self.startRound(prevWinner)
            self.notifyAll(winnerName + " wins the round!")
            self.affectionTokens[winnerName] += 1
            prevWinner = self.players.index(winnerName)

        self.notifyAll(winnerName + " wins the game!")


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(10)

playerNames = []
conns = []

#wait for first player
print("Waiting for player 1")
conn, addr = s.accept()
conn.send("Please enter your name: ".encode())
name = conn.recv(1024).decode()
conns.append(conn)
playerNames.append(name.strip())

#ask how many players
conn.send("How many players? ".encode())
numPlayers = conn.recv(1024).decode().strip()
while not numPlayers.isdigit() or int(numPlayers) < 2 or int(numPlayers) > 4:
    conn.send("Please enter a number between 2 and 4: ".encode())
    numPlayers = conn.recv(1024).decode()
numPlayers = int(numPlayers)


for i in range(1, numPlayers):
    print("Waiting for player", i+1)
    conn, addr = s.accept()
    conn.send("Please enter your name: ".encode())
    name = conn.recv(1024).decode()
    conns.append(conn)
    playerNames.append(name.strip())

h = LoveLetter()
for p, c in zip(playerNames, conns):
    h.addPlayer(p, c)
h.playGame()