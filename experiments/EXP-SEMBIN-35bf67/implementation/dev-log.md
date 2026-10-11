# Development log (instrument construction, before the Stage-1 gate)

These are development/debugging tests run in the session scratchpad while the
instrument was being written. They are NOT experiment runs, produced no Stage-1/2/3
artifacts, and none of their outputs is evidence. Recorded here so that no attempt is
omitted. All ran after the Stage-0 freeze (stage0/FREEZE.json, 2026-10-05T05:20:28Z).

| # | what | outcome |
|---|---|---|
| D1 | M4RI release-20240729 (d0a1ee18) source build; `make check` | 15/15 tests PASS |
| D2 | DREG n=15 rebuild, Sage-default guesses (Conway modulus, lift_x y asc/desc, 2^3 sign flips) | no system_hash match (16 variants) |
| D3 | exhaustive R_X search (2^15 values) x {Conway, minimal-weight} moduli, B = alpha | no match |
| D4 | same search with equation-order variants (reversed / swapped coefficient blocks) | no match |
| D5 | same search with variable indices reversed (PolyBoRi degrevlex) | MATCH: Conway modulus, R_X = 24959; the seeded sample (y ascending, no flips) gives exactly R_X = 24959 |
| D6 | n=18 rebuild with the D5 conventions | system_hash b8bec47d... MATCH (recorded n=18 anchor hash) |
| D7 | calibration 3000x4000 rank 2500 (+ injected deficiency), both arms | 2500 / 2499 on both arms |
| D8 | calibration 20000x30000 rank 17000 (+inject), both arms | 16999 both, identical trajectories |
| D9 | S-A vs S-B vs naive vs Gray-code exhaustive, (12,2,2,6), (12,3,3,4), (13,2,2,7), 6 instances each | all solution sets identical |
| D10 | Gray-code exhaustive vs naive on null systems incl. truncated (3 / 6 equations; up to 2.1M solutions) and prefix split T=4 | identical in all 45 cases |
| D11 | closure, tiny cells (12,2,2,6), (14,2,2,7), (12,3,3,4), (16,2,2,8), early-stop vs full fixpoint, both arms | arms identical (trajectories + digests); full-fixpoint codimension = s in every case |
| D12 | first closure implementation read low rows lazily within a round; changed BEFORE any recorded run to snapshot low rows at round start (OP-R4 wording) | code change only |
| D13 | timing probe (30,2,2,15) dev instances 0-2, both arms | SOLV4 in all; 7-12 s per arm |
| D14 | timing probe (40,2,2,20) dev instance 0 (s = 0), both arms (sub-chunk A 8192 / B 2048) | SOLV4 (dim R_4 = 102,091), 3 closure rounds, 396 s (A) / 336 s (B), peak RSS 1.04 / 0.68 GB |
| D15 | DREG n=15 anchor, transposed Macaulay D=5 rank, both arms | 69,073 both; nrows 74,880; support 143,421 |
| D16 | kernel tuning at (30,2,2,15) dev instance 0: sub-chunk 1024-8192, arm-B column block 16-128 words, AVX-512 width flags | chose sub-chunk A=2048, B=1024, block 32 words; 512-bit vector width gave no gain (not adopted) |
| D17 | per-phase timers added to solv4.c (reporting only) | time split ~45% reduce product, ~38% RREF-maintenance product |

Dev instances used the stage tag "dev" (seed namespace disjoint from "stage1-*" and
"stage2"/"stage3"), so no dev instance is reused in any recorded run.

## After the Stage-1 engine gate and builder check

| # | what | outcome |
|---|---|---|
| D18 | RUN-SEMBIN-5cf90a (first smoke) classification took ~47 s per sols call at n = 40: sols.c chose the trace-1 constant tau by a linear scan over integers, and for the sparse modulus x^40+x^5+x^4+x^3+1 the trace vanishes on alpha^j for small j, so the scan ran to ~2^35. Run stopped by the executor after 2 classification records and 0 SOLV4 computations; manifest status aborted_infrastructure; retained. Fix: tau = lowest alpha^j with Tr = 1. Equivalence check of old vs new binary, S-A and S-B, on 12 dev instances at (40,2,2,20), (30,2,2,15), (21,3,3,7), (12,3,3,4): identical solution sets; n = 40 call time 47 s -> ~1 s (S-A), ~3 s (S-B). RUN-SEMBIN-745bf5 (n = 12) used the old binary; its results are unaffected (tau choice changes no output). | fixed before the replacement smoke run |
