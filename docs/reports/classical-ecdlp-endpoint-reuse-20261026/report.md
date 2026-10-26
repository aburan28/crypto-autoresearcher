# Endpoint reuse: read-only mechanism and prior-work audit

Date: 2026-10-26. This report records source inspection, retrieved literature, and derived algebra. No experiment, benchmark, new scalar recovery, independent scientific review, or ledger transition was performed.

![Proposed bounded admission flow, with public verification before reuse. This is algebra-derived dataflow, not measured performance.](mechanism.pdf){width=95%}

## What is already known or tested

| Source | Observed scope | Consequence for the next experiment |
|---|---|---|
| Kuhn and Struik, SAC 2001, section 4, pp. 218-219 | After a target log is known, its earlier distinguished points acquire known logs and can help later targets. The iteration must be independent of the target. | Basic endpoint recycling is established prior art. |
| C precomputation source, pinned cryptanalysis revision | pc_table_solve takes a const table; unsuccessful online endpoints are discarded. | Monotone post-verification admission is a new implementation change relative to this measured C baseline. |
| Rust batch-rho source, rho_batch_with, same revision | Actual EC batch rho already stores target-tagged distinguished points and uses a publicly verified earlier scalar in later collision equations. | Do not describe cross-target verified-point reuse as absent from the repositories. This is a related existing baseline, rather than the proposed precomputed-BL variant. |
| H-ECDLP-37dc01 / EXP-ECDLP-612fb1 | Weighted reselection: solved walks enlarge a working pool, followed by top-T selection using length-plus-count weights. | Distinguish this from append-only growth with one hard capacity. |
| EV-ECDLP-60e266 | At a=1/4, a reselected T/2 table failed to match static T on the tested generic instruments and one toy EC arm. | The specific half-advice equal-coverage claim must not be retested as an unexamined premise. |
| EV-ECDLP-f6b3f5 | Generic-instrument support at T_sel=0.65T or 0.75T is preliminary, with an inadequate attribution null and working storage above advice size. | Related positive observations remain, but do not establish the proposed complete-cost result. |
| H-ECDLP-32fad8 / EXP-ECDLP-1de2ec | Nineteen Stage-1 generic runs include capped/uncapped growth, relation connectivity, and controls at N=2^24. The implementation states EC Stage 4 was not implemented or executed. | The hypothesis's still-specified status is not evidence that nothing ran. These proxy fractions are not verified EC recoveries. |

The atlas lead LEAD-RHO-advice-table-variants has disposition open_next_step. Its forecloses list is a set of prior-work matching phrases, not a blanket mathematical rejection. The completed generic growth pilot used a target-owner/solved-flag connectivity model and certificate kind none; it did not implement the EC affine scalar relations advertised by the broader hypothesis.

The narrow next study is therefore an independent actual-EC implementation and matched complete-cost comparison: a static small BL table, static full-capacity BL table, and a small table that admits failed online endpoints only after a public scalar check. It uses monotone admission without a weighted candidate pool, reselection, unknown-log entries, or relation union-find. This is a follow-up to the cited work; novelty of the generic reuse mechanism is not claimed.

## Derived correctness invariant

For prime subgroup order r, base P, target Q=xP, and a point-only walk adding known multiples of P, maintain Y=Q+aP. An unsuccessful distinguished endpoint D_j has its own saved offset a_j. After the solver has publicly verified xP=Q, it follows that D_j=(x+a_j)P. Its reusable log is e_j=(x+a_j) mod r. A later target Q' reaching D_j with offset a' gives the candidate x'=e_j-a' mod r, which is checked against Q'.

These are algebraic consequences of the stated invariant, not new experimental findings. They require the same group, base, walk increments, distinguished-point predicate, and point canonicalization throughout the batch. If negation or another quotient is added, its scalar sign/action must be propagated as part of the invariant.

Implementation conditions:

1. Admit only actual distinguished endpoints, not non-DP chain-limit exits.
2. Save the offset at each terminal before restarting; do not reuse the final successful walk's offset for earlier terminals.
3. Verify the target scalar before promoting any pending record. Failed or censored targets do not create known logs.
4. Fingerprints are lookup hints. Hash collisions must still lead to a full target-equation check and a retained failed attempt, never to an accepted false scalar.
5. A table with zero known entries cannot bootstrap under verified-only admission unless a separately charged solver supplies the first verified log. Unknown-relation growth from H-ECDLP-32fad8 is a different algorithm.

## Fair comparison and a real memory cap

A cap on final known entries does not bound peak memory if a separate pending buffer or oversized selection pool is omitted. A possible implementation uses one C-slot arena of (fingerprint, scalar) records: a sorted known prefix followed by pending (fingerprint, offset) records. Lookups see only the known prefix. Admit pending records only while known plus pending is below C; after verification, translate offsets to logs and sort/deduplicate in place. On failure, discard the pending tail. Any sorting allocation must be counted or avoided.

The arena is only one component of memory. Report jump tables, fixed-base powers, point/operation objects, stack, allocator capacity, output buffering, pending duplicates, rejected insertions, and process RSS or the exact missing measurement. Count the complete setup and target API, public checks, restarts, lookups, updates and verification; group-operation counts do not price sorting and hashing by themselves.

Hold initial table construction, walk parameters and target order fixed in paired arms. Compare adaptive C0-to-C with both static C0 and static C. Report complete cumulative prefixes, including the early-target penalty and failures. A disabled-admission control should be identical to the static small arm. Repeated public targets must remain visible: their deterministic restart streams can give legitimate cache benefits that differ from fresh-target generalization.

Under ideal independent uniform walk starts, failed endpoints sample basins outside the current known set, with size bias. Static precomputation already has size-biased endpoint discovery. Better full-capacity coverage is therefore not assumed; the plausible gain is reuse of already-paid online work instead of additional dedicated precomputation.

## Scaling boundary

The repository's preprocessing frontier KR-RHO-ea34b8 states S*T^2 approximately proportional to r, with success and logarithmic factors suppressed. Conditional on that frontier, S=r^(1/3) gives T=r^(1/3); T=r^(1/4) would instead require S=r^(1/2), a different access model, or additional structure. A growing batch can also lower per-target cost under the established multi-target law; its target count, memory and total work must remain in the accounting. A constant-reuse finite comparison does not identify a new exponent.

This audit retrieved Kuhn-Struik's primary section on reuse. It did not independently re-prove the preprocessing lower bound or read the complete Corrigan-Gibbs-Kogan paper. The frontier statement above remains attributed to the repository record and its recorded verification depth.

\newpage

## Decoder context from the existing completed run

RUN-ECDLP-dba66e records 3/768 candidate-only hits, with 765 rho fallbacks. Existing aggregate intervals give setup 0.275634341 CPU seconds and prefix work 0.679317749 CPU seconds. Their derived sum is 0.954952090 seconds, already above the paired standalone rho total 0.308699 seconds. Holding that prefix cost fixed, increasing recovery alone cannot produce a cheaper complete solver on this workload.

The exact-prefix search calls advance independently for two sibling bits, and advance recomputes the same doubled point. Caching the four doubled view points per parent would change 12 group calls to 8 when both bits are legal, saving exactly four calls per such parent. It preserves points, feature labels, RNG, tie ordering and candidate lists. This is an unmeasured implementation optimization, ordinary memoization, and does not improve recovery. The current beam's long suffix scores are formed from powers of fitted one-step feature kernels; fitted-model contraction explains a possible ranking bottleneck without proving anything about true EC dynamics.

## Provenance and next checks

Internal sources were read from the current local repository and exact copied records; their byte hashes are listed in audit.json. Search covered the named atlas records, C baseline, Rust batch-rho implementation, previous growth/reselection records and targeted GitHub code searches across the three repositories. The read-only knowledge-index tools were not exposed in this session; source inspection and exact Git records were used. Search coverage is bounded, not all branches or all literature.

Both cryptanalysis implementations are pinned to commit 379faa0f1e38facd9c8fdfc527f0b89518cf2e70. The Rust function is in suite/src/cryptanalysis/ic_boundary.rs; the C function is pc_table_solve in src/precomp.c.

Primary source read: [Kuhn and Struik, Random Walks Revisited](https://tik-db.ee.ethz.ch/file/24d4a86d39ea8fae126fc84b69885ba7/), sections 2-4 through the reuse construction; bibliographic metadata from [Springer](https://doi.org/10.1007/3-540-45537-X_17). The BL baseline constants were checked against the authors' [publication abstract](https://research.tue.nl/en/publications/computing-small-discrete-logarithms-faster-2/); primary full-PDF retrieval attempts are retained as failures in primary-source-retrieval.json. No source is silently upgraded to a full-paper read.

Next checks are prospective: test the invariant and forced fingerprint collision handling; certify hard-cap behavior including pending records; freeze a fresh EC cohort and target order; compare all complete costs and failures; and keep the previously contradicted half-advice claim outside the new study's asserted premise. No canonical graph or ledger conclusion changes in this audit.

