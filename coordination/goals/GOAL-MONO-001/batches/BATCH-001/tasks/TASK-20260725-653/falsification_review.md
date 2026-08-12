# TASK-20260725-653 falsification review

## Verdict

**REVISE**

Reviewed only Coordinator snapshot `TASK-20260725-652` at commit
`cad21623f2de3917016a8045543b64e67a776e6a` (parent
`65dbb18b4f48e32fc7a723cedcad53574eaea1aa`). The commit is reachable from
review `HEAD`, changes exactly the receipt plus the two producer artifacts, and
producer SHA-256 digests match the receipt:

| Artifact | SHA-256 |
| --- | --- |
| `monodromy_protocol.yaml` | `40550d5ee486bde95ec5027be8424e3cc054eda469fd92b8468ba87e1505ec28` |
| `protocol_design_note.md` | `8dd98a5e8cd3c744237a520d5b98aade7c382592133dda94d184dbeda95d82ba` |

Receipt still shows `pending_post_commit` with null commit metadata; Git
reachability plus exact path/hash binding is the durable evidence used.
Working-tree-only producer edits were not treated as durable evidence.

Inference for this review: requested `review-xhigh`, resolved
`cursor-grok-4.5-high-fast`, `fallback_used: true`, authorization
`AMEND-PATH-001-001`. Equivalence to `review-xhigh` is not claimed.

## What survives

- **Present-tense non-authorization.** `status: review_only_freeze`, explicit
  authorization text, design-note section, and `executor_gate_when_authorized`
  all forbid census execution now. Review PASS only unlocks later scheduling
  under a fresh write_scope plus separate Coordinator ledger authorization.
  PASS is not a barrier theorem or exceptional-locus discovery.
- **Automorphism controls.** `j ∈ {0,1728}` excluded from
  `random_ordinary_controls`, quarantined in `automorphism_artifact_panel`,
  audited by `CTRL-J-EXCLUSION`, and forbidden as sole exceptional-locus
  evidence — matches KN-OPEN-009’s artifact rule.
- **Exceptional positive-exhibition path.** `EXCEPTIONAL_LOCUS_TOY` requires
  named curves, reverification, and exclusion of automorphism artifacts;
  timeouts/infra → `failed_infrastructure`, not negative monodromy.
- **m=3 group-theoretic framing.** Deg_T=2 ⇒ only transitive subgroup of
  S_2 is S_2; full vs exceptional is equidistribution / positively deviant
  densities after controls. Higher-m wreath out of scope; EXP-MONO-001 m=2
  Legendre is harness prior art only.
- **Instrument block.** Planted split, S_3 identities, IMON product/random
  deg-5, and j-exclusion are present with fail-closed dispositions.
- **Toy forbids.** Crypto-scale monodromy, asymptotic barrier-from-census-alone,
  silent proxy→attack upgrade, and hypothesis/goal status change from this task
  are listed.

## Falsification axes

### 1. CM / automorphism controls — partially falsified

Automorphism quarantine is adequate. The CM screen is not.

`cm_exception_screen` is defined and never merged into random controls, but
`barrier_aggregate_rule` for `FULL_MONODROMY_BARRIER_TOY` does **not** require
any completed CM scoring. Concurrently, `require_prime_order_group: true` sits
on the shared `curve_search` / admission block with no CM-panel override.
Small-discriminant CM curves at the pinned toy primes often lack prime order,
so the written rules push toward `cm_screen_unavailable_at_prime` while still
allowing FULL.

KN-OPEN-009 names CM curves as the canonical exceptional family. A freeze that
can close exceptional-rate ICEX content without scoring that family fails the
CM-control completeness test.

### 2. Full vs exceptional claim boundaries — falsified

Two-sided discrimination and toy tiering are mostly well stated, but the FULL
outcome package overclaims:

- ICEX `FULL_MONODROMY_BARRIER_TOY` sets
  `attack_content: closed_at_toy_scope_for_exceptional_rate_sieves` even when
  CM was never scored (OBJ-653-1).
- `full_monodromy_reading` / ICEX “theorem-backed-at-toy-scope” language treats
  the pinned envelope `3·(2/√p)` as if Chebotarev forced that effective error
  for this Semaev cover. Chebotarev’s 1/2 prediction is theorem-backed; the
  multiplier/floor and census agreement are protocol pins (OBJ-653-3).
- At `p=211`, `3·(2/√p)≈0.413`, so the per-curve test is nearly vacuous alone
  (multi-prime aggregation partially mitigates; residual only).

**Cheapest discriminating mutation:** pass random-panel barrier checks on ≥3
primes, leave CM screen unavailable everywhere under the prime-order filter,
mint `FULL_MONODROMY_BARRIER_TOY`. Allowed by the frozen YAML; unacceptable
relative to KN-OPEN-009 / ICEX closure semantics.

### 3. Present-tense non-authorization — not falsified

No present-tense census, factorization campaign, or relation-rate measurement
is authorized. Residual: repair must preserve this split (protocol-review PASS
≠ execution admission ≠ mathematical result).

## Required repairs before PASS

1. **CTRL-CM-GATE-FULL.** Completed CM screen (≥8 scored ordinary CM curves,
   no reverified CM exceptions) hard-gates FULL / any ICEX package that closes
   exceptional-rate content; otherwise `SCOPED_PROTOCOL_NO_GO` or a qualified
   random-panel-only feed that does **not** close CM exceptional-rate content.
2. **CTRL-CM-ADMISSION.** CM panel may admit ordinary composite-order curves
   (still reject SS/anomalous); keep prime-order on random controls; log order
   and CM label.
3. **CTRL-CLAIM-WORDING.** Replace “forces” /
   “theorem-backed-at-toy-scope” with empirical agreement inside the pinned
   envelope; keep theorem-backed language for Chebotarev 1/2 only.

## Baseline comparison

No Pollard-rho, BSGS, or index-calculus path was run or authorized. Closest
baselines remain Chebotarev(S_2) split rate 1/2, the quasirandom window proxy
for ICEX planning, and Pollard-rho as the ECDLP cost the exceptional reading
correctly refuses to claim to beat. This REVISE mints no ECDLP advantage and no
barrier theorem.

## Narrowest supported statement

At `cad21623f2de`, the TASK-20260725-651 freeze correctly forbids present-tense
census execution and adequately quarantines `j=0/1728` artifacts, but does not
yet pin a CM-complete full-vs-exceptional decision procedure. Coordinator must
require a repaired protocol card before authorizing measurement.

## Next concrete action

Scoped repair producer → snapshot archive → re-dispatch independent red-team.
Do not schedule census execution under the unrepaired card.

Hand off to Coordinator ledger archive task `TASK-20260725-654`.
