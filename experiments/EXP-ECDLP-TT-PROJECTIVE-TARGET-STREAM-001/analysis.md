# Analysis: streaming target-cache rank extension

## Result

Status: `MIXED POSITIVE SIGNAL`, `TOY-EVIDENCE`, `MODEL-BOUND`.

The corrected projective implementation processed `3B+1 = 43` generated
targets plus four held-out targets on the fresh 16-bit curve
`p=62071, q=62137` at seed `86420`. Both `source_prf_x` and `random_x`
reached rank `15/15`. Exact support, full-budget witnesses, matched rho, and
the weighted arithmetic comparator all passed. The candidate beat the matched
comparators in `2/2` weighted cells.

The streamed target-local cache kept peak RSS at `4,458,496,000` bytes,
below the strict `6,442,450,944` byte (6 GiB) gate. The run took
`1,532.675` seconds wall time and `1,364.312` CPU seconds, with
`223,916` matched rho group operations. This is a memory/rank systems result,
not an exponent result: the run still performs a large explicit relation
enumeration and does not include a deployment-scale individual-log descent.

## What changed

The shared source-orbit cache remains resident, while target-local predicate
and original-lift values are reset for each target. This permits the larger
rank-completion batch without retaining all target caches simultaneously.
The projective binding is checked by the verifier through nonzero
`projective_predicate_field_multiplications` and `paired_projective_calls`.

## Evidence

- Generator: `RUN-TT-PROJECTIVE-TARGET-STREAM-005`, raw-result SHA-256
  `b2f0ba504f6e4ab0fd8cac5b85050706862af67d52d508eba5595e6c9178072c`.
- Independent verifier: `RUN-TT-PROJECTIVE-TARGET-STREAM-006`, raw-result
  SHA-256 `c1e8fa65676240f540d2a5ca004c9c2c9b49bdefd9601d8c749ff1f77d211714`.
- Verifier result: `valid=true`, `rank_gate=true`, weighted cells `2`, peak
  RSS `4,458,496,000` bytes.

## Interpretation

This resolves the immediate second-curve rank question for a streamed cache:
the candidate family and the random control both reach full toy rank when the
target pool is expanded. It does not show that the relation density is
generic, that target generation is sub-rho, or that the total charged cost
beats rho. The earlier second-curve `2B+1` run remains useful as a negative
control because it found only `13/15` rank for `random_x` while using the
larger retained-cache representation.

The next bottleneck is therefore compressed relation generation: preserve the
projective predicate and its arithmetic accounting while replacing the
explicit target-by-target scan with a source-aware selector, transposed
row-space operator, or non-enumerative zero locator. Any successor must charge
cache bandwidth, sparse linear algebra, target descent, memory, and matched
rho on at least three sizes.

## Claim boundary

No generic prime-field ECDLP break, asymptotic improvement, fixed-curve
preprocessing frontier improvement, or deployed-key recovery is claimed.
