# Autolab task breakdown — runnable units from the attack catalog

*Discrete, self-contained tasks derived from the prime-field frontier (#145–156), the
paper's open problems, and the honest ledger's flagged gaps. Each is scoped so it can be
run as-is. The bar (from the framework): an idea is **alive** only if it changes an
exponent (`< 0.5`) or exhibits a **growing structural invariant** that plausibly forces
it at scale. Everything else is "interesting structure," not evidence.*

**Rubric per task:** Object · Win (alive) · Kill (wall) · Observable · Scale · Reuse · Cost.
**Tag:** **[in-bar]** = could move a core assumption (C/RANK/S6/ICLOSE/DREG); **[out-of-bar]**
= deployment/engineering/reproducibility (real, but not a generic-E/F_p exponent claim).
**Universal controls** (attach to every measurement): matched random polynomial system;
matched random curve (same order); same-order isogenous curve; extension-field positive
control (T-EXT, below); bootstrap CIs + a calibrated null on every scaling claim.

---

## Tier 1 — could move a core assumption (run first)

### T1. R6 — arbitrary explicit factor-base membership solve **[in-bar]**
- **Object:** prime curve `E/F_p`, `ℓ≈2²⁰…2³⁰`, `m=3,4`; system `S_{m+1}(x₁..x_m,x_R)=0`
  **+ explicit membership** `∏_{f∈𝓕}(x_i − x(f))=0` for an explicit birthday-sized index
  set `𝓕` (|𝓕|=ℓ^{1/m}). This is the narrowed R6 (the structured `x_i^q=1` case is done).
- **Win:** total solve-cost exponent `< 0.5` at growing `ℓ`, or `d_reg` bounded as `ℓ→∞`.
- **Kill:** `relation_cost × solve_cost ≥ √ℓ`; or the smooth-subgroup no-win signature
  (degree flat, time exponential) recurs.
- **Observable:** `d_ff`, `d_reg`, total wall-time vs `√ℓ`, fitted exponent + CI.
- **Scale:** `ℓ = 2²⁰,2²⁴,2²⁸,2³⁰` ; ≥8 random `R` per scale.
- **Reuse:** `semaev_tree_prime.py` (swap `x_i^q=1` → `∏(x−x_f)`), `dreg_measure.py`,
  `dsolv_scaling.py`; controls from `pkm_dreg_prime.txt`.
- **Cost:** medium. *The single highest-value open object.*

### T2. D6 — streaming-Macaulay d_reg past the memory wall **[in-bar]**
- **Object:** boolean chained Semaev system, `n` past the `n≈21` `D=4` memory wall.
- **Win:** `d_reg` **bounded** as `n→∞` (→ polynomial solve, ECDLP-threatening), or `d_reg`
  growing **slower than the matched semi-regular null** (a channel).
- **Kill:** `d_reg` tracks the semi-regular null (generic exponential growth → IC loses).
- **Observable:** `d_reg(n)` for Semaev and null, with bootstrap CIs; prediction interval
  at `n=30,50`.
- **Scale:** `n = 12,15,18,21,24,…` to the new ceiling.
- **Reuse:** **build new** sparse/streaming Macaulay or degree-tracked F4/F5 (the current
  `solved_vars_at_D` saturates at `D=4`); requires **T11** (faithful null) first.
- **Cost:** heavy — but the one run that can falsify the core. Prioritize the instrument.

### T3. D5 — Yokoyama semi-normality object **[in-bar]**
- **Object:** the recovered signature object (`D5_YOKOYAMA_OBJECT.md`): `Syz=(J:S)`,
  `NS(Syz)`, signatures `sig(f)=LM(RSC(f))`, `Φ(s)`, and `#G*` vs the generic `m·d^{m-1}`,
  across the CM panel {generic, j=0, 1728, −3375, 8000, −32768, isogenous}.
- **Win:** `#G* ≪ m·d^{m-1}` or `#NS(Syz)` collapses on some family.
- **Kill:** semi-normality holds (counts match `m·d^{m-1}`) on **all** panel families.
- **Observable:** `#G*`, `#NS(Syz)`, signature histogram per family.
- **Scale:** `m=2,3` ; field `q=2^16…2^24`.
- **Reuse:** `D5_YOKOYAMA_OBJECT.md` (definition), the classified source it cites; build a
  Singular/Sage S-polynomial-history instrument (NOT the old `normal()` proxy).
- **Cost:** medium. *Framework calls this the #1 test; do it on the right object.*

### T4. Arity reduction at V₄ + general-w **[in-bar]**
- **Object:** extend the `m=3` symbolic χ₂-resonance counter to **V₄** (three-chord tower),
  and lift `w` from numeric specialization to the **function field** `F_q(E)(λ's)` to make
  the `m=3` result a theorem rather than measurement.
- **Win (constructive):** genuine symmetric resonance rank **bounded + flat** on V₄ across
  generic+CM ⇒ arity reduction `[Proved, m≤4]` (upgrades T4-gap-1 of the §6 proof).
- **Kill (as attack):** a novel, selective, degree-growing m-ary resonance appears.
- **Observable:** genuine rank (ambient−onV, embedded-binary-guarded) vs D, per curve.
- **Scale:** D≤6, ≥6 w-values / function-field-general; CM panel.
- **Reuse:** `review_Vm_arity.sage` (the V₃ engine), `hunt_H7_formsearch_final.sage`.
- **Cost:** cheap–medium. *Two-sided: null = new theorem.*

### T5. D1 — syzygy / Betti channel of the Semaev ideal **[in-bar]**
- **Object:** minimal free resolution / graded Betti table of the Semaev ideal `I`
  (chained, `m=3`) vs a matched semi-regular control, per CM-panel curve.
- **Win:** extra Betti strands / multiplicity that **grow** with `n` and lower `d_reg`.
- **Kill:** Betti table matches the semi-regular control; deviations constant-sized.
- **Observable:** `betti(res(I))`, regularity, vs control; scaling of any extra strand.
- **Scale:** `n=9,12,15,18` ; `q=2^16…2^24`.
- **Reuse:** Singular `res`/`betti` via Sage (verified working); `semaev_tree.py` builder.
- **Cost:** cheap. *Structural, directly tied to solving complexity.*

---

## Tier 2 — sharpen / scale existing negatives to CI-backed status

### T6. Heavy-tail δ — scaling-in-p arm **[in-bar]**
- **Object:** the calibrated Rényi-2 + L∞ tail test, but **across primes** `2²⁰…2⁴⁰`
  (the unrun arm; current result is one curve at 2³²).
- **Win:** tail statistic above the permutation null **and growing with `log p`**.
- **Kill:** flat across `p` (family-wise, Holm-Bonferroni).
- **Observable:** `T_obs(p)` vs permutation-null band, slope vs `log p` + CI.
- **Scale:** ≥5 primes, ≥3 curves each, d≤4 with adequacy guard.
- **Reuse:** `review_renyi_calibrated.py` (generalize beyond the saved npz; sample fresh).
- **Cost:** medium.

### T7. Defect-B — genuinely adversarial deterministic oracle **[in-bar]**
- **Object:** the object the tautological experiment missed — a **fixed deterministic
  function of `c_k=a_k+b_k x`** (chosen *before* the keys), returning valid
  rank-structured decompositions; feed the verbatim T2 Stage-1/2 reduction.
- **Win:** e-block corank that **absorbs the −b column** (x undetermined) **and grows with
  ℓ**, from an oracle that does **not** read `b`.
- **Kill:** x stays recoverable (the information argument: oracle factors through `c_k`,
  `b_k` stays independent) ⇒ defect benign without DL.
- **Observable:** corank fraction, x-determinacy, min-N/|𝓕| across ≥3 `ℓ`.
- **Reuse:** `tier1_defectB.py` (replace the 3 hand-picked strategies with a `c_k`-keyed
  deterministic family + a search over such families).
- **Cost:** cheap. *The proof carries it; this tests whether any `c_k`-function breaks it.*

### T8. K1 / Néron–Severi — multiplicative chord rank on the CM panel **[in-bar]**
- **Object:** the **multiplicative** χ₂ resonant-rank counter (not the bit battery) on a
  small-disc CM panel + high-NS family, with φ-twisted generators (the genuinely
  uncomputed cell from the invalidation pass).
- **Win:** `ρ(V)` strictly above the generic value, on-V-selective, q-persistent.
- **Kill:** `ρ(V)=2` flat on every CM curve (matches generic).
- **Observable:** genuine selective rank per (curve, D), with the H7/H4/H6 guards.
- **Scale:** D≤6, `q=2^17…2^24`, CM disc swept.
- **Reuse:** `hunt_H7_formsearch_final.sage`, `channel_mixed_char.sage`,
  `/tmp/cm_chord_probe.sage`.
- **Cost:** cheap. *(Overlaps T4 on V; here it's the binary-surface CM sweep.)*

### T9. Deployed-prime δ — CI/null-backed **[in-bar, deployment-relevant]**
- **Object:** upgrade the smoke test: P-256/384/521 (Solinas), Curve25519, secp256k1
  (pseudo-Mersenne, j=0), each vs **multiple** random-prime baselines, with permutation
  null + bootstrap CIs, low- and high-bit predicates.
- **Win:** deployed-prime (signal−control) δ above the random-prime null band.
- **Kill:** within the null band on all deployed curves.
- **Observable:** δ-excess per curve vs null band; CI.
- **Reuse:** `review_deployed_primes.py` (add permutation null + CIs + more baselines).
- **Cost:** medium.

### T10. d_reg − d_ff gap growth **[in-bar]**
- **Object:** measure **both** first-fall `d_ff` and solving degree `d_reg` per `n`, ≥8 R;
  the *gap* `d_reg − d_ff` is what carries the exponential cost (the ledger's key point).
- **Win:** gap **bounded** (→ cheap solve) or growing slower than semi-regular.
- **Kill:** gap grows like semi-regular (generic).
- **Observable:** `d_ff(n)`, `d_reg(n)`, gap, with CIs.
- **Scale:** `n=9,12,15,18` (uncensor: raise `max_D` to 6).
- **Reuse:** `ic_first_fall_fast.py` (raise cap), `dreg_measure.py`.
- **Cost:** medium.

### T11. Faithfully-matched semi-regular null harness **[in-bar, infrastructure]**
- **Object:** the calibrated null that was **miscalibrated** in D6 (it injected linear
  monomials the Semaev system lacks). Build a null with **identical** monomial support /
  degree profile, only the coefficients randomized.
- **Win/Kill:** N/A — this is a reusable instrument; success = it reproduces known
  semi-regular `d_reg` (Bardet bound) on a control it should match.
- **Reuse:** `dsolv_scaling.py` `rand_dff` (fix the support), `macaulay_export.py`.
- **Cost:** cheap. **Blocks T2, T5, T10** — do early.

### T12. Best-IC-exponent with CIs **[in-bar]**
- **Object:** pin the actual best achievable IC total exponent (crossbred 0.863 vs MITM
  `(1/2+1/t)`≈0.667) with bootstrap CIs, to firm the compat-aware "loses by 2^43."
- **Win:** a fitted total exponent CI whose lower bound `< 0.5`.
- **Kill:** lower CI bound `> 0.5` (IC loses, quantified).
- **Observable:** fitted exponent + 90% CI for each solver path.
- **Reuse:** `crossbred_real_cost.py`, `crossbred_exponent.py`, `review_stacked_compat.py`.
- **Cost:** medium.

---

## Tier 3 — geometry / structure (lower prior, but cheap and structural)

### T13. D2 — singular locus of V_m **[in-bar]**
- **Object:** dimension/type of the singular locus of the Semaev variety `V_m`, per family;
  correlation with decomposition (relation) yield.
- **Win:** positive-dimensional singular component **correlated** with relation yield.
- **Kill:** singularities match generic expectation; no predictive value.
- **Observable:** `dim(Sing(V_m))`, component count, vs yield.
- **Reuse:** Singular `slocus`, `primdecGTZ`; `review_Vm_arity.sage` for V_m construction.
- **Cost:** cheap–medium.

### T14. D3 — Lang–Weil point-count deviation **[in-bar]**
- **Object:** `#V_m(F_q)` vs the Lang–Weil prediction `q^{dim} + O(q^{dim−1/2})`, per
  family; degree/component anomalies.
- **Win:** persistent deviation beyond the Lang–Weil error band, correlated with PDP success.
- **Kill:** counts follow the generic prediction.
- **Observable:** point counts vs LW band across q; per CM family.
- **Scale:** `q=2^12…2^20` (exact counts feasible), `m=2,3`.
- **Reuse:** Sage point enumeration; `addition_surface_charsum.py`.
- **Cost:** medium.

### T15. D7 — isogeny spectral gap **[in-bar, weak-neighbor theory]**
- **Object:** ℓ-isogeny graph expansion / mixing on the relevant ordinary class; look for
  non-Ramanujan regions or weak-curve concentration (the P-256 "weak-neighbor" thread).
- **Win:** poorly-mixing region / trap structure correlated with a weaker same-order curve.
- **Kill:** near-Ramanujan expansion, polylog mixing, uniform hardness.
- **Observable:** second eigenvalue of the isogeny graph; weak-curve density per region.
- **Reuse:** `isogeny_walk_weak_search.py`, the P256_HIDDEN_STRUCTURE / isogeny-semaev work.
- **Cost:** medium. *Low prior of a real attack (idea #23 already falsified the walk).*

### T16. Composite / hybrid adversary cost model **[in-bar]**
- **Object:** model an attacker **stacking** a sub-constant separability nudge × batching ×
  a favorable constant simultaneously (every existing bound is per-mechanism).
- **Win:** a composite whose total exponent `< 0.5`.
- **Kill:** the composite still has exponent `≥ 0.5` (compat-aware: levers don't multiply).
- **Observable:** symbolic/numeric composite cost vs `√ℓ` at n=256.
- **Reuse:** `review_stacked_compat.py` (extend to cross-step composition + a sliver of
  exponent help, not just constants).
- **Cost:** cheap (analysis).

### T17. Cross-instrument CM probe — one curve, full stack **[in-bar, methodology]**
- **Object:** run **all** instruments (V_m resonance, δ heavy-tail, K2 d_reg, NS rank,
  syzygy/Betti) on **one** small-disc CM curve, looking for a **correlated** cross-instrument
  signal — the invalidation pass's own punchline, never run as one object.
- **Win:** a signal that is jointly elevated across ≥2 instruments on the same curve.
- **Kill:** every instrument flat (independently and jointly).
- **Observable:** the joint instrument vector vs a matched generic curve.
- **Reuse:** T4, T5, T6, T8 harnesses pointed at one curve.
- **Cost:** medium (after the component harnesses exist).

---

## Reproducibility & practical (out-of-bar, but real)

### T18. Persist the width-32/64 MLP distinguisher **[out-of-bar, reproducibility]**
- **Object:** the §5 "ML to width 64" closure currently lives in the ephemeral
  `/tmp/p3_train.py`; re-run at d=16/32/64 and **persist** alongside the Walsh result.
- **Win/Kill:** N/A (closes a reproducibility debt; a "Measured" tag that can't be
  regenerated is a Conjecture).
- **Reuse:** `/tmp/p3_train.py` content (in transcript), `results/lastcorner_P3_points.npz`.
- **Cost:** cheap (needs system `python3` + torch, not `sage -python`).

### T19. Real-library validation-gate audit **[out-of-bar, deployment]**
- **Object:** run the `DEPLOYMENT_GATE_PROBE.md`/`NONCE_FAULT_AUDIT.md §5` checklist against
  actual source: OpenSSL `EC_POINT`/`EC_GROUP_check`, libsecp256k1, Go `crypto/elliptic` +
  `crypto/ed25519`, BoringSSL, libsodium.
- **Win:** a shipped library accepts a constructed weak curve / lacks hedging.
- **Kill:** all audited libraries implement the full gate + hedged nonces.
- **Observable:** per-library checklist (point-on-curve, cofactor, n≠p, embedding degree,
  twist security, nonce hedging).
- **Reuse:** `deployment_gate_probe.py` curves as test vectors. **Blocked on having source.**
- **Cost:** medium. *Needs a checkout — name the library.*

### T20. Deterministic-nonce fault-model matrix → runnable PoCs **[out-of-bar, done+extend]**
- **Object:** the survey (`NONCE_FAULT_AUDIT.md`) reproduced single-bit; extend to runnable
  PoCs for instruction-skip and word-corruption faults on Ed25519/RFC6979/BIP340.
- **Win/Kill:** N/A (reproduction/coverage; protocol-layer).
- **Reuse:** `review_eddsa_fault.py` (generalize the fault model).
- **Cost:** cheap.

---

## Controls / anchors (must run alongside the negatives)

### T21. Extension-field positive control (Gaudry–Diem) **[anchor]**
- **Object:** reproduce sub-`√#E` index calculus on `F_{qⁿ}`, `n=3,4,5`, fixed small `q`.
- **Win (expected):** exponent `< 0.5` over the extension field — this is the **positive
  control** every prime-field negative is contrasted against (rubric requirement).
- **Kill:** if it does NOT beat `√#E`, the whole instrument is suspect.
- **Reuse:** `exp74_invfree_divisor_sieve.py`, the IC ladder; Gaudry–Diem Semaev `m=n+1`.
- **Cost:** medium. *Calibrates that "IC loses" on F_p is a real wall, not a broken solver.*

### T22. Genus-2/3 Jacobian transfer contrast **[anchor]**
- **Object:** the Jacobian IC where it genuinely wins (Diem genus-3), as a contrast anchor
  for the prime-field stall.
- **Win (expected):** faithful transfer to an easier Jacobian DLP.
- **Kill:** transfer asymptotically slower (cover-genus growth overwhelms).
- **Reuse:** `exp72_mumford_ic_dff.py` (sic), `exp64_scholten_weil_restrict_ic.py`,
  `exp106` Smith (2,2,2).
- **Cost:** medium.

### T23. Crossbred minimum-exponent re-confirmation at larger n **[anchor]**
- **Object:** push the crossbred per-PDP exponent measurement past the current ceiling to
  confirm 0.86 total is stable (firms T12).
- **Win:** total exponent CI lower bound `< 0.5`.
- **Kill:** stable at ~0.86 (loses to rho).
- **Reuse:** `bitpacked_solver.py`, `crossbred_kfrac_sweep.py`.
- **Cost:** heavy.

### T24. Rho baseline constant re-verification at scale **[anchor]**
- **Object:** confirm the `0.886√N` (negation) / `1.253√N` baseline constant the whole
  comparison rests on, at the largest feasible `N`, with CIs.
- **Win/Kill:** N/A (calibration); a wrong baseline constant invalidates every "loses by"
  statement.
- **Reuse:** the rho-constant verification (task #47).
- **Cost:** medium.

---

## Run order (dependencies)

1. **First:** T11 (null harness) — blocks T2/T5/T10; T24 (baseline) — blocks all "loses by".
2. **Tier-1 cheap wins:** T4 (arity V₄), T5 (Betti), T3 (D5 Yokoyama), T7 (Defect-B det.),
   T8 (CM χ₂ rank).
3. **Tier-1 medium:** T1 (R6 arbitrary-index), T6 (heavy-tail scaling), T10 (d_reg−d_ff),
   T9 (deployed CI).
4. **Tier-1 heavy (the falsifier):** T2 (streaming d_reg) — needs T11.
5. **Anchors throughout:** T21 (must pass), T24 (must hold).
6. **Tier-3 / practical as capacity allows:** T13–T17, T18–T20, T22–T23.

**Honest note:** by the framework's own bar, the *expected* outcome of the in-bar tasks is
another stream of KILLs (the program has produced zero in-model survivors across ~30
mechanisms). The value is (a) **T1/T2/T3** are the three that could genuinely move a core
assumption, (b) every KILL now carries **CIs + a calibrated null + the positive control
T21**, so "no signal" finally means "instrument that can see a signal saw none," not
"instrument too small." T4 is the one with a **constructive** upside (null = theorem).

---

## Headline integrative gate — added 2026-06-25

### T-SHOUP. Sub-√ℓ total-cost gate: strongest structural solver vs the generic baseline **[in-bar]**

*Why this task exists, stated honestly:* the generic-group lower bound (Nechaev '94,
Shoup '97) is a **theorem** — any algorithm that touches the group only through the group
law and equality test needs `Ω(√ℓ)` operations. So this task is **not** "beat √ℓ
generically" (provably impossible); it is "does a **non-generic, curve-structure-exploiting**
solver's *measured total cost exponent* dip below `0.5` on a defined `E/F_p` family,
beating every generic control?" That is the only sense in which the bound can be beaten,
and it is exactly what the lab's `< 0.5 exponent` bar already encodes. **The generic bound
is the control, not the target.**

- **Object:** prime curve family `E/F_p` over a size ladder `ℓ ≈ 2²⁰…2⁴⁰`. Run the
  strongest available non-generic pipeline end-to-end to recover a *known* `k` in `R=kP`:
  chained-Semaev `m=3` index calculus with the **explicit birthday factor base** (the
  T1/R6 configuration, `|𝓕|=ℓ^{1/3}`). Cost metric = **group-operation-equivalent total**
  = `relation_cost × solve_cost`, not solve-only.
- **Win (alive — sub-Shoup):** fitted total-cost exponent `α < 0.5` with the **upper**
  bootstrap-CI bound also `< 0.5`, on `≥4` ladder points; **or** `d_reg` provably bounded
  as `ℓ→∞` (forces polynomial solve). Either must beat **all four controls** below.
- **Kill (Shoup wall holds):** `α ≥ 0.5` / CI overlaps `0.5` and tracks the rho baseline;
  or the smooth-subgroup no-win signature recurs (`d_reg` flat, time exponential).
- **Observable:** relation count + cost, `d_ff`, `d_reg`, solve wall-time, total vs `√ℓ`,
  fitted `α` + bootstrap CI; the generic-baseline exponent printed side-by-side (must land
  at `0.5`).
- **Controls (mandatory — these separate a real win from a bookkeeping leak):**
  (1) generic baseline = Pollard-rho / BSGS on the same instances (the null, must sit at
  `√ℓ`); (2) matched random curve, same order; (3) same-order isogenous curve;
  (4) matched random polynomial system of identical shape with curve structure stripped.
  A win must beat **all four**.
- **Scale:** `ℓ = 2²⁰,2²⁴,2²⁸,2³²,2³⁶(,2⁴⁰)`; `≥8` random `R` per scale; `≥3` curves.
- **Reuse:** `src/semaev_tree_prime.py`, `src/dreg_measure.py`, `src/dsolv_scaling.py`;
  baseline `src/pollard_rho.py` + `src/sage_baseline.py`; framework bootstrap-CI + null
  harness (T11) and verified rho-constant (T24) — **both are hard prerequisites.**
- **Cost:** heavy. This is the **integrative gate** that composes T1 (relation side) and
  T2/T5 (solve side) into one controlled, sub-√ℓ exponent claim. It does not invent a new
  mechanism; it is the honest scoreboard for whichever mechanism is currently strongest.
- **Prereqs / run order:** after **T11** (null) and **T24** (baseline constant); consumes
  **T1** and **T2** outputs. Slot at the **end of step 4** in the run order above.

**Expected outcome (framework's own prior):** another **KILL** — ~30 in-bar mechanisms have
produced zero in-model survivors, and the generic bound is a theorem, so a positive result
here would mean a *specific structural defect of this curve family*, not a generic speedup.
The deliverable is a single CI-backed number stating exactly how far the best current attack
sits from `√ℓ`, with all four controls attached.

**Driver note:** model-agnostic. GLM-5.2 (UD-IQ1_M, 224 GB) cannot drive this on the
48 GB M4 Pro — it pages off external SSD at < 0.1 tok/s. For a local driver use GLM-4-32B
Q4 (~19 GB, fits); otherwise drive via an API model. The task runs standalone regardless.
