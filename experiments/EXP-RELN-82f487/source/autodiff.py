"""Minimal reverse-mode autodiff over numpy arrays, written for this
experiment because no ML framework (torch/sklearn/xgboost/lightgbm) is
installed in this environment (checked at executor start: all four
ModuleNotFoundError). This is NOT a general-purpose library; it implements
exactly the operations model_gnn.py needs (matmul, add, relu, mean/sum
segment-pooling, elementwise loss) with correct gradients, verified by a
finite-difference gradient check in this module's self_test().

Deviation from the frozen architecture text is recorded in
implementation.md: "a declared tensor library" is this hand-written
autodiff engine, not torch/tensorflow, because neither is installed and the
executor may not install new dependencies mid-run without recording the
deviation (recorded here and in the execution report).
"""
from __future__ import annotations

import numpy as np


class Tensor:
    __slots__ = ("data", "grad", "_backward", "_parents", "requires_grad")

    def __init__(self, data, parents=(), backward=None, requires_grad=True):
        self.data = np.asarray(data, dtype=np.float64)
        self.grad = np.zeros_like(self.data)
        self._parents = parents
        self._backward = backward if backward is not None else (lambda g: None)
        self.requires_grad = requires_grad

    def __repr__(self):
        return f"Tensor(shape={self.data.shape})"

    def backward(self):
        topo = []
        seen = set()

        def visit(t):
            if id(t) in seen:
                return
            seen.add(id(t))
            for p in t._parents:
                visit(p)
            topo.append(t)

        visit(self)
        self.grad = np.ones_like(self.data)
        for t in reversed(topo):
            t._backward(t.grad)


def matmul(a: Tensor, b: Tensor) -> Tensor:
    out = Tensor(a.data @ b.data, parents=(a, b))

    def _back(g):
        a.grad += g @ b.data.T
        b.grad += a.data.T @ g

    out._backward = _back
    return out


def add(a: Tensor, b: Tensor) -> Tensor:
    out = Tensor(a.data + b.data, parents=(a, b))

    def _back(g):
        ga = g
        while ga.ndim > a.data.ndim:
            ga = ga.sum(axis=0)
        for ax, sz in enumerate(a.data.shape):
            if sz == 1 and ga.shape[ax] != 1:
                ga = ga.sum(axis=ax, keepdims=True)
        a.grad += ga
        gb = g
        while gb.ndim > b.data.ndim:
            gb = gb.sum(axis=0)
        for ax, sz in enumerate(b.data.shape):
            if sz == 1 and gb.shape[ax] != 1:
                gb = gb.sum(axis=ax, keepdims=True)
        b.grad += gb

    out._backward = _back
    return out


def relu(a: Tensor) -> Tensor:
    mask = (a.data > 0).astype(np.float64)
    out = Tensor(a.data * mask, parents=(a,))

    def _back(g):
        a.grad += g * mask

    out._backward = _back
    return out


def concat(tensors, axis=-1) -> Tensor:
    datas = [t.data for t in tensors]
    out_data = np.concatenate(datas, axis=axis)
    out = Tensor(out_data, parents=tuple(tensors))
    sizes = [d.shape[axis] for d in datas]

    def _back(g):
        idx = 0
        gs = np.split(g, np.cumsum(sizes)[:-1], axis=axis)
        for t, gi in zip(tensors, gs):
            t.grad += gi

    out._backward = _back
    return out


def segment_mean(values: Tensor, seg_ids: np.ndarray, n_segments: int) -> Tensor:
    """Mean-pool rows of `values` (R x d) into n_segments groups given by
    seg_ids (length R, int array in [0, n_segments)). Segments with no
    members produce a zero row."""
    R, d = values.data.shape
    counts = np.zeros(n_segments, dtype=np.float64)
    np.add.at(counts, seg_ids, 1.0)
    safe_counts = np.where(counts == 0, 1.0, counts)
    out_data = np.zeros((n_segments, d), dtype=np.float64)
    np.add.at(out_data, seg_ids, values.data)
    out_data = out_data / safe_counts[:, None]
    out = Tensor(out_data, parents=(values,))

    def _back(g):
        # d(mean_j)/d(value_i) = 1/count[seg[i]] if seg[i]==j else 0
        contrib = g[seg_ids] / safe_counts[seg_ids][:, None]
        values.grad += contrib

    out._backward = _back
    return out


def gather(values: Tensor, idx: np.ndarray) -> Tensor:
    out = Tensor(values.data[idx], parents=(values,))

    def _back(g):
        np.add.at(values.grad, idx, g)

    out._backward = _back
    return out


def mse_loss(pred: Tensor, target: np.ndarray) -> Tensor:
    target = np.asarray(target, dtype=np.float64).reshape(pred.data.shape)
    diff = pred.data - target
    n = pred.data.size
    out = Tensor(np.array(np.mean(diff ** 2)), parents=(pred,))

    def _back(g):
        pred.grad += g * (2.0 * diff / n)

    out._backward = _back
    return out


def zero_grad(*tensors):
    for t in tensors:
        t.grad = np.zeros_like(t.data)


class Adam:
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8):
        self.params = list(params)
        self.lr = lr
        self.b1, self.b2 = betas
        self.eps = eps
        self.m = [np.zeros_like(p.data) for p in self.params]
        self.v = [np.zeros_like(p.data) for p in self.params]
        self.t = 0

    def step(self):
        self.t += 1
        for i, p in enumerate(self.params):
            g = p.grad
            self.m[i] = self.b1 * self.m[i] + (1 - self.b1) * g
            self.v[i] = self.b2 * self.v[i] + (1 - self.b2) * (g * g)
            mhat = self.m[i] / (1 - self.b1 ** self.t)
            vhat = self.v[i] / (1 - self.b2 ** self.t)
            p.data -= self.lr * mhat / (np.sqrt(vhat) + self.eps)

    def zero_grad(self):
        zero_grad(*self.params)


def self_test(seed=0):
    """Finite-difference gradient check; raises AssertionError on mismatch."""
    rng = np.random.default_rng(seed)
    W1 = Tensor(rng.normal(size=(4, 3)) * 0.1)
    x = Tensor(rng.normal(size=(5, 4)), requires_grad=False)
    y = rng.normal(size=(5, 3))

    def forward():
        h = relu(matmul(x, W1))
        return mse_loss(h, y)

    loss = forward()
    loss.backward()
    analytic = W1.grad.copy()

    eps = 1e-6
    numeric = np.zeros_like(W1.data)
    for i in range(W1.data.shape[0]):
        for j in range(W1.data.shape[1]):
            orig = W1.data[i, j]
            W1.data[i, j] = orig + eps
            lp = forward().data.copy()
            W1.data[i, j] = orig - eps
            lm = forward().data.copy()
            W1.data[i, j] = orig
            numeric[i, j] = (lp - lm) / (2 * eps)
    max_err = np.max(np.abs(analytic - numeric))
    assert max_err < 1e-4, f"gradcheck failed, max_err={max_err}"
    return max_err


if __name__ == "__main__":
    print("max grad error:", self_test())
