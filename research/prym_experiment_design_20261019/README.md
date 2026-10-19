# Prym experiments: geometry, source information, and cost

Designed for [issue #2414](https://github.com/aburan28/crypto-autoresearcher/issues/2414)
and [PR #2415](https://github.com/aburan28/crypto-autoresearcher/pull/2415).
**Prospective designs; no scientific trials or measured advantage.**
The four experiment contracts are `review_required`; native admission is
required before execution. This extends the [intake](../prym_relation_followup_20261019/README.md)
under existing proposal IDEA-20260909-4c5ee9.

The [diagram](diagram.svg) shows the decision sequence; [report.pdf](report.pdf)
is derived by [render_report.py](render_report.py). Full scientific contracts
live in the linked specifications, not this communication report.

## G — Verify the geometry and screen direct transfer

[EXP-ECDLP-da4ba3](../../experiments/EXP-ECDLP-da4ba3/specification.yaml),
[H-ECDLP-9e7a19](../../ledger/hypotheses/H-ECDLP-9e7a19.yaml).

For E:y²=x³+7, use eight deterministic quadratic h=(x-a)(x-b) at each of
eight primes 11 through 59. Require distinct roots and gcd(f,h)=1. These are
**64 newly specified toy covers**, unrelated to the unidentified “32 covers.”
D is the smooth fiber product y²=f, z²=h; H:w²=fh models its genus-two
complement up to isogeny.

Count E, H and D over Fp and Fp² by enumerating square multiplicities. Check
N_D=N_E+N_H-(p^m+1) for m=1,2; reconstruct F_E and F_A, factor F_A, and
compute gcd over Q. Also report whether the largest odd prime divisor r of
#E divides #A. These are different screens: Frobenius detects possible
homomorphisms; group order detects possible rational r-torsion.

Synthetic coprime/shared polynomial cases test the gcd instrument only.
Ordinary and supersingular source cases are labelled separately. Two trace
checks do not independently verify the complete genus-three polynomial.
No Jacobian map or efficient transfer evaluator is certified by this pilot.
Passing enables map/interface validation; it supplies no attack evidence.

Implemented: [geometry_pilot.py](geometry_pilot.py) and frozen prospective
[geometry_inputs.json](geometry_inputs.json). Only compilation and CLI checks
were performed this turn. Runtime wrapper, archive and admission remain due.

## W — Audit source witnesses, independent columns, and native rank

[EXP-ECDLP-ad0ffe](../../experiments/EXP-ECDLP-ad0ffe/specification.yaml),
[H-ECDLP-51f052](../../ledger/hypotheses/H-ECDLP-51f052.yaml).

A known-source constructor receives a public a and R=[a]P, frozen factor-base
atoms and cover data. It must return a checked divisor relation whose norm
has a known coefficient of P. A blind constructor receives Q+[t]P with t
public and the same base. Neither receives the secret k or factor-base logs.

Begin with the explicit PO-transfer-003 principal-divisor generator as an
instrument calibration. Use its two maps on C:y²=x6+A*x²+B:
pi1=(x²,y) to E1:Y²=U³+A*U+B, and
pi2=(B/x²,B*y/x³) to E2:V²=W³+A*W²+B². Here the Prym is elliptic; this is
a different cover family from G, and its maps need their own verification.

Check every source row independently on E1. Normalize duplicate norm images,
signs and zero columns before rank modulo r. Derive the required rank from
the actual unknown columns and gauge constraints; do not assume “B-1.”
Reject wrong signs, false labels, post-hoc kernel residuals, and tuples whose
source log is unknown. Planted known-log atoms test correctness only and are
excluded from decisive unknown-log rank and recovery panels.

Positive: an admissible generator supplies independently useful public rows.
Negative: identify the exact leakage, tautology, map error or rank defect.
Neither outcome closes all Prym approaches. The compact new router remains
open; this audit does not reopen historical IDEA-002.

## S — Test one explicit auxiliary-component selector

[EXP-ECDLP-5e7e74](../../experiments/EXP-ECDLP-5e7e74/specification.yaml),
[H-ECDLP-7cd883](../../ledger/hypotheses/H-ECDLP-7cd883.yaml).

For each PO003 cubic-interpolation candidate, sum the four interpolation
points after mapping them to E2. Before solving the residual quadratic, bucket
this auxiliary sum by infinity, or by (Legendre(W), floor(16*W/p)). This is a
testable public feature; no geometric argument currently says it predicts
factor-base acceptance. Computing it may cost more than the work it avoids.

Use disjoint hash partitions of complete candidate identities. Train on
2^16 distinct tuples and evaluate on 2^16 fresh tuples per admitted instance.
Canonicalize effective source coefficients, FB permutations and the known
acceptance-preserving involutions before hashing, so geometric aliases stay
in the same partition. This integration is still required.
Rank nonempty bins by (hits+1)/(attempts+2), retain their top quarter rounded
up, break ties by canonical bin string and reject unseen bins. A hit requires
both residual endpoints in the exact FB and a valid public source row.
Freeze the model before holdout. Insufficient support is inconclusive.

Compare identical candidate streams under no filter, identity-selector A/A,
the real filter, and a label-permuted filter. Separately test a split-product
null and transported coordinate data; these diagnose false explanations.
Independent curves are the inferential units. Acceptance precision and recall
are diagnostic; decisive metrics are charged work per independent useful row
and, eventually, complete S at the same completion target.

The [selector component](companion_selector.py) implements the maps, group
arithmetic, bins, exact model ranking and record-level split checks. Its two software tests
passed. Generator integration and the current IC baseline are still missing.
This tests an engineering improvement within a fixed generator's scope; it
does not escape P1546 or establish an improved asymptotic exponent.

## E — Attempt blind recovery with complete accounting

[EXP-ECDLP-e193fa](../../experiments/EXP-ECDLP-e193fa/specification.yaml),
[H-ECDLP-ad8992](../../ledger/hypotheses/H-ECDLP-ad8992.yaml).

Run only after source/rank validity and a genuine paired cost benefit survive
independent review. Proposed sizes are 11,13,15,17 bits of subgroup order r,
ten fresh instances per size and three paired seeds: 120 paired attempts per
arm. Freeze actual curve constants, generators, targets, search failures,
source/solver hashes and baseline receipts before approval. The challenge
process alone holds k; it reveals k only after sealed attack output.

Charge construction/search, training, preprocessing, relation attempts and
rejects, normalization, rank, linear algebra, blind descent, recovery and final
verification. Report peak memory, single-target setup-inclusive S, and any
separately specified amortized scope. A subroutine gain is not an end-to-end gain.

Success requires an independently verified complete-S improvement over the
CURRENT matched IC baseline, beyond A/A variation, with correct blind recovery
and the prescribed memory allowance. Report the distance to matched rho
separately. Rho is not the incremental pass/fail threshold. Failures and
censoring remain in the denominator; do not average successful runs alone.
Toy scaling does not certify security impact on secp256k1 or P-256.

## Admission and next work

The exact native diagnostic reports and director assessment are linked from
[admission.json](admission.json). Missing integrations and immutable runtime
bindings leave these protocols review_required, never silently approved.
No runbook is committed unless it can lint cleanly from complete inputs.
Next implement the PO003 candidate/row checker and metering integration, bind
the current verified IC pipeline, and materialize the prospective fixture sets.
The original historical contract and existing scientific states are preserved.

`dominated_by`: not assessed; no algorithmic result claimed.
`sota_delta`: no measured gain; four designs and prospective software components.
Canonical scientific graph nodes were not promoted: this graph records proposed
test dependencies, not established reduction edges.
