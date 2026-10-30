---
id: KN-LIT-caa51d
type: literature
title: "The Exponential Time Hypothesis is False (openai/math family 378)"
authors:
  - "OpenAI (unnamed internal model; no human author listed)"
year: 2026
venue: "openai/math repository, preprint dated 2026-10-25, released in commit 42907c9 (2026-10-26)"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://github.com/openai/math/blob/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf"
tags: [sat, eth, exponential-time-hypothesis, counting, complexity, decomposition, pdp, galactic, openai-math, unverified-proof]
confidence: reported
citation_verified: read
added: "2026-10-27"
superseded_by: null
---

## Contribution (as reported)
For every fixed `k >= 2`, the paper gives a deterministic algorithm that
counts the satisfying assignments of a `k`-CNF with `n` variables and `m`
clauses. It runs in time `(n+m)^{O_k(1)} 2^{n/(log n)^{1/2+o(1)}}` and
polynomial space. Taking `k = 3` refutes ETH. The method:
- clause polynomials of degree at most `3n` (after sparsification and
  variable copying);
- interpolation from restricted sums over small variable groups;
- a derandomized auxiliary construction.

An appendix corollary inverts, and counts preimages of, Boolean maps whose
output bits each read `O(1)` input bits, in the same time.

**Proof status.** Not checked here.
- Lean scope (`lean/docs/378.md`): time
  `(L+1)^{O_k(1)} 2^{O_k(n (log log n)^2/√log n)}`.
- Comparator statement: `ComparatorChallenges/SubexponentialSAT.lean`,
  `exact_count_and_sat`. It was not compared with the paper, and the Lean
  was not built.
- `history.md` says a working group led by R. Impagliazzo, R. Paturi and
  R. Williams will examine the proof.
- OpenAI's announcement of 2026-10-26 ("Working with academic communities to
  build scientific understanding") returned HTTP 403 to automated fetches.
  It is known here only through search summaries and Gizmodo's coverage.
  That coverage recalls an earlier claim (Navier–Stokes) where Lean verified
  a weaker assertion than the one published.

## Read here (verified against the TeX, `main_full_version.tex`)
- The overview's cost (eq. `overview-three-costs`) multiplies three factors:
  Taylor data, measurements, and `2^{2n/r}` for one group, with
  `r = Θ(√log n/(log log n)^2)`.
- The parameter bounds hold "for sufficiently large `n`", with
  `D = r^{2Q} <= (2n)^{1/128}`.
- The constants hidden in `Θ` and `O_k` are not given.

## Relevance to ECDLP relation finding: galactic
These are our derivations from the stated bounds, not measurements.

**Against PPSZ (`2^{0.386 n}` for 3-SAT).** The group factor alone wins
only when `2/r < 0.386`, i.e. `r > 5.2`. With the hidden constant set to 1
and natural logarithms, that needs `log n ≈ 10^6`, i.e. `n ≈ e^{10^6}`.

**Against enumeration for binary point decomposition**
(`LEAD-ICB-decomposition-encoding-and-sat`). The unknowns are `m·l` bits.
- A `k`-CNF encoding needs auxiliary (Tseitin) variables for the field
  multiplications. Their number `N` grows superlinearly in `l`: `Θ(l^2)`
  with schoolbook multiplication.
- The count costs `2^{N/√log N}`. Whenever `N = ω(l √log l)`, that exponent
  grows faster than `m·l`, so the algorithm loses to plain enumeration of
  the `m·l` unknowns at every `l`, not only at small `l`.
- The constant-locality corollary does not apply. The Weil-descended
  summation polynomials give output bits that depend on most of the
  unknowns.

**Whole ECDLP as CNF.** `N = poly(circuit size)`, so the count is far above
`2^{n/2}`.

**What it changes.** No `2^{Ω(n)}` lower bound on a SAT step may be assumed
in any cost model. A grep of `crypto` found no cost row that assumes ETH.

## Limits
- Unverified proof (see Proof status). Asymptotic only, with unstated
  constants.
- A counting algorithm. Search costs `n` further counts by self-reduction.

## Pointers
- `crypto` PR #2680:
  `research/notes/ecc2k130/RESEARCH_ECC2K130_IC_LITERATURE.md`, addendum
  2026-10-26.
- `cryptanalysis/experiments/lit-watch`: its tests use `openai/math` as a
  fixture.
