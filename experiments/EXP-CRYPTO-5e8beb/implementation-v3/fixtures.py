"""Literal laws, partitions and ordering for EXP-CRYPTO-5e8beb.

This module holds only *data* and *pure functions* that reconstruct the frozen
finite fixtures from `experiments/EXP-CRYPTO-5e8beb/specification.yaml`. It
performs **no computation on import**: every partition/permutation is built by
calling a function explicitly, never at module load time.

Scope discipline: this module does not evaluate any fixture, run any kernel,
or produce any experiment output. `scientific_execution_authorized: false` in
the frozen specification and `maximum_runs: 0` in the task handoff bind this
whole implementation task; nothing here is invoked by the executor.

Spec cross-reference (`experiments/EXP-CRYPTO-5e8beb/specification.yaml`):
  - `fixture_definition.prime_partitions` -> PRIME_NS, Q_VALUES, SEEDS,
    generate_permutation, build_matched_feature.
  - `fixture_definition.composite_partitions` -> COMPOSITE_N, COMPOSITE_FEATURES.
  - `fixture_definition.representative` -> representative().
  - `fixture_definition.description` -> table_bits(), canonical_descriptor().
  - `kernels` -> RAW_KERNEL_LAWS, p_translation_law, u_uniform_law,
    KERNEL_ORDER.
  - `ordering.partitions` / `ordering.kernels` -> iter_partition_specs(),
    KERNEL_ORDER.
  - `fixture_definition.prime_partitions.duplicate_rule` -> feature_hash(),
    duplicate_groups().
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

EXP_ID = "EXP-CRYPTO-5e8beb"

# --- fixed literal panel parameters (specification.fixture_definition) -----

PRIME_NS: Tuple[int, ...] = (11, 17)
Q_VALUES: Tuple[int, ...] = (2, 3, 4, 5)
MATCHED_PER_COORDINATE = 32
SEEDS: Tuple[int, ...] = tuple(range(MATCHED_PER_COORDINATE))

COMPOSITE_N = 15
COMPOSITE_FEATURES: Tuple[str, ...] = ("mod3", "mod5", "identity", "constant")

FIXED_COUNTS = {
    "partitions_C11": 134,
    "partitions_C17": 134,
    "partitions_C15": 4,
    "main_partitions": 272,
}


# --- literal fresh-kernel laws (specification.kernels) ----------------------
# Raw (unreduced) translation laws: {label: {signed_delta: Fraction}}.
# Residues are reduced modulo N by reduce_law() in kernels.py, which also
# enumerates them in ascending order per `ordering.translation_order`.

RAW_KERNEL_LAWS: Dict[str, dict] = {
    "R1": {
        "labels": [0],
        "nu": {0: Fraction(1)},
        "mu": {0: {-1: Fraction(1, 2), 1: Fraction(1, 2)}},
    },
    "R2": {
        "labels": [0],
        "nu": {0: Fraction(1)},
        "mu": {0: {-1: Fraction(1, 4), 0: Fraction(1, 2), 1: Fraction(1, 4)}},
    },
    "R3": {
        "labels": [0],
        "nu": {0: Fraction(1)},
        "mu": {0: {-1: Fraction(1, 4), 1: Fraction(3, 4)}},
    },
    "R4": {
        "labels": [0, 1],
        "nu": {0: Fraction(1, 2), 1: Fraction(1, 2)},
        "mu": {
            0: {-1: Fraction(1, 2), 1: Fraction(1, 2)},
            1: {-2: Fraction(1, 2), 2: Fraction(1, 2)},
        },
    },
}

# Ordering of the six declared kernels (specification.ordering.kernels).
KERNEL_ORDER: Tuple[str, ...] = ("R1", "R2", "R3", "R4", "P", "U")


def p_translation_law(N: int) -> dict:
    """P: all a=0..N-1 public, uniform 1/N; translation deterministically a."""
    if N <= 0:
        raise ValueError("N must be positive")
    labels = list(range(N))
    nu = {a: Fraction(1, N) for a in labels}
    mu = {a: {a: Fraction(1)} for a in labels}
    return {"labels": labels, "nu": nu, "mu": mu}


def u_uniform_law(N: int) -> dict:
    """U: single public label 0; private translation fresh uniform 1/N."""
    if N <= 0:
        raise ValueError("N must be positive")
    return {
        "labels": [0],
        "nu": {0: Fraction(1)},
        "mu": {0: {a: Fraction(1, N) for a in range(N)}},
    }


def raw_law_for(kernel_name: str, N: int) -> dict:
    """Return the raw (pre-reduction) law dict for any of the six kernels."""
    if kernel_name in RAW_KERNEL_LAWS:
        return RAW_KERNEL_LAWS[kernel_name]
    if kernel_name == "P":
        return p_translation_law(N)
    if kernel_name == "U":
        return u_uniform_law(N)
    raise KeyError(f"unknown kernel {kernel_name!r}")


# --- representative rule (specification.fixture_definition.representative) --

def representative(states: Sequence[int]) -> int:
    """The least integer state in a nonempty cell; fixed for all kernels/horizons."""
    if not states:
        raise ValueError("empty fiber has no representative")
    return min(states)


# --- table_bits (specification.fixture_definition.description) -------------

def bits_per_symbol(alphabet_size: int) -> int:
    """Integer bit length of (B-1); zero for B=1 (per design-note table_bits rule)."""
    if alphabet_size <= 0:
        raise ValueError("alphabet_size must be positive")
    return (alphabet_size - 1).bit_length()


def table_bits(N: int, alphabet_size: int) -> int:
    return N * bits_per_symbol(alphabet_size)


# --- SHA256 rejection-shuffle generation ------------------------------------
# specification.fixture_definition.prime_partitions.generation, reproduced
# verbatim: Fisher-Yates with SHA256-based rejection sampling, one UTF-8
# message per digest draw, counter incremented after every digest (including
# rejected ones). No RNG library or alternate seed source is used.

def _digest_int(N: int, q: int, seed: int, counter: int) -> int:
    message = f"{EXP_ID}|N={N}|q={q}|seed={seed}|counter={counter}".encode("utf-8")
    digest = hashlib.sha256(message).digest()
    return int.from_bytes(digest, "big")


@dataclass(frozen=True)
class PermutationDraw:
    permutation: Tuple[int, ...]
    total_digests: int
    rejected_digests: int


def generate_permutation(N: int, q: int, seed: int) -> PermutationDraw:
    """Reproduce the exact SHA256-rejection Fisher-Yates shuffle of 0..N-1."""
    permutation = list(range(N))
    counter = 0
    rejected = 0
    for i in range(N - 1, 0, -1):
        modulus = i + 1
        limit = (2 ** 256 // modulus) * modulus
        while True:
            z = _digest_int(N, q, seed, counter)
            counter += 1
            if z < limit:
                j = z % modulus
                break
            rejected += 1
        permutation[i], permutation[j] = permutation[j], permutation[i]
    return PermutationDraw(tuple(permutation), counter, rejected)


# --- feature construction ----------------------------------------------------

def coordinate_cell_sizes(N: int, q: int) -> List[int]:
    """Exact ordered cell sizes c_b = #{x : x mod q = b}, b=0..q-1 ascending."""
    sizes = [0] * q
    for x in range(N):
        sizes[x % q] += 1
    return sizes


def coordinate_feature(N: int, q: int) -> Tuple[int, ...]:
    return tuple(x % q for x in range(N))


def identity_feature(N: int) -> Tuple[int, ...]:
    return tuple(range(N))


def constant_feature(N: int) -> Tuple[int, ...]:
    return tuple(0 for _ in range(N))


def composite_feature(N: int, name: str) -> Tuple[int, ...]:
    """The four C15 features: 'mod3', 'mod5', 'identity', 'constant'."""
    if name == "mod3":
        return tuple(x % 3 for x in range(N))
    if name == "mod5":
        return tuple(x % 5 for x in range(N))
    if name == "identity":
        return identity_feature(N)
    if name == "constant":
        return constant_feature(N)
    raise KeyError(f"unknown composite feature {name!r}")


@dataclass(frozen=True)
class MatchedBuild:
    feature: Tuple[int, ...]
    draw: PermutationDraw


def build_matched_feature(N: int, q: int, seed: int) -> MatchedBuild:
    """Null/matched partition: same ordered cell sizes as coordinate v(x)=x mod q,
    with the SHA256-shuffled permutation assigning which states occupy each
    label's chunk (specification.fixture_definition.prime_partitions.matching).
    """
    sizes = coordinate_cell_sizes(N, q)
    draw = generate_permutation(N, q, seed)
    feature = [None] * N
    idx = 0
    for label, size in enumerate(sizes):
        for _ in range(size):
            state = draw.permutation[idx]
            idx += 1
            feature[state] = label
    assert idx == N and all(v is not None for v in feature)
    return MatchedBuild(tuple(feature), draw)


def cell_sizes_of(feature: Sequence[int]) -> Dict[int, int]:
    sizes: Dict[int, int] = {}
    for label in feature:
        sizes[label] = sizes.get(label, 0) + 1
    return dict(sorted(sizes.items()))


# --- partition specs and fixed ordering (specification.ordering.partitions) -

@dataclass(frozen=True)
class PartitionSpec:
    index: int          # 1..272, fixed_counts.main_partitions
    N: int
    kind: str            # "coordinate" | "matched" | "identity" | "constant"
                          # | "mod3" | "mod5" (composite N=15 reuses "identity"/"constant")
    q: Optional[int] = None
    seed: Optional[int] = None


def iter_partition_specs():
    """Yield the fixed, ordered list of all 272 PartitionSpec descriptors.

    Order: N=11 then N=17; within each N, q ascending (coordinate then seeds
    0..31), then identity, then constant; N=15 last with mod3, mod5, identity,
    constant (specification.ordering.partitions). This function only builds
    lightweight descriptors -- no feature table, permutation or hash is
    computed here.
    """
    index = 1
    for N in PRIME_NS:
        for q in Q_VALUES:
            yield PartitionSpec(index, N, "coordinate", q=q)
            index += 1
            for seed in SEEDS:
                yield PartitionSpec(index, N, "matched", q=q, seed=seed)
                index += 1
        yield PartitionSpec(index, N, "identity")
        index += 1
        yield PartitionSpec(index, N, "constant")
        index += 1
    for name in COMPOSITE_FEATURES:
        yield PartitionSpec(index, COMPOSITE_N, name)
        index += 1


def spec_count() -> int:
    return sum(1 for _ in iter_partition_specs())


@dataclass(frozen=True)
class PartitionRecord:
    spec: PartitionSpec
    feature: Tuple[int, ...]
    cell_sizes: Dict[int, int]
    generation: Optional[PermutationDraw]  # None for deterministic kinds
    table_bits: int
    feature_hash: str


def build_partition(spec: PartitionSpec) -> PartitionRecord:
    """Materialize one partition's feature table from its fixed descriptor.

    This performs the deterministic combinatorial construction described by
    the frozen specification (a SHA256 rejection shuffle for "matched" kinds,
    plain modular/identity/constant formulas otherwise). It is a pure,
    on-demand function: calling it is part of implementing the diagnostic,
    not of running the scientific panel, which this task does not authorize.
    """
    generation = None
    if spec.kind == "coordinate":
        feature = coordinate_feature(spec.N, spec.q)
    elif spec.kind == "matched":
        build = build_matched_feature(spec.N, spec.q, spec.seed)
        feature = build.feature
        generation = build.draw
    elif spec.kind == "identity":
        feature = identity_feature(spec.N)
    elif spec.kind == "constant":
        feature = constant_feature(spec.N)
    elif spec.kind in ("mod3", "mod5"):
        feature = composite_feature(spec.N, spec.kind)
    else:
        raise KeyError(f"unknown partition kind {spec.kind!r}")
    sizes = cell_sizes_of(feature)
    bits = table_bits(spec.N, len(sizes))
    return PartitionRecord(spec, feature, sizes, generation, bits, feature_hash(feature))


# --- descriptors, canonicalization and duplicate reporting ------------------

def canonical_feature_bytes(feature: Sequence[int]) -> bytes:
    """Canonical descriptor bytes: ascending-state-order label sequence."""
    return ",".join(str(b) for b in feature).encode("ascii")


def feature_hash(feature: Sequence[int]) -> str:
    return hashlib.sha256(canonical_feature_bytes(feature)).hexdigest()


def canonical_descriptor(record: PartitionRecord) -> dict:
    """A descriptor dict suitable for description.json; no file I/O here."""
    spec = record.spec
    return {
        "index": spec.index,
        "N": spec.N,
        "kind": spec.kind,
        "q": spec.q,
        "seed": spec.seed,
        "cell_sizes": record.cell_sizes,
        "table_bits": record.table_bits,
        "feature_hash": record.feature_hash,
        "generation_total_digests": record.generation.total_digests if record.generation else None,
        "generation_rejected_digests": record.generation.rejected_digests if record.generation else None,
    }


def duplicate_groups(records: Sequence[PartitionRecord]) -> Dict[str, List[int]]:
    """Group partition indices sharing an identical canonical feature hash.

    Per `duplicate_rule`: every seed is retained regardless of duplication or
    coincidence with the coordinate feature; this only *reports* coincidences,
    it never deduplicates, reweights or drops a labeled seed.
    """
    groups: Dict[str, List[int]] = {}
    for record in records:
        groups.setdefault(record.feature_hash, []).append(record.spec.index)
    return {h: idxs for h, idxs in groups.items() if len(idxs) > 1}
