# Experiment Contract: Implicit Pair-State Index V1

## Hypothesis

An exact target-conditioned `D2+D2` index can retain only unordered pairs of
`D2` state identifiers, while deferring the four-source witness expansion
until a query. This may remove the four-source witness payload that made the
explicit pair index larger than materialized `D4`.

The index remains fixed-curve advice. It is not an ECDLP attack or a
generic-group claim.

## Null hypotheses

1. Deferred witness expansion loses exact witnesses or creates duplicates that
   cannot be charged cleanly.
2. Two state identifiers per pair record are still too large after D2 advice,
   key material, and pair construction are charged.
3. Query-time state-sum checks and witness reconstruction erase the online
   advantage over recursive D2+D2 or materialized D4.

## Parameters

- immutable input: `development/TYPED-FIVE-EC-V1/raw-result.json`;
- three generated ordinary prime-order curves and four coordinate families;
- target batch: planted, held-out, shifted-control;
- exact nondecreasing D2 and D4 source tuples;
- pair records: one unordered pair of D2 state IDs, no stored four-source
  witness tuple;
- exact and coordinate fingerprints `(x mod 2^w,y mod 2^w)` for
  `w in {1,2,4,8}`;
- query-time lift expands the two retained D2 witness lists and replays each
  canonical four-source witness against the complement.

## Metrics

- D2/D4 support and witness records;
- number of D2 states and unordered state-pair records;
- exact/fingerprint bucket counts;
- offline D2, D4, pair-sum, and pair-state construction operations;
- per-target candidate pair records, state-sum rejects, witness products,
  witness replays, accepted witnesses, and online work;
- advice words: D2 point/witness advice plus pair key fields and two state IDs
  per pair record;
- `S*T^2/q` diagnostic only as a finite toy frontier;
- exact hit-set equality against recursive D2+D2 and materialized D4;
- independent replay and mutation rejection.

## Controls

- recursive `D2+D2` is the low-advice scan control;
- materialized `D4` is the exact fast-query control;
- explicit witness-bearing pair index is the predecessor representation;
- width 1 is collision-heavy and width 8 is near-exact;
- all accepted lifted witnesses are independently replayed.

## Success criterion

The implementation is valid only if every route returns the exact same
four-source witness set. A useful fixed-curve result additionally requires the
state-ID route to beat materialized `D4` on the fully charged advice/query/
offline frontier, not merely to use fewer bytes than the explicit predecessor.

## Falsification criterion

Any mismatch, missing witness, uncharged state-pair, or accepted verifier
mutation falsifies the implementation. Exactness with a dominated frontier is
a scoped negative for deferred witness lift, not for all implicit operators.

## Reproduction

```bash
python3 src/implicit_pair_state_index.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --widths 1 2 4 8

python3 src/verify_implicit_pair_state_index.py \
  /path/to/raw-result.json
```

## Handoff

### Claim or task

Test whether deferred witness lift can compress a target-conditioned exact
pair-sum index below the explicit pair-index and materialized-D4 frontiers.

### Status

HYPOTHESIS, TOY-EVIDENCE, MODEL-BOUND

### Assumptions

- fixed-curve D2 state advice is reusable across the target batch;
- state IDs are charged as logical words;
- every pair record and every query-time witness product is charged.

### Evidence so far

- recursive D2+D2 is exact but scans every D2 state;
- explicit pair indexing reduces query work but stores every four-source
  witness product and is advice-dominated;
- coordinate fingerprints only trade key material for replay collisions.

### Failure modes

- pair-state count may remain quadratic in D2 support;
- deferred witness products may dominate query work;
- exact state-sum checking may restore the explicit pair cost.

### Next concrete action

Implement independent producer/verifier, run the registered 12 cells, and
preserve the charged frontier.

### Artifact paths

- `src/implicit_pair_state_index.py`
- `src/verify_implicit_pair_state_index.py`
- `development/IMPLICIT-PAIR-STATE-INDEX-V1/RUN-001/`
