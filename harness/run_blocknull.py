"""EXP-INSTR-85b102: blocked-permutation replacement for NULL-C.

NEW MODULE, NEW FUNCTIONS ONLY. Nothing in `harness/exp_icinv.py`,
`harness/isogeny_class.py`, `harness/run_icinv.py` or `harness/toycurve.py` is
modified or re-implemented with different behaviour: four committed runs depend
on the current behaviour of `_targets`, `targets_uniform`, `permutation_null`,
`binomial_null_verdict`, `exact_null_verdict`, `decomposition_rate_m2`,
`decomposition_rate_m3`, `liftable_density`, `factor_base_fixed_size`,
`factor_base_window` and `two_torsion_x_count`, and this campaign has already
been bitten twice by a silently altered sampler (CORR-20260807-a05e1e,
CORR-20260807-9f83be). Those functions are IMPORTED and CALLED here, never
edited; `frozen_function_diff.txt` is the receipt.

What this module adds, and only this:

    blocking(pool, rung)                  block assignment + realized geometry
    statistic_weighted(values, labels)    SS_within / (n - K)
    statistic_unweighted(values, labels)  mean over labels with n_c >= 2 of s^2_c
    blocked_permutation_null(...)         numpy-vectorized within-block label
                                          permutation, both tails, raw counts
    closed_form_null_mean(...)            exact E[T_pi | B] from block-pooled
                                          sample variances
    sumset_m2(E, fb) / sumset_m3(E, fb)   exact |2V| and |3V| by enumeration,
                                          no targets and no sampling

plus the pools, the control objects, and the emission driver.

SCOPE. Tier TOY. p in {4001, 6007}. This is an INSTRUMENT characterisation: no
ECDLP attack, no discrete logarithm, no relation collection, no solver, no cost
or exponent claim. sota_delta is zero on every axis.

NUMERICAL DETERMINISM, stated because two of this contract's forced values
depend on it. Every statistic below is computed from the CANONICAL layout: the
values of each class are sorted ascending before any sum is taken, the class
mean is `sum / n_c`, and SS_c is accumulated over the same sorted order. The
statistic is therefore a function of the class VALUE MULTISET alone and is
bit-for-bit reproducible under any re-ordering of the curves. That is what makes
R5_PERCLASS -- where the within-block label permutation is provably the identity
-- return a null value bitwise equal to T_obs, hence p_lower exactly 1.0,
without any tolerance, short circuit or special case in the p-value counter.
T_obs itself is computed by pushing the identity permutation through the very
same vectorized code path as the null draws, so the observed value and the null
distribution never disagree by a rounding mode.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field

import numpy as np

from . import exp_icinv as ex
from . import isogeny_class as ic
from . import run_icinv as ri
from .toycurve import EllipticCurve

# --------------------------------------------------------------------------
# frozen declarations from experiments/EXP-INSTR-85b102/specification.yaml
# --------------------------------------------------------------------------

EXPERIMENT_ID = "EXP-INSTR-85b102"
DOMAIN = "EXP-INSTR-85b102/v1"
MASTER_SEED = 85102
REPRODUCTION_SEED = 20260807

MINIMUM_CLASS_SIZE = 20
FB_M2 = 40
FB_M3 = 13
N_TARGETS = 400
REPRO_WINDOW = 400                     # the committed run_icinv --window
PRIMARY_B = 10000
CONTROL_B = 1000
EFFECT_GRID = (0.0, 0.1, 0.2, 0.4, 0.8, 1.6)
CONTROL_REPLICATES = 200
NSURR_REPLICATES = 50
LEVEL = 0.05
BINOMIAL_CONF = 0.99

RUNGS = (
    "R0_FREE",
    "R1_TWIST",
    "R2_NBAND_w2",
    "R3_NBAND_w3",
    "R4_NBAND_w4",
    "R5_PERCLASS",
    "R6_TWIST_AND_NBAND_w2",
)
# The N ladder proper. R1_TWIST is declared ORTHOGONAL to it and R6 is the
# composition; neither is a rung of the ladder whose Delta_max must decay.
N_LADDER = ("R0_FREE", "R2_NBAND_w2", "R3_NBAND_w3", "R4_NBAND_w4", "R5_PERCLASS")

# How many float64 elements one vectorized permutation chunk may hold. Fixed
# constant so the RNG consumption -- and therefore every draw -- is a function
# of (B, n) and the seed alone.
CHUNK_ELEMENTS = 2_400_000


# --------------------------------------------------------------------------
# seed derivation (specification.yaml inputs.seeds.derivation_rule)
# --------------------------------------------------------------------------


def derive_seed(label: str, pool: str, rung: str, functional: str,
                d: int, r: int, master: int = MASTER_SEED) -> int:
    """Big-endian SHA-256 of the declared payload, reduced mod 2^64.

    payload = domain | L | P | Rg | F | decimal(d) | decimal(r) | decimal(master)

    A third party reproduces every draw from (L, P, Rg, F, d, r) alone.
    """
    payload = f"{DOMAIN}|{label}|{pool}|{rung}|{functional}|{d}|{r}|{master}"
    digest = hashlib.sha256(payload.encode("ascii")).digest()
    return int.from_bytes(digest, "big") % (1 << 64)


def _u_order_key(trace: int) -> int:
    """Low byte of SHA-256(domain || "|u|" || decimal(trace)).

    Declared in CTRL_POWER: it fixes the order in which the +-1 class offsets
    are handed out inside a block, so the planted effect is not a monotone
    function of N by construction.
    """
    return hashlib.sha256(f"{DOMAIN}|u|{trace}".encode("ascii")).digest()[-1]


# --------------------------------------------------------------------------
# pools
# --------------------------------------------------------------------------


@dataclass
class Pool:
    """A frozen pool: which classes, which curves, in which order.

    Built at stage S0 and never touched again. `labels[i]` is the class index
    (position in `traces`) of pooled curve i.
    """
    name: str
    p: int
    rule: str
    traces: list[int]
    recs: list = field(repr=False)
    labels: np.ndarray = field(repr=False)
    class_sizes: list[int] = field(default_factory=list)
    class_orders: list[int] = field(default_factory=list)
    dropped: list = field(default_factory=list)

    @property
    def n(self) -> int:
        return len(self.recs)

    @property
    def K(self) -> int:
        return len(self.traces)

    @property
    def curve_N(self) -> np.ndarray:
        return np.array([r.order for r in self.recs], dtype=np.int64)

    @property
    def delta_pool(self) -> int:
        o = self.class_orders
        return max(o) - min(o)


def build_pool(name: str, p: int, traces: list[int], classes: dict,
               rule: str) -> Pool:
    """Freeze a pool from an already-enumerated class dict.

    Classes below MINIMUM_CLASS_SIZE are DROPPED and the drop is recorded with
    its trace and size -- the committed code silently skipped groups of size
    < 2 and this contract removes that silence.
    """
    kept, dropped = [], []
    for t in traces:
        size = len(classes[t])
        if size < MINIMUM_CLASS_SIZE:
            dropped.append({"trace": int(t), "size": int(size),
                            "reason": f"class size {size} < {MINIMUM_CLASS_SIZE}"})
        else:
            kept.append(int(t))
    recs, labels = [], []
    for idx, t in enumerate(kept):
        for rec in classes[t]:
            recs.append(rec)
            labels.append(idx)
    return Pool(name=name, p=p, rule=rule, traces=kept, recs=recs,
                labels=np.array(labels, dtype=np.int64),
                class_sizes=[len(classes[t]) for t in kept],
                class_orders=[classes[t][0].order for t in kept],
                dropped=dropped)


def poolc_traces(p: int, classes: dict, n_traces: int = 12) -> tuple[list[int], list[int]]:
    """POOL_C: twelve ordinary traces drawn uniformly WITHOUT replacement from
    every ordinary trace with class size >= MINIMUM_CLASS_SIZE.

    Selection control for pick_classes, which selects the LARGEST ordinary
    classes; class size is the weighted class number of D = t^2 - 4p and so is
    correlated with the arithmetic of D. Returns (drawn traces, eligible pool).
    """
    eligible = sorted(t for t, v in classes.items()
                      if t % p != 0 and len(v) >= MINIMUM_CLASS_SIZE)
    seed = derive_seed("POOLC", "POOL_C", "NONE", "NONE", 0, 0)
    rng = np.random.default_rng(seed)
    drawn = rng.choice(np.array(eligible, dtype=np.int64), size=n_traces,
                       replace=False)
    return [int(t) for t in drawn], eligible


# --------------------------------------------------------------------------
# blocking ladder
# --------------------------------------------------------------------------


def band_widths(delta_pool: int) -> dict[str, int]:
    """w2 = max(2, ceil(D/2)), w3 = max(2, ceil(D/8)), w4 = max(2, ceil(D/32))."""
    return {
        "R2_NBAND_w2": max(2, -(-delta_pool // 2)),
        "R3_NBAND_w3": max(2, -(-delta_pool // 8)),
        "R4_NBAND_w4": max(2, -(-delta_pool // 32)),
    }


def blocking(pool: Pool, rung: str) -> tuple[dict[int, int], dict]:
    """Block assignment for one rung, plus its realized geometry.

    Returns (assignment, realized) where assignment maps CURVE INDEX -> block id
    and realized carries n_blocks, delta_max_N, blocks_with_ge_2_classes,
    blocks_with_ge_3_classes, degenerate, the band width used and the block
    composition by trace.

    EVERY declared blocking is a COARSENING OF THE CLASS PARTITION: the key is a
    function of the class (through its trace), so each block is a union of whole
    classes. That is what makes the permutation block-separable, preserves the
    group-size multiset exactly, and makes the null mean closed-form.
    """
    if rung not in RUNGS:
        raise ValueError(f"unknown rung {rung!r}")
    widths = band_widths(pool.delta_pool)
    n_min = min(pool.class_orders)

    keys: list = []
    for t, N in zip(pool.traces, pool.class_orders):
        if rung == "R0_FREE":
            keys.append((0,))
        elif rung == "R1_TWIST":
            keys.append((abs(t),))
        elif rung in ("R2_NBAND_w2", "R3_NBAND_w3", "R4_NBAND_w4"):
            keys.append(((N - n_min) // widths[rung],))
        elif rung == "R5_PERCLASS":
            keys.append((t,))
        else:                                     # R6_TWIST_AND_NBAND_w2
            keys.append((abs(t), (N - n_min) // widths["R2_NBAND_w2"]))

    uniq = sorted(set(keys))
    block_of_class = {ci: uniq.index(k) for ci, k in enumerate(keys)}
    assignment = {i: block_of_class[int(c)] for i, c in enumerate(pool.labels)}

    comp: dict[int, list[int]] = {}
    for ci, t in enumerate(pool.traces):
        comp.setdefault(block_of_class[ci], []).append(int(t))
    delta_max = 0
    for bid, traces in comp.items():
        Ns = [pool.class_orders[pool.traces.index(t)] for t in traces]
        delta_max = max(delta_max, max(Ns) - min(Ns))
    ge2 = sum(1 for v in comp.values() if len(v) >= 2)
    ge3 = sum(1 for v in comp.values() if len(v) >= 3)
    realized = {
        "rung": rung,
        "band_width": (widths[rung] if rung in widths else
                       widths["R2_NBAND_w2"] if rung == "R6_TWIST_AND_NBAND_w2"
                       else None),
        "n_blocks": len(uniq),
        "delta_max_N": int(delta_max),
        "blocks_with_ge_2_classes": int(ge2),
        "blocks_with_ge_3_classes": int(ge3),
        "degenerate": bool(ge2 == 0),
        "block_composition_by_trace": {str(k): sorted(v) for k, v in
                                       sorted(comp.items())},
        "block_key_rule": {
            "R0_FREE": "constant (one block)",
            "R1_TWIST": "abs(t)",
            "R2_NBAND_w2": "floor((N - N_min)/w2)",
            "R3_NBAND_w3": "floor((N - N_min)/w3)",
            "R4_NBAND_w4": "floor((N - N_min)/w4)",
            "R5_PERCLASS": "t",
            "R6_TWIST_AND_NBAND_w2": "(abs(t), floor((N - N_min)/w2))",
        }[rung],
    }
    return assignment, realized


def blocks_array(pool: Pool, rung: str) -> tuple[np.ndarray, dict]:
    assignment, realized = blocking(pool, rung)
    arr = np.array([assignment[i] for i in range(pool.n)], dtype=np.int64)
    return arr, realized


# --------------------------------------------------------------------------
# statistics -- canonical, multiset-determined, order-independent
# --------------------------------------------------------------------------


def _canonical_groups(values, labels) -> list[np.ndarray]:
    v = np.asarray(values, dtype=np.float64)
    l = np.asarray(labels)
    out = []
    for g in sorted(set(l.tolist())):
        out.append(np.sort(v[l == g]))
    return out


def statistic_weighted(values, labels) -> float:
    """T_w = SS_within/(n - K), SS_within = sum_c sum_{i in c} (Y_i - mean_c)^2.

    K is the number of labels PRESENT. Groups are summed in ascending value
    order so the result depends on the class value multisets alone.
    """
    groups = _canonical_groups(values, labels)
    n = sum(len(g) for g in groups)
    K = len(groups)
    if n <= K:
        return float("nan")
    ss = 0.0
    for g in groups:
        m = g.sum() / len(g)
        d = g - m
        ss += float((d * d).sum())
    return ss / (n - K)


def statistic_unweighted(values, labels) -> float:
    """T_unw = mean over labels with n_c >= 2 of the (n_c-1)-denominator s^2_c.

    The committed statistic (harness/exp_icinv.py::permutation_null uses the
    mean over groups of `statistics.variance`), retained for comparability only.
    """
    groups = _canonical_groups(values, labels)
    vs = []
    for g in groups:
        if len(g) < 2:
            continue
        m = g.sum() / len(g)
        d = g - m
        vs.append(float((d * d).sum()) / (len(g) - 1))
    return (sum(vs) / len(vs)) if vs else float("nan")


def classes_within_blocks(labels, blocks) -> bool:
    """True iff every class lies entirely inside one block.

    The closed-form null mean is VALID ONLY under this condition. It holds for
    every declared blocking on the real object (blocks are class invariants) and
    FAILS for the synthetic-label null object, whose classes straddle blocks.
    """
    l = np.asarray(labels)
    b = np.asarray(blocks)
    for g in set(l.tolist()):
        if len(set(b[l == g].tolist())) != 1:
            return False
    return True


def closed_form_null_mean(values, labels, blocks, statistic: str = "weighted"):
    """Exact E[T_pi | B] from the block-pooled sample variances.

      weighted   E[T_w   | B] = (sum_c (n_c - 1) * S2_block(c)) / (n - K)
      unweighted E[T_unw | B] = mean over labels with n_c >= 2 of S2_block(c)

    with S2_beta the pooled (n_beta - 1)-denominator sample variance of Y over
    block beta. Returns None when a class straddles blocks, in which case the
    closed form is not applicable and only the Monte-Carlo mean may be reported.
    """
    if not classes_within_blocks(labels, blocks):
        return None
    v = np.asarray(values, dtype=np.float64)
    l = np.asarray(labels)
    b = np.asarray(blocks)
    s2_block = {}
    for beta in sorted(set(b.tolist())):
        y = np.sort(v[b == beta])
        if len(y) < 2:
            s2_block[beta] = 0.0
            continue
        m = y.sum() / len(y)
        d = y - m
        s2_block[beta] = float((d * d).sum()) / (len(y) - 1)
    labs = sorted(set(l.tolist()))
    n = len(v)
    K = len(labs)
    if statistic == "weighted":
        if n <= K:
            return float("nan")
        tot = 0.0
        for g in labs:
            mask = l == g
            n_c = int(mask.sum())
            beta = int(b[mask][0])
            tot += (n_c - 1) * s2_block[beta]
        return tot / (n - K)
    vals = []
    for g in labs:
        mask = l == g
        if int(mask.sum()) < 2:
            continue
        vals.append(s2_block[int(b[mask][0])])
    return (sum(vals) / len(vals)) if vals else float("nan")


# --------------------------------------------------------------------------
# the vectorized within-block label permutation
# --------------------------------------------------------------------------


class _Layout:
    """Precomputed index machinery for one (labels, blocks) pair.

    Curves are first laid out in BLOCK order (so a block is a contiguous column
    range and can be permuted with one argsort), then re-gathered into CLASS
    order (so a class is a contiguous column range and can be reduced with one
    reduceat). Permuting the values within a block and keeping the label layout
    fixed is exactly the declared operation "permute the class labels held by
    the curves in that block": the two differ only by inverting the permutation,
    which is uniform either way.
    """

    def __init__(self, labels, blocks):
        l = np.asarray(labels, dtype=np.int64)
        b = np.asarray(blocks, dtype=np.int64)
        self.n = len(l)
        self.blk_order = np.argsort(b, kind="stable")
        b_sorted = b[self.blk_order]
        self.block_starts = [0] + list(np.flatnonzero(np.diff(b_sorted)) + 1)
        self.block_ends = self.block_starts[1:] + [self.n]
        l_in_blk = l[self.blk_order]
        self.cls_perm = np.argsort(l_in_blk, kind="stable")
        l_in_cls = l_in_blk[self.cls_perm]
        self.cls_offsets = np.array(
            [0] + list(np.flatnonzero(np.diff(l_in_cls)) + 1), dtype=np.int64)
        ends = list(self.cls_offsets[1:]) + [self.n]
        self.cls_sizes = np.array([e - s for s, e in zip(self.cls_offsets, ends)],
                                  dtype=np.int64)
        self.K = len(self.cls_sizes)
        self.ge2 = self.cls_sizes >= 2
        self.ge2_idx = [int(j) for j in np.flatnonzero(self.ge2)]
        self.sizes_f = self.cls_sizes.astype(np.float64)
        self.denom_w = float(self.n - self.K)
        self.n_ge2 = int(self.ge2.sum())

    def values_in_block_order(self, values) -> np.ndarray:
        return np.asarray(values, dtype=np.float64)[self.blk_order]

    def statistics(self, pc: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(T_weighted, T_unweighted) for a (chunk, n) array in CLASS order.

        THE FINAL SUM OVER CLASSES IS AN EXPLICIT LEFT-TO-RIGHT ACCUMULATION
        AND NOT `ndarray.sum(axis=1)`, AND THAT IS NOT A STYLE CHOICE.
        `np.add.reduceat` returns a (rows, K) array whose contiguity depends on
        `rows`, and numpy switches between a pairwise and a strided reduction
        accordingly -- so `SS[:, ge2].sum(axis=1)` returned a DIFFERENT LAST BIT
        for a one-row observed array than for a 2083-row null chunk. That
        one-ulp difference made p_lower at R5_PERCLASS come out at the
        resolution floor instead of exactly 1.0 for three functionals at POOL_B
        (RUN-INSTR-85b102-poolB, superseded). Accumulating column by column is
        elementwise on each column, so it is exact per element and independent
        of the number of rows.
        """
        for s, sz in zip(self.cls_offsets, self.cls_sizes):
            pc[:, s:s + sz].sort(axis=1)
        S = np.add.reduceat(pc, self.cls_offsets, axis=1)
        np.divide(S, self.sizes_f, out=S)
        rep = np.repeat(S, self.cls_sizes, axis=1)
        np.subtract(pc, rep, out=pc)
        np.multiply(pc, pc, out=pc)
        SS = np.add.reduceat(pc, self.cls_offsets, axis=1)
        rows = pc.shape[0]
        t_w = np.zeros(rows, dtype=np.float64)
        for j in range(self.K):
            t_w += SS[:, j]
        t_w /= self.denom_w
        if self.n_ge2:
            t_u = np.zeros(rows, dtype=np.float64)
            for j in self.ge2_idx:
                t_u += SS[:, j] / (self.sizes_f[j] - 1.0)
            t_u /= self.n_ge2
        else:
            t_u = np.full(rows, np.nan)
        return t_w, t_u

    def observed(self, values) -> tuple[float, float]:
        """T_obs through the identical code path, identity permutation."""
        vb = self.values_in_block_order(values)
        pc = vb[self.cls_perm][None, :].copy()
        t_w, t_u = self.statistics(pc)
        return float(t_w[0]), float(t_u[0])

    def observed_shape_invariance(self, values, rows: int = 8) -> dict:
        """Self-check: T_obs must not depend on the array shape it is computed in.

        This is the check whose absence let the POOL_B R5_PERCLASS defect
        through. It costs microseconds and it runs on every cell.
        """
        vb = self.values_in_block_order(values)
        one = self.statistics(vb[self.cls_perm][None, :].copy())
        many = self.statistics(
            np.repeat(vb[self.cls_perm][None, :], rows, axis=0).copy())
        return {"rows_compared": rows,
                "weighted_shape_invariant": bool(one[0][0] == many[0][0]),
                "unweighted_shape_invariant": bool(one[1][0] == many[1][0]),
                "weighted_one_row": float(one[0][0]),
                "weighted_many_rows": float(many[0][0]),
                "unweighted_one_row": float(one[1][0]),
                "unweighted_many_rows": float(many[1][0])}


def _chunk_size(B: int, n: int) -> int:
    return max(1, min(B, CHUNK_ELEMENTS // max(n, 1)))


def blocked_permutation_null_both(values, labels, blocks, B: int, seed: int,
                                  layout: "_Layout | None" = None) -> dict:
    """Both statistics from one pass of B within-block label permutations.

    Returns a dict with, per statistic, T_obs, the empirical null mean, its
    standard deviation and Monte-Carlo standard error, the RAW counts
    r_lower = #{v <= T_obs} and r_upper = #{v >= T_obs}, and
    p_lower = (1 + r_lower)/(1 + B), p_upper = (1 + r_upper)/(1 + B).

    `layout` is a pure cache of the index machinery for this (labels, blocks)
    pair; passing it changes no draw and no number, only the setup cost.
    """
    lay = layout if layout is not None else _Layout(labels, blocks)
    vb = lay.values_in_block_order(values)
    t_obs_w, t_obs_u = lay.observed(values)
    shape_check = lay.observed_shape_invariance(values)

    nulls_w = np.empty(B, dtype=np.float64)
    nulls_u = np.empty(B, dtype=np.float64)
    rng = np.random.default_rng(seed)
    chunk = _chunk_size(B, lay.n)
    done = 0
    while done < B:
        c = min(chunk, B - done)
        keys = rng.random((c, lay.n))
        idx = np.empty((c, lay.n), dtype=np.int64)
        for s, e in zip(lay.block_starts, lay.block_ends):
            idx[:, s:e] = np.argsort(keys[:, s:e], axis=1) + s
        pv = vb[idx]
        pc = pv[:, lay.cls_perm]
        t_w, t_u = lay.statistics(pc)
        nulls_w[done:done + c] = t_w
        nulls_u[done:done + c] = t_u
        done += c

    out = {}
    for key, t_obs, nulls in (("weighted", t_obs_w, nulls_w),
                              ("unweighted", t_obs_u, nulls_u)):
        r_lower = int(np.count_nonzero(nulls <= t_obs))
        r_upper = int(np.count_nonzero(nulls >= t_obs))
        mean = float(nulls.mean())
        sd = float(nulls.std(ddof=1)) if B > 1 else 0.0
        nmin, nmax = float(nulls.min()), float(nulls.max())
        # A null distribution whose whole spread sits at the rounding scale of
        # its own mean is a POINT MASS that np.mean's pairwise summation has
        # smeared by an ulp -- which is what a degenerate rung produces, since
        # the within-block label permutation there is the identity. Saying so
        # matters because a Monte-Carlo standard error computed from that
        # spread is an ulp/sqrt(B) and dividing anything by it is meaningless.
        ulp_scale = 8.0 * np.finfo(np.float64).eps * max(abs(mean), 1e-300)
        point_mass = bool(nmax - nmin == 0.0 or sd <= ulp_scale)
        out[key] = {
            "T_obs": t_obs,
            "empirical_null_mean": mean,
            "null_sd": sd,
            "null_min": nmin,
            "null_max": nmax,
            "null_is_point_mass_within_fp_noise": point_mass,
            "null_point_mass_criterion": {
                "sd": sd, "ulp_scale_8eps_times_mean": ulp_scale,
                "max_minus_min": nmax - nmin},
            "mc_standard_error": sd / math.sqrt(B) if B else float("nan"),
            "r_lower": r_lower,
            "r_upper": r_upper,
            "p_lower": (1 + r_lower) / (1 + B),
            "p_upper": (1 + r_upper) / (1 + B),
            "T_obs_at_or_below_null_min": bool(t_obs <= nmin),
            "T_obs_at_or_above_null_max": bool(t_obs >= nmax),
            "B": B,
            "resolution_floor": 1.0 / (1 + B),
            "t_obs_shape_invariance_check": shape_check,
        }
    return out


def blocked_permutation_null(values, labels, blocks, B: int, seed: int,
                             statistic: str = "weighted"):
    """(T_obs, empirical_null_mean, null_sd, r_lower, r_upper, p_lower, p_upper).

    The contract's required signature. `statistic` selects which of the two
    always-computed statistics is returned; use
    `blocked_permutation_null_both` to get both from one pass.
    """
    d = blocked_permutation_null_both(values, labels, blocks, B, seed)[statistic]
    return (d["T_obs"], d["empirical_null_mean"], d["null_sd"],
            d["r_lower"], d["r_upper"], d["p_lower"], d["p_upper"])


# --------------------------------------------------------------------------
# LAYER 1: exact sum sets, no targets and no sampling
# --------------------------------------------------------------------------


def _pm_points(E: EllipticCurve, fb: list[int]) -> list:
    """+-V for the factor base, built exactly as the frozen decomposition
    functions build it, so |mV| is the size of the very set they test against."""
    pts = []
    for x in fb:
        P = E.lift_x(x)
        if P is not None:
            pts.append(P)
            pts.append(E.negate(P))
    return pts


def sumset_m2(E: EllipticCurve, fb: list[int]) -> tuple[int, set]:
    """(|2V|, 2V) by exact enumeration. No targets, no sampling, no solver.

    Removes the binomial sampling variance from the m=2 decomposition
    functional entirely. |2V| is NOT claimed N-free: it is bounded by N and its
    additive-collision rate depends on N. Only the SAMPLING dependence on N is
    removed, which strictly increases power and therefore strictly increases the
    danger from an uncorrected N confound (pre-registered as P7).
    """
    pts = _pm_points(E, fb)
    sums = set()
    for i in range(len(pts)):
        for jx in range(i, len(pts)):
            S = E.add(pts[i], pts[jx])
            if S is not None:
                sums.add(S)
    return len(sums), sums


def sumset_m3(E: EllipticCurve, fb: list[int]) -> tuple[int, set]:
    """(|3V|, 3V) by exact enumeration."""
    pts = _pm_points(E, fb)
    two = set()
    for i in range(len(pts)):
        for jx in range(i, len(pts)):
            S = E.add(pts[i], pts[jx])
            if S is not None:
                two.add(S)
    three = set()
    for S in two:
        for R in pts:
            T = E.add(S, R)
            if T is not None:
                three.add(T)
    return len(three), three


# --------------------------------------------------------------------------
# control objects
# --------------------------------------------------------------------------


def exact_binomial_interval(n: int, p0: float, conf: float = BINOMIAL_CONF
                            ) -> tuple[int, int]:
    """Exact two-sided acceptance region for Binomial(n, p0) at level 1 - conf.

    {k : P(X <= k) > alpha/2 and P(X >= k) > alpha/2}, computed with exact
    binomial probabilities (no normal approximation).
    """
    alpha = 1.0 - conf
    logs = [math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
            + k * math.log(p0) + (n - k) * math.log1p(-p0) for k in range(n + 1)]
    pmf = [math.exp(x) for x in logs]
    cdf, acc = [], 0.0
    for v in pmf:
        acc += v
        cdf.append(acc)
    lo = next(k for k in range(n + 1) if cdf[k] > alpha / 2)
    sf = [1.0 - (cdf[k - 1] if k > 0 else 0.0) for k in range(n + 1)]
    hi = max(k for k in range(n + 1) if sf[k] > alpha / 2)
    return lo, hi


def null_object_labels(pool: Pool, rung: str, replicate: int) -> np.ndarray:
    """CTRL-NULLOBJ: synthetic trace-independent labels of the TRUE size multiset.

    A uniform permutation of the curves cut into consecutive runs of sizes equal
    to the true class-size multiset. Independent of the trace by construction,
    so the control CANNOT fail for a mathematical reason -- only if the
    implementation is wrong, which is exactly why it is here.
    """
    seed = derive_seed("NULLOBJ", pool.name, rung, "labels", 0, replicate)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(pool.n)
    labels = np.empty(pool.n, dtype=np.int64)
    pos = 0
    for ci, size in enumerate(pool.class_sizes):
        labels[perm[pos:pos + size]] = ci
        pos += size
    return labels


def power_offsets(pool: Pool, blocks: np.ndarray) -> np.ndarray:
    """u_c in {+1,-1}, balanced WITHIN each block, ordered by the low byte of
    SHA-256(domain || "|u|" || decimal(trace)).

    The effect must vary WITHIN blocks or no blocked test could ever see it,
    which would make the arm a tautology rather than a power test; the
    hash-determined order keeps the offsets from being a monotone function of N,
    which would make the planted effect an N effect the blocking is correct to
    remove.
    """
    block_of_class = {}
    for ci in range(pool.K):
        idx = int(np.flatnonzero(pool.labels == ci)[0])
        block_of_class[ci] = int(blocks[idx])
    u = np.zeros(pool.K, dtype=np.float64)
    for beta in sorted(set(block_of_class.values())):
        members = [ci for ci in range(pool.K) if block_of_class[ci] == beta]
        members.sort(key=lambda ci: (_u_order_key(pool.traces[ci]),
                                     pool.traces[ci]))
        for k, ci in enumerate(members):
            u[ci] = 1.0 if k % 2 == 0 else -1.0
    return u


def within_block_corr_u_N(pool: Pool, blocks: np.ndarray, u: np.ndarray) -> float:
    """Realized within-block correlation between the planted offset and N.

    Reported so a reader can see whether the planted effect is accidentally
    aligned with the nuisance the blocking is meant to remove.
    """
    block_of_class = {}
    for ci in range(pool.K):
        idx = int(np.flatnonzero(pool.labels == ci)[0])
        block_of_class[ci] = int(blocks[idx])
    xs, ys = [], []
    for beta in sorted(set(block_of_class.values())):
        members = [ci for ci in range(pool.K) if block_of_class[ci] == beta]
        if len(members) < 2:
            continue
        Ns = np.array([pool.class_orders[ci] for ci in members], dtype=float)
        us = np.array([u[ci] for ci in members], dtype=float)
        Ns -= Ns.mean()
        us -= us.mean()
        xs.extend(Ns.tolist())
        ys.extend(us.tolist())
    if len(xs) < 2:
        return float("nan")
    x = np.array(xs)
    y = np.array(ys)
    dx = float(np.sqrt((x * x).sum()))
    dy = float(np.sqrt((y * y).sum()))
    if dx == 0.0 or dy == 0.0:
        return float("nan")
    return float((x * y).sum() / (dx * dy))


def ols_slope_on_N(pool: Pool, values: np.ndarray) -> tuple[float, float]:
    """Size-weighted OLS slope of class mean on N, with its standard error.

    Used by CTRL-NSURR for every functional except `order` (slope exactly 1) and
    `full_liftable` (slope exactly 1/2), which are EXACT and labelled as such.
    """
    means = np.array([values[pool.labels == ci].mean() for ci in range(pool.K)])
    Ns = np.array(pool.class_orders, dtype=np.float64)
    w = np.array(pool.class_sizes, dtype=np.float64)
    wsum = w.sum()
    nbar = float((w * Ns).sum() / wsum)
    mbar = float((w * means).sum() / wsum)
    sxx = float((w * (Ns - nbar) ** 2).sum())
    if sxx == 0.0:
        return float("nan"), float("nan")
    slope = float((w * (Ns - nbar) * (means - mbar)).sum() / sxx)
    resid = means - (mbar + slope * (Ns - nbar))
    dof = pool.K - 2
    if dof <= 0:
        return slope, float("nan")
    s2 = float((w * resid ** 2).sum() / dof)
    return slope, float(math.sqrt(max(s2, 0.0) / sxx))


# ==========================================================================
# CTRL-FROZEN-DIFF: a behavioural receipt for every frozen harness function
# ==========================================================================

FROZEN_FUNCTIONS = (
    "_targets", "targets_uniform", "permutation_null", "binomial_null_verdict",
    "exact_null_verdict", "decomposition_rate_m2", "decomposition_rate_m3",
    "liftable_density", "factor_base_fixed_size", "factor_base_window",
    "two_torsion_x_count",
)
FROZEN_FILES = ("harness/exp_icinv.py", "harness/isogeny_class.py",
                "harness/run_icinv.py", "harness/toycurve.py")

# Declared behavioural probe. Fixed, cheap, and re-runnable by a reviewer.
PROBE_P, PROBE_A, PROBE_B = 101, 2, 3
PROBE_SEED = 12345


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _function_source_from_blob(blob: str, name: str) -> str | None:
    import ast
    try:
        tree = ast.parse(blob)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(blob, node)
    return None


def frozen_function_report(base_ref: str = "HEAD",
                           context_ref: str = "origin/main") -> tuple[str, dict]:
    """Behavioural diff status for every frozen harness function.

    Three independent receipts, because "I did not change it" is exactly the
    claim this campaign has twice had to retract:
      1. git: the working tree differs from `base_ref` on none of the frozen
         files;
      2. source: the SHA-256 of each named function's source text, taken live
         with `inspect.getsource`, equals the SHA-256 of the same function
         extracted from the committed blob at `base_ref`. Both sides are
         `.strip()`ed first: `inspect.getsource` keeps the trailing newline and
         `ast.get_source_segment` does not, and that difference is a property of
         the two readers, not of the code;
      3. behaviour: each function evaluated on a declared fixed probe, with its
         output recorded so a reviewer can re-run and compare numbers rather
         than trust a hash.

    `base_ref` is the BINDING comparison and defaults to HEAD -- the commit the
    approved contract was written against and the commit the four committed runs
    were produced at. `context_ref` is reported alongside it and is NOT the
    claim: harness/exp_icinv.py and harness/isogeny_class.py already differed
    from origin/main before this contract existed, because commit c9c27221 on
    this branch carries the campaign's own sampler correction
    (CORR-20260807-9f83be), which this contract cites rather than introduces.
    """
    import inspect
    import os
    import subprocess
    from dataclasses import asdict

    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def git(*a):
        return subprocess.run(["git", *a], cwd=repo, capture_output=True,
                              text=True)

    rep: dict = {"base_ref": base_ref,
                 "base_ref_meaning": "BINDING: the commit this contract was "
                                     "approved against and the committed runs "
                                     "were produced at",
                 "context_ref": context_ref,
                 "context_ref_meaning": "informational only; pre-existing "
                                        "branch commits already moved these "
                                        "files relative to it",
                 "base_commit": git("rev-parse", base_ref).stdout.strip(),
                 "context_commit": git("rev-parse", context_ref).stdout.strip(),
                 "head_commit": git("rev-parse", "HEAD").stdout.strip(),
                 "files": {}, "functions": {}, "behavioural_probe": {}}
    for path in FROZEN_FILES:
        d2 = git("diff", base_ref, "--", path)
        dc = git("diff", context_ref, "--", path)
        st = git("status", "--porcelain", "--", path).stdout.strip()
        rep["files"][path] = {
            "diff_vs_base_empty": (d2.stdout.strip() == ""),
            "diff_bytes": len(d2.stdout),
            "git_status_porcelain": st,
            "worktree_sha256": _sha(open(os.path.join(repo, path),
                                         encoding="utf-8").read()),
            "base_sha256": _sha(git("show", f"{base_ref}:{path}").stdout),
            "context_diff_vs_origin_main_empty": (dc.stdout.strip() == ""),
            "context_diff_bytes": len(dc.stdout),
        }

    base_blob = git("show", f"{base_ref}:harness/exp_icinv.py").stdout
    for name in FROZEN_FUNCTIONS:
        live = inspect.getsource(getattr(ex, name)).strip()
        based = _function_source_from_blob(base_blob, name)
        based = based.strip() if based is not None else None
        same = based is not None and _sha(live) == _sha(based)
        rep["functions"][name] = {
            "live_source_sha256": _sha(live),
            "base_source_sha256": _sha(based) if based is not None else None,
            "identical": bool(same),
            "status": "UNCHANGED" if same else "CHANGED_OR_UNRESOLVED",
        }

    E = EllipticCurve(PROBE_P, PROBE_A, PROBE_B)
    order = ic.curve_order(PROBE_P, PROBE_A, PROBE_B)
    fb = ex.factor_base_fixed_size(E, 10)
    win = ex.factor_base_window(E, 40)
    tg_h = ex._targets(E, 5, PROBE_SEED)
    tg_u = ex.targets_uniform(E, order, 5, PROBE_SEED)
    probe = {
        "curve": {"p": PROBE_P, "a": PROBE_A, "b": PROBE_B, "order": order},
        "factor_base_fixed_size(E,10)": fb,
        "factor_base_window(E,40)": win,
        "liftable_density(E,40)": ex.liftable_density(E, 40),
        "two_torsion_x_count(p,a,b)": ex.two_torsion_x_count(PROBE_P, PROBE_A,
                                                             PROBE_B),
        "_targets(E,5,seed)": [list(t) for t in tg_h],
        "targets_uniform(E,order,5,seed)": [list(t) for t in tg_u],
        "decomposition_rate_m2(E,fb,tg_u)": list(
            ex.decomposition_rate_m2(E, fb, tg_u)),
        "decomposition_rate_m3(E,fb[:4],tg_u)": list(
            ex.decomposition_rate_m3(E, fb[:4], tg_u)),
        "permutation_null(probe_groups,50,7)": list(ex.permutation_null(
            {0: [1.0, 2.0, 3.0, 4.0], 1: [2.0, 2.5, 3.5, 9.0]},
            iterations=50, seed=7)),
        "binomial_null_verdict('probe',[3,5,4,6,5],20)": asdict(
            ex.binomial_null_verdict("probe", [3, 5, 4, 6, 5], 20)),
        "exact_null_verdict('probe',[1.0,1.0,1.0])": asdict(
            ex.exact_null_verdict("probe", [1.0, 1.0, 1.0])),
    }
    rep["behavioural_probe"] = probe

    all_files_clean = all(v["diff_vs_base_empty"] for v in rep["files"].values())
    all_fn_same = all(v["identical"] for v in rep["functions"].values())
    rep["verdict"] = ("ZERO BEHAVIOURAL CHANGE" if all_files_clean and all_fn_same
                      else "CHANGE DETECTED -- SEE ROWS")

    lines = [
        "CTRL-FROZEN-DIFF -- behavioural diff status for every frozen harness function",
        f"experiment: {EXPERIMENT_ID}",
        f"base_ref (BINDING): {base_ref} = {rep['base_commit']}",
        f"context_ref (INFO): {context_ref} = {rep['context_commit']}",
        f"head:               {rep['head_commit']}",
        "",
        "1. FILE-LEVEL GIT DIFF (working tree vs base_ref)",
    ]
    for path, v in rep["files"].items():
        lines.append(f"   {path:32s} diff_empty={str(v['diff_vs_base_empty']):5s} "
                     f"bytes={v['diff_bytes']:<6d} sha_worktree={v['worktree_sha256'][:16]} "
                     f"sha_base={v['base_sha256'][:16]} "
                     f"status={v['git_status_porcelain']!r} "
                     f"[info: diff_vs_origin_main_empty="
                     f"{v['context_diff_vs_origin_main_empty']}]")
    lines += ["", "2. PER-FUNCTION SOURCE IDENTITY (inspect.getsource vs committed blob)"]
    for name, v in rep["functions"].items():
        lines.append(f"   {name:26s} {v['status']:22s} live={v['live_source_sha256'][:16]} "
                     f"base={(v['base_source_sha256'] or 'NONE')[:16]}")
    lines += ["", "3. BEHAVIOURAL PROBE (declared fixed inputs; re-runnable)"]
    for k, v in probe.items():
        lines.append(f"   {k} = {v!r}")
    lines += ["", f"VERDICT: {rep['verdict']}",
              "",
              "Note: this contract ADDS harness/run_blocknull.py. Adding a new "
              "module changes no existing function's behaviour; rows 1-3 above "
              "are the evidence, not the claim.",
              "",
              "Note on context_ref: harness/exp_icinv.py and "
              "harness/isogeny_class.py already differed from origin/main "
              "BEFORE this contract existed -- branch commit c9c27221 "
              "(BATCH-523510) carries the campaign's own sampler correction, "
              "which this contract cites (CORR-20260807-9f83be) rather than "
              "introduces. The binding comparison is against base_ref, the "
              "commit the contract was approved at and the committed runs were "
              "produced at."]
    return "\n".join(lines) + "\n", rep


# ==========================================================================
# committed reproduction fixtures
# ==========================================================================

FIXTURES = [
    {"id": "F-PERM-LIFTDENS-RAWCOUNT",
     "quantity": "permutation_null.liftable_density raw count",
     "committed_value": {"r": 1, "B": 2000, "p_value": 0.0005},
     "sampler_free": True,
     "primary_path": "experiments/EXP-ICINV-180a0d/runs/RUN-ICINV-p4001-a/raw-result.json",
     "json_path": ["raw", "permutation_null", "liftable_density", "p_value"]},
    {"id": "F-WDECAY-RAWCOUNT",
     "quantity": "window_decay W=4001 raw count",
     "committed_value": {"r": 0, "B": 1000, "p_value": 0.0},
     "sampler_free": True,
     "primary_path": "experiments/EXP-ICINV-180a0d/runs/RUN-ICINV-p4001-a/raw-result.json",
     "json_path": ["raw", "window_decay", "4001", "permutation_p_value"]},
    {"id": "F-WDECAY-OBSERVED",
     "quantity": "window_decay W=4001 observed_mean_within_variance",
     "committed_value": 1.557881769803647e-08,
     "sampler_free": True,
     "primary_path": "experiments/EXP-ICINV-180a0d/runs/RUN-ICINV-p4001-a/raw-result.json",
     "json_path": ["raw", "window_decay", "4001", "observed_mean_within_variance"]},
    {"id": "F-WDECAY-NULLMEAN",
     "quantity": "window_decay W=4001 null_mean",
     "committed_value": 1.0357263552475702e-05,
     "sampler_free": True,
     "primary_path": "experiments/EXP-ICINV-180a0d/runs/RUN-ICINV-p4001-a/raw-result.json",
     "json_path": ["raw", "window_decay", "4001", "null_mean"]},
    {"id": "F-FULLFIELD-COUNTVAR",
     "quantity": "full_field_liftable_within_class_count_variance",
     "committed_value": 0.24938572928898783,
     "sampler_free": True,
     "primary_path": "experiments/EXP-ICINV-180a0d/runs/RUN-ICINV-p4001-a/manifest.yaml",
     "json_path": ["metrics", "full_field_liftable_within_class_count_variance"]},
    {"id": "F-VARZ-T30",
     "quantity": "Var(two_torsion_x) at traces 30 and -30 (n=138)",
     "committed_value": 1.0053951126626468,
     "sampler_free": True,
     "primary_path": "experiments/EXP-ICINV-180a0d/runs/RUN-ICINV-p4001-a/raw-result.json",
     "json_path": ["raw", "per_class", "30", "verdicts", "two_torsion_x", "variance"]},
    {"id": "F-VARZ-T18",
     "quantity": "Var(two_torsion_x) at traces 18 and -18 (n=98)",
     "committed_value": 0.9896907216494846,
     "sampler_free": True,
     "primary_path": "experiments/EXP-ICINV-180a0d/runs/RUN-ICINV-p4001-a/raw-result.json",
     "json_path": ["raw", "per_class", "18", "verdicts", "two_torsion_x", "variance"]},
    {"id": "F-DEGENFIX-EFF-M2",
     "quantity": "RUN-ICINV-p4001-degenfix decomp_efficiency_m2 permutation p",
     "committed_value": 0.7815, "sampler_free": False,
     "primary_path": "experiments/EXP-ICINV-9b1f7c/runs/RUN-ICINV-p4001-degenfix/raw-result.json",
     "json_path": ["metrics", "permutation_p_values", "decomp_efficiency_m2"]},
    {"id": "F-DEGENFIX-EFF-M3",
     "quantity": "RUN-ICINV-p4001-degenfix decomp_efficiency_m3 permutation p",
     "committed_value": 0.098, "sampler_free": False,
     "primary_path": "experiments/EXP-ICINV-9b1f7c/runs/RUN-ICINV-p4001-degenfix/raw-result.json",
     "json_path": ["metrics", "permutation_p_values", "decomp_efficiency_m3"]},
    {"id": "F-DEGENFIX-RATE-M2",
     "quantity": "RUN-ICINV-p4001-degenfix decomp_rate_m2_RAW permutation p",
     "committed_value": 0.2825, "sampler_free": False,
     "primary_path": "experiments/EXP-ICINV-9b1f7c/runs/RUN-ICINV-p4001-degenfix/raw-result.json",
     "json_path": ["metrics", "permutation_p_values",
                   "decomp_rate_m2_RAW_confounded_by_order"]},
    {"id": "F-DEGENFIX-RATE-M3",
     "quantity": "RUN-ICINV-p4001-degenfix decomp_rate_m3_RAW permutation p",
     "committed_value": 0.107, "sampler_free": False,
     "primary_path": "experiments/EXP-ICINV-9b1f7c/runs/RUN-ICINV-p4001-degenfix/raw-result.json",
     "json_path": ["metrics", "permutation_p_values",
                   "decomp_rate_m3_RAW_confounded_by_order"]},
]


def resolve_fixtures(repo: str) -> list[dict]:
    """Resolve every committed fixture to its primary artifact path.

    RESOLVED / UNREACHABLE, the value read, and the signed difference against
    the value the contract declares. More than half UNREACHABLE stops the run
    and the provenance failure is the deliverable.
    """
    import json
    import os
    out = []
    for fx in FIXTURES:
        row = {k: fx[k] for k in ("id", "quantity", "sampler_free",
                                  "primary_path")}
        row["declared_value"] = fx["committed_value"]
        full = os.path.join(repo, fx["primary_path"])
        if not os.path.exists(full):
            row.update(status="UNREACHABLE", value_read=None,
                       signed_difference=None, note="path does not exist")
            out.append(row)
            continue
        try:
            if full.endswith(".yaml"):
                import yaml
                doc = yaml.safe_load(open(full, encoding="utf-8"))["run"]["result"]
            else:
                doc = json.load(open(full, encoding="utf-8"))
            cur = doc
            for k in fx["json_path"]:
                cur = cur[k]
        except Exception as exc:
            row.update(status="UNREACHABLE", value_read=None,
                       signed_difference=None,
                       note=f"{type(exc).__name__}: {exc}")
            out.append(row)
            continue
        declared = fx["committed_value"]
        if isinstance(declared, dict):
            r_read = round(cur * declared["B"])
            row.update(status="RESOLVED",
                       value_read={"p_value": cur, "r": r_read,
                                   "B": declared["B"]},
                       signed_difference=r_read - declared["r"],
                       note=("raw count recovered exactly as p_value * B; the "
                             "committed artifact stores the p-value, and "
                             "permutation_null returns worse/iterations"))
        else:
            row.update(status="RESOLVED", value_read=cur,
                       signed_difference=cur - declared, note="")
        out.append(row)
    return out


# ==========================================================================
# S1: the zero-compute arithmetic gate
# ==========================================================================

COMMITTED_T_OBS = 0.24938572928898783
COMMITTED_NULL_MEAN_RATE = 1.0357263552475702e-05


def s1_arithmetic_gate(repo: str) -> dict:
    """Re-derive mean_c Var(z_c)/4 and the closed-form free-permutation null
    mean FROM COMMITTED NUMBERS ALONE, in seconds, before any compute.

    If either fails, the diagnosis that the committed 664x is the group order is
    WITHDRAWN, the run ENDS here, and that withdrawal is the deliverable.
    """
    import json
    import os
    src = os.path.join(
        repo, "experiments/EXP-ICINV-180a0d/runs/RUN-ICINV-p4001-a/raw-result.json")
    doc = json.load(open(src, encoding="utf-8"))
    per_class = doc["raw"]["per_class"]
    p = doc["raw"]["p"]
    rows = []
    for t, v in per_class.items():
        z = v["verdicts"]["two_torsion_x"]
        rows.append({"trace": int(t), "N": v["order"], "n": z["n_curves"],
                     "mean_z": z["mean"], "var_z": z["variance"]})
    rows.sort(key=lambda r: r["trace"])

    t_obs = sum(r["var_z"] for r in rows) / len(rows) / 4.0
    diff_t = t_obs - COMMITTED_T_OBS

    n = sum(r["n"] for r in rows)
    nbar = sum(r["n"] * r["N"] for r in rows) / n
    zbar = sum(r["n"] * r["mean_z"] for r in rows) / n
    ss_N = sum(r["n"] * (r["N"] - nbar) ** 2 for r in rows)
    ss_z = (sum((r["n"] - 1) * r["var_z"] for r in rows)
            + sum(r["n"] * (r["mean_z"] - zbar) ** 2 for r in rows))
    sp_Nz = sum(r["n"] * (r["N"] - nbar) * (r["mean_z"] - zbar) for r in rows)
    s2_N = ss_N / (n - 1)
    s2_z = ss_z / (n - 1)
    cov_Nz = sp_Nz / (n - 1)
    s2_Y = (s2_N + s2_z + 2 * cov_Nz) / 4.0
    rate = s2_Y / (p * p)
    rel = (rate - COMMITTED_NULL_MEAN_RATE) / COMMITTED_NULL_MEAN_RATE

    ok_t = abs(diff_t) <= 1e-9
    ok_rate = abs(rel) <= 1e-3
    return {
        "stage": "S1", "source": os.path.relpath(src, repo),
        "inputs_read_from_committed_artifact": rows,
        "pooled_n": n, "grand_mean_N": nbar, "grand_mean_z": zbar,
        "SS_N": ss_N, "S2_N": s2_N, "SS_z": ss_z, "S2_z": s2_z,
        "Cov_N_z": cov_Nz, "S2_Y_count_units": s2_Y,
        "rederived_T_obs_count_units": t_obs,
        "committed_T_obs": COMMITTED_T_OBS,
        "signed_difference_T_obs": diff_t,
        "tolerance_T_obs": 1e-9,
        "T_obs_gate": "PASS" if ok_t else "FAIL",
        "rederived_null_mean_rate_units": rate,
        "committed_null_mean_rate_units": COMMITTED_NULL_MEAN_RATE,
        "signed_difference_null_mean": rate - COMMITTED_NULL_MEAN_RATE,
        "relative_residual_null_mean": rel,
        "tolerance_relative": 1e-3,
        "null_mean_gate": "PASS" if ok_rate else "FAIL",
        "gate": "PASS" if (ok_t and ok_rate) else "FAIL",
        "on_fail": ("The diagnosis that the committed 664x ratio is the group "
                    "order plus the 2-torsion term is WITHDRAWN (H-INSTR-fffbfb "
                    "C1 falsified at zero compute) and the run ENDS."),
        "committed_ratio_664x": (COMMITTED_NULL_MEAN_RATE
                                 / 1.557881769803647e-08),
    }


# ==========================================================================
# S2: committed-fixture reproduction on the frozen POOL-A slice
# ==========================================================================


def s2_reproduce(p: int, traces: list[int], classes: dict) -> dict:
    """Re-run the EXISTING free permutation at seed 20260807 and reproduce the
    committed fixtures on RAW COUNTS, not merely on rounded p-values.

    Every call below is to an UNMODIFIED committed function. The realized dict
    insertion order is recorded, because
    harness/exp_icinv.py::permutation_null derives its group sizes from
    `groups.values()` and its shuffle from `random.Random(seed)`, so
    reproduction depends on it.
    """
    import statistics as _st
    seed = REPRODUCTION_SEED
    out: dict = {"stage": "S2", "seed": seed,
                 "realized_dict_insertion_order": [int(t) for t in traces],
                 "curve_order_within_class":
                     "harness/isogeny_class.py::isogeny_classes order, "
                     "i.e. enumerate_curves(p) order (by j-invariant then twist)",
                 "checks": []}

    # --- fixture 1: top-level permutation_null on liftable_density(W=400) ---
    groups = {}
    for t in traces:
        groups[t] = [ex.liftable_density(r.curve(), REPRO_WINDOW)
                     for r in classes[t]]
    obs, nullmean, pval = ex.permutation_null(groups, iterations=2000, seed=seed)
    r_lower = round(pval * 2000)
    out["checks"].append({
        "fixture": "F-PERM-LIFTDENS-RAWCOUNT", "sampler_free": True,
        "committed": {"r": 1, "B": 2000, "p_value": 0.0005},
        "reproduced": {"r": r_lower, "B": 2000, "p_value": pval,
                       "observed": obs, "null_mean": nullmean},
        "raw_count_match": bool(r_lower == 1),
        "p_value_bitwise_match": bool(pval == 0.0005),
    })

    # --- fixtures 2-4: the committed window_decay code path, verbatim ---
    wins = sorted({max(8, p // 32), p // 16, p // 8, p // 4, p // 2, p})
    decay = ri.window_decay(p, list(traces), classes, wins, seed)
    full = decay[str(p)]
    out["window_decay_windows"] = wins
    out["window_decay_full_field_cell"] = full
    out["checks"].append({
        "fixture": "F-WDECAY-RAWCOUNT", "sampler_free": True,
        "committed": {"r": 0, "B": 1000, "p_value": 0.0},
        "reproduced": {"r": round(full["permutation_p_value"] * 1000),
                       "B": 1000, "p_value": full["permutation_p_value"]},
        "raw_count_match": bool(round(full["permutation_p_value"] * 1000) == 0),
        "p_value_bitwise_match": bool(full["permutation_p_value"] == 0.0),
    })
    out["checks"].append({
        "fixture": "F-WDECAY-OBSERVED", "sampler_free": True,
        "committed": 1.557881769803647e-08,
        "reproduced": full["observed_mean_within_variance"],
        "signed_difference": full["observed_mean_within_variance"]
        - 1.557881769803647e-08,
        "bitwise_match": bool(full["observed_mean_within_variance"]
                              == 1.557881769803647e-08),
    })
    out["checks"].append({
        "fixture": "F-WDECAY-NULLMEAN", "sampler_free": True,
        "committed": 1.0357263552475702e-05,
        "reproduced": full["null_mean"],
        "signed_difference": full["null_mean"] - 1.0357263552475702e-05,
        "bitwise_match": bool(full["null_mean"] == 1.0357263552475702e-05),
    })
    out["checks"].append({
        "fixture": "F-FULLFIELD-COUNTVAR", "sampler_free": True,
        "committed": COMMITTED_T_OBS,
        "reproduced": full["mean_within_class_count_variance"],
        "signed_difference": full["mean_within_class_count_variance"]
        - COMMITTED_T_OBS,
        "bitwise_match": bool(full["mean_within_class_count_variance"]
                              == COMMITTED_T_OBS),
    })

    # --- fixture: per-class Var(two_torsion_x) ---
    zvar = {}
    for t in traces:
        zs = [float(ex.two_torsion_x_count(r.p, r.a, r.b)) for r in classes[t]]
        zvar[int(t)] = _st.variance(zs)
    for fid, tr, val in (("F-VARZ-T30", 30, 1.0053951126626468),
                         ("F-VARZ-T18", 18, 0.9896907216494846)):
        got = [zvar.get(tr), zvar.get(-tr)]
        out["checks"].append({
            "fixture": fid, "sampler_free": True, "committed": val,
            "reproduced": {"trace_+": got[0], "trace_-": got[1]},
            "signed_difference": {"trace_+": (got[0] - val) if got[0] is not None else None,
                                  "trace_-": (got[1] - val) if got[1] is not None else None},
            "bitwise_match": bool(got[0] == val and got[1] == val),
        })
    out["per_class_var_two_torsion_x"] = zvar

    # --- sampler-dependent: RUN-ICINV-p4001-degenfix only ---
    rows_by_trace = {}
    for t in traces:
        rows_by_trace[t] = ri.measure_class(classes[t], FB_M2, FB_M3,
                                            REPRO_WINDOW, N_TARGETS, seed)
    sampler_dep = {}
    for fn, key, committed in (("decomp_efficiency_m2", "eff_m2", 0.7815),
                               ("decomp_efficiency_m3", "eff_m3", 0.098),
                               ("decomp_rate_m2_RAW_confounded_by_order",
                                "rate_m2", 0.2825),
                               ("decomp_rate_m3_RAW_confounded_by_order",
                                "rate_m3", 0.107)):
        g = {t: [r[key] for r in rows_by_trace[t]] for t in traces}
        o, nm, pv = ex.permutation_null(g, iterations=2000, seed=seed)
        sampler_dep[fn] = {"committed_p": committed, "reproduced_p": pv,
                           "committed_r": round(committed * 2000),
                           "reproduced_r": round(pv * 2000),
                           "raw_count_match": bool(round(pv * 2000)
                                                   == round(committed * 2000)),
                           "observed": o, "null_mean": nm}
    out["sampler_dependent_degenfix"] = sampler_dep
    out["sampler_dependent_note"] = (
        "Only RUN-ICINV-p4001-degenfix is a reproduction target for today's "
        "code. RUN-ICINV-p4001-a's decomposition rows used the confounded "
        "hash-and-lift `_targets` (CORR-20260807-a05e1e forbids citing them) "
        "and RUN-ICINV-p4001-uniform's used the pre-fix targets_uniform. A "
        "mismatch here is NOT instrument instability and does NOT stop the run.")

    free_ok = all(c.get("raw_count_match", c.get("bitwise_match"))
                  for c in out["checks"])
    out["sampler_free_all_reproduced"] = bool(free_ok)
    out["gate"] = "PASS" if free_ok else "FAIL"
    return out


# ==========================================================================
# S3: measurement
# ==========================================================================


def window_list(p: int) -> list[int]:
    """The declared liftable-density windows: p//32, p//16, p//8, p//4, p//2, p."""
    return [p // 32, p // 16, p // 8, p // 4, p // 2, p]


def functional_keys(p: int) -> list[str]:
    ws = window_list(p)
    return (["order", "full_liftable"]
            + [f"liftable_density_W{w}" for w in ws]
            + ["two_torsion_x", "sumset_m2", "sumset_m3", "sumset_eff_m2",
               "sumset_eff_m3", "decomp_rate_m2", "decomp_rate_m3",
               "decomp_efficiency_m2", "decomp_efficiency_m3", "s3_support"])


def measure_curve_row(rec, p: int, windows: list[int], cache: dict | None = None
                      ) -> dict:
    """Every declared functional on one curve. Frozen functions only."""
    key = f"{p}:{rec.a}:{rec.b}:{FB_M2}:{FB_M3}:{N_TARGETS}:{REPRODUCTION_SEED}"
    if cache is not None and key in cache:
        return cache[key]
    E = rec.curve()
    fb2 = ex.factor_base_fixed_size(E, FB_M2)
    fb3 = ex.factor_base_fixed_size(E, FB_M3)
    tg = ex.targets_uniform(E, rec.order, N_TARGETS, REPRODUCTION_SEED)
    h2, t2 = ex.decomposition_rate_m2(E, fb2, tg)
    h3, t3 = ex.decomposition_rate_m3(E, fb3, tg)
    s2sz, _ = sumset_m2(E, fb2)
    s3sz, _ = sumset_m3(E, fb3)
    z = ex.two_torsion_x_count(p, rec.a, rec.b)
    full = len(ex.factor_base_window(E, p))
    rate2 = h2 / t2 if t2 else float("nan")
    rate3 = h3 / t3 if t3 else float("nan")
    row = {
        "p": p, "a": rec.a, "b": rec.b, "j": rec.j, "trace": rec.trace,
        "order": rec.order, "aut_order": rec.aut_order,
        "fb_m2": len(fb2), "fb_m3": len(fb3), "n_targets": len(tg),
        "hits_m2": h2, "hits_m3": h3,
        "full_liftable": full, "two_torsion_x": z,
        "sumset_m2": s2sz, "sumset_m3": s3sz,
        "sumset_eff_m2": s2sz / ex.max_sums(len(fb2), 2),
        "sumset_eff_m3": s3sz / ex.max_sums(len(fb3), 3),
        "decomp_rate_m2": rate2, "decomp_rate_m3": rate3,
        "decomp_efficiency_m2": ex.decomposition_efficiency(
            rate2, rec.order, len(fb2), 2),
        "decomp_efficiency_m3": ex.decomposition_efficiency(
            rate3, rec.order, len(fb3), 3),
        "s3_support": ex.s3_monomial_support(p, rec.a, rec.b),
    }
    for w in windows:
        row[f"liftable_density_W{w}"] = ex.liftable_density(E, w)
    row["liftable_identity_holds"] = bool(
        full == ex.liftable_count_identity(rec.order, z))
    if cache is not None:
        cache[key] = row
    return row


def measure_pool(pool: Pool, cache: dict | None = None,
                 progress=None) -> tuple[list[dict], dict]:
    windows = window_list(pool.p)
    rows = []
    for i, rec in enumerate(pool.recs):
        rows.append(measure_curve_row(rec, pool.p, windows, cache))
        if progress and i % 100 == 0:
            progress(i, pool.n)
    values = {}
    for k in functional_keys(pool.p):
        values[k] = np.array([float(r[k]) for r in rows], dtype=np.float64)
    return rows, values


def ctrl_twist(pool: Pool, rows: list[dict]) -> dict:
    """CTRL-TWIST: equal class sizes and identical SORTED two_torsion_x
    multisets across every pooled {t, -t} pair. Tests HEUR-INSTR-2 directly."""
    by_trace: dict[int, list[int]] = {}
    for r in rows:
        by_trace.setdefault(r["trace"], []).append(r["two_torsion_x"])
    pairs, unpaired = [], []
    seen = set()
    for t in pool.traces:
        if t in seen or -t in seen:
            continue
        if -t in by_trace:
            seen.add(t)
            seen.add(-t)
            zp, zm = sorted(by_trace[t]), sorted(by_trace[-t])
            pairs.append({
                "pair": [int(t), int(-t)],
                "size_plus": len(zp), "size_minus": len(zm),
                "sizes_equal": len(zp) == len(zm),
                "sorted_multiset_equal": zp == zm,
                "composition_plus": {str(v): zp.count(v) for v in sorted(set(zp))},
                "composition_minus": {str(v): zm.count(v) for v in sorted(set(zm))},
                "sorted_z_sha256_plus": _sha(",".join(map(str, zp))),
                "sorted_z_sha256_minus": _sha(",".join(map(str, zm))),
            })
        else:
            unpaired.append(int(t))
    ok = all(pr["sizes_equal"] and pr["sorted_multiset_equal"] for pr in pairs)
    return {"pairs": pairs, "unpaired_traces": unpaired,
            "all_pairs_agree": bool(ok),
            "verdict": "HEUR-INSTR-2 CONSISTENT" if ok else
                       "HEUR-INSTR-2 FALSIFIED -- twist blocking is UNJUSTIFIED "
                       "and must be replaced by explicit |D| = |t^2 - 4p| matching",
            "on_failure_scope": "Only twist blocking (R1_TWIST, R6) loses its "
                                "stated basis; the rest of the ladder is unaffected."}


# ==========================================================================
# S4: the ladder
# ==========================================================================


def _partition_of(rung_geometry: dict) -> frozenset:
    """The block partition as a set of trace-sets, IGNORING block ids.

    Two rungs realize the same partition when their blocks hold the same
    classes, whatever order the block ids happen to run in. Comparing the
    id-KEYED composition dict instead reported R5_PERCLASS as not collapsed
    onto R4_NBAND_w4 at POOL_A, POOL_B and POOL_D, where both rungs realize the
    identical all-singleton partition and differ only in whether the ids are
    ordered by N band or by trace (RUN-INSTR-85b102-pool{A-c,B-b,D}, whose
    `_collapsed_onto_predecessor` field is superseded by the collapse audit in
    RUN-INSTR-85b102-scorecard-c).
    """
    return frozenset(frozenset(v) for v in
                     rung_geometry["block_composition_by_trace"].values())


def s4_ladder(pool: Pool, values: dict, B: int = PRIMARY_B,
              progress=None) -> dict:
    """Every (pool, functional, rung) cell, both statistics.

    T_obs, empirical and closed-form null means with their residual in
    Monte-Carlo standard errors, both tails' raw counts and p-values, ratio R,
    Delta_max, the nuisance budget and the degeneracy flag. A bare blocked
    p-value is the exact failure mode this contract exists to end, so no number
    here is emitted without its rung geometry.
    """
    keys = functional_keys(pool.p)
    rung_geo, layouts, blocks = {}, {}, {}
    for rung in RUNGS:
        b, real = blocks_array(pool, rung)
        blocks[rung] = b
        rung_geo[rung] = real
        layouts[rung] = _Layout(pool.labels, b)

    cells: dict = {}
    nuisance: dict = {}
    for rung in RUNGS:
        for fkey in keys:
            seed = derive_seed("LADDER", pool.name, rung, fkey, 0, 0)
            d = blocked_permutation_null_both(values[fkey], pool.labels,
                                              blocks[rung], B, seed,
                                              layout=layouts[rung])
            cf_w = closed_form_null_mean(values[fkey], pool.labels,
                                         blocks[rung], "weighted")
            cf_u = closed_form_null_mean(values[fkey], pool.labels,
                                         blocks[rung], "unweighted")
            for stat, cf in (("weighted", cf_w), ("unweighted", cf_u)):
                s = dict(d[stat])
                s["closed_form_null_mean"] = cf
                if cf is None:
                    s["closed_form_minus_empirical"] = None
                    s["closed_form_relative_residual"] = None
                    s["residual_in_mc_standard_errors"] = None
                    s["residual_in_mc_se_meaningful"] = False
                    s["closed_form_applicability"] = (
                        "not_applicable -- some class straddles blocks")
                else:
                    absres = cf - s["empirical_null_mean"]
                    s["closed_form_minus_empirical"] = absres
                    s["closed_form_relative_residual"] = (
                        absres / s["empirical_null_mean"]
                        if s["empirical_null_mean"] != 0.0 else None)
                    s["closed_form_applicability"] = "exact"
                    meaningful = (s["mc_standard_error"] > 0
                                  and not s["null_is_point_mass_within_fp_noise"])
                    s["residual_in_mc_se_meaningful"] = bool(meaningful)
                    s["residual_in_mc_standard_errors"] = (
                        absres / s["mc_standard_error"]
                        if s["mc_standard_error"] > 0 else None)
                s["variance_ratio_R_empirical"] = (
                    s["T_obs"] / s["empirical_null_mean"]
                    if s["empirical_null_mean"] not in (0.0,) else None)
                s["variance_ratio_R_closed_form"] = (
                    s["T_obs"] / cf if cf not in (None, 0.0) else None)
                s["delta_max_N"] = rung_geo[rung]["delta_max_N"]
                s["degenerate"] = rung_geo[rung]["degenerate"]
                s["n_blocks"] = rung_geo[rung]["n_blocks"]
                cells[f"{pool.name}|{fkey}|{rung}|{stat}|B{B}"] = s
            if fkey == "order":
                nuisance[rung] = {
                    "weighted": cells[f"{pool.name}|order|{rung}|weighted|B{B}"]
                    ["empirical_null_mean"],
                    "unweighted": cells[f"{pool.name}|order|{rung}|unweighted|B{B}"]
                    ["empirical_null_mean"],
                    "weighted_closed_form":
                        cells[f"{pool.name}|order|{rung}|weighted|B{B}"]
                        ["closed_form_null_mean"],
                    "T_obs_weighted":
                        cells[f"{pool.name}|order|{rung}|weighted|B{B}"]["T_obs"],
                }
        if progress:
            progress(rung)

    non_degenerate_ladder = [r for r in N_LADDER
                             if not rung_geo[r]["degenerate"]]
    finest = (min(non_degenerate_ladder,
                  key=lambda r: (rung_geo[r]["delta_max_N"], N_LADDER.index(r)))
              if non_degenerate_ladder else None)
    non_deg_all = [r for r in RUNGS if not rung_geo[r]["degenerate"]]
    finest_all = (min(non_deg_all, key=lambda r: (rung_geo[r]["delta_max_N"],
                                                  RUNGS.index(r)))
                  if non_deg_all else None)

    gap = {}
    for fkey in keys:
        for stat in ("weighted", "unweighted"):
            free = cells[f"{pool.name}|{fkey}|R0_FREE|{stat}|B{B}"]
            row = {"R0_FREE": {"p_lower": free["p_lower"],
                               "R": free["variance_ratio_R_empirical"],
                               "delta_max_N": free["delta_max_N"],
                               "nuisance_budget": nuisance["R0_FREE"][stat]}}
            if finest:
                fin = cells[f"{pool.name}|{fkey}|{finest}|{stat}|B{B}"]
                row["finest_non_degenerate"] = {
                    "rung": finest, "p_lower": fin["p_lower"],
                    "R": fin["variance_ratio_R_empirical"],
                    "delta_max_N": fin["delta_max_N"],
                    "nuisance_budget": nuisance[finest][stat]}
            gap[f"{fkey}|{stat}"] = row

    monotone = {}
    for fkey in keys:
        for stat in ("weighted", "unweighted"):
            seq = []
            for r in N_LADDER:
                c = cells[f"{pool.name}|{fkey}|{r}|{stat}|B{B}"]
                seq.append({"rung": r, "delta_max_N": c["delta_max_N"],
                            "R": c["variance_ratio_R_empirical"],
                            "degenerate": c["degenerate"]})
            vals = [s["R"] for s in seq if s["R"] is not None]
            rises = all(b >= a - 1e-12 for a, b in zip(vals, vals[1:]))
            monotone[f"{fkey}|{stat}"] = {
                "sequence": seq,
                "ratio_rises_monotonically_along_N_ladder": bool(rises),
                "verdict": ("MONOTONE RISE" if rises else
                            "NON-MONOTONE -- reportable outcome, not a failure "
                            "of the clause (see what_non_decay_means)")}

    dmax = [rung_geo[r]["delta_max_N"] for r in N_LADDER]
    nb = [nuisance[r]["weighted"] for r in N_LADDER]
    collapsed = {}
    for i in range(1, len(N_LADDER)):
        prev, cur = N_LADDER[i - 1], N_LADDER[i]
        collapsed[cur] = (_partition_of(rung_geo[cur])
                          == _partition_of(rung_geo[prev]))

    return {
        "stage": "S4", "pool": pool.name, "B": B,
        "functionals": keys, "rungs": list(RUNGS),
        "rung_geometry": rung_geo,
        "cells": cells,
        "nuisance_budget_by_rung": nuisance,
        "finest_non_degenerate_rung_N_ladder": finest,
        "finest_non_degenerate_rung_all_rungs": finest_all,
        "contamination_gap": gap,
        "monotonicity": monotone,
        "delta_max_along_N_ladder": dict(zip(N_LADDER, dmax)),
        "delta_max_non_increasing": bool(
            all(b <= a for a, b in zip(dmax, dmax[1:]))),
        "nuisance_budget_along_N_ladder": dict(zip(N_LADDER, nb)),
        "nuisance_non_increasing": bool(
            all(b <= a + 1e-9 for a, b in zip(nb, nb[1:]))),
        "collapsed_onto_predecessor": collapsed,
    }


# ==========================================================================
# S5: the control objects
# ==========================================================================


def s5_controls(pool: Pool, values: dict, ladder: dict,
                replicates: int = CONTROL_REPLICATES, B: int = CONTROL_B,
                nullobj_functional: str = "full_liftable",
                progress=None) -> dict:
    """CTRL-NULLOBJ, CTRL-SIZE0, CTRL-POWER and CTRL-NSURR at every rung.

    Run and WRITTEN OUT before the S4 ladder table is interpreted: a decision
    rule that emits the same verdict on CTRL-NULLOBJ as on the real object
    discriminates nothing.
    """
    lo, hi = exact_binomial_interval(replicates, LEVEL, BINOMIAL_CONF)
    keys = functional_keys(pool.p)
    out: dict = {
        "stage": "S5", "pool": pool.name, "replicates": replicates, "B": B,
        "level": LEVEL,
        "exact_binomial_acceptance_interval": {
            "n": replicates, "p0": LEVEL, "confidence": BINOMIAL_CONF,
            "lo": lo, "hi": hi,
            "definition": "{k : P(X<=k) > alpha/2 and P(X>=k) > alpha/2}, "
                          "exact binomial, no normal approximation"},
        "nullobj_functional": nullobj_functional,
        "CTRL_NULLOBJ": {}, "CTRL_SIZE0": {}, "CTRL_POWER": {},
        "CTRL_NSURR": {},
    }
    blocks = {r: blocks_array(pool, r)[0] for r in RUNGS}
    geo = ladder["rung_geometry"]

    # ---------------- CTRL-NULLOBJ ----------------
    vals_no = values[nullobj_functional]
    for rung in RUNGS:
        ps, tobs = [], []
        for r in range(replicates):
            lab = null_object_labels(pool, rung, r)
            seed = derive_seed("NULLOBJ", pool.name, rung,
                               nullobj_functional, 0, r)
            d = blocked_permutation_null_both(vals_no, lab, blocks[rung], B,
                                              seed)["weighted"]
            ps.append(d["p_lower"])
            tobs.append(d["T_obs"])
        rej = sum(1 for x in ps if x <= LEVEL)
        out["CTRL_NULLOBJ"][rung] = {
            "rejections": rej, "replicates": replicates,
            "realized_size": rej / replicates,
            "inside_exact_binomial_interval": bool(lo <= rej <= hi),
            "acceptance_interval": [lo, hi],
            "min_p_lower": min(ps), "max_p_lower": max(ps),
            "mean_p_lower": sum(ps) / len(ps),
            "expected_min_of_R_uniform_draws": 1.0 / (replicates + 1),
            "resolution_floor": 1.0 / (1 + B),
            "closed_form_null_mean": "not_applicable -- synthetic classes "
                                     "straddle blocks",
            "delta_max_N": geo[rung]["delta_max_N"],
            "degenerate": geo[rung]["degenerate"],
        }
        if progress:
            progress(f"NULLOBJ {rung}")

    # ---------------- CTRL-POWER (delta = 0 row is CTRL-SIZE0) -------------
    for rung in RUNGS:
        lay = _Layout(pool.labels, blocks[rung])
        u = power_offsets(pool, blocks[rung])
        corr = within_block_corr_u_N(pool, blocks[rung], u)
        u_curve = u[pool.labels]
        curve_rows = {}
        for d_idx, delta in enumerate(EFFECT_GRID):
            ps = []
            for r in range(replicates):
                rng = np.random.default_rng(
                    derive_seed("CTRLPOWER", pool.name, rung, "synthetic",
                                d_idx, r))
                eps = rng.standard_normal(pool.n)
                Y = eps + delta * u_curve
                seed = derive_seed("CTRLPOWERPERM", pool.name, rung,
                                   "synthetic", d_idx, r)
                dd = blocked_permutation_null_both(Y, pool.labels, blocks[rung],
                                                   B, seed, layout=lay)["weighted"]
                ps.append(dd["p_lower"])
            rej = sum(1 for x in ps if x <= LEVEL)
            curve_rows[f"{delta}"] = {
                "delta_in_within_class_sd": delta,
                "rejections": rej, "replicates": replicates,
                "power": rej / replicates,
                "min_p_lower": min(ps), "mean_p_lower": sum(ps) / len(ps),
            }
            if progress:
                progress(f"POWER {rung} delta={delta}")
        powers = {float(k): v["power"] for k, v in curve_rows.items()}
        dstar = None
        for delta in EFFECT_GRID:
            if delta > 0 and powers[delta] >= 0.80:
                dstar = delta
                break
        two_class = (geo[rung]["blocks_with_ge_3_classes"] == 0
                     and geo[rung]["blocks_with_ge_2_classes"] > 0)
        out["CTRL_POWER"][rung] = {
            "curve": curve_rows, "delta_star": dstar,
            "delta_star_definition": "smallest grid delta with power >= 0.80",
            "two_class_block": bool(two_class),
            "within_block_corr_u_N": corr,
            "class_offsets_u": {str(pool.traces[ci]): float(u[ci])
                                for ci in range(pool.K)},
            "delta_max_N": geo[rung]["delta_max_N"],
            "degenerate": geo[rung]["degenerate"],
            "nuisance_budget_weighted":
                ladder["nuisance_budget_by_rung"][rung]["weighted"],
        }
        z = curve_rows["0.0"]
        out["CTRL_SIZE0"][rung] = {
            "rejections": z["rejections"], "replicates": replicates,
            "realized_size": z["power"],
            "inside_exact_binomial_interval": bool(lo <= z["rejections"] <= hi),
            "acceptance_interval": [lo, hi],
            "degenerate": geo[rung]["degenerate"],
            "forced_by_degeneracy": bool(geo[rung]["degenerate"]),
            "note": ("At a DEGENERATE rung the within-block label permutation "
                     "is the identity, so p_lower is exactly 1.0 by "
                     "construction and the realized size is forced to 0. That "
                     "is a property of the declared rung, not a calibration "
                     "failure; the rung reports no test either way."
                     if geo[rung]["degenerate"] else ""),
        }

    for rung in RUNGS:
        free = out["CTRL_POWER"]["R0_FREE"]["curve"]
        out["CTRL_POWER"][rung]["power_cost_vs_R0_FREE"] = {
            k: free[k]["power"] - v["power"]
            for k, v in out["CTRL_POWER"][rung]["curve"].items()}

    # ---------------- CTRL-NSURR ----------------
    exact_slopes = {"order": 1.0, "full_liftable": 0.5}
    for fkey in keys:
        v = values[fkey]
        v_f = statistic_weighted(v, pool.labels)          # pooled within-class
        if fkey in exact_slopes:
            slope, se, label = exact_slopes[fkey], 0.0, "EXACT"
        else:
            slope, se = ols_slope_on_N(pool, v)
            label = "ESTIMATED"
        Nc = np.array([pool.class_orders[ci] for ci in pool.labels],
                      dtype=np.float64)
        per_rung = {}
        for rung in RUNGS:
            ratios = []
            for r in range(NSURR_REPLICATES):
                rng = np.random.default_rng(
                    derive_seed("NSURR", pool.name, rung, fkey, 0, r))
                eps = rng.standard_normal(pool.n)
                Y = slope * Nc + math.sqrt(max(v_f, 0.0)) * eps
                t_obs = statistic_weighted(Y, pool.labels)
                e_t = closed_form_null_mean(Y, pool.labels, blocks[rung],
                                            "weighted")
                ratios.append(t_obs / e_t if e_t else float("nan"))
            fin = [x for x in ratios if not math.isnan(x)]
            r_surr = (sum(fin) / len(fin)) if fin else float("nan")
            cell = ladder["cells"][f"{pool.name}|{fkey}|{rung}|weighted|B"
                                   f"{ladder['B']}"]
            r_f = cell["variance_ratio_R_empirical"]
            per_rung[rung] = {
                "R_surrogate": r_surr,
                "R_functional": r_f,
                "excess_E": (r_f / r_surr) if (r_f is not None and r_surr
                                               and not math.isnan(r_surr)
                                               and r_surr != 0) else None,
                "delta_max_N": ladder["rung_geometry"][rung]["delta_max_N"],
                "replicates": NSURR_REPLICATES,
            }
        out["CTRL_NSURR"][fkey] = {
            "slope": slope, "slope_label": label, "slope_standard_error": se,
            "within_class_variance_v_f": v_f,
            "null_mean_source": "closed_form (exact under the coarsening "
                                "invariant); the surrogate's classes lie "
                                "inside blocks by construction",
            "by_rung": per_rung,
        }
        if progress:
            progress(f"NSURR {fkey}")

    out["uncalibrated_rungs"] = [
        r for r in RUNGS
        if not out["CTRL_NULLOBJ"][r]["inside_exact_binomial_interval"]
        or not out["CTRL_SIZE0"][r]["inside_exact_binomial_interval"]]
    return out


# ==========================================================================
# S0: pool freeze and provenance
# ==========================================================================


def s0_freeze(repo: str, progress=None) -> dict:
    """Freeze the four declared pools BEFORE any functional is measured.

    This is the quantifier order the contract exists to enforce: choosing the
    pool after seeing the functional is the weaker statement and is forbidden.
    Terminates the run on any census failure.
    """
    out: dict = {"stage": "S0", "primes": {}, "pools": {}, "rung_table": {}}
    store = {}
    for p in (4001, 6007):
        if progress:
            progress(f"enumerating p={p}")
        classes = ic.isogeny_classes(p)
        cens = ic.class_census(p, classes)
        fails = [c for c in cens if not c.agrees]
        store[p] = classes
        ordinary = sorted(((len(v), t) for t, v in classes.items()
                           if t % p != 0), reverse=True)
        out["primes"][str(p)] = {
            "prime": p,
            "curves_enumerated": sum(len(v) for v in classes.values()),
            "traces_total": len(classes),
            "ordinary_traces": len(ordinary),
            "census_traces_checked": len(cens),
            "census_failures": len(fails),
            "failed_traces": [c.trace for c in fails],
            "census_agrees": bool(not fails),
            "four_sqrt_p_bound": 4.0 * math.sqrt(p),
        }
    if any(v["census_failures"] for v in out["primes"].values()):
        out["gate"] = "FAIL"
        out["stop_reason"] = ("class_census reports a failure; enumeration is "
                              "incomplete and the run is INVALID, not negative")
        return out
    out["gate"] = "PASS"

    tA, cA, _ = ri.pick_classes(4001, 3)
    tB, cB, _ = ri.pick_classes(4001, 11)
    tD, cD, _ = ri.pick_classes(6007, 11)
    tracesC, eligibleC = poolc_traces(4001, store[4001], 12)
    out["POOL_C_draw"] = {
        "eligible_ordinary_traces_with_size_ge_20": len(eligibleC),
        "eligible_traces": eligibleC,
        "seed": derive_seed("POOLC", "POOL_C", "NONE", "NONE", 0, 0),
        "seed_tuple": {"L": "POOLC", "P": "POOL_C", "Rg": "NONE", "F": "NONE",
                       "d": 0, "r": 0, "master": MASTER_SEED},
        "drawn_traces_in_draw_order": tracesC,
        "draw_rule": "numpy.random.default_rng(seed).choice(sorted(eligible), "
                     "size=12, replace=False)",
    }

    specs = [
        ("POOL_A", 4001, [tA] + cA,
         "harness/run_icinv.py::pick_classes(4001, n_control=3)"),
        ("POOL_B", 4001, [tB] + cB,
         "harness/run_icinv.py::pick_classes(4001, n_control=11)"),
        ("POOL_C", 4001, tracesC,
         "12 ordinary traces drawn uniformly without replacement from all "
         "ordinary traces with class size >= 20, declared seed derivation, "
         "arm label POOLC"),
        ("POOL_D", 6007, [tD] + cD,
         "harness/run_icinv.py::pick_classes(6007, n_control=11)"),
    ]
    pools = {}
    for name, p, traces, rule in specs:
        pool = build_pool(name, p, traces, store[p], rule)
        pools[name] = pool
        cens = {c.trace: c for c in ic.class_census(p, store[p])}
        classes_tbl = []
        for ci, t in enumerate(pool.traces):
            recs = store[p][t]
            hist: dict[str, int] = {}
            for r in recs:
                hist[str(r.aut_order)] = hist.get(str(r.aut_order), 0) + 1
            c = cens[t]
            classes_tbl.append({
                "class_index": ci, "trace": int(t), "N": int(recs[0].order),
                "size": len(recs), "aut_order_histogram": hist,
                "census_observed_weighted": c.observed_weighted,
                "census_predicted_weighted": c.predicted_weighted,
                "census_agrees": bool(c.agrees),
                "discriminant_D": int(t * t - 4 * p),
                "status": "kept",
                "Var_two_torsion_x": None,
                "sorted_z_sha256": None,
                "note": "Var(z) and the sorted-z hash are filled at stage S3; "
                        "measuring them here would violate the S0 freeze order.",
            })
        out["pools"][name] = {
            "name": name, "prime": p, "rule": rule,
            "traces_in_pooled_order": [int(t) for t in pool.traces],
            "n_curves": pool.n, "n_classes": pool.K,
            "class_sizes": pool.class_sizes,
            "class_orders_N": pool.class_orders,
            "delta_pool": pool.delta_pool,
            "four_sqrt_p": 4.0 * math.sqrt(p),
            "delta_pool_over_four_sqrt_p": pool.delta_pool / (4.0 * math.sqrt(p)),
            "delta_pool_over_p_plus_1": pool.delta_pool / (p + 1),
            "dropped_classes": pool.dropped,
            "minimum_class_size": MINIMUM_CLASS_SIZE,
            "band_widths": band_widths(pool.delta_pool),
            "classes": classes_tbl,
        }
        rt = {}
        for rung in RUNGS:
            _, real = blocking(pool, rung)
            rt[rung] = real
        dmax = [rt[r]["delta_max_N"] for r in N_LADDER]
        rt["_delta_max_non_increasing_along_N_ladder"] = bool(
            all(b <= a for a, b in zip(dmax, dmax[1:])))
        rt["_collapsed_onto_predecessor"] = {
            N_LADDER[i]: (rt[N_LADDER[i]]["block_composition_by_trace"]
                          == rt[N_LADDER[i - 1]]["block_composition_by_trace"])
            for i in range(1, len(N_LADDER))}
        out["rung_table"][name] = rt

    out["_pools_object"] = pools
    out["_classes"] = store
    return out


# ==========================================================================
# tail checks and the prediction scorecard
# ==========================================================================


def tail_checks(pool: Pool, rows: list[dict], ladder: dict,
                controls: dict) -> list[dict]:
    B = ladder["B"]
    keys = ladder["functionals"]
    cells = ladder["cells"]
    checks = []

    bad = [k for k in keys
           if cells[f"{pool.name}|{k}|R5_PERCLASS|weighted|B{B}"]["p_lower"] != 1.0
           or cells[f"{pool.name}|{k}|R5_PERCLASS|unweighted|B{B}"]["p_lower"] != 1.0]
    checks.append({"check": "R5_PERCLASS p_lower EXACTLY 1.0, every functional",
                   "result": "PASS" if not bad else "FAIL",
                   "offending_functionals": bad, "tolerance": "bitwise"})

    bad = [r for r in RUNGS
           if cells[f"{pool.name}|order|{r}|weighted|B{B}"]["T_obs"] != 0.0]
    checks.append({"check": "`order` T_obs exactly 0.0 at every rung",
                   "result": "PASS" if not bad else "FAIL",
                   "offending_rungs": bad, "tolerance": "bitwise"})

    n_ok = sum(1 for r in rows if r["liftable_identity_holds"])
    checks.append({"check": "full_liftable == (order - 1 + two_torsion_x)//2 "
                            "per curve",
                   "result": "PASS" if n_ok == len(rows) else "FAIL",
                   "curves_holding": n_ok, "curves_total": len(rows),
                   "curves_failing": len(rows) - n_ok})

    exact_zero, exact_one_forced, exact_one_unexplained = [], [], []
    for k, c in cells.items():
        if c["p_lower"] == 0.0 or c["p_upper"] == 0.0:
            exact_zero.append(k)
        if c["degenerate"]:
            continue
        if c["p_lower"] == 1.0 or c["p_upper"] == 1.0:
            # A tail p-value of exactly 1.0 means the observed statistic lies
            # at or outside that end of the whole realized null support:
            # #{v >= T_obs} = B when T_obs <= min(nulls), and symmetrically.
            # That is the estimator's extreme-tail value, with the OPPOSITE
            # tail sitting at the resolution floor -- it is the separation the
            # ladder is measuring, not a counting bug. It is listed either way.
            forced = ((c["p_upper"] == 1.0 and c["T_obs_at_or_below_null_min"])
                      or (c["p_lower"] == 1.0 and c["T_obs_at_or_above_null_max"]))
            entry = {"cell": k, "T_obs": c["T_obs"],
                     "null_min": c["null_min"], "null_max": c["null_max"],
                     "p_lower": c["p_lower"], "p_upper": c["p_upper"],
                     "opposite_tail_at_resolution_floor":
                         bool(min(c["p_lower"], c["p_upper"])
                              == c["resolution_floor"])}
            (exact_one_forced if forced else exact_one_unexplained).append(entry)
    literal = "PASS" if not (exact_zero or exact_one_forced
                             or exact_one_unexplained) else "FAIL"
    checks.append({
        "check": "no p-value exactly 0.0 or 1.0 outside a degenerate rung",
        "result": literal,
        "result_literal_reading": literal,
        "exactly_zero_cells": exact_zero,
        "exactly_zero_count": len(exact_zero),
        "exactly_one_forced_by_T_obs_outside_the_null_support":
            exact_one_forced[:40],
        "exactly_one_forced_count": len(exact_one_forced),
        "exactly_one_unexplained": exact_one_unexplained,
        "implementation_defect_indicator":
            "FAIL" if (exact_zero or exact_one_unexplained) else "PASS",
        "note": "The contract's stated rationale is that the estimator makes "
                "0.0 impossible, so an observed 0.0 is an implementation "
                "defect. Both readings are reported without choosing between "
                "them: the LITERAL outcome, and a breakdown separating a tail "
                "p-value of exactly 1.0 that is FORCED because T_obs lies at "
                "or outside that end of the realized null support (the "
                "opposite tail then sits at the resolution floor) from any "
                "unexplained case. No p-value of exactly 0.0 is possible under "
                "the frozen estimator and none was observed. This check is not "
                "one of the contract's stopping rules."})

    floor = 1.0 / (1 + B)
    below = [k for k, c in cells.items() if c["p_lower"] < floor - 1e-18]
    checks.append({"check": f"smallest p_lower >= 1/(1+B) = {floor}",
                   "result": "PASS" if not below else "FAIL",
                   "offending_cells": below[:20],
                   "min_p_lower_observed": min(c["p_lower"] for c in cells.values())})

    bad, bad_pointmass, table = [], [], []
    for k in ("order", "full_liftable"):
        for r in RUNGS:
            for stat in ("weighted", "unweighted"):
                c = cells[f"{pool.name}|{k}|{r}|{stat}|B{B}"]
                res = c["residual_in_mc_standard_errors"]
                row = {"cell": f"{k}|{r}|{stat}",
                       "closed_form": c["closed_form_null_mean"],
                       "empirical": c["empirical_null_mean"],
                       "absolute_residual": c["closed_form_minus_empirical"],
                       "relative_residual": c["closed_form_relative_residual"],
                       "mc_standard_error": c["mc_standard_error"],
                       "residual_in_mc_se": res,
                       "null_is_point_mass_within_fp_noise":
                           c["null_is_point_mass_within_fp_noise"],
                       "degenerate_rung": c["degenerate"]}
                table.append(row)
                if res is not None and abs(res) > 3.0:
                    (bad_pointmass if c["null_is_point_mass_within_fp_noise"]
                     else bad).append(row)
    literal = "PASS" if not (bad or bad_pointmass) else "FAIL"
    checks.append({
        "check": "closed-form null mean within 3 MC standard errors of the "
                 "empirical mean for `order` and `full_liftable` at every rung",
        "result": literal,
        "result_literal_reading": literal,
        "offending_with_a_non_degenerate_null": bad,
        "offending_only_where_the_null_is_a_floating_point_point_mass":
            bad_pointmass,
        "genuine_disagreement_indicator": "FAIL" if bad else "PASS",
        "full_table": table,
        "note": "Reported in both readings, choosing neither. At a DEGENERATE "
                "rung the within-block label permutation is the identity, so "
                "every null draw is bitwise T_obs and the realized null is a "
                "point mass; np.mean's pairwise summation of B identical "
                "doubles then reports a mean one ulp off, giving a "
                "'Monte-Carlo standard error' of one-ulp-over-sqrt(B). "
                "Dividing a one-ulp difference by that produces a large "
                "dimensionless number from an exact agreement -- the absolute "
                "and relative residual columns show the agreement is at the "
                "last bit. Cells with a genuinely non-degenerate null are "
                "listed separately and are the ones that could indicate a real "
                "disagreement."})

    worst = {}
    for r in RUNGS:
        no = controls["CTRL_NULLOBJ"][r]
        worst[r] = {"min_p_lower": no["min_p_lower"],
                    "expected_about": no["expected_min_of_R_uniform_draws"],
                    "impossible_below": no["resolution_floor"],
                    "consistent": bool(no["min_p_lower"]
                                       >= no["resolution_floor"] - 1e-18)}
    checks.append({"check": "CTRL-NULLOBJ most extreme replicate consistent "
                            "with 200 Uniform(0,1) draws",
                   "result": "PASS" if all(v["consistent"] for v in worst.values())
                             else "FAIL",
                   "by_rung": worst})

    bad = [k for k, c in cells.items()
           if not (c["t_obs_shape_invariance_check"]["weighted_shape_invariant"]
                   and c["t_obs_shape_invariance_check"]
                   ["unweighted_shape_invariant"])]
    checks.append({"check": "T_obs is invariant to the array shape it is "
                            "computed in (self-check for the defect that "
                            "produced RUN-INSTR-85b102-poolB)",
                   "result": "PASS" if not bad else "FAIL",
                   "offending_cells": bad[:20],
                   "offending_count": len(bad),
                   "cells_checked": len(cells)})

    dmax = [ladder["rung_geometry"][r]["delta_max_N"] for r in N_LADDER]
    checks.append({"check": "Delta_max non-increasing along R0 -> R2 -> R3 -> "
                            "R4 -> R5",
                   "result": "PASS" if all(b <= a for a, b in zip(dmax, dmax[1:]))
                             else "FAIL",
                   "sequence": dict(zip(N_LADDER, dmax)),
                   "collapsed": ladder["collapsed_onto_predecessor"]})
    return checks


def _fmt(x):
    return None if x is None else (float(x) if isinstance(x, (int, float)) else x)


def prediction_scorecard(bundles: dict, s1: dict, s2: dict) -> dict:
    """Score P1-P8 MET / NOT MET / NOT DECIDABLE with the deciding number.

    P1 and the POOL-A rows of P2-P6 are IN-SAMPLE reproductions: the committed
    run records were open while the closed form was written. Everything at
    POOL-B, POOL-C and POOL-D, the whole power and size study, the
    excess-over-surrogate curves, P7 and the p = 6007 twist check are
    OUT-OF-SAMPLE.
    """
    sc: dict = {"experiment_id": EXPERIMENT_ID, "predictions": {}}

    def get(pool, fkey, rung, stat="unweighted"):
        b = bundles.get(pool)
        if not b:
            return None
        L = b["ladder"]
        return L["cells"].get(f"{pool}|{fkey}|{rung}|{stat}|B{L['B']}")

    # ---- P1 ----
    a_free = get("POOL_A", "full_liftable", "R0_FREE")
    if a_free is None:
        sc["predictions"]["P1"] = {"score": "NOT DECIDABLE",
                                   "reason": "POOL_A not run",
                                   "sample": "IN-SAMPLE"}
    else:
        t_obs = a_free["T_obs"]
        cf = a_free["closed_form_null_mean"]
        rate = cf / (4001 ** 2)
        rel = (rate - COMMITTED_NULL_MEAN_RATE) / COMMITTED_NULL_MEAN_RATE
        dt = t_obs - COMMITTED_T_OBS
        sc["predictions"]["P1"] = {
            "statement": "closed-form reproduction of the committed "
                         "free-permutation null mean and T_obs at POOL-A",
            "sample": "IN-SAMPLE",
            "deciding_numbers": {
                "T_obs_count_units": t_obs, "committed_T_obs": COMMITTED_T_OBS,
                "signed_difference": dt, "tolerance": 1e-9,
                "closed_form_null_mean_count_units": cf,
                "closed_form_null_mean_rate_units": rate,
                "committed_null_mean_rate_units": COMMITTED_NULL_MEAN_RATE,
                "relative_residual": rel, "relative_tolerance": 1e-3,
                "frozen_prediction_E_T_pi_R0_FREE": 165.8028717},
            "score": "MET" if abs(dt) <= 1e-9 and abs(rel) <= 1e-3 else "NOT MET",
        }

    # ---- P2 ----
    a_tw = get("POOL_A", "full_liftable", "R1_TWIST")
    if a_tw is None:
        sc["predictions"]["P2"] = {"score": "NOT DECIDABLE",
                                   "reason": "POOL_A not run", "sample": "IN-SAMPLE"}
    else:
        cf = a_tw["closed_form_null_mean"]
        ratio = a_tw["T_obs"] / cf
        floor = a_tw["resolution_floor"]
        sc["predictions"]["P2"] = {
            "statement": "twist-pair blocking at POOL-A: E[T_pi|twist] = "
                         "153.8651 count^2, ratio 1/617.0, p-hat REMAINS at the "
                         "resolution floor. Contradicts IDEA-20260807-34754f "
                         "prediction 1 (honest prior 0.75) by arithmetic derived "
                         "before any run.",
            "sample": "IN-SAMPLE",
            "deciding_numbers": {
                "E_T_pi_twist_closed_form": cf,
                "frozen_prediction": 153.8651,
                "signed_difference": cf - 153.8651,
                "ratio_T_over_E": ratio, "one_over_ratio": 1.0 / ratio,
                "frozen_prediction_one_over_ratio": 617.0,
                "p_lower": a_tw["p_lower"], "resolution_floor": floor,
                "p_lower_at_floor": bool(a_tw["p_lower"] == floor),
                "free_one_over_ratio": (1.0 / (a_free["T_obs"]
                                               / a_free["closed_form_null_mean"])
                                        if a_free else None)},
            "score": "MET" if (abs(cf - 153.8651) < 0.01
                               and abs(1.0 / ratio - 617.0) < 1.0
                               and a_tw["p_lower"] == floor) else "NOT MET",
        }

    # ---- P3 ----
    bA = bundles.get("POOL_A")
    if bA is None:
        sc["predictions"]["P3"] = {"score": "NOT DECIDABLE",
                                   "reason": "POOL_A not run", "sample": "IN-SAMPLE"}
    else:
        L = bA["ladder"]
        finest = L["finest_non_degenerate_rung_N_ladder"]
        cell = get("POOL_A", "full_liftable", finest) if finest else None
        widths = band_widths(bA["pool"].delta_pool)
        nondeg = [r for r in RUNGS
                  if not L["rung_geometry"][r]["degenerate"]]
        clears = [r for r in nondeg
                  if get("POOL_A", "full_liftable", r)["p_lower"] > 0.05]
        sc["predictions"]["P3"] = {
            "statement": "finest non-degenerate N band on full_liftable at "
                         "POOL-A: still far below 1, p-hat still at the floor, "
                         "and the functional clears 0.05 at NO non-degenerate "
                         "rung because N is injective in the trace.",
            "sample": "IN-SAMPLE",
            "deciding_numbers": {
                "finest_non_degenerate_rung": finest,
                "realized_band_width_w2": widths["R2_NBAND_w2"],
                "frozen_prediction_band_width": 24,
                "band_width_rule_realized": "max(2, ceil(Delta_pool/2))",
                "realized_delta_max_N": (L["rung_geometry"][finest]["delta_max_N"]
                                         if finest else None),
                "frozen_prediction_delta_max_N": 12,
                "realized_E_T_pi": cell["closed_form_null_mean"] if cell else None,
                "frozen_prediction_E_T_pi": 9.0279,
                "realized_one_over_ratio": (
                    cell["closed_form_null_mean"] / cell["T_obs"] if cell else None),
                "frozen_prediction_one_over_ratio": 36.2,
                "p_lower_at_finest": cell["p_lower"] if cell else None,
                "resolution_floor": cell["resolution_floor"] if cell else None,
                "non_degenerate_rungs_clearing_0.05": clears},
            "realization_note":
                "THE DECLARED WIDTH RULE AND THE FROZEN ILLUSTRATION DISAGREE, "
                "AND THIS IS RECORDED RATHER THAN RESOLVED. The rule "
                "w2 = max(2, ceil(Delta_pool/2)) realizes 30 at POOL-A, not the "
                "24 the frozen prediction's arithmetic used, so the realized "
                "R2 blocks are {t=30,t=18},{t=-18},{t=-30} rather than "
                "{t=30,t=18},{t=-18,t=-30}. Delta_max = 12 is unchanged. The "
                "numeric sub-claims E[T_pi] = 9.0279 and ratio 1/36.2 are "
                "therefore evaluated against a partition the declared rule does "
                "not produce; the substantive sub-claim (ratio far below 1, "
                "p-hat at the floor, no non-degenerate rung clears 0.05) is "
                "evaluated on the realized partition. No width was retuned.",
            "score": ("MET" if (cell is not None and not clears
                                and cell["p_lower"] == cell["resolution_floor"])
                      else "NOT MET"),
        }

    # ---- P4 ----
    p_off, r_emp_off, r_cf_off = [], [], []
    cells_checked = 0
    max_dev_emp = max_dev_cf = 0.0
    for pname, b in bundles.items():
        L = b["ladder"]
        for k in L["functionals"]:
            for stat in ("weighted", "unweighted"):
                c = L["cells"][f"{pname}|{k}|R5_PERCLASS|{stat}|B{L['B']}"]
                cells_checked += 1
                if c["p_lower"] != 1.0:
                    p_off.append(f"{pname}|{k}|{stat}|p_lower={c['p_lower']!r}")
                if c["T_obs"] == 0.0:
                    continue                       # `order`: ratio is 0/0
                for key, bucket in (("variance_ratio_R_empirical", r_emp_off),
                                    ("variance_ratio_R_closed_form", r_cf_off)):
                    rr = c[key]
                    if rr is None or rr == 1.0:
                        continue
                    bucket.append({"cell": f"{pname}|{k}|{stat}", "R": rr,
                                   "R_minus_1": rr - 1.0})
                    if key.endswith("empirical"):
                        max_dev_emp = max(max_dev_emp, abs(rr - 1.0))
                    else:
                        max_dev_cf = max(max_dev_cf, abs(rr - 1.0))
    sub = {
        "p_hat_exactly_1.0_bitwise":
            {"score": "MET" if not p_off else "NOT MET",
             "cells_checked": cells_checked, "violations": p_off},
        "ratio_exactly_1_bitwise_against_the_EMPIRICAL_null_mean":
            {"score": "MET" if not r_emp_off else "NOT MET",
             "violation_count": len(r_emp_off),
             "max_abs_R_minus_1": max_dev_emp,
             "violations": r_emp_off[:10]},
        "ratio_exactly_1_bitwise_against_the_CLOSED_FORM_null_mean":
            {"score": "MET" if not r_cf_off else "NOT MET",
             "violation_count": len(r_cf_off),
             "max_abs_R_minus_1": max_dev_cf,
             "violations": r_cf_off[:10]},
    }
    literal4 = ("MET" if not (p_off or r_emp_off or r_cf_off) else "NOT MET")
    sc["predictions"]["P4"] = {
        "statement": "R5_PERCLASS: p-hat EXACTLY 1.0 and ratio exactly 1, every "
                     "functional, every pool. Zero tolerance.",
        "sample": "IN-SAMPLE at POOL-A, OUT-OF-SAMPLE at POOL-B/C/D",
        "score": literal4,
        "sub_clauses": sub,
        "deciding_numbers": {
            "pools_scored": sorted(bundles),
            "cells_checked": cells_checked,
            "p_hat_violations": len(p_off),
            "ratio_violations_vs_empirical_mean": len(r_emp_off),
            "ratio_violations_vs_closed_form": len(r_cf_off),
            "max_abs_R_minus_1_vs_empirical_mean": max_dev_emp,
            "max_abs_R_minus_1_vs_closed_form": max_dev_cf},
        "decomposition_note":
            "REPORTED AS TWO SUB-CLAUSES BECAUSE THEY FAIL AND PASS "
            "DIFFERENTLY, AND THE EXECUTOR SCORES BOTH RATHER THAN CHOOSING. "
            "The p-hat clause is met at zero tolerance: p_lower is bitwise 1.0 "
            "in every cell checked, which is also the contract's stopping rule "
            "and its tail check, and both passed at all four pools. The ratio "
            "clause is not met bitwise: R = T_obs / null_mean comes out 1 to "
            "within one or two units in the last place. The cause is the "
            "DENOMINATOR, not the test -- at a degenerate rung all B null draws "
            "are bitwise identical, and numpy's pairwise summation of B "
            "identical doubles divided by B does not return that double "
            "exactly, so the empirical mean sits an ulp off T_obs. The "
            "closed-form denominator is computed by the definitional two-pass "
            "route and lands an ulp off in a smaller number of cells. Both "
            "counts and the maximum deviation are given above so a reviewer can "
            "judge the clause rather than take a verdict."}

    # ---- P5 ----
    tw = {}
    for pname, b in bundles.items():
        tw[pname] = {"prime": b["pool"].p,
                     "all_pairs_agree": b["twist"]["all_pairs_agree"],
                     "pairs": b["twist"]["pairs"],
                     "unpaired_traces": b["twist"]["unpaired_traces"]}
    primes = {b["pool"].p for b in bundles.values()}
    sc["predictions"]["P5"] = {
        "statement": "twist-invariance of the 2-torsion x-count: the sorted "
                     "vector over class t equals that over class -t for every "
                     "pooled pair, at both primes. At POOL-A this predicts 66 "
                     "curves with z=3 and 72 with z=1 in each of traces 30 and "
                     "-30, and 42 with z=3 and 56 with z=1 in each of 18, -18.",
        "sample": "IN-SAMPLE at POOL-A (forced by committed means, sizes and "
                  "'distinct values: 2'), OUT-OF-SAMPLE at p = 6007",
        "deciding_numbers": tw,
        "primes_covered": sorted(primes),
        "score": ("MET" if all(v["all_pairs_agree"] for v in tw.values())
                  else "NOT MET") if len(primes) == 2 else
                 ("NOT DECIDABLE" if not tw else
                  ("MET (ONE PRIME ONLY)" if all(v["all_pairs_agree"]
                                                 for v in tw.values())
                   else "NOT MET"))}

    # ---- P6 ----
    if bA is None:
        sc["predictions"]["P6"] = {"score": "NOT DECIDABLE",
                                   "reason": "POOL_A not run", "sample": "IN-SAMPLE"}
    else:
        g = bA["ladder"]["rung_geometry"]["R6_TWIST_AND_NBAND_w2"]
        w2 = band_widths(bA["pool"].delta_pool)["R2_NBAND_w2"]
        min2t = min(2 * abs(t) for t in bA["pool"].traces)
        c = get("POOL_A", "full_liftable", "R6_TWIST_AND_NBAND_w2")
        sc["predictions"]["P6"] = {
            "statement": "composition of twist blocking with N banding at POOL-A "
                         "is DEGENERATE: every intersection block holds exactly "
                         "one class and the composed rung is the identity "
                         "permutation with p-hat = 1.0.",
            "sample": "IN-SAMPLE",
            "deciding_numbers": {"degenerate": g["degenerate"],
                                 "n_blocks": g["n_blocks"],
                                 "n_classes": bA["pool"].K,
                                 "blocks_with_ge_2_classes":
                                     g["blocks_with_ge_2_classes"],
                                 "w2": w2, "min_2_abs_t": min2t,
                                 "p_lower": c["p_lower"] if c else None},
            "score": "MET" if (g["degenerate"] and c and c["p_lower"] == 1.0)
                     else "NOT MET"}

    # ---- P7 ----
    p7 = {}
    for pname, b in bundles.items():
        L = b["ladder"]
        row = {}
        for m in ("2", "3"):
            ex_c = L["cells"][f"{pname}|sumset_m{m}|R0_FREE|weighted|B{L['B']}"]
            sm_c = L["cells"][f"{pname}|decomp_rate_m{m}|R0_FREE|weighted|B{L['B']}"]
            row[f"m{m}"] = {
                "p_lower_exact_sumset": ex_c["p_lower"],
                "r_lower_exact_sumset": ex_c["r_lower"],
                "p_lower_sampled_rate": sm_c["p_lower"],
                "r_lower_sampled_rate": sm_c["r_lower"],
                "exact_more_significant": bool(ex_c["p_lower"] < sm_c["p_lower"]),
                "R_exact": ex_c["variance_ratio_R_empirical"],
                "R_sampled": sm_c["variance_ratio_R_empirical"]}
        p7[pname] = row
    twelve = [k for k, v in p7.items() if k in ("POOL_B", "POOL_D")]
    ok7 = all(p7[k][f"m{m}"]["exact_more_significant"]
              for k in twelve for m in ("2", "3")) if len(twelve) == 2 else None
    sc["predictions"]["P7"] = {
        "statement": "under the FREE permutation the exact sum-set size |mV| "
                     "should be MORE significant than the sampled decomposition "
                     "rate at the same m, at both primes. Parent proposal's "
                     "honest prior 0.35.",
        "sample": "OUT-OF-SAMPLE",
        "deciding_numbers": p7,
        "score": ("MET" if ok7 else "NOT MET") if ok7 is not None
                 else "NOT DECIDABLE"}

    # ---- P8 ----
    p8 = {}
    for pname in ("POOL_B", "POOL_D"):
        b = bundles.get(pname)
        if not b:
            continue
        L, C = b["ladder"], b["controls"]
        finest = L["finest_non_degenerate_rung_N_ladder"]
        cp = C["CTRL_POWER"].get(finest) if finest else None
        p8[pname] = {
            "finest_non_degenerate_rung": finest,
            "power_at_0.8": cp["curve"]["0.8"]["power"] if cp else None,
            "rejections_at_0.8": cp["curve"]["0.8"]["rejections"] if cp else None,
            "replicates": cp["curve"]["0.8"]["replicates"] if cp else None,
            "threshold": 0.90,
            "delta_star": cp["delta_star"] if cp else None,
            "two_class_block": cp["two_class_block"] if cp else None,
            "delta_max_N": cp["delta_max_N"] if cp else None,
            "nuisance_budget": cp["nuisance_budget_weighted"] if cp else None,
            "within_block_corr_u_N": cp["within_block_corr_u_N"] if cp else None,
            "size_calibrated_at_this_rung": bool(
                C["CTRL_NULLOBJ"][finest]["inside_exact_binomial_interval"]
                and C["CTRL_SIZE0"][finest]["inside_exact_binomial_interval"])
            if finest else None,
        }
    if len(p8) == 2 and all(v["power_at_0.8"] is not None for v in p8.values()):
        score8 = "MET" if all(v["power_at_0.8"] >= 0.90 for v in p8.values()) \
            else "NOT MET"
    else:
        score8 = "NOT DECIDABLE"
    sc["predictions"]["P8"] = {
        "statement": "power of the blocked test at the finest non-degenerate "
                     "rung: at least 0.90 detection at level 0.05 for a planted "
                     "between-class effect of 0.8 within-class standard "
                     "deviations, at the twelve-class pool at both primes.",
        "sample": "OUT-OF-SAMPLE",
        "deciding_numbers": p8, "score": score8}

    sc["s1_gate"] = {"gate": s1["gate"],
                     "signed_difference_T_obs": s1["signed_difference_T_obs"],
                     "relative_residual_null_mean":
                         s1["relative_residual_null_mean"]}
    sc["s2_gate"] = {"gate": s2["gate"],
                     "sampler_free_all_reproduced":
                         s2["sampler_free_all_reproduced"]}
    sc["in_sample_disclosure"] = (
        "THE POOL-A VALUES ARE IN-SAMPLE. The committed run records were open "
        "while the closed form was written, so their reproduction is a "
        "REPRODUCTION and never a prediction. OUT-OF-SAMPLE: every POOL-B, "
        "POOL-C and POOL-D number; the entire power and size study; the "
        "excess-over-surrogate curves; P7's exact-versus-sampled comparison; "
        "and the twist multiset check at p = 6007.")
    return sc


# ==========================================================================
# driver: stages, budget caps, immutable run records
# ==========================================================================

GATES_RUN = "RUN-INSTR-85b102-gates"
RUN_AREA = "INSTR"
WALL_CLOCK_LIMIT_S = 5400
MEMORY_LIMIT_GB = 4


def _repo() -> str:
    import os
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run_dir(run_id: str) -> str:
    import os
    return os.path.join(_repo(), "experiments", EXPERIMENT_ID, "runs", run_id)


def _dump(run_id: str, name: str, obj, text: bool = False) -> None:
    import json
    import os
    path = os.path.join(_run_dir(run_id), name)
    with open(path, "w", encoding="utf-8") as f:
        if text:
            f.write(obj)
        else:
            json.dump(obj, f, indent=2, sort_keys=True, default=str)


def _csv(run_id: str, name: str, rows: list[dict], fields: list[str]) -> None:
    import csv
    import os
    with open(os.path.join(_run_dir(run_id), name), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _cap_memory() -> dict:
    import resource
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        want = MEMORY_LIMIT_GB * 1024 ** 3
        resource.setrlimit(resource.RLIMIT_AS,
                           (want, hard if hard != resource.RLIM_INFINITY
                            else want))
        return {"rlimit_as_bytes": want, "applied": True,
                "previous_soft": soft}
    except Exception as exc:                              # pragma: no cover
        return {"applied": False, "error": f"{type(exc).__name__}: {exc}"}


class _Budget:
    def __init__(self, limit_s: int = WALL_CLOCK_LIMIT_S):
        import time
        self.t0 = time.time()
        self.limit = limit_s
        self.exceeded = False
        self.where = None

    def check(self, where: str) -> bool:
        import time
        if time.time() - self.t0 > self.limit:
            self.exceeded = True
            self.where = where
            return False
        return True

    @property
    def elapsed(self) -> float:
        import time
        return time.time() - self.t0


def _cache_path() -> str:
    """Pure measurement cache, OUTSIDE the repository.

    Keyed by (p, a, b, fb sizes, target count, sampler seed); deleting it
    changes no number, only the time to recompute one.
    """
    import os
    import tempfile
    d = os.environ.get("BLOCKNULL_CACHE_DIR",
                       os.path.join(tempfile.gettempdir(), "blocknull-cache"))
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "measurements.json")


def _load_cache() -> dict:
    import json
    import os
    p = _cache_path()
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    import json
    with open(_cache_path(), "w", encoding="utf-8") as f:
        json.dump(cache, f)


def _emit(run_id_suffix: str, metrics: dict, raw: dict, stdout: str,
          command: str, started: float, finished: float, status: str,
          valid: bool, invalid_reason=None) -> str:
    from .runner import RunResult, write_run
    return write_run(EXPERIMENT_ID, RUN_AREA, RunResult(
        run_suffix=run_id_suffix, curve_id=raw.get("curve_id", "n/a"),
        seed=MASTER_SEED, parameters=raw.get("parameters", {}),
        metrics=metrics, certificate={"kind": "none"},
        valid=valid, invalid_reason=invalid_reason,
        stdout=stdout, stderr="", raw=raw),
        status=status, command=command, started=started, finished=finished)


CERTIFICATE_NOTE = (
    "certificate.kind: none, EXPLICITLY. This contract computes no discrete "
    "logarithm and collects no relation, so there is no solve or relation "
    "claim to certify (docs/claims-and-verification.md). Its forced-value "
    "checks -- the liftable-count identity per curve, T_obs = 0 for `order`, "
    "p_lower = 1.0 at R5_PERCLASS, the closed-form-versus-Monte-Carlo null "
    "mean, the Hurwitz-Kronecker census -- are internal consistency checks, "
    "not certificates, and are reported as such.")


def _stage_gates(args) -> int:
    import json
    import os
    import time
    started = time.time()
    budget = _Budget(args.max_seconds)
    mem = _cap_memory()
    log: list[str] = []

    def say(s):
        print(s, flush=True)
        log.append(s)

    say(f"== {EXPERIMENT_ID} stage GATES (S0, S1, S2) ==")
    say(f"memory cap: {mem}")

    say("-- CTRL-FROZEN-DIFF --")
    diff_text, diff_rep = frozen_function_report(args.base_ref,
                                                 args.context_ref)
    say(f"   base_ref (BINDING) = {args.base_ref} = {diff_rep['base_commit']}")
    for path, v in diff_rep["files"].items():
        say(f"   {path:28s} diff_vs_base_empty={v['diff_vs_base_empty']}")
    say(f"   per-function UNCHANGED: "
        f"{sum(1 for v in diff_rep['functions'].values() if v['identical'])}"
        f"/{len(diff_rep['functions'])}")
    say(f"   verdict: {diff_rep['verdict']}")

    say("-- S1 zero-compute arithmetic gate (runs BEFORE any compute) --")
    s1 = s1_arithmetic_gate(_repo())
    say(f"   re-derived T_obs      = {s1['rederived_T_obs_count_units']!r}")
    say(f"   committed             = {s1['committed_T_obs']!r}")
    say(f"   signed difference     = {s1['signed_difference_T_obs']:.3e} "
        f"(tol 1e-9) -> {s1['T_obs_gate']}")
    say(f"   re-derived null mean  = {s1['rederived_null_mean_rate_units']!r}")
    say(f"   committed             = {s1['committed_null_mean_rate_units']!r}")
    say(f"   relative residual     = {s1['relative_residual_null_mean']:.3e} "
        f"(tol 1e-3) -> {s1['null_mean_gate']}")
    say(f"   S1 GATE: {s1['gate']}")

    say("-- committed fixture resolution --")
    fixtures = resolve_fixtures(_repo())
    n_unreach = sum(1 for f in fixtures if f["status"] == "UNREACHABLE")
    say(f"   {len(fixtures)} fixtures, {n_unreach} UNREACHABLE")
    for f in fixtures:
        say(f"   {f['id']:26s} {f['status']:11s} diff={f['signed_difference']!r}")

    stop = None
    if s1["gate"] != "PASS":
        stop = ("S1 arithmetic gate FAILED: the diagnosis that the committed "
                "664x ratio is the group order is WITHDRAWN and the run ENDS "
                "here. That withdrawal is the deliverable.")
    elif n_unreach * 2 > len(fixtures):
        stop = ("more than half the committed reproduction fixtures resolve "
                "UNREACHABLE; the provenance failure is the deliverable")

    s0 = {"stage": "S0", "skipped": True} if stop else None
    s2 = None
    if not stop:
        say("-- S0 pool freeze (BEFORE any functional is measured) --")
        s0 = s0_freeze(_repo(), progress=lambda s: say(f"   {s}"))
        for p, v in s0["primes"].items():
            say(f"   p={p}: {v['curves_enumerated']} curves, "
                f"{v['traces_total']} traces, census failures="
                f"{v['census_failures']} -> agrees={v['census_agrees']}")
        if s0["gate"] != "PASS":
            stop = s0["stop_reason"]
        else:
            for name, v in s0["pools"].items():
                say(f"   {name}: p={v['prime']} traces={v['traces_in_pooled_order']}")
                say(f"      n={v['n_curves']} K={v['n_classes']} sizes={v['class_sizes']}")
                say(f"      N={v['class_orders_N']}")
                say(f"      Delta_pool={v['delta_pool']} vs 4*sqrt(p)="
                    f"{v['four_sqrt_p']:.2f} ratio={v['delta_pool_over_four_sqrt_p']:.4f} "
                    f"Delta/(p+1)={v['delta_pool_over_p_plus_1']:.6f}")
                say(f"      widths={v['band_widths']} dropped={v['dropped_classes']}")
                for rung in RUNGS:
                    rt = s0["rung_table"][name][rung]
                    say(f"      {rung:24s} nblk={rt['n_blocks']:2d} "
                        f"dmax={rt['delta_max_N']:5d} ge2={rt['blocks_with_ge_2_classes']} "
                        f"ge3={rt['blocks_with_ge_3_classes']} "
                        f"degen={rt['degenerate']} {rt['block_composition_by_trace']}")

    s2_rows = []
    if not stop:
        say("-- S2 committed-fixture reproduction on the frozen POOL-A slice --")
        poolA = s0["_pools_object"]["POOL_A"]
        s2 = s2_reproduce(4001, poolA.traces, s0["_classes"][4001])
        for c in s2["checks"]:
            say(f"   {c['fixture']:26s} raw_match="
                f"{c.get('raw_count_match', c.get('bitwise_match'))!r} "
                f"committed={c['committed']!r} reproduced={c['reproduced']!r}")
        for k, v in s2["sampler_dependent_degenfix"].items():
            say(f"   [sampler-dependent] {k:42s} committed_r={v['committed_r']} "
                f"reproduced_r={v['reproduced_r']} match={v['raw_count_match']}")
        say(f"   S2 GATE: {s2['gate']}")
        if s2["gate"] != "PASS":
            stop = ("S2 failed to reproduce a SAMPLER-FREE committed fixture: "
                    "instrument instability. Nothing is concluded and the "
                    "discrepancy is the deliverable.")
        # per-curve slice actually measured at S2
        zmap = {}
        for t in poolA.traces:
            for r in s0["_classes"][4001][t]:
                zmap[(r.a, r.b)] = ex.two_torsion_x_count(4001, r.a, r.b)
        for t in poolA.traces:
            for r in s0["_classes"][4001][t]:
                E = r.curve()
                s2_rows.append({
                    "p": 4001, "a": r.a, "b": r.b, "j": r.j, "trace": r.trace,
                    "order": r.order, "aut_order": r.aut_order,
                    "liftable_density_W400": ex.liftable_density(E, REPRO_WINDOW),
                    "two_torsion_x": zmap[(r.a, r.b)]})

    finished = time.time()
    status = "completed" if not stop else "completed"
    metrics = {
        "stage": "gates (S0,S1,S2)",
        "frozen_function_diff_verdict": diff_rep["verdict"],
        "s1_gate": s1["gate"],
        "s1_signed_difference_T_obs": s1["signed_difference_T_obs"],
        "s1_relative_residual_null_mean": s1["relative_residual_null_mean"],
        "fixtures_total": len(fixtures), "fixtures_unreachable": n_unreach,
        "s0_gate": (s0 or {}).get("gate"),
        "s2_gate": (s2 or {}).get("gate"),
        "stopped": bool(stop), "stop_reason": stop,
        "wall_seconds": round(finished - started, 3),
        "certificate_note": CERTIFICATE_NOTE,
    }
    s0_public = {k: v for k, v in (s0 or {}).items()
                 if not k.startswith("_")} if s0 else None
    if args.supersedes:
        metrics["supersedes"] = args.supersedes
        metrics["supersedes_reason"] = args.supersedes_reason
    raw = {"stage": "gates", "s0": s0_public, "s1": s1, "s2": s2,
           "frozen_function_diff": diff_rep,
           "committed_fixture_table": fixtures,
           "parameters": {"base_ref": args.base_ref,
                          "context_ref": args.context_ref,
                          "max_seconds": args.max_seconds,
                          "memory_cap": mem,
                          "supersedes": args.supersedes,
                          "supersedes_reason": args.supersedes_reason},
           "curve_id": "n/a (pool freeze and reproduction gates)"}
    cmd = ("python3 -m harness.run_blocknull --stage gates"
           + (f" --suffix {args.suffix}" if args.suffix else ""))
    run_id = _emit(args.suffix or GATES_RUN.replace(f"RUN-{RUN_AREA}-", ""),
                   metrics, raw,
                   "\n".join(log) + "\n", cmd, started, finished, status,
                   valid=True)
    say(f"wrote {run_id}")

    _dump(run_id, "results.json", {"stage": "gates", "metrics": metrics,
                                   "s1": s1, "s2": s2,
                                   "certificate_note": CERTIFICATE_NOTE})
    _dump(run_id, "committed_fixture_table.json",
          {"fixtures": fixtures, "unreachable": n_unreach,
           "total": len(fixtures),
           "stop_rule": "more than half UNREACHABLE stops the run"})
    _dump(run_id, "frozen_function_diff.txt", diff_text, text=True)
    _dump(run_id, "frozen_function_diff.json", diff_rep)
    if s0_public:
        _dump(run_id, "pool_freeze.json", s0_public)
        _dump(run_id, "pool_table.json",
              {"note": "S0 freeze table; Var(z) and the sorted-z hash are "
                       "filled per pool at stage S3 in that pool's run record",
               "pools": s0_public["pools"], "primes": s0_public["primes"],
               "POOL_C_draw": s0_public.get("POOL_C_draw")})
        _dump(run_id, "rung_table.json", s0_public["rung_table"])
    _dump(run_id, "controls.json",
          {"CTRL_FROZEN_DIFF": {"verdict": diff_rep["verdict"],
                                "functions": diff_rep["functions"],
                                "files": diff_rep["files"]},
           "CTRL_REPRO": s2,
           "note": "CTRL-NULLOBJ, CTRL-SIZE0, CTRL-POWER, CTRL-NSURR, "
                   "CTRL-CALIB, CTRL-ORDER, CTRL-PERCLASS, CTRL-TWIST are "
                   "stage S3-S5 controls and are reported in the per-pool run "
                   "records, not here."})
    if s2_rows:
        _csv(run_id, "per_curve.csv", s2_rows,
             ["p", "a", "b", "j", "trace", "order", "aut_order",
              "liftable_density_W400", "two_torsion_x"])
    _dump(run_id, "prediction_scorecard.json",
          {"note": "P1-P8 are scored globally at stage S6 "
                   "(--stage scorecard). This gate-stage record carries only "
                   "the S1 and S2 gate outcomes they depend on.",
           "s1_gate": s1, "s2_gate": (s2 or {}).get("gate")})
    if stop:
        say("STOP: " + stop)
        return 4
    return 0


def _load_freeze() -> dict:
    import json
    import os
    p = os.path.join(_run_dir(GATES_RUN), "pool_freeze.json")
    if not os.path.exists(p):
        raise SystemExit(f"pool freeze not found at {p}; run --stage gates first")
    return json.load(open(p, encoding="utf-8"))


def _rebuild_pool(name: str, freeze: dict, classes_cache: dict) -> Pool:
    spec = freeze["pools"][name]
    p = spec["prime"]
    if p not in classes_cache:
        classes_cache[p] = ic.isogeny_classes(p)
    return build_pool(name, p, [int(t) for t in spec["traces_in_pooled_order"]],
                      classes_cache[p], spec["rule"])


def _stage_pool(args) -> int:
    import time
    started = time.time()
    budget = _Budget(args.max_seconds)
    mem = _cap_memory()
    log: list[str] = []

    def say(s):
        print(s, flush=True)
        log.append(s)

    freeze = _load_freeze()
    say(f"== {EXPERIMENT_ID} stage POOL {args.pool} (S3, S4, S5) ==")
    say(f"pool frozen at S0 in {GATES_RUN}/pool_freeze.json -- "
        f"traces {freeze['pools'][args.pool]['traces_in_pooled_order']}")
    say(f"memory cap: {mem}")
    pool = _rebuild_pool(args.pool, freeze, {})
    say(f"n={pool.n} K={pool.K} sizes={pool.class_sizes} N={pool.class_orders} "
        f"Delta_pool={pool.delta_pool}")

    say("-- S3 measurement --")
    cache = _load_cache()
    t3 = time.time()
    rows, values = measure_pool(
        pool, cache, progress=lambda i, n: say(f"   measured {i}/{n}"))
    _save_cache(cache)
    say(f"   measured {pool.n} curves in {time.time() - t3:.1f} s")
    n_ok = sum(1 for r in rows if r["liftable_identity_holds"])
    say(f"   liftable-count identity holds on {n_ok}/{len(rows)} curves")
    twist = ctrl_twist(pool, rows)
    say(f"   CTRL-TWIST: {twist['verdict']} "
        f"({len(twist['pairs'])} pooled pairs, unpaired={twist['unpaired_traces']})")

    if not budget.check("after S3"):
        return _abort(args, started, budget, log, "S3 measurement")

    say(f"-- S4 ladder (B={args.primary_b}) --")
    t4 = time.time()
    ladder = s4_ladder(pool, values, B=args.primary_b,
                       progress=lambda r: say(f"   rung {r} done "
                                              f"({budget.elapsed:.0f}s)"))
    say(f"   ladder in {time.time() - t4:.1f} s; finest non-degenerate rung "
        f"(N ladder) = {ladder['finest_non_degenerate_rung_N_ladder']}")
    for r in RUNGS:
        g = ladder["rung_geometry"][r]
        nb = ladder["nuisance_budget_by_rung"][r]
        say(f"   {r:24s} dmax={g['delta_max_N']:5d} degen={str(g['degenerate']):5s} "
            f"nuisance(w)={nb['weighted']:.6g}")

    if not budget.check("after S4"):
        return _abort(args, started, budget, log, "S4 ladder", ladder=ladder,
                      pool=pool, rows=rows)

    say(f"-- S5 control objects (replicates={args.replicates}, B={args.control_b}) --")
    t5 = time.time()
    controls = s5_controls(pool, values, ladder, replicates=args.replicates,
                           B=args.control_b,
                           nullobj_functional=args.nullobj_functional,
                           progress=lambda s: say(f"   {s} ({budget.elapsed:.0f}s)"))
    say(f"   controls in {time.time() - t5:.1f} s")
    lo, hi = controls["exact_binomial_acceptance_interval"]["lo"], \
        controls["exact_binomial_acceptance_interval"]["hi"]
    say(f"   exact 99% Binomial({args.replicates},0.05) acceptance = [{lo},{hi}]")
    for r in RUNGS:
        no = controls["CTRL_NULLOBJ"][r]
        s0c = controls["CTRL_SIZE0"][r]
        cp = controls["CTRL_POWER"][r]
        say(f"   {r:24s} NULLOBJ rej={no['rejections']:3d} size={no['realized_size']:.3f} "
            f"in={no['inside_exact_binomial_interval']!s:5s} | "
            f"SIZE0 rej={s0c['rejections']:3d} in={s0c['inside_exact_binomial_interval']!s:5s} | "
            f"power@0.8={cp['curve']['0.8']['power']:.3f} delta*={cp['delta_star']}")

    checks = tail_checks(pool, rows, ladder, controls)
    say("-- tail checks --")
    for c in checks:
        say(f"   {c['result']:4s} {c['check']}")

    # forced-value stopping rules
    stop = None
    r5_bad = [c for c in checks if c["check"].startswith("R5_PERCLASS")
              and c["result"] != "PASS"]
    ord_bad = [c for c in checks if c["check"].startswith("`order`")
               and c["result"] != "PASS"]
    if r5_bad or ord_bad:
        stop = ("R5_PERCLASS returned something other than exactly 1.0, or "
                "`order` returned nonzero within-class variance: implementation "
                "defect, run invalid rather than negative")

    finished = time.time()
    pool_table = _pool_table(pool, rows, freeze)
    metrics = _pool_metrics(pool, ladder, controls, checks, twist, rows,
                            args, finished - started, stop)
    raw = {"stage": f"pool {pool.name}", "pool": pool_table,
           "ladder": ladder, "controls": controls, "tail_checks": checks,
           "ctrl_twist": twist,
           "parameters": {"pool": pool.name, "prime": pool.p,
                          "primary_B": args.primary_b,
                          "control_B": args.control_b,
                          "replicates": args.replicates,
                          "nullobj_functional": args.nullobj_functional,
                          "declared_replicates": CONTROL_REPLICATES,
                          "replicate_reduction":
                              args.replicates < CONTROL_REPLICATES,
                          "memory_cap": mem},
           "curve_id": f"POOL-{pool.name}-p{pool.p}"}
    if args.supersedes:
        metrics["supersedes"] = args.supersedes
        metrics["supersedes_reason"] = args.supersedes_reason
    cmd = (f"python3 -m harness.run_blocknull --stage pool --pool {pool.name} "
           f"--replicates {args.replicates} --primary-b {args.primary_b} "
           f"--control-b {args.control_b} --gates-run {args.gates_run}"
           + (f" --suffix {args.suffix}" if args.suffix else ""))
    run_id = _emit(args.suffix
                   or f"85b102-{pool.name.replace('POOL_', 'pool')}",
                   metrics, raw,
                   "\n".join(log) + "\n", cmd, started, finished,
                   "completed" if not stop else "completed", valid=not stop,
                   invalid_reason=stop)
    say(f"wrote {run_id}")
    _write_pool_artifacts(run_id, pool, rows, pool_table, freeze, ladder,
                          controls, checks, twist, metrics, args)
    return 0 if not stop else 5


def _abort(args, started, budget, log, where, ladder=None, pool=None, rows=None):
    import time
    finished = time.time()
    metrics = {"stage": f"pool {args.pool}", "status": "resource_exhaustion",
               "budget_limit_seconds": args.max_seconds,
               "elapsed_seconds": budget.elapsed,
               "exhausted_after": where,
               "note": "wall clock exhausted; this is INFRASTRUCTURE SIGNAL, "
                       "recorded as failed_infrastructure with its cause. It "
                       "is NEVER negative mathematical evidence and never "
                       "counts toward the falsification criterion."}
    raw = {"stage": f"pool {args.pool}", "ladder": ladder,
           "parameters": vars(args), "curve_id": f"POOL-{args.pool}"}
    run_id = _emit(f"85b102-{args.pool.replace('POOL_', 'pool')}-partial",
                   metrics, raw, "\n".join(log) + "\n",
                   f"python3 -m harness.run_blocknull --stage pool --pool {args.pool}",
                   started, finished, "failed_infrastructure", valid=False,
                   invalid_reason="wall-clock budget exhausted")
    print(f"BUDGET EXHAUSTED after {where}; wrote {run_id}")
    return 6


def _pool_table(pool: Pool, rows: list[dict], freeze: dict) -> dict:
    import statistics as _st
    spec = dict(freeze["pools"][pool.name])
    by_ci: dict[int, list[int]] = {}
    for r, ci in zip(rows, pool.labels):
        by_ci.setdefault(int(ci), []).append(r["two_torsion_x"])
    for entry in spec["classes"]:
        zs = sorted(by_ci[entry["class_index"]])
        entry["Var_two_torsion_x"] = _st.variance(zs) if len(zs) > 1 else 0.0
        entry["sorted_z_sha256"] = _sha(",".join(map(str, zs)))
        entry["z_composition"] = {str(v): zs.count(v) for v in sorted(set(zs))}
        entry["note"] = ("Var(z) and the sorted-z hash were measured at S3, "
                         "after the pool was frozen at S0.")
    return spec


def _pool_metrics(pool, ladder, controls, checks, twist, rows, args,
                  wall, stop) -> dict:
    B = ladder["B"]
    finest = ladder["finest_non_degenerate_rung_N_ladder"]
    return {
        "pool": pool.name, "prime": pool.p, "n_curves": pool.n,
        "n_classes": pool.K, "delta_pool": pool.delta_pool,
        "traces": [int(t) for t in pool.traces],
        "dropped_classes": pool.dropped,
        "liftable_identity_curves_holding":
            sum(1 for r in rows if r["liftable_identity_holds"]),
        "liftable_identity_curves_total": len(rows),
        "ctrl_twist_all_pairs_agree": twist["all_pairs_agree"],
        "finest_non_degenerate_rung_N_ladder": finest,
        "finest_non_degenerate_rung_all_rungs":
            ladder["finest_non_degenerate_rung_all_rungs"],
        "delta_max_along_N_ladder": ladder["delta_max_along_N_ladder"],
        "nuisance_budget_along_N_ladder": ladder["nuisance_budget_along_N_ladder"],
        "delta_max_non_increasing": ladder["delta_max_non_increasing"],
        "nuisance_non_increasing": ladder["nuisance_non_increasing"],
        "realized_size_nullobj": {r: controls["CTRL_NULLOBJ"][r]["realized_size"]
                                  for r in RUNGS},
        "realized_size_size0": {r: controls["CTRL_SIZE0"][r]["realized_size"]
                                for r in RUNGS},
        "size_calibrated": {r: bool(
            controls["CTRL_NULLOBJ"][r]["inside_exact_binomial_interval"]
            and controls["CTRL_SIZE0"][r]["inside_exact_binomial_interval"])
            for r in RUNGS},
        "uncalibrated_rungs": controls["uncalibrated_rungs"],
        "power_at_0.8": {r: controls["CTRL_POWER"][r]["curve"]["0.8"]["power"]
                         for r in RUNGS},
        "delta_star": {r: controls["CTRL_POWER"][r]["delta_star"] for r in RUNGS},
        "two_class_block": {r: controls["CTRL_POWER"][r]["two_class_block"]
                            for r in RUNGS},
        "tail_checks": {c["check"]: c["result"] for c in checks},
        "tail_check_refined_indicators": {
            c["check"]: {k: v for k, v in c.items()
                         if k.endswith("_indicator")}
            for c in checks if any(k.endswith("_indicator") for k in c)},
        "replicates_realized": args.replicates,
        "replicates_declared": CONTROL_REPLICATES,
        "replicate_reduction": bool(args.replicates < CONTROL_REPLICATES),
        "primary_B": B, "control_B": args.control_b,
        "wall_seconds": round(wall, 3),
        "invalid_reason": stop,
        "certificate_note": CERTIFICATE_NOTE,
        "scope": "Tier TOY. Instrument characterisation only. No ECDLP claim, "
                 "no cost or exponent claim, sota_delta zero.",
    }


def _write_pool_artifacts(run_id, pool, rows, pool_table, freeze, ladder,
                          controls, checks, twist, metrics, args) -> None:
    import os
    import shutil
    _dump(run_id, "results.json",
          {"experiment_id": EXPERIMENT_ID, "pool": pool.name, "prime": pool.p,
           "metrics": metrics, "ladder": ladder, "tail_checks": checks,
           "certificate_note": CERTIFICATE_NOTE,
           "keying": "cells are keyed (pool, functional, rung, statistic, B)"})
    _dump(run_id, "pool_table.json", pool_table)
    _dump(run_id, "rung_table.json",
          {pool.name: {**ladder["rung_geometry"],
                       "_delta_max_non_increasing_along_N_ladder":
                           ladder["delta_max_non_increasing"],
                       "_collapsed_onto_predecessor":
                           ladder["collapsed_onto_predecessor"]}})
    _dump(run_id, "controls.json",
          {**controls, "CTRL_TWIST": twist,
           "CTRL_CALIB": {
               "functional": "full_liftable",
               "by_rung": {r: ladder["cells"][
                   f"{pool.name}|full_liftable|{r}|unweighted|B{ladder['B']}"]
                   for r in RUNGS}},
           "CTRL_ORDER": {
               "functional": "order",
               "note": "within-class variance is exactly 0, so T_obs = 0.0 at "
                       "every rung and E[T_pi|rung] IS the nuisance budget",
               "by_rung": {r: ladder["cells"][
                   f"{pool.name}|order|{r}|weighted|B{ladder['B']}"]
                   for r in RUNGS}},
           "CTRL_PERCLASS": {
               "rung": "R5_PERCLASS",
               "p_lower_by_functional": {
                   k: ladder["cells"][
                       f"{pool.name}|{k}|R5_PERCLASS|weighted|B{ladder['B']}"]
                   ["p_lower"] for k in ladder["functionals"]}}})
    fields = (["p", "a", "b", "j", "trace", "order", "aut_order", "fb_m2",
               "fb_m3", "n_targets", "hits_m2", "hits_m3"]
              + functional_keys(pool.p) + ["liftable_identity_holds"])
    _csv(run_id, "per_curve.csv", rows, fields)
    for name in ("committed_fixture_table.json", "frozen_function_diff.txt"):
        src = os.path.join(_run_dir(GATES_RUN), name)
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(_run_dir(run_id), name))
    _dump(run_id, "prediction_scorecard.json",
          {"note": "per-pool view; the global P1-P8 scorecard requiring both "
                   "primes is emitted at stage S6 (--stage scorecard)",
           "pool": pool.name,
           "scorecard": prediction_scorecard(
               {pool.name: {"pool": pool, "ladder": ladder,
                            "controls": controls, "twist": twist}},
               {"gate": "see gates run", "signed_difference_T_obs": None,
                "relative_residual_null_mean": None},
               {"gate": "see gates run", "sampler_free_all_reproduced": None})})


def _stage_scorecard(args) -> int:
    import json
    import os
    import shutil
    import time
    started = time.time()
    log: list[str] = []

    def say(s):
        print(s, flush=True)
        log.append(s)

    freeze = _load_freeze()
    gates_raw = json.load(open(os.path.join(_run_dir(GATES_RUN),
                                            "raw-result.json"), encoding="utf-8"))
    s1 = gates_raw["raw"]["s1"]
    s2 = gates_raw["raw"]["s2"]
    cc: dict = {}
    bundles = {}
    overrides = dict(kv.split("=", 1) for kv in (args.pool_run or []))
    for name in ("POOL_A", "POOL_B", "POOL_C", "POOL_D"):
        rid = overrides.get(
            name, f"RUN-{RUN_AREA}-85b102-{name.replace('POOL_', 'pool')}")
        path = os.path.join(_run_dir(rid), "raw-result.json")
        if not os.path.exists(path):
            say(f"   {name}: NO RUN RECORD at {rid} -- excluded, recorded as missing")
            continue
        doc = json.load(open(path, encoding="utf-8"))["raw"]
        bundles[name] = {"pool": _rebuild_pool(name, freeze, cc),
                         "ladder": doc["ladder"], "controls": doc["controls"],
                         "twist": doc["ctrl_twist"], "run_id": rid,
                         "tail_checks": doc["tail_checks"]}
        say(f"   {name}: loaded {rid}")

    sc = prediction_scorecard(bundles, s1, s2)
    say("-- prediction scorecard --")
    for k in sorted(sc["predictions"]):
        say(f"   {k}: {sc['predictions'][k]['score']} "
            f"[{sc['predictions'][k].get('sample')}]")
        for name, v in (sc["predictions"][k].get("sub_clauses") or {}).items():
            say(f"        sub-clause {name}: {v['score']}")
    summary = _cross_pool_summary(bundles)
    say("-- cross-pool summary --")
    say(json.dumps(summary, indent=1, default=str))

    sc8 = _sc8(bundles)
    say("-- SC8 utility clause --")
    say(json.dumps(sc8, indent=1, default=str))

    finished = time.time()
    metrics = {"stage": "scorecard (S6)",
               "pools_scored": sorted(bundles),
               "pool_run_ids": {n: b["run_id"] for n, b in bundles.items()},
               "pools_missing": [n for n in ("POOL_A", "POOL_B", "POOL_C",
                                             "POOL_D") if n not in bundles],
               "scores": {k: v["score"] for k, v in sc["predictions"].items()},
               "sub_clause_scores": {
                   k: {n: vv["score"] for n, vv in (v.get("sub_clauses") or {}).items()}
                   for k, v in sc["predictions"].items() if v.get("sub_clauses")},
               "sc8": sc8,
               "cross_pool_summary": summary,
               "certificate_note": CERTIFICATE_NOTE}
    if args.supersedes:
        metrics["supersedes"] = args.supersedes
        metrics["supersedes_reason"] = args.supersedes_reason
    raw = {"stage": "scorecard", "scorecard": sc, "sc8": sc8,
           "cross_pool_summary": summary,
           "parameters": {"pools": sorted(bundles),
                          "pool_run_ids": {n: b["run_id"]
                                           for n, b in bundles.items()},
                          "gates_run": args.gates_run,
                          "supersedes": args.supersedes},
           "curve_id": "n/a (emission stage)"}
    run_id = _emit(args.suffix or "85b102-scorecard", metrics, raw,
                   "\n".join(log) + "\n",
                   "python3 -m harness.run_blocknull --stage scorecard",
                   started, finished, "completed", valid=True)
    say(f"wrote {run_id}")
    _dump(run_id, "prediction_scorecard.json", sc)
    _dump(run_id, "results.json", {"scorecard": sc, "sc8": sc8,
                                   "cross_pool_summary": summary,
                                   "metrics": metrics})
    _dump(run_id, "rung_table.json",
          {n: b["ladder"]["rung_geometry"] for n, b in bundles.items()})
    _dump(run_id, "pool_table.json", freeze["pools"])
    _dump(run_id, "controls.json",
          {n: {"CTRL_NULLOBJ": b["controls"]["CTRL_NULLOBJ"],
               "CTRL_SIZE0": b["controls"]["CTRL_SIZE0"],
               "CTRL_POWER": {r: {k: v for k, v in
                                  b["controls"]["CTRL_POWER"][r].items()
                                  if k != "curve"} |
                              {"curve": b["controls"]["CTRL_POWER"][r]["curve"]}
                              for r in RUNGS},
               "CTRL_NSURR": b["controls"]["CTRL_NSURR"],
               "CTRL_TWIST": b["twist"]}
           for n, b in bundles.items()})
    for name in ("committed_fixture_table.json", "frozen_function_diff.txt"):
        src = os.path.join(_run_dir(GATES_RUN), name)
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(_run_dir(run_id), name))
    import csv
    with open(os.path.join(_run_dir(run_id), "per_curve.csv"), "w",
              newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pool", "per_curve_csv_path"])
        for n, b in bundles.items():
            w.writerow([n, f"experiments/{EXPERIMENT_ID}/runs/{b['run_id']}"
                           f"/per_curve.csv"])
    return 0


def _cross_pool_summary(bundles: dict) -> dict:
    """Per-rung realized size, power, nuisance budget and delta*, per pool.

    Observations only. No rung is adopted, recommended or retired here.
    """
    out: dict = {}
    for name, b in bundles.items():
        L, C = b["ladder"], b["controls"]
        rows = {}
        for r in RUNGS:
            g = L["rung_geometry"][r]
            no, s0, cp = (C["CTRL_NULLOBJ"][r], C["CTRL_SIZE0"][r],
                          C["CTRL_POWER"][r])
            rows[r] = {
                "delta_max_N": g["delta_max_N"],
                "n_blocks": g["n_blocks"],
                "blocks_with_ge_2_classes": g["blocks_with_ge_2_classes"],
                "blocks_with_ge_3_classes": g["blocks_with_ge_3_classes"],
                "degenerate": g["degenerate"],
                "nuisance_budget_weighted":
                    L["nuisance_budget_by_rung"][r]["weighted"],
                "nuisance_budget_unweighted":
                    L["nuisance_budget_by_rung"][r]["unweighted"],
                "realized_size_CTRL_NULLOBJ": no["realized_size"],
                "CTRL_NULLOBJ_rejections": no["rejections"],
                "CTRL_NULLOBJ_inside_interval":
                    no["inside_exact_binomial_interval"],
                "realized_size_CTRL_SIZE0": s0["realized_size"],
                "CTRL_SIZE0_rejections": s0["rejections"],
                "CTRL_SIZE0_inside_interval":
                    s0["inside_exact_binomial_interval"],
                "CTRL_SIZE0_forced_by_degeneracy": s0["forced_by_degeneracy"],
                "power_curve": {k: v["power"] for k, v in cp["curve"].items()},
                "power_at_0.8": cp["curve"]["0.8"]["power"],
                "delta_star": cp["delta_star"],
                "two_class_block": cp["two_class_block"],
                "within_block_corr_u_N": cp["within_block_corr_u_N"],
                "power_cost_vs_R0_FREE": cp["power_cost_vs_R0_FREE"],
                "reports_a_result": bool(
                    no["inside_exact_binomial_interval"]
                    and (s0["inside_exact_binomial_interval"]
                         or s0["forced_by_degeneracy"])),
            }
        # SC5 collapse audit, recomputed from the committed block compositions.
        geo = L["rung_geometry"]
        audit, strict = {}, {}
        for i in range(1, len(N_LADDER)):
            prev, cur = N_LADDER[i - 1], N_LADDER[i]
            same = _partition_of(geo[cur]) == _partition_of(geo[prev])
            nb_prev = L["nuisance_budget_by_rung"][prev]["weighted"]
            nb_cur = L["nuisance_budget_by_rung"][cur]["weighted"]
            audit[cur] = {
                "collapsed_onto_predecessor_partition_compare": bool(same),
                "collapsed_onto_predecessor_as_recorded_in_the_pool_run":
                    L["collapsed_onto_predecessor"].get(cur),
                "predecessor": prev,
                "nuisance_predecessor": nb_prev, "nuisance_here": nb_cur,
                "strictly_decreased": bool(nb_cur < nb_prev),
                "sc5_clause_satisfied": bool(nb_cur < nb_prev or same),
            }
            strict[cur] = audit[cur]["sc5_clause_satisfied"]
        out[name] = {
            "sc5_collapse_audit": audit,
            "sc5_nuisance_clause_satisfied_at_every_step": bool(all(strict.values())),
            "sc5_audit_note":
                "Recomputed here from each pool run's committed "
                "block_composition_by_trace. It SUPERSEDES the "
                "_collapsed_onto_predecessor field inside the pool run records, "
                "which compared block-id-keyed dicts and therefore missed that "
                "R5_PERCLASS realizes the same all-singleton partition as "
                "R4_NBAND_w4 wherever R4 is already degenerate. No measured "
                "number changes; only this boolean does.",
            "prime": b["pool"].p, "n_curves": b["pool"].n,
            "n_classes": b["pool"].K, "delta_pool": b["pool"].delta_pool,
            "traces": [int(t) for t in b["pool"].traces],
            "run_id": b["run_id"],
            "acceptance_interval":
                [C["exact_binomial_acceptance_interval"]["lo"],
                 C["exact_binomial_acceptance_interval"]["hi"]],
            "replicates": C["replicates"], "control_B": C["B"],
            "finest_non_degenerate_rung_N_ladder":
                L["finest_non_degenerate_rung_N_ladder"],
            "finest_non_degenerate_rung_all_rungs":
                L["finest_non_degenerate_rung_all_rungs"],
            "uncalibrated_rungs": C["uncalibrated_rungs"],
            "by_rung": rows,
            "tail_checks": {c["check"]: c["result"] for c in b["tail_checks"]},
            "tail_check_refined": {
                c["check"]: {k: v for k, v in c.items()
                             if k.endswith("_indicator")}
                for c in b["tail_checks"]
                if any(k.endswith("_indicator") for k in c)},
            "contamination_gap": L["contamination_gap"],
            "monotonicity_verdicts": {
                k: v["verdict"] for k, v in L["monotonicity"].items()},
        }
    return out


def _sc8(bundles: dict) -> dict:
    """SC8: at the finest non-degenerate rung, for at least one primary
    functional other than `order` and `full_liftable`, is the nuisance budget
    reduced by >= 10x relative to R0_FREE AND the power at 0.8 within-class sd
    still >= 0.90, at BOTH primes?

    Reported as a measurement. Whether the instrument is adopted is a
    Coordinator decision on a later ledger archive, not an Executor act.
    """
    out = {"per_pool": {}, "note":
           "SC8 is reported here as numbers only. This contract retires "
           "nothing and adopts nothing: whether NULL-C is replaced or retained "
           "is a Coordinator decision after independent review."}
    for name, b in bundles.items():
        L, C = b["ladder"], b["controls"]
        finest = L["finest_non_degenerate_rung_N_ladder"]
        if not finest:
            out["per_pool"][name] = {"finest_non_degenerate_rung": None}
            continue
        nb_free = L["nuisance_budget_by_rung"]["R0_FREE"]["weighted"]
        nb_fin = L["nuisance_budget_by_rung"][finest]["weighted"]
        power = C["CTRL_POWER"][finest]["curve"]["0.8"]["power"]
        factor = (nb_free / nb_fin) if nb_fin > 0 else float("inf")
        out["per_pool"][name] = {
            "finest_non_degenerate_rung": finest,
            "nuisance_budget_R0_FREE": nb_free,
            "nuisance_budget_finest": nb_fin,
            "reduction_factor": factor,
            "reduction_at_least_10x": bool(factor >= 10.0),
            "power_at_0.8_at_finest": power,
            "power_at_least_0.90": bool(power >= 0.90),
            "both_conditions_met": bool(factor >= 10.0 and power >= 0.90),
            "size_calibrated_at_finest": bool(
                C["CTRL_NULLOBJ"][finest]["inside_exact_binomial_interval"]
                and C["CTRL_SIZE0"][finest]["inside_exact_binomial_interval"]),
            "delta_star_at_finest": C["CTRL_POWER"][finest]["delta_star"],
        }
    twelve = [n for n in ("POOL_B", "POOL_D") if n in out["per_pool"]]
    out["both_primes_twelve_class_pools"] = twelve
    out["satisfied_at_both_primes"] = (
        bool(len(twelve) == 2 and all(out["per_pool"][n]["both_conditions_met"]
                                      for n in twelve))
        if len(twelve) == 2 else None)
    return out


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description=f"{EXPERIMENT_ID} blocked-permutation instrument")
    ap.add_argument("--stage", required=True,
                    choices=["gates", "pool", "scorecard"])
    ap.add_argument("--pool", default=None,
                    choices=["POOL_A", "POOL_B", "POOL_C", "POOL_D"])
    ap.add_argument("--replicates", type=int, default=CONTROL_REPLICATES)
    ap.add_argument("--primary-b", dest="primary_b", type=int, default=PRIMARY_B)
    ap.add_argument("--control-b", dest="control_b", type=int, default=CONTROL_B)
    ap.add_argument("--nullobj-functional", default="full_liftable")
    ap.add_argument("--max-seconds", type=int, default=WALL_CLOCK_LIMIT_S)
    ap.add_argument("--base-ref", default="HEAD",
                    help="BINDING frozen-function comparison base")
    ap.add_argument("--context-ref", default="origin/main",
                    help="informational second comparison base")
    ap.add_argument("--suffix", default=None,
                    help="run-id suffix override (a corrected run is a NEW "
                         "run id; the defective one is never overwritten)")
    ap.add_argument("--supersedes", default=None)
    ap.add_argument("--supersedes-reason", default=None)
    ap.add_argument("--gates-run", default=GATES_RUN,
                    help="which gates run record the pool/scorecard stages "
                         "read the frozen pool from")
    ap.add_argument("--pool-run", action="append", default=None,
                    metavar="POOL_X=RUN-ID",
                    help="which run record the scorecard stage reads a pool "
                         "from; repeatable")
    args = ap.parse_args(argv)
    globals()["GATES_RUN"] = args.gates_run
    if args.stage == "gates":
        return _stage_gates(args)
    if args.stage == "scorecard":
        return _stage_scorecard(args)
    if not args.pool:
        raise SystemExit("--pool is required for --stage pool")
    return _stage_pool(args)


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "EXPERIMENT_ID", "DOMAIN", "MASTER_SEED", "REPRODUCTION_SEED", "RUNGS",
    "N_LADDER", "EFFECT_GRID", "PRIMARY_B", "CONTROL_B",
    "derive_seed", "Pool", "build_pool", "poolc_traces", "band_widths",
    "blocking", "blocks_array", "statistic_weighted", "statistic_unweighted",
    "classes_within_blocks", "closed_form_null_mean",
    "blocked_permutation_null", "blocked_permutation_null_both",
    "sumset_m2", "sumset_m3", "exact_binomial_interval", "null_object_labels",
    "power_offsets", "within_block_corr_u_N", "ols_slope_on_N",
    "frozen_function_report", "resolve_fixtures", "s1_arithmetic_gate",
    "s2_reproduce", "s0_freeze", "measure_pool", "ctrl_twist", "s4_ladder",
    "s5_controls", "tail_checks", "prediction_scorecard", "main",
]
