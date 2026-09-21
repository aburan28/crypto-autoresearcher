# Supersingular-isogeny cryptanalytic baseline (post-SIDH break)

Task: `TASK-20260725-501` · Goal: `GOAL-SSI-001` · Batch: `BATCH-001`  
Access date: 2026-07-25  
Primary substrate: repository knowledge spine `KN-LIT-062`…`079`, `KN-TECH-024`…`029`, `KN-OPEN-013`…`015`.

This map separates **broken** schemes from **survivors** and states the matched
baselines a novelty-screened candidate must beat. It is literature synthesis,
not an attack claim.

---

## 1. Broken: SIDH / SIKE (torsion images published)

| Item | Status | Spine |
| --- | --- | --- |
| SIDH key exchange | Broken 2022 | `KN-LIT-062`, `KN-TECH-025` |
| SIKE (NIST PQC) | Broken 2022 | `KN-LIT-064` |
| Public data that killed it | Secret isogeny degree **and** images of a known torsion basis | `KN-TECH-025` |
| Attack engine | Higher-dimensional Kani glue-and-split embeddings | `KN-TECH-026`, `KN-LIT-065`…`068` |
| Precursors | GPST adaptive static-key attack; Petit unbalanced torsion | `KN-LIT-076`, `KN-LIT-077` |

**Baseline for the broken regime is polynomial time** (provable in dim 4/8 per
Robert, `KN-LIT-067`). Rediscovering torsion-image key recovery is **not** a
novelty target for this goal.

Lesson formalized as `KN-OPEN-015`: publishing auxiliary structure about a
secret map can collapse an assumption that looked exponential. Survivors are
exactly the constructions that publish **no** images of points under a secret
isogeny at known degree.

---

## 2. Survivors and their hardness cores

### 2.1 CGL hash / pure isogeny path-finding

- Object: walks on the supersingular \(\ell\)-isogeny graph over \(\mathbb{F}_{p^2}\)
  (\(\sim p/12\) vertices, \((\ell+1)\)-regular Ramanujan); hash outputs an
  endpoint \(j\)-invariant (`KN-TECH-024`, `KN-LIT-063`).
- **No torsion images** under a secret isogeny → untouched by the SIDH break.
- Classical baselines (`KN-TECH-029`, `KN-LIT-078`):
  - Meet-in-the-middle on the full graph: \(\tilde{O}(p^{1/2})\) time **and**
    space.
  - Delfs–Galbraith via the \(\mathbb{F}_p\)-rational subgraph:
    \(\tilde{O}(p^{1/4})\).
- Quantum baseline (`KN-LIT-079`): claw / quantum search \(\tilde{O}(p^{1/4})\).
- Hardness core collapses to **endomorphism-ring computation** under GRH
  (`KN-LIT-074`, `KN-TECH-028`) — see §2.2.

### 2.2 Endomorphism ring / Deuring / SQIsign foundation

- Deuring correspondence: supersingular curves \(\leftrightarrow\) maximal orders
  in \(B_{p,\infty}\); isogenies \(\leftrightarrow\) connecting ideals
  (`KN-LIT-075`, `KN-TECH-028`).
- KLPT: quaternion \(\ell\)-isogeny path-finding in heuristic polynomial time
  (`KN-LIT-073`) — the algebraic side is **easy**, so secret endomorphism-ring
  knowledge is a trapdoor.
- SQIsign (`KN-LIT-072`): Fiat–Shamir signatures using KLPT; reveals no torsion
  images under a secret long-term isogeny.
- Equivalence (`KN-LIT-074`): endomorphism-ring recovery \(\equiv\) isogeny
  path-finding under GRH.
- Best known generic costs remain the path-finding bounds of §2.1
  (\(\tilde{O}(p^{1/4})\) classical / quantum). Residual: does **extra
  structure** (orientation, known small-degree endomorphisms, special curves)
  admit faster attacks? → `KN-OPEN-013`.

### 2.3 CSIDH commutative class-group action

- Ideal class group acts commutatively on supersingular curves over
  \(\mathbb{F}_p\) (`KN-LIT-069`, `KN-LIT-070`, `KN-TECH-027`).
- No torsion images → untouched by the SIDH break.
- Classical vectorization: roughly meet-in-the-middle / class-group methods,
  subexponential in \(\log p\).
- Quantum: abelian hidden-shift → Kuperberg sieve
  \(2^{O(\sqrt{\log p})}\) (`KN-LIT-071`) with **contested concrete constants
  and memory/query trade-offs** → `KN-OPEN-014`.
- Commutativity is the trade that enables efficient action **and** the quantum
  attack; SIDH avoided it at the cost of torsion leakage.

---

## 3. Cost-model conventions (“fully charged”)

A candidate must state which baseline and which accounting it claims to beat:

| Convention | What it charges | Spine |
| --- | --- | --- |
| Step-count path-finding | Group/isogeny evaluations; often ignores list storage | `KN-TECH-029` |
| Memory-aware / full cost | Hardware \(\times\) time; large MITM tables are not free | `KN-LIT-094`, `KN-TECH-035` |
| Quantum query / circuit | Oracle calls, quantum memory, gate-level resources | `KN-LIT-071`, `KN-OPEN-014` |
| Auxiliary-data regime | Torsion images / degrees / orientations as oracle inputs | `KN-OPEN-015`, `KN-TECH-026` |

For this goal: **no uncharged torsion oracle, no uncharged exponential table,
no quantum-query free lunch.** Toy-parameter speedups are hypothesis-generating
only (`RQ-SSI-001`).

Parallel to the program's lattice memory discipline (`KN-TECH-044`): the
classical MITM path-finding baseline quotes \(\tilde{O}(p^{1/2})\) time **and
space**; a low-memory alternative may change which algorithm is the true
matched baseline under full cost even if the step-count exponent is unchanged.

---

## 4. Explicitly out of scope for novelty

1. SIDH/SIKE torsion-image key recovery (`KN-TECH-026`) — closed known attack.
2. `RQ-ISO-001` / `EXP-ISO-001` — ordinary-curve \(\ell\)-isogeny neighbors for
   Semaev decomposition yield, not supersingular PQ hardness.
3. Estimator retuning without a new mechanism.
4. Operational attacks on live deployments.

---

## 5. Residual open questions (program spine)

| ID | Question |
| --- | --- |
| `KN-OPEN-013` | How hard is endomorphism-ring / path-finding after SIDH, and do orientation / special curves admit sub-\(p^{1/4}\) attacks? |
| `KN-OPEN-014` | Concrete quantum cost of CSIDH under Kuperberg-style sieves — how large must \(p\) be? |
| `KN-OPEN-015` | General characterization of which auxiliary data collapses isogeny/DL assumptions |

Cheapest decisive directions suggested by this map (for candidate screening):

1. **Full-cost re-baselining** of classical path-finding (MITM space vs
   low-memory collision search) — derivation gate; no curve compute.
2. **Scoped orientation / known-endomorphism** advantage against
   `KN-OPEN-013` — only if a typed mechanism is stated, not a slogan.
3. **Concrete CSIDH quantum cost-model pin** against `KN-OPEN-014` — only with
   an explicit cost convention and falsifiable numeric claim.

---

## 6. Verification honesty

- Claims above are **reported** from the repository knowledge entries cited;
  this task did not re-derive Delfs–Galbraith, Robert, or Kuperberg.
- No new primary PDF was fetched for this batch; citations prefer `KN-*` IDs
  already verified at seeding time.
- No curve or isogeny graph computation was performed.
