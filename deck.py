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

    def _single(self):
        return [self.orderofRanks[i] for i in range(15) if self.count[i] >= 1]

    def _pair(self):
        return [self.orderofRanks[i] for i in range(15) if self.count[i] >= 2]
    
    def _three(self):
        return [self.orderofRanks[i] for i in range(13) if self.count[i] >= 3]
    
    def _four(self):    
        return [self.orderofRanks[i] for i in range(13) if self.count[i] >= 4]
    
    def _five(self):
        return [self.orderofRanks[i] for i in range(13) if self.count[i] >= 5]
    
    def _six(self):
        return [self.orderofRanks[i] for i in range(13) if self.count[i] >= 6]
    
    def _flush(self):
        return [self.orderofRanks[i] for i in range(8) if min(self.count[i:i+5]) >= 1 and self.orderofRanks[i] not in self.royalflush]
    
    def _three_of_pair(self):
        return [self.orderofRanks[i] for i in range(10) if min(self.count[i:i+3]) >= 2]
    
    def _two_of_three(self):
        return [self.orderofRanks[i] for i in range(11) if min(self.count[i:i+2]) >= 3]
    
    def _legal(self):
        return [self._single(), self._pair(), self._three(), self._three_of_pair(), self._flush(), self._two_of_three(), self._four(), self._five(), self.royalflush, self._six()] #bombs: 11,12,13,14
    
    def can_play(self, other_hand):
        hand = self._legal()
        if other_hand.type <= 6:
            for i in range(6):
                if other_hand.type == i+1:
                    hand[i] = [card for card in hand[i] if self.orderofRanks.index(card) > self.orderofRanks.index(other_hand.rank)]
                else: hand[i] = []
        else: 
            for i in range(10):
                if other_hand.type > i+5: hand[i] = []
                elif other_hand.type == i+5:
                    hand[i] = [card for card in hand[i] if self.orderofRanks.index(card) > self.orderofRanks.index(other_hand.rank)]
        return hand
    
    def play(self, hand):
        #Should make sure the hand is legal, won't check here
        if hand.type >0 and hand.type <= 3:
            self.count[self.orderofRanks.index(hand.rank)] -= hand.type
        if hand.type == 4:
            for i in range(3):
                self.count[self.orderofRanks.index(hand.rank) + i] -= 2
        if hand.type == 5 or hand.type == 13:
            for i in range(5):
                self.count[self.orderofRanks.index(hand.rank) + i] -= 1
        if hand.type == 6:
            for i in range(2):
                self.count[self.orderofRanks.index(hand.rank) + i] -= 3
        if hand.type == 11 or hand.type == 12:
            self.count[self.orderofRanks.index(hand.rank)] -= (hand.type-7)
        if hand.type == 14:
            self.count[self.orderofRanks.index(hand.rank)] -= 6

        #check royalflush
        self.royalflush = [card for card in self.royalflush if min(self.count[self.orderofRanks.index(card):self.orderofRanks.index(card)+5]) >= 1]

#Debug      
class Hand:
    def __init__(self, type, rank):
        self.type = type
        self.rank = rank

"""   
test = FrenchDeck()
test.distribute()
player = test.players[0]
print(player.cards)
print(player.royalflush)
other_hand = Hand(3, '4')
print(player.can_play(other_hand))
"""
player = PlayerDeck([Card(rank='5', suit='hearts'), Card(rank='Q', suit='diamonds'), Card(rank='4', suit='spades'), Card(rank='7', suit='hearts'), Card(rank='9', suit='hearts'), Card(rank='J', suit='diamonds'), Card(rank='9', suit='spades'), Card(rank='Joker', suit='Red'), Card(rank='7', suit='clubs'), Card(rank='4', suit='diamonds'), Card(rank='Q', suit='spades'), Card(rank='3', suit='spades'), Card(rank='Q', suit='diamonds'), Card(rank='J', suit='clubs'), Card(rank='3', suit='diamonds'), Card(rank='J', suit='hearts'), Card(rank='6', suit='hearts'), Card(rank='4', suit='spades'), Card(rank='K', suit='spades'), Card(rank='3', suit='clubs'), Card(rank='5', suit='clubs'), Card(rank='5', suit='hearts'), Card(rank='8', suit='clubs'), Card(rank='4', suit='clubs'), Card(rank='6', suit='clubs'), Card(rank='8', suit='diamonds'), Card(rank='6', suit='spades')])
print(player.count, player.royalflush)
other_hand = Hand(5, '4')
print(player.can_play(other_hand))
player.play(Hand(2, '8'))
print(player.count, player.royalflush)
