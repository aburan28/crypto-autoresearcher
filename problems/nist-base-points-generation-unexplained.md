# Generation of the NIST P-224, P-256, P-384, P-521, B-curve and K-curve base points is unknown

- **Status:** `open`
- **Kind:** unknown cause; missing historical generator program or run log. Also an implementation gap (native ports owed for the Python-only searches; detector-blind cells) and an access limit (1997 sources of several candidate libraries not found)
- **Affected work:** [KN-LIT-d2f917](../knowledge/literature/KN-LIT-d2f917.md) (its 2026-10-22 addendum), [KN-FIND-cee88d](../knowledge/findings/KN-FIND-cee88d.md) ("Not covered by this finding"), [provenance reproduction bundle](../research/nist_seed_provenance_20261016/README.md) ("Open") with its scope correction `CORR-20261022-b3c8a5`, the SafeCurves rigidity rows of `GOAL-SCURVE-137bd9`, `GOAL-SCURVE-be9707` and `GOAL-SCURVE-cef9f7` (item (ii) of `CORR-20261016-0bf0b2`), and the C3 coverage count of `EXP-SCURVE-0e4295` (`DEC-20261016-a12871`: P-224's G is an unbound quantity). Cross-repository: [aburan28/crypto PR #2410](https://github.com/aburan28/crypto/pull/2410), [base-point searches](https://github.com/aburan28/crypto/blob/2275ed6ec3a53e1a7df8dcb0aa48d1ac59af9a79/research/nist_basepoint_provenance_20261017/README.md)
- **Next action owner:** unassigned. A run in this repository needs a Coordinator-approved contract. The native ports are owed by the aburan28/crypto study under its own rules.
- **Last updated:** 2026-10-22

## Problem

We cannot say how the published base points of P-224, P-256, P-384, P-521, B-163, B-233, B-283, B-409, B-571, K-163, K-233, K-283, K-409 and K-571 were produced, because the 1997-98 generation code and its run logs are unavailable and no tested generator reproduces any of these points.

The seeds of these curves are explained (B-163 excepted; see [its own record](nist-b163-seed-generation-unexplained.md)), and so are the six May-1997 base points of P-192, prime192v2/v3 and prime239v1-3, which come from FreeLIP `zrandom` (KN-LIT-d2f917, as reported by the posts). The standards do not fix the base point. The follow-up note quotes FIPS 186-4 D.1.1.5 ("Any point of order n can serve as the base point") and describes X9.62-1998 A.3.1 as drawing a random `R` and publishing `G = hR`, with no rule for the sign of `y`. This Coordinator did not retrieve either standard. This blocks a complete account of how the published parameters were generated, which is the base-point half of the SafeCurves rigidity question for P-224, P-256 and P-384 and of the coverage count C3. It blocks no ECDLP statement: any point of order `n` is an equally good generator.

## Evidence and uncertainty

- **Observed (aburan28/crypto PR #2410, open and unmerged, branch head `2275ed6e` as read on 2026-10-22; no independent validation):** 12 of its 14 searches (T1-T12) concern the base points; T13 and T14 concern the B-163 seed. Each base-point search found its planted positive controls, except in the blind cells below, and none found an informative target hit. On the binary curves every target includes all `R` with `hR = G` (2 halvings for the B-curves and K-163, 4 quarter points for K-233 to K-571), each coordinate in the polynomial and the normal basis: 137 targets, 50 B-curve and 87 K-curve (`out/scan_bin.out`, `out/scan_k.out`; the halvings double back to `G`, 2 of 2 on all five B-curves, `out/gnb.out`). Prime-curve searches: FreeLIP `zrandomb` with seeds 1 to 2^24 and with 1990-98 timestamp and date seeds (T1, T2); FreeLIP limb lattice for any seed (T3); drand48 continuing the seed run (T4); drand48 chunks un-reduced mod `p` (T5); GMP 2.0.2 `mpz_random` (T6); MIRACL `bigrand` (T7); PARI `random()`/genrand (T8); SHA-1 expansion of the curve seed (T9); `G = kP0` from small-`x` points, `x0 <= 12`, `k <= 2^20` (T10). Binary-curve searches: FreeLIP and drand48-family lattice (T11); PARI patterns (T12). Scopes as in that README's table.
- **Observed, implementation status:** T3, T4, T5, T8, T9, T11 and T12 were computed in Python in a standalone session. aburan28/crypto forbids Python for results, keeps their sources as a frozen snapshot, and treats them as observations until a native port reproduces them. T1, T2, T6, T7 and T10 and the target construction are C or PARI/GP.
- **Observed, blind cells (untested, not negative):** T3 on P-224 and P-256 (0 of 3 controls at every width; the mod-`p` reduction hides the limbs); T3 on P-384 at NBITS = 62 (flags 126 of 200 random values and 3 of 5 controls, so its flags on `Gx` and `Gy` carry no information, `out/fl384w62.out`); Maple V `rand` in T8 and T12 (control missed on every curve). In `out/scan_k.out` the K-curve `Gy` in the polynomial basis is not listed as a target. The draws `R` are.
- **Observed, side check:** FreeLIP `zsqrtmod` for `p = 3 (mod 4)` returns `a^((p+1)/4)` and takes no seed input, so on 3 of the 6 FreeLIP base points the negated `Gy` was chosen by the lost calling code. The seed-parity fit for that sign (6 of 6) is a post-hoc lead.
- **Earlier observation, corrected scope:** the bundle's seed-agnostic scan ("No hits on the 19 targets") tested the published binary `Gx`, `Gy`, not the X9.62 draw `x(R)`, and probably did not include the K-curves (`CORR-20261022-b3c8a5`). Its prime-curve part stands as an outside-repository observation.
- **Derived or proved:** not established. A bounded search with found controls excludes only the generator, layout, seed range and draw model it ran.
- **Suspected explanations:** the follow-up names two, and neither can be tested from public data: (1) a generator not covered so far; (2) a choice that is not a function of a recoverable seed. Labelled conjectures.
- **Missing capability:** the 1997-98 base-point code and logs; native ports of the seven Python searches; a detector that sees FreeLIP output through the mod-`p` reduction on P-224 and P-256; 1997 generator sources for Magma, SIMATH, KANT, ZEN/BigNum and libI (LiDIA 1.3), which the follow-up did not find.
- **What this evidence does not establish:** that any of these base points is not generator output, that it was chosen deliberately, or anything about ECDLP hardness. Wall times were not recorded, and some invocations are reconstructed from their "done:" lines (follow-up "Caveats").

## What would unblock it

- [ ] Contemporaneous code, logs or documentation that, replayed from stated inputs, outputs a published `G` (or an `R` with `hR = G`) exactly, with sound provenance.
- [ ] Or a generator model declared before it is run (library and version, seed rule and range, output layout, draw-to-point map, sign rule), implemented natively in C or Rust, whose planted controls on the same curves are found, and which reproduces a published `Gx` or `x(R)` exactly, with a stated chance bound for the hit of at most 2^-64, then replicated by an independent session.

Either condition, met for one curve, explains that curve's base point. A model that reproduces the six FreeLIP points and the target points under one rule would also tie them to one process. Neither establishes intent, and neither bears on ECDLP. Native ports and validation of the existing nulls would strengthen the negative scope but would not resolve this record.

## Next discriminating step

- **Action or proof obligation:** close the T3 blind cells on P-224 and P-256. Declare the FreeLIP draw width used for these fields before running; from it, enumerate every reduction quotient `q` with `X = Gx + q p` inside that width, and run the FreeLIP limb test on each `X`, natively in C or Rust. Repeat for `Gy`.
- **Inputs and controls:** published `Gx`, `Gy` of P-224 and P-256; synthetic FreeLIP points on P-224 and P-256 with arbitrary seeds, reduced the same way, which must be found before any target result is read; the six explained FreeLIP points as positive controls; random field elements as a specificity control (the P-384 NBITS = 62 window shows why that control is needed).
- **Execution limits and stop condition:** if the declared width makes the quotient range too large to enumerate, record the range and stop; that is the measured obstruction for this cell. Otherwise stop at the end of the declared range, or at the first exact hit, which is preserved and checked for its chance bound before anything else runs.
- **Outcomes and next actions:** an exact hit with a negligible chance bound is a candidate explanation for that curve and goes to independent replication; a null with controls found closes only these cells for that width; a missed control leaves the cells blind; an infrastructure failure supports no inference.
- **Recheck trigger:** PR #2410 merging, a native port of any Python search, a recovered 1997 library source, or new primary-source material.

A planned step is not a completed experiment. Apply the existing execution, review, budget, and archival rules before acting on it.

## Resolution and history

2026-10-22 (Coordinator, DEC-20261022-4e7b19): Opened from the base-point searches in aburan28/crypto PR #2410 and the scope correction CORR-20261022-b3c8a5 of the bundle's earlier scan. Unresolved. This record is a named obstruction, not evidence. It changes no goal, hypothesis or SafeCurves status.
