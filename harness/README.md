# harness — executable spine

Minimal, correct ECDLP experiment substrate. The included implementations are
deterministic and independently verifiable; each run records the parameters
and evidence scope needed to interpret results at the scale actually tested.

| module | role |
|---|---|
| `toycurve.py` | F_p short-Weierstrass arithmetic, exact point counting, deterministic ECDLP instance generation. Also the **independent verifier** for certificates. |
| `rho.py` | Pollard rho (Teske r-adding walk) — the matched generic baseline (KN-TECH-001). Recovers k using public data only. |
| `sixclass_native.py` | Launches crypto's native six-class GLV worker, pins its binary and job hashes, and independently checks the first distinguished point and any recovered logarithm. The Python file contains no walk implementation. `fixtures/sixclass_p25.json` is a planted small-curve interoperability case. |
| `sixclass_challenge.py` | Original local conformance generator. The preferred challenge custody and answer check now run in native Rust through `sixclass_isolated.py`. |
| `sixclass_isolated.py` | Launches native Rust custody, worker, and answer-check binaries in separate pinned, networkless, read-only containers; the worker receives no private audit mount. Docker's host daemon and the orchestrator remain trusted. |
| `sixclass_paired.py` | Audits native baseline / candidate / baseline trial rows, A/A work equality, recovered logs, binary and job hashes, and unpriced full-work categories. |
| `sixclass_assumptions.py` | Emits a five-clause H1 coverage ledger from the pinned falsifiable matrix. Current diagnostic receipts leave all clauses open and block a production claim. |
| `sixclass_followup.py` | Freezes the job, native binary and bounded inputs, runs one initial observation, records one reviewer-selected follow-up before execution, then seals the receipt chain. |
| `walk.py` | The rho walk as a first-class object: Teske r-adding steps with coefficient bookkeeping, orbit tracing (tail/cycle), distinguished-point walks, and the van Oorschot--Wiener DP collision search. |
| `kangaroo.py` | Pollard kangaroo over an interval: tame/wild herds meeting at distinguished points, trajectories retained. |
| `walkviz.py` | Draws what those two produce -- functional graph with one rho highlighted, DP forest with the golden collision, kangaroo herds -- as dependency-free SVG. |
| `run_walkviz.py` | `python -m harness.run_walkviz --seed 7 --field-bits 16 --out-dir out/`: walk records (JSON) plus figures (SVG) for one instance. |
| `semaev.py` | Semaev summation polynomials S_2/S_3/S_4 and the S_3 point-decomposition Groebner measurement (KN-TECH-002/003/004). |
| `runner.py` | Run wrapper: captures commit/env/timing/resources, re-verifies every certificate independently, and writes the immutable run record. Refuses to overwrite a run id. |
| `run.py` | Experiment entry point (EXP-SEMAEV-001). `python -m harness.run --experiment EXP-SEMAEV-001`. |
| `bench_rho_throughput.py` | Rho **step throughput** on this machine, CPU and CUDA from one walk definition: three implementations cross-checked limb-for-limb before any rate is reported. Kernel and dual-target field arithmetic in `gpu/` (see `gpu/README.md`). |
| `endosweep/` | Endomorphism-ring **sweeper for scalar-multiplication decompositions** (constructive side, not an attack): certifies the CM discriminant class of a curve without factoring, enumerates units, small-degree endomorphisms, isogeny-cycle pumps and Frobenius-type generators, LLL-reduces every relation lattice exactly, costs each configuration under one operation-count table and labels what it reproduces from the literature; `endosweep/explicit.py` then builds the winning endomorphism on the real curve (division polynomials, Frobenius-eigenvalue kernels, Kohel-form Vélu, closed walk through the isogeny class) and verifies it on points. `endosweep/corpus.py` runs the whole pipeline over the 248-curve std-curves database; `endosweep/fourq.py` verifies FourQ with its real endomorphisms; `endosweep/genus2.py` adds the rank-4 genus-2 route with counted Cantor arithmetic; `endosweep/chainsweep.py` builds every chain realisation (every element, every step order) of a curve's cheap endomorphisms, prices each against the native evaluators' exact operation counts, and exports the frozen chain set for the crypto repository's native sweep. `python -m harness.endosweep`; `python -m harness.endosweep.explicit --target "GOST CryptoPro-B"`; see `endosweep/README.md`. |

Run tests with `python -m pytest -q`. Metrics honesty: the Groebner
`*_max_degree_proxy` is the reduced-basis max degree, an implementation-bound
proxy, **not** the theoretical degree of regularity (see KN-TECH-004). Trends
and absolute timings are interpreted only with their tested parameters, cost
model, and any stated transfer assumptions.

The native six-class p25 interoperability run is recorded in
[`harness/evidence/sixclass-p25-20261024.json`](evidence/sixclass-p25-20261024.json).
After building `crypto`'s `six_class_rho` binary, reproduce a new receipt with:

```sh
python -m harness.sixclass_native \
  --job harness/fixtures/sixclass_p25.json \
  --worker /path/to/crypto/target/debug/six_class_rho \
  --walkers 1000 --out /tmp/sixclass-p25-receipt.json
```

The recorded run solved planted log `0x3039` in 430 walkers. The receipt pins
the tested binary and verifies its proposed log independently. It is a toy
correctness check, not a secp256k1 throughput measurement.

## Curve Smash secp256k1 challenge

[`fixtures/curvesmash_secp256k1_profile.json`](fixtures/curvesmash_secp256k1_profile.json)
is byte-for-byte the `secp256k1-ecdlp` target profile from
[`Layr-Labs/curvesma.sh@1f084c1`](https://github.com/Layr-Labs/curvesma.sh/blob/1f084c1914c81a0cdc830b176453adba5dc19ab9/tracks/secp256k1-ecdlp/target-profile.json),
SHA-256 `18c3338de676f1909715814325bffdb1513f1621d678b942e8a7a9563b8fd086`.
The profile specifies uniform rejection sampling of a private scalar and
exposes only `Q=[x]P`. The generator uses that sampling rule and keeps the
scalar in a mode-0600 audit file outside this repository. A zero draw causes
an explicit stop because the current native worker cannot encode infinity.

The public job
[`fixtures/curvesmash_secp256k1_challenge.json`](fixtures/curvesmash_secp256k1_challenge.json)
was generated from this profile with public walk seed 7, 32 branches,
`dp_bits=5`, and a 512-step cap. Its SHA-256 is
`b9a9194796a2386d5d6fe67de44c01707b2b656a067e716253b6a16fccadcacd`.
The private scalar is absent from the repository. Create another instance with:

The original Python generator remains a local conformance path. For isolated
custody, build `crypto`'s `six_class_challenge`, `six_class_rho`, and
`six_class_compare` binaries, create two empty disjoint directories, and run:

```sh
mkdir -m 700 /tmp/sixclass-public /tmp/sixclass-private
python -m harness.sixclass_isolated generate \
  --template harness/fixtures/curvesmash_secp256k1_challenge.json \
  --binary /path/to/crypto/target/debug/six_class_challenge \
  --public-dir /tmp/sixclass-public --private-dir /tmp/sixclass-private
python -m harness.sixclass_isolated run \
  --job /tmp/sixclass-public/job.json \
  --binary /path/to/crypto/target/debug/six_class_rho \
  --walkers 1 --out /tmp/sixclass-public/worker-receipt.json
```

Use `--sudo` before the subcommand only on hosts where the Docker socket
requires it. The custody container sees the private audit directory; the
separate worker container mounts only the public job and native binary. A
third native container verifies a proposed `{"x":"<64 lowercase hex>"}`
answer with `sixclass_isolated verify`; it does not mount the audit directory.
The checked [isolated public job and receipts](evidence/sixclass-isolated-secp256k1-20261024/)
are a full-curve arithmetic and boundary smoke test. The answer and audit
files are deliberately absent from the repository. A host Docker administrator
can still access the private directory, so this is process isolation on one
host, not independent remote custody or attestation.

### H1, paired work, and one follow-up

The [five-clause H1 matrix](fixtures/sixclass_h1_matrix.json) lists each
prediction, falsifier, control, and required observable. Generate a coverage
ledger with `python -m harness.sixclass_assumptions --receipt RECEIPT --out
REPORT`. The [current ledger](evidence/sixclass-h1-coverage-20261024.json)
keeps every clause open. Algebraic correctness and one-worker DPs cannot
establish a collision-arrival CDF, bit independence, or a production cost.

Run `python -m harness.sixclass_paired --job JOB --binary COMPARE_BINARY
--walkers 100 --trials 2 --out RECEIPT` for native A/B/A rows. The
[p25 paired receipt](evidence/sixclass-paired-p25-20261024.json) preserves
both raw trials and the unpriced field arithmetic, memory, network, and
coordinator categories. Its deterministic repeats check timing drift and
work-count consistency; they are not independent success trials. The current
BigUint six-class path was slower on this toy job and is not a production
throughput result.

For a bounded follow-up, write a JSON input with exactly `walkers`,
`num_branches`, `dp_bits`, `max_steps_per_walker`, and `seed`, then call
`python -m harness.sixclass_followup freeze`, `initial`, `followup`, and
`finalize` with `--attempt`, `--binary`, and `--job`. The `followup` command
also requires `--input`, `--reviewer`, and `--reason`. It refuses a second
follow-up, a changed binary or job, and a changed runner. The
[p25 protocol example](evidence/sixclass-followup-p25-20261024/) recovered
the planted toy log in its single follow-up; its `local-smoke` reviewer label
is an internal test, not independent review or secp256k1 evidence.

The earlier conformance command is:

```sh
python -m harness.sixclass_challenge \
  --job /tmp/secp256k1-job.json \
  --audit "$HOME/.local/share/crypto-autoresearcher/challenges/new.audit.json" \
  --seed 7 --dp-bits 5 --max-steps 512
python -m harness.sixclass_native \
  --job /tmp/secp256k1-job.json \
  --worker /path/to/crypto/target/debug/six_class_rho \
  --walkers 1 --timeout 120 --out /tmp/secp256k1-receipt.json
```

The committed [one-walker receipt](evidence/sixclass-secp256k1-20261024.json)
records one independently verified distinguished point after 11 class visits
and no recovered log. It pins the native binary SHA-256
`877829b847dedd3e41cfe6ecc8021ba507eba41e21c50362f055d37643786269`.
This is a native end-to-end admission and arithmetic check on the full curve;
the one-walker result makes no success-probability or 126.96-bit cost claim.
The BigUint worker is not a production-throughput implementation. The public
job and receipt are harness data, not a Curve Smash submission or verifier score.

## Exemplar-aligned experiment classes (optional manifest metadata)

Two experiment classes in the spirit of the canonical exemplar
(`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`; see also
`docs/target-result-profile.md`) need manifest metadata beyond `metrics`:

- **Heuristic validation** — samples a quantity whose distribution a numbered,
  formally stated heuristic predicts, and compares the empirical distribution
  against the pre-registered prediction (exemplar §4.2: the empirical CDF of
  the largest prime factor of the smallest isogeny degree vs. the
  Dickman–de Bruijn prediction ρ(u), at cryptographically sized p, with
  explicit sample sizes and a tail check on the smoothest sample).
- **Cost measurement** — measures concrete cost under an explicit cost model
  (exemplar §4.1: F_{p^2}-operation and memory bounds at standardized
  parameter sets, with optimistic assumptions flagged). The operation unit and
  assumptions are recorded so costs from different models are never compared
  without conversion (baseline discipline, docs/evidence-and-reproducibility).

`RunResult` accepts two optional dicts, recorded verbatim in the manifest when
provided and omitted entirely otherwise — existing runs and manifests are
unaffected. Like `parameters` and `metrics`, these blocks are recorded, not
interpreted: the runner enforces no schema beyond "dict or absent".

```yaml
run:
  ...
  heuristic_validation:            # optional; key absent => not this class
    heuristic_id: null             # e.g. "H1"
    statement_ref: null            # where the heuristic is formally stated
    prediction: null               # pre-registered before the run
    theoretical_distribution: null # e.g. "dickman_de_bruijn rho(u)"
    sample_size: null
    scale_relevance: null          # tested parameters and transfer assumptions
  cost_model:                      # optional; key absent => not this class
    operation_unit: null           # e.g. "group_operation", "Fp2_operation"
    assumptions: []                # optimistic assumptions flagged explicitly
    notes: null
```

Results recorded under these fields may be used for direct or conditional
claims when the tested parameters, evidence scope, and transfer assumptions
are stated explicitly (AGENTS.md rule 7).

## Compute efficiency (optional, opt-in)

`harness/efficiency.py` adds a wrapper-measured `result.metrics.efficiency`
block to a run record. It measures how the run used the machine; it is a cost
observation scoped to this machine and run, never mathematical evidence.

```python
from harness.efficiency import run_wrapped_measured

run_wrapped_measured(
    "EXP-...", "AREA", run_fn, status="completed_valid", command=cmd,
    efficiency={                                   # optional: roofline score
        "machine": "rtx-pro-6000-blackwell-server",   # third_party/gpueff/profiles
        "workload": "ecc2k130-packed-walk",
        "work_units_metric": "iterations",         # key in the run's own metrics
        "dcgm_url": "http://host:9400/metrics",    # optional, scraped at start and end
        # "prometheus_url": "http://prom:9090",    # optional, range-queried over the run
    })
```

- `cpu` (always): process-tree CPU seconds (own plus waited-for children)
  over the wrapper's wall seconds, as `parallelism` in cores and
  `utilization` of the cores this process may use.
- `roofline` (with a spec): the gpueff score from `third_party/gpueff`, which
  is vendored from `aburan28/cryptanalysis` at the commit in its
  `UPSTREAM.json`. It records the achieved/attainable throughput, the
  `clock x sm_active x in_kernel` loss decomposition, the components, the
  findings, and the sha256 of both profiles. Throughput is work units over
  the wrapper's wall clock, never caller-reported.
- Missing inputs are listed under `missing` with the reason. A scoring
  failure is recorded as `status: error` in the block and the run is still
  written. An experiment metric already named `efficiency` is refused, not
  overwritten.

It is a separate entry point on purpose. `harness/runner.py` and
`schemas/run-manifest.schema.json` are hash-pinned by locked execution plans,
so they are unchanged, and runs that do not call this function record exactly
what they recorded before. Using it in a frozen protocol is an additive
amendment to that protocol, as for any change of entry point.
