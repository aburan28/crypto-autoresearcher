# BLK-1 alternative fix — TASK-20260901-eb81f4 (executor, BATCH-241d37, GOAL-AES-002)

**Artifact class:** PROSE_REPORT. **Covering manifest:** `blk1-alternative-fix-receipt.json`.
**Disposition:** APPLIED to the shared working tree. Nothing committed.
**Asserts nothing about AES at any round count.** This is protocol/tooling work.
No margin is stated anywhere in this task, so SC-4's `dominated_by` string is
not required and `dominated_by_if_any` is null.

## What was asked

DEC-20260901-1fc2f5 names two routes past BLK-1. Route 1 (regenerate the
prune-only baseline) is a Coordinator authorization this task does not hold.
This task took route 2: a **differently-worded edit** that adds the
`key_recovery` certificate kind **without changing the existing error text
verbatim**. Acceptance bar: validator output byte-identical to the pre-task
shared-tree run — zero new errors, zero stale baseline entries.

## The mechanism, verified cheaply rather than rediscovered

Confirmed directly, not re-derived by re-running the failed experiment:

- `tools/validate_ledger.py:626` tested `kind in ("discrete_log",
  "decomposition")` and line 631–632 emitted the literal
  `run.result.certificate.kind must be one of discrete_log|decomposition|none`.
- `grep -c "discrete_log|decomposition|none" tools/validate_ledger_baseline.txt`
  → **112**. Suppression is by exact line match (`new = [e for e in ctx.errors
  if e not in baseline]`, `stale = baseline - current`), and `--update-baseline`
  is prune-only.

So the amendment's specified rewording of that message was self-defeating: it
staled 112 entries and re-emitted 112 freshly-worded errors in one stroke.

## The edit

One string added to an accepted-kind set, hoisted to a named module constant,
and **the rejection message left byte-for-byte alone**:

- new `CERTIFICATE_KINDS = ("discrete_log", "decomposition", "key_recovery")`
  beside `BASELINE_PATH`, documented as the single source of truth;
- `check_run` now tests `if kind in CERTIFICATE_KINDS:`;
- the `elif kind != "none": ctx.err(...)` message is **unchanged**, with a
  comment at the site explaining exactly why it must stay unchanged.

Documentation updated to match what the code accepts: the enum line in
`docs/claims-and-verification.md` and `docs/evidence-and-reproducibility.md`
becomes `discrete_log | decomposition | key_recovery | none`, plus the
amendment's `key_recovery` statement block (key size, round count, exact
plaintext/ciphertext pairs, recovered key; two-implementation independent
verifier) and the rules bullet.

The exact diff is `blk1-alternative-fix.patch`.

## What the bar measured, and what it could not

Validator output was captured verbatim at four points (all in the receipt):
shared tree before; isolated detached worktree after the code edit only;
the same worktree after the doc edits too; shared tree after applying. All four
are **byte-identical**: `1210 grandfathered suppressed`, `FAIL: 4 new validation
error(s)` — the same four pre-existing `EXP-ISOU-2ac81f` lines — and **no stale
note at all**. The before-run was re-executed immediately before applying and
was byte-identical to the first before-run, so the comparison is not stale.

Byte-identical output is necessary but **not sufficient**: a no-op edit would
produce it too. Direct controls on `check_run` close that gap
(`controls` in the receipt):

- positive: `kind=key_recovery, verified=true` → **no error** (previously rejected);
- duty retained: `kind=key_recovery, verified=false` → `run claims a key_recovery
  but certificate.verified is not true`;
- null-object: `kind=bogus_kind` and a missing `kind` still emit the protected
  literal **verbatim** — which is precisely why all 112 baseline entries keep matching;
- no regression on `discrete_log`, `decomposition`, `none`.

## The disclosed cost of this wording

`check_run`'s rejection message now **under-enumerates** the accepted
vocabulary: it says `discrete_log|decomposition|none` while `key_recovery` is
accepted. An operator reading only that message will not learn `key_recovery`
exists. This is a real cost, deliberately paid, and it is disclosed in three
places: a comment at the code site, a `KNOWN DISCREPANCY` bullet in
`docs/claims-and-verification.md`, and here. The documentation, not the message,
is authoritative. The discrepancy is retired when a Coordinator-authorized
baseline regeneration retires those 112 grandfathered entries — route 1, still
available and now cheaper, because after it the message can simply be reworded.

## Named as OPEN AND UNATTEMPTED (SC-9) — not tried, not screened, not negative

- `tools/cairn_bridge.py` (`_OBJECTIVE_FILES` / `SUPPORTED_KINDS`) has no
  `key_recovery` checker, so the cairn re-verification path cannot score such a
  certificate. Outside this task's write_scope.
- The amendment's required two-implementation verifier (pycryptodome + openssl
  CLI, in the run wrapper) is not implemented in `harness/runner.py`. Outside
  write_scope.
- `check_run` validates the *kind* and the verification duty only; it enforces
  no structure on `key_bits`, `rounds`, `statement.pairs` or `statement.key`.

A conforming run therefore may now *record* `kind: key_recovery`, but the
independent verification machinery the amendment demands for it does not exist
yet. Whether BLK-1 is CLOSED on that basis is a Coordinator judgment on this
evidence; this executor does not declare it.

## Unexpected observation, recorded not discarded

An untracked file
`coordination/goals/GOAL-AES-002/amendments/protocol-amendment-GOAL-AES-002-004.yaml`
appeared in the shared tree **during** this task. It was not created, read,
modified or removed by this task and is outside its write_scope. It is recorded
because it changes `git status --short` between the pre- and post-task
snapshots, and a reviewer would otherwise see an unexplained delta. It did not
affect validator output (the re-run before-state proves this).

## Provenance and honesty notes

- The handoff binds snapshot `69f52eba…`; shared-tree HEAD at execution was
  `775386fb9`, two coordination `claim(...)` commits later, neither touching
  `tools/` or `docs/`. Work and comparison were done at HEAD.
- `tools/validate_ledger_baseline.txt` sha256 is identical before and after
  (`5dcfb520…`). `--update-baseline` was never invoked.
- Requested policy `executor-implementation` (effort medium, no fallback, no
  degradation). The model that answered was **claude-opus-5**; the anthropic
  binding for that policy is `claude-sonnet-5`. Model selection is process-level
  under this runtime, so it could not be rebound mid-task. Not a downgrade and
  not degraded mode, but a substitution — disclosed, not passed over.
- Nothing was committed. The Coordinator's archive task commits.
