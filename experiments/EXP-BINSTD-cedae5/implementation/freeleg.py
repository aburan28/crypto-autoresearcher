"""Free-leg residual-banking large-prime accumulator for EXP-BINSTD-cedae5.

Stages 1–4 instrument. No GTTD. No deployed-curve attack. Observations only.
"""
from __future__ import annotations

import math
import random
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from curve import Curve
from gf2n import MODULUS, N, TableField

# Frozen RC-1 cell
RC1_A = 97044
RC1_B = 126251
RC1_L = 32603
RC1_ORDER = 4 * RC1_L  # 130412
WINDOW_DEG = 9  # deg(x) < 9


@dataclass
class Attempt:
    i: int
    j: int
    key: int  # x(L) or truncated
    p1: tuple
    p2: tuple
    L: tuple | None


@dataclass
class CensusResult:
    window_kind: str
    window_size: int
    T: int
    identity_sum_pairs: int
    full_relation_count: int
    combined_relation_count: int
    combined_verified: int
    combined_failed: int
    certificate_pass_rate_combined: float
    residual_support_S_fitted: float | None
    residual_collision_rate_ratio: float | None
    max_residual_multiplicity: int
    residual_value_histogram: dict
    attempts_to_B_relations: int | None
    attempts_to_B_relations_log2: float | None
    collection_wall_clock_s: float
    merge_wall_clock_s: float
    peak_rss_bytes: int | None = None
    N: int = RC1_ORDER
    modeled_T2_over_2N: float = 0.0
    modeled_T2_over_2S: float | None = None
    extra: dict = field(default_factory=dict)


def build_rc1() -> tuple[TableField, Curve, int]:
    F = TableField(N, MODULUS)
    E = Curve(F, RC1_A, RC1_B)
    order = E.count_by_trace()
    if order != RC1_ORDER:
        raise RuntimeError(f"RC-1 order {order} != {RC1_ORDER}")
    return F, E, order


def enumerate_window(E: Curve, kind: str = "V") -> list[tuple]:
    """V = deg(x)<9; V'_0 = V with constant bit of x cleared."""
    pts: list[tuple] = []
    for x in range(1 << WINDOW_DEG):
        P = E.lift_x(x)
        if P is None:
            continue
        if kind == "V0" and (x & 1) != 0:
            continue
        pts.append(P)
        Pn = E.neg(P)
        if Pn != P:
            if kind == "V0" and (Pn[0] & 1) != 0:
                pass  # neg preserves x, so same filter
            pts.append(Pn)
    # dedupe while preserving order
    seen = set()
    out = []
    for P in pts:
        if P in seen:
            continue
        seen.add(P)
        if kind == "V0" and (P[0] & 1) != 0:
            continue
        out.append(P)
    return out


def window_x_set(window: list[tuple]) -> set[int]:
    return {P[0] for P in window}


def hash_key(x: int, bits: int | None) -> int:
    if bits is None:
        return x
    return x & ((1 << bits) - 1)


def collect_attempts(
    E: Curve,
    window: list[tuple],
    *,
    pairs: Iterable[tuple[int, int]] | None = None,
    hash_key_bits: int | None = None,
) -> tuple[list[Attempt], int, float]:
    """Enumerate unordered pairs; bank residuals keyed by x(L) (optional truncate)."""
    t0 = time.perf_counter()
    identity = 0
    attempts: list[Attempt] = []
    n = len(window)
    if pairs is None:
        pair_iter = ((i, j) for i in range(n) for j in range(i + 1, n))
    else:
        pair_iter = pairs
    for i, j in pair_iter:
        P1, P2 = window[i], window[j]
        S = E.add(P1, P2)
        if S is None:
            identity += 1
            continue
        L = E.neg(S)
        key = hash_key(L[0], hash_key_bits)
        attempts.append(Attempt(i=i, j=j, key=key, p1=P1, p2=P2, L=L))
    return attempts, identity, time.perf_counter() - t0


def verify_combined(E: Curve, a: Attempt, b: Attempt) -> bool:
    """Independent re-sum of a free-leg large-prime merge.

    Both attempts satisfy Pi+Pj+L = O with the same x(L), so either:
      - L_a == L_b:   cancel L ⇒ P1+P2+(-P3)+(-P4) = O
      - L_a == -L_b:  add the two equations ⇒ P1+P2+P3+P4 = O
    (In char 2, P+P is doubling, not O — same-sum four-point addition is wrong.)
    """
    if a.L is None or b.L is None:
        return False
    if a.L == b.L:
        s = E.add(E.add(a.p1, a.p2), E.add(E.neg(b.p1), E.neg(b.p2)))
        return s is None
    if a.L == E.neg(b.L):
        s = E.add(E.add(a.p1, a.p2), E.add(b.p1, b.p2))
        return s is None
    # Same x(L) but neither equal nor neg — should be impossible on a curve;
    # treat as certificate failure (adversarial truncation lands here).
    return False


def verify_full(E: Curve, a: Attempt, P3: tuple) -> bool:
    """Full free-leg: P1+P2+P3 = O with P3 in the window."""
    s = E.add(E.add(a.p1, a.p2), P3)
    return s is None


def fit_S_from_histogram(hist: Counter, T: int) -> float | None:
    """Method-of-moments: E[C(k,2)] = T^2/(2S) => S = T^2 / (2 * sum C(k,2))."""
    collisions = sum(k * (k - 1) // 2 for k in hist.values())
    if collisions <= 0:
        return None
    return (T * T) / (2.0 * collisions)


def merge_and_certify(
    E: Curve,
    attempts: list[Attempt],
    window: list[tuple],
    *,
    recombination: bool = True,
    verify_all_combined: bool = True,
    max_combined_verify: int | None = None,
) -> dict:
    t0 = time.perf_counter()
    buckets: dict[int, list[Attempt]] = defaultdict(list)
    for a in attempts:
        buckets[a.key].append(a)
    hist = Counter(len(v) for v in buckets.values())
    # also value-level histogram of keys (for residual support)
    key_mult = Counter(a.key for a in attempts)

    x_in_window = window_x_set(window)
    # index a representative point per x in window for full-relation lift
    by_x: dict[int, list[tuple]] = defaultdict(list)
    for P in window:
        by_x[P[0]].append(P)

    full = 0
    full_verified = 0
    full_failed = 0
    for a in attempts:
        if a.L is None:
            continue
        if a.L[0] not in x_in_window:
            continue
        # try L and -L as the third window point
        candidates = by_x.get(a.L[0], [])
        ok = False
        for P3 in candidates:
            if verify_full(E, a, P3):
                ok = True
                break
        full += 1
        if ok:
            full_verified += 1
        else:
            full_failed += 1

    combined = 0
    combined_ok = 0
    combined_fail = 0
    verified_pairs = 0
    if recombination:
        for key, group in buckets.items():
            k = len(group)
            if k < 2:
                continue
            # count matched pairs = C(k,2); verify each (or sample if capped)
            for ii in range(k):
                for jj in range(ii + 1, k):
                    combined += 1
                    if not verify_all_combined:
                        continue
                    if max_combined_verify is not None and verified_pairs >= max_combined_verify:
                        # still count but stop verifying — mark in extra
                        continue
                    verified_pairs += 1
                    if verify_combined(E, group[ii], group[jj]):
                        combined_ok += 1
                    else:
                        combined_fail += 1

    merge_s = time.perf_counter() - t0
    T = len(attempts)
    collisions = sum(m * (m - 1) // 2 for m in key_mult.values())
    if collisions > 0:
        S_fit = (T * T) / (2.0 * collisions)
    else:
        S_fit = None
    modeled_2N = (T * T) / (2.0 * RC1_ORDER) if T else 0.0
    ratio = (collisions / modeled_2N) if modeled_2N > 0 else None
    modeled_2S = (T * T) / (2.0 * S_fit) if S_fit else None

    if verify_all_combined and combined > 0 and (max_combined_verify is None or verified_pairs >= combined):
        pass_rate = combined_ok / combined if combined else None
    elif verified_pairs > 0:
        pass_rate = combined_ok / verified_pairs
    else:
        pass_rate = None if recombination else 1.0

    # attempts_to_B: smallest prefix T' where full+combined reach |window|
    # For exhaustive we report based on cumulative if needed; default None here
    return {
        "full_relation_count": full,
        "full_verified": full_verified,
        "full_failed": full_failed,
        "combined_relation_count": combined,
        "combined_verified": combined_ok,
        "combined_failed": combined_fail,
        "combined_verified_pairs": verified_pairs,
        "certificate_pass_rate_combined": pass_rate,
        "residual_support_S_fitted": S_fit,
        "residual_collision_rate_ratio": ratio,
        "max_residual_multiplicity": max(key_mult.values()) if key_mult else 0,
        "residual_key_multiplicity_histogram": dict(sorted(Counter(key_mult.values()).items())),
        "bucket_size_histogram": dict(sorted(hist.items())),
        "distinct_residual_keys": len(key_mult),
        "collision_pair_count": collisions,
        "modeled_T2_over_2N": modeled_2N,
        "modeled_T2_over_2S": modeled_2S,
        "merge_wall_clock_s": merge_s,
        "T": T,
    }


def attempts_to_B_scan(
    E: Curve,
    attempts: list[Attempt],
    window: list[tuple],
    B_target: int | None = None,
) -> tuple[int | None, float | None]:
    """Scan attempts in order; return smallest T where full+combined >= B."""
    if B_target is None:
        B_target = len(window)
    x_in_window = window_x_set(window)
    by_x: dict[int, list[tuple]] = defaultdict(list)
    for P in window:
        by_x[P[0]].append(P)
    first: dict[int, Attempt] = {}
    relations = 0
    for t, a in enumerate(attempts, start=1):
        # full?
        if a.L is not None and a.L[0] in x_in_window:
            for P3 in by_x[a.L[0]]:
                if verify_full(E, a, P3):
                    relations += 1
                    break
        # combined with prior same key
        if a.key in first:
            # each new collision with an existing entry in the bucket adds
            # (current multiplicity) new matched pairs; count +1 for spanning
            # tree style toward B, use matched-pair increment:
            # we approximate by counting each collision event as +1 relation
            # when joining a non-empty bucket (spanning-tree / UF style).
            relations += 1
        first.setdefault(a.key, a)
        # better: track multiplicity
        # redo properly below
    # Proper scan with multiplicity
    mult: dict[int, int] = defaultdict(int)
    relations = 0
    for t, a in enumerate(attempts, start=1):
        if a.L is not None and a.L[0] in x_in_window:
            for P3 in by_x[a.L[0]]:
                if verify_full(E, a, P3):
                    relations += 1
                    break
        m = mult[a.key]
        if m >= 1:
            relations += m  # adds m new matched pairs with prior m entries
        mult[a.key] = m + 1
        if relations >= B_target:
            return t, math.log2(t)
    return None, None


def run_census(
    window_kind: str,
    *,
    hash_key_bits: int | None = None,
    recombination: bool = True,
    pair_indices: list[tuple[int, int]] | None = None,
    verify_all_combined: bool = True,
    max_combined_verify: int | None = None,
) -> CensusResult:
    from runpack import peak_rss_bytes

    F, E, order = build_rc1()
    # Fresh curve object for certificate path
    E_cert = Curve(TableField(N, MODULUS), RC1_A, RC1_B)
    window = enumerate_window(E, "V0" if window_kind in ("V0", "V'_0", "V_prime_0") else "V")
    attempts, identity, collect_s = collect_attempts(
        E, window, pairs=pair_indices, hash_key_bits=hash_key_bits
    )
    stats = merge_and_certify(
        E_cert,
        attempts,
        window,
        recombination=recombination,
        verify_all_combined=verify_all_combined,
        max_combined_verify=max_combined_verify,
    )
    att_B, att_B_log2 = attempts_to_B_scan(E_cert, attempts, window)
    return CensusResult(
        window_kind=window_kind,
        window_size=len(window),
        T=stats["T"],
        identity_sum_pairs=identity,
        full_relation_count=stats["full_relation_count"],
        combined_relation_count=stats["combined_relation_count"],
        combined_verified=stats["combined_verified"],
        combined_failed=stats["combined_failed"],
        certificate_pass_rate_combined=stats["certificate_pass_rate_combined"]
        if stats["certificate_pass_rate_combined"] is not None
        else (1.0 if stats["combined_relation_count"] == 0 else 0.0),
        residual_support_S_fitted=stats["residual_support_S_fitted"],
        residual_collision_rate_ratio=stats["residual_collision_rate_ratio"],
        max_residual_multiplicity=stats["max_residual_multiplicity"],
        residual_value_histogram=stats["residual_key_multiplicity_histogram"],
        attempts_to_B_relations=att_B,
        attempts_to_B_relations_log2=att_B_log2,
        collection_wall_clock_s=collect_s,
        merge_wall_clock_s=stats["merge_wall_clock_s"],
        peak_rss_bytes=peak_rss_bytes(),
        N=order,
        modeled_T2_over_2N=stats["modeled_T2_over_2N"],
        modeled_T2_over_2S=stats["modeled_T2_over_2S"],
        extra={
            "full_verified": stats["full_verified"],
            "full_failed": stats["full_failed"],
            "combined_verified_pairs": stats["combined_verified_pairs"],
            "distinct_residual_keys": stats["distinct_residual_keys"],
            "collision_pair_count": stats["collision_pair_count"],
            "bucket_size_histogram": stats["bucket_size_histogram"],
            "hash_key_bits": hash_key_bits,
            "recombination": recombination,
        },
    )


def subsample_pair_indices(n_window: int, T: int, seed: int) -> list[tuple[int, int]]:
    """Sample T unordered pairs without replacement from C(n,2)."""
    total = n_window * (n_window - 1) // 2
    if T > total:
        raise ValueError(f"T={T} > C({n_window},2)={total}")
    rng = random.Random(seed)

    def unrank(r: int) -> tuple[int, int]:
        # lexicographic unrank of unordered pairs
        i = 0
        while True:
            row = n_window - 1 - i
            if r < row:
                return i, i + 1 + r
            r -= row
            i += 1

    chosen = rng.sample(range(total), T)
    return [unrank(r) for r in chosen]


def generic_zn_census(
    window_size: int,
    seed: int,
    *,
    modulus: int = RC1_ORDER,
    T: int | None = None,
    hash_key_bits: int | None = None,
) -> dict:
    """Z/(4*32603) replica: window = random subset; residual = -(a+b) mod M."""
    rng = random.Random(seed)
    window = rng.sample(range(modulus), window_size)
    n = len(window)
    if T is None:
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    else:
        pairs = subsample_pair_indices(n, T, seed ^ 0x9E3779B9)
    t0 = time.perf_counter()
    keys = []
    identity = 0
    attempts = []
    for i, j in pairs:
        s = (window[i] + window[j]) % modulus
        if s == 0:
            identity += 1
            continue
        L = (-s) % modulus
        key = hash_key(L, hash_key_bits)
        attempts.append((i, j, key, window[i], window[j], L))
        keys.append(key)
    collect_s = time.perf_counter() - t0
    key_mult = Counter(keys)
    collisions = sum(m * (m - 1) // 2 for m in key_mult.values())
    T_eff = len(attempts)
    modeled = (T_eff * T_eff) / (2.0 * modulus) if T_eff else 0.0
    ratio = collisions / modeled if modeled else None
    S_fit = (T_eff * T_eff) / (2.0 * collisions) if collisions else None

    # "full" when residual lands in window set
    wset = set(window)
    full = sum(1 for *_, L in attempts if L in wset)
    # certificate in Z/n: same residual L ⇒ a+b+(-c)+(-d) ≡ 0; opposite ⇒ a+b+c+d ≡ 0
    buckets: dict[int, list] = defaultdict(list)
    for att in attempts:
        buckets[att[2]].append(att)
    combined = 0
    ok = 0
    fail = 0
    for group in buckets.values():
        k = len(group)
        for ii in range(k):
            for jj in range(ii + 1, k):
                combined += 1
                a1, a2, La = group[ii][3], group[ii][4], group[ii][5]
                b1, b2, Lb = group[jj][3], group[jj][4], group[jj][5]
                if La == Lb:
                    if (a1 + a2 - b1 - b2) % modulus == 0:
                        ok += 1
                    else:
                        fail += 1
                elif La == ((-Lb) % modulus):
                    if (a1 + a2 + b1 + b2) % modulus == 0:
                        ok += 1
                    else:
                        fail += 1
                else:
                    # truncated-key false match
                    fail += 1
    return {
        "group": f"Z/{modulus}",
        "window_size": window_size,
        "seed": seed,
        "T": T_eff,
        "identity_sum_pairs": identity,
        "full_relation_count": full,
        "combined_relation_count": combined,
        "combined_verified": ok,
        "combined_failed": fail,
        "certificate_pass_rate_combined": (ok / combined) if combined else 1.0,
        "residual_support_S_fitted": S_fit,
        "residual_collision_rate_ratio": ratio,
        "max_residual_multiplicity": max(key_mult.values()) if key_mult else 0,
        "residual_key_multiplicity_histogram": dict(sorted(Counter(key_mult.values()).items())),
        "modeled_T2_over_2N": modeled,
        "collection_wall_clock_s": collect_s,
        "hash_key_bits": hash_key_bits,
    }


def result_to_metrics(r: CensusResult) -> dict:
    return {
        "window_kind": r.window_kind,
        "window_size": r.window_size,
        "T": r.T,
        "N": r.N,
        "identity_sum_pairs": r.identity_sum_pairs,
        "full_relation_count": r.full_relation_count,
        "combined_relation_count": r.combined_relation_count,
        "combined_verified": r.combined_verified,
        "combined_failed": r.combined_failed,
        "certificate_pass_rate_combined": r.certificate_pass_rate_combined,
        "residual_support_S_fitted": r.residual_support_S_fitted,
        "residual_collision_rate_ratio": r.residual_collision_rate_ratio,
        "max_residual_multiplicity": r.max_residual_multiplicity,
        "residual_value_histogram": r.residual_value_histogram,
        "attempts_to_B_relations": r.attempts_to_B_relations,
        "attempts_to_B_relations_log2": r.attempts_to_B_relations_log2,
        "collection_wall_clock_s": r.collection_wall_clock_s,
        "merge_wall_clock_s": r.merge_wall_clock_s,
        "peak_rss_bytes": r.peak_rss_bytes,
        "modeled_T2_over_2N": r.modeled_T2_over_2N,
        "modeled_T2_over_2S": r.modeled_T2_over_2S,
        **{f"extra_{k}": v for k, v in r.extra.items()},
    }


# ---- Stage 5 optional n=19 Koblitz sibling ---------------------------------
N19 = 19
MOD19 = (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1  # t^19+t^5+t^2+t+1
N19_A = 0
N19_B = 1
N19_ORDER = 4 * 130873  # 523492
N19_WINDOW_DEG = 10  # analogous l ≈ ceil(n/2)


def build_n19() -> tuple[TableField, Curve, int]:
    F = TableField(N19, MOD19)
    E = Curve(F, N19_A, N19_B)
    order = E.count_by_trace()
    if order != N19_ORDER:
        raise RuntimeError(f"n=19 order {order} != {N19_ORDER}")
    return F, E, order


def enumerate_window_n19(E: Curve, kind: str = "V") -> list[tuple]:
    pts: list[tuple] = []
    for x in range(1 << N19_WINDOW_DEG):
        P = E.lift_x(x)
        if P is None:
            continue
        if kind == "V0" and (x & 1) != 0:
            continue
        pts.append(P)
        Pn = E.neg(P)
        if Pn != P:
            pts.append(Pn)
    seen = set()
    out = []
    for P in pts:
        if P in seen:
            continue
        seen.add(P)
        if kind == "V0" and (P[0] & 1) != 0:
            continue
        out.append(P)
    return out


def run_census_n19(
    window_kind: str = "V",
    *,
    hash_key_bits: int | None = None,
    recombination: bool = True,
    verify_all_combined: bool = True,
) -> CensusResult:
    from runpack import peak_rss_bytes

    F, E, order = build_n19()
    E_cert = Curve(TableField(N19, MOD19), N19_A, N19_B)
    window = enumerate_window_n19(E, "V0" if window_kind in ("V0", "V'_0") else "V")
    attempts, identity, collect_s = collect_attempts(E, window, hash_key_bits=hash_key_bits)
    # Temporarily patch RC1_ORDER usages inside merge via local N
    stats = merge_and_certify(
        E_cert,
        attempts,
        window,
        recombination=recombination,
        verify_all_combined=verify_all_combined,
    )
    # Recompute ratio against n19 order (merge_and_certify uses RC1_ORDER)
    T = stats["T"]
    collisions = stats["collision_pair_count"]
    modeled_2N = (T * T) / (2.0 * order) if T else 0.0
    ratio = (collisions / modeled_2N) if modeled_2N > 0 else None
    S_fit = (T * T) / (2.0 * collisions) if collisions else None
    att_B, att_B_log2 = attempts_to_B_scan(E_cert, attempts, window)
    return CensusResult(
        window_kind=f"n19_{window_kind}",
        window_size=len(window),
        T=T,
        identity_sum_pairs=identity,
        full_relation_count=stats["full_relation_count"],
        combined_relation_count=stats["combined_relation_count"],
        combined_verified=stats["combined_verified"],
        combined_failed=stats["combined_failed"],
        certificate_pass_rate_combined=stats["certificate_pass_rate_combined"]
        if stats["certificate_pass_rate_combined"] is not None
        else (1.0 if stats["combined_relation_count"] == 0 else 0.0),
        residual_support_S_fitted=S_fit,
        residual_collision_rate_ratio=ratio,
        max_residual_multiplicity=stats["max_residual_multiplicity"],
        residual_value_histogram=stats["residual_key_multiplicity_histogram"],
        attempts_to_B_relations=att_B,
        attempts_to_B_relations_log2=att_B_log2,
        collection_wall_clock_s=collect_s,
        merge_wall_clock_s=stats["merge_wall_clock_s"],
        peak_rss_bytes=peak_rss_bytes(),
        N=order,
        modeled_T2_over_2N=modeled_2N,
        modeled_T2_over_2S=(T * T) / (2.0 * S_fit) if S_fit else None,
        extra={
            "full_verified": stats["full_verified"],
            "full_failed": stats["full_failed"],
            "combined_verified_pairs": stats["combined_verified_pairs"],
            "distinct_residual_keys": stats["distinct_residual_keys"],
            "collision_pair_count": collisions,
            "bucket_size_histogram": stats["bucket_size_histogram"],
            "hash_key_bits": hash_key_bits,
            "recombination": recombination,
            "curve": "y^2+xy=x^3+1",
            "n": 19,
            "modulus": hex(MOD19),
        },
    )
