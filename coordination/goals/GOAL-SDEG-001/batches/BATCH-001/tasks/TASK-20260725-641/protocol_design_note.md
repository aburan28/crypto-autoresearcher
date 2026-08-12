# Protocol design note — TASK-20260725-641

## Purpose

Review-only frozen **scaling protocol** for GOAL-SDEG-001 (Tier 1 / G4): Semaev
\(S_3/S_4\) solving-degree proxies and charged multi-coordinate decomposition
cost \(C_{\mathrm{decomp}}(p,m)\) over toy prime fields, pinned to certificate
contract `1.0.0-review` from GOAL-ECDLP-001
(`TASK-20260722-012/certificate_contract.yaml`).

Uncertainty reduced: whether a lawful \(C_{\mathrm{decomp}}\) numerator can be
*specified* before any run — yes, as a non-scalarized resource vector under the
inherited conservation obligations, with matched rho/BSGS controls and toy claim
boundary.

## Inference

- requested_policy: `research-sol-max`
- resolved_model_id: `cursor-grok-4.5-high-fast`
- fallback_used: `true`
- authorization_ref: `AMEND-PATH-001-001`
- Equivalence to research-sol-max is not claimed.

## Authorization (non-negotiable)

No implementation or experiment is authorized by this design. Independent review
PASS is **not** auto-execution license: a separate Coordinator ledger
authorization is required before any measurement task may be admitted.

GOAL-ECDLP-001 toy validation protocol PASSed (`DEC-20260725-025`) for
fixture + sealable empty/pilot schedule pins. Activation residuals remain open
(`independent_verifier_artifact_sha256` null; precommit snapshot fields
unverified). This SDEG card **inherits that hard gate** and adds its own
`SDEG_PROTOCOL_REVIEW_NOT_PASSED` / separate-authorization gates. Present-tense
non-authorization is explicit in `scaling_protocol.yaml`.

## GOAL-ECDLP-001 alignment

| Pin | Status for SDEG BATCH-001 |
|---|---|
| Contract schema/version `1.0.0-review` | Inherited as read-only obligation set |
| Claim tier `toy`, ≤32-bit fields | Frozen |
| `no_scalarization: true` + stage charging | Frozen for \(C_{\mathrm{decomp}}\) |
| Decomposition certificate + independent verify | Mandatory for any `RELATION_VALID` |
| Exhaustive terminal vocabulary | Inherited (`rank-failure-terminal-v1`) |
| Nine planted conservation controls | Required before campaign certificate PASS |
| Forbid `ceil(r/p_L)` | Inherited |
| ECDLP concrete fixture/schedule hashes | Reference for schema alignment only; **not** SDEG ladder fixtures |
| Verifier hash / precommit activation | Still null / blocked — no execution |

## What was frozen

1. **Ladder cells** — toy bit sizes `{8,10,12,16,20,24}` (hard cap 32) with
   \(S_3\) (\(m=2\)) and \(S_4\) (\(m=3\)) cells, factor-base size rules, and a
   materialization rule for later hash-bound public fixtures (bytes not sealed
   here).

2. **Solving-degree metrics** — `gb_basis_size`, `gb_max_total_degree`
   (implementation-bound proxies; **not** theoretical \(d_{\mathrm{reg}}\)),
   optional `d_ff_proxy` / `attained_d_solve` (null if uninstrumented), plus
   `is_trivial_ideal` / certificate-backed `decomposition_found`.

3. **\(C_{\mathrm{decomp}}(p,m)\)** — multi-coordinate
   `rank-failure-resource-v1` vector with additive/non-additive split, required
   stages (setup, relation_collection, linear_algebra, descent, verification),
   and explicit ban on single-scalar packaging for ICEX.

4. **Matched baselines** — sealed Pollard-rho and BSGS control campaigns under
   the same resource schema; comparison only by coordinatewise dominance.

5. **Seeds / budgets / stopping rules** — `seed_256_hex` with ≥3 replicas per
   cell; per-attempt and campaign caps; exhaustion → terminal codes; stop on
   conservation failure, activation residuals, proxy mislabel, or scalar rescue.

6. **Controls** — nine contract planted controls plus planted-decomposition
   positive control, random-target negative control, matched rho/BSGS, field/
   order checks, and monomial-order pin.

7. **Post-PASS executor gate** — review PASS only allows scheduling a later
   executor task; admission still requires verifier hash, sealed schedules,
   fixtures, Coordinator authorization, and ECDLP activation closure (or a
   named amendment).

## Novelty

`novelty_status: adaptation`. Corpus screen: KN-OPEN-002, KN-TECH-002/004,
KN-LIT-005/010/029, RQ-SDEG-001 / RQ-ECDLP-001. Known Semaev/Groebner
measurement methodology adapted to the Tier-path full-cost certificate contract;
not a new cryptanalytic mechanism. Web literature not re-fetched this session.

## Claim boundary

Toy-tier measurement protocol only. Does not claim asymptotic advantage
(\(\alpha < 1/2\)), crypto-scale relevance, ECDLP lower bounds, breakthroughs,
or identification of Groebner proxies with theoretical degree of regularity.

## Recommended next action

Archive via `TASK-20260725-642` and submit the immutable snapshot to
`TASK-20260725-643` red team; authorize no runs.
