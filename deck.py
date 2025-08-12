import collections
import random

Card = collections.namedtuple('Card', ['rank', 'suit'])

class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self.cards = [Card(rank, suit) for suit in self.suits
                                        for rank in self.ranks for _ in range(2)]
        self.cards += [Card('Joker', 'Black'), Card('Joker', 'Red'), Card('Joker', 'Black'), Card('Joker', 'Red')]
        self.players = []
    
    def distribute(self):
        random.shuffle(self.cards)
        for i in range(4):
            hand = self.cards[i*27:(i+1)*27]
            self.players.append(PlayerDeck(hand))

class PlayerDeck:
    orderofRanks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2', 'Black Joker', 'Red Joker']
    def __init__(self, cards):
        self.cards = cards
        self.count = [0]*15
        for card in cards:
            if card.rank == 'Joker':
                if card.suit == 'Black': self.count[13] += 1
                else: self.count[14] += 1
            else: self.count[self.orderofRanks.index(card.rank)] += 1
        spade_count = [0]*13
        diamond_count = [0]*13
        club_count = [0]*13
        heart_count = [0]*13
        suit_count = [spade_count, diamond_count, club_count, heart_count]
        self.special = 0
        for card in cards:
            if card.suit == 'spades':
                spade_count[self.orderofRanks.index(card.rank)] += 1
            elif card.suit == 'diamonds':
                diamond_count[self.orderofRanks.index(card.rank)] += 1
            elif card.suit == 'clubs':
                club_count[self.orderofRanks.index(card.rank)] += 1
            elif card.suit == 'hearts':
                if card.rank == '2':
                    self.special += 1
                heart_count[self.orderofRanks.index(card.rank)] += 1
        self.royalflush = []
        for suit in suit_count:
            for i in range(8):
                k = min(suit[i:i+5])
                self.royalflush += [self.orderofRanks[i]] * k
        #Special heart of A

    def single(self):
        return [self.orderofRanks[i] for i in range(15) if self.count[i] >= 1]

    def pair(self):
        return [self.orderofRanks[i] for i in range(15) if self.count[i] >= 2]
    
    def three(self):
        return [self.orderofRanks[i] for i in range(13) if self.count[i] >= 3]
    
    def four(self):    
        return [self.orderofRanks[i] for i in range(13) if self.count[i] >= 4]
    
    def five(self):
        return [self.orderofRanks[i] for i in range(13) if self.count[i] >= 5]
    
    def six(self):
        return [self.orderofRanks[i] for i in range(13) if self.count[i] >= 6]

    
    def flush(self):
        return [self.orderofRanks[i] for i in range(8) if min(self.count[i:i+5]) >= 1 and self.orderofRanks[i] not in self.royalflush]
    
    def three_of_pair(self):
        return [self.orderofRanks[i] for i in range(10) if min(self.count[i:i+3]) >= 2]
    
    def two_of_three(self):
        return [self.orderofRanks[i] for i in range(11) if min(self.count[i:i+2]) >= 3]
    
    def legal(self):
        return [self.single(), self.pair(), self.three(), self.four(), self.five(),
                self.flush(), self.three_of_pair(), self.two_of_three()]
        
test = FrenchDeck()
test.distribute()
player = test.players[0]
print(player.cards)
print(len(player.cards))
print(player.royalflush, player.flush())