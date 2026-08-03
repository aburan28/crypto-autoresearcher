# (O2) — no cheap sum-compatible filter on `E(F_p)`

Self-contained analysis of obstruction **(O2)** for `GOAL-ECDLP-001`: whether a
cheaply computable `h : E(F_p) → [M]` can satisfy `h(P+Q) = f(h(P), h(Q))` often
enough to drive a Wagner k-tree, and therefore move the ECDLP attack exponent
below Pollard rho's `1/2`.

**Answer: no, for the character-filter class under group-law or quasigroup
combining.** The `j = 2` four-tree at exponent `0.4167` — the last
exponent-moving configuration the campaign had identified — is closed.

**This is a barrier result, not an attack.** No speedup is claimed, no
`sota_delta` is positive, and all computation is toy scale (`N <= 65539`).

---

## Why this lives here and not under `coordination/`

These documents were produced under `GOAL-ECDLP-001` on branch
`feat/ecdlp-harness-experiments-54a06f`. That branch and `main` **independently
ran the same goal forward** from common ancestor `e7fd9038e`, allocating the
same `BATCH-*` and `TASK-*` IDs to different research — including two distinct
`BATCH-028`s. Merging it produces 66 conflicts, 62 of them add/add on immutable
records.

`AGENTS.md` forbids resolving that by picking a side; a Coordinator must issue
superseding records with fresh IDs. That adjudication is **still pending**
([#109](https://github.com/aburan28/crypto-autoresearcher/pull/109)).

So the mathematics is filed at a **neutral path that asserts nothing about batch
identity**, and merges cleanly. Nothing here depends on which `BATCH-028` is
canonical.

---

## Read in this order

| file | what it is |
|---|---|
| `claim_a_adjudication.md` | The adjudication that named (O2) and identified the surviving escape. |
| `F1_sum_compatible_filter_search.md` | The 507-family measurement sweep. Unfalsified, but a sweep, not an argument. |
| `O2_derivation_attempt.md` | **[D]** — Theorem 1 (exact case), Proposition 2 (no class-free proof exists), Theorem 3 (Weil/Bombieri bound). |
| `O2_fourier_obstruction.md` | **[F]** — Theorem A (`eps <= 1/M + Λ`, no factor `M`), Theorem B, exact identity. Carries a correction notice. |
| `O2_composition_closure.md` | **The composition.** [D]'s Weil bound into [F]'s Theorem A ⇒ `j = 2` closes. |
| `O2_quasigroup_gap.md` | **Theorem C** — the quasigroup escape, closed exactly; measured approximately. |
| `O2_quasigroup_scaling.md` | The missing control, run. Jacobson-Matthews sampling to `M = 32`; the `M` loss does not materialize. |

[D] and [F] were derived **independently and in parallel**, from the same parent
commit, neither session seeing the other. They agree numerically to 3–4 decimals
on shared quantities and hit the same `M²` barrier at the same step from
opposite directions.

## Reproducing

```bash
cd analysis/o2-sum-compatible-filters
python3 fourier_obstruction.py     # Theorems A/B verified to 1e-15, 18/18 configs
python3 charfilter_decay.py        # Λ ~ p^-1/2 on family C, 125x range in p
python3 quasigroup_gap.py          # exhaustive over all Latin squares, M = 3,4,5
python3 quasigroup_scaling.py      # Jacobson-Matthews sampling, M = 4,8,16,32
```

Pure `numpy`, a few minutes total. **Every count is exact whole-group
enumeration over all `N²` pairs — no sampled statistics anywhere.** The one
sampled quantity in the whole directory is the *search* over Latin squares in
`quasigroup_scaling.py` at `M > 5`, where exhaustive enumeration is infeasible;
that column is a typical-case statement and is labelled as such. The
worst-case-over-all-`f` column beside it is exact.

## The result

| `j` | needed `M` | exponent (`m=16`) | via `(★)` | **via Theorem A + Weil** |
|---|---|---|---|---|
| 2 | `p^{1/3}` | **0.4167** | open | **CLOSED** |
| 3 | `p^{1/4}` | 0.3750 | closed (boundary) | **CLOSED** |
| 4 | `p^{1/5}` | 0.4000 | closed | **CLOSED** |

## What is still open

1. **Approximate quasigroup combining.** Theorem C closes the exact case
   unconditionally; the approximate case is unrefuted but unrealized at every
   `M` where it can be measured — see `O2_quasigroup_scaling.md`, where the
   exact worst case over all `f` stays ~160x below the `(star)` ceiling at
   `M = 32`. No robust version of Theorem C is proved.
2. **Interval / bit-window filters** (F1 families A, B, I, J) — additive-character
   completion is sketched in [D] §7.6, not carried out.
3. **Arbitrary cheap `h`** — [D]'s Proposition 2 proves no group-theoretic
   argument can reach it. Only a definitional restriction closes it.
4. **(H1)**: the Weil/Bombieri bound is now **partially verified** — see
   `knowledge/literature/KN-LIT-7639.md`. Its form, its non-degeneracy
   hypothesis and its validity regime (`g << sqrt(q)`; here `g = 1`) are
   confirmed from a 2024 source; the explicit `(2g-2+2m)` constant and the
   general-`k` curve statement remain untraced. **(H3)**: the zero/pole count for `F_R` is asserted as `O(D)`, not
   carried out.
5. **Toy scale.** `N <= 65539` throughout. Under `AGENTS.md` rule 4 this is not
   crypto-scale validation of anything and is not offered as such. The theorems
   are asymptotic; the computations check their steps and their `p`-dependence.

## Claim tier

**Exploratory** under `docs/claims-and-verification.md`. `certificate.kind: none`
— no solve or relation is claimed. No `EXP-*`, `RUN-*`, `EV-*`, `DEC-*` or
hypothesis status is created or changed by this directory. Disposition of (O2)
belongs to the Reviewer and Coordinator.

Both derivations resolved to `claude-opus-5`, so their agreement is evidence
about the derivations, not an independent-backend check. Theorems A and C are
short enough to check by hand, which remains the intended mitigation.
