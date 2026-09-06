# R5 — claim (A) of H-PFDR-c88f14: the non-transferring steps, and whether any bound could exist

Red Team, TASK-20260904-3a2ff5. Sources: `stage0-transfer.md` sections 1-3,
H-PFDR-c88f14 statement (A) and `structural_ingredients`, KN-LIT-7605, KN-LIT-7607, and
two retrievals I performed in this session (recorded below).

## 1. What claim (A) says, and its two stated grounds

(A) asserts: no version of the bounded-last-fall theorem of arXiv:2103.07282 transfers to
the F_p digit presentation, because (B1) Lemma 2.1's Frobenius cyclic shift has no F_p
analogue (x -> x^p is the identity on F_p; the digit map is not additive) and (B2)
Theorem 2.6's "reducible for k" hypothesis needs k'-linear structure and F_p has no
proper subfield. Consequence recorded: the formal analogue constant
max((d-1)m + 1, d deg S) = 8 = 4m at m = 2 is "a number with no theorem behind it".

## 2. Retrieval, and a correction the package does not carry

I fetched the source (Red Team responsibility 9; the record's provenance is `retrieved`
at abstract/ar5iv level by another session, proof bodies unread by anyone).

- https://arxiv.org/abs/2103.07282 -- "On the last fall degree of Weil descent polynomial
  systems", **Ming-Deh Huang, 2021**. Abstract: "As an application we derive upper bounds
  on the last fall degree of F'_1 **in the case where F is a set of linearized
  polynomials**."
- https://ar5iv.labs.arxiv.org/html/2103.07282 -- Theorem 2.6 as displayed: "Suppose F is
  a finite set of **k'-linearized polynomials of maximum degree d = q^c**. Let F' be the
  Weil descent system ... If F is **reducible for k**, then d_{F'_1} <= max((q-1)m+1, qd)."
  Theorem 1.1: max(d_{F_1}, q deg F) = max(d_{F'_1}, q deg F), with k' a PROPER subfield.
  Lemma 2.1: "Suppose f = sum_{i,j} a_{ij} x_{ij} in S_1 with a_{ij} in k. Then with
  respect to Qbar, f_i^q == f_{i+1} (mod Qbar)."

TWO DELTAS.

(i) THEOREM 2.6 HAS TWO HYPOTHESES, AND THE PACKAGE NAMES ONLY ONE. The first is that F
is a set of k'-LINEARIZED polynomials of maximum degree a power of q. `stage0-transfer.md`
section 1's dictionary and H-PFDR-c88f14 (A) name only "reducible for k". This matters
twice over:
  - It supplies a THIRD non-transferring step, call it B3, which is decidable from the
    retrieved STATEMENT alone with no proof-body reading and no argument about what the
    proof uses: S~ = S_3(ell_1, ell_2, x_R) has degree 4 and is not additive, so it is not
    a linearized polynomial over any field. Theorem 2.6 does not apply to the digit
    system for that reason before any Frobenius argument is made. B3 is strictly cheaper
    and strictly safer than B1.
  - It voids the "formal analogue constant" more completely than the package says. In
    max((q-1)m+1, qd), the symbol d is the maximum degree of the LINEARIZED generators,
    constrained to be q^c. Substituting deg S_3 = 4 for d, as `stage0-transfer.md`
    section 3 does to obtain 8 = 4m, substitutes into a formula whose variable ranges over
    a different class of objects. The number 8 is not merely "a number with no theorem
    behind it"; it is a category error, and the ladder's inability to "test d_lf <= 4m" is
    therefore not a limitation of the ladder.

(ii) KN-LIT-7605 IS WRONG IN A DIRECTION THAT FLATTERS HEUR-002. That corpus note records
`authors: []`, `year: null` (actual: Ming-Deh Huang, 2021 -- the record's own "Not
verified here" asks for this to be filled) and states as a key claim: "Bounded-fall-degree
results are stated for summation-polynomial systems over F_2 specifically." The abstract
and the displayed theorems name LINEARIZED POLYNOMIALS and say nothing about summation
polynomials; H-PFDR-c88f14's own retrieval note already says "no mention of summation
polynomials, Semaev or ECDLP in the retrieved text", contradicting the corpus note it
cites alongside. The note also states "the last fall degree is bounded independently of n"
without either hypothesis. This is a citation delta for the curator: KN-LIT-7605 as
written overstates the paper's scope in exactly the direction that makes a bounded last
fall for Semaev systems look like established prior art.

## 3. Are B1 and B2 sound as stated?

B2: SOUND and now redundant. F_p has no proper subfield, so the whole k/k' setup of
Theorem 1.1 and Theorem 2.6 (which assume a PROPER subfield k') is not instantiable.
This is the cleanest ground and it is decidable from the theorem statements alone.

B1: SOUND AS A STATEMENT ABOUT THE LEMMA. Lemma 2.1 as displayed concerns
f = sum a_{ij} x_{ij} with coefficients in k and produces a SHIFT of the block index i;
over F_p, k = k' = F_p, there is no block index to shift and x -> x^p is the identity on
the coefficients, so with a_i^2 = a_i in the quotient one gets f^p == f: the lemma
degenerates to a tautology. That much needs no proof body.

WHERE B1 OVERREACHES. The step from "Lemma 2.1 has no analogue" to "no version of the
bounded-last-fall theorem transfers" is an inference about what the PROOF of Theorem 2.6
uses -- and the proof body was not read by the proposing session and could not be read by
the executing session. Claim (A)'s conclusion happens to be correct for the independent
reasons B2 and B3, but its stated derivation contains one link (the essentiality of Lemma
2.1) that the retrieved material does not license. The narrowest correctly supported
version of (A) is: *Theorem 2.6 and Theorem 1.1 of arXiv:2103.07282 are not instantiable
for the F_p digit presentation, because they require a proper subfield k' (B2) and a
generating set of k'-linearized polynomials of degree q^c (B3); no bound is therefore
INHERITED from that source. Nothing here says a bound does not exist.*

## 4. Does the DATA independently exclude a uniform bound?

Not by itself, and the package should not be read as if it did.

- On s = 2..5 the measured d_lf is 5, 5, 6, 6: bounded by 6 on the tested range. Four
  points cannot exclude a uniform bound; they exclude FLATNESS on the tested range
  (d_lf(4) > d_lf(3) on 480 of 480 draws, deterministically, at three primes).
- The exclusion of ANY uniform bound comes from d_lf >= d_ff together with
  H-PFDR-4148b8's closed form d_ff(2,2,s) = 4 + floor(s/2), reproduced with residual 0 at
  s = 2..5 (P3). That closed form is itself conditional -- its EXACTNESS direction rests
  on Wilson's rank theorem (the unconditional part is only the upper bound
  a_0 <= floor((s-e)/2)+1), on H-TOP (derived at m = 2), and the hypothesis record's
  status is `specified`. Wilson's hypothesis is satisfiable in this regime: the record's
  sufficient condition "every binom(k-i, t-i) is a positive integer below p" holds because
  every such binomial is < 2^s <= p under the standing assumption d^s <= p.
- So the honest chain is: (A) is a negative statement about ONE published route and it
  holds (on corrected grounds); the data make a uniform bound implausible but do not
  refute it; the refutation of HEUR-002 for all s runs through the derived d_ff law and
  inherits its conditions.

## 5. Is there any route by which a uniform bound could still hold?

I looked for one and did not find it, but the search is not exhaustive and I record the
one place it would have to live. Since d_lf >= d_ff, a uniform bound requires d_ff to be
bounded in s. H-PFDR-4148b8 reduces d_ff to the initial degree of the graded annihilator
of the top form under the tensor-kernel identity; a uniform bound would require that
initial degree to stop growing, i.e. Wilson's rank formula to fail for the inclusion
matrices W_{j, j+2} at some large s with 2^s <= p. That is the single load-bearing place,
and it is a question about inclusion-matrix ranks modulo p, not about elliptic curves --
which is itself a useful narrowing: the surviving uncertainty in the ECDLP lane sits in a
classical combinatorial rank theorem.

RESULT FOR R5: HOLDS (conclusion), with the grounds corrected. Claim (A)'s conclusion
stands and is better supported than the package argues; its stated grounds are incomplete
(the linearized-polynomial hypothesis B3 is missing) and one of them (B1) leans on an
unread proof body. The data alone do not confirm (A)'s strongest reading; they refute
flatness on s = 2..5.
