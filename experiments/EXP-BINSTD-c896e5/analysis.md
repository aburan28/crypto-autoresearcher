# Analysis — EXP-BINSTD-c896e5 Stages 0–1

Hypothesis: `H-BINSTD-b130e3`. Heuristic under test: `HEUR-BINSTD-df6215-H1`
(Nagao unique-rels/sec over chained S_3 ≥ ρ with ρ=1 on the authorized
cell). Approval: `DEC-20261003-34592e`. Producer: `TASK-20261003-6ab26a`.
Review plan: `experiments/EXP-BINSTD-c896e5/review/review-plan.yaml`
(coordinator prior left as written). Decision: `DEC-20261004-c7d380`.
Evidence: `EV-BINSTD-c3d1c5`. No Bedrock, Magma, Sage, or AUXIN. No
discrete logarithm, no exponent, no ECC2K-130 result.

## Observation

Two authorized runs, and only those two, are in the package. Both
receipts are `output_validated`, `returncode` 0, `check_returncode` 0.
Both `check.stdout.log` files are `OK`. Both manifests are
`completed_valid` with `code.dirty` false, `certificate.kind` none, and
`verified` null. `claims.break`, `claims.exponent_move`, and
`claims.n_ge_131` are false on both raw results. `certificate.kind`
none is the expected envelope for this instrument: the card claims no
discrete-log solve.

| run | stage | receipt | check | outcome |
|---|---|---|---|---|
| `RUN-BINSTD-4e0a84` | 0 | `output_validated` | 0 | `O-STAGE0-OK`, `twin_ok` true, `mul_probe` true, `fb_size_n17_ell3` 10 |
| `RUN-BINSTD-41f31f` | 1 | `output_validated` | 0 | `O-FAIL-BAND`, `nagao_unique` 4, `chained_unique` 5, `twin_ok` true, `band_holds` false, `both_zero` false |

`RESULTS.md` states `outcome: O-FAIL-BAND`. That matches
`RUN-BINSTD-41f31f/raw-result.json`. Stage 0 has no second outcome file;
its raw result is `O-STAGE0-OK`.

Archived Stage-1 panel `(n, ell)=(17, 3)`, `fb_size` 10, `rho` 1/1:
`nagao_unique` 4, `chained_unique` 5, `nagao_passes` 1,
`chained_passes` 26, `nagao_rps` 64.57166792817132, `chained_rps`
2572.3310277774244, `band_holds` false, `twins_agree` true,
`null_total_hits` 0. Control table null seeds 2026100311, 2026100312,
and 2026100313 each have `hits_a` 0 and `hits_b` 0.

The product comparison used those two archived rates and ρ=1/1 only.
`64.57166792817132 * 1` is 64.57166792817132.
`2572.3310277774244 * 1` is 2572.3310277774244. The first product is
strictly smaller. Archived ratio
`nagao_rps / chained_rps` = 0.0251023943772755.

A Stage-1 replay from a temp copy of the experiment tree
(`/tmp/review-binstd-c896e5`, archived `stage1/panels.json`,
`stage1/control-table.json`, and `RESULTS.md` removed in that copy
only) returned `O-FAIL-BAND` with `nagao_unique` 4 and `chained_unique`
5. Replay rates were 54.79363710040227 and 2098.516684800475. The
archived stage files' digests were unchanged after the replay.

## Comparison

`HEUR-BINSTD-df6215-H1` predicted R ≥ 1 on this cell after twins agree
and at least one arm has a nonzero unique count. The archived panel has
twins agreeing, unique counts 4 and 5, and R = 0.0251023943772755 < 1.
`decide()` emits `O-ARTIFACT` on twin failure, `O-INCONCLUSIVE` when
both unique counts are 0, `O-SUPPORT` only when
`nagao_rps * 1 >= chained_rps * 1`, and `O-FAIL-BAND` otherwise.
`check.py` refuses `O-FAIL-BAND` when that inequality holds. The
archived label is the R < 1 branch.

The temp replay kept the outcome and both unique counts. It moved the
wall-clock rates, which the review plan allowed. The support branch
does not fire on either the archived rates or the replay rates.

Stage 0 is the freeze and twin probe (`O-STAGE0-OK`). It is not a
hypothesis verdict. Null FB-hit counts are 0 on all three seeds under
both meters. That null is recorded; it is not the band statistic.

## Inference

The package is valid on the declared gates: two runs, checks passed,
raw outcome matches `RESULTS.md`, code not dirty, no exponent claim.
`O-FAIL-BAND` is the pre-registered falsifier of
`HEUR-BINSTD-df6215-H1` on the only authorized cell. Official decision
is **weaken**. Evidence direction is **weakens**. Strength is
**preliminary**: one valid unreplicated toy cell. `claim_tier` is
**toy**. `proof_status` is **empirical_only**.

`reject_scoped` does not apply. The refutation is one unreplicated
empirical cell, with no counterexample certificate and no derivation
that Nagao search fails off this cell. `support` does not apply: R < 1.
`H-BINSTD-b130e3` moves from approved to **weakened**.
`EXP-BINSTD-c896e5` moves from approved to **analyzed**. The protocol
stays frozen. The next action is a replication of this same `(17, 3)`
cell under a new contract. Stage 2 remaining cells stay unauthorized.

## Limitation

- Scope is the single cell `(n, ell)=(17, 3)`, wall B=0.05s, ρ=1,
  in-Python Field/TableField twin meters. Not n≥19. Not ECC2K-130.
  No discrete logarithm was solved.
- Unique counts 4 and 5 repeated on replay. The rels/sec floats are
  wall-clock and moved. The obstruction point estimate is the archived
  ratio, not the replay rates.
- One coordinator task owned J1, J2, and J3 (PD-1). No separate
  validator session and no red-team session.
- Receipt `artifact_sha256` for `manifest.yaml` does not match the
  current manifest bytes on either run. The other receipt hashes match,
  and the manifest fields used above agree with the raw results. That
  digest drift is not a raw/RESULTS mismatch, a failed check, a dirty
  tree, or `exponent_move` true.
- No `KN-FIND`. Weaken at preliminary strength is not a promotion.
