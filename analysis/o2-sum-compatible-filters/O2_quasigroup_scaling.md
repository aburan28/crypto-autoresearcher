# The missing control, run — the `M` loss does not materialize

Runs the control `O2_quasigroup_gap.md` §4 and §6.1 declared missing, and which
that document named as *"the cheapest thing that could still overturn §3"*.

**Status: EXPLORATORY ANALYSIS.** No frozen specification, no `EXP-*`, `RUN-*`,
`EV-*`, or ledger record is created or modified. Claim tier *exploratory*.
`certificate.kind: none`.

---

## 0. Answer first

| Question | Answer |
|---|---|
| Was §3's finding an artifact of tiny `M`? | **No.** Extending to `M = 8, 16, 32`, the quasigroup excess **decreases** — 0.076 → 0.004. It never tracks `M`. §2 |
| Does the worst case over *all* `f` realize the `M` loss? | **No, and this is exact rather than sampled.** `excess_arb <= 0.196` where `(★)` permits 32 — loose by ~160×. §3 |
| Does that bound worst-case quasigroups? | **Yes, rigorously.** Quasigroups ⊂ all `f`, so the exact arbitrary-`f` maximum caps them. §3 |
| Anything new about *why*? | Yes. On `dlog mod M` the group law separates sharply from quasigroups — `excess_grp` → 0.470 while `excess_quasi` → 0.014. §4 |
| Is the closure overturned? | **No — it is strengthened.** The gap §5.1 of the composition flagged is empirically absent at every `M` tested. |

---

## 1. What was owed, and the sampler

`O2_quasigroup_gap.md` enumerated **all** Latin squares of order 3, 4, 5 and
found the normalized excess `(eps − 1/M)/Λ <= 0.17`. It then stated plainly that
this could **not** separate *"quasigroups are special"* from *"`M <= 5` is too
small for the loss to appear"*, because the arbitrary-`f` excess was small there
too. The discriminating question is how the excess **scales with `M`**.

Exhaustive enumeration dies at `M = 6` (`8.1 × 10^8` squares), so this samples,
using **Jacobson–Matthews** — the standard Markov chain that is uniform on Latin
squares.

**A cheaper sampler was deliberately rejected.** Permuting rows, columns and
symbols of the cyclic table yields only isotopes of the cyclic **group**, which
are group-like by construction. Using it would have rigged the control toward
this program's own conclusion. This is exactly the null-object discipline
`docs/inventor-protocol.md` §3 requires, applied to the sampler itself.

Four comparators at matched sample size (`K = 600`) so maxima are comparable:
`eps_grp` (group law), `eps_quasi` (max over `K` uniform Latin squares),
`eps_randf` (max over `K` uniform arbitrary `f` — matched null, **not**
tree-usable), and `eps_arb` (**exact** max over all `f`, computed as
`Σ_{a,b} max_c C[a,b,c]`, not sampled).

Curve `p = 8219`, `a = b = 1`, `N = 8117` prime. All triple counts exact over all
`N²` pairs by cyclic convolution — no sampling in the counts.

---

## 2. The scaling

```
    filter    M    Lambda  excess_grp  excess_quasi  excess_randf  excess_arb  (star) cap
   x mod M    4   0.04076       0.044         0.076         0.097       0.125           4
   x mod M    8   0.04076       0.024         0.029         0.044       0.195           8
   x mod M   16   0.04076       0.014         0.010         0.019       0.196          16
   x mod M   32   0.04086       0.011         0.004         0.005       0.144          32

dlog mod M    4   0.90032       0.278         0.278         0.243       0.278           4
dlog mod M    8   0.97450       0.385         0.120         0.072       0.385           8
dlog mod M   16   0.99359       0.440         0.035         0.033       0.441          16
dlog mod M   32   0.99839       0.470         0.014         0.010       0.471          32
```

**`excess_quasi` decreases monotonically in `M`** on both filters — `0.076 →
0.029 → 0.010 → 0.004` and `0.278 → 0.120 → 0.035 → 0.014`. If quasigroups
realized the `(★)` loss this column would grow like the last one. It moves the
opposite way.

`excess_quasi ≈ excess_randf` throughout: **quasigroups behave like random
predictors**, not like adversarial ones.

---

## 3. The exact worst case, which is stronger than the sample

`excess_arb` is **not sampled**. It is the exact maximum over every `f : [M]² →
[M]`, computed in closed form. It stays `<= 0.196` while `(★)` permits `M = 32`
— the bound is loose by a factor of about **160** at `M = 32`.

Two consequences.

1. **Worst-case quasigroups are rigorously capped.** Quasigroups are a subset of
   all `f`, so `excess_quasi <= excess_arb <= 0.196` **exactly**, for these
   filters, at these `M`, on this curve. The sampling limitation of §2 does not
   apply to this statement — the `K = 600` maximum is a lower bound on the
   quasigroup worst case, but `excess_arb` is an exact upper bound on it.
2. **The `M` loss is a proof artifact here, not a phenomenon.** No `f` whatever —
   quasigroup, adversarial, or otherwise — comes within two orders of magnitude
   of the `(★)` ceiling on the filters measured.

---

## 4. An unforced separation

On `dlog mod M` the two columns move **in opposite directions** as `M` grows:

```
   M:            4       8      16      32
   excess_grp    0.278   0.385   0.440   0.470     <- grows
   excess_quasi  0.278   0.120   0.035   0.014     <- shrinks
```

At `M = 32` the group law does **34×** better than the best of 600 random
quasigroups. The dlog filter's exploitable structure is *group* structure, and
only the group law can see it — a random quasigroup is blind to it.

This is Theorem C's exact-case rigidity showing up as an approximate tendency,
which is what §6.2 of `O2_quasigroup_gap.md` asked for and could not prove. It
is **evidence, not a theorem**: no robust version of Theorem C is established
here.

---

## 5. Limits, stated plainly

1. **Two filters, one curve, `M <= 32`.** The regime that matters is
   `M ≈ p^{1/3}` at cryptographic `p` — orders of magnitude away. Under
   `AGENTS.md` rule 4 this is not crypto-scale evidence and none is offered.
2. **`excess_arb`'s exactness is per-filter.** It exactly bounds all `f` for the
   filters tested; it does **not** prove `(★)` is loose in general, since an
   adversary chooses the filter as well as the predictor.
3. **`K = 600` is a vanishing fraction** of the Latin squares of order 32. §2's
   quasigroup column is a typical-case statement; only §3's exact column speaks
   to the worst case.
4. **No theorem is proved here.** §4 is a tendency, not a robust Theorem C. The
   mathematical target of `O2_quasigroup_gap.md` §6.2 remains open.

---

## 6. Net effect

`O2_composition_closure.md` §5.1 listed approximate quasigroup combining as the
one route that could reopen the `j = 2` four-tree. That route is:

- **closed exactly** — Theorem C, unconditional;
- **empirically absent** at every `M` where it can be measured, with the
  worst-case-over-all-`f` bound exact and `~160×` below the `(★)` ceiling;
- **still unproved** in the approximate case, which is honest and unchanged.

The control that could have overturned the closure instead supports it.

---

## Inference

```yaml
inference:
  requested_policy: executor-implementation
  resolved_model_id: claude-opus-5
  reasoning_effort: null
  fallback_used: true
  fallback_reason: >-
    This Claude Code harness cannot resolve the policy aliases in
    orchestration/model-policies.yaml; subagent frontmatter supports only Claude
    models. Recorded, never silently substituted (AGENTS.md rule 11).
  degraded_allowed: false
  degraded_requirements: []
  model_verified: false
  model_verified_reason: >-
    `python3 -m orchestration.adapter doctor --probe` was not run in this
    session. The identifier is unverified configuration.
```
