---
id: KN-LIT-0a321c
type: literature
title: "Quasi-subfield polynomials and the ECDLP (read at source): the algorithm, its cost formula, the beta = l n / n'^2 quality parameter, and what the paper proves about existence"
authors: [Huang Ming-Deh, Kosters Michiel, Petit Christophe, Yeo Sze Ling, Yun Yang]
year: 2020
venue: Journal of Mathematical Cryptology 14(1), pp. 25-38, De Gruyter (open access, CC BY 4.0); received 2020-02-05, accepted 2020-02-06
identifiers:
  eprint: null
  doi: "10.1515/jmc-2015-0049"
  arxiv: null
  url: https://doi.org/10.1515/jmc-2015-0049
  source_package: inputs/HUANG-2020-JMC-QSP
tags: [quasi-subfield-polynomial, index-calculus, factor-base, summation-polynomial, semaev,
  sparse-resultant, rojas, binary-field, prime-extension-degree, characteristic-2, ecdlp,
  linearized-polynomial, additive-subgroup, multiplicative-subgroup, mersenne-prime,
  complexity-estimate, heuristic, ecc2k-130, primary-source, retrieved]
confidence: reported
citation_verified: read
provenance: retrieved
frozen_source: inputs/HUANG-2020-JMC-QSP/
source_record: SRC-HUANG-2020-JMC-QSP
verified_by: cloud-agent session on branch claude/ecc2k-130-quasi-subfield-poly-nhcj1f, 2026-09-16; frozen bytes and hashes in inputs/HUANG-2020-JMC-QSP/provenance.json
added: 2026-09-16
superseded_by: null
---

## Why this record exists

Until 2026-09-16 this program cited the quasi-subfield line only by
recollection: `GOAL-ECDLP-001`'s screening list names "Huang-Kosters-Yang-Yeo"
as a family screened out, and the SEMBIN and DREG lanes cite the same authors'
CRYPTO 2015 last-fall-degree paper from its abstract (`KN-LIT-7604` lineage,
`CORR-20260916-0c9c0a`). Under AGENTS.md core rule 9 a recalled reference is a
pointer, not support. The user asked on 2026-09-16 for an investigation of
this line as an index-calculus alternative for ECC2K-130, so the version of
record was frozen and read in full. Every claim below cites the paper's own
section, lemma, theorem or remark number; the text is at
`inputs/HUANG-2020-JMC-QSP/paper_fulltext.md`.

## What the paper does (as read)

**Setting** (Section 2). `K = F_{q^n}`, `q` a small prime, `E/K`, ECDLP in a
prime-order subgroup. Standard index calculus with factor base
`F = {(x, y) in E(K) : x in V}` for an `F_q`-subspace `V` of dimension `n'`,
relations `a_i P + b_i Q = sum_{j=1}^m P_ij`, point decomposition through
Semaev's `S_{m+1}(x_1, ..., x_m, x_R) = 0` with `x_i in V`, Weil descent to
`n` equations in `m n'` variables. Section 2.2 recalls the standard heuristics
(`|F| ~ q^{n'}`; decomposition probability `|F|^m / (m! q^n)`) and Theorem 2.1:
total cost `m! q^{n - n'm + n'} C(q, n, m, n') + m q^{2n'}`, where `C` is the
cost of one decomposition attempt and the second term is sparse linear
algebra. Section 2.3 states the two standing challenges: the decomposition cost
`C` is hard to analyse (the first-fall-degree assumption of [21] versus the
evidence against it in [16]), and in practice the method has not threatened
cryptographic curves; in the paper's words, "the best proven attack for the
important class of elliptic curves over `F_{2^n}` for `n` prime are the
generic attacks" (Section 1).

**The idea** (Section 3). Replace the subspace `V` by the root set of
`L(X) = X^{q^{n'}} - lambda(X)` with `deg lambda = d` small, when `L` splits
completely in `K`. The point is Section 3's opening observation: with
`V = F_q` (so `x^q = x`) one derives from a single summation-polynomial
equation `n` equations by applying Frobenius powers and reducing mod
`X_i^q - X_i`; a quasi-subfield polynomial lets one do the same with the
substitution `X_i^{q^{n'}} -> lambda(X_i)`. Concretely (Section 3.1): with
`phi(f) = F^{n'}(f)(lambda(X_1), ..., lambda(X_m))` (`F` raises coefficients
to the `q`-th power), `f^{q^{n'}} = phi(f) mod (X_i^{q^{n'}} - lambda(X_i))`,
so from `S^{(0)} = S_{m+1}(X_1, ..., X_m, x_R)` the chain
`S^{(k)} = phi(S^{(k-1)})`, `k = 1, ..., m-1`, gives `m` equations in `m`
variables **over `K` itself, with no Weil descent**. The system `S` is a
relaxation of the true system `T = {S_{m+1}, X_i^{q^{n'}} - lambda(X_i)}` and
may have extra solutions, which are filtered by checking `x_j in V` and
`y_j in K`. The paper assumes `S` is zero-dimensional (Appendix B argues
plausibility via `phi`-chains of prime ideals; it is not a proof).

**The cost** (Section 3.2). Lemma 3.1: Rojas' sparse resultant method
solves `S` in `O~(m^{5.188} (3d)^{4.876 m^2})` arithmetic steps (proof in
Appendix A.1: `S^{(k)}` has degree `d^{k-1} 2^{m-1}` in each variable, the
mixed volume `M(E) = 2^{m(m-1)} d^{m(m-1)}`, and the exponent `4.876` comes
from Rojas' Theorem 2.1). Theorem 3.2: total cost
`m! q^{n - n'm + n'} O~(m^{5.188} (3d)^{4.876 m^2}) + m q^{2n'}`. Remark 3.1:
if `d > q^{0.102 n / m^2}` some term is at least `O(q^{n/2})`, so the method
does not beat generic algorithms; with `m ~ alpha n / n'` and
`d ~ q^{n'^2 / n}` the exponent is `n(1 - alpha + 4.876 alpha^2) + alpha n / m`,
whose minimum over `alpha` is about `0.95`, "which beats brute force
algorithms". Definition 3.1: `L` is a **quasi-subfield polynomial** when
`L | X^{q^n} - X` and `l := log_q d < n'^2 / n`.

**Existence** (Section 4, Appendix C).
- Lemma 4.1 (proved, Appendix A.2): if `L | X^{q^n} - X` and `l > 0` then
  `floor(n/n') * l + (n mod n') >= n'`. The paper notes the bound is tightest
  when `n mod n'` is small and that `n = 1 mod n'` is "the worst case scenario".
- Section 4.2 (heuristic): about `q^{n l - n'^2}` `n'`-dimensional subspaces
  are expected to have `l = log_q deg lambda`, so none when `l << n'^2 / n`;
  the subfield case `n' | n`, `lambda = X`, `l = 0` is the known exception
  (Diem's subexponential family [4]).
- Lemma 4.3 (proved): the explicit family `n = p_{k+1} = 1 + q' + ... +
  q'^{k+1}`, `n' = p_k`, `l = p_{k-1}`, with `l < n'^2 / n`; these have
  `n = 1 mod n'`.
- Appendix C.1: for `n = 2^k - 1` a Mersenne prime, a density heuristic
  concludes the approach "cannot lead to interesting parameters ... unless the
  above probabilistic argument fails significantly" (Euler-Petit, KN-LIT-4fe9d2,
  later exhibit a family that does fail it).
- Appendix C.2: multiplicative subgroups `V = {0} U mu_r`, `r | q^n - 1`, give
  `L = X^{q^{n'}} - X^a` with `a = q^{n'} mod r`; Lemma C.2 generalises Lemma
  4.1 to `floor(n/n') l + (n mod n') >= log_q |V|`; the same negative
  expectation is stated "except maybe for exceptional parameters".

**Open problems** (Section 5, verbatim in substance): find or rule out
quasi-subfield polynomials with `deg lambda` small enough to beat generic
algorithms; whether Lemma 4.1 is tight ("removing the term `n mod n'` in this
bound would show that our approach cannot beat generic algorithms"); rational
`lambda`, isogeny maps for `L`, and double-large-prime or unbalanced variants
as untried generalisations.

## What is verified here and what is not

Verified by reading: every statement above is located in the frozen text.
Not verified: the proofs of Lemma 3.1 (depends on Rojas' Theorem 2.1, not
frozen), Lemma 4.2, and Appendix B were read for statement only. No number in
this record is the program's own; the program's arithmetic at `n = 131` is in
`analysis/qsp-ecc2k130/` and cites this record.

## Relevance to this program

1. **It is an index-calculus variant with no Weil descent**, so the
   decomposition system stays over `K` with `m` variables instead of
   `m n'` over `F_2` -- a different object from every Semaev/Weil-descent
   system this program has measured (SEMBIN, DREG, ICPERF). Its cost is
   carried by a resultant bound, not a first-fall-degree assumption.
2. **The quality parameter `beta = l n / n'^2`** (named by Euler-Petit;
   here it appears as `l < n'^2/n`) is the single number the whole line
   turns on, and Lemma 4.1 makes `n mod n'` the lever. For ECC2K-130,
   `n = 131` and `131 + 1 = 132 = 4 * 3 * 11`, so `n = -1 mod n'` for
   `n' in {2, 3, 4, 6, 11, 12, 22, 33, 44, 66}` -- the best case of Lemma
   4.1, not the worst. See `RQ-QSP-f9bbdb` and `analysis/qsp-ecc2k130/`.
3. **Theorem 3.2's constants are not ignorable at `n = 131`.** The
   `3^{4.876 m^2}` and `m!` factors that Remark 3.1 treats as constants
   are `2^{70}` and larger at `m = 3`; any concrete-cost statement for
   ECC2K-130 must keep them, which the analysis note does.

## Limits of applicability

The algorithm and every bound are conditional on the assumptions of Sections
2.2 and 3.1 (`|F| ~ q^{n'}`, the `m!` decomposition heuristic, `S`
zero-dimensional). The paper reports no implementation, no experiment, and no
parameter set at which the method beats generic algorithms; its only
constructive result (Lemma 4.3) beats exhaustive search, not rho.
