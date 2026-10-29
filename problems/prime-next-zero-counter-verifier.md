# Frozen census verifier rejects an explicit zero counter

Observed 2026-10-29 after EXP-PNEXT-624f41 / RUN-PNEXT-ad1645. The producer
completed all 106 encoding and six coefficient cells, but native checking
returned 1 at encoding.py's census-cost equality; the native receipt is
`invalid_output`. No result is promoted and no rerun is launched.

The first failing case p17-s2-r0/quartic has identical complete model sets
and nonzero census costs. Its producer census contains
`restriction_term_visits: 0`; the fresh checker ring omits that unused key.
`delta` retains the union of historical counter keys, including zeros. Exact
dictionary equality therefore rejects equivalent sparse count maps.

The original source, protocol, raw artifacts, and failed receipt remain
immutable. The additive `supplemental_check.py` verifies all sealed hashes,
then replaces exactly one comparison in the frozen verifier with integer
counter equality treating absent entries as zero. It rejects nonzero,
negative, and noninteger discrepancies. All other full-model, certificate,
witness, chart, configuration and journal checks remain in force.

This correction is filed after the affected data (`filed_before_affected_data:
false`), is exploratory only, and does not satisfy or rewrite the native
validated-output requirement. Exit criterion for the mathematical replay is
all retained cells passing the additive checker; this does not complete
native measurement, archival review, or independent scientific adjudication.
The next software test is a synthetic serialization/history test of sparse
counter equality. A future scientific run requires a new prospectively frozen
instrument and admission; the existing fixed single-run plan is not retried.

The supplemental export will keep all native arm rows failed and retain the
recorded subcell counts separately. Its extraction reuses the frozen counter
aggregation without changing scientific metrics. A supplemental check may
verify the artifacts without changing that failed native outcome. Any such
export/report is post-data descriptive analysis, not confirmatory evidence.
