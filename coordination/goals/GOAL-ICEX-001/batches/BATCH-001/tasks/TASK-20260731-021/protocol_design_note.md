# Protocol design note — TASK-20260731-021

## Purpose

Review-only frozen **end-to-end charged index-calculus exponent protocol** for
GOAL-ICEX-001 (Tier 2 / G7): aggregate admissible G4–G6 outputs into one
full-cost toy-scale IC-versus-Pollard-rho/BSGS comparison under certificate
contract `1.0.0-review`.

Uncertainty reduced: whether a lawful ICEX accounting equation and activation
gate can be *specified* before any run — yes, as multi-coordinate \(C_{\mathrm{IC}}\)
fed only by charged SDEG/MONO/RELN pins, with explicit bans on `ceil(r/p_L)`,
`p_exist` imports, KN-LIT-009 heuristic substitution, and illicit scalarization.

## Inference

- requested_policy: `research-sol-max`
- resolved_model_id: `cursor-grok-4.5-high-fast`
- fallback_used: `true`
- authorization_ref: `AMEND-PATH-001-001`
- Equivalence to research-sol-max is not claimed.

## Authorization (non-negotiable)

No implementation, measurement, or solver campaign is authorized by this design.
Independent review PASS is **not** auto-execution license: a separate Coordinator
ledger authorization is required, and ICEX remains non-executing until charged
SDEG/MONO/RELN **measurement packages** exist. Protocol PASS ≠ measurement ≠
crypto-scale.

## Feed pins (named decisions + artifacts)

| Feed | Decision | Protocol artifact | Charged ICEX symbols |
|---|---|---|---|
| **SDEG (G4)** | `DEC-20260725-015` | `GOAL-SDEG-001/.../TASK-20260725-641/scaling_protocol.yaml` | `C_decomp`, matched `C_rho`, `C_bsgs` |
| **MONO (G5)** | `DEC-20260725-027` | `GOAL-MONO-001/.../TASK-20260725-705/monodromy_protocol.yaml` | Labeled Chebotarev/toy envelope / family rates (structure context only) |
| **RELN (G6)** | `DEC-20260725-017` | `GOAL-RELN-001/.../TASK-20260725-661/decomp_probability_protocol.yaml` | Sole supply pin `declared_p_lower_solve` (+ charged `C_rel_trial`) |

Cost-honesty pattern inheritance: ECDLP toy validation
`TASK-20260725-697` / `DEC-20260725-025` and certificate contract `1.0.0-review`
(`no_scalarization`, five stages, forbid `ceil(r/p_L)`, nine planted controls).

All three G4–G6 decisions are **protocol-design PASSes only**. No empirical
`C_decomp`, census rates, or `p_L` numbers are fabricated or assumed here.

## Accounting equation

\[
C_{\mathrm{IC}}
=
C_{\mathrm{setup}}
\oplus C_{\mathrm{relation\_collection}}
\oplus C_{\mathrm{linear\_algebra}}
\oplus C_{\mathrm{descent}}
\oplus C_{\mathrm{verification}}
\]

under `rank-failure-resource-v1` (coordinatewise aggregation; **no** cross-unit
scalarization). Relation collection is built from charged SDEG `C_decomp` /
RELN `C_rel_trial` attempts. Relation supply uses **only**
\(p_L = \texttt{declared\_p\_lower\_solve}\). MONO envelopes are structure
context, never a `p_L` substitute. Baselines are matched `C_rho` / `C_bsgs`.

Per-coordinate toy exponent (where defined, \(\ell\) = subgroup order):

\[
\alpha_{\mathrm{coord}}[c]
=
\frac{\log C_{\mathrm{IC}}[c]}{\log \ell}.
\]

A predeclared primary coordinate carries the CI test against \(1/2\); other
coordinates remain mandatory for honesty and dominance checks. \(R_{\mathrm{gain}}=0\)
⇒ \(\alpha\) undefined.

**Forbidden:** `ceil(r/p_L)`; optimistic `p_exist` as charged supply; KN-LIT-009
`HEUR-SEMAEV-2015-4.3` as `p_L`; single-scalar “proof” of advantage.

## What was frozen

1. **Feed pin table** — exact decision IDs, task paths, charged symbols, and
   forbidden imports for SDEG/MONO/RELN.
2. **Full-cost vector accounting** — five named stages, additive/non-additive
   split, feed composition rules, matched rho/BSGS baselines.
3. **Exponent / discrimination** — \(\alpha_{\mathrm{coord}}\), primary-coordinate
   CI vs \(1/2\), coordinatewise dominance predicate, four outcome IDs.
4. **Certificates / controls** — decomposition + discrete-log certificates;
   nine planted conservation controls; feed-pin, no-ceil, no-scalar, MONO CM,
   matched baseline, and planted end-to-end controls.
5. **Activation gates** — review PASS, Coordinator auth, **measurement**
   packages from G4–G6 (not protocol PASSes alone), fixtures, sealed schedules,
   verifier hash, ECDLP residuals; present-tense non-authorization.
6. **Toy claim boundary** — ≤32-bit; protocol PASS ≠ measurement ≠ crypto-scale
   IC-beats-rho.

## Novelty

`novelty_status: adaptation`. Corpus screen: KN-OPEN-001, KN-TECH-003/008/035,
KN-LIT-006/009/025, RQ-ICEX-001 / GOAL-ICEX-001, and the three feed protocol
cards. Known full-cost IC-vs-rho accounting composed with Tier-path charged
feeds — not a new cryptanalytic mechanism. Web literature not re-fetched this
session.

## Claim boundary

Toy-tier protocol design only. Does not claim \(\alpha < 1/2\) at any scale,
crypto-scale relevance, ECDLP lower bounds, breakthroughs, or establishment of
KN-LIT-009 heuristics. A later toy CI excluding \(1/2\) would at most motivate a
separate medium-scale trend gate — never a crypto-scale IC-beats-rho claim.

## Recommended next action

Archive via `TASK-20260731-022` and submit the immutable snapshot to independent
red-team review; authorize no runs. Keep ICEX blocked on charged G4–G6
**measurement** packages before any aggregation/executor task.
