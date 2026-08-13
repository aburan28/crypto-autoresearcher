# TASK-20260813-cdcd88 — AUTHOR PREREG-4

    goal / batch    GOAL-MLKEM-005 / BATCH-6e08fe
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           completed
    depends_on      (none)
    review_required false
    archived_by     TASK-20260813-e24ad9
    budget          5400 s, 2 GB, 1 run
    claim tier      TOY

## What it did

Wrote and froze `PREREG-4`: **(a)** RC-3, a frozen mechanical correction of
`BATCH-fbb639`'s coverage table, carried verbatim from the Red Team's own
already-committed probe (`probe_coverage_beta_mismatch.py` /
`_output.json`) — `hkz/L9_b15` and `hkz/L11_b20` restated genuinely
UNCOVERED, `hkz/L9_b22`/`hkz/L11_b30` restated with the corrected true
`beta_hi`-based `D_route` source, numerically unchanged at `0.0`. **(b)** the
lead measurement: a genuinely non-code-shared re-implementation of `ROUTE-I`
for `lam1n`/`hkz` at `L7`/`L9`/`L11` (`d <= 40`, no new reduction above
`d = 40`), re-run against the SAME archived `ROUTE-P` values
(`results_relvar.json`), with an operational definition of "genuinely
non-code-shared" (`PREREG-4` §2.2), a frozen coverage-audit-first obligation
(§2.3, `ROUTE-P` restricted to `results_relvar.json`'s own `G_REL1` per-basis
array — `results_l7l8.json`/`results_am4.json` explicitly excluded as a
`ROUTE-P` source, since both are `ROUTE-I`-family, code-shared artifacts
under F-1/RT-1), and a frozen three-branch termination clause (§2.6:
`T-INDVERIFY-NODATA` / `-ARTIFACT` / `-CONFIRMED`, each `-PARTIAL`-suffixable,
precedence stated) matching `DEC-20260813-28d7b2`'s own two-outcome revisit
condition exactly. §2.7 re-derives, not merely cites, why this is not an
eighth/ninth consecutive gate repair and does not trigger `PREREG-2` 7.5.

Executed with NO SHELL, using read-only file access only; every number
attributed to "this Coordinator" is a read-only observation, weaker than a
measurement, and the lead's own obligation-0 audits (§1, §2.3) are the
batch's actual attributed measurements.

## Artifact

    tasks/TASK-20260813-cdcd88/prereg.md
