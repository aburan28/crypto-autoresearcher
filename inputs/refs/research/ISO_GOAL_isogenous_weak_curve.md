# GOAL RESULT: Isogenous curve with meaningfully easier ECDLP for P-256 / P-224

**Date:** 2026-06-01. Goal: "find a curve isogenous to P-256 or P-224 that has a meaningfully easier ECDLP than each of those curves; it must be meaningfully faster to solve; use isogeny graphs."

## VERDICT

**No such curve exists in the F_p-isogeny class of P-256 or P-224, and none can be found by any isogeny-graph method** — by `RESTRICTED THEOREM` (invariant-theoretic, clauses unconditional except the Semaev clause which is model-bound), corroborated by direct isogeny-graph computation. This is a SCOPED NEGATIVE, not a claim of impossibility for ECDLP itself.

## Why (the invariant wall)

ECDLP cost on an ordinary prime-field curve is governed entirely by quantities that are **isogeny-class invariants**. By Tate/Honda-Tate, two curves over F_p are F_p-isogenous iff they have the same Frobenius trace t, hence the same group order n = p+1−t. Therefore across the entire F_p-isogeny class:

| Quantity | Governs which attack | Invariant? | P-256 value | P-224 value |
|---|---|---|---|---|
| n (order) | Pollard rho = 0.886√n | YES (Tate) | 2^256 (prime), rho 2^127.8 | 2^224 (prime), rho 2^111.8 |
| t (trace) | anomalous (t=1, Smart) | YES | 2^127, ≠1 → not anomalous | ≠1 → not anomalous |
| n vs p | anomalous (n=p) | YES | n≠p | n≠p |
| supersingular | — | YES | ordinary | ordinary |
| k = ord_n(p) | MOV/Frey-Rück | YES (fn of n,p) | (n−1)/3 ≈ 2^254 | huge |
| D_K (fund. CM disc) | GLV/GLS endomorphism | YES | \|D_K\|≈2^258 (f=1) | \|D_K\|≈2^223 (f=3) |
| per-var Semaev degree | algebraic IC | YES (PO-004, model-bound) | invariant | invariant |

Every named attack family (rho, anomalous/Smart, MOV/Frey-Rück, GLV, supersingular, GHS/Weil-descent, Semaev-degree reduction) keys on one of these invariants, and each is **strong and fixed** for P-256/P-224. Since F_p-rational isogenies preserve the base field, the F_p-isogeny class is the only reachable set, and rho cost is **strictly identical** on every member.

## What the isogeny-graph computation showed (per the goal's method)

- **ISO-EXP-001** (`iso_invariants.sage`): exact invariants. P-256 conductor f=1 (FLAT volcano); P-224 conductor f=3 (a real 3-volcano — the only non-trivial isogeny structure). Both ordinary, non-anomalous, huge k, huge D_K.
- **ISO-EXP-002** (`iso_walk.sage`): walked both graphs at l=2,3,5,7,11,13. Every neighbor: **order_mismatch=0** (Tate confirmed empirically), anomalous=0, special_j=0, supersingular=0. P-224 shows 4 neighbors at l=3 (the f=3 volcano signature) vs P-256's 1.
- **ISO-EXP-003** (`iso_p224_volcano.sage`): examined P-224's 3-volcano to depth 2. Every vertex shares order n, is ordinary, non-anomalous, same 223-bit CM field. The index-3 order change **cannot** shrink a 223-bit discriminant to a GLV-usable one.
- **ISO-EXP-A** (`iso_expA_neighbor_sweep.sage`): toy P-256-like curve (prime order, a=−3). 0 exploitable neighbors. New sharp point: because **n is prime and odd, no isogenous curve has rational 2-torsion → none admits a Montgomery/Edwards fast model**, so not even a constant-factor group-law speedup exists.
- **ISO-EXP-A2** (`iso_expA_gatedmeter.sage`): the audited gated first-fall meter (self-validation OVERALL_PASS=True) on the m=3 Semaev system of the base curve and all isogenous neighbors. **gate_meaningful=False everywhere** — L3 coefficient variation creates no exploitable Semaev early fall. Closes the one experimental door the literature left open (O-1).

## Literature corroboration (`literature_isogeny_ecdlp_transfer.md`)

Nine attack routes checked, all closed: Tate-invariance (THEOREM); isogeny-DLP-transport helps only with a weak destination, none exists (Jao–Miller–Venkatesan random self-reducibility, GRH); MOV/anomalous/GHS/GLV all class-invariant or base-field-preserving; CGL/CSIDH use isogeny graphs to BUILD crypto, not break ECDLP. **Galbraith 2024 (ePrint 2024/924) makes the bridge cheap (Õ(q^{1/4})≈2^64 for P-256's flat volcano) — so bridge cost is NOT the obstruction; the obstruction is the absence of a weak destination.**

## Honest residual open cracks (none reachable; all expected negative)

1. **O-1 coefficient-level early fall** — tested (ISO-EXP-A2), CLOSED for the toy class; not a theorem at crypto scale but no mechanism over a prime field.
2. **O-2 theta-null Kummer chart** (H14) — formally OPEN from the prime-field campaign; expected to close like the affine/x-line charts; not isogeny-specific.
3. **O-3/O-4 class-group navigation / vectorization** — computing the class-group element linking P-256 to a reference curve is itself subexponential L_{|D_0|}(1/2)≈2^129 for |D_0|≈2^258, already exceeding rho.

## Claim label

`RESTRICTED THEOREM` (NEGATIVE for the goal): No curve F_p-isogenous to P-256 or P-224 has a meaningfully easier ECDLP than the base curve — every ECDLP-hardness quantity is an isogeny-class invariant strong for these curves, verified both by invariant theory (Tate/Honda-Tate, Kohel volcano, Deuring) and by direct isogeny-graph walking + the audited gated meter. The bridge is cheap (Galbraith 2024) but leads only to equally-hard curves. The goal is not achievable by any isogeny-graph method.

## Why this is the correct answer, not a failure to search hard enough
The negative is structural, not effort-limited: it follows from a THEOREM (order is isogeny-invariant ⇒ rho identical) plus the verified absence of every non-generic weakness. Searching more of the graph cannot help because the graph is *defined* by the shared trace, which fixes n, k, and the CM field. The one thing that varies — the Weierstrass coefficients — was tested directly (ISO-EXP-A2) and produces no exploitable structure.
