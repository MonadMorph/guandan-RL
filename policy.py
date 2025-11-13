import torch.nn as nn
import torch
import torch.nn.functional as F
from deck import Hand

def trained_policy(state):
    pass    


class HandRankEncoder(nn.Module):
    def __init__(self, d_model: int):
        super().__init__()
        self.proj = nn.Linear(168, d_model)
        self.activation = nn.ReLU()
        self.norm = nn.LayerNorm(d_model)

    def forward(self, state) -> torch.Tensor:
        x = self.encode_state(state)  # Should be 168 dim vector from 0 to 1
        x = torch.tensor(x, dtype=torch.float32).unsqueeze(0)  # shape [1, 164]
        x = self.proj(x)       # shape [B, d_model]
        x = self.activation(x)
        x = self.norm(x)
        return x
    
    #private hand, private legal actions, public history (last 8), public cards left (mine, next, ..., total), public last hand, public last player, player index
    # 15 + exclude +8*(4+10+1+1) + 5 + (4+10+1+1) +4 = 168
    def encode_state(self,state):
        vecs = []
        x = [i/8.0 for i in state[0]]
        vecs.extend(x)

        for i in range(8):
            #Hand encoding, 4 for one-hotplayer, 10 for type one-hot, 1 for bomb, 1 for order of rank
            players_en = [0]*4
            if state[2][i][0] is not None:
                players_en[state[2][i][0]] = 1
            type_en = [0]*11
            if state[2][i][1] is not None:
                type = state[2][i][1].type
                if type < 10:
                    type_en[type-1] = 1
                else: 
                    type_en[type-5] = 1
                    type_en[-1] = 1  # bomb indicator
                rank_en = 1/14 * state[2][i][1].rank
            else: rank_en = 0
            vecs.extend(players_en)
            vecs.extend(type_en)
            vecs.append(rank_en)

        #Public cards left
        x = [i/108.0 for i in state[3]]
        vecs.extend(x)

        # public last hand
        players_en = [0]*4
        if state[4][0] is not None:
            players_en[state[4][0]] = 1
        type_en = [0]*11
        if state[4][1] is not None:
            type = state[4][1].type
            if type < 10:                           
                type_en[type-1] = 1
            else: 
                type_en[type-5] = 1
                type_en[-1] = 1  # bomb indicator           
            rank_en = 1/14 * state[4][1].rank
        vecs.extend(players_en)
        vecs.extend(type_en)
        vecs.append(rank_en)

        #player index
        players_en = [0]*4
        players_en[state[5]] = 1
        vecs.extend(players_en)

        return vecs
    
#This is just a MLP now. Can be replaced by Transformer later.
#num_actions: 15+15+13+10+8+11+13+13+8+13+1 = 120 For now, the last action is pass, which is always legal.
class PolicyValueNet(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_actions):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        self.policy_head = nn.Linear(hidden_dim, num_actions) #num_actions to be defined
        self.value_head = nn.Linear(hidden_dim, 1)

    def forward(self, x, action_mask=None):
        h = self.backbone(x)
        logits = self.policy_head(h)
        if action_mask is not None:
            logits = logits.masked_fill(~action_mask, -1e9)
        value = self.value_head(h)
        return logits, value
    
class Agent:
    def __init__(self):
        self.encoder = HandRankEncoder(d_model=128)
        self.policy_value_net = PolicyValueNet(input_dim=128, hidden_dim=256, num_actions=120)

    def masking(self, state):
        legal_actions = state[1]
        ans = {1: [0]*15, 2: [0]*15, 3: [0]*13, 4: [0]*10, 5: [0]*8, 6: [0]*11, 11: [0]*13, 12: [0]*13, 13: [0]*8, 14: [0]*13}
        for action in legal_actions:
            ans[action.type][action.rank] = 1
        flat_mask = []
        for key in sorted(ans.keys()):
            flat_mask.extend(ans[key])
        flat_mask.append(1)  # for pass action
        return torch.tensor(flat_mask, dtype=torch.bool).unsqueeze(0)  # shape [1, num_actions]

    def select_action(self, state):
        state_vec = self.encoder(state)                    # [1, 128]
        action_mask = self.masking(state)                  # [1, 120], bool tensor

        logits, value = self.policy_value_net(state_vec, action_mask)

        probs = F.softmax(logits, dim=-1)

        action = torch.multinomial(probs, num_samples=1)
        logprob = torch.log(probs.gather(1, action))

        #Transform action index back to Hand
        action_index = action.item()
        if action_index == 119:  # pass action
            return None, logprob, value, action_index
        elif action_index < 15:
            hand = Hand(1, action_index)
        elif action_index < 30:
            hand = Hand(2, action_index - 15)
        elif action_index < 43:
            hand = Hand(3, action_index - 30)
        elif action_index < 53:
            hand = Hand(4, action_index - 43)
        elif action_index < 61:
            hand = Hand(5, action_index - 53)
        elif action_index < 72:
            hand = Hand(6, action_index - 61)
        elif action_index < 85:
            hand = Hand(11, action_index - 72)
        elif action_index < 98:
            hand = Hand(12, action_index - 85)
        elif action_index < 106:
            hand = Hand(13, action_index - 98)
        elif action_index < 119:
            hand = Hand(14, action_index - 106)

        return hand, logprob, value, action_index