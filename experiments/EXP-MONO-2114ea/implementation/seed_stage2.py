"""
Seed derivation for EXP-MONO-2114ea's own Stage 2/3 null-subset draws, per
specification.yaml `inputs.seed_derivation_rule`:

    SHA-256 of domain || "|" || decimal(master_seed) || "|" ||
    "null-subset" || "|" || decimal(p) || "|" || decimal(F) || "|" ||
    decimal(curve_ordinal) || "|" || decimal(draw_index)

big-endian unsigned, rejection-sampled against modulo bias, identical
REJECTION-SAMPLING MECHANISM to EXP-MONO-b19c6b's own
`controls.py::draw_symmetric_subset` / EXP-MONO-b1423c's own
`draw_symmetric_null_subset` (same algorithmic pattern; NEW preimage, as
this contract's own frozen seed_derivation_rule declares -- keyed on
(p, F, curve_ordinal) rather than perturbation fraction or panel size,
which is what makes ONE null population per curve reusable across every
grid cell that curve appears in). This module is NOT copied from any prior
contract: it implements only this contract's own declared preimage.
"""
import hashlib

DOMAIN = "EXP-MONO-2114ea/v1"
MASTER_SEED = 20260901


def stage2_seed_int(domain: str, master_seed: int, p: int, F: int,
                     curve_ordinal: int, draw_index: int, counter: int) -> int:
    s = (f"{domain}|{master_seed}|null-subset|{p}|{F}|{curve_ordinal}|"
         f"{draw_index}|{counter}").encode("ascii")
    return int.from_bytes(hashlib.sha256(s).digest(), "big")


class Stage2Drawer:
    """Stateful per-(domain, master_seed, p, F, curve_ordinal, draw_index)
    counter with rejection-sampled uniform draws."""

    def __init__(self, domain: str, master_seed: int, p: int, F: int,
                 curve_ordinal: int, draw_index: int, start_counter: int = 0):
        self.domain = domain
        self.master_seed = master_seed
        self.p = p
        self.F = F
        self.curve_ordinal = curve_ordinal
        self.draw_index = draw_index
        self.counter = start_counter
        self.digests_consumed = 0
        self.rejections = 0

    def draw(self, modulus: int) -> int:
        assert modulus > 0
        limit = (2 ** 256 // modulus) * modulus
        while True:
            v = stage2_seed_int(self.domain, self.master_seed, self.p, self.F,
                                 self.curve_ordinal, self.draw_index, self.counter)
            self.counter += 1
            self.digests_consumed += 1
            if v < limit:
                return v % modulus
            self.rejections += 1


def draw_symmetric_null_subset_stage2(cs, F, domain, master_seed, curve_ordinal, draw_index):
    """Draw a uniformly random SYMMETRIC subset of E(F_p) affine points of
    size F, built as random +/- pairs, keyed by (domain, master_seed, cs.p,
    F, curve_ordinal, draw_index) via `Stage2Drawer` above. Identical
    rejection-sampling / self-negating-slot mechanism to
    EXP-MONO-b1423c's own `draw_symmetric_null_subset`, generalized here to
    any curve's own (n1, n2) presentation (this contract tests up to 15
    distinct curves, not one fixed curve)."""
    drawer = Stage2Drawer(domain, master_seed, cs.p, F, curve_ordinal, draw_index)
    chosen = set()
    n_affine = len(cs.points)
    guard = 0
    while len(chosen) < F:
        guard += 1
        if guard > 200 * F + 1000:
            raise RuntimeError("draw_symmetric_null_subset_stage2: too many rejection iterations")
        idx = drawer.draw(n_affine)
        P = cs.points[idx]
        Q = cs.negate(P)
        if P in chosen:
            continue
        if P == Q:
            if F - len(chosen) == 1:
                chosen.add(P)
            else:
                continue
        else:
            if len(chosen) + 2 > F:
                continue
            chosen.add(P)
            chosen.add(Q)
    return list(chosen)
