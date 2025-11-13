# guandan-RL
A reinforcement learning system that plays a certain type of collaborative card game, Guandan.

The project is mainly for me you learn the basics of RL and getting my hands dirty. Still feel free to use it if you find that project interesting.

Currently my idea is to use proximal policy gradient with Transformer as backbone. The policy net first encode the state (more precisely observation, each agent cannot see others' card), then give a valid action. Action masking is used to make sure output is legal by game rule. An state valuation is also produced from the same net, per PPO standard. However, I am not using GAE for advantage estimation, just a simple MC method, since individual trajectory won't get too long.