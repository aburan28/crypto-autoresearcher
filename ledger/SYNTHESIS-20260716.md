# Coordinator synthesis — 2026-07-16 autoresearch session

**Goal:** find a novel *generic prime-field* ECDLP breakthrough (exponent change vs
Pollard rho) via this harness, tracking progress in commits.

**Method:** each direction run as a full harness cycle (RQ → H → frozen protocol →
executor run → evidence → coordinator decision), under AGENTS.md evidence rules:
matched controls, non-degeneracy verification, multi-seed replication, toy≠crypto scope.

## Programs run this session

| ID | Direction (fresh, in-bar) | Result | Verdict |
|---|---|---|---|
| REP-001 | Model-native PDP `d_reg`, Edwards vs Weierstrass, **m=2** | Both best-formulations `d_reg=2` (verified 0-dim, planted root) | reject_scoped |
| REP-002 | Same, **m=3** chained | Both `d_reg=2`, `vdim=6`; Edwards native is constant-factor *slower* | reject_scoped |
| ISO-001 | Isogeny-neighborhood audit (`d_reg` + decomposition yield), matched controls | No neighbor `d_reg<2`; yields inside control band | reject_scoped |

## Honest bottom line

- **No generic-prime-field exponent signal was found** at reachable (toy) scale. All three
  fresh directions produced **scoped negatives**, each with matched controls and
  non-degeneracy checks — not eyeballed, and not infrastructure failures.
- **Reusable findings** (reinforce, do not overturn, the prior corpus):
  1. The **curve model** (Weierstrass Semaev vs twisted-Edwards native) is **not a
     solving-degree lever**: the best formulation of each solves the membership-constrained
     PDP at `d_reg=2` for m=2 and m=3. A surprising-looking "Edwards wins" was caught as a
     formulation artifact (explicit-`y` sign branches) by the fair Semaev control — the
     harness working as intended. Reinforces IC-5 (model/symmetrization = constant-factor).
  2. **Isogeny structure** is not a PDP lever: solving degree and decomposition yield track
     coefficient variance, not the isogeny class.
- **Scope (AGENTS rule 6–7):** toy `p ≤ 2^16`, `m ≤ 3`, Edwards-admitting / small-degree
  isogeny families. These negatives close only the tested scope; they are consistent with,
  and add matched-control rigor to, the accumulated program-wide result that no in-bar
  mechanism (~30+ across the wider corpus, incl. the CI-backed R6 kill) beats rho.

## Standing assessment

A generic prime-field ECDLP breakthrough was **not** found and, on the accumulated
evidence, is not expected from the remaining catalogued directions. The harness now has a
working cycle and three committed negatives; the honest research value is the rigor and the
map of what does *not* move the exponent. Any future "win" must clear the Phase-5 red-team
gates (reproduce, scale, matched controls, independent inspection, explicit cost-vs-rho)
before it is recorded as anything above `preliminary` — and fabricating one would violate
AGENTS.md rule 9 and is out of the question.

## Next candidate directions (declining prior)

- Pair-selection learning (Phase 4.3): at `d_reg=2` only step-count constants remain; prior
  low (corpus SAT/ML found no scale win). 
- Representation search beyond model: elimination orders / alternative factor-base addresses
  (largely covered; low prior).
- The genuinely-open theoretical residuals remain **theory**, not toy experiments: the
  reverse black-box separation and a d_reg instrument past the memory wall (needs real F4/F5).
