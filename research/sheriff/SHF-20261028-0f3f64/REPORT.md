# Sheriff case SHF-20261028-0f3f64: independent re-audit of current main

Audit record. It changes no research state and repairs nothing. Verdicts are in
`findings.yaml` (passes `tools/sheriff.py check-case`). Heads audited:
crypto-autoresearcher `b7d5e65b9f`, isogeny-labs/crypto `669809d5c6`,
isogeny-labs/cryptanalysis `f3cce49955` (all origin/main, clean).

## Prior (written before reading, `prior.md`)

I expected: a DEEP-ALI gap (binding order, unrecomputed D(x), untested checks);
`complete_manifest` sound on the happy path but loose on contradictions and
bytes; the 143 -> 126 count reproducible only at the PR's commit; a band
rounding or ordering slip in cryptanalysis#1077; L-N9 open; the deferred items
unchanged. Outcome: confirmed for the manifest (contradictions), the ledger
count, L-N9 and the deferred items; the DEEP verifier read sound, but its
tests are thinner than claimed; the band numbers held.

## Verdicts (21 claims)

2 upheld, 13 upheld_scoped, 4 overclaimed, 2 not_covered, 0 unsupported, 0 broken.
No blocker. 7 major findings, 27 minor.

| claim | verdict | one line |
| --- | --- | --- |
| C-STARK-1 OOD values transcript-bound | upheld_scoped | order replays exactly; read from code, cargo not run |
| C-STARK-2 verifier recomputes D(x) | upheld_scoped | from Merkle-bound f(x), f(ωx), Comp(x); compared to FRI layer 0 |
| C-STARK-3 degree bound, λ-adjustment | upheld_scoped | checked numerically at three (n, β); depth gate untested |
| C-STARK-4 stated ε | upheld_scoped | 2^-240 / 2^-40 / worst ε_field 2^-217.6 re-derive; formula uncited |
| C-STARK-5 negative tests hit each check | **overclaimed** | FRI fold check and depth gate have no isolating test (S2N-1, S2N-2) |
| C-MAN-1 never invents | upheld_scoped | no measured value invented; 15 constant fields filled (LGN-4) |
| C-MAN-2 refuses contradictions | **overclaimed** | only id, run_id, experiment_id compared; 24 of 27 contradictions accepted (LGN-2) |
| C-MAN-3 gates on check_run | upheld_scoped | check_run passes an empty manifest allowed by the plan (LGN-3) |
| C-MAN-4 preserves bytes | upheld_scoped | kept and hashed in the receipt; published manifest is re-serialised (LGN-5) |
| C-LED-1 143 -> 126 | **overclaimed** | 141 -> 124 at the PR tip; as merged 115 -> 100 (LGN-1, LGN-6) |
| C-LED-2 manifest_v2 faithful | upheld_scoped | 53/53 hashes, 7/7 registry entries; one wrong custody date (LGN-7) |
| C-LED-3 rulings justified | upheld_scoped | premises hold except two measurement artifacts and one unfixed budget |
| C-KOB-1 receipts verify | upheld_scoped | 150/150 SHA256SUMS; S3 bytes not on disk |
| C-KOB-2 analysis reproduces | upheld_scoped | independent re-implementation; analyze_v2.py itself not rerun |
| C-KOB-3 §5a numbers match | upheld | 37 quoted numbers equal derived values |
| C-KOB-4 no improvement; unresolved vs rho | upheld | band straddles rho; order flips at w* = 0.0029 GAE |
| C-LEAN-1 TranslationDescent builds | not_covered | no Lean; elan install refused |
| C-LEAN-2 name and docstring "descends" | **overclaimed** | proves commutation with ι_S; L-N9 still open |
| C-DEF-1 rank-finder band | upheld_scoped | disclosure accurate; band still unported |
| C-DEF-2 lean-verification disabled | not_covered | Actions API unreachable |
| C-SWEEP | upheld_scoped | canary 15/15 in both sweeps |

## Major findings (no blockers)

- **LGN-1** PR #2497's merge (`21acbaab63`) dropped the `- kind: ledger` and
  `registered:` lines of two new `tools/schema_supersession_registry.yaml`
  entries. They became duplicate keys inside the DEC-20261019-624f64 entry
  (confirmed by me: duplicate keys at line 1873). YAML keeps the last value, so
  TASK-20261017-2d324f was never fixed and DEC-20261019-624f64 lost its routing.
  Neither merge hygiene nor the validator detects duplicate keys.
- **LGN-2** `complete_manifest()` refuses a contradiction only on id fields;
  a driver contradicting the plan's task_id, seed or commit reaches
  `output_validated`.
- **LGN-3** `check_run` is silent on an empty or null manifest, so a plan that
  allows an empty `manifest.yaml` passes the gate.
- **LGN-8** schema-failing run manifests keep entering main (26 of today's 67
  validate_ledger errors); the ledger gate is not stopping them.
- **S2N-1** the FRI fold-consistency check has no test that fails without it.
  I confirmed that the tests reject earlier, at the final-layer root check
  (stark.rs:526). A test gap, not a demonstrated forgery.
- **S2N-2** the FRI depth gate (stark_v2.rs:766) is the only guard against
  over-folding and is not isolated by any test.
- **S2N-10** `plonk.rs` verify never checks the sent evaluations against their
  polynomials (sweep lead confirmed). No claim in scope cites PLONK.

## Per-beat results

- **B2:** the DEEP-ALI verifier is sound on reading. Transcript order, D(x)
  recomputation, degree bound and ε arithmetic hold. The tests are not complete
  (above). `cargo test --release --lib zk::stark` was **not run**.
- **B3:** text scan only. L-N9 open (`LN9-R`). No Lean build.
- **B5:** cryptanalysis#1077: S/rT is 0.01138 at 0 GAE, 29.00 at 0.1, 115.5 at
  1 (P: 0.01141, 43.93, 175.0). Unresolved against rho; no improvement claimed.
  Distance remaining is a lower bound (CAN-2).
- **B6:** protocol commit precedes data (verified on the PR head); analysis
  script written 62 minutes after the data (CAN-4, stricter only).
- **B7:** validate_ledger has 67 new errors on main (review_plan 30, run
  manifest schema 30, prior_art 4, spec 1, handoff budget 1, promotion 1,
  citations 0). Merge hygiene `--absolute` passes. 4 runbook sessions await audit.
- **B8:** the 6 semaev untraced-number leads all trace to the raw result
  (`scripts/session/semaev_untraced.out`). Two historical records use
  "verified execution" for row verification (SES-1).

## Prior findings, current state

42 fixed, 6 partially fixed, 1 not fixed (L-N9), 1 not covered (CI1).
Partially fixed: V1 (v1 grinding at a caller-chosen q is by design), M2 and M2-R
(349 and 330 -> 67), K-N1 (no band for B's own row), L-N2 (conductor-gap README
banner, PPN-1), E1-R (CI deletes the unbound receipt, PPN-5). Full list in
`findings.yaml`.

## Deferred items

- **validate_ledger:** prior_art 4 (IDEA-20261003-43f871, -4f41d0, -94078e,
  -c9c6c3); citations 0; FROB `TASK-20260914-7119f2` 3 errors; RUN-QSP-715b58
  has no manifest and no output.
- **Rank-finder GAE band:** still "Not computable", counters unported.
- **lean-verification workflow:** state not_covered (see below).

## Not covered, and what would cover it

| item | command |
| --- | --- |
| `cargo test --release --lib zk::stark -- --include-ignored`, plus forgeries for S2N-1/S2N-2 | in `isogeny-labs/crypto` |
| Lean build and axiom audit of TranslationDescent | `./formal/setup.sh && lake build CryptoResearch.Quotient.TranslationDescent && lake env lean AxiomAudit.lean` in `formal/` |
| Workflow enabled states | `gh api repos/isogeny-labs/crypto-autoresearcher/actions/workflows` |
| `analyze_v2.py` rerun, S3 objects behind pointers | run it in the cryptanalysis checkout; `tools/artifacts/artifacts.py pull` |
| sibling-repo sweep checkers (ecbench, fb-archive, Lean gates) | `python3 tools/sheriff.py sweep --target all --deep` with the siblings attached |
| info-level strong-word and metaprogram leads; 412 outside-sparse roots | full checkouts |

## Impediments

`add_repo` for the two isogeny-labs siblings was refused, so I used read-only
partial clones of the public repositories. Executing code from them (cargo,
elan, analyze_v2.py) was refused as external code. Those are impediments, not
negative evidence.

## What this case does not establish

It does not establish execution verification of anything (the execution-proof
milestones remain open). Reader verdicts on crypto and cryptanalysis rest on
reading code and independent re-implementation, not on running the producers'
own tests. Lean semantic review stays pending. `ci_ledger_gate.py` and the
workflows were not observed running.
