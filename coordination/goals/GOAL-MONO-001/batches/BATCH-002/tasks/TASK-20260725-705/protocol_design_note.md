# Protocol design note — TASK-20260725-705

## Purpose

Repair of the review-only m=3 Semaev-cover monodromy census freeze
(TASK-20260725-651 / snapshot `cad21623f2de`) to discharge RT-20260725-653
blocking objections OBJ-653-1 and OBJ-653-2, plus major wording OBJ-653-3
(DEC-20260725-016 / EV-MONO-001). This card supersedes the unrepaired protocol
for claim-boundary purposes; it does not execute a census.

## Inference

- requested_policy: `research-sol-max`
- resolved_model_id: `cursor-grok-4.5-high-fast`
- fallback_used: `true`
- authorization_ref: `AMEND-PATH-001-001`
- Equivalence to research-sol-max is not claimed.

## Authorization (non-negotiable)

No curve census, factorization campaign, or relation-rate measurement is
authorized by this design. Independent review PASS later only unlocks
*scheduling* of a future executor task under a fresh write_scope plus a
separate Coordinator ledger authorization. Review PASS is not a barrier
theorem and not an exceptional-locus discovery.

## What survived from TASK-20260725-651

- Automorphism quarantine: \(j\in\{0,1728\}\) excluded from random controls,
  artifact panel, CTRL-J-EXCLUSION.
- Present-tense non-authorization / `review_only_freeze`.
- EXCEPTIONAL_LOCUS_TOY positive-exhibition + independent factorization
  reverification.
- m=3 framing (only transitive subgroup of \(S_2\) is \(S_2\)); higher-\(m\)
  wreath out of scope; EXP-MONO-001 m=2 Legendre is harness prior art only.
- Instrument block: planted split, \(S_3\) identities, IMON product/random
  deg-5.
- Toy forbids: crypto-scale monodromy, asymptotic barrier-from-census-alone,
  silent proxy→attack upgrade, hypothesis/goal status change from this task.

## Repairs (OBJ-653-1 / 2 / 3)

### 1. CM hard-gate for FULL (OBJ-653-1 / CTRL-CM-GATE-FULL)

`FULL_MONODROMY_BARRIER_TOY` now requires a **completed** `cm_exception_screen`:
≥8 scored ordinary CM curves under the CM admission override, with no
reverified CM-panel exceptions beyond the pinned envelope. Missing or
unavailable CM screen **forbids** FULL and forbids any ICEX package that closes
exceptional-rate sieve content for unscored CM families.

If random-panel tests pass but CM is incomplete after the override, allowed
outcomes are only `SCOPED_PROTOCOL_NO_GO` or `RANDOM_PANEL_CALIBRATION_TOY`
(random-panel-only; `attack_content: not_closed_for_unscored_cm_families`).
This blocks the cheapest RT mutation: mint FULL while every prime logs
`cm_screen_unavailable_at_prime`.

### 2. CM panel admission override (OBJ-653-2 / CTRL-CM-ADMISSION)

`require_prime_order_group: true` remains the default for
`random_ordinary_controls` only. The CM panel explicitly overrides:

- `require_prime_order_group: false`
- `allow_composite_order: true`
- keep ordinary / non-supersingular / non-anomalous

Scored CM curves must log `group_order`, `order_is_prime`,
`cm_label_or_discriminant`, and `admission_override_applied: true`.
`cm_screen_unavailable_at_prime` is allowed only after exhausting this
override — and still never unlocks unqualified FULL.

### 3. Chebotarev / envelope wording (OBJ-653-3 / CTRL-CLAIM-WORDING)

- **Theorem-backed:** Chebotarev(\(S_2\)) prediction `split_1_1 = inert_2 = 1/2`
  only (KN-LIT-039).
- **Protocol pin / toy calibration:** empirical agreement envelope
  \(3\cdot(2/\sqrt{p})\). Not an effective monodromy theorem for the Semaev
  cover.
- Removed “Chebotarev forces…” and ICEX label
  `theorem-backed-at-toy-scope`. ICEX FULL package now uses
  `chebotarev_prediction_plus_toy_census_envelope`.

## Cover and census design (unchanged pins)

**Object.** Short-Weierstrass \(E/\mathbb{F}_p\). Cover is Semaev
\(S_3(x_1,x_2,T)\) (KN-LIT-001), univariate in \(T\) of degree 2 after pinned
monic-in-\(T\) normalization. Frobenius cycle type from exact factorization.

**Pinned sizes.** Primes \(\{211,431,809,1601\}\), master seed `20260725`,
≥20 ordinary prime-order curves per size on ≥3 sizes, 30 000 samples/curve,
toy factor-base window \(W=4\).

**Primary metrics.** Frequencies of `split_1_1`, `inert_2`, `ramified`,
`degree_drop`; `delta_split_vs_S2` against prediction \(1/2\); Weil floor
\(2/\sqrt{p}\); `delta_over_weil`; plus `joint_relation_proxy_rate` vs
quasirandom prediction for GOAL-ICEX-001 feed.

**Error tolerance.** Full-monodromy agreement on the random control panel:
\(|\Delta_{\mathrm{split}}| \le 3\cdot(2/\sqrt{p})\) on every admitted curve
(protocol pin). Exception candidates with larger deviation require an
independent second factorization path before admission.

## Panels (never mixed)

1. `random_ordinary_controls` — ordinary, **prime-order**, non-anomalous,
   non-supersingular; **exclude** \(j=0,1728\).
2. `cm_exception_screen` — explicit CM / small-discriminant curves under
   **composite-order admission override**; hard-gate for FULL; scored only as
   exception screen / gate.
3. `automorphism_artifact_panel` — \(j=0/1728\) quarantine; cannot alone mint
   an exceptional attack locus.

## Claim boundaries

- **Toy tier only.** No crypto-scale monodromy or asymptotic barrier theorem
  from this census alone.
- **Full** (`FULL_MONODROMY_BARRIER_TOY`): empirical census agreement within
  pinned envelope **plus** completed CM screen with no CM exceptions. Closes
  exceptional-rate sieve content at toy scope only under that gate.
- **Random-panel calibration** (`RANDOM_PANEL_CALIBRATION_TOY`): CM unscored;
  does **not** close CM exceptional-rate content; not aliasable to FULL.
- **Exceptional locus** (`EXCEPTIONAL_LOCUS_TOY`): positively exhibited with
  named curves, panel IDs, and reverification receipts after excluding
  automorphism artifacts. Family-scoped only.
- Timeouts / crashes / OOM → `failed_infrastructure`, never negative
  mathematical evidence.
- This task does not change hypothesis or goal status.

## Feed into GOAL-ICEX-001

- **Full (CM-gated):** quasirandom proxy
  \(\tfrac12\cdot(W_{\mathrm{eff}}/p)^2\) with pinned envelope on the split
  factor — labeled `chebotarev_prediction_plus_toy_census_envelope`;
  exceptional-rate attack content closed at toy scope **only** because CM
  gate passed.
- **Random-panel only:** planning proxy allowed; label
  `random_panel_only_cm_unscored`; CM exceptional-rate content **not** closed.
- **Exceptional:** per-family measured rates on the exhibited locus only.
- **No-go / invalid controls:** do not mint a charged ICEX rate pin; MONO
  remains blocking.

## Ranking rationale

Cheapest valid discriminator for KN-OPEN-009 after RT-653: keep the same
cycle-type / Weil bookkeeping, but force CM scoring (under a non-empty
composite-order admission rule) before any FULL / exceptional-rate closure
package can be minted. The minimal first measurement, when later authorized,
should run controls → random panel → CM screen under the override before any
ICEX pin; controls and CM-gate fail closed.

## Residual notes (non-blocking; inherited from RT-653)

- At \(p=211\), \(3\cdot(2/\sqrt{p})\approx 0.413\); multi-prime aggregation
  remains required.
- CTRL-NEG-UNIFORM-WINDOW tolerance is a smoke check only.
- Exact monic \(S_3\) helper hash remains an executor-card pin under
  CTRL-S3-IDENTITY.
