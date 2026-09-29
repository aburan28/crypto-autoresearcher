# PREREGISTRATION -- TASK-20260804-8965ec: cross-instrument anchor

Written and frozen at 2026-09-08T00:49:00Z, BEFORE any full-coset arm below had
produced a result (the driver process was launched immediately prior; its
per-arm raw.jsonl entries did not exist at the time this file was written --
verify against raw.jsonl timestamps in the archived package).

## Objective

Anchor BATCH-002's counting engine (`cnt.c`, TASK-20260802-142a4b) against
BATCH-001's independently written counting engine (`count5.c`) on a shared,
reproducible case, per RANK 3 of BATCH-9845b0's dispatch objective and the
open confound recorded in `ledger/evidence/EV-AES-d33b1c.yaml` OBS-B2-3
("The cross-instrument anchor against BATCH-001's engine was never run").

## Constraint that shapes the design

`count5.c` is AES-NI-hardware-only and cannot vary the GF(2^8) mixing matrix
at all (confirmed by reading its source: it calls `_mm_aesenc_si128` /
`_mm_aesenclast_si128` directly, which is fixed-function standard AES
MixColumns). Therefore the shared case MUST use the standard AES_MC matrix
(hex `02030101010203010101020303010102`, i.e. rows [2,3,1,1],[1,2,3,1],
[1,1,2,3],[3,1,1,2]) -- not BATCH-002's M0/M1 zero-entry substitutes, which
`count5.c` cannot run. `cnt.c` is run in its `soft` mode (software T-table
engine, the mode this task's objective specifically names as the untested
one -- `cnt.c`'s own `aesni` mode was already cross-checked against its
`soft` mode via its built-in `block` pin, see PIN section below, and is not
the object of this anchor).

Both engines are run on the SAME key, base, r and j0, over the FULL 2^32
coset (`id`/coset convention on `count5.c`; `j0=0`, C1 last-round-no-mixing
convention on both, matching each engine's own documented convention).

Shared parameters (identical to BATCH-002's already-committed M0 arms, so the
anchor reuses parameters this campaign has already spent review attention on):
- key: `6fe52e2e9b3ea04085c370f9bc609245`
- base/plaintext-coset-base: `e35f00e7631cdd862e59d126e72b8fc9`
- j0: 0
- matrix: AES_MC (standard), hex `02030101010203010101020303010102`

## PIN, before any full-coset arm (completion-gate requirement)

1. **anchor.c self-check**: an independent third AES-128 implementation,
   written from the FIPS-197 specification (not derived from either
   producer engine), reproduces FIPS-197 Appendix C.1 to the byte:
   key `000102030405060708090a0b0c0d0e0f`, plaintext
   `00112233445566778899aabbccddeeff` -> ciphertext
   `69c4e0d86a7b0430d8cdb78070b4c55a`. PASS (see `pin_receipt.json`).
2. **Block-level cross-check** at the shared key/base, r in {4,5}, C1
   convention (final round has no MixColumns): `anchor.c`'s reference,
   `cnt.c`'s `soft` path and `cnt.c`'s `aesni` path (both exposed by `cnt.c`'s
   own `block` mode, which runs both unconditionally) all agree bit-for-bit.
   This pins `cnt.c` (both its internal paths) against an independent
   reference before any full-coset count is trusted.
3. `count5.c` has no single-block mode; it is pinned by BATCH-001's own
   committed `pin.c`/`pin_result.json` (not modified here, read only) AND,
   more directly for this anchor, by the fact that it is fed the EXACT
   round-key schedule this task's `anchor.c` computed and verified against
   FIPS-197 -- i.e. `count5.c`'s full-coset arm below is driven by a
   round-key blob this task independently derived and validated, not by a
   blob `count5.c` computed itself (it never computes a key schedule).

## Predictions (before measurement)

### CASE Z (expected exactly zero)
r=4, j0=0, matrix AES_MC. AES_MC has no zero entries in any row/column, so
by the round-split derivation already reviewed in this campaign
(`ledger/corrections/CORR-20260802-46b73b.yaml`; restated in BATCH-002's
`RESULTS.json` `split_by_round_count.r4`: "the four entries
M[(-c-j0) mod 4][c] ... must be non-zero" for the r=4 property to be
destroyed at that j0), the r=4 property is predicted to HOLD at every j0
under AES_MC. Prediction: **n = 0, max_occ = 1, N = 2^32**, for BOTH engines.
This is also exactly BATCH-002's own dropped `CTRL_AESMC_r4_j0` control
(pred_n=0, pred_max_occ=1; never measured there -- killed at ~90s under
external contention, see BATCH-002 RESULTS.json deviation D-6). A successful
measurement here additionally discharges that dropped control, incidentally.

### CASE NZ (expected large and non-zero)
r=5, j0=0, matrix AES_MC, same key/base. This exact (key, base, r=5, AES_MC)
combination was never previously measured by either engine (BATCH-001's own
r=5 AES_MC arms used different keys/bases; BATCH-002's `CTRL_AESMC_r5_j0` was
also dropped, never run). Prediction, from the reviewed r=5 analysis
(`CORR-20260802-46b73b`, "DROP the no-zero-entry condition ... the correct
hypothesis at r=5 is a non-singular column-preserving mixing layer" -- AES_MC
qualifies): **n mod 8 = 0**, and by analogy with BATCH-001's other AES_MC
r=5 arms (same matrix, different keys), **n on the order of ~2^31 (roughly
2.1-2.2 x 10^9)**, materially non-zero and NOT matching CASE Z. This is a
qualitative/order-of-magnitude prediction, not an exact digit prediction
(no prior committed record measured this exact key/base/r/matrix
combination), and is reported as such.

## Falsification condition

The anchor FAILS to close the confound (and the disagreement itself becomes
the reportable finding) if, on the SAME (key, base, r, j0, matrix) input,
`count5.c` and `cnt.c`-soft report different `N`, different `n`, or different
`n_mod8` after both pass their own internal exactness checks
(`n == (sum m^2 - N)/2`, `N == 2^32`, counter-integrity). Agreement on CASE Z
alone (both trivially reading zero) is explicitly flagged as WEAKER evidence
than agreement on CASE NZ, per this task's own red-team-anticipated risk that
two buggy engines could coincidentally agree on an all-zero case.

## Budget and machine state

C2 clock: start 2026-09-08T00:37:08Z, binding_stop_utc 2026-09-08T01:10:28Z
(declared_wall_clock_seconds 2000). Machine: 4 cores, AES-NI present,
uncontended at task start except for a pre-existing unrelated dirty
working-tree state in other goals' dispatch queues (recorded in the
execution report, not touched here). All four full-coset arms are run
SEQUENTIALLY by `driver.sh` to preserve uncontended timing validity; if the
clock binds before all four complete, the remaining arms are dropped and
named explicitly, not estimated.
