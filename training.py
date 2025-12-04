from ppo_algorithm import train_one_epoch
from guandan_transformer import Agent
import torch, os
from tqdm import trange

learning_rate = 1e-4
epochs = 500
checkpoint = 20

agent = Agent()
# agent.policy_value_net.load_state_dict(torch.load("policy_value_net.pt"))
print("Agent initialized")

os.makedirs("models", exist_ok=True)

pbar = trange(epochs, desc="Training")

optimizer = torch.optim.Adam(agent.policy_value_net.parameters(), lr=learning_rate)
for i in pbar:
    loss = train_one_epoch(agent, optimizer, games_per_epoch=4)
    pbar.set_postfix(loss=float(loss))

    if i % checkpoint == 0:
        torch.save(agent.policy_value_net.state_dict(), f"models/policy_value_net_{i}.pt")

torch.save(agent.policy_value_net.state_dict(), f"models/policy_value_net_final.pt")