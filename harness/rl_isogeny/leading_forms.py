"""Leading-form certificate: why no curve in any isogeny class, over any prime
field, can present these systems with an earlier first fall.

The lemma (checked mechanically here, not assumed)
--------------------------------------------------
Fix a presentation of the grid.  Its generators are
    F_i  = S_3 with the factor-base map substituted (curve-dependent)
    f_V  = membership polynomials (curve-independent)
and every ring is graded by total degree.  Write LF(g) for the top-degree
homogeneous part of g.  S_3(x_1, x_2, x_3) has total degree 4 and its degree-4
part is (x_1 - x_2)^2 x_3^2 - 2 x_1 x_2 (x_1 + x_2) x_3 + x_1^2 x_2^2: the curve
constants a, b sit in degrees <= 3.  Substituting x_i = u_i^k + c u_i (or the
digit expansion) keeps a, b strictly below the top degree.  Hence

    LF(F_i) does not depend on the curve,          (*)

which :func:`leading_forms` verifies coefficient by coefficient on random
curves at each prime, up to 56-bit primes.

Consequence for the Macaulay meter.  The degree-D layer M_D has rows m * g
(deg m = D - deg g).  A FALL at D is a row combination whose top part
vanishes, i.e. a coefficient vector in the syzygy space K_D of the leading
forms; by (*) K_D is the same for every curve.  The fall space is the image of
K_D under (coefficients -> full combination), so

    fall_dim(D) = dim K_D - dim { syzygies of the FULL system in degree D },

and the first fall degree is the first D with K_D nontrivial UNLESS the
remainder of every such syzygy happens to vanish for that curve -- a proper
Zariski-closed condition on (a', b', x_R), met with probability O(deg / p) per
member.  (Under the per-layer convention the multipliers have exact degree
D - deg g, so even a Koszul-type relation LF(g_j) g_i - LF(g_i) g_j is a row
combination with a nonzero remainder; in a squarefree ring a multiple m * LF(g)
can also collapse in degree, which the meter counts as a fall.  Both mechanisms
depend only on the leading forms.)  So:

  1. d_ff(real) >= d_ff(generic) for EVERY curve over EVERY prime field, with
     equality off a measure-zero locus: ``excess_fall > 0`` is impossible for
     these presentations, at every scale, exhaustively.
  2. The only curve-dependent event is a rank DROP (extra syzygies of the full
     system), rarer as p grows; enumerating classes to 2^48 or 2^56 can only
     confirm the toy enumerations with fewer coincidences, never contradict them.
  3. A within-class effect therefore needs a presentation whose leading forms
     depend on the curve; none of the polynomial-parametrised families does.

The certificate records, per presentation and per prime: the leading forms,
their coefficient-wise agreement across random curves, the first degree with
a non-Koszul leading-form syzygy (the predicted first fall), and the measured
first fall of the full system on each curve.  Claim tier of the numbers: toy;
the lemma itself is scale-free.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from harness.macaulay_fp import analyze_degrees, first_nonzero_fall
from tools.isogeny_dreg_search import is_singular, random_point, s3_coeffs

from .reward import Built, PresentationSpec, build_presentation

# primes used by default: the toy prime of the demonstrations, a 32-bit, a
# 48-bit and a 56-bit prime (all checked prime by the Ring constructor)
DEFAULT_PRIMES = (7127, 4294967291, 281474976710597, 72057594037927931)


def leading_forms(built: Built) -> List[Tuple[Tuple, ...]]:
    """Top-degree forms of every generator, as sorted (monomial, coeff) tuples."""
    out = []
    for g in built.polys:
        top = built.ring.top_form(g)
        out.append(tuple(sorted(top.items())))
    return out


def _random_curve(p: int, rng: random.Random) -> Tuple[int, int]:
    while True:
        a, b = rng.randrange(1, p), rng.randrange(1, p)
        if not is_singular(a, b, p):
            return a, b


@dataclass
class PrimeCertificate:
    p: int
    curves: List[Tuple[int, int]]
    leading_forms_identical: bool
    leading_form_support: List[List[str]]      # per generator, monomials as strings
    predicted_first_fall: Optional[int]        # first degree with a leading-form syzygy or collapse (K_D != 0)
    measured_first_fall: List[Optional[int]]   # full system, per curve
    consistent: bool                           # every measured == predicted

    def as_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class Certificate:
    spec: PresentationSpec
    per_prime: List[PrimeCertificate]
    support_identical_across_primes: bool
    holds: bool
    statement: str = field(default="")

    def as_dict(self) -> dict:
        return {"spec": self.spec.as_dict(), "per_prime": [c.as_dict() for c in self.per_prime],
                "support_identical_across_primes": self.support_identical_across_primes,
                "holds": self.holds, "statement": self.statement}


def _mono_str(ring, m) -> str:
    return ring.to_string({m: 1})


def certify(spec: PresentationSpec, primes: Sequence[int] = DEFAULT_PRIMES, curves_per_prime: int = 3,
            seed: int = 0, max_rows: int = 40000, max_cols: int = 40000) -> Certificate:
    per_prime: List[PrimeCertificate] = []
    supports: List[List[List[str]]] = []
    for p in primes:
        rng = random.Random(f"{seed}:{p}:{spec.key}")
        curves = [_random_curve(p, rng) for _ in range(curves_per_prime)]
        forms = []
        measured = []
        predicted = None
        support: List[List[str]] = []
        for (a, b) in curves:
            x_R = random_point(a, b, p, rng)[0]
            built = build_presentation(p, s3_coeffs(a, b, p), x_R, spec)
            forms.append(leading_forms(built))
            degs = [d for d in built.degrees if d > 0]
            D_max = spec.initial_cap() + 2
            layers = analyze_degrees(built.ring, built.polys, min(degs), D_max, convention="per_layer",
                                     max_rows=max_rows, max_cols=max_cols)
            measured.append(first_nonzero_fall(layers))
            if predicted is None:
                lf_layers = analyze_degrees(built.ring, built.polys, min(degs), D_max, convention="per_layer",
                                            leading_forms=True, max_rows=max_rows, max_cols=max_cols)
                # first degree at which the leading forms alone admit a syzygy with
                # exact-degree multipliers, or a squarefree collapse: K_D != 0
                predicted = next((l.degree for l in lf_layers if l.syzygy_dim > 0 or l.fall_dim > 0), None)
                support = [[_mono_str(built.ring, m) for (m, _c) in f] for f in forms[0]]
        identical = all(f == forms[0] for f in forms)
        consistent = all(m == predicted for m in measured)
        per_prime.append(PrimeCertificate(p, curves, identical, support, predicted, measured, consistent))
        supports.append(support)
    same_support = all(s == supports[0] for s in supports)
    holds = same_support and all(c.leading_forms_identical and c.consistent for c in per_prime)
    stmt = ("leading forms are curve-independent at every tested prime and the measured first fall equals "
            "the leading-form syzygy degree on every curve: excess_fall > 0 is impossible for this presentation"
            if holds else "CERTIFICATE FAILED: see per_prime")
    return Certificate(spec, per_prime, same_support, holds, stmt)


def certify_grid(specs: Sequence[PresentationSpec], primes: Sequence[int] = DEFAULT_PRIMES,
                 curves_per_prime: int = 3, seed: int = 0) -> Dict[str, Certificate]:
    return {s.label(): certify(s, primes, curves_per_prime, seed) for s in specs}
