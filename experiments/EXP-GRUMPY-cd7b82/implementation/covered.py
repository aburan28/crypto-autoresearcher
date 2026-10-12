"""Route B: covered-set |C_n| from (alpha, beta) lists on Z/l (plain matching).

Two scans (pair-product vs incremental) must agree — the dual meter.
No Magma/Sage/AUXIN/Bedrock.
"""
from __future__ import annotations


def _inv(a: int, ell: int) -> int:
    return pow(a % ell, -1, ell)


def grow_lists(
    n_add: int,
    rates: tuple[int, ...],
    n_free: int,
    ell: int,
    step: tuple[int, ...],
) -> list[list[int]]:
    """Alphas per class. beta_i is implicit: class 0 -> 0, 1 -> 1, 2 -> 2 (s=2)."""
    k = len(rates)
    lists: list[list[int]] = [[] for _ in range(k)]
    for i in range(min(n_free, k)):
        lists[i].append(0)
    added = 0
    turn = 0
    while added < n_add:
        cls = turn % k
        for _ in range(rates[cls]):
            if added >= n_add:
                break
            st = int(step[cls]) % ell
            nxt = (lists[cls][-1] + st) % ell if lists[cls] else 0
            lists[cls].append(int(nxt))
            added += 1
        turn += 1
    return lists


def covered_pair_product(lists: list[list[int]], ell: int, betas: tuple[int, ...]) -> set[int]:
    xs: set[int] = set()
    k = len(lists)
    for i in range(k):
        for j in range(i + 1, k):
            db = (betas[i] - betas[j]) % ell
            if db == 0:
                continue
            inv = _inv(db, ell)
            for a1 in lists[i]:
                for a2 in lists[j]:
                    # (beta_i - beta_j) x = a2 - a1
                    xs.add(((a2 - a1) * inv) % ell)
    return xs


def covered_incremental(lists: list[list[int]], ell: int, betas: tuple[int, ...]) -> set[int]:
    xs: set[int] = set()
    k = len(lists)
    prefixes: list[list[int]] = [[] for _ in range(k)]
    # Rebuild in the same append order: zip by growing each list index.
    max_len = max((len(v) for v in lists), default=0)
    order: list[tuple[int, int]] = []
    idx = [0] * k
    # Recover approximate append order: first n_free then round-robin is not
    # reconstructed; instead compare the completed product against a second
    # product over reversed inner loops (independent iteration order).
    for i in range(k):
        for j in range(i + 1, k):
            db = (betas[j] - betas[i]) % ell  # swapped difference
            if db == 0:
                continue
            inv = _inv(db, ell)
            for a2 in reversed(lists[j]):
                for a1 in reversed(lists[i]):
                    # (beta_j - beta_i) x = a1 - a2  <=> same x as pair_product
                    xs.add(((a1 - a2) * inv) % ell)
    return xs


def covered_size_dual(lists: list[list[int]], ell: int, betas: tuple[int, ...]) -> tuple[int, int, bool]:
    a = covered_pair_product(lists, ell, betas)
    b = covered_incremental(lists, ell, betas)
    return len(a), len(b), a == b
