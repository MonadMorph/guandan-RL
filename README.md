# guandan-RL
A reinforcement learning system that plays a certain type of collaborative card game, Guandan.

The project is mainly for me you learn the basics of RL and getting my hands dirty. Still feel free to use it if you find that project interesting.

Currently my idea is to use proximal policy gradient for RL algorithm. The policy net first encode the state (more precisely observation, each agent cannot see others' card), then give a valid action. The state consisst of 16 historical hands, the player's current hand, and the cards remaining for everyone. Action masking is used to make sure output is legal by game rule. An state valuation is also produced from the same net, per PPO standard. However, I am not using GAE for advantage estimation, just a simple MC method, since individual trajectory won't get too long. Still, the model should also output a value head besides its action head, to decrease MC variance. I did a bit of reward shaping, where the step level reward is final reward - small penalty from remaining cards, to encourage agent deplete their deck.

I used Transformer as model backbone. The states are encoded as 20 tokens. I added attention masking as padding for history hands, while we not yet as full history. The model itself consists of 2 transformer layers each with 4 heads. It only has around 450k params, and could run in ms on every computer.

Train with `python training.py` and evaluate with `python evaluate.py`. These are my results of training the agent for 500 epoches, and playing against agents at different epoches:

| Epoch | Win Rate (%) | Avg Score |
| ----- | ------------ | --------- |
| 0     | 98           | 2.70      |
| 99    | 63           | 0.87      |
| 199   | 59           | 0.49      |
| 299   | 57           | 0.34      |
| 399   | 49           | -0.07     |

Epoch 0 is in fact the random agent.

250 + 450:

Evaluation completed over 100 games, against policy_value_net_50.pt.
Agent won 62 games. Average score: 0.55
Evaluation completed over 100 games, against policy_value_net_100.pt.
Agent won 54 games. Average score: 0.16
Evaluation completed over 100 games, against policy_value_net_150.pt.
Agent won 58 games. Average score: 0.32
Evaluation completed over 100 games, against policy_value_net_200.pt.
Agent won 57 games. Average score: 0.27
Evaluation completed over 100 games, against policy_value_net_250.pt.
Agent won 49 games. Average score: 0.07
Evaluation completed over 100 games, against policy_value_net_0.pt.
Agent won 69 games. Average score: 0.9
Evaluation completed over 100 games, against policy_value_net_300.pt.
Agent won 49 games. Average score: -0.01
Evaluation completed over 100 games, against policy_value_net_350.pt.
Agent won 52 games. Average score: 0.09
Evaluation completed over 100 games, against policy_value_net_400.pt.
Agent won 58 games. Average score: 0.25
Evaluation completed over 100 games, against policy_value_net_final.pt.
Agent won 44 games. Average score: -0.27