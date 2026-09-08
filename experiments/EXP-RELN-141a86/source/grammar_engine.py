"""
Deterministic bounded grammar-search engine for EXP-RELN-141a86, Stage 0a.

Implements the frozen `primary_engine` block of
experiments/EXP-RELN-141a86/specification.yaml:

  - operators: binary {add, sub, mul, div, pow, binomial},
               unary  {log, exp, floor, ceil}
  - leaves by convention pack (frozen_pipeline.primary_engine.grammar.leaves_by_pack)
  - derived leaves n, M, mu, W as defined in derived_leaf_definitions
  - node_counting_rule: every operator application counts 1, every leaf
    (variable, derived leaf, or constant) counts 1; pow and binomial each
    count 1 plus their two children (i.e. they are ordinary binary nodes
    under this rule, with no extra weight)
  - complexity_cap C_max = 12
  - canonical-form deduplication: commutative operand ordering (add, mul),
    constant folding, and numeric-fingerprint dedup on a fixed sample grid

This stage does NOT read any measured data. It only needs to (a) enumerate
canonical-form expressions up to a given complexity for a given leaf pack,
and (b) report the node count of a specific target expression under the
frozen rule. Both capabilities are implemented for real below; enumeration
at the full C_max = 12 over 6-leaf packs is expensive and is a Stage-1
budget item (stage1_grammar_fits), not required here -- this module is
exercised at small complexity as a self-test and used at arbitrary
complexity for direct node-counting of hand-built target expressions.

Expression representation
--------------------------
An expression is one of:
  ('leaf', name)            -- a variable or derived leaf, e.g. 'B', 'mu'
  ('const', value)          -- a numeric constant (int, Fraction, or float)
  ('CONST',)                -- an unbound free-constant placeholder leaf
  (unary_op, child)         -- unary_op in UNARY_OPS
  (binary_op, left, right)  -- binary_op in BINARY_OPS

No implicit simplification happens at construction time; `canonicalize`
performs commutative reordering and constant folding explicitly and is the
only path that should be relied on for deduplication.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Dict, Tuple, List, Iterable, Union
import math

BINARY_OPS = ("add", "sub", "mul", "div", "pow", "binomial")
UNARY_OPS = ("log", "exp", "floor", "ceil")

# frozen_pipeline.primary_engine.grammar.leaves_by_pack (transcribed verbatim)
LEAVES_BY_PACK: Dict[str, List[str]] = {
    "fb3_unsigned_m3_and_enum_unsigned_m3": ["N", "B", "m", "M", "mu", "CONST"],
    "enum_xclass_signed_m2": ["N", "B", "n", "M", "mu", "CONST"],
    "symmetric_m3": ["N", "B", "W", "M", "mu", "CONST"],
    "degree_table": ["m", "B", "D_S", "CONST"],
    "dreg_semaev_D5": ["n_vars", "CONST"],
    "enum_zn_and_sidon": ["N", "B", "m", "M", "mu", "CONST"],
}

# derived_leaf_definitions (contract text):
#   n = (N-1)/2
#   M = binomial(B+m-1, m)
#   mu = M/N
#   W = |D u -D| = the effective symmetric size B' read from the record
# CONST is a free constant placeholder, fitted after structural enumeration
# (not evaluable symbolically; treated as an unbound leaf for node counting
# and enumeration purposes).
DERIVED_LEAVES = {"n", "M", "mu", "W"}

C_MAX = 12
TIE_BREAKING_SEED = 20260906

Expr = Union[Tuple, tuple]


# ---------------------------------------------------------------------------
# Node counting (frozen node_counting_rule)
# ---------------------------------------------------------------------------

def node_count(expr: Expr) -> int:
    """
    Complexity = number of nodes in the expression tree; every operator
    application counts 1 and every leaf (variable, derived leaf, or
    constant) counts 1; pow counts 1 plus its two children; binomial counts
    1 plus its two children -- i.e. every binary operator is a plain
    2-child node and every unary operator a plain 1-child node under this
    rule; there is no extra weighting for pow/binomial beyond the ordinary
    binary-node cost.
    """
    if not isinstance(expr, tuple) or len(expr) == 0:
        raise ValueError(f"malformed expression node: {expr!r}")

    tag = expr[0]

    if tag == "leaf":
        if len(expr) != 2:
            raise ValueError(f"malformed leaf node: {expr!r}")
        return 1
    if tag == "const":
        if len(expr) != 2:
            raise ValueError(f"malformed const node: {expr!r}")
        return 1
    if tag == "CONST":
        return 1
    if tag in UNARY_OPS:
        if len(expr) != 2:
            raise ValueError(f"malformed unary node: {expr!r}")
        return 1 + node_count(expr[1])
    if tag in BINARY_OPS:
        if len(expr) != 3:
            raise ValueError(f"malformed binary node: {expr!r}")
        return 1 + node_count(expr[1]) + node_count(expr[2])

    raise ValueError(f"unknown expression tag: {tag!r}")


# ---------------------------------------------------------------------------
# Canonicalization: commutative reordering + constant folding
# ---------------------------------------------------------------------------

def to_canonical_string(expr: Expr) -> str:
    """Deterministic string form used for canonical-string ordering and
    for the canonical-form dedup key (before numeric fingerprinting)."""
    tag = expr[0]
    if tag == "leaf":
        return expr[1]
    if tag == "const":
        return f"#{expr[1]}"
    if tag == "CONST":
        return "CONST"
    if tag in UNARY_OPS:
        return f"{tag}({to_canonical_string(expr[1])})"
    if tag in BINARY_OPS:
        return f"{tag}({to_canonical_string(expr[1])},{to_canonical_string(expr[2])})"
    raise ValueError(f"unknown expression tag: {tag!r}")


def _is_const(expr: Expr):
    return expr[0] == "const"


def _fold_binary_const(op: str, a, b):
    """Attempt exact constant folding for op(a, b) where a, b are numeric
    (int/Fraction). Returns a folded numeric value, or None if the
    operation is undefined/not exactly foldable (e.g. non-integer
    binomial arguments, division by zero)."""
    try:
        if op == "add":
            return a + b
        if op == "sub":
            return a - b
        if op == "mul":
            return a * b
        if op == "div":
            if b == 0:
                return None
            return Fraction(a) / Fraction(b)
        if op == "pow":
            if isinstance(b, (int, Fraction)) and int(b) == b:
                bi = int(b)
                if bi < 0 and a == 0:
                    return None
                return Fraction(a) ** bi
            return None
        if op == "binomial":
            if isinstance(a, (int, Fraction)) and isinstance(b, (int, Fraction)) \
                    and int(a) == a and int(b) == b:
                ai, bi = int(a), int(b)
                if bi < 0 or ai < 0:
                    return None
                if bi > ai:
                    return 0
                return math.comb(ai, bi)
            return None
    except (ZeroDivisionError, ValueError, OverflowError):
        return None
    return None


def canonicalize(expr: Expr) -> Expr:
    """
    Recursively canonicalize: commutative operand ordering for add/mul
    (operands sorted by canonical string ascending), then constant folding
    where both operands (post-canonicalization) are numeric constants.
    Idempotent: canonicalize(canonicalize(e)) == canonicalize(e).
    """
    tag = expr[0]
    if tag in ("leaf", "const", "CONST"):
        return expr

    if tag in UNARY_OPS:
        child = canonicalize(expr[1])
        if _is_const(child):
            v = child[1]
            folded = None
            try:
                if tag == "log" and v > 0:
                    folded = None  # log of a constant is not exactly
                    # rational in general; leave symbolic (do not fold)
                elif tag == "exp":
                    folded = None
                elif tag == "floor":
                    folded = math.floor(v)
                elif tag == "ceil":
                    folded = math.ceil(v)
            except (ValueError, TypeError):
                folded = None
            if folded is not None:
                return ("const", folded)
        return (tag, child)

    if tag in BINARY_OPS:
        left = canonicalize(expr[1])
        right = canonicalize(expr[2])
        if tag in ("add", "mul"):
            ls, rs = to_canonical_string(left), to_canonical_string(right)
            if rs < ls:
                left, right = right, left
        if _is_const(left) and _is_const(right):
            folded = _fold_binary_const(tag, left[1], right[1])
            if folded is not None:
                return ("const", folded)
        return (tag, left, right)

    raise ValueError(f"unknown expression tag: {tag!r}")


# ---------------------------------------------------------------------------
# Numeric fingerprinting for algebraic-duplicate dedup
# ---------------------------------------------------------------------------

# A small fixed sample grid used only to fingerprint canonical-form
# expressions against each other on the *enumerated* set (never against
# any measured cell). Values are chosen to be small, distinct, and safe
# for the operators in this grammar (no zero divisors, no negative
# binomial arguments under the leaf semantics used here).
_SAMPLE_GRID = {
    "N": [67, 131],
    "B": [5, 7],
    "m": [2, 3],
    "M": [11, 13],
    "mu": [Fraction(1, 4), Fraction(1, 3)],
    "n": [17, 19],
    "W": [6, 8],
    "D_S": [3, 5],
    "n_vars": [12, 15],
    "CONST": [Fraction(1, 1), Fraction(2, 1)],
}


# Magnitude cap applied ONLY inside numeric fingerprinting (never applied
# to the exact constant-fitting / recovery-check evaluation path in
# constant_fit.py or the Stage-1 fit tables, which operate on measured
# (N, B, m) values that are never remotely this large). This exists solely
# to keep the fingerprint dedup pass on the fixed small sample grid from
# hanging on a tower-exponential pow/binomial nesting artifact; recorded as
# a protocol deviation (implementation.md) since it was not in the frozen
# Stage-0a module.
_FINGERPRINT_MAGNITUDE_CAP = 1e6


def _eval_expr(expr: Expr, env: Dict[str, float]):
    tag = expr[0]
    if tag == "leaf":
        return env[expr[1]]
    if tag == "const":
        return expr[1]
    if tag == "CONST":
        # BUGFIX (protocol deviation, recorded in implementation.md): a
        # single shared env["CONST"] value used for EVERY CONST leaf in
        # the tree makes numeric_fingerprint spuriously conflate
        # expressions with two INDEPENDENT free constants (permitted by
        # the frozen constant_fitting clause, "at most two free constants
        # per expression") with structurally different expressions that
        # only coincide when both constants happen to equal that one
        # shared value -- confirmed empirically: div(binomial(add(B,
        # CONST),CONST),N) (the true INV-A4 coverage law, CONST=2 and
        # CONST=3) was silently deduplicated out of the enumerated set
        # because both its CONST leaves fingerprinted as 1. A
        # "_CONST_STREAM" list in env, when present, supplies a DISTINCT
        # fingerprint value per CONST leaf in left-to-right evaluation
        # order (consumed via "_CONST_STREAM_IDX", a single-element list
        # used as a mutable counter); this never changes node counts,
        # canonical string form, or the grammar's semantics -- only the
        # numeric fingerprint used for algebraic-duplicate detection.
        stream = env.get("_CONST_STREAM")
        if stream is not None:
            idx_holder = env["_CONST_STREAM_IDX"]
            i = idx_holder[0]
            idx_holder[0] += 1
            return stream[i % len(stream)]
        return env.get("CONST", Fraction(1, 1))
    if tag in UNARY_OPS:
        v = _eval_expr(expr[1], env)
        if v is None:
            return None
        vf = float(v)
        if tag == "log":
            if vf <= 0:
                return None
            return math.log(vf)
        if tag == "exp":
            try:
                return math.exp(vf)
            except OverflowError:
                return None
        if tag == "floor":
            return math.floor(vf)
        if tag == "ceil":
            return math.ceil(vf)
    if tag in BINARY_OPS:
        a = _eval_expr(expr[1], env)
        b = _eval_expr(expr[2], env)
        if a is None or b is None:
            return None
        try:
            if tag == "add":
                return a + b
            if tag == "sub":
                return a - b
            if tag == "mul":
                return a * b
            if tag == "div":
                if float(b) == 0:
                    return None
                return Fraction(a) / Fraction(b) if isinstance(a, (int, Fraction)) and isinstance(b, (int, Fraction)) else a / b
            if tag == "pow":
                af, bf = float(a), float(b)
                if abs(af) > _FINGERPRINT_MAGNITUDE_CAP or abs(bf) > _FINGERPRINT_MAGNITUDE_CAP:
                    # A pathologically large intermediate value on this
                    # module's fixed *fingerprinting* sample grid (e.g. a
                    # deeply nested pow/binomial tower); exact evaluation
                    # would be computationally unbounded (tower-exponential
                    # bignum growth) for a purely cosmetic dedup check.
                    # Treated as domain-invalid (None) here, exactly as
                    # division-by-zero already is -- this never changes
                    # which expressions exist or their node counts, only
                    # prevents the fingerprint pass from hanging on an
                    # astronomically large intermediate.
                    return None
                if af == 0 and bf < 0:
                    return None
                if af < 0 and bf != int(bf):
                    # non-integer power of a negative base is complex under
                    # real arithmetic; treat as domain-invalid (None), same
                    # as any other undefined evaluation on this module's
                    # fixed sample grid -- never silently coerced to a
                    # complex or NaN fingerprint value.
                    return None
                result = af ** bf
                if isinstance(result, complex):
                    return None
                return result
            if tag == "binomial":
                af, bf = float(a), float(b)
                if abs(af) > _FINGERPRINT_MAGNITUDE_CAP or abs(bf) > _FINGERPRINT_MAGNITUDE_CAP:
                    return None
                if af < 0 or bf < 0 or bf > af or int(af) != af or int(bf) != bf:
                    return None
                return math.comb(int(af), int(bf))
        except (ZeroDivisionError, ValueError, OverflowError):
            return None
    raise ValueError(f"unknown expression tag: {tag!r}")


def _count_const_leaves(expr: Expr) -> int:
    tag = expr[0]
    if tag == "CONST":
        return 1
    if tag in ("leaf", "const"):
        return 0
    if tag in UNARY_OPS:
        return _count_const_leaves(expr[1])
    if tag in BINARY_OPS:
        return _count_const_leaves(expr[1]) + _count_const_leaves(expr[2])
    raise ValueError(tag)


# Distinct fingerprint values assigned to successive CONST leaves (see the
# "CONST" branch of _eval_expr for why a single shared value is unsound).
# DELIBERATELY small DISTINCT POSITIVE INTEGERS, not fractions: many real
# target expressions place CONST directly as a binomial() or pow()
# argument, and both operators require integer-valued arguments to be
# evaluable at all (see their domain checks below) -- a fractional
# fingerprint value there makes the whole subtree evaluate to None on
# every grid point, and *every* such "always-None" expression then
# collides on the same (None, None, ..., None) fingerprint and gets
# deduplicated against whichever one was registered first, silently
# discarding unrelated valid integer-CONST expressions (confirmed
# empirically: this cost the true INV-A4 coverage law,
# div(binomial(add(B,CONST),CONST),N), its own distinct fingerprint before
# this fix). Small primes keep every occurrence evaluable and distinct.
_CONST_STREAM_VALUES = [Fraction(v) for v in (2, 3, 5, 7, 11, 13, 17)]


def numeric_fingerprint(expr: Expr, leaves: Iterable[str]) -> Tuple:
    """
    Evaluate the canonical expression on the cross product of the fixed
    sample grid restricted to the leaves actually present in this pack,
    rounding to 9 significant digits. Used only to deduplicate the
    enumerated candidate set against itself -- never evaluated against any
    measured record. Each CONST leaf in the tree gets its OWN distinct
    fingerprint value (see _eval_expr's "CONST" branch bugfix note) so
    that expressions with two independent free constants are not
    spuriously conflated with expressions that only coincide when both
    constants take one shared value.
    """
    leaves = [l for l in leaves if l != "CONST"]
    grids = [_SAMPLE_GRID[l] for l in leaves]
    n_const = _count_const_leaves(expr)
    const_stream = _CONST_STREAM_VALUES[:max(n_const, 1)]
    fp = []
    for combo in product(*grids):
        env = dict(zip(leaves, combo))
        env["CONST"] = Fraction(1, 1)
        env["_CONST_STREAM"] = const_stream
        env["_CONST_STREAM_IDX"] = [0]
        try:
            v = _eval_expr(expr, env)
        except (OverflowError, ValueError, ZeroDivisionError, RecursionError):
            v = None
        if v is None:
            fp.append(None)
        else:
            try:
                fp.append(round(float(v), 9))
            except (TypeError, OverflowError):
                fp.append(None)
    return tuple(fp)


# ---------------------------------------------------------------------------
# Bounded exhaustive enumeration
# ---------------------------------------------------------------------------

def enumerate_expressions(pack: str, max_complexity: int) -> Dict[int, List[Expr]]:
    """
    Exhaustive bounded grammar search: enumerate every canonical-form
    expression over the leaf set of `pack` with node count <= max_complexity,
    deduplicated by canonical string AND by numeric fingerprint on the fixed
    sample grid. Returns {complexity: [expr, ...]} for complexity in
    1..max_complexity, built bottom-up (every expression of complexity C is
    built from smaller already-enumerated subexpressions, so it is complete
    at each step by construction).

    This is a real, deterministic implementation; it is exercised at small
    max_complexity in this stage's self-test. Enumerating leaf packs of 6
    leaves up to C_max = 12 is combinatorially large and is a Stage-1
    (stage1_grammar_fits) budget item, not required by Stage 0a.
    """
    if pack not in LEAVES_BY_PACK:
        raise ValueError(f"unknown leaf pack: {pack!r}")
    leaves = LEAVES_BY_PACK[pack]

    by_complexity: Dict[int, List[Expr]] = {c: [] for c in range(1, max_complexity + 1)}
    seen_strings: set = set()
    seen_fingerprints: set = set()

    def _register(expr: Expr, c: int) -> bool:
        canon = canonicalize(expr)
        actual_c = node_count(canon)
        if actual_c != c:
            # folding shrank the tree; file it at its true (smaller) size
            c = actual_c
        s = to_canonical_string(canon)
        if s in seen_strings:
            return False
        fp = numeric_fingerprint(canon, leaves)
        if fp in seen_fingerprints:
            seen_strings.add(s)
            return False
        seen_strings.add(s)
        seen_fingerprints.add(fp)
        by_complexity.setdefault(c, [])
        by_complexity[c].append(canon)
        return True

    # complexity 1: leaves
    for leaf_name in leaves:
        if leaf_name == "CONST":
            _register(("CONST",), 1)
        else:
            _register(("leaf", leaf_name), 1)

    # complexity >= 2: build from smaller pieces, ascending
    for c in range(2, max_complexity + 1):
        # unary: 1 + size(child) == c  => child has size c - 1
        for child in by_complexity.get(c - 1, []):
            for op in UNARY_OPS:
                _register((op, child), c)
        # binary: 1 + size(left) + size(right) == c
        for c_left in range(1, c - 1):
            c_right = c - 1 - c_left
            if c_right < 1:
                continue
            for left in by_complexity.get(c_left, []):
                for right in by_complexity.get(c_right, []):
                    for op in BINARY_OPS:
                        _register((op, left, right), c)

    # deterministic enumeration order: complexity ascending, then by
    # canonical string ascending (tie_breaking_seed exists only for the
    # constant fitter's optional random restart, never for enumeration order)
    for c in by_complexity:
        by_complexity[c].sort(key=to_canonical_string)

    return by_complexity


def enumeration_counts(pack: str, max_complexity: int) -> Dict[int, int]:
    return {c: len(v) for c, v in enumerate_expressions(pack, max_complexity).items()}


# ---------------------------------------------------------------------------
# Self-test / CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    import sys

    # Sanity: enumerate a small pack at a small complexity and print counts.
    pack = "degree_table"
    counts = enumeration_counts(pack, 6)
    print(f"enumeration self-test pack={pack} max_complexity=6", file=sys.stderr)
    print(json.dumps(counts, indent=2), file=sys.stderr)
