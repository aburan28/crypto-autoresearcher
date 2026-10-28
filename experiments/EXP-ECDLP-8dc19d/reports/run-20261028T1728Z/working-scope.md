# Working-domain scope and matched baseline

The frozen eight-circuit transfer trial recorded 226 independently verified success events across 80,256 candidate attempts, covering 181 target/arm pairs. Nineteen of 320 candidate curve/arm cells had an observed recovery; all 301 zero-success cells remain in the census. The working BSGS reference recovered every one of the 2,508 public targets.

A concrete working domain is F_23, y²=x³+11x+5, with P=(5, 22), group order 17. Fixed circuit2 uses alpha=-2, beta=-1 and known-base multiplier a=1. It produced 40 verified recovery events in 64 fresh blinded attempts, recovering all 16 original target IDs at least once within the registered four attempts per target. The registered pointwise Wilson interval for 40/64 is [0.502503786840045, 0.7333401982117536].

The separate validator-only exhaustive retained-bit recovery census is 8/16, q=1/2, with zero fresh constructor calls. This diagnostic is distinct from the 40 fresh primary recovery events. Its full half-bit ordering test has two truth mismatches; the universal ordering gate is false. Sixteen registered odd-anchor null functions have exact rates 0 or 1/2 on this domain (four of sixteen at 1/2); these are descriptive validator controls, not extra algorithm executions or a tail-probability test.

| Registered tier | Curves | Candidate cells | Attempts | Verified events | Unique target/arm pairs | Positive cells |
|---|---:|---:|---:|---:|---:|---:|
| exact-r127 | 2 | 16 | 8064 | 117 | 100 | 2 |
| exact-r17 | 2 | 16 | 1024 | 40 | 16 | 1 |
| exact-r29 | 2 | 16 | 1792 | 36 | 32 | 3 |
| exact-r61 | 2 | 16 | 3840 | 19 | 19 | 3 |
| sampled-r10 | 16 | 128 | 32768 | 13 | 13 | 9 |
| sampled-r13 | 16 | 128 | 32768 | 1 | 1 | 1 |

On that r=17 domain, the empirical cold model S+mean(online)/qhat is 3587/40=89.675 emitted group-add calls. Matched BSGS is 188/16=11.75 group-add calls. The observed candidate batch ratio is 3314/40=82.85 calls per success event. These are same-family source counter comparisons; all field, inversion, scalar, RNG and bookkeeping vectors remain separate. Common cohort/input construction and independent validation are retained once separately. No qualified runtime, exhaustive machine price or asymptotic exponent is inferred.

The attached successor-working-domain-supplement.json indexes all nineteen positive cells with exact paired cold-cost fractions, while the original census and readable report retain every fixed cell and undefined zero-success ratio. Empirical zero successes do not establish zero population probability. This is a descriptive working-domain index, not a selected confirmatory test.

