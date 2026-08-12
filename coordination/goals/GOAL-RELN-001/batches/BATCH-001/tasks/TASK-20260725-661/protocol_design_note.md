# Protocol design note — TASK-20260725-661

## Purpose

Review-only frozen **decomposition-probability audit protocol** for
GOAL-RELN-001 (Tier 2 / G6): measure \(P(\mathrm{decomp})\) versus factor-base
size \(B=|V|\) for prime-field Semaev / Petit-Kosters-Messeng-style
constructions under matched controls, feeding GOAL-ICEX-001 relation-supply
budgeting.

Uncertainty reduced: whether relation supply can be *specified* honestly before
any run — yes, as dual metrics \(\hat p_{\mathrm{exist}}(B)\) (audit) and
charged \(\hat p_{\mathrm{solve}}(B)\) / Clopper-Pearson \(p_L\) (ICEX pin),
with contested KN-LIT-009 heuristics kept at confidence `reported`.

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
Activation residuals from GOAL-ECDLP-001 (null verifier hash / unverified
precommit) remain hard gates. Present-tense non-authorization is explicit in
`decomp_probability_protocol.yaml`.

## Literature diff (novelty)

`novelty_status: adaptation`.

| Source | Role in this protocol |
|---|---|
| KN-LIT-009 (Semaev 2015/310) | Contested heuristic \(P(q,m,t,\|V\|)\approx 1-(1-1/q)^{\|V\|^t/t!}\) (§4.3) pinned as **reported reference curve** `HEUR-SEMAEV-2015-4.3` only; asymptotic ECDLP claims stay `reported`, not established |
| KN-LIT-025 (Petit–Kosters–Messeng PKC 2016) | Direct prime-field prior art; secondary arm requires literature-derived fixture materialization before any PKM cell seal |
| KN-TECH-002 / KN-TECH-003 | Semaev summation polynomials + point-decomposition index calculus method pins |
| KN-OPEN-001 | Prime-field IC-vs-rho remains open; toy \(P(\mathrm{decomp})\) cannot settle it |
| EV-SEMAEV-001 / EXP-SEMAEV-001 | Prior fixed-\(B{=}14\) incidence 3/6 is an unresolved confound — this protocol replaces that gap with a controlled \(B\)-ladder |

Matching those constructions is adaptation, not novelty. Web check performed on
eprint 2015/310 (abstract + PDF §4.3). Full KN-LIT-025 primary text still not
in corpus — PKM equations are not invented here.

## What was frozen

1. **Constructions** — Primary `ARM-SEMAEV-SP` (\(S_3\)/\(m{=}2\) primary,
   \(S_4\)/\(m{=}3\) secondary). Secondary `ARM-PKM-PRIME` blocked on
   literature fixture materialization.

2. **Dual success metrics** — \(Y_{\mathrm{exist}}\) (toy enumeration oracle for
   mathematical existence) vs \(Y_{\mathrm{solve}}\) (charged algebraic solver
   with independent decomposition certificate). Only \(p_{\mathrm{solve}}\) /
   \(p_L\) feeds ICEX; oracle existence alone is forbidden as free relation
   supply.

3. **\(B\)-ladder** — Toy bit sizes \(\{8,10,12,16\}\) (hard cap 32) with
   explicit increasing \(B\) sequences (design defaults in YAML); fixtures and
   schedules not sealed in this batch.

4. **Sampling** — IID unconditional targets \(R=aP+bQ\); strata
   \((\mathrm{arm},p,m,B,\mathrm{solver})\); \(N\geq 64\) trials/stratum
   (target 128); `seed_256_hex` derivation pinned.

5. **Heuristic audit rule** — Predeclared match against
   `HEUR-SEMAEV-2015-4.3` (absolute tolerance or CI-overlap; choose one at
   seal). Match upgrades only to `measured_at_toy_scope` for that cell — never
   to established asymptotic complexity.

6. **Cost honesty** — Full stage attribution; every ICEX-feeding trial charges
   relation_collection; forbid `ceil(r/p_L)`; multi-coordinate resource vectors
   only.

7. **Controls** — Planted decomposition, negative random target,
   oracle/solve separation, \(B\)-monotone sanity, optional matched random FB,
   field/order checks, reported-label hygiene; conservation planted controls
   inherited when rank-yield certificates are claimed.

8. **ICEX feed** — Outcome packages
   `MEASURED_P_SOLVE_LADDER_TOY` / `HEURISTIC_REJECTED_AT_TOY_SCOPE` /
   `SCOPED_PROTOCOL_NO_GO` with required contents and forbidden substitutions.

9. **Post-PASS executor gate** — Review PASS only allows scheduling a later
   executor task; admission still requires verifier hash, sealed schedules,
   fixtures, Coordinator authorization, and ECDLP activation closure (or a
   named amendment).

## Claim boundary

Toy-tier measurement protocol only. Does not claim asymptotic advantage
(\(\alpha < 1/2\)), crypto-scale relevance, ECDLP lower bounds, breakthroughs,
or that KN-LIT-009 complexity exponents are established.

## Discrimination (what outcomes mean)

- **Heuristic tracks** at a toy cell → usable calibration reference for that
  cell; still not an asymptotic validation of Semaev 2015 complexity claims.
- **Heuristic misses** → ICEX must use measured \(p_L\) only; reported formula
  banned as substitute for missing cells.
- **Solve gap** (\(p_{\mathrm{exist}}\gg p_{\mathrm{solve}}\)) → relation supply
  bottleneck is solver/budget, not mere existence; ICEX must not use the
  oracle rate.
- **Control / certificate failure** → invalid measurement; not negative
  mathematical evidence against the mechanism.

## Recommended next action

Archive via `TASK-20260725-662` and submit the immutable snapshot to
`TASK-20260725-663` red team; authorize no runs.
