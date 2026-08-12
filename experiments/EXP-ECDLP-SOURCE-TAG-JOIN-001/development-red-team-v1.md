# Development red-team v1

## Handoff: source-tag join post-run validation

### Claim or task

Determine whether an implementation or interpretation defect invalidates the
verified development artifact or its narrowly scoped negative result.

### Status

`NEGATIVE RESULT`, final classification `VALID`.

### Assumptions

- One seed and one generated curve at each of 10, 12, and 14 bits.
- Noncanonical toy evidence only.
- The scoped negative is no tested 20% matched-null advantage and no useful
  compiler threshold, not a scaling theorem or ECDLP claim.

### Evidence so far

- Independent replay verified three curves, 15 factor-base instances, 2,520
  route rows, 2,160 matched nulls, and 39,475 returned factor witnesses.
- No defect was found in route coverage, target reuse, scalar exclusion, witness
  recovery, randomized descent, or D5 outer-factor point/byte accounting.
- Null invariants and scalar calibration pass 270/270 candidates. Every
  matched-null 20% work/payload metric has zero passing candidates.
- Exact-D2 query `S*T^2` ratios are at least `1819/11605/34882`; partial-D4
  online ratios are at least `16.3/34.9/101.1` at 10/12/14 bits.
- Only 104/270 candidates satisfy both effective-null movement and nonsaturation:
  zero at 10 bits, 62 at 12 bits, and 42 at 14 bits.

### Failure modes

- Empty top-level promotion arrays are mandatory with one seed and are not
  negative evidence.
- The best 10-bit D4 ratio is ineligible because no 10-bit row passes both null
  movement and saturation prerequisites. It cannot anchor a scaling claim.
- Total payload is `C + 3*tag_bits*R`, with shared scaffold `C`. Even deleting
  every candidate route cannot reach the `0.8` total-payload threshold for any
  four-tag row and two eight-tag rows. Total payload is a compiler-storage gate,
  not an independent source-correlation statistic.
- Route count is not proven impossible for nonsaturated rows. Near-one observed
  ratios are an empirical miss, not a general lower bound.
- One descent and BSGS challenge per row establish correctness on the scheduled
  target only.
- The valid negative is that these candidates show no robust 20% matched-null
  advantage and are decisively worse than the tested compiler baselines. It is
  not a full three-size structural falsification because the 10-bit controls are
  ineligible.

### Next concrete action

Preserve the artifact. A successor must replace ineffective null draws, gate
incremental route payload separately from total advice, prove every retained
gate reachable with a positive control, remove saturated cells, use at least two
curve seeds and multiple descent/BSGS challenges, and change the outer query
schedule.

### Artifact paths

- `development/DEV-SOURCE-TAG-JOIN-001/analysis.json`
- `development/DEV-SOURCE-TAG-JOIN-001/verification.json`
- `development/DEV-SOURCE-TAG-JOIN-001/raw-result.json.gz`
- `src/source_tag_join.py`
- `contract.md`

No issue invalidates the raw artifact or the explicitly narrowed negative. The
boundaries above are mandatory interpretation constraints, not reasons to edit
or discard the evidence.
