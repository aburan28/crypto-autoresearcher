# Scope correction for SSI audits

## Correction basis

The repository classifier reports both `IDEA-20261007-20f660` and
`IDEA-20261007-cd446e` as `non-ECC`:

```text
IDEA-20261007-20f660  area=-  non-ECC
IDEA-20261007-cd446e  area=-  non-ECC
```

They belong to `RQ-SSI-1946c9` and the SSI campaign, whose goal is
`GOAL-SSI-2fa82a`, not to the active `GOAL-ECDLP-001` campaign. The audits
committed at `e62c5e92ac` and `e63fc4a8f2` were therefore placed under the
active ECDLP proposal directory as a coordination-scope mistake.

## Effect

- The two SSI audit files remain immutable historical artifacts; they are not
  deleted, rewritten, or treated as ECDLP evidence.
- Their dispositions do not change any ECDLP hypothesis, experiment, goal, or
  queue state.
- The SSI findings are advisory material for the corresponding SSI goal and
  should be refiled or superseded there by a Coordinator working on
  `GOAL-SSI-2fa82a`.
- The active ECDLP loop returns to ECDLP-classified ideas only. No experiment
  was launched under either SSI audit.
