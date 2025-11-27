import torch
import torch.nn as nn
import torch.nn.functional as F
from deck import Hand

class GuandanTransformer(nn.Module):
    def __init__(self, d_model=128, n_heads=4, n_layers=2, num_actions=120):
        super().__init__()
        self.token_dims = {
            "hand": 16,              # 15 ranks + 1 royal flush count
            "history": 16*16,        # 16 history entries, each 16 dims
            "cards_left": 5,
            "last_hand": 16,
            "player": 4,
        }
        self.num_tokens = 1 + 16 + 1 + 1 + 1   # 20 total tokens
        self.proj = nn.ModuleList([
            nn.Linear(in_features, d_model)
            for in_features in [
                16,         # hand
                *([16]*16),  # history entries
                5,          # cards_left
                16,         # last_hand
                4           # player index
            ]
        ])

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_model*4,
            batch_first=True,
            activation='gelu'
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=n_layers
        )

        self.norm = nn.LayerNorm(d_model)
        self.cls_token = nn.Parameter(torch.randn(1, 1, d_model))
        self.policy_head = nn.Linear(d_model, num_actions) #num_actions to be defined
        self.value_head = nn.Linear(d_model, 1)

    def forward(self, tokens, history_length):
        mask = torch.tensor([False]*2 + (16-history_length) * [True] + (history_length+3) * [False])
        device = self.cls_token.device
        mask = mask.unsqueeze(0).to(device)

        proj_tokens = []
        for tok, proj in zip(tokens, self.proj):
            x = torch.tensor(tok, dtype=torch.float32, device=device).unsqueeze(0)  # [1, dim]
            proj_tokens.append(proj(x))                             # [1, d_model]

        X = torch.cat(proj_tokens, dim=0).unsqueeze(0)

        cls = self.cls_token.expand(X.size(0), -1, -1)
        X = torch.cat([cls, X], dim=1)

        # Run transformer
        Y = self.transformer(X, src_key_padding_mask = ~mask)   # [B, num_tokens+1, d_model]

        # Use CLS output
        final_hidden = self.norm(Y[:, 0, :])  # [B, d_model]

        # Heads
        logits = self.policy_head(final_hidden)

        value = self.value_head(final_hidden)
        return logits, value
    
class Agent:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.policy_value_net = GuandanTransformer()
        self.policy_value_net.to(self.device)

    def encode_state(self,state):
        vecs = []
        x = [i/8.0 for i in state[0]]
        vecs.append(x)

        for _ in range(16 - len(state[2])):
            vecs.append([0]*16) #padding for history

        for i in range(len(state[2])):
            #Hand encoding, 4 for one-hotplayer, 10 for type one-hot, 1 for bomb, 1 for order of rank
            players_en = [0]*4
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
            vecs.append(players_en + type_en + [rank_en])

        #Public cards left
        x = [i/108.0 for i in state[3]]
        vecs.append(x)

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
        else: rank_en = 0
        vecs.append(players_en + type_en + [rank_en])

        #player index
        players_en = [0]*4
        players_en[state[5]] = 1
        vecs.append(players_en)

        return vecs
    
    def masking(self, state):
        legal_actions = state[1]
        ans = {1: [0]*15, 2: [0]*15, 3: [0]*13, 4: [0]*10, 5: [0]*8, 6: [0]*11, 11: [0]*13, 12: [0]*13, 13: [0]*8, 14: [0]*13}
        for action in legal_actions:
            ans[action.type][action.rank] = 1
        flat_mask = []
        for key in sorted(ans.keys()):
            flat_mask.extend(ans[key])
        flat_mask.append(1)  # for pass action
        return torch.tensor(flat_mask, dtype=torch.bool, device=self.device).unsqueeze(0)  # shape [1, num_actions]
    
    def model_output(self, state):
        state_vec = self.encode_state(state)                    # [1, 128]
        logits, value = self.policy_value_net(state_vec, len(state[2]))  # logits: [1, num_actions], value: [1, 1]
        action_mask = self.masking(state)  # [1, num_actions]
        logits = logits.masked_fill(~action_mask, -1e9)
        return logits, value

    def select_action(self, state):
        logits, value = self.model_output(state)
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