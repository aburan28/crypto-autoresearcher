# Derivation note — matched classical path-finding baselines under full cost

Task `TASK-20260725-505` · Goal `GOAL-SSI-001` · Batch `BATCH-002`  
Implements revised `IDEA-20260725-001` under `DEC-20260725-002` caps.  
Zero curve computation. Spine: `KN-TECH-029`, `KN-TECH-024`, `KN-LIT-078`,
`KN-LIT-094`, `KN-TECH-035`.

## 0. Claim ceiling

This note recommends **matched classical baselines**. It does not claim a
sub-\(p^{1/4}\) endomorphism-ring break, does not attack CSIDH/SQIsign/CGL
parameters, and does not satisfy `GOAL-SSI-001` completion criteria.

---

## 1. Regime A — \(\mathbb{F}_{p^2}\) pure path-finding (CGL-style)

### 1.1 Step-count baselines (from spine)

Graph has \(\sim p/12\) vertices (`KN-TECH-024`). Pure path-finding with no
torsion images (`KN-TECH-029`):

| Algorithm | Time | Space | Source |
| --- | --- | --- | --- |
| Meet-in-the-middle (MITM) trees from both ends | \(\tilde{O}(p^{1/2})\) | \(\tilde{O}(p^{1/2})\) | `KN-TECH-029` |
| Delfs–Galbraith \(\mathbb{F}_p\)-subgraph | not applicable as stated when endpoints are not \(\mathbb{F}_p\)-rational | — | `KN-LIT-078` / `KN-TECH-029` |

So the classical **step-count** baseline on the full \(\mathbb{F}_{p^2}\) graph is
MITM.

### 1.2 Full-cost correction for MITM (Wiener analogy)

Wiener (`KN-LIT-094`, `KN-TECH-035`): a \(\sqrt{n}\)-element random-access table
cannot be reached in unit time in 3D wiring; BSGS has \(n^{1/2+o(1)}\) steps but
full cost \(n^{2/3+o(1)}\).

MITM stores a table of size \(S=\tilde{\Theta}(p^{1/2})\) (half-depth nodes /
\(j\)-invariants). Mapping problem size \(N\sim p\) (vertex count scale), this is
the same memory shape as BSGS. Under the **same wiring model**, MITM's full cost
is therefore

\[
\tilde{O}\big(p^{2/3+o(1)}\big)
\]

not \(\tilde{O}(p^{1/2})\). This is a **reported analogy** to Wiener's BSGS
theorem, not a re-proof of the wiring bound for isogeny-graph tables.

### 1.3 Low-memory analogue — definition (not falsified)

**Defined algorithm (claw-finding PCS on the isogeny graph):**

1. Fix a deterministic pseudorandom walk on supersingular \(j\)-invariants via
   \(\ell\)-isogeny steps (standard expander walk; no torsion oracle).
2. Run distinguished-point walks that encode an endpoint tag (start from \(E_A\)
   vs \(E_B\), or a single claw-style pairing of two walk families), storing only
   distinguished \(j\)-invariants and short path digests — van Oorschot–Wiener /
   golden-collision style claw search (`KN-LIT-094` cites PCS retaining
   advantage when per-processor storage is small; ECDLP sibling `KN-LIT-012`).
3. On a claw (same \(j\), opposite endpoint tags), reconstruct the concatenated
   isogeny path.

**Modelled cost (heuristic, reported):** \(\tilde{O}(p^{1/2})\) isogeny steps with
**small** (poly / \(O(1)\) per processor) memory — same step-count exponent as
MITM, without the \(\tilde{\Theta}(p^{1/2})\) table.

**Why this is well-defined enough for a baseline recommendation:** it uses only
public graph walks and distinguished points; it does not require SIDH torsion
images or other uncharged oracles. What remains heuristic (as with all
`KN-TECH-029` costs) is expansion / collision accounting, not oracle access.

**Falsification condition from BATCH-001 — not triggered:** we do not claim a
fully rigorous path-reconstruction theorem here; we claim a *named modelled
algorithm* sufficient to refuse silent use of high-memory MITM as the
full-cost baseline.

### 1.4 Regime A recommendation

Under cost convention `wiener_full_cost_plus_isogeny_step_count`:

- **Do not** use high-memory MITM as the honest full-cost classical baseline.
- **Do** use low-memory claw-finding PCS (as defined above) at
  \(\tilde{O}(p^{1/2})\) steps / small memory, or state explicitly that a claim
  compares against high-memory MITM full cost \(\tilde{O}(p^{2/3+o(1)})\).

This is a **material ranking change** relative to quoting MITM
\(\tilde{O}(p^{1/2})\) time-and-space as if memory were free.

---

## 2. Regime B — \(\mathbb{F}_p\)-rational path-finding (DG available)

### 2.1 Step-count baselines

| Algorithm | Time | Space | Source |
| --- | --- | --- | --- |
| MITM on full graph | \(\tilde{O}(p^{1/2})\) | \(\tilde{O}(p^{1/2})\) | `KN-TECH-029` |
| Delfs–Galbraith via \(\mathbb{F}_p\) subgraph | \(\tilde{O}(p^{1/4})\) | \(\tilde{O}(p^{1/4})\) (subgraph MITM scale) | `KN-LIT-078`, `KN-TECH-029` |

DG already **strictly dominates** MITM in step count (\(p^{1/4}\) vs \(p^{1/2}\)).

### 2.2 Full-cost effect

Charging MITM memory makes MITM **worse** (\(\sim p^{2/3}\) full cost), which
**widens** DG's lead. Even if DG's subgraph MITM also pays a Wiener penalty on
a \(p^{1/4}\)-size table, the natural analogy is: table size \(S\sim p^{1/4}\)
corresponds to BSGS parameter \(n\sim p^{1/2}\) under \(S\sim n^{1/2}\), hence
full cost \(n^{2/3}\sim p^{1/3}\), still far below MITM full cost \(p^{2/3}\).
Low-memory PCS on the subgraph would sit near \(p^{1/4}\) steps with small
memory.

### 2.3 Regime B recommendation

**Matched classical baseline remains Delfs–Galbraith** as already recorded in
`KN-TECH-029`. Full-cost accounting does **not** change the baseline identity.
`DOCUMENTATION_ONLY` for this regime: IDEA-20260725-001 adds no
decision-relevant correction beyond stating that MITM must not be used as a
straw baseline when DG applies.

---

## 3. Cross-regime summary

| Regime | Honest classical baseline (full cost) | Ranking change vs naive MITM quote? |
| --- | --- | --- |
| \(\mathbb{F}_{p^2}\) pure | Low-memory claw-PCS \(\tilde{O}(p^{1/2})\) small mem; or high-mem MITM at full cost \(\tilde{O}(p^{2/3+o(1)})\) if that algorithm is the claimed comparator | **Yes** — memory-free MITM \(\tilde{O}(p^{1/2})\) is dishonest under Wiener |
| \(\mathbb{F}_p\)-rational | Delfs–Galbraith \(\tilde{O}(p^{1/4})\) | **No** — DG already dominates |

Quantum \(\tilde{O}(p^{1/4})\) claw (`KN-LIT-079`) is out of scope for this
classical gate.

---

## 4. Disposition

**`MATERIAL_RANKING_CHANGE`** — scoped to Regime A (\(\mathbb{F}_{p^2}\)).  
Regime B confirms `KN-TECH-029` already suffices.

Optional knowledge follow-up (Coordinator only): a short `KN-TECH` note stating
the regime-split full-cost baseline rule. Not a `KN-FIND`.

---

## 5. Verification honesty

- Wiener \(n^{2/3}\) BSGS result: established in `KN-LIT-094` (read at seeding).
- MITM/DG exponents: reported from `KN-TECH-029` / `KN-LIT-078`.
- MITM↦Wiener full-cost map and claw-PCS definition: **this program's derivation**;
  not a theorem in the spine; constants \(o(1)\) not extracted.
- No primary PDF re-fetched this batch; no isogeny computed.
