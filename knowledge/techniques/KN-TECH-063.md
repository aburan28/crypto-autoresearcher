---
id: KN-TECH-063
type: technique
title: Truncated, higher-order, and impossible differentials - relaxing, lifting, and inverting the differential predicate
tags: [truncated-differential, higher-order-differential, impossible-differential, miss-in-the-middle, algebraic-degree, derivative, structural-distinguisher, block-cipher, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "truncated: probability aggregated over a difference set, so a set of size 2^t gains up to a factor 2^t over a single difference; higher-order: 2^{d+1} chosen plaintexts distinguish a component of algebraic degree <= d; impossible: data set by the cost of eliminating wrong keys, not by any positive probability"
applicability: word-oriented SPNs and Feistel networks (truncated), low-algebraic-degree round functions (higher-order), and any cipher whose middle rounds admit a contradiction between forward and backward propagation (impossible)
source_refs: [KN-TECH-062, KN-LIT-4765, KN-LIT-2162, KN-LIT-4214, KN-LIT-4409, KN-LIT-1995, KN-LIT-3896, KN-LIT-2516, KN-LIT-4764, KN-LIT-5965, KN-TECH-074]
added: 2026-07-31
superseded_by: null
---

## Method

Three independent relaxations of the differential predicate of `KN-TECH-062`.
They are grouped here because each changes *what is predicted*, not how the
prediction is exploited.

### Truncated differentials (Knudsen, 1994)

Predict only part of the difference — typically *which words are active* rather
than their values. The predicate becomes a set membership, so probabilities
aggregate: a truncated differential covering `2^t` output differences is up to
`2^t` times likelier than any single one it contains. This is the natural
granularity for byte- or nibble-oriented SPNs, where the linear layer acts on
words and the activity pattern is what propagates deterministically.

The structural distinguishers on AES-like designs live here: activity-pattern
and multiset properties of 5-round AES (`KN-LIT-2162`), and the truncated
boomerangs of `KN-TECH-064`. Truncated differentials also have a documented
correspondence with multidimensional linear properties (`KN-LIT-4765`), which is
one of the links catalogued in `KN-TECH-069`.

### Higher-order differentials (Lai; Knudsen, 1994)

The `d`-th order derivative of a function of algebraic degree `d` is constant,
and the `(d+1)`-st is zero. Concretely: if every output bit of `E_k` restricted
to the relevant variables has degree at most `d`, then

  `⊕_{v ∈ V} E_k(x ⊕ v) = 0` for any affine subspace `V` of dimension `d+1`.

The distinguisher costs `2^{d+1}` chosen plaintexts and is **deterministic** —
it is a structural identity, not a statistical bias, so no data is spent
separating signal from noise. Everything downstream of it in this corpus is the
same identity in different clothing: the integral/saturation property, the cube
sum (`KN-TECH-073`), and the division property that predicts when the identity
survives (`KN-TECH-074`).

Its reach is set entirely by **algebraic degree growth**. Degree grows quickly
in bit-oriented designs with high-degree S-boxes and slowly in designs chosen
for low multiplicative complexity — which is why higher-order differentials are
the dominant tool against arithmetization-oriented ciphers (`KN-TECH-075`) and
against components with an exploitably low degree (`KN-LIT-4214` on Keccak and
Luffa; `KN-LIT-4409` and `KN-LIT-1995` on MISTY1).

### Impossible differentials (Knudsen; Biham–Biryukov–Shamir, 1998–99)

Use a differential of probability **exactly zero**. The construction is
**miss-in-the-middle**: propagate a difference forward from the plaintext with
probability 1 for some rounds, propagate another backward from the ciphertext
with probability 1, and exhibit a contradiction where they meet.

The exploitation inverts the usual logic. Instead of a right key being
*reinforced*, every key guess that produces the impossible pair is *eliminated*.
So the data complexity is governed by how fast wrong keys are sieved out, and
the analysis obligation is a counting argument over the remaining key space —
not a signal-to-noise ratio. The canonical result is 31-round Skipjack; the
technique is standard against Feistel and generalised-Feistel structures
(`KN-LIT-2516`).

Impossible-differential search is now automated (`KN-LIT-3896`), and structural
provable-resistance arguments exist against it (`KN-LIT-5965`). It sits in a
documented equivalence family with zero-correlation linear approximations and
integral distinguishers (`KN-LIT-4764`), catalogued in `KN-TECH-069`.

## Program usage

- **The higher-order route is the one that touches this program's own
  machinery.** A higher-order differential is a statement about algebraic
  degree, which makes it directly continuous with the Gröbner and MQ solving
  entries (`KN-TECH-004`, `KN-TECH-011`, `KN-TECH-053`) and with the
  degree-of-regularity discipline the program already applies to
  summation-polynomial systems. The connection is real but must not be
  overdrawn: degree growth in a cipher and the solving degree of a polynomial
  system are different quantities and are not interchangeable.
- **Impossible differentials are the cleanest available example of a
  zero-probability control.** The program's inventor protocol (`KN-TECH-056`)
  requires null-object controls before belief; the miss-in-the-middle
  construction is a mature instance of proving a *negative* structural fact and
  then exploiting it, and is worth reading as protocol precedent rather than as
  an ECDLP tool.
- **Truncated differentials are the reason activity patterns, not difference
  values, are the right abstraction for word-oriented designs.** That choice of
  abstraction is what makes automated search tractable (`KN-TECH-076`).

## Applicability limits

- **Truncated differentials need word structure.** Against a design with no
  word-aligned linear layer, the aggregation that makes them work has nothing to
  aggregate over.
- **Higher-order differentials need a *bound* on degree, not a guess.** The
  distinguisher is deterministic only if the degree bound holds; an
  underestimated degree yields a test that simply fails, and an overestimated
  one wastes `2^{d+1}` data. Establishing the bound is the hard part, and is
  exactly what `KN-TECH-074` exists to do.
- **Impossible differentials prove nothing positive.** They eliminate keys.
  Turning elimination into recovery requires the key-space counting argument to
  actually close, and published attacks in this family have historically needed
  correction when that counting was done loosely.
- **All three are usually round-reduced.** The round count and the access model
  belong in every citation, per `KN-TECH-062`.

## Verified vs reported

Governed by the sourcing note in `KN-TECH-062`, which applies in full. The
derivative identity, the `2^{d+1}` cost, the aggregation factor for truncated
differentials and the miss-in-the-middle construction are standard published
results written from established knowledge, not re-derived here. Knudsen's and
Lai's foundational papers are named in prose because this corpus holds no
`KN-LIT` entry for them; no identifier was minted. The MISTY1 figures implied by
`KN-LIT-1995` and `KN-LIT-4527` are **title-level only** — this program has not
read those papers, and the titles are the whole of what is archived. The
placement of the higher-order/integral/cube/division-property chain as one
identity in four presentations is this program's own framing.
