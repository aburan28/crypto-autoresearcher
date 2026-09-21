---
id: KN-LIT-92919e
type: literature
title: "ANF-Based Satisfiability for Weil-Descent Cryptographic Attacks"
authors:
  - "Anthony Blomme"
  - "Sami Cherif"
  - "Sorina Ionica"
  - "Gilles Dequen"
year: 2025
venue: "11th International Conference on Control, Decision and Information Technologies (CoDIT 2025), Split, Croatia, pp. 906-911"
identifiers:
  eprint: null
  doi: "10.1109/CoDIT66093.2025.11321693"
  arxiv: null
  url: "https://hal.science/hal-05176414v1"
tags: [ecdlp, index-calculus, point-decomposition, semaev, summation-polynomial, weil-descent, binary-curves, sat-solver, anf, xnf, xor-reasoning, lazy-data-structures, watched-monomials, gaussian-elimination, wdsat, cryptominisat, dpll, algebraic-cryptanalysis, elliptic-curve, benchmark]
confidence: reported
citation_verified: read
added: "2026-09-06"
superseded_by: null
---

> **Provenance.** Read from a local PDF supplied by the user under
> `/Volumes/SSD990/downloads/CODIT2025_article.pdf`
> (465,285 bytes, `sha256:3c85889ee795c9d0d38184ed5cfb3408f3f65d4f1e54d359a82495ba9cfee229`).
> This is the **HAL author deposit** (`hal-05176414v1`, submitted 2025-07-22,
> CC BY 4.0), which carries its own citation block giving the CoDIT 2025 venue, page
> range and DOI. Front matter and the solver-comparison discussion were read
> directly. The DOI is taken from the deposit's citation block and was **not**
> resolved against IEEE Xplore by this program. Not vendored into `inputs/`.

## Contribution

Successor work to [[KN-LIT-102cdb]] from the same laboratory (MIS UR 4290, Université
de Picardie Jules Verne, with CRIL Lens). Builds a solver — referred to as
`DPLL_ANF` — that reasons **directly on ANF formulae** arising from Weil-descent
attacks on Semaev polynomials of elliptic curves, carrying SAT-style lazy data
structures over into the ANF setting rather than translating the instance first.

## Key claims (as reported)

**The gap it targets.** Contemporary solvers are built for CNF. ANF is the natural
form for logical cryptanalysis, and solvers that accept ANF typically convert only
part of it, yielding an **XNF** formula of mixed OR and XOR clauses, then apply XOR
recovery/manipulation and Gaussian elimination. The paper's position is that the
translation itself is the cost worth removing.

**Method.** DPLL search operating on ANF, with lazy structures adapted from SAT
solvers — the text refers to **watched monomials**, the ANF analogue of watched
literals — so that propagation is done over monomials of the algebraic system rather
than over clauses of a translation of it.

**Comparison.** Benchmarked against **WDSat** (in plain, Gaussian-elimination, and
symmetry-breaking configurations) and **CryptoMiniSat**. The authors note the
methodological asymmetry honestly: their solver and WDSat both accept ANF, but WDSat
"internally reasons on" a converted form, and for CryptoMiniSat the instances had to
be translated to XNF. Reported findings:

- Without Gaussian elimination, DPLL_ANF and WDSat appear to perform a *relatively
  similar search*, but DPLL_ANF performs it **faster**.
- Across all tested approaches, their solver achieves the **best solving times** on
  these instances, with satisfiable and unsatisfiable families reported separately.
- Gaussian elimination "is known to be inefficient" in this setting; incorporating it
  into their solver is left as future work.

**Benchmarks.** ECDLP instance families named by curve and subspace parameters —
e.g. `ECn29l9` (`n = 29`, `l = 9`) is called out as the largest family — drawn from
the public `mtrimoska/EC-Index-Calculus-Benchmarks` repository, i.e. the benchmark set
established by the WDSat line. Results are reported as average conflict counts and
solving times.

## Relevance to this program

Together with [[KN-LIT-102cdb]] this establishes a **named, benchmarked, publicly
reproducible baseline** for the point-decomposition step that the program's own
Semaev-presentation work targets, and it comes with a **public instance family**
(`EC n l` naming, `mtrimoska/EC-Index-Calculus-Benchmarks`) that this program could
adopt directly rather than inventing its own.

That matters concretely for `harness/rl_isogeny` and the `EXP-PFDR-*` line. Those
score a presentation by Macaulay-layer readings — first-fall degree and layer
sparsity — as a **proxy** for solve cost. This paper measures the thing itself, on
published instances, with three competing solvers. It is therefore both the
comparison the program's cost claims will eventually be held to, and a ready-made way
to test whether the Macaulay proxy predicts actual solve time — the open diagnostic in
[[KN-OPEN-7f0d85]] Q2, transplanted from masks to presentations.

Note the parameter scale on both sides: these are `n = 29` and `n = 41` binary curves,
i.e. toy-tier by `docs/claims-and-verification.md`, which is the same tier this
program's own presentation work occupies. The baseline is directly comparable, not
aspirational.

## Not verified here

Nothing reproduced. Conflict counts, solving times, the claimed win over WDSat and
CryptoMiniSat, and the composition of the benchmark families are **reported**. No
numeric table value is transcribed — the results table was read only as extracted
text and its columns did not survive extraction, so quote none from this entry. The
DOI and page range come from the HAL deposit's own citation block, not from a
publisher record; the benchmark repository was not fetched.
