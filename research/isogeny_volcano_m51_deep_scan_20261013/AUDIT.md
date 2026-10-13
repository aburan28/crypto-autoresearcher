# Post-run audit record

This is an additive audit of the sealed discovery result. No frozen input,
scientific output, certificate, receipt, or manifest was modified.

## Directly repeated checks

| Check | Observation | Result |
| --- | --- | --- |
| Frozen-input manifest | All 16 entries in `FROZEN.sha256` matched; the copy inside the run is byte-identical | PASS |
| Sealed root manifest | 1,665/1,665 listed entries matched | PASS |
| Archive identity | Extracted `run1.tar.zst` is byte-for-byte identical to the sealed tree | PASS |
| Archive manifest | 1,665/1,665 extracted entries matched | PASS |
| Coverage | 256/256 shards complete and scientific-eligible; union is `[0, 3,600,000,000)` | PASS |
| Process outcomes | 256 shard exit codes were zero; zero timeouts and zero cancellations | PASS |
| Aggregate | 42 unique sorted hit ranks; aggregate hash matches its receipt | PASS |
| Classification | 42 records and 42 pairs; all 42 are `CERTIFIED_BOTTOM_PARENT` | PASS |
| Controls | 21/21 expected labels observed, including all 16 `f_E=271` exclusions and three positive controls | PASS |
| Global selection | Valid, 32/32 selected, 32 distinct parent and bottom orbits, cutoff `2,531,725,702` | PASS |
| Fail-closed policy | Zero admitted failures seen, zero admitted failures selected, zero blocking failures | PASS |
| Transfer boundary | All 42 certificates set evaluator, dual, and transfer permission to zero | PASS |

Uniform-field rechecking across the 42 per-hit certificates produced exactly
one value for each of the following: source order
`2,251,799,852,369,764`; `f_pi=32,756,041=271*120871`; source
`f_E=32,756,041`; target `f_E=120,871`; orbit sizes 51 and 51; degree 271;
separable 1; direction `ascending`; evaluator 0; dual 0; transfer permission 0.

The coordinating session also received two independent discovery-audit PASS
reports. Together they reported re-counting all 84 endpoints with GP and an
independent `GF(2)` orbit/PRP/sieve replay. Those reviews are summarized here;
they are not represented as extra files inside the immutable scientific run
or as evidence of an executable transfer.

## Selection audit

The first selected global rank is `2,279,805`; the 32nd is
`2,531,725,702`. The convenience CSV has one header plus exactly 32 rows and
matches the order and fields in `results/selection.json`. Ten later certified
hits remain in `results/pairs.jsonl` and the full archive; they were not erased
or used for outcome-dependent backfill.

## Scope of PASS

These checks validate execution integrity, exact artifact binding, endpoint
certification, and the frozen selection rule. They do not test an evaluator,
dual, subgroup transport, recovery, unknown-scalar solving, or comparative
ECDLP work. Therefore no `weak curve`, `source-transfer-weak`, or
`no weakness found` label follows from this discovery audit alone.
