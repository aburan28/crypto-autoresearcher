# VAL-20261016-cd9156: independent validation of the NIST / X9.62 seed-provenance bundle

**Task:** TASK-20261016-9bf74b, run under the frozen review plan on that card (DEC-20261016-7bcdd6).

**Subject:** `research/nist_seed_provenance_20261016/` at freeze commit
`dbd1b8d15845579aaaa3af47b827955e2b625e77` (parent `6c775b6634f710dbf61c5d5c2547781eae3e2604`).
The bundle is bound by the 14 SHA-256 values in its `SOURCE.md`.

**Scope:** The Validator owns joints J1 to J7, the proves-too-much control and the blind re-derivation.
Each verdict applies to one joint, not to the claim as a whole.

**Records:**
- Machine-readable report: `validation_report.yaml`.
- Run order and output hashes: `logs/order.log`.

**Nonce:** SHA-256 of the ASCII string `dbd1b8d15845579aaaa3af47b827955e2b625e77` is
`702c36f2b6afb1a50f1b561a7e6583df966d4a3e02dc4b0d90618421f8176f92`.

| joint | verdict | one line |
|---|---|---|
| J1 byte mapping and block indexing | holds | All 10 seeds were found once each, block-aligned, at the stated 1-based blocks. All adjacent, reversed and t±1 controls fail. |
| J2 X9.62 seed-to-c | holds | All 10 satisfy `c·b² ≡ −27`, and `c` matches the c printed by FIPS 186-2 and SP 800-186. The candidate sets are identical. |
| J3 point counts and early abort | holds | 289 full counts give 0 mismatches. The re-census of all 11,042 rows agrees row by row. |
| J4 twist bookkeeping | holds (concern) | The counts 47 and 31 hold. "four" should be five. Only 26 of the 31 "lost" seeds would pass the criteria. |
| J5 classifier | holds | All lists equal summary.json and the posts (21 of 21). The n < p rule rejects prime239v2. |
| J6 bundle integrity | holds | 14 of 14 hashes match at the worktree, the freeze commit and crypto `bc6b8f29`. Four referenced files are not here (not_run by plan). |
| J7 C5 labelling and preregistration | inconclusive | The labelling holds. No immutable record dates PREREGISTRATION.md before the census data. |

## Method (independence)

All code is in `scripts/` and was written from public texts only:

- **drand48, lrand48, srand48:** the Open Group page (`specs/posix_drand48_excerpt.txt`).
- **X9.62 seed-to-c map:** FIPS 186-2 Appendix 6.4/6.5 and SP 800-186 C.3.1/C.3.2. The two texts agree (`specs/`).
- **Curve parameters:** OpenSSL 3.0.13, cross-checked against both NIST texts with 0 disagreements (`out/params.json`).
- **Tonelli-Shanks:** Wikipedia's algorithm text.
- **MOV bounds:** SEC 1 v2 and SP 800-186 C.1.

I never opened `classify.gp`, `sea_census.gp`, `research/nist_seed_skipped_curves_20261016/` or anything under `/home/user/crypto/`; those received opaque hashing and `git log`/`ls-tree` only.

There is one disclosed exposure. At session start the harness injected the contents of `/home/user/crypto/CLAUDE.md` into my context. It holds generic workflow rules and nothing about this bundle. Because of it, `blind_from_respected` is recorded as false (see the attestation).

The order of work was as follows; every step is logged with hash and UTC time in `logs/order.log`:

1. I logged my regenerated seeds, candidate sets, classification and point counts.
2. Only then did I open `census/summary.json`, at 23:39:32Z.
3. I read `PREREGISTRATION.md` after the blind re-derivation.
4. I read the two posts after the logged comparison.

## Observation

**J1 (Q1).**
- **Stream check.** For each of the six README `t`, I generated the `(int)(drand48()*256)` stream for the README block count + 2 blocks, 435,300 calls in all.
  - `int(X/2^48·256) == X>>40` held on every call.
  - glibc 2.39 `drand48` agreed on every call.
- **Seed search.** I searched each published seed at every byte offset in all 18 streams (`t−1`, `t`, `t+1` for each run). Each seed occurs exactly once, at an offset divisible by 20, in its own run. The 1-based blocks are:

  | seed | block |
  |---|---|
  | P-192 | 139 |
  | prime192v3 | 5228 |
  | prime192v2 | 6013 |
  | prime239v1 | 2185 |
  | prime239v2 | 2320 |
  | prime239v3 | 3048 |
  | P-521 | 1136 |
  | P-256 | 1842 |
  | P-384 | 2688 |
  | P-224 | 7026 |

- **Index base.** The README block counts equal the 1-based index of each run's last published seed. The orders files' `i` column equals my 1-based candidate set exactly; the 0-based reading overlaps only by chance.
- **Dates.** The UTC dates match the README table, from 1997-05-15 to 1998-04-03.

**Binary seeds (Q2).**
- **Reading family.** I declared an 8-member family: word order, byte order inside each 32-bit word, and stride 1 or 2. For all four seeds only one member matches: forward word order, big-endian words, consecutive `lrand48()` calls.
- **Recovered seeds.** Exhaustive recovery of the 17 hidden bits, followed by a walk back, gives:

  | seed | s | 2s (UTC) | first word: call d / 5-word block |
  |---|---|---|---|
  | B-233 | 446413329 | 1998-04-17 15:24:18 | 771 / 155 |
  | B-283 | 446413432 | 1998-04-17 15:27:44 | 156 / 32 |
  | B-409 | 446413509 | 1998-04-17 15:30:18 | 296 / 60 |
  | B-571 | 446413564 | 1998-04-17 15:32:08 | 361 / 73 |

- **Regeneration.** Running forward from `srand48(s)` reproduces all 160 bits of each seed.
- **Controls.** B-163 and the 10 nonce-derived random strings match no member of the family.

**J2 (Q3, Q4).**
- **Published curves.** `c·b² + 27 ≡ 0 (mod p)` for all 10. My `c` equals the printed `c` in all 9 cases where FIPS 186-2 or SP 800-186 prints one.
- **Variant (a), top bit not cleared.** It also holds on 6 of 10 curves but fails on P-192, prime192v2, P-256 and P-384, so the check does identify it.
- **Variants (b), (d), (e).** Each fails on all 10.
- **Variant (c), no mod-2^160 wrap.** It holds on all 10 and is **non-identifying**: no published seed is near 2^160.
- **Candidate sets.** Candidates are blocks with `−27/c` a nonzero square: 1,555 / 3,061 / 584 / 960 / 1,337 / 3,545 = 11,042. They are identical to the `i` columns. No block had `c = 0` or `4c + 27 = 0`.

**J3 (Q5).**
- **Full counts on 289 rows.** I ran `ellcard` with no early abort on the 85 named rows and on the 204-row nonce sample (34 per run; no augmentation needed).
  - Every recorded nonzero `N0` equals `N` (59 rows).
  - Every recorded nonzero `Nt` equals `2(p+1) − N` (103 rows).
  - All 230 recorded `N0 = 0` rows and all 186 recorded `Nt = 0` rows are composite. Their smallest prime factors are at most 137 and at most 127, so none reaches the 1000 threshold.
  - All 38 prime `N` and all 48 prime twist orders pass the Hasse test and `N·P = O` on 3 random points.
- **Independent early-abort re-census of all 11,042 rows.** My GP driver uses `ellsea(·,1)` on the curve, and separately on the twist model `y² = x³ − 3d²x + d³b0`.
  - 10,576 rows are identical in both columns. There are 0 mismatches.
  - In 466 rows the recorded `Nt` is a nonzero composite equal to `2(p+1) − N0`, while my independent twist count aborted (0). Their smallest prime factors are at most 199.
  - Re-classifying my own counts gives the same lists.

**J4.**
- **Twist-only counts.** 9 / 14 / 0 / 4 / 4 / 16 = 47 by both routes; 31 of them are in p ≡ 3 (mod 4) runs.
- **The −b curve.** On 11 demonstration rows, the full order of the `−b0` curve equals `2(p+1) − N` for p ≡ 3 (mod 4), and equals `N` for P-224. Here kronecker(−1, p224) = 1.
- **Lost seeds.** Five runs have p ≡ 3 (mod 4), and four of them contain twist-only rows. Of the 31 twist-only twists, five have more bits than p (p192: 774, 1477, 3506, 4492; p384: 1432). So only 26 would pass the stated criteria.

**J5 (Q6).**
- **Classifier.** My classifier, applied to the recorded files, gives:
  - accepted 8/5/1/2/1/4 (21);
  - bitlen rejects 0/7/0/0/2/8 (17);
  - twist-only 47;
  - published/skipped 10/11.
- **Sensitivity.**
  - The MOV variants (B = 20, B < 100, k ≤ 100, k < 2^10) change no row. No prime `N0` has an embedding degree ≤ 10^5.
  - The bitlen rule cannot fire at p239 or p256 (the Hasse maximum keeps the order within 239 and 256 bits).
  - prime239v2 has n > p. The n < p rule rejects it and three skipped p239 rows (1562, 2491, 2682).

**C2 (Q7).**
- **State recovery.** A lattice CVP (dimension 20) on each seed alone recovers a state that regenerates all 20 bytes, for all ten prime seeds.
- **Walk-back.** Walking back 8,000 blocks finds 2 or 3 srand48-form states. Exactly one is block-aligned, and it equals the README `t` and the J1 block in all ten cases.
- **Arithmetic.**
  - 2^48/2^160 = 2^−112.
  - 63,072,000/2^32 = 0.014685.
  - 0.014685^6 = 1.003·10^−11.
  - lcm(65536, 20) = 327,680 steps, so "at most one aligned" holds for any window up to 16,384 blocks.
- **Controls.** No random string yields a regenerating state. The 10 synthetic positive controls are all recovered.

**C4.**
- All nine p ≡ 3 (mod 4) published b are the (p+1)/4 root.
- For P-224, the smallest non-residue is 11. Tonelli-Shanks with z = 11 gives R with b = p − R. With z = 22 or 31 the sign would be +R.

**J6.**
- **Hashes.** 14 of 14 SOURCE.md hashes match:
  - in the working tree;
  - at `git show dbd1b8d1:<path>`;
  - opaquely, at `git -C /home/user/crypto show origin/claude/nist-seed-provenance:<path>`, where that ref is `bc6b8f292ccb868433b435caaf08d0ec85854810`.
- **Files.** The freeze tree has no unlisted file.
- **Missing references.** These README references are absent here: `census.sh`, `plot_streams.py`, `examples/nist_seed_candidates.rs` and `src/cryptanalysis/nist_seed_provenance.rs`. SOURCE.md declares them not copied, and all four exist in crypto (`ls-tree`).

**J7.**
- **Commit history.** PREREGISTRATION.md and all census files were first committed together: crypto `bc6b8f29` (2026-10-16T21:16:28Z) and here `64a46b4c` (21:16:40Z).
- **The file's own claims.** It says it was written at about 19:27 UTC. It says the published curves' (b, n, G) had been looked at. Its amendment was "added 19:35 UTC, after the P-192 run reproduced".

## Comparison

- **Recorded and classifier data.** Every count, set and list in the README census table, the six orders files and `summary.json` equals my independent values. This covers:
  - 21,753 blocks; 11,042 with b; 47 twist-only; 17 bitlen; 21 accepted; 10 published and 11 skipped;
  - every per-run row.
- **The posts.** Valsorda's accepted list (21 indices, with 2-byte seed prefixes) equals mine.
- **Differences.** The only difference from the recorded data is the 466 `Nt` entries above. They are explained by the producer filling `Nt` from `N0`, and every one is consistent.
- **Claim wording.**

  | README says | Measured |
  |---|---|
  | "the four p ≡ 3 mod 4 runs" | five such runs, four with twist-only rows |
  | "31 seeds were lost" | 31 twist-only-prime candidates; 26 would be accepted on the twist |
  | "frozen before any curve order was seen" | the file had seen the published n; its amendment came after the P-192 run reproduced |

## Inference

- **C1, C2, C4.** These hold as exact, independently re-derived facts, and every known-false control fails as the plan requires. My implementation shares no code with the producer's and was written from the standards, so agreement is evidence about the quantities, not about a shared implementation.
- **C3.** The census holds on the strongest check the plan offers. The full independent re-census agrees row by row, and every prime value the classification depends on is certified by `N·P = O`, independently of SEA. The derived "31 seeds lost" sentence overstates the loss by 5 under the bundle's own criteria. "four" miscounts the p ≡ 3 (mod 4) runs.
- **C5.** The labelling holds. The preregistration's timing claim cannot be checked against any immutable record: no record supports it, and none refutes it.

**Recommended strengths:**

| claim | strength | qualification |
|---|---|---|
| C1 | replicated | The native-test sentence is unverifiable by plan design, and the binary layout needed a declared 8-member reading family. |
| C2 | strong | All ten state recoveries and walk-backs are done. |
| C3 | strong | Scoped to exclude the "31 seeds were lost" and "four" wording. |
| C4 | replicated | |
| C5 | no strength | Labelling holds; timing is unverifiable. |

The rationale is in `validation_report.yaml`.

## Limitation

- **Shared SEA library.** PARI/GP SEA is common to producer and Validator. The `N·P = O` certificates (38 curve and 48 twist primes) are the only SEA-free checks. They cover every prime value the classification uses, but not the zero rows. For those, the evidence is the two independent early-abort runs plus 416 full counts with small factors.
- **X9.62 itself.** The text was not retrievable.
  - prime192v2/v3 and prime239v1-v3 parameters come from OpenSSL only.
  - The X9.62-1998 MOV bound B = 20 is taken from SEC 1 v2's commentary.
- **Native Rust receipt and `census.sh`.** These were not read or run (blind_from). README statements about them remain unverified.
- **Infrastructure failures.** Not negative evidence, all preserved in `logs/`:
  - J3 attempt 1 hit a PARI stack overflow;
  - J3 attempt 2 wrote 0 rows;
  - re-census attempt 1 hit a stack overflow on shard 1;
  - my `pkill` killed its own launching shell.
- **Ordering.** The constraint-4 ordering is attested, not enforced. I printed 3 lines of one orders file at about 22:44Z, after my candidate sets were logged (22:42Z) and before the logged EVENT (22:46:47Z).
- **Independence.** A single reviewer covered all joints, and there was no red team. The harness-injected `/home/user/crypto/CLAUDE.md` exposure is disclosed in the attestation. `tools/check_review_independence.py --plan ledger/handoffs/TASK-20261016-9bf74b.yaml --reports <this report>` reports one problem, and it is exactly that disclosed read (blind_from `/home/user/crypto/`). It reports nothing else.

## J6 commands (opaque operations on blind paths)

```text
sha256sum research/nist_seed_provenance_20261016/<f>                      # 14 files, worktree
git show dbd1b8d15845579aaaa3af47b827955e2b625e77:research/nist_seed_provenance_20261016/<f> | sha256sum
git -C /home/user/crypto show origin/claude/nist-seed-provenance:research/nist_seed_provenance_20261016/<f> | sha256sum
git -C /home/user/crypto ls-tree -r --name-only origin/claude/nist-seed-provenance research/nist_seed_provenance_20261016/
git -C /home/user/crypto log --all --format='%H %cI %s' -- research/nist_seed_provenance_20261016/<f>
```

## Files

`scripts/` contains the code; `out/` the outputs; `logs/` the logs, including `order.log`; `specs/` the retrieved specification excerpts and `SOURCES.txt`.
Every file is listed with its SHA-256 in `validation_report.yaml` under `artifact_paths`.
