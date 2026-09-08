"""Inductive message-passing GNN (K=3, width 64) per specification.yaml's
gnn_architecture: bipartite {base, relation, target} incidence graph on
TRAINING targets only; mean aggregation; readout MLP on
(features(R), pooled context). Trained end-to-end with the hand-written
reverse-mode autodiff in autodiff.py (no torch/tensorflow available in this
environment; see autodiff.py's module docstring for that deviation).

A held-out or validation target has no incident relation node: it is scored
by its own coordinate features concatenated with the pooled global context
g = mean(final base embeddings), which is shared across all targets and is
the ONLY channel through which the trained graph can affect an unseen
target's score (matches H-RELN-10ad6b's mechanism section, "the GNN-specific
claim is exactly that this context adds nothing beyond trees on the same
per-target and base-summary features").
"""
from __future__ import annotations

import numpy as np

from autodiff import Tensor, matmul, add as tadd, relu, concat, segment_mean, gather, mse_loss, Adam


def _init_linear(rng, in_dim, out_dim, scale=None):
    if scale is None:
        scale = np.sqrt(2.0 / in_dim)
    W = Tensor(rng.normal(size=(in_dim, out_dim)) * scale)
    b = Tensor(np.zeros((1, out_dim)))
    return W, b


class GNNModel:
    def __init__(self, feat_dim: int, width: int = 64, k_rounds: int = 3, seed: int = 0):
        self.width = width
        self.k_rounds = k_rounds
        self.feat_dim = feat_dim
        rng = np.random.default_rng(seed)
        self.W_b_in, self.b_b_in = _init_linear(rng, feat_dim, width)
        self.W_t_in, self.b_t_in = _init_linear(rng, feat_dim, width)
        self.rel_layers = []
        self.base_layers = []
        self.target_layers = []
        for _ in range(k_rounds):
            self.rel_layers.append(_init_linear(rng, 2 * width, width))
            self.base_layers.append(_init_linear(rng, 2 * width, width))
            self.target_layers.append(_init_linear(rng, 2 * width, width))
        self.W_read1, self.b_read1 = _init_linear(rng, feat_dim + width, width)
        self.W_read2, self.b_read2 = _init_linear(rng, width, 1)

    def parameters(self):
        params = [self.W_b_in, self.b_b_in, self.W_t_in, self.b_t_in,
                  self.W_read1, self.b_read1, self.W_read2, self.b_read2]
        for (W, b) in self.rel_layers + self.base_layers + self.target_layers:
            params.extend([W, b])
        return params

    def _forward_graph(self, base_feat: np.ndarray, train_feat: np.ndarray, graph: dict):
        n_base = base_feat.shape[0]
        n_train = train_feat.shape[0]
        Xb = relu(tadd(matmul(Tensor(base_feat, requires_grad=False), self.W_b_in), self.b_b_in))
        Xt = relu(tadd(matmul(Tensor(train_feat, requires_grad=False), self.W_t_in), self.b_t_in))
        idx1, idx2, idx3 = graph["idx1"], graph["idx2"], graph["idx3"]
        rel_target_idx = graph["relation_target_idx"]
        R = graph["n_relations"]
        for k in range(self.k_rounds):
            if R > 0:
                b1 = gather(Xb, idx1)
                b2 = gather(Xb, idx2)
                b3 = gather(Xb, idx3)
                base_mean_data = (b1.data + b2.data + b3.data) / 3.0
                base_mean = Tensor(base_mean_data, parents=(b1, b2, b3))

                def _bm_back(g, b1=b1, b2=b2, b3=b3):
                    b1.grad += g / 3.0
                    b2.grad += g / 3.0
                    b3.grad += g / 3.0
                base_mean._backward = _bm_back

                t_of_rel = gather(Xt, rel_target_idx)
                rel_in = concat([base_mean, t_of_rel], axis=1)
                Wr, br = self.rel_layers[k]
                Xr = relu(tadd(matmul(rel_in, Wr), br))

                # scatter relation embeddings back to base nodes (each
                # relation touches 3 base slots, possibly repeated)
                rep_idx = np.concatenate([idx1, idx2, idx3])
                rep_vals_data = np.concatenate([Xr.data, Xr.data, Xr.data], axis=0)
                rep_vals = Tensor(rep_vals_data, parents=(Xr,))

                def _rep_back(g, Xr=Xr, R=R):
                    Xr.grad += g[0:R] + g[R:2 * R] + g[2 * R:3 * R]
                rep_vals._backward = _rep_back

                base_agg = segment_mean(rep_vals, rep_idx, n_base)
                target_agg = segment_mean(Xr, rel_target_idx, n_train)
            else:
                base_agg = Tensor(np.zeros((n_base, self.width)), requires_grad=False)
                target_agg = Tensor(np.zeros((n_train, self.width)), requires_grad=False)

            Wb, bb = self.base_layers[k]
            Wt, bt = self.target_layers[k]
            Xb = relu(tadd(matmul(concat([Xb, base_agg], axis=1), Wb), bb))
            Xt = relu(tadd(matmul(concat([Xt, target_agg], axis=1), Wt), bt))
        g_context = Tensor(Xb.data.mean(axis=0, keepdims=True), parents=(Xb,))

        def _g_back(gr, Xb=Xb, n_base=n_base):
            Xb.grad += np.tile(gr / n_base, (n_base, 1))
        g_context._backward = _g_back
        return Xb, Xt, g_context

    def _readout(self, feat: np.ndarray, g_context: Tensor) -> Tensor:
        n = feat.shape[0]
        g_tile_data = np.tile(g_context.data, (n, 1))
        g_tile = Tensor(g_tile_data, parents=(g_context,))

        def _back(gr, g_context=g_context, n=n):
            g_context.grad += gr.sum(axis=0, keepdims=True)
        g_tile._backward = _back
        inp = concat([Tensor(feat, requires_grad=False), g_tile], axis=1)
        h = relu(tadd(matmul(inp, self.W_read1), self.b_read1))
        out = tadd(matmul(h, self.W_read2), self.b_read2)
        return out

    def predict_with_graph(self, base_feat, train_feat, graph, query_feat: np.ndarray) -> np.ndarray:
        _, _, g_context = self._forward_graph(base_feat, train_feat, graph)
        out = self._readout(query_feat, g_context)
        return out.data.reshape(-1)


def train_gnn(base_feat, train_feat, graph, y_train, val_feat, y_val,
              width=64, k_rounds=3, lr=1e-3, epochs=100, seed=0, patience=15):
    model = GNNModel(feat_dim=train_feat.shape[1], width=width, k_rounds=k_rounds, seed=seed)
    opt = Adam(model.parameters(), lr=lr)
    best_val = np.inf
    best_epoch = -1
    best_state = None
    history = []
    for epoch in range(epochs):
        opt.zero_grad()
        Xb, Xt, g_context = model._forward_graph(base_feat, train_feat, graph)
        pred_train = model._readout(train_feat, g_context)
        loss = mse_loss(pred_train, y_train)
        loss.backward()
        opt.step()

        pred_val = model.predict_with_graph(base_feat, train_feat, graph, val_feat)
        val_mse = float(np.mean((pred_val - y_val) ** 2))
        history.append({"epoch": epoch, "train_loss": float(loss.data), "val_mse": val_mse})
        if val_mse < best_val - 1e-9:
            best_val = val_mse
            best_epoch = epoch
            best_state = [p.data.copy() for p in model.parameters()]
        elif epoch - best_epoch > patience:
            break
    if best_state is not None:
        for p, s in zip(model.parameters(), best_state):
            p.data = s
    return model, {"best_epoch": best_epoch, "best_val_mse": best_val, "n_epochs_run": len(history),
                   "history_tail": history[-5:]}


def select_and_train_gnn(base_feat, train_feat, graph, y_train, val_feat, y_val,
                          lr_grid=(1e-3, 3e-3), width=64, k_rounds=3, epochs=100, seed=0):
    best_model = None
    best_info = None
    best_val = np.inf
    best_params = None
    for lr in lr_grid:
        model, info = train_gnn(base_feat, train_feat, graph, y_train, val_feat, y_val,
                                 width=width, k_rounds=k_rounds, lr=lr, epochs=epochs, seed=seed)
        if info["best_val_mse"] < best_val:
            best_val = info["best_val_mse"]
            best_model = model
            best_info = info
            best_params = {"learning_rate": lr, "width": width, "k_rounds": k_rounds}
    return best_model, best_params, best_info
