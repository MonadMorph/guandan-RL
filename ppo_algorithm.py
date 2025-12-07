from guandan_transformer import Agent
from deck import FrenchDeck
import torch
import torch.nn.functional as F
import random

beta = 0.5  # value loss coefficient
remaining_card_penalty = 0.03
teammate_remaining_card_penalty = 0.005
PPO_clip_ratio = 0.2 # PPO clip parameter
gradient_clip_ratio = 0.5

@torch.no_grad()
def play_simulation(agent, contrast_agent = None):
    # print("Starting a game simulation")
    test = FrenchDeck()
    test.distribute()

    k = 0 #start from player 0
    prev_hand = [None, 0]  # Placeholder for other hand, if needed
    won = []
    history = []
    old_teammate = random.random() < 0.5

    while True:
        turn = k%4
        if turn in won:
            k += 1
            continue
        if prev_hand[1] == turn: prev_hand[0] = None  # Reset if it's the same player's turn, he can play anything
        if won and prev_hand[1] == won[-1] and turn == (won[-1] + 2) %4: prev_hand[0] = None
        state = test.state(turn, prev_hand)

        if contrast_agent and (turn %2 == 1 or (old_teammate and turn == 2)): # freeze contrast agent for player 1 and 3
            action, logprob, value, action_index = contrast_agent.select_action(state)
        else:
            action, logprob, value, action_index = agent.select_action(state)
            history.append((state, logprob, value, action_index)) # only store for training agent

        test.play(turn, action)
        prev_hand = [action, turn]
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

    # print(f"Game finished in {k} turns, winners: {result[0]}, {result[1]} with score {result[2]}")
    return result, history

def train_one_epoch(agent, optimizer, alpha = 0.01, games_per_epoch=4, contrast_agent = None):
    all_states, all_logprobs, all_values, all_rewards, all_aindex = [], [], [], [], []

    for _ in range(games_per_epoch):
        result, history = play_simulation(agent, contrast_agent)       # each history = [(state, logprob, value, action_index), ...]
        winners = {result[0], result[1]}
        score   = float(result[2])

        for (state, logprob, value, action_index) in history:
            reward = score if state[-1] in winners else -score

            # reward shaping based on remaining cards
            reward -= remaining_card_penalty * state[3][0] / 27  # own remaining cards
            reward -= teammate_remaining_card_penalty * state[3][2] / 27  # own remaining cards

            all_states.append(state)
            all_logprobs.append(logprob)
            all_values.append(value)
            all_rewards.append(reward)
            all_aindex.append(action_index)

    # Implement minibatch later if needed 
    actions     = torch.tensor(all_aindex, dtype=torch.long, device=agent.device).unsqueeze(1)
    old_logprob = torch.cat(all_logprobs, dim=0).detach().to(agent.device)
    old_value = torch.cat(all_values, dim=0).detach().to(agent.device)
    returns     = torch.tensor(all_rewards, dtype=torch.float32, device=agent.device).unsqueeze(1)

    batch_logits = []
    batch_values = []

    for s in all_states:
        logits, value = agent.model_output(s)     # already masked
        batch_logits.append(logits)               # logits: [1, num_actions]
        batch_values.append(value)                # value:  [1, 1]

    logits = torch.cat(batch_logits, dim=0)   # [B, num_actions]
    new_value = torch.cat(batch_values, dim=0)  # [B, 1]

    # Pure MC advantage, not using GAE for simplicity
    adv = (returns - old_value)
    adv = (adv - adv.mean()) / (adv.std() + 1e-8)
    target_value = returns
    logprobs_all = torch.log_softmax(logits, dim=-1)
    new_logprob = logprobs_all.gather(1, actions)

    # importance ratio
    ratio = (new_logprob - old_logprob).exp()
    surr1 = ratio * adv
    # clipping
    surr2 = torch.clamp(ratio, 1.0 - PPO_clip_ratio, 1.0 + PPO_clip_ratio) * adv
    policy_loss = -torch.min(surr1, surr2).mean()
    value_loss  = torch.nn.functional.mse_loss(new_value, target_value)
    entropy     = (-(logprobs_all.exp() * logprobs_all).sum(dim=1)).mean()

    loss = policy_loss + beta * value_loss - alpha * entropy

    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(agent.policy_value_net.parameters(), gradient_clip_ratio)
    optimizer.step()

    return loss.item()