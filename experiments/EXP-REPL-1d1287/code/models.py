import torch
import torch.nn as nn

class MLPModel(nn.Module):
    def __init__(self, n_limbs, hidden):
        super().__init__()
        self.n_limbs = n_limbs
        in_dim = n_limbs * 16  # one-hot per hex limb
        layers = []
        d = in_dim
        for h in hidden:
            layers += [nn.Linear(d, h), nn.ReLU()]
            d = h
        layers += [nn.Linear(d, 1)]
        self.net = nn.Sequential(*layers)

    def forward(self, limbs):  # limbs: (B, n_limbs) long
        oh = torch.nn.functional.one_hot(limbs, num_classes=16).float().flatten(1)
        return self.net(oh).squeeze(-1)

class TransformerModel(nn.Module):
    def __init__(self, n_limbs, d_model, layers=1, nhead=1):
        super().__init__()
        self.embed = nn.Embedding(16, d_model)
        self.pos = nn.Parameter(torch.randn(n_limbs, d_model) * 0.02)
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=max(4, 2 * d_model),
            batch_first=True, activation="relu")
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=layers)
        self.head = nn.Linear(d_model, 1)

    def forward(self, limbs):  # (B, n_limbs) long
        x = self.embed(limbs) + self.pos.unsqueeze(0)
        x = self.encoder(x)
        x = x.mean(dim=1)
        return self.head(x).squeeze(-1)

CAPACITY_TABLE = {
    "mlp": [
        {"capacity_id": 0, "hidden": [4]},
        {"capacity_id": 1, "hidden": [32, 16]},
        {"capacity_id": 2, "hidden": [512, 128]},
    ],
    "transformer": [
        {"capacity_id": 0, "d_model": 4, "layers": 1, "nhead": 1},
        {"capacity_id": 1, "d_model": 16, "layers": 1, "nhead": 2},
        {"capacity_id": 2, "d_model": 64, "layers": 1, "nhead": 4},
    ],
}

def build_model(architecture, capacity_id, n_limbs, seed):
    torch.manual_seed(seed)
    if architecture == "mlp":
        cfg = CAPACITY_TABLE["mlp"][capacity_id]
        m = MLPModel(n_limbs, cfg["hidden"])
    elif architecture == "transformer":
        cfg = CAPACITY_TABLE["transformer"][capacity_id]
        m = TransformerModel(n_limbs, cfg["d_model"], cfg["layers"], cfg["nhead"])
    else:
        raise ValueError(architecture)
    n_params = sum(p.numel() for p in m.parameters())
    return m, n_params, cfg
