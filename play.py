from deck import FrenchDeck
import random

test = FrenchDeck()
test.distribute()
for player in test.players:
    print(player)

def random_policy(state):
    poss = state[1]
    this_hand = random.choice(poss) if poss else None
    return this_hand

k = 0 #start from player 0
prev_hand = [None, 0]  # Placeholder for other hand, if needed
while True:
    turn = k%4
    if prev_hand[1] == turn: prev_hand[0] = None  # Reset if it's the same player's turn, he can play anything
    state = test.state(turn, prev_hand)
    print(f'State for player {turn}: {state}')

    # This part is a temporary random player for testing
    # Should be replaced by RL agent decision, from state
    this_hand = random_policy(state)

    if this_hand is not None:
        test.play(turn, this_hand)
        prev_hand = [this_hand, turn]
        print(f'Player {turn} played: {prev_hand[0]}')
    else: 
        print(f'Player {turn} pass.')
    if sum(test.players[turn].count) == 0:
        print(f'Player {turn} wins!')
        break
    k += 1

