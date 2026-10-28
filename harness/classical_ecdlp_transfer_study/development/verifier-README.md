# Independent transfer verifier

This directory is implementation preparation for the fixed-circuit transfer
study. It grants no scientific execution authority. Development checks use the
existing public F11 software fixture and fabricated record envelopes; no new
curve cohort is drawn and no candidate screen is run.

The standalone production `verify.py` imports only the Python standard library.
`independent.py` is a development test facade outside the production closure.
The verifier implements affine elliptic curve
arithmetic, its own double-and-add scalar multiplication, deterministic primality
checking for inputs below 2^64, the prime subgroup witness, a Hasse-interval
certificate for full prime curve order, and the ordinary trace check. Larger
inputs are rejected rather than treated as certified. The full-order certificate
requires the only possible positive multiple of r in the Hasse interval to be r.

For every registered r at most 8191, the primary validator primitive builds a
linear public orbit `R_k=kP`, accumulates `D_k=sum_{j<k} slope(R_j,P)`, and sets
`Z(P)=-D_r/r`, `Z(R_k)=k*Z(P)+D_k`. Its complete orbit and Z table are
validator-only state in the separate post-run process. A second table built
from `2P` and an independently written right-to-left coefficient chain are
checked at twelve fixed public points, `floor(i*r/12)P` for i=0,...,11. Larger
curves also receive twelve fixed cocycle checks. For the exact panel (r at most
127), every Z value is additionally checked by the full subgroup slope sum
`Z(R)=-sum_T slope(R,T)/r`, and the complete cocycle is checked on all r² pairs.
All constructions share the registered mathematical cocycle identity; agreement
is not an independent proof of that identity. Synthetic F11 regressions check
all three constructions, known public points, oddness and the complete cocycle.
Internal full-group primitive coverage does not imply all-r candidate bit
coverage on larger curves. No table is available to the candidate.

The interval rule uses exact integer arithmetic. L bits give the half-open
interval `[r*v/2^L, r*(v+1)/2^L)`. Its candidate is the lower endpoint rounded
up, and its upper endpoint remains strict. Arbitrary bit strings can give an
empty interval or candidate r; neither may be wrapped modulo r before the
public candidate check. Every primary attempt blinds its target by a known
nonzero `b`, uses `Q_b=bQ`, and converts `x=a*b^-1*x' mod r`, after which both
`x'P'=Q_b` and `xP=Q` must hold. Primary targets are nonidentity. Each attempt
retains exactly L fresh answers, including answers after an undefined result.
Undefined answers, empty intervals and rejected final checks remain unsuccessful
outcomes. Public SHA256 rejection-sampling replay checks domain, arm and
replicate bindings. A/A must use the same draw and return an identical result.

Coverage comes from the complete frozen cohort crossed with the eleven fixed
arms: four fresh draws for candidate, A/A and uniform arms, and one BSGS result
per public target. Every setup row and registered small all-r diagnostic must
be present exactly once. Small diagnostics retain undefined values, truth
mismatches and the full pulse residual. They never gate primary attempts. The
prior F11 positive and wrong-scalar controls occupy their own input file.

Per curve and arm, the report distinguishes actual batch counters per observed
success `(S+sum online)/successes` from the cold retry estimate with reused setup,
`S+mean(online)/q = S+sum online/successes`. Zero observed successes leave these
estimates undefined and do not establish zero true success probability. Common
input validation and cohort generation remain separately charged study phases.

A separate validator-only structural null matches oddness and the public base
anchor. It uses sixteen fixed seed indices per curve and the following frozen
hash input: `nonce32 || 00transfer-study/odd-anchor-null/v1 00 || curve_id.UTF8 ||
00 || seed_index.u32be || x.fixed_fieldwidth_be`. The hash bit is SHA256 digest
byte zero AND one, and the field width is `ceil(bit_length(p)/8)`. For finite R,
`raw_h(R)=int(y(R)>floor(p/2)) XOR hash_bit(seed_index,x(R))`; the anchored bit is
`raw_h(R) XOR raw_h(P')`, with `H(O)=0`. The full exact rule is emitted as JSON
under `validator_odd_anchor_null.rule`, with canonical SHA256
`74625aaff9665e99b277c6095393f862db776ca4fe66dc2d108dc8d734add220`.

The null repeats the same L-bit interval reduction, known a/b conversion and
both public equations, using the independent validator public-multiple table
for cached doubling and equation checks. It performs no Miller evaluation.
Small exact-panel curves receive an exact null recovery census over all
nonidentity transformed targets; larger curves receive only the same observed
blinded-target events as each actual candidate arm. Both circuits reuse the
same sixteen raw functions for a given curve, and every base anchor normalizes
those same functions. These are correlated comparisons, not additional
independent null samples. A/A is not counted again. Zero-success seeds remain
visible. Sixteen seeds provide a descriptive distribution, without a strong
tail or familywise discovery claim.

This hash-on-x null is **not coordinate covariant**. It matches oddness and
anchoring on the one canonical fresh-cohort view; source covariance is excluded
from the null comparison. Null work has separate validator event counters and
changes no primary algorithm rows, count denominators, costs or performance
claims. Oddness, anchors, deterministic encoding, exact/sample coverage and
cached recovery equations have synthetic F11 software regressions.

For the small exact panel, the existing retained all-r diagnostic bits also
give an exact candidate recovery census over nonidentity transformed targets.
This performs L table reads per target, applies the same strict interval and
public scalar equations, and makes **zero fresh constructor calls**. Its exact
q is compared with each of the sixteen exact small null q values. It is labeled
`retained_bit_exact_recovery_census` in small diagnostics and
`candidate_retained_bit_exact_census` in the null comparison. Its counters are
separate validator work. Primary fresh success events and larger sampled q
remain unchanged; the retained-bit census is not another executed solver run.

Arithmetic witness checks and complete trace coverage do not themselves prove
fresh execution or the correctness of a producer's cost counters. Source hashes,
the producer boundary, and an eventual approved execution record are separate
requirements. The verifier's own counters describe validation work only: exact
orbit builds, entries, reads and affine group/slope/inversion calls across the
primary oracle and controls. They are not complete machine or field costs. No
native counter replay, machine timing, attack-cost claim, global novelty claim,
or asymptotic exponent claim is made here.

Source review completed before implementation (internal provenance):

- `/workspace/classical-ecdlp-validation-ready/AGENTS.md`, the literature-first
  and observation-first rules in `docs/agent-contract-extended.md`, and
  `ledger/goals/GOAL-ECDLP-e70832/goal.yaml`, including its no-new-science boundary.
- The prior `harness/classical_ecdlp_nongeneric_screen/verify.py`,
  `constructor.py`, `protocol.plan.json`, `README.md`, and software regressions.
- The fixed-grammar proposal at
  `coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-45711d/nongeneric-design/proposal/proposal.md`.
- `/workspace/classical-ecdlp-endpoint-reuse/continuation-nongeneric/primary-source-retrieval.json`
  records a prior agent's reading of Voloch's zeta preprint
  <https://www.math.canterbury.ac.nz/~f.voloch/Pdfs/zeta3.pdf>, Acta Arithmetica
  79 (1997), DOI 10.4064/aa-79-1-1-6. It explicitly supplies no local PDF byte
  hash. This task did not independently reread that primary source: remote work
  was excluded by its scope. It is a prior source-review pointer, not new support
  for an analytic-zeta identification or decoder correctness.

The source search and primary-source gap above do not establish novelty. This
verifier checks the explicitly stated finite arithmetic and public equations.

Software tests: `python3 -m unittest -v test_independent.py test_verify.py`.

Production interface (an example only; no scientific records were checked):

```sh
python3 verify.py --protocol compute-plan.json --cohort cohort-public.json \
  --source-manifest source-manifest.json --source-root source \
  --prior-exclusions prior-exclusions.json --controls control-phase.json \
  --attempts attempts.jsonl --setups setups.jsonl --diagnostics diagnostics.jsonl \
  --output verification.json
```

The CLI requires frozen source/plan bytes, the exact seven-module closure,
bound exclusions and complete streams. It independently checks prospective
strata, field/j exclusions and public prime-order witnesses. It does not replay
the full generator proposal stream, census counters or producer cost counters;
its output records those limits.
