# Red-team review: streaming target-cache rank extension

## Disposition

The corrected receipt is semantically valid for the stated toy experiment.
It should be promoted only as a memory/rank systems signal. It is not a
cryptanalytic break or a demonstrated improvement over the square-root
frontier.

## Checks that passed

- The verifier regenerated the 43 generated targets and four held-out rows.
- Both target families reached rank `15/15`.
- Full-budget support and witness checks passed.
- Projective counters were nonzero, preventing the earlier affine-binding
  false positive from being accepted as projective evidence.
- Weighted arithmetic advantage held in `2/2` cells.
- Peak RSS `4,458,496,000` bytes stayed below 6 GiB.
- Matched rho solved all cases.

## Remaining objections

1. The experiment is one fresh 16-bit curve. Full rank at this dimension does
   not establish a density law or a scalable factor-base relation compiler.
2. The candidate still enumerates a large explicit relation surface. Streaming
   reduces retained memory; it does not by itself reduce the dominant relation
   work or establish an exponent below one half.
3. The weighted comparator is an arithmetic sub-cost. Wall time, CPU time,
   cache bandwidth, relation filtering, matrix elimination, and target descent
   must be charged together before any end-to-end claim.
4. The held-out rows validate support and witnesses, not an individual-log
   algorithm for arbitrary targets at cryptographic sizes.
5. The previous stream receipt was produced before projective predicate binding
   was repaired, and the first verifier accepted it too broadly. Those
   artifacts are preserved as implementation-audit evidence and must not be
   pooled with the corrected result.

## Required successor gate

Run at least three sizes with fresh ordinary prime-order curves and both the
source-derived family and a randomized negative control. Require exact
support, independent verification, full rank, held-out descent, explicit
memory/bandwidth accounting, sparse linear algebra, and matched rho. The
candidate must show a fitted total exponent below `0.5` before any generic
break language is considered.

## Handoff

### Claim or task
Replace the explicit streamed target scan with a compressed projective
relation locator while preserving the verified rank and support gates.

### Status
OPEN

### Assumptions
- Ordinary prime-order prime-field curves.
- Projective shared-sign predicate remains algebraically exact.
- Compression can avoid materializing the full target-local relation surface.

### Evidence so far
- Corrected 16-bit run reaches full rank for both target families with 2/2
  weighted wins and peak RSS below 6 GiB.

### Failure modes
- Compression loses support or rank; bandwidth or sparse linear algebra
  dominates; the relation exponent remains at or above rho.

### Next concrete action
Implement a source-aware sampled/transposed locator and compare its fully
charged cost against the corrected streaming baseline on three fresh sizes.

### Artifact paths
- `runs/RUN-TT-PROJECTIVE-TARGET-STREAM-005/raw-result.json`
- `runs/RUN-TT-PROJECTIVE-TARGET-STREAM-006/raw-result.json`
