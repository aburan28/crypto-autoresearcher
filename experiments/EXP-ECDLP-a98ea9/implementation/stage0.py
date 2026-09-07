"""Stage 0 for EXP-ECDLP-a98ea9: write the transport lemma (zero compute).

Hard gate: the projection step including the vacuous r=1 case; where
gcd(n,p)=1 is used; the prime-n homomorphism argument; the NULL-2 r=1
width-zero cell. No measurement is taken.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

LEMMA = r'''# Stage 0 receipt: transport lemma (EXP-ECDLP-a98ea9)

This document is the Stage 0 hard gate. It writes the procedure. It
measures nothing. It authorizes no D2 closure, attack, speedup, novelty,
support, completion, or breakthrough.

Ordinary base-p digits, Witt coordinates, and a primitive character of
Z/p^r Z are three different observables. This contract measures only the
first (DEC-20260907-1cf1c0).

## 1. Objects

Let E be an elliptic curve given by a Weierstrass model over Z_p with
v_p(discriminant) = 0 (good reduction). Let p be the residue characteristic
and let S be a point of prime order n on E(F_p). Write Ŝ_r for the
canonical order-n prime-to-p lift of S to E(Z/p^r Z), when it exists.

The reduction map π_r : E(Z/p^{r+1} Z) → E(Z/p^r Z) is induced by the
ring homomorphism Z/p^{r+1} Z → Z/p^r Z. That ring map is a homomorphism
of rings for every r ≥ 1. At r = 1 the source and target of the first
interesting comparison are E(Z/p^2 Z) → E(Z/p Z); there is no
Z/p^0 Z. The r = 1 cell of the digit family is the F_p coordinate of S
itself.

Digits: the unique integer representative of affine x([k] Ŝ_r) in the
interval [0, p^r) is written Σ_{j=0}^{r-1} d_j p^j with each d_j in
{0,...,p-1}. These are ordinary base-p digits, not Witt coordinates.

## 2. Where gcd(n, p) = 1 is used

The sentence, stated so it can be found:

    Because gcd(n, p) = 1, reduction E(Z/p^r Z)[n] → E(F_p)[n] is a
    group isomorphism, so S has a unique lift Ŝ_r of exact order n, and
    p^{r-1} is a unit modulo n, so the integer
    m = (p^{r-1})^{-1} mod n exists.

If gcd(n, p) ≠ 1 the order-n lift does not exist. That is why anomalous
curves (a generator of order p) are excluded before entering the run set:
the statistic is undefined there, not uninformative.

The same coprimality is what makes [p^{r-1}] an automorphism of the
prime-to-p n-torsion: it is multiplication by a unit of Z/n Z.

## 3. The k-free construction

Given only the F_p point P (here P = S or P = [k]S; the scalar is not an
input) of order n:

1. Hensel-lift P along the Weierstrass equation to a point P̃ on
   E(Z/p^r Z) that reduces to P. Stop. This is also NULL-2.
2. Set U = [p^{r-1}] P̃. On E(Z/p^r Z) this kills the kernel of
   reduction (the formal-group p-power component) and retains the
   prime-to-p part.
3. Set m = (p^{r-1})^{-1} mod n and return [m] U.

This is the procedure the Stage 1 transport path must implement. It
reads P, n, p, r, and the curve. It does not read k.

At r = 1 one has p^{0} = 1 and m = 1, so the return value equals the
Hensel lift, which equals P itself. The projection step is vacuous.

## 4. The transport lemma (prime-n homomorphism)

Claim (procedure, not a complexity result): for every integer k and every
r in {1,2,3,4},

    π( [k] Ŝ_{r} ) = [k] (π Ŝ_{r}) = [k] S    on E(F_p),

and, comparing two constructions of the same point on E(Z/p^r Z),

    [k] Ŝ_r  =  canonical_order_n_lift([k] S)

digit-for-digit on ordinary base-p digits of affine x (and of affine y).

Reason: reduction is a group homomorphism, so it commutes with [k].
Because gcd(n, p) = 1 the n-torsion reduces isomorphically, so the
canonical order-n lift is a group homomorphism
Z/n Z → E(Z/p^r Z)[n] sending 1 to Ŝ_r. Therefore it sends k to [k] Ŝ_r,
which is exactly the canonical order-n lift of [k] S.

The prime-n hypothesis is used here as: End(Z/n Z) = Z/n Z, so every
group homomorphism Z/n Z → E(Z/p^r Z)[n] is multiplication by a single
integer. There is no extra endomorphism that could send S to a lift of
[k]S other than [k] Ŝ_r. At composite order a genuine extra homomorphism
can exist; that is Control C and is not a Stage 0–1 cell.

## 5. NULL-2 and the r = 1 width-zero cell

NULL-2 is the Hensel lift of step 1 with steps 2–3 omitted. It still
reduces correctly and still has r digits, but it carries a formal-group
component and is not the canonical order-n lift.

At r = 1 steps 2–3 are the identity, so NULL-2 and the treatment coincide
exactly. That cell is a consistency check (they must agree) and is not a
discriminating comparison. Reporting r = 1 agreement as evidence that
the projection "does nothing to the statistic" would be reporting a
forced identity. The discriminating cells are r in {2,3,4}. This split
is recorded here, before any number is read.

## 6. What Stage 1 will check

- Exact digit-for-digit agreement, at every tested r, between
  (1) lift-then-multiply-by-k and (2) the k-free procedure applied to
  the F_p point [k]S alone.
- A static AST check that kfree_transport.py never takes a discrete-log
  scalar.
- The r = 1 identity of NULL-2 with the treatment, as a consistency
  check only.

Stage 0 writes this lemma. It does not run those checks.
'''


def main() -> None:
    t0 = time.time()
    here = Path(__file__).resolve().parent
    run_dir = here.parent / "runs" / "RUN-ECDLP-a98ea9-S0"
    run_dir.mkdir(parents=True, exist_ok=True)
    lemma_path = run_dir / "transport-lemma.md"
    lemma_path.write_text(LEMMA)
    raw = {
        "stage": 0,
        "experiment_id": "EXP-ECDLP-a98ea9",
        "hypothesis_id": "H-ECDLP-07c7c6",
        "compute": False,
        "description": (
            "Transport lemma with projection step, gcd(n,p)=1 sentence, "
            "prime-n homomorphism argument, and NULL-2 r=1 width-zero cell."
        ),
        "lemma_path": str(lemma_path.relative_to(here.parent)),
        "null2_r1_width_zero": {
            "declared": True,
            "discriminating": False,
            "reason": (
                "At r=1 the [p^{r-1}] projection is the identity, so NULL-2 "
                "equals the treatment by construction."
            ),
        },
        "gcd_np_sentence": (
            "Because gcd(n, p) = 1, reduction E(Z/p^r Z)[n] → E(F_p)[n] is a "
            "group isomorphism, so S has a unique lift of exact order n, and "
            "p^{r-1} is a unit modulo n."
        ),
        "wall_clock_seconds": round(time.time() - t0, 6),
        "validity": "valid",
        "validity_reason": "Stage 0 is a write-up gate; the lemma file exists.",
    }
    (run_dir / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    print(json.dumps({"stage": 0, "lemma": str(lemma_path), "valid": True}, indent=2))


if __name__ == "__main__":
    main()
