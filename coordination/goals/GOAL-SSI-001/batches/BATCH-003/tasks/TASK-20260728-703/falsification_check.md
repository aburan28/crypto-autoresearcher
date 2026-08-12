# Red-Team Falsification Check: TASK-20260728-703

**Goal:** GOAL-SSI-001 · **Batch:** BATCH-003 · **Task:** TASK-20260728-703
**Role:** Red Team (independent session) · **Date:** 2026-07-28
**Artifacts under review:**
- `TASK-20260728-701/corrected_derivation_note.md` (snapshot commit `94df4f86`)
- `TASK-20260728-701/corrected_baseline_recommendation.yaml` (same commit)

---

## Verdict: SUPPORT

The F1 fix is correct and complete. The seeded hash construction
h_i(x) = H(i || x) mod (l+1) produces P genuinely distinct walk functions
(not merely l+1 constant edge selectors), restoring P = p^{1/4} useful
processors. The re-derived VW full-cost exponents are confirmed at
p^{1/2} (F_{p^2}) and p^{1/4} (F_p conditional on mixing). All four
nonfatal objections N1-N4 are correctly reconciled. The MITM and DG
full-cost exponents are unchanged and correct. The complete matched-
baseline package is coherent and ready for KN-TECH promotion, subject to
three nonfatal objections (receipt metadata, Wiener theorem applicability
precision, useless-collision reasoning precision).

No fatal objections remain. No breakthrough claim is detected.

---

## Check 1: Receipt Validity

**Result: PASS (with nonfatal metadata gap NF1).**

| Item | Expected | Found | Match |
|------|----------|-------|-------|
| Snapshot commit SHA | recorded in receipt | `null` in receipt; `94df4f86` in Git | receipt gap (NF1) |
| Parent commit SHA | recorded in receipt | `null` in receipt; `bf766ae6` in Git | receipt gap (NF1) |
| Changed paths | 2 producer + 1 receipt | exactly 3 (corrected_derivation_note.md, corrected_baseline_recommendation.yaml, snapshot-receipt.json) | yes |
| `corrected_derivation_note.md` SHA-256 | `fbe238e6...671daa9` | `fbe238e6229d4052adc9f38aaa1e5475a4809142d31a3dfe2443fb67e671daa9` | yes |
| `corrected_baseline_recommendation.yaml` SHA-256 | `ed76265f...6410c6` | `ed76265f50256fcecf015036f25782cd574f515ca2ec7d70a95cbdaef66410c6` | yes |

Verification performed:
- `git diff-tree -r 94df4f86` confirms exactly the 3 declared paths changed (all
  added, mode 100644).
- `git cat-file -p <blob> | shasum -a 256` for both producer blobs confirms the
  committed content hashes match the receipt's `source_path_sha256` exactly.
- Commit `94df4f86` is HEAD, reachable, parent `bf766ae6` (BATCH-003 opening
  commit).
- Commit message names TASK-20260728-702 and TASK-20260728-701.
- Working-tree modifications are confined to `experiments/EXP-SIG-008/`
  (macOS `._` metadata files); no SSI task artifacts are dirty.

**Nonfatal NF1:** The receipt's `commit_sha` and `parent_sha` are both `null`,
and `verification.status` is `"pending_post_commit"`. Unlike BATCH-002 (where
the receipt was committed separately after the snapshot commit 65e5bdb8 and
could record that commit's SHA), in BATCH-003 the receipt was committed together
with the producer files in a single commit 94df4f86. The receipt therefore
cannot self-record its own commit SHA (circular dependency). The commit is
independently verifiable against Git, and all hashes match, but the receipt is
self-incomplete. The Coordinator should update the receipt post-commit with
`commit_sha=94df4f86` and `parent_sha=bf766ae6`, or the dispatcher should fill
these in during verification. This is a metadata gap, not an evidence-integrity
failure.

---

## Check 2: F1 Fix Verification

**Result: CORRECT AND COMPLETE.**

### 2a. Is the per-processor walk-function variation correctly described?

**Yes.** The corrected derivation (section 5, "Per-processor walk-function
variation (F1 fix)") describes:

- Processor i (i = 1, ..., P/2) runs a walk from E_0 using walk function h_i,
  selecting edge h_i(j(E)) mod (l+1) at each step.
- Processor j (j = P/2+1, ..., P) runs a walk from E_1 using walk function h_j.
- The hash functions {h_1, ..., h_P} are independent pseudo-random functions on
  F_{p^2} -> {0, 1, ..., l}, constructed from a single hash H and a seed:
  **h_i(x) = H(i || x) mod (l+1)**.
- The retraction of "the walk function is fixed and shared by all processors"
  is explicit.
- The reconstruction records the walk-function index, enabling the correct
  deterministic walk to be re-run.

### 2b. Does the distinct-hash-functions concern invalidate the fix?

**No. This is NOT a fatal objection.** The concern that "for l=2, there are
only 3 possible hash functions (selecting edge 0, 1, or 2)" is based on a
misinterpretation. The hash function h_i is NOT a constant edge selector —
it is a function that maps each j-invariant x to an edge index, with the seed
i creating a different function:

- At vertex with j-invariant x, processor i selects edge H(i || x) mod (l+1).
- At the same vertex, processor j selects edge H(j || x) mod (l+1).
- These are different with probability l/(l+1) (for l=2, probability 2/3).

So h_1 and h_2 are genuinely different functions: they disagree at most
vertices. Two walks from E_0 with different seeds diverge after O(1) steps
with probability 1 - (1/(l+1))^t. Over O(log p) mixing steps, the walks are
almost certainly on different paths. There are P distinct walk functions,
not merely l+1.

This is exactly how seeded parallel collision search works in the group
setting (van Oorschot-Wiener, KN-LIT-012): the walk function includes a
random seed to create distinct walks. The corrected derivation correctly
adapts this to the isogeny graph.

### 2c. Does it restore P = p^{1/4} useful processors?

**Yes.** With P/2 distinct hash functions from E_0 and P/2 from E_1:
- Each processor explores a different deterministic path from its endpoint.
- A collision between any E_0-walk (using h_i) and any E_1-walk (using h_j)
  yields a path E_0 -> E_1.
- Total walk steps: O~(sqrt(|V|)) = O~(p^{1/2}) (birthday bound).
- Steps per processor: p^{1/2} / p^{1/4} = p^{1/4}.
- P = p^{1/4} useful processors, not 2.

### 2d. Does a collision between any E_0-walk and any E_1-walk yield E_0 -> E_1?

**Yes.** The walks are deterministic given their hash function and starting
curve. If walk A (from E_0, using h_i) and walk B (from E_1, using h_j) collide
at vertex j_m, then:
- Walk A gives a path E_0 -> j_m (re-run using h_i).
- Walk B gives a path E_1 -> j_m (re-run using h_j).
- The dual of walk B gives j_m -> E_1.
- Composition: E_0 -> j_m -> E_1.

The reconstruction (section 5, step 4) correctly describes this, including
walk-function tracking and kernel recomputation.

### 2e. Useless-collision overhead

With P/2 walks from each endpoint:
- E_0-E_0 pairs: C(P/2, 2) ~ P^2/8 (useless)
- E_0-E_1 pairs: (P/2)^2 = P^2/4 (useful)
- E_1-E_1 pairs: C(P/2, 2) ~ P^2/8 (useless)

Useful and useless pairs are both O(P^2) and equally numerous. The first
collision is equally likely to be useful or useless, giving a factor-2
overhead. **Nonfatal NF3:** The derivation's "O(P/2) / O(P/2) = O(1)"
notation is imprecise — the correct argument is the pair-counting above.
The result (constant overhead) is correct.

---

## Check 3: Mathematical Interpretation

### 3a. VW full-cost exponent F_{p^2}: p^{1/2}

**CORRECT.** With F1 fix:
- P = p^{1/4} useful processors, T = p^{1/4} steps each.
- Clock cycle O(1) (per-processor storage, N1 reconciliation).
- Wall-clock O~(p^{1/4}), hardware O(p^{1/4}).
- Full cost = p^{1/4} * O~(p^{1/4}) = **O~(p^{1/2})**.

Without fix: P=2, wall-clock O~(p^{1/2}), full cost O~(p^{3/4}) — worse than
MITM's p^{2/3}. The F1 fix is essential.

### 3b. VW full-cost exponent F_p: p^{1/4} (conditional on mixing)

**CORRECT.** With F1 fix:
- P = p^{1/8} useful processors on F_p subgraph (|V^{F_p}| ~ sqrt(p)).
- T = p^{1/8} steps each.
- Clock cycle O(1), wall-clock O~(p^{1/8}), hardware O(p^{1/8}).
- Full cost = p^{1/8} * O~(p^{1/8}) = **O~(p^{1/4})**.

Without fix: P=2, wall-clock O~(p^{1/4}), full cost O~(p^{3/8}) — worse than
DG's p^{1/3} (3/8 > 1/3). The F1 fix is essential.

Conditional on unproven F_p subgraph mixing. If mixing fails, DG at p^{1/3}
is the unconditional fallback.

### 3c. MITM full-cost exponent: p^{2/3} (F_{p^2})

**CORRECT (unchanged).** Table of p^{1/2} entries, clock cycle p^{1/6} (set by
table), P = p^{1/2}, wall-clock p^{1/6}, hardware p^{1/2}, full cost p^{2/3}.
Confirmed by RT-20260727-603.

### 3d. DG full-cost exponent: p^{1/3} (F_p)

**CORRECT (unchanged).** Table of p^{1/4} entries, clock cycle p^{1/12} (set by
table), P = p^{1/4}, wall-clock p^{1/12}, hardware p^{1/4}, full cost p^{1/3}.
Confirmed by RT-20260727-603.

### 3e. Wiener theorem applicability — NONFATAL NF2

Wiener's parallel collision search theorem (KN-LIT-094) and the van
Oorschot-Wiener method (KN-LIT-012) are proven for random walks on cyclic
groups. The supersingular l-isogeny graph is a Ramanujan expander, not a
group. The birthday bound O~(sqrt(|V|)) on a Ramanujan graph after mixing is
a well-supported heuristic:

1. The Ramanujan property gives mixing time O(log |V|) (KN-TECH-024).
2. After mixing, the walk distribution is close to uniform on V.
3. The birthday paradox applies to near-uniform distributions: O(sqrt(|V|))
   samples are needed for a collision.
4. The deterministic walk structure ensures collided walks merge and can be
   detected at distinguished points, as in the group setting.

However, this is NOT a direct application of Wiener's group theorem — it is an
application of the birthday paradox to mixed walks on an expander graph. The
derivation cites KN-LIT-012 and KN-TECH-024 but does not explicitly state the
group-vs-expander distinction. Limitation 5 acknowledges the heuristic nature
of walk independence but frames it as a joint-distribution issue rather than
a group-vs-expander transfer issue.

The result is correct as a heuristic. The KN-TECH entry should explicitly
note that the VW framework is adapted from the group setting to the expander-
graph setting via the birthday paradox on mixed walks, and that formal
collision-time analysis on expanders (standard in the literature but not
cited here) would be needed for a rigorous transfer.

### 3f. F_p subgraph mixing

**Correctly scoped.** G_l^{F_p} is NOT known to be Ramanujan. VW on F_p
requires unproven mixing. DG uses BFS (no mixing needed) and is the
unconditional fallback at p^{1/3}. The YAML records this conditional clearly
with `matched_baseline_fallback`. Consistent with AGENTS.md rule 2
(heuristic-conditional claim with falsification condition and fallback).

---

## Check 4: N1-N4 Reconciliation

### N1: Clock-cycle inconsistency — RECONCILED

The corrected derivation explicitly states:
- For MITM: every step accesses the table, so clock cycle = S^{1/3} = p^{1/6}.
- For VW: every step is a local isogeny computation accessing only per-processor
  storage O(1). The shared table is accessed only at distinguished points (once
  every 2^d steps). Clock cycle = O(1), not S^{1/3}.
- Amortized table-access cost per step: O(S^{1/3}/2^d) = O(p^{1/12}/p^{1/4}) =
  O(p^{-1/6}), subconstant.
- Section 4 generalizes the clock-cycle definition to cover both cases.

This is Wiener's explicit theorem (KN-LIT-094): "parallel collision search
retains its asymptotic advantage because per-processor storage is small." The
result (full cost p^{1/2}) is correct; the reasoning is now internally
consistent. **N1 is reconciled.**

### N2: Stored-kernels phrasing — RECONCILED

Both the derivation note and the YAML use "recomputed kernels" / "kernels
recomputed during reconstruction" throughout. The derivation (section 5,
step 4): "the kernel K is recomputed from h_i(j(E)) mod (l+1) -- kernels are
not stored (N2 fix)." The YAML: "Kernels are recomputed at each step from
h_i(j(E)) mod (l+1) during the reconstruction re-run -- not stored (N2 fix)."
No per-step kernel storage is implied. The polynomial-space claim is
preserved. **N2 is reconciled.**

### N3: Isogeny degree l not specified — RECONCILED

l is specified as a small fixed prime (l = 2 for CGL) in section 1 and
section 5 of the derivation, and in the YAML walk_model fields. The derivation
states: "Computing E[l] via the l-division polynomial and enumerating its
(l+1) subgroups of order l is polynomial in log p for fixed small l. All
per-step costs assume fixed small l; the exponents are in p, not in l."
**N3 is reconciled.**

### N4: Birthday bound assumes mixing — RECONCILED

The corrected derivation (section 5, "Mixing-time assumption (N4)") states:
"The O~(sqrt(|V|)) birthday bound assumes that O(log p) mixing steps have
occurred before a collision is expected. After O(log p) steps, the walk
distribution is close to uniform on V, and the birthday bound applies. If a
collision occurs before mixing (short paths), the birthday constant may
differ, but the exponent is unaffected." Also noted in limitation 4 and YAML
vw_mixing_assumption fields. **N4 is reconciled.**

---

## Check 5: Knowledge Promotion Readiness

**The complete matched-baseline package is coherent and ready for KN-TECH
promotion**, subject to Coordinator verification of promotion gates and the
three nonfatal objections.

The package contains:
1. MITM full-cost exponent p^{2/3} (F_{p^2}) — confirmed correct, unchanged.
2. DG full-cost exponent p^{1/3} (F_p) — confirmed correct, unchanged.
3. VW analogue definition — walk model with per-processor hash-function
   variation (F1 fix), distinguished predicate, collision-to-path
   reconstruction with walk-function tracking and recomputed kernels, no
   uncharged oracles.
4. VW full-cost exponents p^{1/2} (F_{p^2}), p^{1/4} (F_p conditional on
   mixing) — re-derived with F1 fix.
5. Matched-baseline recommendation — VW, not MITM/DG, under full cost; F_p
   conditional on mixing with DG fallback at p^{1/3}.

KN-TECH-029 records step-count exponents only (p^{1/2} MITM, p^{1/4} DG) and
does not include full-cost exponents or the VW analogue. The package adds new,
decision-relevant information: it raises the bar for novelty screening (future
candidates must beat VW full cost p^{1/2}/p^{1/4}, not the easier MITM/DG
full cost p^{2/3}/p^{1/3}).

The KN-TECH entry should explicitly note:
- The birthday bound on the Ramanujan graph is a heuristic application of the
  birthday paradox to mixed walks, not a direct Wiener group-theorem transfer
  (NF2).
- The walk independence is heuristic (limitation 5).
- The F_p variant rests on unproven subgraph mixing with DG fallback.

Promoting the complete package in a single coherent promotion is correct —
promoting MITM/DG without VW would be misleading because the matched-baseline
recommendation depends on all three algorithms being correctly costed.

---

## Check 6: Uncharged Oracles

**No uncharged oracles detected.** The walk, distinguished predicate, and
collision-to-path reconstruction use only:
1. l-torsion enumeration (polynomial for fixed small l, N3).
2. Velu isogeny from kernel (standard, polynomial-time).
3. Velu dual from recomputed kernel (standard, polynomial-time, N2).
4. j-invariant isomorphism (standard over F_{p^2}; bounded for j=0, 1728).
5. Seeded hash function h_i(x) = H(i || x) mod (l+1) (O(1)-time, F1 fix).

No torsion images, no preprocessing, no quantum queries, no nonstandard graph
access. Satisfies RQ-SSI-001's "all preprocessing, memory, oracle, quantum-
query, and verification costs must be charged" constraint.

---

## Check 7: Breakthrough Assessment

**No breakthrough claim detected.** The derivation explicitly disclaims a
sub-p^{1/4} break, caps claim strength at matched-baseline recommendation /
KN-TECH update, and does not count toward GOAL-SSI-001 completion criteria.
No `review-breakthrough` review is required.

---

## Summary of Objections

### Fatal

| ID | Title | Scope |
|----|-------|-------|
| — | none | — |

### Nonfatal

| ID | Title | Scope |
|----|-------|-------|
| NF1 | Receipt metadata gap (null commit_sha/parent_sha) | The commit exists and is verifiable, but the receipt does not self-record its commit SHA. Coordinator should update post-commit. |
| NF2 | Wiener theorem applicability precision | Birthday bound on Ramanujan graph is heuristic (birthday paradox on mixed walks), not direct group-theorem transfer. KN-TECH entry should note this explicitly. |
| NF3 | Useless-collision overhead reasoning imprecise | "O(P/2)/O(P/2) = O(1)" is sloppy; correct argument is pair-counting (useful and useless pairs both O(P^2)). Result is correct. |

---

## Conclusion

**Verdict: SUPPORT.**

The F1 fix is correct and complete. The seeded hash construction
h_i(x) = H(i || x) mod (l+1) produces P genuinely distinct walk functions,
not merely l+1 constant edge selectors. This restores P = p^{1/4} useful
processors (F_{p^2}) or P = p^{1/8} (F_p), with a collision between any
E_0-walk and any E_1-walk yielding a path E_0 -> E_1. The re-derived VW
full-cost exponents are confirmed at p^{1/2} (F_{p^2}) and p^{1/4} (F_p
conditional on mixing). All four nonfatal objections N1-N4 are correctly
reconciled. The MITM (p^{2/3}) and DG (p^{1/3}) full-cost exponents are
unchanged and correct. No uncharged oracles are present. No breakthrough
claim is made.

The complete matched-baseline package is coherent and ready for KN-TECH
promotion, subject to Coordinator verification of promotion gates and
addressing the three nonfatal objections (NF1: receipt metadata, NF2:
Wiener theorem applicability precision, NF3: useless-collision reasoning
precision) in the KN-TECH entry.

**Breakthrough claim detected:** No.

**Official state changed:** No. This review changes no producer artifact or
ledger record.
