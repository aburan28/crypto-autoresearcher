# EXP-CERTBIN-e94b27 implementation (RC-1)

Written from `experiments/EXP-CERTBIN-e94b27/specification.yaml` (version 1)
under TASK-20260924-41c7be. Pure Python 3.11 + numpy (bit-packed GF(2)); no
compiled helper, no Sage. One worker; OMP/OPENBLAS threads 1; RLIMIT_AS 3 GiB.

## Modules

| file | responsibility |
|---|---|
| `gf2n.py` | COPIED unchanged from EXP-CERTBIN-4e92d7/impl (see `impl-provenance.json`): F_2[t]/(t^17 + t^3 + 1), schoolbook and table multiplication, trace, half-trace, irreducibility test. |
| `curve.py` | COPIED unchanged: binary-curve group law, x-lift, schoolbook S_3 evaluation (self-test only). |
| `macaulay.py` | COPIED unchanged: Weil descent of S_3 to the 17 x 172 matrix E(r), affine basis, monomial orders, and the fixed-shape Macaulay matrix `MacaulayShape(D)` (used for C-BASE at D = 3, 4 and as a cross-check of the generic builder at D = 4, 5). Already parameterised by D; no edit was needed for D = 5. |
| `elim.py` | COPIED unchanged: the Stage-1 column pass, used for C-BASE (rank_3, rank_4, "1 in R_D"). |
| `closure.py` | NEW. Generic (nv, D, neq) Macaulay builder, the column-pass echelon with int32 operation logs, M_D and the mutant closure W_D (least fixpoint by iteration, semi-naive in the products but with iterates identical to the literal rule; proof in the module docstring), membership test, and certificate extraction by back-tracing the operation logs to pairs (mu, k) with sum mu*f_k = 1. Per-instance watchdog by SIGALRM. |
| `oracles_rc1.py` | NEW. Oracle B (exhaustive truth tables of all equations via the Moebius transform over 2^18 assignments) and oracle A (512 quadratic root findings over V). |
| `instances.py` | NEW. Archived-record loading and the deterministic set rules (U62, S62, C20, N-AFF62, N-F262); a wrong set size is a ContractDefect STOP. Builds E for each instance and runs the C-NULLS structural identities. |
| `stats_exact.py` | NEW. Clopper-Pearson 95% bounds by exact-rational bisection (math.comb + Fraction), and the DR-4 separation test. |
| `common.py` | NEW. Paths, constants, C-SRC (input hashes vs the TASK-20260923-c2e57b receipt; specification vs the TASK-20260924-d3a90c receipt), JSON helpers. |
| `selftest.py` | Phase 0: C-SRC first (writes inputs.json), then C-SELF (seed 2026092430099) and C-FIX; writes selftest.json. |
| `make_trial_plan.py` | Writes trial-plan-v1.json from the specification (no computed value, no instance index). |
| `driver.py` | Phases 1-4 (checkpoint per closure per set), assembly of closures.jsonl.gz and certificates.jsonl.gz, phase 5 (`--phase determinism`, separate process), the C-VERIFIER negative controls (verifier re-invoked as a subprocess) and phase 7 (`--resume` after phase 6). `--dev-limit N` is for development only and is refused for any output inside the repository. |
| `analysis.py` | Phase 7: instrument checks, MR1-MR5, secondary metrics, RC1-DR-1..7, the independent raw-result recount and its agreement check, manifest.yaml, environment.json, run-report.md. |

## Commands (repository root)

```sh
python3 experiments/EXP-CERTBIN-e94b27/impl/make_trial_plan.py --spec experiments/EXP-CERTBIN-e94b27/specification.yaml --run-id RUN-CERTBIN-c417e0 --out experiments/EXP-CERTBIN-e94b27/trial-plan-v1.json
python3 experiments/EXP-CERTBIN-e94b27/impl/selftest.py --out experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/selftest.json && python3 experiments/EXP-CERTBIN-e94b27/impl/driver.py --spec experiments/EXP-CERTBIN-e94b27/specification.yaml --plan experiments/EXP-CERTBIN-e94b27/trial-plan-v1.json --source-run experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05 --run-id RUN-CERTBIN-c417e0 --out experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0
python3 experiments/EXP-CERTBIN-e94b27/impl/driver.py ... --phase determinism          # phase 5, separate process
python3 experiments/EXP-CERTBIN-e94b27/verifier/verify_cert.py --certs .../certificates.jsonl.gz --source-run experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05 --out .../certificate-verification.json   # phase 6
python3 experiments/EXP-CERTBIN-e94b27/impl/driver.py ... --resume                      # negative controls + phase 7
```

## W_D, exactly

W^(0) = rowspace(M_D); W^(i+1) = W^(i) + span{v_j * b}; stop at the first i
with dim W^(i+1) = dim W^(i); W_D = W^(i). Each iteration eliminates the stack
[echelon rows of W^(i); products v_j * b] with the column pass (echelon rows
first, so they are their own pivots and are never modified). The rows whose
leading monomial has degree <= D - 1 span W^(i) cap B_{<=D-1} (columns are in
descending degrevlex, so a row with a low-degree lead has no higher-degree
entry). Only products of the rows whose low-degree lead is new at iteration i
are added; the products of the older ones already lie in W^(i), so the
iterates are the literal rule's. The self-test compares dims per iteration,
fixpoint index and first iteration containing 1 against a plain-Python literal
implementation on random 6-variable systems.

## Certificates

A forward step XORs pivot row p into the rows X. Walking a log backwards, a
target set S of final rows becomes S xor {p} whenever |S cap X| is odd; this
yields the original rows whose XOR is the final row "1". Rows of a later
iteration are (echelon row of the previous iteration) or (v_j times such a
row), so the trace continues into the previous log with the multiplier pushed
into mu (multilinear reduction is a ring map). The result is the flat set C of
pairs (mu, k). The engine evaluates sum mu*f_k itself as a self-check, but a
refutation counts only after `verifier/verify_cert.py` (separate process, no
shared import) accepts it.
