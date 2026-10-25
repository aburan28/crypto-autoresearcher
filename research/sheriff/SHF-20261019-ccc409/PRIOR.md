# Prior (written before reading any evidence record)

Slice C, ledger/evidence. Expectations, in order of confidence:

1. Most `replicated` labels rest on same-author, same-instrument reruns (a
   deterministic script rerun is reproducibility, not independent replication).
   Expect many to be justified only as `preliminary`/`replicated` scoped to the
   instrument.
2. `strong` is defined as predefined protocol + controls + multiple instances.
   Expect several `strong` records with a single instance or pseudo-replicated
   cells (see EV-ECDLP-284817's own group-vs-cell note).
3. `moderate` is not in schemas/evidence.schema.json's enum: every such record
   is schema-invalid as labelled.
4. Many run ids cite directories that exist, but digests are rarely declared in
   run manifests of the pre-tooling era; "digests_ok" will often be
   not-checkable, which is not a pass.
5. Records with `strength: n/a` and prose strengths are label-vocabulary
   drift, not necessarily weak evidence; the brief's count (63 reading `n`)
   will not match the on-disk count.
6. Recomputation of arbitrary metrics generically is not possible; I expect
   recomputed_ok to be null for most records and to say so.
