# Implementation notes — EXP-ECDLP-bbb42f

Executor: this session (policy `executor-implementation`, resolved model
`claude-sonnet-5`; `requested_reasoning_effort`/`reasoning_effort` recorded
as `null` exactly as the handoff's `inference` block wrote them — this
runtime does not expose the per-subagent effort dial to the running
process as a readable value, so it is disclosed as absent rather than
guessed).

## 0. Pre-execution contract validation (a disclosed anomaly)

`specification.yaml` line 13 sets `status: approved`, but the adjacent
`status_note` (lines 14–21) is stale draft boilerplate literally stating
"NOT `review_required` AND NOT APPROVED ... NO RUN OF THIS CONTRACT IS
AUTHORIZED." The bottom-of-file `approved_by_note` (lines 409–416), dated
2026-09-03, is more specific, more recent, and explicitly authorizes
execution: "Approval authorizes the Executor to run the bounded, seeded,
replicate design under this frozen contract." The dispatching handoff
(`TASK-20260903-58449b`) independently instructs execution of this same
contract. I proceeded on the `approved_by_note` + handoff basis, flagging
the stale `status_note` as an anomaly requiring a Coordinator amendment to
scrub, rather than silently resolving the contradiction or halting on it.

## 1. Language / library choice

Pure Python 3.13 + `sympy` (for exact polynomial factorization over
`GF(p)` and integer factorization). No `gmpy2` (not installed in this
environment). Sage is installed (`/usr/local/bin/sage`) but every
invocation hit a sandbox write restriction on `~/.sage/cache` that could
not be resolved without repeated `dangerouslyDisableSandbox` overrides
outside this task's write scope; pure Python was well within budget at
these toy sizes (see timings below), so Sage was not pursued further.

## 2. Core arithmetic — verified before trusting at scale

Every non-trivial routine was checked against an independent brute-force
or oracle computation *before* being used in a real run, per this
program's "recalled vs. retrieved/verified" discipline. Scripts retained
under `tests/` (moved there from a shared `.tmp/` scratch directory outside
this task's write scope — see §8):

- `ecc.py` (affine add/double/scalar-mult, Tonelli–Shanks): brute-force
  point counting on primes up to 100003 (`test_order.py` indirectly;
  direct affine arithmetic is standard and was exercised continuously).
- `curve_order.py` (BSGS group order in the Hasse interval, multi-point
  intersection): verified against brute-force point counting on primes
  97–1048583 (`test_order.py`, 40/40 trials). A real bug was caught and
  fixed here: the baby-step table can collide when a probe point's order
  is smaller than the table size (always true for composite-order test
  curves; never true for a curve this driver ultimately accepts, since
  acceptance requires prime N) — `debug_order.py` through `debug_order5.py`
  isolate and fix it.
- `isogeny2.py` (Vélu degree-2): verified via on-curve, homomorphism, and
  Tate-invariance (equal N) checks across curves at multiple primes
  (`test_isogeny2.py`, 39 curves, hundreds of point pairs each, 0 failures).
- `projective_ecc.py`: the projective addition/doubling formulas were
  **derived, not recalled** — mechanically cleared from `ecc.py`'s own
  verified affine formulas via `sympy` (`derive_projective.py`,
  `derive_projective_double2.py`), then re-verified against affine
  arithmetic (`test_projective.py`, 4900 checks, 0 failures). Needed for
  `sssa.py` (below), where the point `[p]P` reduces to the identity mod
  `p` and affine coordinates cannot represent that without hitting a
  non-invertible denominator.
- `sssa.py` (Smart/Satoh–Araki/Semaev anomalous-curve solver via the
  p-adic formal-group log at precision `p^2`): verified against 6 genuine
  anomalous curves found by direct search, 20–24 bits, 6/6 correct
  (`test_sssa.py`).
- `baselines.py` (Pollard rho with negation, BSGS): BSGS verified directly;
  an initial rho implementation using an ad hoc multiplicative walk failed
  to converge within 20×√N steps at every tested size (`test_baselines.py`
  first run) — replaced with the standard r-adding walk
  (Teske/Handbook-of-Applied-Cryptography style), which converges correctly
  and matches the true `k` at 20/24/28 bits.
- `isogeny3.py` (Vélu degree-3, kernel not required to be F_p-rational):
  **the single most error-prone part of this implementation.** Three
  successive closed-form derivation attempts were each wrong in a
  different way — (a) an ad hoc `y0`-elimination substitution loop that
  silently dropped/mis-signed terms, (b) a sign error in the `(x0-x)^3`
  vs. `(x-x0)^3` denominator (an odd power, so the sign matters), (c) a
  double-counted leading `+x`/`+y` term left over from misreading what
  `sympy.together()`/`fraction()` had already absorbed into the combined
  numerator. Each was caught by numeric testing against **two independent
  oracles** built from this driver's own verified `point_add`: one over
  `F_p` using a genuinely rational 3-torsion point, one over a hand-rolled
  `F_p^2` (`fp2_oracle.py`) for the far more common case where the kernel's
  y-coordinate is not itself `F_p`-rational. The final derivation
  (`isogeny3_final.py`) matches both oracles exactly and the resulting
  implementation passes 113/113 on-curve, homomorphism, and Tate-invariance
  checks across curves without the prime-N restriction (`test_isogeny3.py`).
  This episode is recorded in detail because it is exactly the kind of
  silent, plausible-looking error this program's verification discipline
  exists to catch before it reaches a run record.

## 3. Two load-bearing mathematical findings (not bugs — theorems)

### 3.1 ℓ₀=2 is provably vacuous for this experiment's entire curve population

`curve_sampling_rule` requires prime `N`. A rational point of order ℓ in
`E(F_p)` requires `ℓ | N` (Lagrange), which is impossible for prime `N`
and `ℓ ≠ N`. For ℓ₀=2 specifically, a rational 2-isogeny kernel is
*equivalent* to an actual F_p-rational 2-torsion point (the kernel
`{O,T}` has only one non-identity element, so Frobenius-stability of the
set forces `T` itself to be fixed). Consequence: **no curve this
experiment ever samples can have a rational 2-isogeny, at any bit size,
ever.** Confirmed empirically before being proven: 60/60 sampled census
curves across all three bit sizes had zero 2-torsion roots
(`check_psi3_census.py`-adjacent checks; `test_graph.py`).

### 3.2 ℓ₀=3 avoids the Lagrange obstruction, but only when p ≡ 1 (mod 3)

A degree-3 kernel `{O,T,-T}` only needs `T`'s x-coordinate to be
Frobenius-*fixed* (a root of the 3-division polynomial in F_p) — Frobenius
is free to *swap* `T ↔ -T`, which still leaves the kernel set stable
without `T` itself being an F_p-point. So Lagrange on `N` does not apply.
Whether a root exists is governed by whether `X² - tX + p` has a root mod
3 (a Frobenius eigenvalue), which is a condition purely on `t mod 3` and
`p mod 3`. Worked out exactly and confirmed both analytically and
empirically:

- `p ≡ 2 (mod 3)`: a root exists **only** when `N ≡ 0 (mod 3)` —
  impossible for prime N. **Never usable.** Confirmed: 0/20 curves at each
  of the 20-bit (`p=1048583`) and 24-bit (`p=16777259`) primes — both
  `≡ 2 (mod 3)` — had any psi_3 root (`check_psi3_census.py`), while
  unrestricted random curves at the *same* p had roots at the expected
  ~50% rate (`check_psi3_unrestricted.py`, 15/30) — ruling out an
  implementation bug and confirming the obstruction is specific to the
  prime-N population.
- `p ≡ 1 (mod 3)`: exactly one of the two root-giving `t`-residues is
  compatible with prime N. Confirmed at the 28-bit prime (`p=268435459`,
  `≡ 1 mod 3`): 7/20 curves had roots, and in every single case `t mod 3`
  was 1 (the allowed residue) — the other 13 curves had `t mod 3 = 0` (the
  forbidden, `N≡0 mod 3`, residue) and correctly had zero roots
  (`check_psi3_28bit.py`, `check_eigenvalue_mod3.py`).

**Consequence for CTRL-PLANTED-PATH specifically:** an anomalous curve
(E1) has trace `t = 1` always (fixed, not merely a residue class), so
`t mod 3 = 1` always. By the rule above, a genuine forward chain from E1
is possible **only** at the 28-bit prime (`p ≡ 1 mod 3`); at 20 and 24
bits (`p ≡ 2 mod 3`) it is mathematically impossible, not merely
improbable. `planted.py` checks `p % 3` up front (an earlier version
instead retried `find_anomalous_curve` up to 200 times per bit size before
falling back, which is expensive — ~3–20s per attempt — and pointless once
the theorem is known; this was a real efficiency bug, fixed) and falls
back to `chain_len=0` at 20/24 bits, disclosed explicitly in every planted
outcome record (`achieved_chain_len`, `fallback_to_chain_len_0`,
`fallback_reason`) — never silently substituted. RUN-4 actually achieves a
genuine `chain_len=4` (`forward_degree=81`) walk at 28 bits.

**Consequence for the driver's step-prime set:** `isogeny_step_primes =
{2, 3}` (recorded per instance as the spec requires). ℓ₀=2 is retained
(correctly implemented, fires for curves without a prime-N constraint —
exercised in `isogeny3.py`'s own test suite) but contributes no edges to
this experiment's own population; ℓ₀=3 contributes real, bounded,
multi-node exploration for roughly a third to a half of curves at bit
sizes where `p ≡ 1 (mod 3)` (28-bit here), and none at 20/24-bit. This
is disclosed rather than concealed by, e.g., silently reporting only
"NOT_FOUND" without explaining why the search space was so often a single
node.

## 4. "Meet-in-the-middle" → single bounded BFS (disclosed deviation)

Tate's isogeny theorem (1966): two elliptic curves over the same finite
field are isogenous over that field **iff** they have the same number of
points. Every curve reachable from the origin by any same-field isogeny
therefore has exactly the origin's N. Since E1 (`N==p`) and E2
(`k=ord_N(p)`) depend only on N, their truth value is fixed at the origin,
before any walk begins, and cannot change along the walk — confirmed as a
running correctness check every 200 visited nodes during every real BFS
(`graph_search.py`'s `tate_spot_checks`; would raise `AssertionError` on
violation, never fired). There is therefore no independent "target side"
to meet from: this driver implements a single bounded BFS of the reachable
class rather than fabricating a second, vacuous search side. Disclosed as
a deviation from the literal "BFS/MITM" phrasing, justified by the theorem
above.

## 5. E1/E2/E3 predicates

- E1 (anomalous, `N==p`): exact, via `curve_order.py`.
- E2 (low embedding degree): `k = ord_N(p)` computed exactly by factoring
  `N-1` (`sympy.factorint`, exact) and testing divisors in increasing
  order (verified against brute-force order computation on small N,
  `test_predicates.py`, 50/50). `K_MAX = 6`.
- E3 (subfield/Weil-descent/GHS): **constant False**, not a guessed
  threshold. Every curve here is drawn over a genuine prime field `F_p`
  (`curve_sampling_rule`: "smallest prime p >= 2^k"), which has no proper
  subfield, so there is no Weil-restriction descent target. This resolves
  the predicate directly from the cited source record (IDEA-20260727-005:
  GHS/Weil descent is "relevant to E/F_{q^e}, not directly to a curve
  natively over F_p with no proper base field") per ST-2, rather than
  requiring a stop-and-report on an invented numeric threshold.

Consequence, also mathematically forced: E1 is excluded from the
unplanted census by the sampling rule itself (`N != p` required at
acceptance), and — per §3 — can never be *reached* by any same-field
isogeny either, so it is a structural impossibility for the census, not
an empirical negative. E2 is not excluded at sampling time, so a
naturally-occurring low-embedding-degree curve *could* appear among the
census curves (astronomically unlikely at these sizes: none did across
60 sampled curves). E3 is always False by construction.

## 6. Exit-map self-map check (CTRL-EXITMAP-CONSISTENCY)

Implemented via j-invariant equality between a discovered "special" node
and the origin (`exitmap.py`). Dedicated spot-check (RUN-6) constructs
30 genuinely isomorphic pairs (via the standard twist scaling
`(a,b) → (u⁴a, u⁶b)`, which MUST be flagged) and 30 independently sampled
distinct-j-invariant pairs (which MUST NOT), both passing 30/30. No
exit-map voids were triggered during the real census/planted runs (no
credited "special" nodes existed to check beyond the origin itself, which
the code explicitly excludes from the self-map check since it is not a
"path" at all).

## 7. Cost model (`cost_model.py`)

Every routine instruments its own field multiplications and inversions
(`ecc.OpCounter`). The one MODELED constant is `I_OVER_M = 8` (the
inversion/multiplication cost ratio; standard Hankerson-Menezes-Vanstone
convention). `GROUP_OP_EQUIV_MULTS` is *measured* directly from
`ecc.point_add`'s own instrumented op-count (1 inversion + 3
multiplications for a generic affine addition — verified directly against
the source in `tests/test_costmodel.py`), not assumed. Every other
quantity in `results/summary.json` and the per-run `results.json` files is
either a direct field-operation count (measured) or a modeled reference
value (`0.886*sqrt(N)` for rho, `2*sqrt(N)` for BSGS), and the two are
never mixed into one column — measured rho/BSGS costs are reported
alongside, not instead of, the modeled reference positions.

## 8. Write-scope discipline (housekeeping)

Numerous scratch/derivation/verification scripts were initially written to
a pre-existing shared `.tmp/` directory at the repository root, which is
**outside** this task's declared `write_scope`
(`experiments/EXP-ECDLP-bbb42f/`) and is used by other concurrent
sessions/agents (confirmed: files there predate this session and belong to
unrelated tasks — `ecq_v*`, `agent-outputs-*`, `handoff_TASK-20260831-*`,
etc.). All 63 files this session created there were moved into
`experiments/EXP-ECDLP-bbb42f/tests/` and every in-code docstring
reference updated accordingly; nothing pre-existing in `.tmp/` was
touched or deleted.

## 9. Protocol deviations, summarized

1. Stale contradictory `status_note` in the frozen contract (§0) —
   proceeded on `approved_by_note` + handoff authority, flagged for
   amendment.
2. `isogeny_step_primes = {2, 3}` rather than a single fixed prime,
   justified in §3 — both mathematically forced choices, not a scope
   expansion for its own sake.
3. "Meet-in-the-middle" implemented as a single bounded BFS (§4), per
   Tate's theorem making a second search side vacuous by construction.
4. E2 special-curve solver (MOV/Frey–Ruck pairing reduction) is **not
   implemented** — out of scope given the astronomically low probability
   of an E2 hit at these sizes (none occurred). Had one occurred, the
   driver reports `C_special` as an explicitly labeled MODELED estimate
   (`L_{p^k}(1/3)` order of magnitude) and flags the instance as an
   anomaly for Coordinator attention rather than silently counting it
   toward S1/F1 — this code path exists in `isogeny_transfer_census.py`
   but was never exercised.
5. CTRL-PLANTED-PATH's literal "walk a short random chain" is
   unsatisfiable at 20/24 bits (§3.2, Lemma 2); satisfied instead at
   `chain_len=0`, which still meets every explicit sub-condition of the
   control's own description (path found within budget, solver run on the
   target, log pulled back, certificate re-verified). At 28 bits a genuine
   `chain_len=4` walk was achieved and used.
6. `tests/` scratch files moved from a shared `.tmp/` directory outside
   write_scope (§8).

None of these deviations touch a stated success/falsification criterion,
a metric definition, or a budget; all are disclosed here and in the
per-run manifests/`results.json` rather than silently absorbed.
