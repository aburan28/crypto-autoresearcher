"""CNF-XOR encoder for descended Semaev-S_3 PDP systems (EXP-BINSTD-a8efe2).

Encodes S_3(x1,x2,x3) = target over F_{2^n} with xi in the degree-<l
polynomial-basis window V_l. Field multiplication expands via
schoolbook-plus-reduction under a chosen irreducible; XOR-clause widths
and Tseitin substitution-variable counts are the encoder-level c_leaf
proxies. No WDSat / SAT solve required.

Symbolic bits are XOR-of-monomials (monomials = bitmasks over core vars,
plus an optional constant bit tracked separately). Degree-2+ monomials
are Tseitin-substituted into XOR clauses.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable

from gf2n import Field, clmul, pmod


# ---------------------------------------------------------------------------
# Symbolic bit = (linear XOR of core vars via bitmask-of-degree-1, constant,
#                 set of higher-degree monomial bitmasks)
# We represent a Boolean polynomial as a frozenset of monomials, where each
# monomial is an int bitmask over the ml core variables. The empty monomial
# (mask 0) is the constant 1.
# ---------------------------------------------------------------------------

Poly = frozenset  # frozenset[int] of monomial masks


def poly_add(a: Poly, b: Poly) -> Poly:
    return frozenset(a.symmetric_difference(b))


def poly_const(bit: int) -> Poly:
    return frozenset({0}) if bit else frozenset()


def poly_var(idx: int) -> Poly:
    return frozenset({1 << idx})


def poly_mul(a: Poly, b: Poly) -> Poly:
    """Multiply two squarefree-ish Boolean polys over F_2 (monomial OR)."""
    out: dict[int, int] = {}
    for m1 in a:
        for m2 in b:
            # Boolean: x_i^2 = x_i, so OR bits; over F_2 char, field bits
            # are already 0/1 so for ANF of boolean functions x^2=x.
            m = m1 | m2
            out[m] = out.get(m, 0) ^ 1
    return frozenset(m for m, c in out.items() if c)


@dataclass
class SymFieldElem:
    """n symbolic bits, each a Poly over core variables."""

    bits: list  # list[Poly]
    n: int

    @staticmethod
    def zero(n: int) -> "SymFieldElem":
        return SymFieldElem([frozenset() for _ in range(n)], n)

    @staticmethod
    def from_const(val: int, n: int) -> "SymFieldElem":
        return SymFieldElem([poly_const((val >> i) & 1) for i in range(n)], n)

    @staticmethod
    def from_window(block_id: int, l: int, n: int, core_offset: int) -> "SymFieldElem":
        """xi = sum_{j<l} v_{block,j} * alpha^j  (higher bits zero)."""
        bits = []
        for i in range(n):
            if i < l:
                bits.append(poly_var(core_offset + block_id * l + i))
            else:
                bits.append(frozenset())
        return SymFieldElem(bits, n)

    def add(self, other: "SymFieldElem") -> "SymFieldElem":
        return SymFieldElem([poly_add(a, b) for a, b in zip(self.bits, other.bits)], self.n)


def mul_schoolbook_reduce(x: SymFieldElem, y: SymFieldElem, mod: int) -> SymFieldElem:
    """Symbolic schoolbook multiply + polynomial reduction mod `mod`."""
    n = x.n
    # Schoolbook: degree up to 2n-2
    acc = [frozenset() for _ in range(2 * n - 1)]
    for i in range(n):
        if not x.bits[i]:
            continue
        for j in range(n):
            if not y.bits[j]:
                continue
            acc[i + j] = poly_add(acc[i + j], poly_mul(x.bits[i], y.bits[j]))
    # Reduce using modulus: for deg >= n, xor with (mod without leading) shifted
    # mod = t^n + lower; replacing t^{n+k} by lower * t^k
    dm = n
    lower = mod ^ (1 << n)  # bits of degree < n
    for deg in range(2 * n - 2, n - 1, -1):
        if not acc[deg]:
            continue
        # acc[deg] * t^deg = acc[deg] * t^{deg-n} * (t^n) = acc[deg] * t^{deg-n} * lower
        shift = deg - n
        chunk = acc[deg]
        acc[deg] = frozenset()
        for b in range(n):
            if (lower >> b) & 1:
                acc[shift + b] = poly_add(acc[shift + b], chunk)
    return SymFieldElem(acc[:n], n)


def sym_square(x: SymFieldElem, field: Field) -> SymFieldElem:
    """Squaring is F_2-linear on coordinates: bit i of x^2 = linear form of bits."""
    n = x.n
    # Precompute for each basis element e_i = 1<<i, the bits of e_i^2
    out_bits = [frozenset() for _ in range(n)]
    for i in range(n):
        sq = field.sqr(1 << i)
        for b in range(n):
            if (sq >> b) & 1:
                out_bits[b] = poly_add(out_bits[b], x.bits[i])
    return SymFieldElem(out_bits, n)


def semaev_s3(x1: SymFieldElem, x2: SymFieldElem, x3: SymFieldElem, field: Field, b_curve: int = 1) -> SymFieldElem:
    """S_3(x1,x2,x3) = (x1x2 + x1x3 + x2x3)^2 + x1 x2 x3 + b  (char 2)."""
    mod = field.mod
    p12 = mul_schoolbook_reduce(x1, x2, mod)
    p13 = mul_schoolbook_reduce(x1, x3, mod)
    p23 = mul_schoolbook_reduce(x2, x3, mod)
    s = p12.add(p13).add(p23)
    s2 = sym_square(s, field)
    p123 = mul_schoolbook_reduce(p12, x3, mod)
    bconst = SymFieldElem.from_const(b_curve, field.n)
    return s2.add(p123).add(bconst)


@dataclass
class EncodedSystem:
    n: int
    m: int
    l: int
    arm: str
    mod: int
    core_variable_count: int
    block_partition: list
    xor_clauses: list  # list of (list[int] lit_ids_positive, constant_rhs 0/1)
    # lit_ids: 1..core are core vars; core+1.. are substitution vars
    substitution_variable_count: int
    clause_widths: list
    f_set_clause_widths: list  # same as clause_widths here (all eqs are F-set)
    monomial_support_size: int
    target: int
    instance_status: str
    planted: tuple | None = None

    def clause_width_mean(self) -> float:
        w = self.f_set_clause_widths
        return sum(w) / len(w) if w else 0.0

    def clause_width_max(self) -> int:
        return max(self.f_set_clause_widths) if self.f_set_clause_widths else 0

    def clause_width_histogram(self) -> dict:
        return dict(sorted(Counter(self.f_set_clause_widths).items()))


def _tseitin_encode(equations: list, n_core: int) -> tuple[list, int, list]:
    """Convert list[Poly] (=0 equations) into XOR clauses + substitution vars.

    Each poly p: XOR_{monomials} = 0. Degree-0 (const) contributes RHS.
    Degree-1: core lit. Degree>=2: introduce/reuse substitution var.
    Returns (xor_clauses, n_subst, widths).
    """
    subst: dict[int, int] = {}  # monomial_mask -> subst var id
    next_id = n_core + 1
    clauses = []
    widths = []

    for poly in equations:
        lits = []
        rhs = 0
        for mon in poly:
            deg = mon.bit_count()
            if deg == 0:
                rhs ^= 1
            elif deg == 1:
                # single variable index
                idx = mon.bit_length() - 1  # 0-based
                lits.append(idx + 1)  # 1-based
            else:
                if mon not in subst:
                    subst[mon] = next_id
                    next_id += 1
                lits.append(subst[mon])
        # XOR lits = rhs; skip tautology empty with rhs 0; contradiction empty rhs 1 kept
        clauses.append((sorted(set(lits)), rhs))
        widths.append(len(set(lits)))

    n_subst = next_id - n_core - 1
    return clauses, n_subst, widths


def encode_pdp(
    field: Field,
    m: int,
    l: int,
    target: int,
    arm: str,
    instance_status: str,
    planted: tuple | None = None,
    b_curve: int = 1,
    block_basis: list | None = None,
) -> EncodedSystem:
    """Encode S_3(x1..xm) = target with xi in V_l (m must be 3).

    block_basis: optional list of m matrices (l x l bit-columns as ints),
    each an invertible F_2 linear map applied to that block's coordinates
    before embedding into V_l (relabelling control).
    """
    if m != 3:
        raise ValueError("this encoder implements m=3 Semaev S_3 only")
    n = field.n
    n_core = m * l
    # Build symbolic xi with optional per-block linear relabelling
    xs = []
    for bid in range(m):
        if block_basis is None:
            xs.append(SymFieldElem.from_window(bid, l, n, 0))
        else:
            # y_j = XOR_k M_{k,j} v_k  then embed y as degree-<l poly
            M = block_basis[bid]  # list of l ints, column j = M[j] as bitmask of rows
            bits = []
            for i in range(n):
                if i >= l:
                    bits.append(frozenset())
                    continue
                # coordinate i of the relabelled block = row i of M * v
                acc = frozenset()
                for j in range(l):
                    if (M[j] >> i) & 1:
                        acc = poly_add(acc, poly_var(bid * l + j))
                bits.append(acc)
            xs.append(SymFieldElem(bits, n))

    s3 = semaev_s3(xs[0], xs[1], xs[2], field, b_curve=b_curve)
    tgt = SymFieldElem.from_const(target, n)
    # equations: s3 + target = 0
    eqs = [poly_add(s3.bits[i], tgt.bits[i]) for i in range(n)]
    mon_support = set()
    for p in eqs:
        mon_support |= set(p)

    clauses, n_subst, widths = _tseitin_encode(eqs, n_core)
    return EncodedSystem(
        n=n,
        m=m,
        l=l,
        arm=arm,
        mod=field.mod,
        core_variable_count=n_core,
        block_partition=[l] * m,
        xor_clauses=clauses,
        substitution_variable_count=n_subst,
        clause_widths=widths,
        f_set_clause_widths=widths,
        monomial_support_size=len(mon_support),
        target=target,
        instance_status=instance_status,
        planted=planted,
    )


def eval_s3_coords(field: Field, coords: tuple, l: int, b_curve: int = 1) -> int:
    """Evaluate S_3 on m=3 window elements given as packed l-bit ints."""
    elems = []
    for c in coords:
        # c is l-bit value -> field element
        elems.append(c & ((1 << l) - 1))
    x1, x2, x3 = elems
    p12 = field.mul(x1, x2)
    p13 = field.mul(x1, x3)
    p23 = field.mul(x2, x3)
    s = p12 ^ p13 ^ p23
    s2 = field.sqr(s)
    p123 = field.mul(p12, x3)
    return s2 ^ p123 ^ b_curve


def apply_block_basis(coords: tuple, block_basis: list, l: int) -> tuple:
    """Apply per-block linear maps to packed coordinate tuple."""
    out = []
    for bid, c in enumerate(coords):
        M = block_basis[bid]
        v = [(c >> j) & 1 for j in range(l)]
        # new_coord_i = XOR_j M[j]_i * v_j
        nc = 0
        for i in range(l):
            bit = 0
            for j in range(l):
                if (M[j] >> i) & 1:
                    bit ^= v[j]
            if bit:
                nc |= 1 << i
        out.append(nc)
    return tuple(out)


def brute_force_solutions(
    field: Field,
    l: int,
    target: int,
    b_curve: int = 1,
    block_basis: list | None = None,
) -> list:
    """Enumerate all (c1,c2,c3) in (F_2^l)^3 with S_3 = target under field."""
    m = 3
    limit = 1 << l
    sols = []
    for c1 in range(limit):
        for c2 in range(limit):
            for c3 in range(limit):
                coords = (c1, c2, c3)
                if block_basis is not None:
                    ev = eval_s3_coords(field, apply_block_basis(coords, block_basis, l), l, b_curve)
                else:
                    ev = eval_s3_coords(field, coords, l, b_curve)
                if ev == target:
                    sols.append(coords)
    return sols


def encoder_solutions(system: EncodedSystem) -> list:
    """Brute-force core assignments satisfying all XOR clauses."""
    n_core = system.core_variable_count
    # Build subst definitions: subst_id -> monomial mask over core
    # Recover from clauses? Better: re-derive by evaluating polys.
    # Direct: enumerate core, evaluate each XOR clause.
    # We need subst values from ANDs — reconstruct subst map from encoding.
    # Simpler path: evaluate algebraic oracle equivalent by expanding clauses
    # with subst meaning. Store subst table on system? Re-encode knowledge:
    # Walk clauses: we don't have subst defs. Fix encode_pdp to store them.

    # Fallback: use algebraic evaluation matching the arm (caller should
    # prefer brute_force_solutions). Here evaluate XOR after computing
    # subst from implied monomials — requires subst_monomials on system.
    if not hasattr(system, "subst_monomials"):
        raise RuntimeError("system missing subst_monomials; use encode_pdp_full")
    sols = []
    for assign in range(1 << n_core):
        # core bits: var i (1-based) = bit i-1
        vals = {}
        for i in range(1, n_core + 1):
            vals[i] = (assign >> (i - 1)) & 1
        for mon, sid in system.subst_monomials.items():
            bit = 1
            mm = mon
            while mm:
                lsb = mm & -mm
                idx = lsb.bit_length() - 1
                bit &= (assign >> idx) & 1
                mm ^= lsb
            vals[sid] = bit
        ok = True
        for lits, rhs in system.xor_clauses:
            x = 0
            for lit in lits:
                x ^= vals[lit]
            if x != rhs:
                ok = False
                break
        if ok:
            # pack into (c1,c2,c3)
            l = system.l
            c1 = assign & ((1 << l) - 1)
            c2 = (assign >> l) & ((1 << l) - 1)
            c3 = (assign >> (2 * l)) & ((1 << l) - 1)
            sols.append((c1, c2, c3))
    return sols


def encode_pdp_full(
    field: Field,
    m: int,
    l: int,
    target: int,
    arm: str,
    instance_status: str,
    planted: tuple | None = None,
    b_curve: int = 1,
    block_basis: list | None = None,
) -> EncodedSystem:
    """Like encode_pdp but attaches subst_monomials for encoder brute force."""
    if m != 3:
        raise ValueError("m=3 only")
    n = field.n
    n_core = m * l
    xs = []
    for bid in range(m):
        if block_basis is None:
            xs.append(SymFieldElem.from_window(bid, l, n, 0))
        else:
            M = block_basis[bid]
            bits = []
            for i in range(n):
                if i >= l:
                    bits.append(frozenset())
                    continue
                acc = frozenset()
                for j in range(l):
                    if (M[j] >> i) & 1:
                        acc = poly_add(acc, poly_var(bid * l + j))
                bits.append(acc)
            xs.append(SymFieldElem(bits, n))

    s3 = semaev_s3(xs[0], xs[1], xs[2], field, b_curve=b_curve)
    tgt = SymFieldElem.from_const(target, n)
    eqs = [poly_add(s3.bits[i], tgt.bits[i]) for i in range(n)]
    mon_support = set()
    for p in eqs:
        mon_support |= set(p)

    subst: dict[int, int] = {}
    next_id = n_core + 1
    clauses = []
    widths = []
    for poly in eqs:
        lits = []
        rhs = 0
        for mon in poly:
            deg = mon.bit_count()
            if deg == 0:
                rhs ^= 1
            elif deg == 1:
                idx = mon.bit_length() - 1
                lits.append(idx + 1)
            else:
                if mon not in subst:
                    subst[mon] = next_id
                    next_id += 1
                lits.append(subst[mon])
        clauses.append((sorted(set(lits)), rhs))
        widths.append(len(set(lits)))

    n_subst = next_id - n_core - 1
    sys = EncodedSystem(
        n=n,
        m=m,
        l=l,
        arm=arm,
        mod=field.mod,
        core_variable_count=n_core,
        block_partition=[l] * m,
        xor_clauses=clauses,
        substitution_variable_count=n_subst,
        clause_widths=widths,
        f_set_clause_widths=widths,
        monomial_support_size=len(mon_support),
        target=target,
        instance_status=instance_status,
        planted=planted,
    )
    sys.subst_monomials = subst  # type: ignore[attr-defined]
    sys.block_basis = block_basis  # type: ignore[attr-defined]
    return sys


def random_gl_l(l: int, rng) -> list:
    """Random invertible l x l matrix over F_2 as list of l column bitmasks."""
    while True:
        cols = [rng.randrange(1, 1 << l) for _ in range(l)]
        # Gaussian elimination rank check
        mat = cols[:]
        rank = 0
        used = [False] * l
        for row in range(l):
            piv = None
            for j in range(l):
                if not used[j] and ((mat[j] >> row) & 1):
                    piv = j
                    break
            if piv is None:
                continue
            used[piv] = True
            rank += 1
            for j in range(l):
                if j != piv and ((mat[j] >> row) & 1):
                    mat[j] ^= mat[piv]
        if rank == l:
            return cols


def histogram_distance(h1: dict, h2: dict) -> float:
    keys = set(h1) | set(h2)
    return sum(abs(h1.get(k, 0) - h2.get(k, 0)) for k in keys)


def width_match_ok(h_ctrl: dict, h_target: dict, mean_ctrl: float, mean_tgt: float) -> bool:
    """Width-match metric: identical histogram counts OR mean within 5% and L1<=2."""
    if h_ctrl == h_target:
        return True
    if mean_tgt == 0:
        return mean_ctrl == 0
    if abs(mean_ctrl - mean_tgt) / mean_tgt > 0.05:
        return False
    return histogram_distance(h_ctrl, h_target) <= 2
