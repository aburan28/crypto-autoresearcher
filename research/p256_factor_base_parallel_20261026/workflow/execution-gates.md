# Second-pass execution gates, 26 October 2026

The eight cards open **Phase A engineering only**. Reading sources, writing
implementation/analysis/export code, syntax checks and schema checks do not
authorize collecting the next observation panel. The first-pass artifacts are
immutable references. The root session owns Git operations and release.

Before choosing or implementing a method, each worker reads its linked prior
results and the primary literature or official documentation that matters to
its approach. Write `literature.md` first: exact paths/URLs, what was read,
assumptions checked, parameter-transfer limits and inaccessible-source gaps.
The prior report's citation is a pointer; do not claim to have read a primary
source because the previous worker read it. No novelty claim is in scope.

Each worker prepares these files inside its exclusive `tracks/fN/` scope:

- `run.py --out <fresh-directory> --seed <integer>`; import and `--help`
  perform no observation panel. Retain every case and every rejected draw.
- `protocol.draft.json`, complete `experiment.protocol/v1`, using
  `docs/experiment-protocol.md`, the schema, checker and worked example.
  Keep it explicitly draft. Record the complete fixed case/seed law, controls,
  exact counted metrics, all exclusions and the requested/finished/not-completed
  flow. The protocol must not quote pilot results collected before release.
- `analysis.py`, deterministic analysis of recorded rows only, plus exporter
  support. Pin the analysis and actual instrument source before data.

The executable writes raw per-case records plus `rows.jsonl`. The export unit
must be stated explicitly in the draft: an execution is either a whole frozen
panel with all internal cases retained, or a named case. Never switch units
after observing data. Every export row records `run_id`, `arm`, `instance_id`,
`seed`, `replicate`, `warmup`, `status`, verification, observed exact metrics,
native counters, host/source identities, artifacts, exclusions and diagnostic
resource values. Configure `from-rows` with an explicit column map or write
the schema directly, then use `check-export --protocol ... --verify-files`.
Do not copy planned identities into missing observed identities.

Metrics are exact identities, sets, object counts and ranks. No timed primary,
performance comparison or inferential natural-yield claim is planned. On the
shared host wall/CPU clocks are diagnostic; `wall_valid` is false. A stopped
solve is unknown, a wrong certificate is wrong, and neither is an empty set.
Any control omitted from the protocol needs its real applicability reason;
embedded positive/refusal controls must exercise the actual solver path.

Phase B has **all** these preconditions, bound to the exact affected bytes:

1. Root commits and pushes the handoffs, source, inputs and analysis.
2. Root validates and freezes the complete protocol before its first affected
   data, with actual commits/source hashes and a prospective analysis hash.
3. `.resume/RESUME.md` is complete and accurately describes the frozen work.
4. A real `scripts/checkpoint.sh push` succeeds, followed by `gate`. A local
   preview, rejected upload, expired token or elapsed time is not this gate.
5. Root explicitly releases execution with the source/protocol/checkpoint
   identities. Workers run only the released bytes. A changed scientific
   panel needs a new prospective protocol version/amendment.

Automatic approval review rejected the first S3 resume disclosure attempt.
Root prepared a concrete payload and an explicit question. Engineering may
continue; affected execution waits for a successful real push and gate.
The question cannot be treated as answered by waiting.

After execution, checkpoint again, preserve raw/export failures, and return
the source and output paths. Root snapshots exact producer data before fresh
reviewers run. Every track leaves a new report, editable diagram/SVG and an
inspected compact PDF. The frozen prospective review obligations describe
coverage, not a scientific admission, approval or official promotion.
