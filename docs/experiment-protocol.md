# Experiment protocol, export and review: one shape for every runner

Owner request, 2026-10-22: every experiment in the owner's repositories
(crypto, crypto-autoresearcher, cryptanalysis, ml-cryptanalysis,
cryptanalysis-rl) is designed without bias, carries its controls, isolates its
confounders, follows a frozen protocol and schema, exports its data in one
form with precise measurements, and can be reviewed by another runner that
files judgments and observations of its own. This document is the normative
statement. The skills that apply it are `experiment-protocol` (design and
freeze), `run` and the backend skills (execute and export), and `review-run`
(the cross-runner review). The schemas are
`schemas/experiment-protocol.v1.json`, `schemas/experiment-export.v1.json` and
`schemas/experiment-review.v1.json`; `tools/experiment_protocol.py` checks all
three. The worked example is `examples/experiment-protocol/ecbench-l2-smoke-subset/`.

It adds a shape to rules this program already has; it lowers none of them.
`AGENTS.md` core rules 1-10, "Durable research commits" and the
`design-experiment` contract (`docs/confound-control.md`) still bind a
ledgered `EXP-*`; a `research/<study>/PROTOCOL.md` in crypto still binds a
preregistration there. The protocol record is where those obligations are
written once, in a form a tool can check and another runner can read.

## 1. What the protocol must fix before the first data point

| block | fixes | the bias it removes |
| --- | --- | --- |
| `claims` | each sentence to be published, in one class (theorem, exact computation, comparative, heuristic estimate, out of scope), and for a comparative claim the comparison that decides it | a comparative claim made from one number with no reference |
| `arms` and `controls` | reference, baseline and candidate arms; an **A/A** control (two arms differing only in a nuisance factor), a **positive** control (an input where the effect is known to be present, through the same code path) and a **negative** control (a sample from the stated null population), or a reason each is not applicable | a difference inside the noise; a "nothing found" from a blind detector; a target compared with nothing |
| `variable_ledger` | every factor that could move a primary metric, with its treatment (`fixed`, `randomized`, `crossed`, `measured`), and every comparison with its `design` (`one_factor`, `factorial`, `absolute`, `aa`, `confounded`) | a comparison that differs in two things and credits one |
| `randomization` | arm order (interleaved or randomized; `fixed` needs a reason), seed derivation (from the protocol hash, an explicit list, an external nonce, or the harness's own frozen rule), instance sampling independent of arm, and whether arm labels are masked during analysis | one-time costs landing on the arm that ran first; seeds chosen after a look; an analyst steering toward the labelled candidate |
| `sample_size` | instances, replicates, warmups, the power check (`2/(N+1) < alpha/m` for a rank test, with the correction named) and the pre-flight runtime estimate (fixed and per-sample cost) | a null that could never reject; a protocol that cannot be finished |
| `metrics` | each metric's unit, kind (`counted`, `timed`, `derived`, `exact`, `rate`), definition (from which event to which), source field, aggregation, resolution and uncertainty method | a stage count read as a method cost; a clock quoted where a count was available |
| `measurement` | the isolation level a clock needs (ecbench L0-L3 or isolab tiers A-D), warmups, order, and the host and run facts every row must record | wall time from a noisy host; a result without its host |
| `execution` | backend, queue, placement, timeout, the checkpoint policy (`none`, `application`, `criu`) with interval, grace and restore validation, and infrastructure-only retries | a resumed row's clock counted as a measurement; a non-zero exit retried until it passes |
| `stopping_rules`, `decision_rule`, `analysis_plan` | fixed-N or preregistered sequential stopping; the statistic, interval, correction and effect-size measure; the analysis script by hash, frozen before the data | optional stopping; the threshold moved after the result; the analysis tuned to the data |
| `inadmissible` | what does not count (changing N, seeds, unit or accounting after seeing results; a stage ratio as a speedup; favourable seeds) | the moves that turn a null into a win |
| `freeze` and `amendments` | the canonical hash and commit of the frozen record; every later change as a dated amendment that says whether it preceded the data it affects | silent edits; a prediction re-dated after the fact |

`python3 tools/experiment_protocol.py validate protocol.json` checks the
schema and the cross-references (a comparative claim decided by a decisive
comparison, an A/A arm or a reason, a positive control or a reason, a timed
primary metric only with its justification and at least L2, the power
arithmetic, a frozen analysis before a frozen protocol). `freeze` writes the
hash; a frozen protocol that no longer hashes to its `freeze.protocol_sha256`
fails validation, which is the point.

## 2. Confounders this program isolates, and how

The variable ledger lists them per experiment. The usual list, with the
treatment each backend gives it:

- **Instrument**: commit, build flags, binary SHA-256, compiler version,
  allocator, thread count. `fixed` across arms unless the instrument is the
  independent variable; the same-instrument rule (`same_instrument_as`) makes
  the validator compare commit, binary and threads.
- **Host**: CPU model and features, frequency and turbo, SMT, NUMA node,
  kernel, hypervisor, co-tenants, IRQs, memory pressure. `measured` per row by
  ecbench and isolab, which grade each row's isolation level from what they
  observed, never from a node label. A clock is evidence only at the
  protocol's `isolation_required`.
- **Memory layout and environment**: ASLR, environment size, link order,
  page cache, THP. Recorded by isolab; the remedy for layout bias is to repeat
  across layouts (Mytkowicz et al. 2009; Curtsinger and Berger 2013), which
  is what replicates with fresh processes do.
- **Order and warm-up**: one-time costs (thread pools, lazy statics, cold
  caches) land on whichever arm runs first. Interleave arms within every
  round and discard warmups.
- **Inputs and seeds**: instance sampling independent of arm, seeds derived
  from the frozen protocol or a post-freeze nonce, never chosen after a look.
- **Spot capacity**: a preempted and restored row has a valid count and an
  invalid clock. The export marks `resumed` and `wall_valid: false`; the
  protocol's `execution.checkpoint.after_restore` says so in advance.
- **Analyst**: arm labels masked (`blind`) until the analysis script is
  frozen and run; the key file stays closed, and its hash is in the export.

## 3. Precise measurement

- **Counts are the primary metric** wherever the instrument emits them
  (group operations, field multiplications, relations, instructions); they
  survive hardware and contention. A clock is a secondary metric unless the
  protocol says why a count will not do, and then only at L2/tier B or better,
  read against the A/A interval of the same session.
- **Every row carries its own host facts**: the `measurement.record` list
  (CPU model, kernel, governor, threads, binary SHA-256, isolation level and
  its blockers, steal, PSI, run CPU). A number without its host is not a
  measurement.
- **Precision is stated**: each metric's `resolution` (one GAE, one
  microsecond, one count) and `uncertainty` method (paired bootstrap,
  Clopper-Pearson, standard deviation, none for an exact value).
- **Uncharged work is listed**: every native counter the instrument emits
  goes into `measurements.counters`, uncharged ones included, so the
  pricing band of crypto's AGENTS.md section 5a can be applied by a reviewer.
- **Failures are rows**: timeouts, crashes, refuted certificates, contended
  and interrupted executions stay in the export with their status and the
  rule that excludes them. A `not_completed` row is never evidence about the
  thing measured.

## 4. Queued execution on spot capacity, and what a restore means

Measurement jobs (a clock or counter is a metric) go to an isolated host:
isolab, the EKS `isolab` namespace (`isolab_k8s_benchmark`, L2 from a static
whole-core CPU manager on a Karpenter Spot pool), or a taskq `cpu-exclusive`
pool with Guaranteed QoS. Throughput jobs (searches, relation collection,
training) go to the cheapest capacity (spotlab, the Spot taskq pool, the
spot-system host) and checkpoint. The design for a queue of
protocol-bound jobs on Kubernetes Spot nodes with checkpoint and restore is
`taskq/deploy/spot-checkpoint/README.md` in aburan28/crypto; the
`queue-experiment` skill there submits one.

Whatever the checkpoint mechanism (an application manifest with a committed
generation and SHA-256 per file, or a CRIU process image), the measurement
semantics are fixed by the protocol and enforced by the export lint:

- counted units survive a restore and stay valid;
- wall and CPU time across a restore are `wall_valid: false`; the row
  records `resumed` and `checkpoint.restored_from_generation`;
- a restore is admitted only after its validation (`manifest_sha256`,
  `application_managed`, `criu_selfcheck`); a failed restore is an
  `infra_error`, never a fresh start under the same `run_id`;
- a retry counts infrastructure failures only; a non-zero exit or a timeout
  is an outcome.

## 5. The export

One `export.json` per experiment (or per backend session when an experiment
spans several), beside the raw records, never inside a directory a harness
seals. It binds the frozen protocol by hash, names the producer (runtime,
model, session, role) and the source commit, carries one row per execution
with its arm, instance, seed, replicate, warmup flag, status and outcome
class, attempts and resumes, counted measurements, clock, rusage, counters,
isolation tier and blockers, verification status, exclusion rule and
artifacts by hash; the CONSORT-style `flow` (planned, attempted, completed,
not completed, interrupted, resumed, excluded by rule); every file by hash;
and the analysis script, its blinding state and outputs. `notes` carry
observations only.

Adapters: `from-ecbench` (an `ecbench.session/v1` directory), `from-taskq` (a
`taskq.task-result/v1` document), `from-rows` (a CSV or JSON lines table with a
column map). Other backends write the shape directly; `check-export
--protocol` tells them what is missing. In crypto-autoresearcher a ledgered
experiment writes `experiments/<EXP>/export.json` from its run packages and
binds `protocol.json` in `execution_plan.protocol_hashes`.

## 6. Review by another runner

Any runner (Claude Code, Codex, OpenCode, a human, CI) can review an export
without the producer's session: `review new` scaffolds an
`experiment.review/v1` record with the hash and adherence checks already run;
the reviewer fills the controls, recompute, statistics, scope and blinding
checks, replays a nonce-chosen sample where the backend admits replay
(`ecbench verify --replay`, `tools/runbook.py audit`, a taskq re-run at the
pinned commit), and writes observations, per-claim judgments in the fixed
vocabulary, open questions and a recommendation. Reviews are write-once
under the export's `reviews/` directory; a second review is a second file.
A review asserts nothing about official research status: in
crypto-autoresearcher the Coordinator's `review-evidence` decides, in crypto
the validation gate and the PR, and a review record is one of the inputs
they cite.

## 7. Literature

- Hoefler and Belli, "Scientific Benchmarking of Parallel Computing Systems:
  Twelve Ways to Tell the Masses when Reporting Performance Results", SC15,
  DOI 10.1145/2807591.2807644 (provenance: retrieved, abstract and
  publication page; the twelve rules inform sections 1 and 3).
- Mytkowicz, Diwan, Hauswirth and Sweeney, "Producing Wrong Data Without
  Doing Anything Obviously Wrong!", ASPLOS 2009, DOI 10.1145/1508244.1508275
  (retrieved, project page and course notes: link order and environment
  size as measurement bias; section 2).
- Curtsinger and Berger, "Stabilizer: Statistically Sound Performance
  Evaluation", ASPLOS 2013 (retrieved, project page: layout randomization,
  `-O3` vs `-O2` indistinguishable from noise; section 2).
- Georges, Buytaert and Eeckhout, "Statistically Rigorous Java Performance
  Evaluation", OOPSLA 2007 (retrieved, proceedings listing; confidence
  intervals over repeated runs rather than best-of; section 3).
- Kubernetes kubelet checkpoint API: `ContainerCheckpoint` beta since
  v1.30, `POST /checkpoint/{namespace}/{pod}/{container}`, archive under
  `/var/lib/kubelet/checkpoints` (retrieved, kubernetes.io reference page);
  AWS Spot interruption notices: two-minute best-effort warning via
  EventBridge and IMDS `spot/instance-action` (retrieved, EC2 user guide);
  Karpenter interruption handling: taint, drain and replace on a Spot
  interruption warning via the SQS queue, rebalance recommendations only
  evented (retrieved, karpenter.sh disruption page). The restore side
  (CRI-O and containerd checkpoint images, CRIU's CUDA plugin) is cited in
  the crypto design document with its own provenance; criu.org was
  unreachable (HTTP 503) when this document was written.
