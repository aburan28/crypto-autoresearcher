# Bounded-separation revision history v3

## Handoff: immutable paper-preflight lineage

### Claim or task

Preserve the reviewed revisions and identify the authoritative paper result.

### Status

`OBSERVATION`, provenance record. V3 is authoritative only through
`decision-v3.json`; v1 and v2 are historical `REVISE` records.

### Assumptions

- No source code or experiment was authorized in any version.
- Hashes are SHA-256 over the repository file bytes before the final commit.

### Evidence so far

```text
v1  e2c4f65663affe48f42f75289ac314dc704f79588d4ae6c9f6a3ff5125ef8024
v2  2627ea854f03698eb904659e09e3e479dd209b8498b8c2c3a55892683c237488
v3  48dc472d318206406dec6d3280eeb9c3494264406408e0db2ce9e1e868dbd81f
```

- V1 established the moment theorem, canonical count, symbolic divisor
  exclusion, and trace-resolvent route, but did not yet separate every
  characteristic, active-term, identity, or cumulative-cost condition.
- V2 repaired characteristic-p active counts, exact trace multiplicities,
  odd-subgroup roots, and both identity sentinels. It still overcharged
  first-witness descent by demanding both child values and lacked a cumulative
  path gate.
- V3 evaluates one chosen child at each known-zero parent, distinguishes
  all-root enumeration, and requires cumulative work/traffic plus aggregate
  peak-live state below B2.
- During pre-freeze concurrent review, the benchmark agent also reported an
  unbound transient v1 hash
  `1563f8a97593a84d65a672654aad391f3b69cf031ef3506e931c759612a61aa4`.
  Those transient bytes were never committed and are not designated evidence;
  the discrepancy is preserved here rather than silently normalized.

### Failure modes

- Selecting authority by the largest filename without the decision record.
- Treating a historical draft as reviewed GO.
- Omitting the transient-hash discrepancy from provenance.

### Next concrete action

Bind v3 and its review artifacts in `decision-v3.json`.

### Artifact paths

- `bounded-separation-preflight-v1.md`
- `bounded-separation-preflight-v2.md`
- `bounded-separation-preflight-v3.md`
- `bounded-separation-theory-review-v3.md`
- `bounded-separation-accounting-review-v3.md`
