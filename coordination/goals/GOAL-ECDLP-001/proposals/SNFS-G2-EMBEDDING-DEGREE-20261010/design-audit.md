# SNFS-G2 embedding-degree design audit

```yaml
generated_at: 2026-10-10
task_id: T-971
fencing_epoch: 1
idea_id: IDEA-20261009-64a1c0
hypothesis_id: H-ECDLP-bd1572
experiment_id: EXP-ECDLP-6dacdb
goal_id: GOAL-ECDLP-001
idea_status: proposed
idea_approval: false
hypothesis_status: proposed
experiment_status: review_required
goal_status_change: none
scientific_result: none
disposition: reconcile with EXP-ECDLP-6dacdb; do not create a second contract
```

## Audit scope

This is a design and lineage audit, not an execution record. I read
`ledger/proposals/IDEA-20261009-64a1c0.yaml`,
`ledger/hypotheses/H-ECDLP-bd1572.yaml`,
`experiments/EXP-ECDLP-6dacdb/specification.yaml`,
`experiments/EXP-ECDLP-6dacdb/implementation/run.py`, and the directly
relevant prime-set contract `experiments/EXP-ECDLP-2535ec/specification.yaml`.
The adjacent SNFS-G1, SNFS-G4, and SNFS-E3 design audits were also checked for
lineage and priority consistency. No run output, status transition, approval,
or scientific result is created here.

`IDEA-20261009-64a1c0` is a proposed idea under `H-ECDLP-bd1572`, whose L1
limb asks whether special-form primes alter embedding-degree behavior or make
pairing transfer reach an elliptic-curve subgroup. `EXP-ECDLP-6dacdb` is
already the corresponding L1 experiment. The idea is substantially duplicate/lineage
of that experiment, not a new experiment. The shared
question, null, embedding-degree observable, public-parameter check, and
SNFS/exTNFS threshold framing are the same. The correct unit of work is a
reconciled repair of the existing contract.

## Exact overlap and boundary of the existing implementation

The existing specification and implementation already cover the following
core of the filing:

- Part A compares special-form primes with matched random primes, samples
  random short-Weierstrass curves, counts `#E`, selects the largest prime
  factor `l`, and computes the order of `p` modulo `l`.
- The current Part A contract is the small-prime `EXP-ECDLP-2535ec` family:
  `d in {2, 3, 4, 5}`, the first three special primes per `d` in the
  declared small bit interval, one matched random prime per special prime,
  64 seeded curves per prime, and seeds `[1, 2, 3]`.
- The implementation uses direct point counting by a residue table, a
  complete trial-division routine for these small point orders, and a direct
  multiplicative-order search. It reports the small-`k` fraction, mean
  `log2((l-1)/k)`, a histogram, permutation tests, and the supersingular
  field when `p % 4 == 3`.
- Part B already contains public rows for Curve25519, P-256, secp256k1,
  P-521, Ed448, and the brainpool random-prime control. It checks primality,
  the Hasse relation, and the bound-point order where a point is bound; it
  searches `p^k mod l` up to a cap of `10^6` and otherwise records a lower
  bound. It then computes a model-derived `k*` table from the configured
  GNFS, exTNFS, and SNFS/STNFS constants.

That implementation does not implement the additional scope asserted by the
idea:

1. **The `10^4`-curve Mersenne census is absent.** The idea names
   `2^31-1`, `2^61-1`, `2^89-1`, and `2^127-1`, with `10^4` curves for each
   and matched random primes. The existing code instead uses its generic
   small `m^d-c` prime generator, 64 curves per prime, and the existing
   small-bit cell set. Its point counter is an `O(p)` scan, so the larger
   Mersenne rows cannot be inferred from the current implementation or
   treated as a parameter-only extension.
2. **The `ord_l(2) <= 10^4` density census is absent.** Existing Part A
   records `k = ord_l(p)` and `t = (l-1)/k`; it does not compute
   `ord_l(2)`, enumerate the relevant factors of `2^d-1`, or compare an
   observed density with a Cunningham prediction. That is a separate
   empirical census, even though it is motivated by the same identities.
3. **The public-curve list is only partly overlapping.** P-521 and P-256
   are present in Part B. P-192 and P-224, named by the idea, are not present.
   The current rows also contain Curve25519, secp256k1, Ed448, and brainpool,
   with mixed source strength; those rows cannot be silently relabelled as
   the idea's four-curve set.
4. **The CADO polyselect comparison is absent.** `run.py` is pure Python and
   does not invoke CADO-NFS, GNFS polyselect, sieving, Murphy-E measurement,
   or norm-size reporting. It computes only the analytic threshold model and
   writes a deployed table. The idea's fixed-budget comparison of the
   special pair `(x^5 - 16, x - 2^105)` at `p = 2^521-1` against a GNFS
   polyselect is consequently a proposed addition, not an existing result.

The overlap is thus substantive enough that a second `EXP-*` record would
split one L1 question across duplicate contracts and make controls and claim
boundaries ambiguous. The Mersenne-scale, density-census, added public rows,
and optional polyselect are repairs or explicitly separate subparts of
`EXP-ECDLP-6dacdb`, not evidence of novelty.

## Arithmetic controls versus empirical and model-dependent claims

The following are theorem-closed or exact arithmetic controls for the
Mersenne form `p = 2^c - 1`, assuming the stated odd prime divisor `l` and
correct modular arithmetic:

- `Phi_1(p) = p - 1 = 2(2^(c-1)-1)`;
- `Phi_2(p) = p + 1 = 2^c`, so an odd `l` cannot give `k = 2` through
  `l | Phi_2(p)`;
- `Phi_3(p) = 2^(2c) - 2^c + 1 = Phi_6(2^c)`;
- `Phi_4(p) = p^2 + 1 = 2(2^(2c-1)-2^c+1)`; and
- the displayed Aurifeuillean product of the two factors of
  `2^(4c-2)+1`.

Consequently, the exact tests for `k = 1`, the impossibility of `k = 2` for
odd `l`, the stated `k = 3` condition, and the Aurifeuillean `k = 4`
condition are controls. A violation is first an arithmetic, factorization,
or implementation failure and invalidates the affected cell; it is not a new
mathematical observation. These identities do not determine the distribution
for `k >= 5`, and they do not prove the Balasubramanian--Koblitz null.

Likewise, `p+1=2^c` and the exact identity
`16(2^521-1)=(2^105)^5-16` are public algebraic facts. They establish the
special form of the multiplicative-side input, not a measured polyselect
advantage.

The following remain empirical or assumption-bearing:

- the special-versus-random distribution of `k` after the exact controls;
- the fraction of curve orders containing an `l` with `ord_l(2) <= 10^4`;
- agreement with a Cunningham-density prediction or a
  Balasubramanian--Koblitz null at the selected sample size;
- any larger-prime direct-order lower bound, beyond the exact computation
  actually performed; and
- any CADO Murphy-E, norm-size, or elapsed-resource comparison.

Part B's `k_actual > 10^6` is a deterministic lower bound when the direct
search and inputs pass, not an exact order. Its `k*` is a cost-model quantity:
the current code drops the `o(1)`, uses recalled constants, compares unlike
operation units, and applies an optional factor-of-`10^3` sensitivity row.
Those assumptions must remain visibly separate from the direct modular-order
receipt. A model-derived gap is not a measured ECDLP cost bound.

## Readiness and required repairs if the Coordinator later admits the existing experiment

`EXP-ECDLP-6dacdb` is `review_required`, `approved_by: null`, and has no run or
outcome. It is not selectable until the Coordinator records approval, a
dispatch handoff exists, and a frozen trial plan is present; the specification
itself currently records the missing approval ceremony, dispatch task, and
`trial-plan.json`. Do not create a second duplicate contract to bypass those
requirements.

Before any admission, reconcile the existing specification and implementation
with at least these repairs:

1. **Freeze the cell table.** State the exact number of curves per prime and
   per seed, the exact special and matched-random prime sets, and the
   resource-based reason for the sample count. If the idea's `10^4` rows are
   retained, make them a separately named, runnable cell family with an
   implementation that can support those parameters. Distinguish Mersenne
   exponent `c` from generic polynomial degree `d` and bit length; do not
   silently map `p=2^c-1` into the existing `d in {2,3,4,5}` cells.
2. **Bind `p`, `d`, and bit cells.** For every row record the family,
   `p` expression and integer, Mersenne `c` where applicable, generic-form
   `d` where applicable, bit length, matched-random construction, seed, and
   prime certificate. Reconcile the current small `EXP-ECDLP-2535ec` cells
   with any larger-prime extension instead of replacing their identity.
3. **Label factorization and order evidence directly.** For Part A retain
   the complete factorization of each `#E` with factors and exponents, and
   label `l` as the selected exact prime factor. For Part B distinguish a
   supplied public order from a factorization-derived order; record whether
   `l`, the cofactor, and `l-1` are fully certified, partially known, or
   recalled. Label direct exponentiation as an exact order only when the
   complete divisor test is performed; otherwise label it explicitly as
   `k_actual > cap`.
4. **Strengthen the supersingular control.** For every applicable special
   prime, certify `#E=p+1` for `y^2=x^3+x`, retain the exact factor used for
   the control, and require the same order routine to report `k=2`. The
   existing implementation computes a supersingular row but does not itself
   assert the required `k=2`; a missing or inconsistent control must
   invalidate the affected Part A run.
5. **Repair public-parameter provenance.** Bind the exact source commit and
   path for every field, curve equation, base point, subgroup order, cofactor,
   and special-form claim. Recheck every row independently. If P-192 or
   P-224 are retained, add their complete rows and checks; if Ed448 remains,
   keep its current recalled-only order limitation visible rather than
   treating it as equivalent to a checked base-point order.
6. **Separate Part B read and recalled cost inputs.** For each GNFS, SNFS,
   exTNFS, and STNFS constant, record whether the value is read from a named,
   versioned source or remains recalled. Keep the `o(1)` omission, operation
   unit mismatch, and factor-of-`10^3` sensitivity as explicit assumptions.
   Report `k_actual` lower bounds and `k*` model outputs in separate fields;
   neither is a measured bound without the required bound receipt.
7. **If CADO polyselect is retained, freeze it as a bounded subpart.** Pin
   the CADO version/commit, exact special and GNFS polynomial pairs, command,
   fixed 24 CPU-hour polyselect budget, CPU and memory limits, no-sieving
   rule, Murphy-E and norm-size outputs, stdout/stderr, and raw result
   hashes. Treat the comparison as a fixed public-field cost observation,
   not as an ECDLP or asymptotic claim.
8. **Complete artifacts and replay.** Preserve the exact command, source and
   input hashes, interpreter and dependency versions, seeds, raw per-cell
   machine-readable results, stdout, stderr, validity/invalidation reasons,
   timestamps, peak memory and CPU/resource measurements, and a replay
   receipt that recomputes the prime, curve, factorization, order, controls,
   and statistics. Add artifact paths for the trial plan and any CADO
   outputs; the current `raw-result.json` and manifest are not by themselves
   a complete resource or replay record.
9. **Write the review plan before review.** A claim-changing review must name
   the prior, give each load-bearing joint exactly one independent owner, set
   blindness and its deliberate lifting rule, include a proves-too-much
   control, and require blind re-derivation of the load-bearing counts and
   cost inputs. The plan and its handoff must exist before a reviewer runs.

## claim ceiling and falsification boundary

The maximum defensible claim is a finite, public-parameter control on the
declared prime cells, curve sample, exact identities, and replayed statistics.
It may report an observed special-versus-random difference, a certified
absence of odd-prime `k=2` in the stated Mersenne arithmetic, a lower bound on
the order for a named public row, or a fixed-budget polyselect comparison if
that subpart is actually run and valid. It does not support an asymptotic
claim, a universal statement about Mersenne primes, a statement about all
curves, a deployed-curve security conclusion, a secret-scalar claim, or an
ECDLP improvement.

The falsification boundary is equally narrow. A pre-registered empirical
shift in the valid census, outside its stated tolerance with all controls
passing, falsifies the corresponding finite null for that cell family. An
identity violation, failed factorization, bad order certificate, or failed
supersingular control is an invalid/infrastructure or arithmetic result to be
repaired, not evidence against the identity. A public row with an actual
embedding degree at or below the declared `k*` threshold would reopen the
transfer question and require independent breakthrough review before any
interpretation. A CADO result can falsify only the fixed cost prediction under
the pinned version, polynomial pair, and resource envelope.

## Disposition and priority

Keep `IDEA-20261009-64a1c0` proposed with approval false. Attach and reconcile
its Mersenne identities, density-census request, public-row additions, and
optional CADO subpart to `EXP-ECDLP-6dacdb`; do not create a second duplicate
experiment. Superseding the idea or replacing the existing contract is
permitted only through a new Coordinator decision with explicit lineage and
scope. No approval or status change is made by this audit.

SNFS-G1 and SNFS-G4 remain ahead of an unready duplicate G2 lane when they
offer a ranked, bounded task; this audit does not open another G2 lane or
displace either. SNFS-E3 remains a separate, lower-priority section-solver
direction until its construction, degree, solver, and control dependencies
are repaired; it is not a justification for duplicating the L1 census. The
existing EXP-ECDLP-6dacdb repair should be considered as one reconciled L1
contract in that ordering.

**next_action:** Coordinator: reconcile
`experiments/EXP-ECDLP-6dacdb/specification.yaml` and its implementation with
this audit, then run
`python3 tools/newest_experiments.py --experiment EXP-ECDLP-6dacdb --json`;
approve or dispatch only after the repaired contract reports
`execution_state: ready` and a frozen trial plan exists.
