# Red-Team Falsification Check: TASK-20260727-603

**Goal:** GOAL-SSI-001 · **Batch:** BATCH-002 · **Task:** TASK-20260727-603
**Role:** Red Team (independent session) · **Date:** 2026-07-27
**Artifacts under review:**
- `TASK-20260727-601/derivation_note.md` (snapshot commit `65e5bdb8`)
- `TASK-20260727-601/matched_baseline_recommendation.yaml` (same commit)

---

## Verdict: REVISE

The derivation has merit — the MITM and Delfs-Galbraith full-cost exponents
are correct, the F_p mixing conditional is properly scoped, and no uncharged
oracles are smuggled in. But the VW collision-search analogue is incorrectly
parallelized as specified: a fixed walk function on the isogeny graph yields
only 2 useful walks (from E_0 and E_1), not the claimed P = p^{1/4}, making
the VW full cost O~(p^{3/4}) — worse than MITM, not better. The fix
(per-processor walk-function variation) is straightforward and would make the
claim correct, but the derivation explicitly contradicts it and must be
revised before the VW exponents or matched-baseline recommendation are
promoted.

---

## Check 1: Receipt Validity

**Result: PASS.**

| Item | Expected | Found | Match |
|------|----------|-------|-------|
| Snapshot commit SHA | `65e5bdb87ee4e8a0a4bdedfca9d4e93d3134c704` | `65e5bdb87ee4e8a0a4bdedfca9d4e93d3134c704` | yes |
| Parent commit SHA | `37f7b12898f38214c4a653c4ce1cc0e723408f39` | `37f7b12898f38214c4a653c4ce1cc0e723408f39` | yes |
| Changed paths | 2 declared producer paths | exactly 2 (derivation_note.md, matched_baseline_recommendation.yaml) | yes |
| `derivation_note.md` SHA-256 | `2a405d94...f9277c9` | `2a405d9417523e0383b9123a50ec8e2bda1d4bc210b1f956450c2c3e4f9277c9` | yes |
| `matched_baseline_recommendation.yaml` SHA-256 | `dfa6b50b...5609cea` | `dfa6b50b036aba720ff4d9696715d10108792f3b7a6d6ba6347cd14495609cea` | yes |

- `git diff-tree -r 65e5bdb8` confirms exactly the two declared paths changed.
- Archive receipt commit `c92f2656` (HEAD) adds only `snapshot-receipt.json`
  with parent `65e5bdb8`. No scope expansion.
- Working-tree modifications are confined to `experiments/EXP-SIG-008/`
  (macOS `._` metadata files); no SSI task artifacts are dirty.

The snapshot is durable evidence per the AGENTS.md commit policy.

---

## Check 2: Mathematical Interpretation

### 2a. MITM full-cost exponent p^{2/3} (F_{p^2})

**CORRECT.** The isogeny MITM stores a table of sqrt(|V|) ~ p^{1/2}
j-invariants and performs p^{1/2} lookups — structurally identical to BSGS
with group order n = p. Applying the Wiener 3D wiring model (KN-LIT-094):

- Table size S = p^{1/2}, linear dimension S^{1/3} = p^{1/6}
- Clock cycle tau = p^{1/6}
- Optimal P = p^{1/2} processors, each doing 1 step
- Wall-clock = 1 * p^{1/6} = p^{1/6}
- Hardware = p^{1/2}
- Full cost = p^{1/2} * p^{1/6} = **p^{2/3}**

This matches Wiener's proven BSGS result (n^{1/2} steps, n^{2/3} full cost)
with n = p. No objection.

### 2b. Delfs-Galbraith full-cost exponent p^{1/3} (F_p)

**CORRECT.** DG is MITM on the F_p subgraph of |V^{F_p}| ~ sqrt(p) vertices
(KN-LIT-078, KN-TECH-029). Table size S = (sqrt(p))^{1/2} = p^{1/4}.

- Clock cycle tau = S^{1/3} = p^{1/12}
- Optimal P = p^{1/4}, wall-clock = p^{1/12}
- Hardware = p^{1/4}
- Full cost = p^{1/4} * p^{1/12} = **p^{1/3}**

Matches Wiener's BSGS result with n = sqrt(p). No objection.

### 2c. VW collision-search full-cost exponent — FATAL OBJECTION F1

**INCORRECT AS SPECIFIED; correct with a straightforward fix.**

The derivation claims:
- P = p^{1/4} processors, p^{1/4} walk steps each, total p^{1/2} steps
- Full cost = p^{1/4} * O~(p^{1/4}) = O~(p^{1/2})

The claim relies on distributing O~(p^{1/2}) total walk steps across
P = p^{1/4} processors. This requires P useful walks. The derivation
specifies:

> "The walk function is fixed and shared by all processors." (section 5)
> "Run P independent walks from different starting curves (including E_0
> and E_1)." (section 5)

**Why this fails on isogeny graphs:** The walk is deterministic — at each
vertex, the next edge is selected by `hash(j(E)) mod (l+1)`. With a fixed
hash function, every walk from E_0 follows the *same* path. There is exactly
one useful walk from E_0 and one from E_1. Walks from random starting curves
S_A, S_B produce paths S_A -> S_B, which are useless for the E_0-to-E_1
path-finding problem.

This is fundamentally different from the group setting (KN-LIT-012), where:
- The walk function f(x) = x * g^{h(x)} keeps every walk on the same cyclic
  group.
- Starting points g^{r_i} are all group elements.
- Any collision yields an exponent relation r_A + s_A = r_B + s_B.
- All P walks are useful; total steps O~(sqrt(n)) distribute across P
  processors.

On the isogeny graph there is no group structure that makes random-start
collisions useful. With only 2 useful walks (P=2):

- Each walk runs O~(sqrt(|V|)) = O~(p^{1/2}) steps (birthday bound for 2
  walks on ~p vertices)
- Wall-clock = O~(p^{1/2}) (walks are sequential chains)
- Hardware = 2 + O(p^{1/4}) ~ p^{1/4}
- Full cost = p^{1/4} * O~(p^{1/2}) = **O~(p^{3/4})** — worse than MITM's
  p^{2/3}

**The fix:** Assign P/2 distinct hash functions h_i to walks from E_0 and
P/2 to walks from E_1. Each processor explores a different path from its
endpoint. A collision between any E_0-walk (with h_i) and any E_1-walk (with
h_j) yields a path E_0 -> E_1. With P = p^{1/4} useful walks:

- Steps per walk = O~(sqrt(|V|) / P) = O~(p^{1/4})
- Per-processor storage O(1) → clock cycle O(1) (Wiener's theorem: parallel
  collision search retains advantage because per-processor storage is small,
  KN-LIT-094)
- Wall-clock = O~(p^{1/4})
- Hardware = p^{1/4}
- Full cost = **O~(p^{1/2})** ✓

The fix is standard (per-processor walk-function variation is a common
technique in parallel collision search), but the derivation does not describe
it and explicitly states the opposite ("fixed and shared by all processors").
The reconstruction must also record which walk function produced each
distinguished point, so the correct walk can be re-run.

### 2d. Clock-cycle inconsistency — NONFATAL OBJECTION N1

Section 4 defines `tau = S^{1/3}` and applies it to MITM. Section 6 lists
`tau = p^{1/12}` for VW (S = p^{1/4}) but then states wall-clock is
`O~(p^{1/4}) (dominated by local computation)`, implying tau = polylog.
Under the section-4 rule, wall-clock would be `p^{1/4} * p^{1/12} = p^{1/6}`,
giving full cost `p^{1/4} * p^{1/6} = p^{5/12}` — even better than claimed.

The correct justification (from KN-LIT-094) is that the clock cycle for
parallel collision search is set by *per-processor* storage (O(1)), not the
shared table, because table accesses are infrequent (only at distinguished
points). The derivation should state this explicitly and reconcile the tau
column with the wall-clock column. The result p^{1/2} is correct; the
reasoning is inconsistent.

### 2e. "Stored kernels" phrasing — NONFATAL OBJECTION N2

The YAML says "Velu duals from stored kernels." If read as storing one kernel
per walk step, that is O(sqrt(p) * polylog) bits — exponential in log p, not
polynomial. The derivation note correctly describes recomputation: during
reconstruction, re-run the deterministic walk and recompute each kernel from
`hash(j(E)) mod (l+1)`. The YAML should say "recomputed kernels" to avoid
implying non-polynomial storage.

---

## Check 3: Baseline Comparison

### 3a. Is the matched-baseline recommendation decision-relevant?

**Yes, conditional on the F1 fix.** Under step-count accounting, MITM, DG,
and VW are tied (p^{1/2} for F_{p^2}, p^{1/4} for F_p). Under full cost they
separate:

| Algorithm | F_{p^2} full cost | F_p full cost |
|-----------|-------------------|---------------|
| MITM | p^{2/3} | p^{2/3} (full graph) |
| DG | n/a | p^{1/3} |
| VW (with fix) | p^{1/2} | p^{1/4} (conditional on mixing) |

Choosing VW as the baseline raises the bar: a future candidate must beat
p^{1/2} (not the easier p^{2/3} MITM target) for F_{p^2}, and p^{1/4} (not
the easier p^{1/3} DG target) for F_p. This prevents a high-memory candidate
from claiming an advantage by comparing against the inflated MITM/DG
full-cost baseline. This is decision-relevant for GOAL-SSI-001 novelty
screening.

**Without the F1 fix**, VW achieves O~(p^{3/4}) full cost (2 walks only),
which is worse than MITM. The matched baseline falls back to MITM (p^{2/3})
for F_{p^2} and DG (p^{1/3}) for F_p, and the recommendation is incorrect.

### 3b. Does KN-TECH-029 already suffice?

**No.** KN-TECH-029 records step-count exponents only:
- MITM: O~(p^{1/2}) time and space
- DG: O~(p^{1/4}) on F_p subgraph
- Quantum: O~(p^{1/4})

It does not record:
- Full-cost exponents under the Wiener 3D wiring model (p^{2/3} for MITM,
  p^{1/3} for DG)
- The VW distinguished-point collision search analogue on the isogeny graph
- VW full-cost exponents
- The matched-baseline recommendation under full cost

The full-cost exponents for MITM and DG are new, correct, and decision-
relevant. They should be added to KN-TECH-029 (or a new entry) regardless of
the F1 fix. The VW analogue and its exponents require the F1 fix before
promotion.

---

## Check 4: Uncharged Oracles

**No uncharged oracles detected.** The walk, distinguished predicate, and
collision-to-path reconstruction use only:

1. **l-torsion enumeration:** Compute E[l], enumerate (l+1) subgroups of
   order l. Standard, polynomial in log p for fixed small l (NONFATAL N3:
   l is not specified, but standard choices like l=2 are fine).
2. **Vélu isogeny:** Compute phi_K: E -> E/K from kernel K. Standard,
   polynomial-time.
3. **Vélu dual:** Compute phi_K^vee from K. Standard, polynomial-time.
4. **j-invariant isomorphism:** Map between curve models at the same
   j-invariant. Standard over F_{p^2}; bounded correction for j=0, 1728.
5. **Hash function:** O(1)-time evaluation of hash(j(E)) mod (l+1).

No torsion images, no preprocessing, no quantum queries, no nonstandard
graph access. The walk uses only local isogeny computations available in the
same cost model as the MITM steps. This satisfies RQ-SSI-001's "all
preprocessing, memory, oracle, quantum-query, and verification costs must be
charged" constraint.

---

## Check 5: F_{p^2} vs F_p Regime Split

**Correctly handled.** The derivation separates the two regimes throughout:

- **F_{p^2}:** Full graph G_l, |V| ~ p, proven Ramanujan (KN-TECH-024).
  Mixing time O(log p) is proven. VW birthday bound O~(p^{1/2}) rests on
  proven expansion.
- **F_p:** Subgraph G_l^{F_p}, |V^{F_p}| ~ sqrt(p), NOT known to be
  Ramanujan. VW birthday bound O~(p^{1/4}) is conditional on unproven
  mixing. DG uses BFS (no mixing needed) and is the unconditional fallback.

The matched_baseline_recommendation.yaml records the conditional clearly:
- F_p matched baseline: "VW ... (conditional on F_p subgraph mixing)"
- F_p fallback: "If the F_p subgraph mixing assumption is rejected,
  Delfs-Galbraith at full cost p^{1/3} is the matched baseline."

This is the correct scope: a heuristic-conditional claim with a
falsification condition (mixing failure) and a fallback baseline, consistent
with AGENTS.md rule 2 and the target-result-profile's "explicit conditional
rigor" requirement. No objection on the F_p mixing scoping.

---

## Check 6: Collision-to-Path Reconstruction

**Well-defined in mechanism; no hidden oracle.** The reconstruction
procedure (section 5, steps 1-4) is:

1. Re-run both walks from their starting curves, recording distinguished
   points (segments of expected length 2^d).
2. Find the first matching distinguished point on both paths (narrows merge
   to a segment pair).
3. Re-run the two segments step-by-step, comparing j-invariants (finds exact
   merge vertex j_m).
4. Compose phi_A (E_0 -> j_m) with the dual of phi_B (E_1 -> j_m), using
   Vélu duals and the j-invariant isomorphism.

Each step uses only standard polynomial-time operations. The walk is
deterministic, so re-running reproduces the exact path. The kernel at each
step is recomputed (not stored — see N2). The output path has O(sqrt(p))
isogeny steps in O(log p) bits each; this is sequential output, inherent to
the problem, and not charged under the Wiener model.

**Caveat (N4):** The birthday bound assumes the walk has mixed (O(log p)
steps). If the collision occurs before mixing, the bound's constant may
differ. This does not affect the exponent but should be noted.

**With the F1 fix:** The reconstruction must record which walk function
(e.g., hash function index) produced each distinguished point, so the
correct deterministic walk can be re-run. This is a minor bookkeeping
addition, not a fundamental obstacle.

---

## Summary of Objections

### Fatal

| ID | Title | Scope |
|----|-------|-------|
| F1 | VW parallelization fails with fixed walk function | Invalidates the VW full-cost exponents (p^{1/2} F_{p^2}, p^{1/4} F_p) and the matched-baseline recommendation as specified. Fix: per-processor walk-function variation. |

### Nonfatal

| ID | Title | Scope |
|----|-------|-------|
| N1 | Clock-cycle inconsistency between MITM and VW tables | Does not affect the result (p^{1/2} is correct by Wiener's theorem) but the reasoning is internally inconsistent. |
| N2 | "Stored kernels" YAML phrasing implies non-polynomial storage | Misleading; should say "recomputed kernels." Does not affect the derivation note's correct description. |
| N3 | Isogeny degree l not specified | Standard choice (small l) is fine; should be stated for completeness. |
| N4 | Birthday bound assumes mixing has occurred | Standard caveat; does not affect the exponent. |

---

## Conclusion

**Verdict: REVISE.**

The derivation correctly computes the Wiener full-cost exponents for MITM
(p^{2/3}) and Delfs-Galbraith (p^{1/3}), correctly scopes the F_p mixing
conditional with a fallback, and introduces no uncharged oracles. The VW
collision-search analogue has a well-defined walk model, distinguished
predicate, and collision-to-path reconstruction.

However, the VW parallelization is incorrectly specified (F1): a fixed walk
function yields only 2 useful walks on the isogeny graph, not the claimed
P = p^{1/4}. The VW full cost is O~(p^{3/4}) as specified — worse than
MITM — not the claimed p^{1/2}. The matched-baseline recommendation (VW
dominates MITM/DG) is incorrect as specified. The fix (per-processor
walk-function variation) is straightforward and would make the claim
correct, but the derivation must be revised to describe it and retract
"the walk function is fixed and shared by all processors."

**Knowledge promotion:** Promote the MITM/DG full-cost exponents to the
knowledge spine now (they are correct and not in KN-TECH-029). Do not
promote the VW analogue or matched-baseline recommendation until F1 is
fixed.

**Breakthrough claim detected:** No. The derivation explicitly disclaims a
sub-p^{1/4} break and caps claim strength at matched-baseline
recommendation. No `review-breakthrough` review is required.

**Official state changed:** No. This review changes no producer artifact or
ledger record.
