from deck import FrenchDeck
import random

test = FrenchDeck()
test.distribute()
for player in test.players:
    print(player)

k = 0
prev_hand = [None, 0]  # Placeholder for other hand, if needed
while True:
    turn = k%4
    if prev_hand[1] == turn: prev_hand[0] = None  # Reset if it's the same player's turn
    poss = test.players[turn].can_play(prev_hand[0])
    this_hand = random.choice(poss) if poss else None
    if this_hand is not None:
        test.players[turn].play(this_hand)
        prev_hand = [this_hand, turn]
        print(f'Player {turn} played: {prev_hand[0]}')
    else: 
        print(f'Player {turn} pass.')
    if sum(test.players[turn].count) == 0:
        print(f'Player {turn} wins!')
        break
    k += 1

