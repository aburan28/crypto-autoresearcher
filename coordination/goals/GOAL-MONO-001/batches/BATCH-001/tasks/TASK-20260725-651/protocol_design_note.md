# Protocol design note — TASK-20260725-651

## Purpose

Review-only freeze of a **toy-scope Frobenius cycle-type / monodromy census**
for the **m=3 Semaev summation cover**, under GOAL-MONO-001 / RQ-MONO-001 /
KN-OPEN-009. This card pins sampling, histogram metrics, error tolerance,
CM/automorphism controls, and claim boundaries for full vs exceptional
monodromy. It does not execute a census.

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

## Cover and census design

**Object.** Short-Weierstrass \(E/\mathbb{F}_p\colon y^2=x^3+Ax+B\). The cover
is Semaev \(S_3(x_1,x_2,T)\) (KN-LIT-001), viewed as a univariate in \(T\) of
degree \(2^{m-2}=2\) after a pinned monic-in-\(T\) normalization. For each
seeded sample \((x_1,x_2)\in\mathbb{F}_p^2\), record the Frobenius cycle type
from exact factorization of \(f_{x_1,x_2}(T)\).

**Why m=3 is still two-sided.** At degree 2 the only transitive subgroup of
\(S_2\) is \(S_2\) itself, so “full monodromy” means Chebotarev(\(S_2\))
equidistribution of split \((1,1)\) vs inert \((2)\) (KN-LIT-039), while
“exceptional” means a **positively exhibited** ordinary locus whose densities
deviate beyond the Weil envelope after controls — not a silent \(j=0/1728\)
artifact. Higher-\(m\) wreath/\(S_d\) resolution is out of scope here.

**Pinned sizes.** Primes \(\{211,431,809,1601\}\), master seed `20260725`,
\(\ge 20\) ordinary prime-order curves per size on \(\ge 3\) sizes, \(30\,000\)
samples/curve, toy factor-base window \(W=4\) for a joint relation-rate proxy.

**Primary metrics.** Frequencies of `split_1_1`, `inert_2`, `ramified`,
`degree_drop`; `delta_split_vs_S2` against prediction \(1/2\); Weil floor
\(2/\sqrt{p}\); `delta_over_weil`; plus `joint_relation_proxy_rate` vs
quasirandom prediction for GOAL-ICEX-001 feed.

**Error tolerance.** Full-monodromy agreement on the random control panel:
\(|\Delta_{\mathrm{split}}| \le 3\cdot(2/\sqrt{p})\) on every admitted curve.
Exception candidates with larger deviation require an independent second
factorization path before admission.

## Controls

| Control | Role |
| --- | --- |
| Planted split identity stream | Positive: rate exactly 1.0 |
| Uniform / shuffled window | Negative quasirandom checks |
| IMON product-cover \(g_2 g_3\) | Harness can flag non-full groups |
| IMON random deg-5 | Harness matches Chebotarev(\(S_5\)) |
| \(S_3\) addition identities | Coefficient normalization pin |
| \(j\in\{0,1728\}\) exclusion audit | Random-control purity |

**Panels (never mixed).**

1. `random_ordinary_controls` — ordinary, prime-order, non-anomalous,
   non-supersingular; **exclude** \(j=0,1728\).
2. `cm_exception_screen` — explicit CM / small-discriminant curves, scored
   only as an exception screen.
3. `automorphism_artifact_panel` — \(j=0/1728\) quarantine; cannot alone mint
   an exceptional attack locus.

Prior EXP-MONO-001 phase-1 (m=2 Legendre split) is harness prior art only; it
is **not** m=3 Semaev monodromy evidence. Primary metric must factor
\(S_3(x_1,x_2,T)\) in \(T\).

## Claim boundaries

- **Toy tier only.** No crypto-scale monodromy or asymptotic barrier theorem
  from this census alone.
- **Full monodromy** (`FULL_MONODROMY_BARRIER_TOY`) is a **barrier outcome** at
  tested scope: Chebotarev forces quasirandom split rates up to the stated
  Weil error. It closes exceptional-rate sieve *content* at toy scope; it does
  not prove \(G=S_2\) for all ordinary curves at all primes.
- **Exceptional locus** (`EXCEPTIONAL_LOCUS_TOY`) must be **positively
  exhibited** with named curves, panel IDs, and reverification receipts, after
  excluding automorphism artifacts. Family-scoped only.
- Timeouts / crashes / OOM → `failed_infrastructure`, never negative
  mathematical evidence.
- This task does not change hypothesis or goal status.

## Feed into GOAL-ICEX-001

Either decisive outcome supplies a labeled relation-rate input package:

- **Full:** quasirandom proxy
  \(\tfrac12\cdot(W_{\mathrm{eff}}/p)^2\) with Weil envelope on the split
  factor — calibration pin, not a crypto-scale rate law; exceptional-rate
  attack content closed at toy scope.
- **Exceptional:** per-family measured split / joint proxy rates only on the
  exhibited locus; generics keep quasirandom unless separately measured.
- **No-go / invalid controls:** do not mint an ICEX rate pin; MONO remains
  blocking.

## Ranking rationale (design choice)

This is the cheapest valid discriminator for KN-OPEN-009 at m=3: cycle-type
histograms plus Weil bookkeeping reuse the existing MONO/IMON harness
patterns, avoid solving Semaev systems, and still force a two-sided reading
(barrier calibration vs named exceptional family) that GOAL-ICEX-001 can
consume. The minimal first measurement, when later authorized, should run the
pinned prime list with the control block before any CM deep-dive — controls
fail closed.
