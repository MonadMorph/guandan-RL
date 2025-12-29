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
        self.history = []
        self.left = [27, 27, 27, 27, 108]  #player0, player1, player2, player3, total
    
    def distribute(self):
        random.shuffle(self.cards)
        hands = []
        for i in range(4):
            sublist = self.cards[i*27:(i+1)*27]
            sublist.sort(key=lambda card: self.orderofRanks.index(card.rank))
            hands.append(sublist)
        #implement exchange hand            
        self.players = [PlayerDeck(hands[i], self.orderofRanks) for i in range(4)]

    def play(self, player_index, hand):
        if self.history and player_index == self.history[-1][0] and hand.type == 7 and hand.aux_rank is not None: # Handle second "play" of 3+2
            self.history[-1] = (player_index, hand)
        else:
            self.history.append((player_index, hand))
        if hand is not None:
            self.players[player_index].play(hand)
            self.left[4] -= hand.size
            self.left[player_index] -= hand.size

    def state(self, player_index, prev_hand):
        #private hand, private legal actions, public history (last 16), public cards left (mine, next, ..., total), (public last player index, public last hand), player index
        return (self.players[player_index].count + [len(self.players[player_index].royalflush)], 
                self.players[player_index].can_play(prev_hand[0]), 
                self.history[-16:], 
                self.left[player_index:4] + self.left[:player_index] + [self.left[4]], 
                (prev_hand[1], prev_hand[0]), 
                player_index)


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
                self.royalflush += [i] * k

    def __repr__(self):
        ans = ''
        for i in range(len(self.orderofRanks)):
            if self.count[i] > 0:
                ans += self.orderofRanks[i]*self.count[i]
        return ans
    
    def _single(self):
        return [i for i in range(15) if self.count[i] >= 1]

    def _pair(self):
        return [i for i in range(15) if self.count[i] >= 2]
    
    def _three(self):
        return [i for i in range(13) if self.count[i] >= 3]
    
    def _four(self):    
        return [i for i in range(13) if self.count[i] >= 4]
    
    def _five(self):
        return [i for i in range(13) if self.count[i] >= 5]
    
    def _six(self):
        return [i for i in range(13) if self.count[i] >= 6]
    
    def _flush(self):
        return [i for i in range(8) if min(self.count[i:i+5]) >= 1 and self.orderofRanks[i] not in self.royalflush]
    
    def _three_of_pair(self):
        return [i for i in range(10) if min(self.count[i:i+3]) >= 2]
    
    def _two_of_three(self):
        return [i for i in range(11) if min(self.count[i:i+2]) >= 3]
    
    #to be added: 3+2, kingbomb

    
    def _legal(self):
        return [self._single(), self._pair(), self._three(), self._three_of_pair(), self._flush(), self._two_of_three(), self._three(), self._four(), self._five(), self.royalflush, self._six()] #bombs: 11,12,13,14
    
    
    def can_play(self, other_hand=None):
        hand = self._legal()
        pairs = hand[1].copy()
        if other_hand is not None and other_hand.type == 7 and other_hand.aux_rank is None: # aux_rank is None, which means this is for selecting the "2" of 3+2
            try:
                pairs.remove(other_hand.rank)
            except ValueError:
                pass
            ans = [Hand(2, card) for card in pairs]
            return ans

        if other_hand is None:
            pass
        elif other_hand.type <= 6:
            for i in range(7):
                if other_hand.type == i+1:
                    hand[i] = [card for card in hand[i] if card > other_hand.rank]
                    if other_hand.type == 7: # All these to check if we have a valid pair for 3+2
                        if len(pairs) == 0: hand[6] = []
                        elif len(pairs) == 1 and pairs[0] in hand[6]:
                            hand[6].remove(pairs[0])
                else: hand[i] = []
        else: 
            for i in range(11):
                if other_hand.type > i+4: hand[i] = []
                elif other_hand.type == i+4:
                    hand[i] = [card for card in hand[i] if card > other_hand.rank]
        ans = []
        for i in range(len(hand)):
            if i <= 6:
                ans += [Hand(i+1, card) for card in hand[i]]
            else: ans += [Hand(i+4, card) for card in hand[i]]
        return ans
    
    def play(self, hand):
        #Should make sure the hand is legal, won't check here
        if hand.type >0 and hand.type <= 3:
            self.count[hand.rank] -= hand.type
        if hand.type == 4:
            for i in range(3):
                self.count[hand.rank + i] -= 2
        if hand.type == 5 or hand.type == 13:
            for i in range(5):
                self.count[hand.rank + i] -= 1
        if hand.type == 6:
            for i in range(2):
                self.count[hand.rank + i] -= 3
        if hand.type == 7: # 3+2 is "played" twice
            if hand.aux_rank == None:
                self.count[hand.rank] -= 3
            else:
                self.count[hand.aux_rank] -= 2
        if hand.type == 11 or hand.type == 12:
            self.count[hand.rank] -= (hand.type-7)
        if hand.type == 14:
            self.count[hand.rank] -= 6

        #check royalflush
        self.royalflush = [card for card in self.royalflush if min(self.count[card:card+5]) >= 1]

'''Type as follows:
1: single 
2: pair
3: three
4: three of pair
5: flush
6: two of three
7: three plus two
11: four
12: five
13: royal flush
14: six'''
class Hand:
    orderofRanks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2', 'Black Joker', 'Red Joker']
    def __init__(self, type, rank, aux_rank = None):
        self.type = type
        self.rank = rank #Rank now is just the index in orderofRanks
        self.aux_rank = aux_rank # only for 3+2
        if self.type <= 3: self.size = self.type
        elif self.type == 4 or self.type == 6: self.size = 6
        elif self.type == 5 or self.type == 13 or self.type == 7: self.size = 5
        elif self.type == 11 or self.type == 12: self.size = self.type - 7
        elif self.type == 14: self.size = 6

    def __repr__(self):
        if self.type <= 3:
            return (self.orderofRanks[self.rank] + ' ')*self.type
        elif self.type == 4:
            return ' '.join([self.orderofRanks[self.rank+i] for i in range(3) for _ in range(2)])
        elif self.type == 5:
            return ' '.join([self.orderofRanks[self.rank+i] for i in range(5)])
        elif self.type == 6:
            return ' '.join([self.orderofRanks[self.rank+i] for i in range(2) for _ in range(3)])
        elif self.type == 7:
            return (self.orderofRanks[self.rank] + ' ')*3 + (self.orderofRanks[self.aux_rank] + ' ')*2
        elif self.type == 11 or self.type == 12:
            return (self.orderofRanks[self.rank] + ' ')*(self.type-7)
        elif self.type == 13:
            return 'Royal Flush ' + ' '.join([self.orderofRanks[self.rank+i] for i in range(5)])
        elif self.type == 14:
            return (self.orderofRanks[self.rank] + ' ')*6


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