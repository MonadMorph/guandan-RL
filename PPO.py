from policy import select_action
from deck import FrenchDeck

def play_simulation():
    print("Starting a game simulation")
    test = FrenchDeck()
    test.distribute()

    k = 0 #start from player 0
    prev_hand = [None, 0]  # Placeholder for other hand, if needed
    won = []
    history = []

    while True:
        turn = k%4
        if turn in won:
            k += 1
            continue
        if prev_hand[1] == turn: prev_hand[0] = None  # Reset if it's the same player's turn, he can play anything
        if won and prev_hand[1] == won[-1] and turn == (won[-1] + 2) %4: prev_hand[0] = None
        state = test.state(turn, prev_hand)

        this_hand, logprob, value = select_action(state)
        history.append((state, this_hand, logprob, value))

        if this_hand is not None:
            test.play(turn, this_hand)
            prev_hand = [this_hand, turn]
        if sum(test.players[turn].count) == 0:
            won.append(turn)
            if len(won) == 2 and won[0]%2 == won[1]%2:
                score = 3
                result = (won[0], (won[0]+2)%4, score)
                break
            if len(won) == 3:
                if won[0]%2 == won[2]%2: score = 2
                else: score = 1
                result = (won[0], (won[0]+2)%4, score)
                break
        k += 1

    return result, history