"""Stage-1 generic instrument for EXP-ECDLP-1de2ec.

Operative parameters are taken from specification.yaml `definitions` and
`instrument.generic_walk`. Curve arms are Stage 4 and are not implemented.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

import numpy as np

from .rng import MASK64, SplitMixStream, derive_u64, splitmix64

N_PILOT = 1 << 24
T_BL = 256  # frozen: round(N^{1/3}) at n=24
A_PILOT = 1.0 / 4.0
R_PILOT = 2
K_PILOT = 4
U_LADDER = (1, 512, 4096)
T0_GRID = (T_BL, T_BL // 2, 0)
EPSILON = 0.9
BITS_PER_LOG = 2 * math.ceil(math.log2(N_PILOT))
BATCH_ENTRY_BITS = BITS_PER_LOG + BITS_PER_LOG + 32
UF_NODE_BITS = 64

# definitions.W = sqrt(a N / T_BL). At the headline cell this is exactly 128.
# specification.cost_model.standardized_parameter_sets lists W=362; that
# contradicts the definition and is recorded as an observation, not used.
W = int(round(math.sqrt(A_PILOT * N_PILOT / T_BL)))
CAP = 8 * W
DP_THRESHOLD = MASK64 // W  # floor(2^64 / W)


def mix64(x: np.ndarray | int) -> np.ndarray | int:
    """splitmix64 finaliser on a 64-bit word."""
    if isinstance(x, (int, np.integer)):
        return splitmix64(int(x))
    z = (x.astype(np.uint64) + np.uint64(0x9E3779B97F4A7C15))
    z ^= z >> np.uint64(30)
    z *= np.uint64(0xBF58476D1CE4E5B9)
    z ^= z >> np.uint64(27)
    z *= np.uint64(0x94D049BB133111EB)
    z ^= z >> np.uint64(31)
    return z


def step_f(x: int, walk_key: int) -> int:
    return mix64(int(x) ^ int(walk_key)) % N_PILOT


def is_dp(x: int, dp_key: int) -> bool:
    return mix64(int(x) ^ int(dp_key)) < DP_THRESHOLD


class UnionFind:
    """Weighted union-find over target indices; solved flag lives on the root."""

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n
        self.solved = [False] * n
        self.ops = 0

    def find(self, i: int) -> int:
        self.ops += 1
        p = self.parent[i]
        if p != i:
            self.parent[i] = self.find(p)
            return self.parent[i]
        return i

    def union(self, i: int, j: int) -> int:
        ri, rj = self.find(i), self.find(j)
        if ri == rj:
            return ri
        self.ops += 1
        if self.rank[ri] < self.rank[rj]:
            ri, rj = rj, ri
        self.parent[rj] = ri
        if self.rank[ri] == self.rank[rj]:
            self.rank[ri] += 1
        self.solved[ri] = self.solved[ri] or self.solved[rj]
        return ri

    def mark_solved(self, i: int) -> None:
        r = self.find(i)
        self.solved[r] = True

    def is_solved(self, i: int) -> bool:
        return self.solved[self.find(i)]

    def component_sizes(self) -> list[int]:
        sizes: Counter[int] = Counter()
        for i in range(len(self.parent)):
            sizes[self.find(i)] += 1
        return sorted(sizes.values(), reverse=True)


def generate_pool(
    seed: int,
    *,
    r: int = R_PILOT,
) -> dict[str, Any]:
    walk_key = derive_u64(seed, 1)
    dp_key = derive_u64(seed, 2)
    starts = SplitMixStream(derive_u64(seed, 3))
    need = r * T_BL
    stats: dict[int, list[int]] = {}  # d -> [S, h]
    p_steps = 0
    walks = 0
    while len(stats) < need:
        x = starts.next_mod(N_PILOT)
        length = 0
        terminal = None
        capped = False
        while length < CAP:
            if is_dp(x, dp_key):
                terminal = x
                break
            x = step_f(x, walk_key)
            length += 1
        if terminal is None:
            capped = True
            length = CAP
        p_steps += length if not capped else CAP
        walks += 1
        if terminal is None:
            continue
        rec = stats.setdefault(terminal, [0, 0])
        rec[0] += length if length > 0 else 1
        rec[1] += 1
    return {
        "walk_key": walk_key,
        "dp_key": dp_key,
        "stats": stats,
        "P": p_steps,
        "generation_walks": walks,
        "n_distinct": len(stats),
    }


def select_table(
    stats: dict[int, list[int]],
    t0: int,
    seed: int,
) -> list[int]:
    if t0 <= 0:
        return []
    tie = SplitMixStream(derive_u64(seed, 200 + (seed % 1000)))
    keyed = []
    for d, (s_d, h_d) in stats.items():
        weight = s_d + 4 * W * h_d
        keyed.append((-weight, tie.next_u64(), d))
    keyed.sort()
    return [d for _, _, d in keyed[:t0]]


def _walk_to_dp(start: int, walk_key: int, dp_key: int) -> tuple[int | None, int, bool]:
    x = start
    length = 0
    if is_dp(x, dp_key):
        return x, 0, False
    while length < CAP:
        x = step_f(x, walk_key)
        length += 1
        if is_dp(x, dp_key):
            return x, length, False
    return None, CAP, True


def run_arm(
    *,
    seed: int,
    arm: str,
    t0: int,
    u: int,
    phi: float = 1.0,
    pool: dict[str, Any],
) -> dict[str, Any]:
    """Run one (arm, T_0, U) cell. Shared pool / walk / targets per seed."""
    arm = arm.upper()
    walk_key = pool["walk_key"]
    dp_key = pool["dp_key"]
    table = set(select_table(pool["stats"], t0, seed))
    targets = SplitMixStream(derive_u64(100 + seed, 11))
    walks_rng = SplitMixStream(derive_u64(seed, 12))
    phi_rng = SplitMixStream(derive_u64(400 + seed, 13))
    uf = UnionFind(u)
    # batch store: dp -> owner target index
    batch: dict[int, int] = {}
    store_cap = T_BL if arm == "GROW-CAP" else None
    grow = arm in {"GROW-UNCAP", "GROW-CAP", "KS"} or arm.startswith("PHI")
    null1 = arm == "NULL1"
    if arm == "BASELINE":
        grow = False
        null1 = False
    if arm == "KS":
        if t0 != 0:
            raise ValueError("KS requires T_0 = 0")
        grow = True

    records = []
    peak_entries = len(table)
    lookups = 0
    restarts = 0
    solved_immediate = 0
    upper_hits = 0
    outcome_hist: Counter[str] = Counter()
    resolution_hist: Counter[str] = Counter()
    capped_walks = 0
    online_steps = 0

    def known_dp(d: int) -> bool:
        return d in table or d in batch

    for ui in range(u):
        _ = targets.next_mod(N_PILOT)  # consume a target id token (unused on generic)
        walks_used = 0
        steps_this = 0
        outcome = None
        hit_entry = None
        time_res = "never"
        lower_now = False
        upper_now = False
        for _w in range(K_PILOT):
            start = walks_rng.next_mod(N_PILOT)
            restarts += 1
            d, length, capped = _walk_to_dp(start, walk_key, dp_key)
            walks_used += 1
            steps_this += length
            online_steps += length
            if capped:
                capped_walks += 1
                continue
            assert d is not None
            lookups += 1
            if d in table:
                outcome = "i"
                hit_entry = d
                uf.mark_solved(ui)
                lower_now = True
                upper_now = True
                time_res = "immediately"
                break
            if d in batch:
                owner = batch[d]
                lookups += 1
                upper_now = True
                if uf.is_solved(owner):
                    outcome = "ii"
                    hit_entry = d
                    uf.mark_solved(ui)
                    lower_now = True
                    time_res = "immediately"
                    break
                # unsolved owner
                if null1 or arm == "BASELINE":
                    outcome = "iii-miss"
                    continue
                uf.union(ui, owner)
                outcome = "iii"
                hit_entry = d
                if uf.is_solved(ui):
                    lower_now = True
                    time_res = "immediately"
                break
            # new DP
            if arm == "BASELINE" or null1:
                outcome = "iv-miss"
                continue
            store = True
            if arm.startswith("PHI") or arm == "GROW-UNCAP" or arm == "GROW-CAP" or arm == "KS":
                if phi < 1.0:
                    store = (phi_rng.next_u64() / MASK64) < phi
            if store_cap is not None and store:
                if len(table) + len(batch) >= store_cap:
                    # store only if a relation can be recorded — new DP cannot
                    store = False
            if store and grow:
                batch[d] = ui
                peak_entries = max(peak_entries, len(table) + len(batch))
                outcome = "iv"
                hit_entry = d
                continue  # walk again
            outcome = "iv-drop"
        if uf.is_solved(ui):
            if time_res == "never":
                time_res = "later_in_batch"
        records.append({
            "target": ui,
            "walks_used": walks_used,
            "steps": steps_this,
            "outcome_type": outcome,
            "hit_entry": hit_entry,
            "time_of_resolution": time_res,
            "lower_at_hit": lower_now,
            "upper_at_hit": upper_now,
            "solved_end": uf.is_solved(ui),
        })
        outcome_hist[str(outcome)] += 1
        if lower_now:
            solved_immediate += 1
        if upper_now:
            upper_hits += 1

    # Propagate later resolution already done via mark_solved on unions.
    solved_end = sum(1 for rec in records if rec["solved_end"])
    for rec in records:
        if rec["solved_end"] and rec["time_of_resolution"] == "never":
            rec["time_of_resolution"] = "later_in_batch"
        resolution_hist[rec["time_of_resolution"]] += 1

    first10 = max(1, u // 10)
    solved_first10 = sum(1 for rec in records[:first10] if rec["solved_end"])
    lower_frac = solved_immediate / u
    measured_frac = solved_end / u
    upper_frac = upper_hits / u
    # UPPER diagnostic: any hit on a known DP. Recompute strictly.
    upper_strict = sum(1 for rec in records if rec["upper_at_hit"]) / u

    p_per_entry = (pool["P"] / t0) if t0 else None
    s_bits = t0 * BITS_PER_LOG
    s_peak_bits = peak_entries * BATCH_ENTRY_BITS

    return {
        "arm": arm,
        "seed": seed,
        "T_0": t0,
        "U": u,
        "phi": phi,
        "N": N_PILOT,
        "T_BL": T_BL,
        "W": W,
        "cap": CAP,
        "a": A_PILOT,
        "r": R_PILOT,
        "k": K_PILOT,
        "P": pool["P"],
        "P_per_entry": p_per_entry,
        "solved_fraction": measured_frac,
        "solved_fraction_first10": solved_first10 / first10,
        "LOWER": lower_frac,
        "UPPER": upper_strict,
        "deferred_resolution_loss": upper_strict - measured_frac,
        "S_bits": s_bits,
        "S_peak_bits": s_peak_bits,
        "S_peak_entries": peak_entries,
        "table_size": len(table),
        "batch_size": len(batch),
        "online_steps": online_steps,
        "restarts": restarts,
        "lookups": lookups,
        "union_find_ops": uf.ops,
        "capped_walks": capped_walks,
        "outcome_histogram": dict(outcome_hist),
        "resolution_histogram": dict(resolution_hist),
        "component_sizes": uf.component_sizes()[:32],
        "n_components": len(uf.component_sizes()),
        "certificate": {"kind": "none", "verified": None, "verifier": None},
        "records": records,
        "exceeds_upper": measured_frac > upper_strict + 1e-15,
    }


def exact_basins(pool: dict[str, Any]) -> dict[str, Any]:
    """Memoized exact basins of the generic walk. O(N) mixer applications."""
    walk_key = np.uint64(pool["walk_key"])
    dp_key = np.uint64(pool["dp_key"])
    n = N_PILOT
    xs = np.arange(n, dtype=np.uint64)
    dp_hash = mix64(xs ^ dp_key)
    isdp = dp_hash < np.uint64(DP_THRESHOLD)
    nxt = mix64(xs ^ walk_key) % np.uint64(n)
    terminal = np.full(n, -1, dtype=np.int32)
    terminal[isdp] = xs[isdp].astype(np.int32)
    # Iterate pointer-following up to CAP; remaining are cycle/capped.
    cur = xs.copy()
    alive = ~isdp
    for _ in range(CAP):
        if not bool(alive.any()):
            break
        cur[alive] = nxt[cur[alive]]
        hit = isdp[cur]
        newly = alive & hit
        terminal[newly] = cur[newly].astype(np.int32)
        alive &= ~hit
    cycle_mass = int(alive.sum())
    # Basin sizes for terminals (DPs only).
    valid = terminal >= 0
    dps, counts = np.unique(terminal[valid], return_counts=True)
    hist = {int(d): int(c) for d, c in zip(dps, counts)}
    capped_mass = 0  # walks that hit cap without DP or cycle; folded into alive leftover
    return {
        "n_points": n,
        "n_dp_terminals": int(isdp.sum()),
        "cycle_or_capped_mass": cycle_mass,
        "capped_mass_note": "alive after CAP hops with no DP; includes cycles without a DP",
        "capped_mass": capped_mass,
        "basin_histogram": hist,
        "sum_basin": int(counts.sum()) if len(counts) else 0,
        "max_basin": int(counts.max()) if len(counts) else 0,
    }
