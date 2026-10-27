# F1 source review before implementation

26 October 2026, `/root/pass2_symmetric`, TASK-20261026-a0cc5b.
Phase A preparation only: no new mathematical program was imported or executed.

Sources actually read in this session:

- **Retrieved primary paper:** Petit, Kosters and Messeng, *Algebraic approaches
  for the Elliptic Curve Discrete Logarithm Problem over prime fields*, PKC 2016,
  https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf. Read the abstract,
  introduction and section 2.1 by streaming its PDF through `pdftotext`. The paper
  describes composed low-degree membership maps, separates that description
  from unresolved relation-solving complexity, and suggests dedicated solving
  approaches. Its composed-domain framework is prior work; no novelty or
  complexity improvement is claimed here.
- **Internal primary derivations and source:** the prior study's
  `tracks/f1/derivations.md`, `f1.py`, `forward.py`, and
  `tracks/f1/cubic-divisor/{derivation.md,cubic.py,checks.py,report.md,result.json}`.
  These give the exact Dickson chain, separable-factor scheme, repeated strata,
  committed symmetric S4 and the unresolved fixed depth-four attempts. Old
  reports are historical evidence, not an independent verification by this
  session. Fixed parameters, terminals and target points are copied as inputs;
  old roots, answers and bases do not enter the new implicit extractor.
- **Retrieved official implementation source:** python-flint 0.8.0
  https://raw.githubusercontent.com/flintlib/python-flint/0.8.0/src/flint/types/fmpz_mod_mat.pyx.
  Read constructor, `rref`, `rank`, `solve`, `charpoly`, indexing and transpose
  definitions/docstrings. `rref` returns `(matrix, rank)` and assumes a prime
  modulus. There is no dependency on an unverified `nullspace` API: the new
  implementation derives a right-kernel basis from RREF pivots and checks it.
- **Internal workflow sources:** `AGENTS.md`, literature-first and
  observation-first rules, `docs/experiment-protocol.md`, protocol/export schemas,
  `tools/experiment_protocol.py` seed/export/flow routines, the worked example,
  the committed task card and `workflow/execution-gates.md`. These require a
  prospective frozen protocol, source identity, actual checkpoint gate, exact
  row accounting and fresh reports. Syntax/schema checks are preparation only.

The exterior-quotient construction in `derivation.md` is a self-contained derived
argument in this session. No external source was retrieved establishing priority
for that particular formulation; absence of such a source is not evidence of
novelty. The paper's full experimental analysis and unrelated complexity claims
were not reverified.

Assumptions checked in the design: actual published P-256 has odd characteristic
greater than three; the generic terminal must satisfy `c != ±2`; the scalar
chain then has a separable degree-`2^k` polynomial. Complete rational extraction
also checks that every retained eigenspace is recovered as a rational character.
The old finite fixtures split over Fp; the independent reference will check the
full root count again after release. The nonseparable control must be refused.
No result transfers from a fixed matrix of dimension `C(2^k,3)` to large depths,
relation yield, logarithm labels, total attack cost or a whole ECDLP solve.
