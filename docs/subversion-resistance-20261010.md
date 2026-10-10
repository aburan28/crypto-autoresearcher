# Subversion resistance: can an executor fabricate a result?

Written 2026-10-10 while designing the H-ECDLP-bd1572 battery, in answer to
the owner's question whether a model that runs and reports experiments can
bypass the ledger and simply invent its numbers. This note records what the
harness enforces today (read from the code, not the docs), where the gap is,
what the H3 battery does about it, and the rule proposed to close the gap
program-wide. It is a design note: it changes no record and grants no
authority. Adopting the proposal in section 5 needs its own `DEC-*` and an
`AGENTS.md` amendment.

## 1. Threat model

The adversary is an executor session that wants a run to be read as a
result without doing the computation, or wants a computation it did do to
read differently. It controls every byte it writes: `run.py`, `check.py`,
`raw-result.json`, `manifest.yaml`. It cannot change a frozen specification,
a trial plan or a handoff without the hash check noticing, and it cannot
change a hypothesis status or write a decision (role contracts,
`orchestration/roles.yaml`). The question is whether the bytes it does
control can carry a fabricated observation through to an evidence record.

## 2. What is enforced today, from `tools/experiment_execution.py`

- The trial plan is frozen and hash-bound: `specification_sha256`, every
  entry of `source_sha256` (driver, checker, dependencies) and the plan's
  own hash in the executor handoff must match before launch. A changed
  driver is a refused launch, not a quiet substitution.
- The supervisor, not the executor, launches `argv`, captures stdout and
  stderr, enforces the memory ceiling and the watchdog, writes
  `launch.json`, `command.txt`, `environment.json` and the
  `execution-receipt.json` with the SHA-256 of every artifact. A run
  directory is created exclusively and never reused.
- `check_argv` runs after the driver under the same supervision; a
  non-zero checker exit is not `output_validated`.
- Run records are immutable; a later edit to `raw-result.json` breaks the
  receipt hash (`trial_state` then reads `needs_reconciliation`).
- Claimed solves and relations carry certificates that an independent
  code path re-verifies (`docs/claims-and-verification.md`): an ECDLP
  witness `k` is checked by `[k]P = Q`. These cannot be fabricated.
- Evidence promotion goes through independent validator and red-team
  sessions with a frozen `review_plan`, optional blind re-derivation, and
  a Coordinator decision; an executor's own words never promote anything.
- Cairn external verification (`docs/cairn-integration-plan.md`) adds a
  pinned, sandboxed checker owned by nobody in the session, where it is
  wired.

## 3. The gap

Everything above protects the **integrity** of the bytes (what was run,
what was written, that nothing changed afterwards). None of it protects
the **provenance of a measurement** when the executor authored both
`run.py` and `check.py`:

1. A driver can print the predicted numbers instead of computing them.
   It is deterministic, replays byte-identically, hashes correctly, and
   passes a checker that only re-derives summaries (a ratio from two
   counts, a histogram sum) from the driver's own output.
2. The certificate discipline covers claimed successes (solves,
   relations, key recoveries), which are NP-checkable. A distribution, a
   count, an exponent fit or a null result has no witness, and most of
   this program's measurements are of that kind.
3. Independent review is a later, human-scheduled act. Between a run and
   its review the raw result stands unchallenged, and reviewers who
   "look at the report" tend to look at the legible summary.

This is the "three-body" failure: the instrument reports whatever the
instrument's author wants, and the record-keeping, which is sound, faithfully
preserves the fabrication.

## 4. What the H3 battery does about it

Every checker in `experiments/EXP-ECDLP-{2535ec,6dacdb,3e8403,15534c,28ad87}/implementation/check.py`
is written to catch a result that was not produced by the stated
computation, not merely one that is internally inconsistent:

- **No shared code.** No checker imports `run.py`; each carries its own
  primality test, trial division, Legendre test, elliptic-curve arithmetic,
  Z/p^r Jacobian arithmetic, number-field ring arithmetic or genus-2 Cantor
  arithmetic as the experiment needs.
- **Replay from recorded inputs.** The driver records the per-sample
  inputs (seeds, primes, curves, points, scalars, hit vectors, relation
  records), and the checker recomputes a seeded sample of samples from
  those inputs with its own arithmetic and demands equality:
  a full box of smoothness counts (2535ec), recounted group orders and
  embedding degrees (6dacdb), every recorded lift point plus a sample of
  non-hits that must be non-squares (3e8403), replayed formal-group
  defects (15534c), relations rebuilt as `[r]A + [s]B + T` (28ad87).
- **Tamper tests.** In the design session a doctored count, a faked
  embedding degree, an invented point and a "perfect recovery" defect log
  were each written into a copy of an honest smoke output; every checker
  returned non-zero with the forged field named.
- **The remaining exposure, stated.** A checker that replays a *sample*
  bounds the fabrication rate rather than excluding it: a driver that
  computes honestly on the sampled items and lies on the rest is caught
  only with the probability that the seeded sample hits a lie, and the
  checker's seed is public. The full-replay checker (2535ec, smallest box)
  and the every-hit checker (3e8403) do not have this exposure; the others
  do, at 5 to 20 items per cell. The closing move is section 5.

## 5. Proposed program rule (not adopted by this note)

> A run of a measurement experiment (certificate kind `none`) may be cited
> by an evidence record only if at least one of the following holds, and
> the evidence record says which: (a) its `check.py` shares no code with
> the driver and re-derives a declared fraction of the recorded samples
> from recorded inputs, with the fraction and the seed stated in the trial
> plan; (b) an independent session (different executor, `independent_session: true`)
> re-executed the frozen trial plan from the committed sources and obtained
> a byte-identical `raw-result.json` **and** a second implementation of the
> primary metric agreed within the pre-registered tolerance; (c) a cairn
> `replay` or `certificate` verdict is recorded under
> `external_verification`. `tools/validate_ledger.py` should emit an
> advisory on any `EV-*` citing a `kind: none` run with none of the three.

(b) alone is weaker than it looks: a deterministic forger replays
byte-identically. The second implementation of the metric is the part that
matters, and (a) is the cheap, always-available form of it. The `executor`
role contract should also say plainly that a checker which only re-derives
summaries from the driver's output is not a checker.
