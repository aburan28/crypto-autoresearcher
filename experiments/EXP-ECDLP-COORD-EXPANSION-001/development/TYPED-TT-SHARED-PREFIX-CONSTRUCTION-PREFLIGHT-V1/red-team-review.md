# Red-Team Review: TYPED-TT-SHARED-PREFIX-CONSTRUCTION-PREFLIGHT-V1

## Verdict

Accept as a constructive toy target-sharing observation. Do not promote it to a fixed-curve attack or ECDLP improvement.

## Objections and responses

1. **The skeleton is discovered from a fully materialized base tensor.** Correct. This is the dominant unresolved cost. The specialization ratio cannot be treated as an attack cost until discovery is compiled and charged.

2. **The basis was selected from one target and tested on eight relation targets plus one held-out target.** This is useful evidence, but it is still one frozen seed and one target schedule. Fresh curves, fresh factor bases, random target batches, and larger batches are required.

3. **The selected-column specialization formula is not yet a complete TT core chain.** Correct. It is an exact cut-3 matrix skeleton, not a full five-mode reusable TT compiler. The missing left/right interface, normalization, and witness-bearing zero selector remain substantial.

4. **The 45-60% saving is a constant-factor tensor application saving.** Correct. It is not an exponent improvement and may disappear once persistent advice, coefficient generation, memory bandwidth, and relation/linear-algebra costs are charged.

5. **Held-out exactness is not relation success.** Correct. The held-out point is only a tensor reconstruction check; no quotient rank or individual-log witness was recovered by this experiment.

## Required follow-up

Run a fresh-seed batch sweep with target counts `1,2,4,8,16`, construct the basis without full target enumeration, and bind the resulting shared operator into the existing typed relation and descent verifier. Reject any claim unless all offline, advice, online, relation-rank, and target-descent costs are included.
