import collections
import random

Card = collections.namedtuple('Card', ['rank', 'suit'])

class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()
    orderofRanks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2', 'Black Joker', 'Red Joker']

    def __init__(self, last_game = None):
        self.cards = [Card(rank, suit) for suit in self.suits
                                        for rank in self.ranks for _ in range(2)]
        self.cards += [Card('Black Joker', 'Black'), Card('Red Joker', 'Red'), Card('Black Joker', 'Black'), Card('Red Joker', 'Red')]
        self.exchange = last_game
    
    def distribute(self):
        random.shuffle(self.cards)
        hands = []
        for i in range(4):
            sublist = self.cards[i*27:(i+1)*27]
            sublist.sort(key=lambda card: self.orderofRanks.index(card.rank))
            hands.append(sublist)
        #implement exchange hand            
        self.players = [PlayerDeck(hands[i], self.orderofRanks) for i in range(4)]

class PlayerDeck:
    def __init__(self, cards, orderofRanks):
        self.cards = cards
        self.count = [0]*15
        self.orderofRanks = orderofRanks
        for card in cards:
            self.count[self.orderofRanks.index(card.rank)] += 1
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
                if card.rank == self.orderofRanks[-3]:  # Heart of 2
                    self.special += 1
                heart_count[self.orderofRanks.index(card.rank)] += 1
        self.royalflush = []
        #Implement special heart of 2
        #Remove duplicate Royal Flush
        for suit in suit_count:
            for i in range(8):
                k = min(suit[i:i+5])
                self.royalflush += [self.orderofRanks[i]] * k

    def __repr__(self):
        ans = ''
        for i in range(len(self.orderofRanks)):
            if self.count[i] > 0:
                ans += self.orderofRanks[i]*self.count[i]
        return ans
    
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
    
    #to be added: 3+2, kingbomb

    
    def _legal(self):
        return [self._single(), self._pair(), self._three(), self._three_of_pair(), self._flush(), self._two_of_three(), self._four(), self._five(), self.royalflush, self._six()] #bombs: 11,12,13,14
    
    
    def can_play(self, other_hand=None):
        hand = self._legal()
        if other_hand is None:
            pass
        elif other_hand.type <= 6:
            for i in range(6):
                if other_hand.type == i+1:
                    hand[i] = [card for card in hand[i] if self.orderofRanks.index(card) > self.orderofRanks.index(other_hand.rank)]
                else: hand[i] = []
        else: 
            for i in range(10):
                if other_hand.type > i+5: hand[i] = []
                elif other_hand.type == i+5:
                    hand[i] = [card for card in hand[i] if self.orderofRanks.index(card) > self.orderofRanks.index(other_hand.rank)]
        ans = []
        for i in range(len(hand)):
            if i <= 5:
                ans += [Hand(i+1, card) for card in hand[i]]
            else: ans += [Hand(i+5, card) for card in hand[i]]
        return ans
    
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

class Hand:
    orderofRanks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2', 'Black Joker', 'Red Joker']
    def __init__(self, type, rank):
        self.type = type
        self.rank = rank

    def __repr__(self):
        if self.type <= 3:
            return (self.rank + ' ')*self.type
        elif self.type == 4:
            n = self.orderofRanks.index(self.rank)
            return ' '.join([self.orderofRanks[n+i] for i in range(3) for _ in range(2)])
        elif self.type == 5:
            n = self.orderofRanks.index(self.rank)
            return ' '.join([self.orderofRanks[n+i] for i in range(5)])
        elif self.type == 6:
            n = self.orderofRanks.index(self.rank)
            return ' '.join([self.orderofRanks[n+i] for i in range(2) for _ in range(3)])
        elif self.type == 11 or self.type == 12:
            return (self.rank + ' ')*(self.type-7)
        elif self.type == 13:
            n = self.orderofRanks.index(self.rank)
            return 'Royal Flush ' + ' '.join([self.orderofRanks[n+i] for i in range(5)])
        elif self.type == 14:
            return (self.rank + ' ')*6



"""   
test = FrenchDeck()
test.distribute()
player = test.players[0]
print(player.cards)
print(player.royalflush)
other_hand = Hand(3, '4')
print(player.can_play(other_hand))
player = PlayerDeck([Card(rank='5', suit='hearts'), Card(rank='Q', suit='diamonds'), Card(rank='4', suit='spades'), Card(rank='7', suit='hearts'), Card(rank='9', suit='hearts'), Card(rank='J', suit='diamonds'), Card(rank='9', suit='spades'), Card(rank='Joker', suit='Red'), Card(rank='7', suit='clubs'), Card(rank='4', suit='diamonds'), Card(rank='Q', suit='spades'), Card(rank='3', suit='spades'), Card(rank='Q', suit='diamonds'), Card(rank='J', suit='clubs'), Card(rank='3', suit='diamonds'), Card(rank='J', suit='hearts'), Card(rank='6', suit='hearts'), Card(rank='4', suit='spades'), Card(rank='K', suit='spades'), Card(rank='3', suit='clubs'), Card(rank='5', suit='clubs'), Card(rank='5', suit='hearts'), Card(rank='8', suit='clubs'), Card(rank='4', suit='clubs'), Card(rank='6', suit='clubs'), Card(rank='8', suit='diamonds'), Card(rank='6', suit='spades')])
print(player.count, player.royalflush)
other_hand = Hand(5, '4')
print(player.can_play(other_hand))
player.play(Hand(2, '8'))
print(player.count, player.royalflush)
"""