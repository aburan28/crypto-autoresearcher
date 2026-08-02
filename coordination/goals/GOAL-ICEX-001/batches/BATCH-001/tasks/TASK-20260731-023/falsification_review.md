# TASK-20260731-023 falsification review

## Verdict

**PASS**

Reviewed only Coordinator snapshot `TASK-20260731-022` at commit
`a1d6ec1d82cb06a93830fa08ad30dc4bd8f0f176` (parent
`8e3997175d4d1748bacf043b351964a144d2a67e`). The commit is reachable from
review `HEAD`, changes exactly the receipt plus the two producer artifacts,
and producer SHA-256 digests match the receipt `source_path_sha256` map.
The receipt still shows `pending_post_commit` with null commit metadata; Git
checks bind the review. Working-tree-only producer edits were not treated as
durable evidence.

Inference for this review: requested `review-xhigh`, resolved
`cursor-grok-4.5-high-fast`, `fallback_used: true`, authorization
`AMEND-PATH-001-001`, independent session. Equivalence to `review-xhigh` is
not claimed.

No measurement, implementation, or experiment is authorized by this PASS.

## What was attacked

Attempt to falsify that the BATCH-001 ICEX exponent protocol is safe to ledger
without overclaim, specifically:

1. Silent import of uncharged `p_exist` / KN-LIT-009 / HEUR-SEMAEV as relation supply
2. `ceil(r/p_L)` or illicit scalarization of multi-coordinate cost vectors
3. Optional / hand-waved matched rho/BSGS baselines
4. Activation without measured G4–G6 packages or Coordinator auth
5. Escape hatch to claim IC-beats-rho from this card alone
6. Inference/fallback honesty omission

## Snapshot hash verification

| Path | Receipt digest | Git blob at `a1d6ec1d82cb` |
| --- | --- | --- |
| `ic_exponent_protocol.yaml` | `368439095328d0976a5f05458ea0be813f94bf73362aa484ba30d6bce07611bd` | match |
| `protocol_design_note.md` | `b7bd62aa9f68f234db65db053b6b4e091893a67c42436f213be263db575f6584` | match |
| `snapshot-receipt.json` | `7147cd969176736fd3a8095dfd07419fd7b59f29241aa44bbcf748570653f951` | match |

## Axis results

### Feed pins vs uncharged heuristics — not falsified

SDEG/MONO/RELN are pinned to `DEC-20260725-015` / `027` / `017` with named
protocol, red-team, and snapshot paths. Charged allowlists are explicit
(`C_decomp`/`C_rho`/`C_bsgs`; MONO labeled envelopes as structure context only;
`declared_p_lower_solve` as sole `p_L`). Forbidden imports cover
`p_exist`-as-charged-supply, HEUR-SEMAEV / KN-LIT-009 as established inputs,
and treating protocol PASSes as measurement packages
(`FORBID-PROTOCOL-PASS-AS-DATA`, `measurement_status_at_protocol_design: absent`).
`CTRL-FEED-PIN-INTEGRITY` is specified as a machine check on digests and charged
symbols. Optimistic heuristics cannot silently mint ICEX probability.

### `ceil(r/p_L)` and no-scalarization — not falsified

`accounting.no_scalarization: true`; five named stages; additive/non-additive
split; `FORBID-CEIL-RP` / `FORBID-SCALARIZATION` with stop rules;
`OBL-NO-SCALARIZATION` / `OBL-PROBABILITY-GATE`; `CTRL-NO-CEIL-RP` /
`CTRL-NO-SCALAR-RESCUE`. Finite-tail claims require sealed IID + Clopper-Pearson
`declared_p_lower_solve`; preferred model is observed charged cohort without
imputed successes. Design-level stop/CTRL language matches accepted SDEG/RELN
protocol-design PASSes. Executable closed-boolean checkers remain a seal-time
residual, not a present-tense honesty failure for this review-only card.

### Matched rho/BSGS required — not falsified

Matched `C_rho`/`C_bsgs` are SDEG charged symbols, required by `GATE-SDEG-DATA`,
and covered by `CTRL-MATCHED-RHO` / `CTRL-MATCHED-BSGS`. Advantage predicate
requires non-dominance by `C_rho` on the predeclared critical set. Operative
baseline is measured matched vectors, not imputed \(\sqrt{\ell}\).

### Activation gates — not falsified

Present-tense non-authorization; null verifier hash hard-gate; activation
blocked until measured SDEG/MONO/RELN packages, separate Coordinator ledger
authorization, fixtures, sealed schedules, precommit verification, and ECDLP
residuals (or named equal-hardness amendment). `post_pass_executor_gate`
allows only later design / wait-for-feeds — not immediate execution.
Protocol PASS ≠ measurement ≠ crypto-scale.

### IC-beats-rho escape from this card — not falsified

Prohibited claims and executor gate block crypto-scale IC-beats-rho and medium
upgrades from this card. `H-ALPHA-EXCLUDES-HALF` / `TOY_ALPHA_CI_EXCLUDES_HALF`
are post-measurement toy-scope outcomes that at most motivate a separate medium
trend gate. This design card alone cannot mint IC-beats-rho.

### Inference/fallback honesty — recorded

Producer and this review record requested policy, resolved
`cursor-grok-4.5-high-fast`, `fallback_used: true` under `AMEND-PATH-001-001`,
and deny equivalence to the preferred policy.

## Nonblocking residuals (do not flip PASS)

1. **STOP-ORACLE-LEAK wording** — condition “uses `p_exist` without charged
   `declared_p_lower_solve`” is softer than `FORBID-P-EXIST-IMPORT`; tighten at
   seal so `p_exist` cannot ride alongside `p_L` as charged supply.
2. **Dual baseline path** — “ICEX may also seal its own matched rho/BSGS” must
   not replace SDEG matched digests with optimistic ICEX-native controls.
3. **Deferred checkers/bytes** — executable feed-pin / no-ceil / no-scalar
   checkers, fixtures, schedules, and verifier hash remain hard-gated; MONO
   `RANDOM_PANEL_CALIBRATION_TOY` must not substitute for `declared_p_lower_solve`.

## Overclaim check

No breakthrough, attack improvement, ECDLP lower bound, crypto-scale relevance,
fallback-equivalence, KN-LIT-009-established, or IC-beats-rho claim was found.
`PROTOCOL_COMPLETE_REVIEW_REQUIRED` is scoped to review-only design completeness,
not executable readiness.

## Narrowest supported statement

At snapshot `a1d6ec1d82cb`, TASK-20260731-021 specifies a review-only toy
end-to-end charged IC exponent protocol with hard-pinned G4–G6 feeds, charged-only
relation supply, full-cost multi-coordinate accounting vs matched rho/BSGS,
forbid `ceil(r/p_L)` and illicit scalarization, and hard activation gates on
measured packages plus Coordinator authorization. It authorizes no runs and
does not establish Semaev heuristics or claim crypto-scale IC advantage.

## Next concrete action

Coordinator may ledger-archive this PASS via `TASK-20260731-024`; authorize no
implementation or measurement until charged SDEG/MONO/RELN measurement packages
exist and a separate ledger authorization clears activation gates.
