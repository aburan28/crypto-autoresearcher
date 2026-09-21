# Red-Team Review: Target-Conditioned Pair Index V1 RUN-001

## Scope

This review tests whether the exact pair-index result can be misread as an
ECDLP improvement or whether the accounting omits the cost that makes the
index possible.

## Findings

1. **No generic ECDLP claim is supported.** The input contains generated toy
   curves at `q in {953,3919,15583}` and four registered coordinate families.
   There is no relation-matrix, individual-log, or optimized-rho campaign.
2. **The pair index is not D2-scale advice.** Every unordered D2-state pair
   and every witness product is retained. The four source indices per record
   are included in advice, so the query win cannot be read as a compressed
   fixed-curve compiler.
3. **Fingerprint collisions are not free.** Widths 1, 2, and 4 generate
   substantial rejected-candidate replay. Those additions are included in
   online work; width 8 is nearly exact and correspondingly gives little
   compression.
4. **The target conditioning is genuine but narrow.** The query computes
   `C=T-A` and uses its nonlinear coordinate fingerprint to select a bucket.
   It does not remove the offline pair-sum enumeration or source-witness
   payload.
5. **The exactness control is sufficient for this preflight.** The independent
   verifier reproduces all rows byte-for-byte after runtime fields are
   normalized and rejects all five mutations.

## Disposition

`SCOPED NEGATIVE` for this explicit pair-sum/fingerprint representation.
Preserve the code and receipt as a baseline for an implicit or compositional
successor. Do not promote the exact pair-index online work to an exponent
claim, since advice and pair construction dominate the charged frontier.
