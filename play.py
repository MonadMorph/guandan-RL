from deck import FrenchDeck
import random
from policy import select_action

test = FrenchDeck()
test.distribute()
for player in test.players:
    print(player)

def random_policy(state): #Would always play if possible
    poss = state[1]
    this_hand = random.choice(poss) if poss else None
    return this_hand

k = 0 #start from player 0
prev_hand = [None, 0]  # Placeholder for other hand, if needed
won = []

while True:
    turn = k%4
    if turn in won:
        k += 1
        continue
    if prev_hand[1] == turn: prev_hand[0] = None  # Reset if it's the same player's turn, he can play anything
    if won and prev_hand[1] == won[-1] and turn == (won[-1] + 2) %4: prev_hand[0] = None
    state = test.state(turn, prev_hand)
    print(f'State for player {turn}: {state}')
    if len(state[1]) == 0: 
        k += 1
        continue  # No possible actions

    # This part is a temporary random player for testing
    # Should be replaced by RL agent decision, from state
    #testing
    if turn == 2:
        this_hand, logprob, value = select_action(state)
    else:
        this_hand = random_policy(state)

    if this_hand is not None:
        test.play(turn, this_hand)
        prev_hand = [this_hand, turn]
        print(f'Player {turn} played: {prev_hand[0]}')
    else: 
        print(f'Player {turn} pass.')
    if sum(test.players[turn].count) == 0:
        print(f'Player {turn} is done!')
        won.append(turn)
        if len(won) == 2 and won[0]%2 == won[1]%2:
            score = 3
            print(f'Team of player {won[0]} and player {(won[0]+2)%4} wins with score {score}!')
            break
        if len(won) == 3:
            if won[0]%2 == won[2]%2: score = 2
            else: score = 1
            print(f'Team of player {won[0]} and player {(won[0]+2)%4} wins with score {score}!')
            break
    k += 1

