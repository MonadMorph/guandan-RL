from guandan_transformer import Agent
from policy import RandomAgent
from deck import FrenchDeck
import torch, os
from tqdm import trange

contrast_timestep = 200
num_games = 100

agent = Agent()
agent.policy_value_net.load_state_dict(torch.load("models/policy_value_net_150.pt"))

def evaluate(agent, contrast_agent, num_games=100):
    wins = 0
    scores = []
    pbar = trange(num_games, desc="Evaluating")

    for _ in pbar:
        test = FrenchDeck()
        test.distribute()

        k = 0 #start from player 0
        prev_hand = [None, 0]  # Placeholder for other hand, if needed
        won = []

        while True:
            turn = k%4
            if turn in won:
                k += 1
                continue
            if prev_hand[1] == turn and (prev_hand[0] is None or prev_hand[0].type != 7 or prev_hand[0].aux_rank is not None):
                prev_hand[0] = None  # Reset if it's the same player's turn, he can play anything
            if won and prev_hand[1] == won[-1] and turn == (won[-1] + 2) %4: prev_hand[0] = None
            state = test.state(turn, prev_hand)

            if turn % 2 == 0:
                this_hand, _, _, _ = agent.select_action(state)
            else:
                this_hand, _, _, _ = contrast_agent.select_action(state)     

            if prev_hand[1] == turn and prev_hand[0] is not None and this_hand: # didn't reset, must be 3 in 3+2
                prev_hand[0].aux_rank = this_hand.rank # This is a bit tricky case, while playing the 2, the model should record selection a pair, while the deck should record 3+2 as a whole
                # So we need fixing the action here, just add the new pair action to aux_rank
                this_hand = prev_hand[0] # This new action has rank 7, instead of 2.
            test.play(turn, this_hand)
            prev_hand = [this_hand, turn]

            if sum(test.players[turn].count) == 0:
                won.append(turn)
                if len(won) == 2 and won[0]%2 == won[1]%2:
                    score = 3
                    # print(f'Team of player {won[0]} and player {(won[0]+2)%4} wins with score {score}!')
                    if won[0] % 2 == 0:
                        wins += 1
                        scores.append(score)
                    else: scores.append(-score)
                    break
                if len(won) == 3:
                    if won[0]%2 == won[2]%2: score = 2
                    else: score = 1
                    # print(f'Team of player {won[0]} and player {(won[0]+2)%4} wins with score {score}!')
                    if won[0] % 2 == 0:
                        wins += 1
                        scores.append(score)
                    else: scores.append(-score)
                    break
            if this_hand and this_hand.type == 7 and this_hand.aux_rank is None: # So for 3+2, we got the 3 but not the 2. Continue without increases turn.
                continue
            k += 1

    print(f'Agent won {wins} games. Average score: {sum(scores)/num_games}')


'''for file in os.listdir("models"):
    if file.startswith("policy_value_net_") and file.endswith(".pt"):
        contrast_agent = Agent()
        contrast_agent.policy_value_net.load_state_dict(torch.load(os.path.join("models", file)))
        print(f'Evaluation completed over {num_games} games, against {file}.')
        evaluate(agent, contrast_agent, num_games)'''

contrast_agent = Agent()
contrast_agent.policy_value_net.load_state_dict(torch.load("models/policy_value_net_50.pt"))
print(f'Evaluation completed over {num_games} games, against 50.')
evaluate(agent, contrast_agent, 100)