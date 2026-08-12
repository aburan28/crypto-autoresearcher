## Handoff: TT norm-rank implementation red team

### Claim or task

Audit producer/verifier independence, frozen-input firewalls, semantic replay,
mutation coverage, and interpretation boundaries before harness execution.

### Status

OBSERVATION - `GO` for bounded development execution.

### Assumptions

- The review authorizes only the frozen toy diagnostic.
- Import independence and adversarial fixtures reduce implementation risk but
  do not prove mathematical independence or mutation completeness.

### Evidence so far

- The verifier contains an independent compact RCB transcription and does not
  import or load the producer.
- It independently replays source tuples, primary and control targets, norm
  products, six-term source-span evaluation, zero sets, projective rescaling,
  ranks, and deterministic samples.
- Primary target and registry provenance is checked during manifest audit;
  post-observation target selection is separately rejected.
- The producer and verifier require the `SANITY_ONLY`, no-compiler,
  no-breakthrough, and deterministic-success firewall fields.
- The full baseline replay covered six instances, 60 cells, and 288 rank jobs
  with zero mismatches.
- All 15 frozen producer, artifact, manifest, source, accounting, and claim
  mutations were detected; none survived.
- The verifier now binds the producer's declared source hash to the local
  producer file without importing it.

### Failure modes

- Shared conceptual mistakes remain possible even with separately structured
  transcriptions.
- The mutation corpus is finite and does not establish completeness against
  unseen implementation faults.
- Toy exact ranks and correctness do not construct an implicit compiler or
  imply asymptotic ECDLP progress.

### Next concrete action

Launch the frozen development partitions through the harness and preserve the
independent verifier results without widening the `SANITY_ONLY` claim.

### Artifact paths

- `experiments/EXP-ECDLP-TT-NORM-RANK-001/src/generate_tt_norm_rank.py`
- `experiments/EXP-ECDLP-TT-NORM-RANK-001/src/verify_tt_norm_rank.py`
- `tests/test_tt_norm_rank.py`
- `experiments/EXP-ECDLP-TT-NORM-RANK-001/mutation-manifest-v2.json`
