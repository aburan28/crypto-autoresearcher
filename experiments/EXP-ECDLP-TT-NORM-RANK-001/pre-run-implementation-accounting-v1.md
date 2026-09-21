## Handoff: TT norm-rank implementation accounting

### Claim or task

Audit the frozen census, rank-traffic formulas, field conversion, enumeration,
storage, and RSS accounting before harness execution.

### Status

OBSERVATION - `GO` for the bounded V3 row-basis accounting model.

### Assumptions

- The traffic model is specific to the incremental normalized row-basis
  implementation; it is not a lower bound for every rank algorithm.
- One `F_p2` coefficient is charged as two base-field words.
- Cumulative logical traffic and peak RSS are separate resources.

### Evidence so far

- The census is exactly 24 source tables, 60 semantic cells, 264 EC plus 24
  control rank jobs, 12 cohort-span jobs, and 18 comparator jobs.
- The frozen `F_p` ceiling is `(P,E,N,T) =
  (6,183,256, 152,824,740, 159,007,996, 495,573,756)`.
- The frozen `F_p2` ceiling is `(615,868, 14,109,700, 14,725,568,
  46,024,308)`.
- The aggregate ceiling is `495,573,756 + 2*46,024,308 = 587,622,372`
  base-field-word equivalents.
- Observed traffic was `299,838,977` `F_p` words and `18,262,674` `F_p2`
  words, or `336,364,325` base-field-word equivalents.
- The verifier enforces materialization `2P`, pivot scans at most `P`, fused
  updates `3E`, normalization `2(N-E)`, certificate reads `N-E`, phase sums,
  per-field ceilings, and the extension-field conversion.
- Full enumeration is explicitly charged as 615,868 tuples and 2,463,472 RCB
  calls and is marked `retained_as_advice=false`.
- Producer/verifier peak RSS stayed below 190 MB, within the 2 GiB limit; all
  canonical storage and logical traffic buckets are present.
- The stale `development-v1` artifact label found during review was repaired
  to `development-v3`, and the complete round trip was rerun successfully.

### Failure modes

- Logical traffic is an implementation-level access model, not measured DRAM
  traffic.
- RSS includes interpreter overhead and must not be added to cumulative
  logical traffic.
- This accounting says nothing about a missing coefficient-space compiler,
  relation generation, descent, or rho comparison at cryptographic scale.

### Next concrete action

Run the four frozen development partitions through the harness and compare the
registered receipts with these exact census and ceiling values.

### Artifact paths

- `experiments/EXP-ECDLP-TT-NORM-RANK-001/rank-traffic-model-v3.md`
- `experiments/EXP-ECDLP-TT-NORM-RANK-001/execution-matrix-v3.json`
- `experiments/EXP-ECDLP-TT-NORM-RANK-001/src/generate_tt_norm_rank.py`
- `experiments/EXP-ECDLP-TT-NORM-RANK-001/src/verify_tt_norm_rank.py`
