# PQC cryptanalysis targets and measurable goals

Research snapshot: 26 September 2026. This is an attack research agenda, not a claim that any currently recommended parameter set has been broken.

## Repository context and source provenance

This is an **additive planning note** to [the July additional-signatures goals](research_goals_20260729_nist_pqc_signatures.md) and [the July selected-algorithm goals](research_goals_20260729_nist_pqc_selected.md). It creates no formal GOAL or experiment record, changes no ledger status, and reports no experimental result. The ranking below is **within PQC**; the ECC scheduling priority in [AGENTS.md](AGENTS.md) still governs dispatch.

| Existing goal | Where this agenda contributes | Immediate dependency |
|---|---|---|
| `GOAL-UOV-001` | Goals 1–2: calibrate the UOV baseline and audit the uov-Ip wedge estimate. | Reproduce a verified oil-space recovery at reduced sizes. |
| `GOAL-MAYO-001` | Goals 1–2: test the Round 3 MAYO2 forgery and key-recovery margins. | Complete the shared UOV baseline and obtain any newly published attack details. |
| `GOAL-SNOVA-001` | Goals 1 and 3: test combined structural attacks at Round 3 parameters. | Validate the known attacks on their exact original parameter sets. |

Goal 4 proposes a **BIKE** correctness track for Coordinator intake; it does not change `GOAL-HQC-001` into a BIKE goal. Goal 5 describes receipts for any later approved experiments. Source citations in the decision and parameter comparisons are **retrieved** primary NIST material, the current submission specifications, and the HAWK attack authors' account. Their security figures remain **submitter estimates**, not independent reproductions. Linked attack papers are literature intake pointers; the existing requirement to read and file relevant primary sources as `KN-LIT` entries before formal experiment design still applies.

**Additive HAWK correction:** The July planning record's unverified description of a polynomial-time HAWK attack and unresolved candidate status is superseded for future prioritization: [the attack authors](https://www.anthropic.com/research/discovering-cryptographic-weaknesses) describe an improved **exponential-time** attack with an executable HAWK-256 challenge-size recovery, and [NIST's candidate update](https://www.nist.gov/news-events/news/2026/05/nine-candidates-advance-third-round-additional-digital-signatures-pqc) records the withdrawal. This note preserves that historical planning record; the Coordinator owns any later formal goal update.

## Decision

**First target: MAYO2, Round 3.** It is an active, structured multivariate signature, and its submitters estimate about **2^145 bit operations** for the cheapest listed direct forgery attack against a category 1 target of about **2^143 gates**. Those are model-dependent lower-bound estimates, not an executable 2^145-step attack or a practical break. The submitters also increased MAYO2's parameters after learning of a more broadly applicable key-recovery attack shortly before their Round 3 deadline; the specification says they did not yet have the details to include in its analysis. Start by checking whether those details have since appeared and independently audit the *new* parameters, (n,m,o,k,q)=(86,64,13,5,16). [MAYO Round 3 specification](https://csrc.nist.gov/csrc/media/Projects/pqc-dig-sig/documents/mayo_specification.pdf), pp. 3–4, 32.

**Parallel high-upside target: SNOVA, Round 3.** Its algebraic structure has produced multiple successful attack improvements. NIST reported that an extended wedge attack broke six of eleven *Round 2* parameter sets; a separate group-action attack improved both reconciliation and forgery methods. SNOVA's *Round 3* recommended parameters are different: its submission lists no applicable known wedge attack against the nine recommended sets and puts the least expensive *listed* level-I attack at approximately 2^182 bit operations for SNOVA_I_S. SNOVA is the more interesting search for a new structural insight, but is not the nearest published category-level margin. [NIST IR 8610](https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8610.pdf), sec. 3.14; [SNOVA Round 3 specification](https://csrc.nist.gov/csrc/media/Projects/pqc-dig-sig/documents/SNOVA_specifications.pdf), pp. 28, 33–34; [group-action attack](https://eprint.iacr.org/2024/1770); [extended wedge attack](https://eprint.iacr.org/2026/237).

**Numerically closest benchmark: UOV uov-Ip, Round 3.** The submission estimates 2^144 binary gates for the best listed wedge attack against a level-I benchmark of about 2^143. That narrow *gate-model* margin makes it a good audit target. The same table attaches an additional 17 bits of cost to that attack under its optional memory-access model. A twofold improvement in the gate estimate would be a category claim worth independently examining, but it would not amount to a feasible real-world key recovery. [UOV Round 3 specification](https://csrc.nist.gov/csrc/media/Projects/pqc-dig-sig/documents/UOV_Specification.pdf), pp. 1, 22, 26–27.

HAWK is a useful **published-attack benchmark**, not a live candidate: a 2026 attack recovered keys at the HAWK-256 *challenge* size, and its team withdrew it from NIST consideration. The improved attack remains exponential; it does not make the larger parameters practically breakable or transfer automatically to other lattice schemes. [NIST withdrawal notice](https://www.nist.gov/news-events/news/2026/05/nine-candidates-advance-third-round-additional-digital-signatures-pqc); [attack authors' report](https://www.anthropic.com/research/discovering-cryptographic-weaknesses).

## The twenty-scheme comparison set

“Top 20” has no objective cross-family ranking: security categories, signature and KEM goals, and attack models differ. This curated set covers the five NIST standards or selections, eight surviving additional-signature candidates, five prominent earlier KEM candidates, and two recently eliminated signatures. **CROSS and LESS are not still in NIST's competition.** HAWK and SIKE are omitted from the twenty because their already-known failures would obscure the new-target ranking. Sources for membership and status: [NIST PQC overview](https://csrc.nist.gov/projects/post-quantum-cryptography), [NIST additional-signature Round 3 page](https://csrc.nist.gov/projects/pqc-dig-sig/round-3-additional-signatures), [NIST IR 8610](https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8610.pdf), [NIST IR 8545](https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8545.pdf), and the [earlier KEM Round 3 roster](https://csrc.nist.gov/projects/post-quantum-cryptography/post-quantum-cryptography-standardization/round-3-submissions).

| # | Scheme | Status in this set | Hardness / useful research question |
|---:|---|---|---|
| 1 | ML-KEM | NIST standard | Module-LWE; audit primal/dual/hybrid lattice cost and decapsulation, with a very high bar for a new mathematical break. |
| 2 | ML-DSA | NIST standard | Module-SIS/LWE style assumptions; investigate signature sampling and proof/implementation gaps. |
| 3 | SLH-DSA | NIST standard | Hash-based few-shot and hypertree security; check quantum query models and misuse, low probability of an algebraic break. |
| 4 | FN-DSA (Falcon) | Selected, standard in development | NTRU lattices; lattice estimates and signing implementation, especially numerical behavior. |
| 5 | HQC | Selected, standard in development | Quasi-cyclic syndrome decoding and KEM correctness; NIST found a more stable decoding-failure analysis than BIKE. |
| 6 | FAEST | Active signature Round 3 | AES/VOLE-in-the-head proof, commitment and transcript soundness; NIST found strong security confidence among MPC-style candidates. |
| 7 | MQOM | Active signature Round 3 | Random multivariate quadratic solving and MPC-in-the-head/QROM proof. |
| 8 | SDitH | Active signature Round 3 | Random-code syndrome decoding plus MPC-in-the-head proof. |
| 9 | UOV | Active signature Round 3 | Recover hidden oil space using wedge, truncated-ring, intersection or reconciliation methods. |
| 10 | MAYO | Active signature Round 3 | UOV-type hidden oil space plus whipping map, direct MQ solving and signing model. |
| 11 | QR-UOV | Active signature Round 3 | UOV over quotient-ring/extension-field blocks and resampling/timing behavior. |
| 12 | SNOVA | Active signature Round 3 | Structured UOV, matrix-group stable ideals, ring blocks and altered rectangular parameters. |
| 13 | SQIsign | Active signature Round 3 | Supersingular isogenies and endomorphism-ring computation; leakage from intricate signing. SIKE's torsion-information break does not directly apply. |
| 14 | BIKE | Earlier NIST KEM candidate, unselected | QC-MDPC decoding failure/weak keys and chosen-ciphertext security. |
| 15 | Classic McEliece | Earlier NIST KEM candidate, unselected | Goppa-code structure and information-set decoding; no claim that a distinguisher is a KEM break. |
| 16 | FrodoKEM | Earlier NIST KEM candidate | Unstructured LWE; compare lattice estimates, implementations and conservative parameter margins. |
| 17 | NTRU | Earlier NIST KEM finalist | Structured NTRU lattice and hybrid attacks; specify the exact variant/parameters. |
| 18 | NTRU Prime | Earlier NIST KEM alternate | NTRU-type lattice without the same cyclotomic ring; compare structural versus generic lattice attack cost. |
| 19 | CROSS | Signature Round 2, eliminated | Restricted syndrome decoding and multi-round Fiat–Shamir analysis; attacked and reparameterized. |
| 20 | LESS | Signature Round 2, eliminated | Linear code equivalence; a new attack lowered estimated costs by 12–24 bits, depending on parameter set. |

The table describes **research entry points**, not a strongest-to-weakest ordering. A forgery, key recovery, distinguishing attack, failure of a proof, physical fault, and attack on a weaker parameter set are different outcomes. NIST's assessments of the extra signature candidates are in [IR 8610](https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8610.pdf), secs. 2–3, and its assessments of HQC, BIKE and Classic McEliece are in [IR 8545](https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8545.pdf), sec. 3.

## Goals and experiment receipts

### Goal 1 — Baselines that actually recover secrets

Within two weeks, import the **exact Round 2 and Round 3 specification versions** and known-answer tests for MAYO, UOV and SNOVA. Reproduce Ran's exterior-algebra UOV attack, the SNOVA block-ring wedge extension, and the published SNOVA group-action solver on scaled instances. For each, require an independently verified recovered oil space or a fresh valid signature, not only a decreased matrix rank. Record success rate across random seeds, field operations, wall time, peak RAM, preprocessing, and the cost of failed trials. Compare against generic F4/XL, reconciliation, and a random quadratic system with matched dimensions. Primary methods: [Ran's wedge attack](https://eprint.iacr.org/2025/1143), [SNOVA block-ring wedge attack](https://eprint.iacr.org/2026/237), [SNOVA group-action solver](https://eprint.iacr.org/2024/1770), [truncated-ring attack](https://eprint.iacr.org/2026/298).

### Goal 2 — Try to cross MAYO2's current margin

Measure degree of regularity, rank and time for direct/hybrid forgery and p-truncated intersection/reconciliation on toy instances tending toward the *Round 3* MAYO2 geometry (86,64,13,5,16). Test whether whitening/whipping correlations yield a smaller independent system or a lower solving degree than a matched random UOV key; count any cost to construct that reduction. Audit the new publicly available attack literature before claiming novelty. **Go** only when independent scaling supports a lower full-parameter cost than the best published ~2^145 model; the stricter category goal is below ~2^143 *under the same gate-count convention*. Publish a separate memory-aware estimate. Stop this branch if apparent small-instance gains disappear in two successive sizes or vanish when preprocessing is charged. [MAYO Round 3 specification](https://csrc.nist.gov/csrc/media/Projects/pqc-dig-sig/documents/mayo_specification.pdf), pp. 3–4, 32–34.

### Goal 3 — Test a new SNOVA composition

In parallel, test whether the **known** stable-ideal group action can be combined with block-ring wedge or truncated-ring constraints in the *Round 3 rectangular* parameter family. Sweep (v, o, q, l, r, m1, m2) around the recommended level-I points (29,3,16,4,8,5,96), (27,4,16,4,6,5,96), and (27,5,16,4,4,5,80). Track the size of invariant subspaces, extraneous roots, solving degree, matrix density, total memory traffic and verified key recovery. A proposed Frobenius quotient must be proved to preserve the public equation system; the ECC Frobenius-orbit gains from other work cannot be transferred by dividing the attack cost by the orbit size. Existing group-action attacks are a **baseline**, not a novel result. Stop if the composition adds overhead without changing the asymptotic trend or the current parameters remain far above generic attacks. [SNOVA Round 3 specification](https://csrc.nist.gov/csrc/media/Projects/pqc-dig-sig/documents/SNOVA_specifications.pdf), changelog and secs. 1.9, 4–5; [prior group-action work](https://eprint.iacr.org/2024/1770).

### Goal 4 — Fallback: BIKE correctness

If the algebraic tracks stall, reproduce the *specific* gathering-property weak-key and near-codeword decoder-failure findings against the **corresponding BIKE versions**. Measure failure probability with confidence intervals and explain whether the issue persists in any current version and actually affects IND-CCA security. NIST describes a former level-I weak-key class with average decoding-failure rate at least 2^-117 and a subsequent decoder change, and did not select BIKE. This would be a useful independent analysis, but a result on an old decoder is not a break of HQC. [NIST IR 8545](https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8545.pdf), sec. 3.2.

### Goal 5 — Research throughput and claim discipline

Keep a machine-readable attack receipt with `scheme`, `spec_version`, `parameter_id`, `security_game`, `hypothesis`, `baseline_reference`, `seed`, `instances_attempted`, `verified_successes`, `preprocessing`, `field_ops`, `bit_gates`, `wall_time`, `peak_ram`, `memory_traffic`, and `projection_method`. Each hypothesis has one small falsification test and a next-size gate. If the PQC lane has no runnable experiment and is eligible under repository priority rules, propose a **Design Experiments** item to the Coordinator from its highest-ranked open hardness question, with required inputs, baseline, controls, budget, stopping rule and falsifier. The Coordinator owns intake and dispatch. Daily score: verified hypotheses tested and decisions reached; weekly score: independent reproductions, cost improvements under matched models and open questions resolved. Label results distinctly: *toy-instance reproduction*, *changed estimate*, *category-level estimate below target*, *actual current-parameter forgery/key recovery*, or *implementation failure*.

## Claim threshold

To call a current scheme broken, provide an independently checkable attack against **current exact parameters** and the **claimed security game**, with actual verified witnesses where feasible, and credible end-to-end work/data/memory accounting where a full attack is infeasible to execute. A finding below a category threshold based only on a heuristic model should be presented as a revised *security estimate*. A 2^140 attack would still be impractical to run. Re-run any striking result on independent keys and have someone else verify the implementation and model before public claims.
