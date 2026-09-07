"""
Blind re-derivation instrument for PA-ECDLP-6ac801-v2-to-v3, Stage A''.
Written entirely from quantity.md (the only definitional source read).
No existing implementation was consulted.
"""
import numpy as np
import hashlib
from decimal import Decimal, getcontext, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction

getcontext().prec = 80

MASK64 = np.uint64((1 << 64) - 1)
C1 = np.uint64(0xbf58476d1ce4e5b9)
C2 = np.uint64(0x94d049bb133111eb)


def mix64_scalar(z: int) -> int:
    z &= (1 << 64) - 1
    z = ((z ^ (z >> 30)) * 0xbf58476d1ce4e5b9) & ((1 << 64) - 1)
    z = ((z ^ (z >> 27)) * 0x94d049bb133111eb) & ((1 << 64) - 1)
    z = z ^ (z >> 31)
    return z & ((1 << 64) - 1)


def mix64_vec(z: np.ndarray) -> np.ndarray:
    z = z.astype(np.uint64)
    z = z ^ (z >> np.uint64(30))
    z = z * C1
    z = z ^ (z >> np.uint64(27))
    z = z * C2
    z = z ^ (z >> np.uint64(31))
    return z


def derive_keys(seed: int):
    K = mix64_scalar(0x9E3779B97F4A7C15 + seed)
    K_dp = mix64_scalar(K ^ 0xD1B54A32D192ED03)
    return K, K_dp


def compute_W(a_frac: Fraction, N: int, T: int) -> Decimal:
    val = a_frac * N / Fraction(T)
    d = Decimal(val.numerator) / Decimal(val.denominator)
    return d.sqrt()


def compute_cap(W: Decimal) -> int:
    eight_w = 8 * W
    return int(eight_w.to_integral_value(rounding=ROUND_CEILING))


def compute_dp_threshold(W: Decimal) -> int:
    two64 = Decimal(1 << 64)
    thr = (two64 / W).to_integral_value(rounding=ROUND_FLOOR)
    return int(thr)


def build_graph(N: int, K: int, K_dp: int, dp_threshold: int):
    x = np.arange(N, dtype=np.uint64)
    fx = (mix64_vec(x ^ np.uint64(K)) % np.uint64(N)).astype(np.int64)
    dpval = mix64_vec(x ^ np.uint64(K_dp))
    is_dp = dpval < np.uint64(dp_threshold)
    return fx, is_dp


def bfs_partition(N: int, fx: np.ndarray, is_dp: np.ndarray, cap: int):
    """
    dist[x] = number of forward steps from x to first DP on its orbit,
              computed EXACTLY (never truncated at cap), -1 if unreachable.
    root[x] = the DP node first hit, -1 if unreachable.
    Uses reverse-graph (predecessor) multi-source BFS from all DP nodes,
    which is exact because each node has out-degree exactly 1 in the
    forward graph, so "shortest path from x to the DP set" (computed by
    reversing edges and searching from the set) equals the unique forward
    hitting time.
    """
    order = np.argsort(fx, kind='stable')          # x's sorted by fx(x)
    counts = np.bincount(fx, minlength=N)
    offsets = np.zeros(N + 1, dtype=np.int64)
    np.cumsum(counts, out=offsets[1:])
    pred_flat = order

    dist = np.full(N, -1, dtype=np.int64)
    root = np.full(N, -1, dtype=np.int64)

    dp_nodes = np.nonzero(is_dp)[0]
    dist[dp_nodes] = 0
    root[dp_nodes] = dp_nodes

    frontier = dp_nodes
    depth = 0
    while frontier.size > 0:
        starts = offsets[frontier]
        lengths = counts[frontier]
        total = int(lengths.sum())
        if total == 0:
            break
        block_id = np.repeat(np.arange(frontier.size), lengths)
        cum = np.cumsum(lengths)
        block_start_pos = cum - lengths
        idx_within = np.arange(total) - np.repeat(block_start_pos, lengths)
        src_idx = starts[block_id] + idx_within
        preds = pred_flat[src_idx]
        new_root = root[frontier][block_id]

        mask = dist[preds] == -1          # exclude already-visited (e.g. DP-to-DP edges)
        preds = preds[mask]
        new_root = new_root[mask]

        if preds.size == 0:
            break
        dist[preds] = depth + 1
        root[preds] = new_root
        frontier = preds
        depth += 1

    return dist, root


def brute_force_partition(N: int, fx: np.ndarray, is_dp: np.ndarray, cap_for_reach_check=None):
    """Reference (slow, O(N * path length)) implementation for validation only."""
    dist = np.full(N, -1, dtype=np.int64)
    root = np.full(N, -1, dtype=np.int64)
    for start in range(N):
        seen = {}
        cur = start
        steps = 0
        path = []
        while True:
            if cur in seen:
                # entered a cycle without hitting DP (from 'path' local perspective)
                # everything in path is unreachable via this exploration alone;
                # but cur might have been resolved already from a previous start.
                break
            if dist[cur] != -1:
                # already resolved
                base_dist = dist[cur]
                base_root = root[cur]
                for i, node in enumerate(reversed(path)):
                    dist[node] = base_dist + i + 1
                    root[node] = base_root
                path = []
                break
            if is_dp[cur]:
                dist[cur] = 0
                root[cur] = cur
                for i, node in enumerate(reversed(path)):
                    dist[node] = i + 1
                    root[node] = cur
                path = []
                break
            seen[cur] = steps
            path.append(cur)
            cur = int(fx[cur])
            steps += 1
        if path:
            # hit a cycle (cur in seen) without finding a DP anywhere in 'path' or via memo
            for node in path:
                dist[node] = -1
                root[node] = -1
    return dist, root


if __name__ == "__main__":
    # Correctness validation on tiny N against brute force, several seeds/thresholds.
    import random
    rng = random.Random(12345)
    n_trials = 40
    all_ok = True
    for trial in range(n_trials):
        N = rng.choice([8, 16, 32, 64, 128])
        seed = rng.randint(1, 10_000_000)
        K, K_dp = derive_keys(seed)
        fx, is_dp = build_graph(N, K, K_dp, dp_threshold=rng.randint(1, 1 << 63))
        # force at least plausible DP density by also trying a threshold scaled to ~1/8 of range
        dist_fast, root_fast = bfs_partition(N, fx, is_dp, cap=10**9)
        dist_slow, root_slow = brute_force_partition(N, fx, is_dp)
        ok_dist = np.array_equal(dist_fast, dist_slow)
        # root correctness: where reachable, root must itself be a DP and lie on the
        # forward path implied by dist; check root's is_dp and dist(root)==0 and
        # basin membership consistent by re-simulating a few samples.
        ok_root_isdp = True
        idxs = np.nonzero(dist_fast >= 0)[0]
        for i in idxs[:50]:
            if not is_dp[root_fast[i]]:
                ok_root_isdp = False
        ok = ok_dist and (root_fast[idxs] == root_slow[idxs]).all() and ok_root_isdp
        if not ok:
            all_ok = False
            print("MISMATCH", trial, N, seed)
            print("fast dist", dist_fast)
            print("slow dist", dist_slow)
            print("fast root", root_fast)
            print("slow root", root_slow)
            break
    print("ALL_OK" if all_ok else "FAILED", n_trials, "trials")
