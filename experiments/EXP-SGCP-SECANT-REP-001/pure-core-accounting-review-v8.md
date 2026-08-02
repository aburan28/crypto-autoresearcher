# Handoff: Pure-core V8 accounting review

## Claim or task

Review operation-count invariance, accounting boundaries, and V8 authorization
closure at exact commit `b672372fb6e810fa129f288ae0bca406cf5ace53`.

## Status

`OPEN` - `REVISE`.

## Assumptions

- Reviewed tree: `5227118bb4e70d0ac446b642c7b40feaf6ccfe71`.
- Reviewer principal: `019fac07-155f-7f61-82f6-a0c88ee84193`.
- Review was static only; no source or experiment action was performed.

## Evidence so far

- V7 mathematics is unchanged.
- Independent recounting reproduces the complete successful-call totals:
  58 additions, 156 subtractions, 151 multiplications, 76 squarings,
  24 negations, 18 inversions, 24 membership checks, 21 pair additions,
  12 secants, 6 tangents, 3 vertical exclusions, and 18 witnesses.
- The counters are explicitly development metadata, not process costs, bit
  complexity, memory, relation collection, linear algebra, target descent, or
  cryptanalytic evidence.
- The V8 trusted-local model is proportionate to the singleton reversible action
  and preserves `maximum_runs=0`.

## Failure modes

- V8 retains a V7 receipt schema that cannot bind fresh V8 reviews.
- The hard-coded V7 red-team GO JSON is absent, while the retained V7 red-team
  Markdown review says `REVISE`.
- A later decision therefore cannot prove the V8 review gate without replacing
  immutable evidence or departing from the exact schema.

## Next concrete action

Create a fresh immutable review-receipt schema and decision-reference array
binding the revised exact commit, tree, consistency digest, trust-model digest,
authorization digest, role, verdict, and distinct reviewer principal.

## Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/pure-core-design-consistency-v8.json`
- `experiments/EXP-SGCP-SECANT-REP-001/authority-trust-model-v8.json`
- `experiments/EXP-SGCP-SECANT-REP-001/source-authorization-amendment-v8.json`
