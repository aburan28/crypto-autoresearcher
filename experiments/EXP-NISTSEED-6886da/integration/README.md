# Prospective ECPP integration additions

These are unapproved, incomplete integration helpers for the reserved
`EXP-NISTSEED-6886da`. They do not execute a cohort order or grant execution
authority. The earlier V9 implementation, its mock tests, frozen inputs,
reports and receipts remain unchanged.

The source review identified four requirements for a later full-cohort packet:

- A quiet supervisor wrapper, since V9's CLI prints after hashing its own
  supervisor stdout log.
- A mandatory deterministic capsule and exact inventory for variable raw VM
  artifacts, including partial and censored captures.
- A narrowly specified independent checker path for malformed guest framing,
  with all static identity and raw-custody checks preserved.
- An actual non-cohort A/A execution producer; the existing A/A interface only
  compares two supplied records.

The current helpers implement capsule construction/validation and a
source-bound supplemental factor-token extractor. They are not a complete
trial wrapper, A/A producer, approved protocol or admitted experiment.

`printed_trace.py` binds the original archive and C source member hashes.
It preserves printed tokens, byte offsets, repetitions, incomplete lines and
arithmetic-shape anomalies. It associates a factor with a printed D/depth only
through the source's consecutive optional A/B/m lines and factor lines.
Unknown intervening text clears that association. No unprinted attempt is
inferred.

`test_custody_helpers.py` uses only synthetic byte fixtures and temporary
directories. It verifies deterministic custody and refuses missing, extra,
changed, symlinked or inconsistently indexed raw artifacts. It invokes no
legacy executable, VM or mathematical cohort trial.
