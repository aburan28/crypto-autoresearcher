---
id: KN-LIT-102cdb
type: literature
title: "Parity (XOR) Reasoning for the Index Calculus Attack"
authors:
  - "Monika Trimoska"
  - "Sorina Ionica"
  - "Gilles Dequen"
year: 2020
venue: "arXiv preprint (MIS Laboratory, University of Picardie Jules Verne)"
identifiers:
  eprint: null
  doi: null
  arxiv: "arxiv:2001.11229"
  url: "https://arxiv.org/abs/2001.11229"
tags: [ecdlp, index-calculus, point-decomposition, semaev, summation-polynomial, weil-descent, binary-curves, sat-solver, anf, xor-reasoning, gaussian-elimination, minimal-vertex-cover, wdsat, cryptominisat, groebner, algebraic-cryptanalysis, elliptic-curve]
confidence: reported
citation_verified: read
added: "2026-09-06"
superseded_by: null
---

> **Provenance.** Read from a local PDF supplied by the user under
> `/Volumes/SSD990/downloads/2001.11229v1.pdf`
> (282,752 bytes, `sha256:2655d755d58e7f97b5a2123dcb0372c42b227e6d334d338ce788ff70c77e8da2`),
> marked `arXiv:2001.11229v1 [cs.CR] 30 Jan 2020` on its own first page. Sections 1–2
> and the experimental discussion were read directly; the identifier is
> self-reported by the document and was **not** confirmed against the arXiv listing
> by this program. The PDF is not vendored into `inputs/`.

## Contribution

A purpose-built SAT solver, **WDSat**, for the *point-decomposition* step of the
index calculus attack on elliptic curves over `F_{2^n}`. Rather than translating the
algebraic system to CNF, WDSat reads **algebraic normal form (ANF)** directly and
reasons natively about XOR (parity) constraints. Two further contributions: a
correction to how Gaussian elimination is done inside XOR-enabled SAT solvers, and a
graph-theoretic preprocessing step.

## Key claims (as reported)

**The problem it targets.** Following Gaudry and Diem, a point on the curve is
decomposed into `m` other points by solving Semaev's `(m+1)`-th summation polynomial
`S_{m+1}`. For `E/F_{2^n}`, an x-coordinate is an `n`-bit vector; the standard
parameterisation decomposes a random point into `m` points whose x-coordinates lie in
an `l`-bit subspace with `l ~ n/m`. This is exactly the point-decomposition
bottleneck, not the full discrete log.

**The XG-ext method — the paper's sharpest technical point.** Gaussian elimination on
a CNF-XOR instance is *not* equivalent to Gaussian elimination on the underlying
algebraic system. There is a **cancelling property** present in algebraic resolution
that is lost when the instance is presented as OR-plus-XOR clauses: the second premise
needed for the inference either disappears or must be recovered by syntactic search.
The authors' remedy is that **the solver must read ANF** in order to retain it, and
they give six inference rules for the substitution case. They are explicit that XG-ext
"comes at a high computational cost" and pays only where it cuts conflicts
substantially.

**Minimal-Vertex-Cover preprocessing.** A preprocessing technique based on the minimal
vertex cover problem, designed to permit rapid linearisation of the underlying
algebraic system. Reported as **conditional on XG-ext**: without the substitution
machinery, "the positive outcome of the preprocessing technique cannot [be]
guaranteed." Confirmed adversarially — pairing the same preprocessing with
CryptoMiniSat produced **slower** runtimes than CryptoMiniSat alone.

**Benchmarks.** Instances from the third summation polynomial (`m = 2`) at
`n = 41`, `l = 20`, giving systems in roughly 40 variables. Satisfiable and
unsatisfiable instances are reported separately because their runtime and memory
profiles differ. WDSat is reported to outperform Gröbner-basis techniques, MiniSat,
Glucose and CryptoMiniSat on these instances.

**Security-assessment framing.** The authors propose the preprocessing technique
itself as an assessment instrument for a cryptographic system, tied to a worst-case
time-complexity statement for the optimised solver.

## Relevance to this program

This is close to the centre of the ECDLP spine and should have been in the corpus
already. `harness/macaulay_fp` and the Semaev-presentation work
(`harness/rl_isogeny`, `KN-FIND-007`, the `EXP-PFDR-*` battery) all attack the same
object — the polynomial system a point-decomposition solver sees — but score it
through **Macaulay-layer readings**, whereas this paper attacks it with a **dedicated
SAT solver** and measures wall-clock. Two distinct consequences:

1. **A missing baseline.** Any claim this program makes about a presentation being
   cheaper must eventually be compared against a solver that reasons on ANF natively.
   WDSat is a named, published, benchmarked competitor for exactly the step
   `harness/rl_isogeny` is trying to make cheaper, and the program's records do not
   currently cite it.
2. **A methodological warning that matches one this program already holds.** The
   MVC-preprocessing result — a transformation that helps one solver and *hurts*
   another — is the same shape as the proxy/objective mismatch recorded in
   [[KN-TECH-d64293]] and [[KN-OPEN-7f0d85]]: a local restructuring scored against the
   wrong downstream consumer inverts sign. Here it is measured rather than argued.

See also [[KN-LIT-92919e]], the successor work from the same laboratory, which
reasons on ANF without WDSat's internal translation and reports beating it.

## Not verified here

Nothing reproduced. The runtimes, conflict counts, the claimed advantage over Gröbner
and the three SAT solvers, the worst-case complexity statement, and the `n = 41`,
`l = 20` parameterisation are all **reported**. The arXiv identifier is self-reported
by the PDF and unconfirmed against the listing. Tables 3 and 4 were read only through
extracted text, so no numeric benchmark value is transcribed into this entry — quote
none from here without opening the PDF.
