"""Gradient-boosted-tree baseline (source/model_trees.py), the
non_graph_tree_baseline control. No xgboost/lightgbm/sklearn is installed in
this environment (checked at executor start); this is a from-scratch CART
regression tree plus a simple gradient-boosting ensemble on squared-error
loss, using EXACTLY the same features and splits protocol as the GNN
(features.py) and the frozen grid: depth in {4,6}, trees in {200,500},
learning_rate 0.05, selected on the validation split only. Recorded as a
protocol deviation (custom implementation, not a named library) in
implementation.md and the execution report.
"""
from __future__ import annotations

import numpy as np


class _Node:
    __slots__ = ("feature", "threshold", "left", "right", "value", "is_leaf")

    def __init__(self):
        self.is_leaf = True
        self.value = 0.0
        self.feature = None
        self.threshold = None
        self.left = None
        self.right = None


def _best_split(X, residual, feature_subset, min_leaf=5):
    """Exact split search via sort + cumulative-sum SSE (O(n log n) per
    feature per node), replacing an earlier quantile-candidate version that
    was too slow at this dataset size for the executor's time budget --
    recorded as a performance-only refactor, not a protocol change (same
    CART objective, exact rather than 9-quantile-approximate)."""
    best = None  # (sse_reduction, feature, threshold)
    n = len(residual)
    if n < 2 * min_leaf:
        return None
    total = residual.sum()
    total_sq = np.sum(residual ** 2)
    for f in feature_subset:
        col = X[:, f]
        order = np.argsort(col, kind="mergesort")
        col_sorted = col[order]
        res_sorted = residual[order]
        cs = np.cumsum(res_sorted)
        cs2 = np.cumsum(res_sorted ** 2)
        k = np.arange(1, n)  # split after position k (1..n-1), left size k
        valid = (k >= min_leaf) & ((n - k) >= min_leaf)
        # also require an actual value change at the boundary (no split
        # inside a run of identical feature values)
        distinct = col_sorted[1:] != col_sorted[:-1]
        valid = valid & distinct
        if not np.any(valid):
            continue
        sl = cs[k - 1]
        sl2 = cs2[k - 1]
        sr = total - sl
        sr2 = total_sq - sl2
        sse_left = sl2 - (sl ** 2) / k
        sse_right = sr2 - (sr ** 2) / (n - k)
        sse = sse_left + sse_right
        sse[~valid] = np.inf
        best_k_local = np.argmin(sse)
        if not valid[best_k_local]:
            continue
        reduction = (total_sq - total ** 2 / n) - sse[best_k_local]
        if best is None or reduction > best[0]:
            kk = best_k_local + 1  # split after position kk in sorted order
            t = float(col_sorted[kk - 1])
            best = (float(reduction), f, t)
    return best


def _build_tree(X, residual, depth, max_depth, min_leaf=5):
    node = _Node()
    if depth >= max_depth or len(residual) < 2 * min_leaf:
        node.value = float(residual.mean()) if len(residual) else 0.0
        return node
    n_features = X.shape[1]
    feature_subset = list(range(n_features))
    best = _best_split(X, residual, feature_subset, min_leaf)
    if best is None or best[0] <= 1e-12:
        node.value = float(residual.mean())
        return node
    _, f, t = best
    left_mask = X[:, f] <= t
    node.is_leaf = False
    node.feature = f
    node.threshold = float(t)
    node.left = _build_tree(X[left_mask], residual[left_mask], depth + 1, max_depth, min_leaf)
    node.right = _build_tree(X[~left_mask], residual[~left_mask], depth + 1, max_depth, min_leaf)
    return node


def _predict_tree(node, X):
    out = np.zeros(X.shape[0])
    def rec(node, idx):
        if node.is_leaf or len(idx) == 0:
            out[idx] = node.value
            return
        col = X[idx, node.feature]
        left_idx = idx[col <= node.threshold]
        right_idx = idx[col > node.threshold]
        rec(node.left, left_idx)
        rec(node.right, right_idx)
    rec(node, np.arange(X.shape[0]))
    return out


class GradientBoostedTrees:
    def __init__(self, max_depth=4, n_trees=200, learning_rate=0.05, min_leaf=5):
        self.max_depth = max_depth
        self.n_trees = n_trees
        self.learning_rate = learning_rate
        self.min_leaf = min_leaf
        self.trees = []
        self.init_value = 0.0

    def fit(self, X, y, X_val=None, y_val=None, early_stopping_rounds=15):
        self.init_value = float(y.mean())
        pred = np.full(len(y), self.init_value)
        pred_val = np.full(len(y_val), self.init_value) if X_val is not None else None
        best_val = np.inf
        best_n_trees = 0
        self.trees = []
        for i in range(self.n_trees):
            residual = y - pred
            tree = _build_tree(X, residual, depth=0, max_depth=self.max_depth, min_leaf=self.min_leaf)
            self.trees.append(tree)
            pred = pred + self.learning_rate * _predict_tree(tree, X)
            if X_val is not None:
                pred_val = pred_val + self.learning_rate * _predict_tree(tree, X_val)
                val_mse = float(np.mean((pred_val - y_val) ** 2))
                if val_mse < best_val - 1e-9:
                    best_val = val_mse
                    best_n_trees = i + 1
                elif i + 1 - best_n_trees > early_stopping_rounds:
                    break
        if X_val is not None and best_n_trees > 0:
            self.trees = self.trees[:best_n_trees]
        return self

    def predict(self, X):
        pred = np.full(X.shape[0], self.init_value)
        for tree in self.trees:
            pred = pred + self.learning_rate * _predict_tree(tree, X)
        return pred


def select_and_fit(X_train, y_train, X_val, y_val, grid_depth=(4, 6), grid_trees=(200, 500), lr=0.05):
    """Frozen hyperparameter-selection protocol: grid search on validation
    split only, matched to the GNN's selection protocol."""
    best_model = None
    best_val_mse = np.inf
    best_params = None
    for depth in grid_depth:
        for n_trees in grid_trees:
            model = GradientBoostedTrees(max_depth=depth, n_trees=n_trees, learning_rate=lr)
            model.fit(X_train, y_train, X_val, y_val)
            pred_val = model.predict(X_val)
            val_mse = float(np.mean((pred_val - y_val) ** 2))
            if val_mse < best_val_mse:
                best_val_mse = val_mse
                best_model = model
                best_params = {"max_depth": depth, "n_trees_requested": n_trees,
                                "n_trees_used": len(model.trees), "learning_rate": lr}
    return best_model, best_params, best_val_mse
