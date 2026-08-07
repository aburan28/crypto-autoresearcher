# y-Sign Oracle Analysis — IDEA formulation for the C7 control object
**Task:** TASK-20260805-014, BATCH-124, GOAL-ECDLP-001
**Date:** 2026-08-05
**Source:** C7 correction in ct_minimality_lemma.md (y-dependent oracles are
encoding-dependent, non-simulable, and not functions of x alone)

---

## 1. Motivation

The C_t-minimality theorem (KN-FIND-982fdf) restricted its claims to the
ORDER-BASED class: 1-bit oracles whose 1-set is an x-prefix {x < t} on the
curve. Correction C7 established that y-dependent oracles exist and are not of
that form. The natural control object is the **sign oracle**:

    S(P) = [y(P) < p/2]   (canonical F_p sign on the Weierstrass y-coordinate)

This is 1-bit, non-simulable (encoding-dependent, public), and clearly NOT
x-based. Does S define a factor base? It CANNOT: the factor base in Semaev IC
must be a set of x-coordinates (the summation polynomial needs x_i), and the
preimage set {P : S(P)=1} is NOT of the form {x : x < t} — it contains both
x(P) and x(-P)=-P values in the sense that opposite points have different
y-signs but the same x.

## 2. Formal statement (candidate IDEA)

**IDEA: sign-membership is not a factor-base selector.** For any choice of the
sign fragment, the set F_s = {P : y(P) < p/2} satisfies: for every affine P,
either exactly one of P, -P lies in F_s. Therefore F_s contains exactly one of
each opposite pair, i.e. |F_s| = (N-1)/2 identically (the whole curve minus the
pair of non-existent 2-torsion is split). It is NOT a "small" factor base:
half the curve's points qualify, so it never satisfies |F_s| << N, the
requirement for a factor base in Semaev index calculus. Hence the sign oracle
cannot produce a factor base at ANY threshold.

**Negation:** No choice of t for y-thresholding (y < t) yields a factor base;
only the x-threshold family {C_t} does.

## 3. Quick proof

Fix x. The preimage pair is {P+, P-} with y(P+) = -y(P-) mod p. Exactly one is
< p/2 unless p odd and y = p/2 (impossible: p odd, y = (p-1)/2 can occur; if
it does both the point and its negation have y=(p-1)/2, i.e., same sign —
this happens iff the curve has a point with y = (p-1)/2, in the degree-2
cases). In the degenerate case a few x have both points of sign +. Still the
set is O(N/2), not B = N^{1/m} << N. So it fails the cardinality.

## 3. Prediction / falsifier

Prediction: for every toy curve, |F_s| >= (N-1)/2 for the sign fragment, hence
NOT a factor base (cardinality floor). Falsifier: if some other "semantic"
factor base like the sign OR x-threshold union could reduce the enumeration
below B^m/N, then IC yield would be repairable — test at toy scale.

## 4. Prior art + ties

- C7 in KN-FIND-982fdf analysis states the y-dependent oracle is not x-based;
this IDEA closes the constructive use (factor base from signs).
- BATCH-060: sign not studied; the closest object is the y-coordinate control.
- The practical takeaway for the attack: membership test in IC is a
  coordinate-threshold test; a y-sign bit is provided by the same encoding
  for free but does not carve a factor base. So the oracle economy of C_t is
  preserved: x-order is the only curved ordering useful for base / IC.

---

## 5. Verdict (analysis)

**Close as a dead end (expected)**: IDEA-S is a factor-base selector barrier.
A variant CONSIDERED in the afterword: "2 points sign + even-x vs odd-x" is
just a 2-bit prefix selector and is dominated by C_t.

## 6. Priority

Low; record as `rejected` with the cardinality argument.