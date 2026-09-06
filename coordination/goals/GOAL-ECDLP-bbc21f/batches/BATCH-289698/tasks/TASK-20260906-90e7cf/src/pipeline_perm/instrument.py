"""Generic keyed-random-function instrument for EXP-ECDLP-612fb1.

One code path for every arm of the frozen contract
(experiments/EXP-ECDLP-612fb1/specification.yaml, version 1). Arms are
selected by an ArmConfig; they share the walk, the precomputation pool and
the target sequence at a given seed and differ only in the bookkeeping the
contract declares.

Every cost is COUNTED (walk steps = group operations; restarts, lookups,
re-selection integer operations counted separately). Wall clock is never
read here for any decision.

Nothing in this module solves a logarithm: certificate kind is `none` for
every generic run.
"""
from __future__ import annotations

import hashlib
import math
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Frozen parameters (contract "definitions" and "standardized_parameter_sets")
# ---------------------------------------------------------------------------

T_OF_NBITS = {20: 64, 24: 256, 30: 1024}      # T = N^{1/3} rounded, as frozen
K_WALKS = 4                                   # k online walks per target
CAP_MULT = 8                                  # cap = 8W
U_MAX_MULT = 16                               # U up to 16T
FIXTURE_TRIALS = 40000                        # G2 fixture single-walk trials per seed
MASK64 = (1 << 64) - 1
# RED TEAM TASK-20260906-90e7cf, J4(i) proves-too-much object: the walk is selected by
# environment variable so that NOTHING else in the pipeline changes.
#   random_function (default) = the producer's keyed random function (unchanged)
#   permutation              = keyed random BIJECTION of [0, N) (numpy permutation seeded by the walk key K)
#   affine_xorshift          = keyed bijection x -> affine(odd m) o xorshift o affine(odd m) mod 2^n_bits
RT_WALK_KIND = os.environ.get("RT_WALK_KIND", "random_function")

_M1 = np.uint64(0xBF58476D1CE4E5B9)
_M2 = np.uint64(0x94D049BB133111EB)
_S30 = np.uint64(30)
_S27 = np.uint64(27)
_S31 = np.uint64(31)


def mix64(z: np.ndarray) -> np.ndarray:
    """splitmix64 finaliser on a uint64 array (wrapping arithmetic)."""
    z = z ^ (z >> _S30)
    z = z * _M1
    z = z ^ (z >> _S27)
    z = z * _M2
    z = z ^ (z >> _S31)
    return z


def mix64_int(z: int) -> int:
    """Python-int version of mix64 (used only to derive keys)."""
    z &= MASK64
    z ^= z >> 30
    z = (z * 0xBF58476D1CE4E5B9) & MASK64
    z ^= z >> 27
    z = (z * 0x94D049BB133111EB) & MASK64
    z ^= z >> 31
    return z


@dataclass
class Params:
    n_bits: int
    a: float
    seed: int
    k: int = K_WALKS
    N_override: Optional[int] = None   # curve arm: the (prime) group order, about 2^n_bits

    def __post_init__(self) -> None:
        self.N = self.N_override if self.N_override is not None else (1 << self.n_bits)
        self.T = T_OF_NBITS[self.n_bits]
        self.W = math.sqrt(self.a * self.N / self.T)
        self.theta = 1.0 / self.W
        self.cap = int(math.ceil(CAP_MULT * self.W))
        self.U_max = U_MAX_MULT * self.T
        self.R_default = self.T
        # walk key K from the walk-key seed s; DP key from K with a domain tag
        self.K = mix64_int(0x9E3779B97F4A7C15 + self.seed)
        self.K_dp = mix64_int(self.K ^ 0xD1B54A32D192ED03)
        self.dp_threshold = int(math.floor((1 << 64) / self.W))
        self.bits_entry = 2 * self.n_bits            # frozen bits per table entry
        self.bits_pool_entry = self.bits_entry + 48  # + 32 (S_d) + 16 (h_d)
        self.restart_cost = 1.5 * self.n_bits        # group ops per restart scalar mult
        # seed streams exactly as the contract's seed_policy
        self.seed_targets = 100 + self.seed
        self.seed_phi = 200 + self.seed
        self.seed_null_a = 300 + self.seed
        self.seed_tiebreak = 400 + self.seed
        # RED TEAM J4(i): keyed bijection in place of the random function (bijectivity verified by counting)
        self.walk_kind = RT_WALK_KIND
        if self.walk_kind == "permutation":
            self.perm = np.random.default_rng(self.K).permutation(self.N).astype(np.uint64)
            assert len(np.unique(self.perm)) == self.N, "not a bijection"
        elif self.walk_kind == "affine_xorshift":
            rng = np.random.default_rng(self.K)
            self.aff = (int(rng.integers(0, self.N)) | 1, int(rng.integers(0, self.N)),
                        int(rng.integers(0, self.N)) | 1, int(rng.integers(0, self.N)))
            img = self.step(np.arange(self.N, dtype=np.uint64))
            assert len(np.unique(img)) == self.N, "not a bijection"

    def describe(self) -> dict:
        return {
            "n_bits": self.n_bits, "N": self.N, "T": self.T, "a": self.a,
            "W": self.W, "theta": self.theta, "cap": self.cap, "k": self.k,
            "U_max": self.U_max, "R_default": self.R_default,
            "walk_key_K": self.K, "dp_key": self.K_dp, "walk_kind": self.walk_kind,
            "dp_threshold": self.dp_threshold,
            "bits_per_table_entry": self.bits_entry,
            "bits_per_pool_entry": self.bits_pool_entry,
            "restart_scalar_mult_group_ops": self.restart_cost,
            "seeds": {
                "walk_key_seed": self.seed,
                "precomputation_restart_stream": self.seed,
                "target_seed": self.seed_targets,
                "phi_bernoulli_stream": self.seed_phi,
                "null_a_relabelling_stream": self.seed_null_a,
                "tiebreak_permutation_stream": self.seed_tiebreak,
            },
        }

    # -- the walk ----------------------------------------------------------
    def step(self, x: np.ndarray) -> np.ndarray:
        """f(x) = mix64(x XOR K) mod N on a uint64 array (producer's walk), or the
        RED TEAM J4(i) keyed bijection when RT_WALK_KIND is set."""
        if self.walk_kind == "permutation":
            return self.perm[x.astype(np.int64)]
        if self.walk_kind == "affine_xorshift":
            m1, c1, m2, c2 = self.aff
            mask = np.uint64(self.N - 1)
            y = (x * np.uint64(m1) + np.uint64(c1)) & mask
            y = y ^ (y >> np.uint64(9))
            y = (y ^ (y << np.uint64(5))) & mask
            y = (y * np.uint64(m2) + np.uint64(c2)) & mask
            return y
        return mix64(x ^ np.uint64(self.K)) & np.uint64(self.N - 1)

    def is_dp(self, x: np.ndarray) -> np.ndarray:
        return mix64(x ^ np.uint64(self.K_dp)) < np.uint64(self.dp_threshold)


# ---------------------------------------------------------------------------
# Vectorised walker (the online instrument at every N)
# ---------------------------------------------------------------------------

def walk_to_dp(P: Params, starts: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Walk every start to its first DP or the cap.

    Returns (terminal, length): terminal = DP value, or -1 if capped;
    length = number of walk steps (group operations), = cap when capped.
    """
    n = len(starts)
    x = np.asarray(starts, dtype=np.uint64).copy()
    term = np.full(n, -1, dtype=np.int64)
    length = np.zeros(n, dtype=np.int64)
    active = np.arange(n)
    dp = P.is_dp(x[active])
    term[active[dp]] = x[active[dp]].astype(np.int64)
    active = active[~dp]
    steps = 0
    while active.size and steps < P.cap:
        xa = P.step(x[active])
        x[active] = xa
        steps += 1
        dp = P.is_dp(xa)
        hit = active[dp]
        term[hit] = xa[dp].astype(np.int64)
        length[hit] = steps
        active = active[~dp]
    length[active] = P.cap          # capped walks charged at the cap
    return term, length


# ---------------------------------------------------------------------------
# Exact basins by pointer jumping (N <= 2^24)
# ---------------------------------------------------------------------------

@dataclass
class Basins:
    dps: np.ndarray            # sorted DP values (int64)
    size: np.ndarray           # exact basin size of each DP (int64), cap 8W
    first_dp: np.ndarray       # for every x: first DP reached (int32), valid where reach
    dist: np.ndarray           # for every x: distance to first DP (int32), saturated if none
    cycle_mass: int            # points that never reach a DP (DP-free cycle and its tails)
    capped_mass: int           # points whose first DP lies beyond the cap
    N: int
    cap: int

    def index_of(self, dp_values: np.ndarray) -> np.ndarray:
        idx = np.searchsorted(self.dps, dp_values)
        idx = np.minimum(idx, len(self.dps) - 1)
        ok = self.dps[idx] == dp_values
        if not np.all(ok):
            raise ValueError("value is not a distinguished point")
        return idx

    def coverage(self, dp_values) -> float:
        """Exact single-walk hit probability of a table = sum of basins / N."""
        vals = np.asarray(list(dp_values), dtype=np.int64)
        if vals.size == 0:
            return 0.0
        return float(self.size[self.index_of(vals)].sum()) / self.N

    def top_share(self, t: int) -> float:
        srt = np.sort(self.size)[::-1]
        return float(srt[:t].sum()) / self.N

    def top_dps(self, t: int) -> np.ndarray:
        """Top-t DPs by exact basin size; ties broken by ascending DP value."""
        order = np.lexsort((self.dps, -self.size))
        return self.dps[order[:t]]


def exact_basins(P: Params) -> Basins:
    N = P.N
    x = np.arange(N, dtype=np.uint64)
    dp = P.is_dp(x)
    nxt = P.step(x).astype(np.int32)
    del x
    dps = np.flatnonzero(dp).astype(np.int64)
    nxt[dp] = np.flatnonzero(dp).astype(np.int32)          # DPs absorb
    dist = (~dp).astype(np.int32)                          # 0 at DPs, else 1
    del dp
    for _ in range(P.n_bits):                              # 2^n_bits > N - 1
        dist = dist + dist[nxt]
        nxt = nxt[nxt]
    sat = np.int32(1 << P.n_bits)
    reach = dist < sat
    ok = reach & (dist <= P.cap)
    cycle_mass = int((~reach).sum())
    capped_mass = int((reach & ~ok).sum())
    idx = np.searchsorted(dps, nxt[ok].astype(np.int64))
    size = np.bincount(idx, minlength=len(dps)).astype(np.int64)
    return Basins(dps=dps, size=size, first_dp=nxt, dist=dist,
                  cycle_mass=cycle_mass, capped_mass=capped_mass, N=N, cap=P.cap)


def basin_lookup_walk(B: Basins, starts: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Walk outcome read from the exact tables (cross-check of the walker)."""
    d = B.dist[starts].astype(np.int64)
    ok = d <= B.cap
    term = np.where(ok, B.first_dp[starts].astype(np.int64), -1)
    length = np.where(ok, d, B.cap)
    return term, length


# ---------------------------------------------------------------------------
# Precomputation pool (Bernstein-Lange procedure, every walk charged)
# ---------------------------------------------------------------------------

@dataclass
class PoolSnapshot:
    r: int
    dps: List[int]
    S: List[float]
    h: List[int]
    walks: int                 # generation walks consumed (all charged to P)
    P_cost: int                # group operations, capped walks at the cap
    capped_walks: int
    logs: Optional[List[int]] = None   # curve arm: known logarithm per pool DP


def generate_pools(P: Params, r_list: List[int], extra_targets: Optional[List[int]] = None
                   ) -> Dict[int, PoolSnapshot]:
    """Generate walks from uniform restarts (stream = walk-key seed s) until
    r*T DISTINCT DPs exist, for each r in r_list; every generating walk is
    charged to P and credits (length, +1) to its DP.  Pools for larger r
    extend the smaller ones (same generation sequence)."""
    rng = np.random.default_rng(P.seed)
    targets = sorted(set(int(r * P.T) for r in r_list) | set(extra_targets or []))
    out: Dict[int, PoolSnapshot] = {}
    dps: List[int] = []
    S: List[float] = []
    h: List[int] = []
    index: Dict[int, int] = {}
    walks = 0
    P_cost = 0
    capped = 0
    want = 0
    batch = 4 * P.T
    while want < len(targets):
        starts = rng.integers(0, P.N, size=batch, dtype=np.int64)
        term, length = walk_to_dp(P, starts)
        for i in range(batch):
            walks += 1
            t = int(term[i])
            L = int(length[i])
            P_cost += L
            if t < 0:
                capped += 1
            else:
                j = index.get(t)
                if j is None:
                    index[t] = len(dps)
                    dps.append(t)
                    S.append(float(L))
                    h.append(1)
                else:
                    S[j] += L
                    h[j] += 1
            while want < len(targets) and len(dps) == targets[want]:
                out[targets[want]] = PoolSnapshot(
                    r=targets[want] // P.T if targets[want] % P.T == 0 else -1,
                    dps=list(dps), S=list(S), h=list(h), walks=walks,
                    P_cost=P_cost, capped_walks=capped)
                want += 1
            if want >= len(targets):
                break
    return out


# ---------------------------------------------------------------------------
# Counted top-T_sel selection (published weight S_d + 4 W h_d, ties by key)
# ---------------------------------------------------------------------------

class CountedSelector:
    """Streaming min-heap selection of the top-t entries by
    (weight desc, tiebreak key asc).  Every comparison and every move is
    counted as one integer operation -- the contract's re-selection cost."""

    def __init__(self) -> None:
        self.ops = 0

    def _less(self, a, b) -> bool:
        # heap order: the WORST entry (smallest weight; among equal weights
        # the largest key) sits at the root.
        self.ops += 1
        if a[0] != b[0]:
            return a[0] < b[0]
        return a[1] > b[1]

    def select(self, weights: np.ndarray, keys: np.ndarray, t: int) -> List[int]:
        n = len(weights)
        heap: List[Tuple[float, int, int]] = []
        wl = weights.tolist()
        kl = keys.tolist()
        for i in range(n):
            item = (wl[i], kl[i], i)
            if len(heap) < t:
                heap.append(item)
                self.ops += 1
                self._sift_up(heap, len(heap) - 1)
            elif self._less(heap[0], item):
                heap[0] = item
                self.ops += 1
                self._sift_down(heap, 0)
        # rank order: best first
        heap.sort(key=lambda e: (-e[0], e[1]))
        self.ops += int(len(heap) * max(1, math.log2(max(2, len(heap)))))
        return [e[2] for e in heap]

    def _sift_up(self, heap, i) -> None:
        while i > 0:
            p = (i - 1) // 2
            if self._less(heap[i], heap[p]):
                heap[i], heap[p] = heap[p], heap[i]
                self.ops += 1
                i = p
            else:
                break

    def _sift_down(self, heap, i) -> None:
        n = len(heap)
        while True:
            l = 2 * i + 1
            r = l + 1
            m = i
            if l < n and self._less(heap[l], heap[m]):
                m = l
            if r < n and self._less(heap[r], heap[m]):
                m = r
            if m == i:
                break
            heap[i], heap[m] = heap[m], heap[i]
            self.ops += 1
            i = m


def numpy_select(weights: np.ndarray, keys: np.ndarray, t: int) -> List[int]:
    """Independent (numpy) re-implementation of the same ordering, used to
    verify the counted selector every round."""
    order = np.lexsort((keys, -weights))
    return order[:t].tolist()


# ---------------------------------------------------------------------------
# Arm engine
# ---------------------------------------------------------------------------

@dataclass
class ArmConfig:
    name: str
    mode: str                  # static | resel_lower | resel_upper | null_a | null_b | phi | static2t | rho | oracle
    t_sel: int                 # entries stored (advice)
    r: int = 2                 # precomputation pool ratio
    R: Optional[int] = None    # round length in targets (default T)
    phi: float = 1.0           # PHI arms: admission probability per solved target
    pool_cap: Optional[int] = None   # CAP arms: pool entries retained after re-selection
    twin: Optional[str] = None       # STATIC twin for the round-0 identity check


@dataclass
class ArmResult:
    config: ArmConfig
    rounds: List[dict] = field(default_factory=list)
    used: np.ndarray = None            # per target: walks used
    solved: np.ndarray = None          # per target: bool
    hit_dp: np.ndarray = None          # per target: hit entry or -1
    steps: np.ndarray = None           # per target: group operations (walk steps)
    S_bits: int = 0
    S_peak_bits: int = 0
    max_pool: int = 0
    reselection_ops_total: int = 0
    selector_verified: bool = True
    pool_snapshots: Dict[int, dict] = field(default_factory=dict)  # U -> {dps, S, h}
    table_at_round: List[np.ndarray] = field(default_factory=list)
    k_found: Optional[np.ndarray] = None   # curve arm: recovered logarithm per solved target (-1 otherwise)


class Pool:
    def __init__(self, snap: PoolSnapshot, key_rng: np.random.Generator):
        self.dps: List[int] = list(snap.dps)
        self.S: List[float] = list(snap.S)
        self.h: List[int] = list(snap.h)
        self.index: Dict[int, int] = {d: i for i, d in enumerate(self.dps)}
        self.key_rng = key_rng
        self.keys: List[int] = key_rng.integers(0, 1 << 63, size=len(self.dps), dtype=np.int64).tolist()
        # curve arm only: known logarithm of every pool entry (None on the generic arm)
        self.logs: Optional[List[int]] = list(snap.logs) if getattr(snap, "logs", None) is not None else None

    def __len__(self) -> int:
        return len(self.dps)

    def add_or_credit(self, dp: int, length: float, count: int, log: Optional[int] = None) -> int:
        j = self.index.get(dp)
        if j is None:
            j = len(self.dps)
            self.index[dp] = j
            self.dps.append(dp)
            self.S.append(0.0)
            self.h.append(0)
            self.keys.append(int(self.key_rng.integers(0, 1 << 63, dtype=np.int64)))
            if self.logs is not None:
                self.logs.append(log)
        self.S[j] += length
        self.h[j] += count
        return j

    def credit_index(self, j: int, length: float, count: int) -> None:
        self.S[j] += length
        self.h[j] += count

    def weights(self, W: float) -> np.ndarray:
        return np.asarray(self.S, dtype=np.float64) + 4.0 * W * np.asarray(self.h, dtype=np.float64)

    def restrict(self, keep: List[int]) -> None:
        keep = sorted(keep)
        self.dps = [self.dps[i] for i in keep]
        self.S = [self.S[i] for i in keep]
        self.h = [self.h[i] for i in keep]
        self.keys = [self.keys[i] for i in keep]
        if self.logs is not None:
            self.logs = [self.logs[i] for i in keep]
        self.index = {d: i for i, d in enumerate(self.dps)}


def table_hash(dps) -> str:
    arr = np.sort(np.asarray(list(dps), dtype=np.int64))
    return hashlib.sha256(arr.tobytes()).hexdigest()[:16]


def run_arm(P: Params, cfg: ArmConfig, pools: Dict[int, PoolSnapshot],
            term: np.ndarray, length: np.ndarray, basins: Optional[Basins],
            oracle_share: Optional[Dict[int, float]] = None,
            snapshot_U: Optional[List[int]] = None,
            walk_scalar: Optional[np.ndarray] = None, group_order: Optional[int] = None) -> ArmResult:
    """Process U_max targets in rounds of R under the arm's rule.

    term, length: (U_max, k) walk outcomes shared by every arm.
    walk_scalar (curve arm only): (U_max, k) accumulated scalar c + s of each
    walk, so that a hit on a table entry d with known log gives
    k_u = log(d) - (c + s) mod N and a solved target's other walks enter the
    pool with log = k_u + (c' + s').  None on the generic arm.
    """
    U = term.shape[0]
    k = term.shape[1]
    curve = walk_scalar is not None
    R = cfg.R or P.R_default
    res = ArmResult(config=cfg)
    res.used = np.zeros(U, dtype=np.int64)
    res.solved = np.zeros(U, dtype=bool)
    res.hit_dp = np.full(U, -1, dtype=np.int64)
    res.steps = np.zeros(U, dtype=np.int64)
    res.k_found = np.full(U, -1, dtype=np.int64) if curve else None
    snapshot_U = set(snapshot_U or [])

    rng_keys = np.random.default_rng(P.seed_tiebreak)
    rng_phi = np.random.default_rng(P.seed_phi)
    rng_null = np.random.default_rng(P.seed_null_a)
    phi_draws = rng_phi.random(U)                 # one uniform per target, in order

    if cfg.mode == "rho":
        pool = None
        table = np.zeros(0, dtype=np.int64)
    elif cfg.mode == "oracle":
        pool = None
        table = basins.top_dps(cfg.t_sel)
    else:
        pool = Pool(pools[cfg.r * P.T], rng_keys)
        if cfg.mode == "static2t":
            table = np.asarray(pool.dps, dtype=np.int64)
        else:
            sel = CountedSelector()
            idx = sel.select(pool.weights(P.W), np.asarray(pool.keys, dtype=np.int64), cfg.t_sel)
            ref = numpy_select(pool.weights(P.W), np.asarray(pool.keys, dtype=np.int64), cfg.t_sel)
            if set(idx) != set(ref):
                res.selector_verified = False
            res.reselection_ops_total += sel.ops   # initial selection is charged too
            table = np.asarray([pool.dps[i] for i in idx], dtype=np.int64)
    reselect = cfg.mode in ("resel_lower", "resel_upper", "null_a", "phi")
    res.max_pool = len(pool) if pool is not None else 0
    res.S_bits = int(len(table) * P.bits_entry)

    n_rounds = (U + R - 1) // R
    for rnd in range(n_rounds):
        u0, u1 = rnd * R, min((rnd + 1) * R, U)
        tb = term[u0:u1]
        lb = length[u0:u1]
        table_set = set(table.tolist())
        if len(table):
            hit = np.isin(tb, table)
        else:
            hit = np.zeros_like(tb, dtype=bool)
        if cfg.mode == "rho":
            # a hit = collision among the target's own walks (two walks, one DP)
            hit = np.zeros_like(tb, dtype=bool)
            for i in range(tb.shape[0]):
                seen = set()
                for j in range(k):
                    t = int(tb[i, j])
                    if t < 0:
                        continue
                    if t in seen:
                        hit[i, j] = True
                        break
                    seen.add(t)
        anyhit = hit.any(axis=1)
        first = np.where(anyhit, hit.argmax(axis=1), k - 1)
        used = np.where(anyhit, first + 1, k)
        cols = np.arange(k)[None, :]
        usedmask = cols < used[:, None]
        steps = (lb * usedmask).sum(axis=1)
        capped_used = int(((tb < 0) & usedmask).sum())
        lookups = int(((tb >= 0) & usedmask).sum())
        hit_dp = np.where(anyhit, tb[np.arange(tb.shape[0]), first], -1)

        res.used[u0:u1] = used
        res.solved[u0:u1] = anyhit
        res.hit_dp[u0:u1] = hit_dp
        res.steps[u0:u1] = steps
        if curve and pool is not None and cfg.mode not in ("rho", "oracle"):
            # logarithm recovery: table entry d has known log; walk (u, j*) started
            # at Q_u + [c]P and accumulated s, so Q_u = [log(d) - c - s] P
            for i in np.flatnonzero(anyhit):
                d = int(hit_dp[i])
                cs = int(walk_scalar[u0 + i, first[i]])
                res.k_found[u0 + i] = (pool.logs[pool.index[d]] - cs) % group_order

        walks_in_round = int(used.sum())
        hits_in_round = int(anyhit.sum())
        rec = {
            "round": rnd, "u0": int(u0), "u1": int(u1), "targets": int(u1 - u0),
            "solved": hits_in_round, "walks": walks_in_round,
            "hits": hits_in_round,
            "hit_rate": hits_in_round / walks_in_round if walks_in_round else None,
            "group_ops": int(steps.sum()),
            "restarts": walks_in_round,
            "restart_group_ops": walks_in_round * P.restart_cost,
            "lookups": lookups,
            "capped_walks_used": capped_used,
            "table_size": int(len(table)),
            "table_hash": table_hash(table),
            "pool_size": len(pool) if pool is not None else 0,
            "S_bits": int(len(table) * P.bits_entry),
        }
        if basins is not None and len(table):
            cov = basins.coverage(table)
            rec["exact_coverage"] = cov
            if oracle_share is not None and len(table) in oracle_share:
                rec["oracle_share"] = oracle_share[len(table)]
                rec["exact_exceeds_oracle"] = bool(cov > oracle_share[len(table)] + 1e-12)
        res.table_at_round.append(table.copy())

        # ---- evidence bookkeeping (round end) -------------------------------
        resel_ops = 0
        if pool is not None and cfg.mode not in ("static", "static2t"):
            pool_size_at_start = len(pool)
            for i in range(tb.shape[0]):
                u = u0 + i
                solved = bool(anyhit[i])
                nu = int(used[i])
                admit = True
                if cfg.mode == "phi":
                    admit = bool(phi_draws[u] < cfg.phi)
                if cfg.mode == "resel_upper":
                    walks_to_enter = range(nu)
                elif solved and admit:
                    walks_to_enter = range(nu)
                else:
                    walks_to_enter = range(0)
                for j in walks_to_enter:
                    t = int(tb[i, j])
                    if t < 0:
                        continue                      # capped walk: no DP
                    L = float(lb[i, j])
                    is_hit = bool(hit[i, j])
                    new_log = None
                    if curve and solved:
                        # log of this walk's terminal DP = k_u + (c' + s')
                        new_log = (int(res.k_found[u]) + int(walk_scalar[u, j])) % group_order
                    if cfg.mode == "null_a":
                        # every evidence increment goes to a uniformly random
                        # EXISTING pool entry; a new DP enters with zero evidence
                        target_j = int(rng_null.integers(0, pool_size_at_start))
                        pool.credit_index(target_j, L, 1)
                        if not is_hit and t not in pool.index:
                            pool.add_or_credit(t, 0.0, 0, log=new_log)
                    else:
                        pool.add_or_credit(t, L, 1, log=new_log)
            res.max_pool = max(res.max_pool, len(pool))
            if reselect:
                sel = CountedSelector()
                w = pool.weights(P.W)
                keys = np.asarray(pool.keys, dtype=np.int64)
                idx = sel.select(w, keys, cfg.t_sel)
                ref = numpy_select(w, keys, cfg.t_sel)
                if set(idx) != set(ref):
                    res.selector_verified = False
                resel_ops = sel.ops
                res.reselection_ops_total += resel_ops
                table = np.asarray([pool.dps[i] for i in idx], dtype=np.int64)
                if cfg.pool_cap is not None and len(pool) > cfg.pool_cap:
                    order = numpy_select(w, keys, cfg.pool_cap)
                    pool.restrict(order)
            if (u1 in snapshot_U) and cfg.mode == "resel_lower":
                res.pool_snapshots[u1] = {"dps": list(pool.dps), "S": list(pool.S), "h": list(pool.h)}
        rec["reselection_int_ops"] = resel_ops
        rec["reselection_ops_over_group_ops"] = (resel_ops / rec["group_ops"]) if rec["group_ops"] else None
        rec["pool_size_after"] = len(pool) if pool is not None else 0
        res.rounds.append(rec)
    res.S_peak_bits = int(res.max_pool * P.bits_pool_entry)
    return res


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------

def wilson(successes: int, n: int, z: float = 1.959964) -> Tuple[float, float, float]:
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = successes / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (p, centre - half, centre + half)


def c_max(a: float) -> Tuple[float, float]:
    """MODEL (IDEA-20260906-aed829 (B2)): C_max(a) = erfc(sqrt(x*/2)) where
    2 x^{-1/2} e^{-x/2} - sqrt(2 pi) erfc(sqrt(x/2)) = a sqrt(2 pi)."""
    s2p = math.sqrt(2 * math.pi)

    def g(x: float) -> float:
        return 2 * x ** -0.5 * math.exp(-x / 2) - s2p * math.erfc(math.sqrt(x / 2)) - a * s2p

    lo, hi = 1e-6, 50.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if g(mid) > 0:
            lo = mid
        else:
            hi = mid
    x = 0.5 * (lo + hi)
    return x, math.erfc(math.sqrt(x / 2))


def borel_logpmf(n: np.ndarray, mu: float) -> np.ndarray:
    n = np.asarray(n, dtype=np.float64)
    lg = np.array([math.lgamma(v + 1) for v in n])
    return -mu * n + (n - 1) * np.log(mu * n) - lg


def borel_max_band(mu: float, m: int, n_max: int, lo: float = 0.005, hi: float = 0.995) -> Tuple[int, int]:
    """99% band of the maximum of m iid Borel(mu) samples (order statistic)."""
    n = np.arange(1, n_max + 1, dtype=np.float64)
    lg = np.cumsum(np.log(n))                       # lgamma(n+1)
    logp = -mu * n + (n - 1) * np.log(mu * n) - lg
    p = np.exp(logp)
    cdf = np.cumsum(p)
    cdf = np.minimum(cdf, 1.0)
    logF = m * np.log(np.maximum(cdf, 1e-300))
    Fm = np.exp(logF)
    q_lo = int(np.searchsorted(Fm, lo) + 1)
    q_hi = int(np.searchsorted(Fm, hi) + 1)
    return q_lo, q_hi


def survival_slope(sizes: np.ndarray, n_lo: int, n_hi: int, grid: str = "log",
                   ref_survival: Optional[np.ndarray] = None) -> Tuple[float, int]:
    """Least-squares log-log slope of the basin-size survival S(n) = P(size >= n)
    on n_lo <= n <= n_hi.  grid = "log": 60 log-spaced integers (equal weight
    per decade; the declared primary estimator); grid = "int": every integer
    (weighted toward the top of the range).  If ref_survival (S(n) for
    n = 1, 2, ...) is given, the same estimator is applied to that reference
    law instead of the data (model-reference value under the same estimator)."""
    if grid == "log":
        ns = np.unique(np.round(np.exp(np.linspace(math.log(n_lo), math.log(n_hi), 60))).astype(int))
    else:
        ns = np.arange(n_lo, n_hi + 1)
    if ref_survival is not None:
        surv = ref_survival[ns - 1]
    else:
        sizes = np.asarray(sizes)
        ndp = len(sizes)
        srt = np.sort(sizes)
        surv = (ndp - np.searchsorted(srt, ns, side="left")) / ndp
    ok = surv > 0
    x = np.log(ns[ok])
    y = np.log(surv[ok])
    slope = float(np.polyfit(x, y, 1)[0])
    return slope, int(ok.sum())


def borel_survival(mu: float, n_max: int) -> np.ndarray:
    """S(n) = P(X >= n) for X ~ Borel(mu), n = 1..n_max (exact law)."""
    n = np.arange(1, n_max + 1, dtype=np.float64)
    lg = np.cumsum(np.log(n))
    p = np.exp(-mu * n + (n - 1) * np.log(mu * n) - lg)
    return np.maximum(1.0 - np.cumsum(p) + p, 1e-300)


def fit_cutoff(sizes: np.ndarray, theta: float, n_lo: int, min_count: int = 20,
               ref_survival: Optional[np.ndarray] = None) -> dict:
    """Fit the exponential cutoff n_c of the basin-size law on the tail
    n >= n_lo: least squares of log S(n)/S(n_lo) on a 40-point log grid
    against the exact Borel(mu) survival ratio with mu = 1 - sqrt(2/n_c),
    over a 120-point log grid of n_c in [W^2/16, 64 W^2].  The tail sums are
    computed as 1 - CDF so nothing is truncated.  With ref_survival the
    estimator is applied to that reference law (model-reference value)."""
    sizes = np.asarray(sizes)
    ndp = len(sizes)
    srt = np.sort(sizes)
    n_hi = int(srt[-min_count]) if ndp >= min_count else int(srt[-1])
    if n_hi <= n_lo * 1.5:
        return {"n_c": None, "n_c_theta2_over_2": None, "note": "tail too short"}
    grid_n = np.unique(np.round(np.exp(np.linspace(math.log(n_lo), math.log(n_hi), 40))).astype(int))
    if ref_survival is not None:
        surv = ref_survival[grid_n - 1]
    else:
        surv = (ndp - np.searchsorted(srt, grid_n, side="left")) / ndp
    ok = surv > 0
    grid_n = grid_n[ok]
    y = np.log(surv[ok] / surv[ok][0])
    W2 = 1.0 / theta ** 2
    best = None
    for nc in np.exp(np.linspace(math.log(W2 / 16), math.log(64 * W2), 120)):
        mu = 1.0 - math.sqrt(2.0 / nc)
        if mu <= 0 or mu >= 1:
            continue
        n_all = np.arange(1, int(n_hi) + 2, dtype=np.float64)
        lg_all = np.cumsum(np.log(n_all))
        p = np.exp(-mu * n_all + (n_all - 1) * np.log(mu * n_all) - lg_all)
        tail = np.maximum(1.0 - np.cumsum(p) + p, 1e-300)   # sum_{m >= n}: Borel(mu) has total mass 1
        model = np.log(tail[grid_n - 1] / tail[grid_n[0] - 1])
        sse = float(((model - y) ** 2).sum())
        if best is None or sse < best[0]:
            best = (sse, float(nc))
    nc = best[1]
    return {"n_c": nc, "n_c_theta2_over_2": nc * theta ** 2 / 2, "sse": best[0],
            "tail_range": [int(n_lo), int(n_hi)], "grid_points": int(len(grid_n)),
            "n_c_grid_range": [W2 / 16, 64 * W2]}
