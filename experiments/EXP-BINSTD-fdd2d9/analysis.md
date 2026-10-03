# Analysis: EXP-BINSTD-fdd2d9 (H-BINSTD-f9fa00) Stages 0–1

Review plan: `experiments/EXP-BINSTD-fdd2d9/review/review-plan.yaml`
(`REVIEW-BINSTD-fdd2d9-20261003`), written before this analysis.
Producer: `TASK-20261003-c9329a`. Snapshot: `TASK-20261003-11b469`.
Spec approval: `DEC-20261003-2e4a60` (immutable). Exec admit:
`DEC-20261003-6c2db4` / `AMD-EXP-BINSTD-fdd2d9-20261003-exec-admit`.
Decision target: **support** on integer catalog-count agreement only.
O-SUPPORT does **not** transfer to encoding or ECDLP. No break; no
exponent; no n≥131 transfer; no Bedrock/AUXIN. No scientific re-run
this tick. No sibling reviews existed when the prior was recorded.

## Observation

**Validity (J1).** Two run directories under `runs/`:
`RUN-BINSTD-51ad99` (Stage 0, difference route) and `RUN-BINSTD-e55dcf`
(Stage 1, product route). Each has `manifest.yaml`, additive
`manifest_v2.yaml`, `raw-result.json`, `certificate.yaml`,
`environment.json`, `command.txt`, `execution-receipt.json`, stdout/stderr
logs, and `check.stdout.log` = `PASS`. Both receipts:
`status: output_validated`, `check_returncode: 0`, `returncode: 0`.
Receipt `artifact_sha256` matches on-disk bytes for every named file.
`n_runs=2` equals `maximum_runs=2`. Trial-plan `source_sha256` and
`specification_sha256` match current implementation and specification
bytes. Amazon Bedrock not used. Certificates: `kind: integer_catalog_check`;
`discrete_log: false`; `decomposition: false`; `key_recovery: false`;
`encoding_run: false`. Producer claims: `break: false`,
`exponent_move: false`. Supervisor package: required=2,
output_validated=2, measurement_complete=true.

**Stage 0 (J2 freeze).** `RUN-BINSTD-51ad99` raw-result:
`outcome: O-STAGE0-OK`, `route: difference`, `stage: 0`,
`encoding_run: false`, `implementations_agree: null` (Stage 0 does not
yet compare routes). Freeze artifacts
`stage0/preregistered-predictions.json` and `stage0/v-catalog.json`
present. Catalog values: `ell_product=12`, `hundredths_excess=20`,
`slots=72`, `catalog=12` (not 9), `n_sum=59`, `n_product=null` on the
difference route by design.

**Stage 1 (J2 agreement).** `RUN-BINSTD-e55dcf` raw-result:
`outcome: O-SUPPORT`, `route: product`, `stage: 1`,
`hundredths_excess: 20`, `excess_product: 80`, `n_product: 7429`,
`slots: 72`, `ell_product: 12`, `implementations_agree: true`,
`encoding_run: false`. `stage1/control-table.json`:
`implementations_agree: true`, `independent: true`,
`import_audit.difference_imports: ["__future__"]`,
`import_audit.product_imports: ["__future__"]`. All `agree_keys` match
across difference, product, and expected maps. `stage1/panels.json`
repeats the two value maps and `outcome: O-SUPPORT`. `RESULTS.md` names
exactly one O-* label: **O-SUPPORT**.

**Route independence (J2).** AST parse of `route_difference.py` and
`route_product.py` (review, not a trial): each imports only
`__future__`. Neither imports the other.

**Blind integer re-derivation (J3).** Computed without importing either
route module and without reading RESULTS.md summaries as inputs:

| quantity | expression | value |
| --- | --- | --- |
| ell_product | 3×4 | 12 |
| hundredths_excess | 70−50 | 20 |
| catalog_quot | 12÷3 | 4 |
| excess_product | 20×4 | 80 |
| slots | 6×12 | 72 |
| n_sum | 17+19+23 | 59 |
| n_product | 17×19×23 | 7429 |
| gap_product | 2×4 | 8 |
| span | 23−17 | 6 |
| cross_two_thirds | 7×3 − 10×2 | 1 |
| cross_three_fifths | 7×5 − 10×3 | 5 |

These match Stage-0 freeze values, Stage-1 control-table expected /
difference / product maps, and both run `raw-result.json` value maps
(with Stage 0 `n_product` left null as specified).

**Scope / non-claims (J4).** RESULTS.md: `encoding: not run`,
`n>=131 transfer: not claimed`, `break: false`, `exponent_move: false`,
`Amazon Bedrock: NOT_USED`. No Spearman, XOR-SAT, or encoding artifact
is present.

## Comparison

Against H-BINSTD-f9fa00 / EXP-BINSTD-fdd2d9 success and falsification
criteria (DEC-20261003-2e4a60):

- 3×4 catalog / ell_product = 12: **holds** on both routes.
- 6×12 slots = 72 and 72÷12 = 6 = hour cap: **holds**.
- 70−50 hundredths_excess = 20: **holds** (falsifier was agreement that
  the difference is computed and is not 20 — not observed).
- 20×4 excess_product = 80: **holds**.
- n list 17,19,23 sum 59 product 7429: **holds** (product on the
  product route only, as specified).
- Two arithmetic routes, no mutual import: **holds**.
- Encoding run: **false** (required).
- Catalog reported as 9: **not observed**.
- O-FAIL / O-ARTIFACT / O-IMPEDIMENT: **not met** (runs completed;
  check PASS; integers agree).

The producer O-SUPPORT label matches the frozen success criterion as
integer catalog-count agreement. It does not match, and is not compared
to, any encoding-size or ECDLP prediction.

## Inference

The Stages 0–1 package is valid. Independent integer re-derivation and
twin-route agreement support the scoped arithmetic claim of
H-BINSTD-f9fa00 at the locked toy catalog (n ∈ {17,19,23}, dimensions
3 and 4, catalog floor 12, bound 70 hundredths). Official decision:
**support** on that integer claim only. Evidence strength:
**preliminary** (first observation of this EXP; two designed routes in
one session; PD-1 no independent validator). Hypothesis
approved→analyzed. Hypothesis is **not** moved to `supported` (that
status would over-read toy arithmetic).

O-SUPPORT is integer catalog-count agreement only. It is not an
encoding result, not an ECDLP claim, not an exponent move, and not a
KN-FIND.

## Limitation

- Toy integers only; no field arithmetic beyond listing n=17,19,23.
- No encoding, subspace sweep, rank correlation, or Spearman panel was
  run under this card. Absence of encoding is a scope bound, not a
  null encoding result.
- Two routes are the protocol’s designed pair (`independent_instances: 2`),
  not a second-campaign replication; strength stays preliminary.
- No independent validator/red-team (PD-1).
- Certificate kind is observational `integer_catalog_check`, not a
  discrete-log or decomposition certificate.
- Transfer of these integers to encoding size, usable_dimensions, rho,
  or n≥131 is UNVALIDATED and is an explicit non-claim.
- DEC-20261003-2e4a60 is not rewritten. No scientific re-run this tick.
