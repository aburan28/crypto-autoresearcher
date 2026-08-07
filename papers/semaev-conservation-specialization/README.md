# Conservation and Specialization in Semaev-Based Index Calculus over Prime Fields

Manuscript draft. **Not submitted, not posted, and not cleared for either.**

- `paper.tex` — the manuscript (LaTeX, `article`, needs only `amsmath/amssymb/amsthm/
  mathtools/geometry/hyperref/booktabs`).
- Verification code and artifacts: `../../experiments/EXP-SMON-e5cbe6/`
- Ledger: `H-SMON-db677d`, `EV-SMON-9c1c23`, `DEC-20260807-64df6a`,
  `CORR-20260807-652652`, `KN-FIND-a8990a`.

## What it says

1. **Theorem 3.4.** The Galois group of `S_m(t_1,…,t_{m-1},T)` over
   `K(t_1,…,t_{m-1})` is `(Z/2)^{m-2}` acting simply transitively, for every elliptic
   curve over every field in every characteristic. The splitting field is
   `K(E^{m-1}/Δ)` with `Δ` the diagonal inversion; the group is the deck group of the
   fibre product of `m-1` copies of `x : E → P¹`, modulo the diagonal. Arithmetic
   monodromy equals geometric monodromy.
2. **Theorem 4.2.** Over `F_q`, at every specialization outside an explicit degenerate
   locus of size `O_m(q^{m-2})`, `S_m(a,T)` is either totally split or a product of
   `2^{m-3}` irreducible quadratics — never a factor of degree `≥ 3`, never a mixed
   type — according as the `m-1` fibres of the `x`-map are simultaneously rational or
   not.
3. **Theorem 5.1.** The factor-base locus lies entirely inside the totally split locus,
   at every `m`.
4. **Proposition 6.1.** Conservation: mean decomposition yield is
   `binom(B+m-1,m)/N` for *every* factor base of size `B`.

Synthesis: generic-fibre arithmetic statistics and factor-base relation statistics are
different objects. Several proposed relation-rate levers are fixed either by
conservation or by complete splitting on the rational-point locus.

## What it does not say

No ECDLP speedup, no security reduction, no new hardness result, no change to any
complexity estimate. Section 5.1 explains at length why complete splitting is *not* an
algorithm — it solves for the last coordinate given the others, while relation search
does the opposite.

## Two blockers before this goes anywhere

1. **No independent proof review has been obtained.** Point a reader experienced in
   function fields or arithmetic geometry at Lemma 2.3 (Artin's theorem for a quotient
   by a finite group acting faithfully) and Lemma 3.2 (properness of the preimage of
   `E[2]`, in characteristic 2 where `E[2]` is non-reduced).
2. **Novelty is not adjudicated.** `eprint.iacr.org` returned HTTP 403 to every request
   from the environment this was written in, including Semaev's own 2004/031. Section 9
   lists exactly what a reader with access must check. The searches that *were* possible
   surfaced nothing stating Theorem 3.4 or 4.2, which is weak evidence and not a claim.

## Reproducing the verification

```sh
cd experiments/EXP-SMON-e5cbe6/code
python3 verify.py --out ../runs/RUN-SMON-e5cbe6-002/raw-result.json   # ~70 s, no deps
```

Deterministic (seed `20260807`); the committed `RUN-SMON-e5cbe6-001/raw-result.json`
should be reproduced byte for byte. Content hashes are in that run's `manifest.yaml`.

## Building

`paper.tex` **has not been compiled** — no LaTeX toolchain is present in the
environment where it was written. Its structure was checked programmatically (balanced
environments, no dangling `\ref`/`\cite`), but it has never been typeset, so expect the
usual first-compile friction.

```sh
latexmk -pdf paper.tex
```
