from ppo_algorithm import train_one_epoch
from guandan_transformer import Agent
import torch, os
from tqdm import trange
import random

learning_rate = 1e-4
epochs1 = 300
epochs2 = 500
checkpoint = 50

agent = Agent()
# agent.policy_value_net.load_state_dict(torch.load("policy_value_net.pt"))
print("Agent initialized")

os.makedirs("models", exist_ok=True)

pbar = trange(epochs1 + epochs2, desc="Training")

optimizer = torch.optim.Adam(agent.policy_value_net.parameters(), lr=learning_rate)
checkpoints = []

# First phase training
for i in pbar:
    if i >= epochs1:
        break
    loss = train_one_epoch(agent, optimizer, games_per_epoch=10)
    pbar.set_postfix(loss=float(loss))

    if i % checkpoint == 0 and i > 0:
        torch.save(agent.policy_value_net.state_dict(), f"models/policy_value_net_{i}.pt")
        checkpoints.append(f"models/policy_value_net_{i}.pt")

# Second phase training with older agent as contrast agent
for i in pbar:
    if random.random() < 0.3:
        loss = train_one_epoch(agent, optimizer, games_per_epoch=10) # without contrast agent
    else:
        contrast_agent = Agent()
        contrast_agent.policy_value_net.load_state_dict(torch.load(random.choice(checkpoints)))
        loss = train_one_epoch(agent, optimizer, games_per_epoch=10, contrast_agent=contrast_agent)

    pbar.set_postfix(loss=float(loss))

    if i % checkpoint == 0:
        torch.save(agent.policy_value_net.state_dict(), f"models/policy_value_net_{i}.pt")
        checkpoints.append(f"models/policy_value_net_{i}.pt")

torch.save(agent.policy_value_net.state_dict(), f"models/policy_value_net_final.pt")