# External ECDLP idea corpus — non-canonical dedup input

**Status: pointer index only. Nothing here is an allocated idea, a canonical ID,
a contract, or approved evidence.** No row in this file has passed this program's
deduplication or red-team review, and only the Coordinator may allocate an ID or
change an official state. The file exists so that the Idea Generator and the
dedup pass can screen *against* an external corpus instead of rediscovering or
duplicating it.

The external work lives in a separate workspace (`/Volumes/Volume/research/`) and
was produced outside this repo's ledger, contract, and run-receipt discipline.
Paths are recorded verbatim so a reviewer can read the primary bytes.

## Why this is not a bulk import

The canonical corpus already spans IDs `001`-`410` with 17 active, 27 deferred and
366 rejected records, all screened by named dedup and red-team passes. Minting IDs
for externally-generated mechanisms without those passes would (a) bypass the
review gate and (b) very likely re-create existing rejections — the external
catalogue below was mined against a different taxonomy (R6/K1/K2/Defect-B/CM
cells) and has substantial expected overlap with existing scoped negatives.
Screening is a Coordinator-run operation, not a file copy.

## Pointer index

| External source | What it holds | Relevance here |
|---|---|---|
| `ECDLP_MECHANISM_CATALOG.md` | ~111 prime-field mechanisms mined from an external corpus, mapped to R6 / K1 / K2 / Defect-B / CM cells | **Largest unscreened input.** Candidate generation + dedup screening against IDs 001-410 |
| `LIT_REVIEW_PRIME_FIELD_ECDLP.md` | 23-paper review, 8 field cards, dedup tags | Literature cross-check for `knowledge/literature`; names three untouched gaps: syzygies/Betti, singular loci of the Semaev ideal/variety, and Yokoyama semi-normality (flagged there as the top F_p test) |
| `ISOGENY_SEMAEV_REVIEW.md`, `isogeny-semaev/` | Four-channel isogeny x Semaev sweep, alpha-stable factor bases, GLV/CM orbit folding, scaling study | Captured as [KN-FIND-007](../knowledge/findings/KN-FIND-007.md), [KN-FIND-008](../knowledge/findings/KN-FIND-008.md) |
| `POLLARD_RHO_FRONTIER.md` | Six-lens adversarial survey of rho improvements (0 live / 9 capped / 17 dead) | Captured as [KN-FIND-009](../knowledge/findings/KN-FIND-009.md); baseline accounting for KN-OPEN-001 |
| `ecdlp-autolab/PKM_ANALYSIS.md` | Prime-field index-calculus analysis (incl. P-521/P-256 scope, bounded d_reg) | KN-OPEN-001 / KN-OPEN-002 prior art |
| `ecdlp-autolab/P256_HIDDEN_STRUCTURE.md`, `P256_FORMAL.md` | P-256 five-routes note; End = O_K and k = (n-1)/3 proved + certified; weak-neighbour definition, JMV reduction | Curve-specific structure claims with machine-checked certificates |
| `ecdlp-autolab/SAT_VS_GB.md` | SAT vs Gröbner solver comparison for ECDLP systems | Alternative-solver lane for KN-OPEN-002 |
| `ecdlp-autolab` (ML-guided policy) | Learned triage + Gröbner ordering; decomposition signal real at n=8, gone by n=10 | Negative scaling result for learned heuristics |
| `EC_SIEVE` last-corner probe | Non-algebraic predicates pushed to d = 8,16,32,64 via Walsh/linear correlation; signal ~1e-3 flat, no growth | Closes a sieve-predicate corner; no entry here yet |
| `QUANTUM_CIRCUITS.md` | Shor-on-ECC circuit review; inversion is the bottleneck | Out of scope for the classical program; recorded for completeness |
| `ecdlp-cost-challenge/research/rho96/` | Checkpointed 96-bit rho attempt, stopped at ~7.2%, `solved 0` | Operational baseline cost datapoint (see KN-FIND-009) |

## Suggested screening order

1. `ECDLP_MECHANISM_CATALOG.md` — highest volume, highest duplication risk.
   Screen cell-by-cell against the rejected corpus before any ID allocation.
2. `LIT_REVIEW_PRIME_FIELD_ECDLP.md` gaps — the syzygies/Betti and singular-loci
   items are adjacent to [KN-FIND-006](../knowledge/findings/KN-FIND-006.md),
   whose open question is exactly a Betti-number count; semi-normality is
   currently near-absent from `knowledge/`.
3. The remaining rows are already summarized as findings or are out of scope.

Nothing in this file is a breakthrough, a promotion, or a claim that any listed
mechanism works.
