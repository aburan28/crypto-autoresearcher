# Prime-field algebra diagnostics: leads 3 and 4

`run.py --config proposed_config.json --output result.json` constructs a finite,
fully specified corpus and emits certificates. Do not run it until the parent
experiment protocol has been frozen and admitted. `check.py result.json` is an
independent verifier: it imports neither the producer nor its polynomial core.

The ordinary corpus is the coordinate residual `S3(x,y,r)=0`, with two `s`-bit
coordinate blocks. It does not enforce curve-point membership, target subgroup
membership, distinctness or a complete point decomposition. This is an algebra
instrument on an explicitly limited residual. The null population replaces each
nonzero input coefficient with a deterministic nonzero coefficient, preserving
the exact support. The control panel includes an affine contradiction and a
synthetic gated circuit with a known one-bit strong backdoor.

## Lead 3

The four arms ablate whole versus partial batches and total versus block
filtration of **squarefree multiplier monomials** in
`Fp[b]/(b_i^2-b_i)`. Total batches group multipliers by total degree. Block batches
group by the maximum degree in either coordinate block. Partial batches split
each level into fixed batches of sixteen multipliers. These are explicitly
defined Boolean adaptations, not a proof that ordinary homogeneous regularity
or the last-fall degree decreased.

Each row has a certificate as an exact linear combination of original generator
multiples. The solver stops on a constant contradiction, or after checking that
the span contains all inputs and is closed under multiplication by every Boolean
variable. The latter proves equality with the input ideal. Root extraction then
enumerates the Boolean cube, and this enumeration is counted. The independent
checker verifies all certificates, closure, the rank/model-count identity and
the entire model set. Oracle results are generated only after the solver arms;
they never select rows or stopping points.

The A/A arm reverses equation input order. In single-generator ordinary cells
this is intentionally identical; in controls it exposes row-order sensitivity.
No wall-clock metric is a primary metric. Operation counts include certificate
arithmetic and repeated closure checks. `generated_matrix_entries` is a defined
dense matrix-size proxy, not a measured process-memory peak.

The source-method calibration uses the four displayed quadratics from pages
4–5 of the authors' August 2026 slides, explicitly homogenizes them over F5,
and reconstructs initial-segment homogeneous matrices at degrees 2 and 3. The
slide does not name the field, so F5 is this protocol's choice. Every matrix and
its rank are independently reconstructed, and every projective chart is covered
by exhaustive normalized coordinates. This calibrates matrix construction;
it does not reproduce a published benchmark table or establish the paper's
monomial semi-regularity assumptions.

**Unfinished original lead:** the full 2026 paper's rank-prediction reproduction,
the published 2025 Multi-homogeneous XL algorithm, and a valid target-system
multi-homogenization with infinity-chart accounting remain unimplemented. The
block arms must not be reported as that published algorithm.

## Lead 4

Cuts contain two Boolean variables. Policies use only public equation syntax:
fixed first-block bits, a seeded SHA256 ordering, min-fill order of the monomial
interaction graph, and a degree-drop policy enumerating pairs and minimizing
the sorted list of residual syntactic monomial degrees. Selection work is
recorded. The degree-drop policy does not inspect witnesses, oracle solutions,
or trial solver results. Its pair search is charged rather than called free
preprocessing.

For every one of the four legal assignments the residual solver includes all
original-generator Boolean monomial multiples whose reduced degree is at most
two. It then obtains affine consequences by exact elimination. It reports a
complete branch only on a checked contradiction or when at most two affine
free variables remain, in which case all at most four candidates are checked
against the original residual. Any other branch is `UNKNOWN`. A strong backdoor
is reported only when every legal branch is complete. This is a bounded
monomial-multiple procedure, not full polynomial-calculus closure.

All residual arithmetic, certificate work, candidate checks and selection work
are retained. Arithmetic operations and syntactic selection operations have
different units and must be shown separately; their sum is not elapsed time.
The independent checker enumerates every legal branch and verifies that its
solutions agree exactly with the unspecialized instance under that assignment.

## Primary source reconciliation

- [2026/408](https://eprint.iacr.org/2026/408): landing page read; PDF and version
  endpoint returned HTTP 403 on 2026-10-29. No full-text theorem claim is made.
- [Author slides](https://pqcrypto.cs.ru.nl/ampqc/slides/Tuesday_Melvin.pdf):
  pages 4–9 specify the initial-segment construction; pages 10–12 separate
  trivial syzygies and the rank assumptions.
- [Authors' code](https://github.com/LarsMath/monomial-of-regularity):
  `solver.sage`, `tools/algebraic_tools.sage` and `tools/prediction_tools.py`
  inspected through their raw primary URLs. The solver constructs a homogeneous
  Macaulay matrix and selects a predicted trailing submatrix; the calibration
  here reconstructs the mechanism without assuming the prediction.
- [2025/2060](https://eprint.iacr.org/2025/2060): landing page read; PDF returned
  HTTP 403. [Authors' implementation](https://github.com/kcning/MinRankSolver)
  states GF16 support and requires extension for arbitrary fields.
- Local `KN-LIT-deca10` explicitly records abstract-only ingestion, so it does
  not fill the full-paper gap.
- Existing `IDEA-20260904-b40e6d` concerns a binary CNF-XOR null ladder with a
  fixed factor-base backdoor. `IDEA-20260905-24d827` already proposes prime-field
  CDCL comparisons. `IDEA-20260930-ba8184` motivates the two-free-block degree
  obstruction. The current work is a complete tiny strong-backdoor diagnostic,
  not a claim to have originated backdoor or hybrid solving.

No output of this program is a prime-field ECDLP attack, a large-field scaling
measurement, or an exact degree-of-regularity theorem.
