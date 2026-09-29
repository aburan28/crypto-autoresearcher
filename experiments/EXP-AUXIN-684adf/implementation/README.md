# EXP-AUXIN-684adf implementation (zero-run)

This directory contains the reviewable source implementation of the
generalized-CRT calibration frozen in
`experiments/EXP-AUXIN-684adf/specification.yaml`, produced under
`ledger/handoffs/TASK-20260907-58fcbe.yaml`. **No scientific execution has
occurred.** `maximum_runs: 0` for this task; every function that would
perform fixture evaluation, CRT folding, independent verification, or
cost-model measurement over real inputs exists as reviewable code but has
not been invoked against the declared 26,546-case panel. The only checks
actually performed were static (syntax compilation and module import) —
see `implementation-report.yaml` for the exact list.

A later, separately authorized scientific handoff (not this one) supplies
its own allocated `RUN_ID`, an independent implementation review of these
five files, and a genuine launch lock bound to the exact approved
spec/code bytes before any cell may be evaluated. See
`docs/agent-runtime-core.md` "Experiment execution" and this experiment's
`execution_gate`.

## Module map: specification requirement -> source

| Specification section | Responsibility | Source |
| --- | --- | --- |
| `arithmetic_definitions.fold` | Generalized CRT fold (gcd consistency, `h`, modular inverse, `Mnew`/`Anew`) | `crt.py::fold_congruences` |
| `arithmetic_definitions.residue` | Canonical residue reduction, `a=0` for `m=1` | `crt.py::canonical_residue` (production), `reference.py::_independent_canonical_residue` (independent copy) |
| `arithmetic_definitions.candidate_set` | Candidate exponent enumeration `E={k0+M*t}` | `crt.py::enumerate_candidates` |
| `arithmetic_definitions.primes`, `primality`, `primitive_element` | Prime/factorization data, trial-division primality, least-primitive-element search | `fixtures.py::PRIMES`, `is_prime_trial_division`, `verify_factorization`, `find_primitive_element` |
| `arithmetic_definitions.nonzero_positions`, fixture truth `x=pow(zeta,k,r)` | Fixture truth generation, kept on a separate channel from CRT input | `fixtures.py::fixture_truth` |
| `arithmetic_definitions.toy_original_verification` | Independent scalar-equality surrogate check, evaluate-all-candidates, match count/first-match index | `reference.py::verify_original_target` |
| `arithmetic_definitions.independent_reference` | Independent brute-force full-domain scan, sorted-set comparison, independent candidate-scalar verification | `reference.py::full_domain_matches`, `is_consistent`, `compare_candidate_sets` |
| `input_supply.token_binding` | Per-constraint labeled token placeholders, `d=n//m`, `source_kind=synthetic_placeholder`, multiplicity/distinct-`d` reporting | `fixtures.py::TokenRecord`, `make_token_record`, `token_multiplicity_report` |
| `input_supply.acquisition_cost_policy` | Explicit `None`/`not_executed` accounting for real acquisition | `cost_model.py::AcquisitionAccounting` |
| `positive_panels` (P00-P11) | Literal panel table, verbatim | `fixtures.py::POSITIVE_PANELS` |
| `inconsistency_panels` (I01-I04) | Literal panel table + residue-rule evaluator | `fixtures.py::INCONSISTENCY_PANELS`, `inconsistency_residues` |
| `wrong_target_panels` | Source-positive-id list, `(k+1) mod m` transformation, zero-match expectation | `fixtures.py::WRONG_TARGET_SOURCE_POSITIVE_IDS`, `wrong_target_residue`, `wrong_target_from_positive` |
| `malformed_fixtures` (V01-V12), `gate_order` | Literal mutation table, base rule, ordered gate stages, per-stage case ownership | `fixtures.py::MALFORMED_CASES`, `MALFORMED_BASE_RULE`, `GATE_ORDER`, `GATE_STAGE_TO_CASE`, `run_input_gate` (documented, deliberately raises `NotImplementedError` — see below) |
| `zero_boundary` | Identity-branch case description and count | `fixtures.py::ZERO_BOUNDARY_CASES_PER_PRIME`, `ZERO_BOUNDARY_DESCRIPTION` |
| `ordering_and_counts` | Prime/family order, three order variants, traversal rule, exact declared counts/formulas | `fixtures.py::PRIME_ORDER`, `FAMILY_ORDER`, `ORDER_VARIANTS`, `apply_order_variant`, `TRAVERSAL_ORDER`, `CASE_COUNT_FORMULAS`, `CASE_COUNTS`, `CASES_BY_PRIME`, `SCALAR_CONSTRAINT_CASES`, `REFERENCE_EXPONENT_VISITS`, `PREDICTED_CANDIDATE_EQUALITY_EVALUATIONS` |
| `controls.deliberately_faulty_product_rule` | `M_bad=product(m_i)` mutant, expected 5100-cell detection panels | `fixtures.py::PRODUCT_RULE_MUTANT_EXPECTED_PANELS`, `PRODUCT_RULE_MUTANT_EXPECTED_TOTAL`; `reference.py::faulty_product_modulus`, `check_product_rule_mutant` |
| `controls.order_invariance` | Cross-variant reference-set agreement check | `reference.py::order_invariance_check` |
| `cost_and_frontier.exact_proxy` | `isqrtceil`, `W`/`S` integer proxies | `cost_model.py::isqrtceil`, `ResidualProxy`, `residual_proxy` |
| `cost_and_frontier.symbolic_total` | Named, unevaluated symbolic cost terms | `cost_model.py::SymbolicCostTerms`, `SYMBOLIC_COST_TERMS` |
| `cost_and_frontier.comparator_rows` (F0-F8), `dominated_by`, `sota_delta` | Literal comparator-row table and honesty fields | `cost_model.py::COMPARATOR_ROWS`, `DOMINATED_BY`, `SOTA_DELTA`, `divisors_of`, `single_divisor_proxy` |
| `cost_and_frontier.comparison_rule` / `decision_outcomes.modeled_benefit` | Descriptive-only lower/equal/higher labeling | `cost_model.py::modeled_benefit_label` |
| `metrics.secondary` operation counters | Explicit gcd/inverse/residue-test/modular-power/candidate-equality counters | `cost_model.py::OperationCounters` |
| `prospective_group_interface` | **Not implemented.** Documented only (see below). | n/a |
| `execution_gate`, budget (`maximum_runs`, `maximum_workers`, `memory_gb`) | Guard context, one-worker/4-GiB enforcement, refusal-only entry point, planned-artifact description | `driver.py::GuardContext`, `preflight_guard`, `run_calibration`, `describe_planned_artifacts`, `REQUIRED_ARTIFACTS`, `EXACT_ARTIFACT_COUNT` |

## Production vs. independent reference: why they are separate modules

`crt.py` is the *production combiner*. Its two public entry points
(`fold_congruences`, `enumerate_candidates`) take only an integer domain
size `n` and an ordered list of `(a, m)` congruences. They never see
fixture truth (`k`, `x`), a prime `r`, a primitive element `zeta`, or any
reference/oracle output. This is enforced structurally: no function in
`crt.py` accepts those values as a parameter, and `crt.py` imports nothing
from `reference.py` or `fixtures.py`.

`reference.py` is a deliberately independent re-implementation of the same
mathematical fact ("which exponents in `[0, n)` satisfy every supplied
congruence"), written as a brute-force scan over the full domain
(`full_domain_matches`) rather than by running the CRT fold. It does not
import `crt.py`, does not call any of its helper functions, and does not
read any value `crt.py` predicted (a candidate set, `M`, or `k0`) as an
input to its own scan — it only receives the same raw `(n, congruences)`
that would be given to `crt.py`, plus (uniquely, and only here and in the
fixture generator/boundary gate) the fixture's `zeta`, `r`, and truth `x`,
which it needs to run the independent scalar-equality surrogate check
(`verify_original_target`). A bug shared between the fold logic and the
brute-force scan is very unlikely to be identical, because the two are
written from the specification's prose independently rather than by
factoring out common code.

`fixtures.py` owns: literal panel tables, deterministic panel/case
generation rules, token-label mutation definitions, and — critically — the
only two places (besides the reference/verification service) fixture
truth `k`/`x` is allowed to reach: the generator itself, and the
input-gate boundary. `fixtures.py` never calls `crt.fold_congruences` with
`k`/`x` attached; the congruence tuples it would hand to the combiner
carry only `(a, m)`.

`cost_model.py` is pure integer bookkeeping (isqrt-based proxies,
comparator-row text, explicit "not measured" accounting). It has no
dependency on `crt.py`, `reference.py`, or `fixtures.py`, and performs no
group, acquisition, or floating-point computation anywhere.

`driver.py` is the only module that would eventually import all four of
the above together. It does not do so usefully yet: its `run_calibration`
function always raises `ScientificExecutionRefused` under any
`GuardContext` this implementation task can honestly construct, because
the required approval-hash / independent-review / launch-lock fields
cannot exist until later, separate tasks (Coordinator archive,
review-adversarial implementation review, and a genuine scientific launch
lock) produce them.

## The `prospective_group_interface` boundary (explicitly not implemented)

Per the specification's `prospective_group_interface` section and this
task's hard constraint "Do NOT implement or execute the 'prospective group
interface' ... in this task", no code in this directory represents an
actual elliptic-curve group, group point, group operation, or Cheon first
stage. The specification's own group-interface description is preserved
here only as a documentation pointer, not as code:

- **Input**: an exact-order group `(G, P, r)`, original `Q=[x]P`, certified
  `n` factorization and primitive `zeta`, and explicitly supplied
  `Q_i=[x^{d_i}]P` with recorded source/acquisition/storage. Encoding and
  subgroup-membership validation, and correctness of supply as distinct
  from mere membership, would need to be established by that later
  protocol — none of it is implemented here.
- **First stage**: recovering `a_i` from `g_i = zeta^{d_i}` of order `m_i`
  via a sourced implicit-group first stage, with a residue certificate
  `[pow(zeta, d_i*a_i, r)]P = Q_i`, `0 <= a_i < m_i`. Not implemented here;
  this calibration's `a_i` values are synthetic scalar residues computed
  directly from `k` (see `fixtures.fixture_residue`), never derived from
  any group first stage.
- **CRT**: would reuse exactly `crt.fold_congruences`/`enumerate_candidates`
  unchanged — this is the one part of the group interface this
  calibration's production code is already suitable for, by construction,
  since the combiner's interface is already restricted to `(n, congruences)`.
- **Residual search**: baby-step/giant-step table search over group
  elements (`A_j=[zeta^{k0+M*j}]P`, `B_i=[zeta^{-M*b*i}]Q`), with charged
  modular exponentiation, scalar multiplication, table hashing/collision
  checks, storage, and final verification `[candidate]P=Q`. **Not
  implemented; no such table or scalar multiplication exists in this
  directory.**
- **Cost boundary**: a future group implementation would need to charge
  every one of the above group operations, an explicit memory/streaming
  schedule for the baby/giant tables, a defined success/attempt model
  (including inverse-success probability across attempts), and a resolved
  source rule for any reused `d=1`/`d=n` token before any net-benefit
  claim could even be attempted. None of that accounting exists in
  `cost_model.py` beyond the explicit `None`/`not_executed`
  `AcquisitionAccounting` fields and the symbolic (unevaluated)
  `SymbolicCostTerms`.
- **Remaining requirements** (verbatim from the specification): exact
  curve/group fixtures, authenticated or planted supply generation,
  source-defined stage implementation and independent review, baseline
  operation accounting, memory/data schedule, success definition, and a
  new genuine launch lock. All of these are open and unaddressed by this
  implementation.

## Failure classification (per `agents/executor.md`)

This implementation task produced no runs, so no run was actually
classified. The classes below describe how a *future* scientific
invocation's outcomes would be classified, for reviewer orientation:

- `specification_error`: a required spec field the driver's guard needs
  (spec hash, review receipt, launch lock) is absent or malformed —
  surfaces as `ScientificExecutionRefused` from `preflight_guard`.
- `implementation_error`: `crt.py`'s fold disagrees with `reference.py`'s
  brute-force scan on a scalar-constraint cell (`SetComparison.equal ==
  False`), or a malformed case is accepted rather than rejected at the
  declared `GATE_ORDER` stage.
- `infrastructure_error`: process/host/dependency failure during a future
  authorized run (e.g. an artifact write failure), unrelated to the
  arithmetic itself.
- `resource_exhaustion`: a future run exceeds the enforced 4 GiB / 1-worker
  ceiling; `driver.preflight_guard` rejects any `requested_worker_count >
  1` or `requested_memory_bytes` above `MAX_MEMORY_BYTES_ALLOWED` before
  any other check.
- `invalid_measurement`: a certificate-bearing result (none is claimed by
  this arithmetic-only calibration; `certificate.kind: none` per the
  specification) fails independent re-verification.
- `negative_observation`: a complete, provenance-valid future run produces
  a genuine independent-reference mismatch, missed inconsistency, or
  wrong-target recovery — this is the only class that would constitute
  empirical evidence against the calibration's frozen prediction, per
  the specification's `falsification_criterion`.

## Future CLI shape (documented, not run)

No CLI has been executed. The intended future invocation shape, once a
scientific handoff supplies a genuine `GuardContext`, is illustrated (and
only illustrated) by `driver.py`'s `if __name__ == "__main__":` block,
which today only demonstrates the refusal path with an intentionally empty
context:

```sh
python3 experiments/EXP-AUXIN-684adf/implementation/driver.py
# -> prints "REFUSED (expected under this implementation-only handoff): ..."
```

A later authorized run would instead construct a `GuardContext` populated
with real hash bindings, a real independent-review receipt id/verdict, and
a real, genuine launch lock bound to an allocated `RUN_ID`/`TASK_ID`, then
call `run_calibration(ctx, run_directory=...)`. That later task's own
(superseding, not this file's) version of `run_calibration` would drive
`fixtures.py` generation, `crt.py` folding, `reference.py` verification,
and `cost_model.py` accounting for all 26,546 declared cases and write
exactly the 18 artifacts named in `driver.REQUIRED_ARTIFACTS` to
`experiments/EXP-AUXIN-684adf/runs/<RUN_ID>/`. No such invocation has
occurred, and this file does not claim otherwise.

## Platform RSS / memory-protection notes

No process has been launched by this task, so no RSS has actually been
measured. For the future authorized run, the specification's `cost_and_frontier.memory`
field requires reporting "measured arithmetic peak memory"; the following
constraints apply and must be honored by that later run, not retrofitted
here:

- Peak resident set size (RSS) units are platform-dependent: Linux's
  `resource.getrusage(RUSAGE_SELF).ru_maxrss` reports **kibibytes**, while
  macOS/BSD report **bytes** for the same field. Any future measurement
  must record the platform (`sys.platform` or `platform.system()`) and the
  raw unit alongside the converted byte value, never silently assume Linux
  kibibyte semantics.
- The `maximum_memory_gb: 4` / `memory_limit_bytes: 4294967296` budget is
  machine protection, not a scientific parameter (per
  `docs/agent-runtime-core.md`, "machine-protection limits ... remain
  binding and are not scientific conclusions"). A future run should enforce
  it with a portable resource limit where the platform supports one (e.g.
  POSIX `resource.setrlimit(RLIMIT_AS, ...)` on Linux) and must **fail
  closed with a precise reason** — not silently proceed unprotected — on
  any platform/sandbox where no such enforcement mechanism can be
  established (e.g. a restricted container without `RLIMIT_AS` support, or
  a platform lacking the `resource` module such as native Windows). This
  implementation task performs no such measurement or enforcement itself
  (`maximum_runs: 0`); `driver.preflight_guard`'s worker/memory checks only
  validate the *requested* values against the declared ceiling before any
  execution would be considered, they do not themselves impose an OS-level
  limit — that enforcement mechanism, and its fail-closed behavior, is left
  as an explicit obligation for the later scientific handoff's own
  (superseding) driver code, and must be documented in that later run's
  `environment.json`/`manifest.yaml`.

## What has and has not been done

- **Done**: five Python source files plus this README, syntax-checked
  (`python3 -m py_compile`) and import-checked (`python3 -c "import
  crt, reference, fixtures, cost_model, driver"`) with zero exceptions and
  zero scientific function calls.
- **Not done, by design**: no fixture was generated, no primitive element
  was searched for, no CRT cell was folded, no independent reference scan
  ran, no cost proxy was evaluated, no artifact was written to any
  `experiments/EXP-AUXIN-684adf/runs/` directory (no such directory
  exists), and no independent implementation review or launch lock exists
  yet. See `implementation-report.yaml` for the exact static-check list
  and `implementation-manifest.yaml` for the exact hash bindings and
  explicitly absent (pending) fields.
