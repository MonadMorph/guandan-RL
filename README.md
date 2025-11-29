# guandan-RL
A reinforcement learning system that plays a certain type of collaborative card game, Guandan.

The project is mainly for me you learn the basics of RL and getting my hands dirty. Still feel free to use it if you find that project interesting.

Currently my idea is to use proximal policy gradient for RL algorithm. The policy net first encode the state (more precisely observation, each agent cannot see others' card), then give a valid action. The state consisst of 16 historical hands, the player's current hand, and the cards remaining for everyone. Action masking is used to make sure output is legal by game rule. An state valuation is also produced from the same net, per PPO standard. However, I am not using GAE for advantage estimation, just a simple MC method, since individual trajectory won't get too long. Still, the model should also output a value head besides its action head, to decrease MC variance.

I used Transformer as model backbone. The states are encoded as 20 tokens. I added attention masking as padding for history hands, while we not yet as full history. The model itself consists of 2 transformer layers each with 4 heads. It only has around 450k params, and could run in ms on every computer.

Train with `python ppo_train.py` and evaluate with `python evaluate.py`. Currently I only played it with random policy, and it would beat random for 95% the times and with high score.
