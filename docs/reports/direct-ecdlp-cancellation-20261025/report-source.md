# Classical-only ECDLP research outside index calculus

Date: 25 October 2026. Status: research design and bounded source review; no new algorithm, experimental result, or speedup is claimed.

**Hard scope: classical algorithms only, executable on ordinary CPUs or GPUs.** Shor's algorithm, Grover search, amplitude amplification, quantum walks, quantum annealing, quantum hardware, and simulation of a quantum attack are excluded. This explicit scope statement records the user's clarification; the original proposal already specified classical computation.

The proposed direction is **exact cancellation in a classical program for scalar multiplication, with its output fixed to the public target point**. A "Boolean circuit" here means an ordinary program of deterministic bit operations. The objective is to compute the scalar bits directly from the public point. This workstream has no factor base, smoothness search, relation matrix, or index-calculus descent.

There is an important qualification: the counting formulation below is established machinery. A novel algorithm would require a new, constructive identity specific to elliptic-curve arithmetic that makes its evaluation cheap. That identity has not been supplied. The plan is concrete about how to search for it and how to reject a repackaging; it does not certify novelty in advance.

## 1. Research objective

For an elliptic curve over an odd prime field, a point $P$ of known prime order $r$, and $Q=[k]P$, recover the canonical integer $0\leq k<r$ using public inputs and a classical computation. Put $\ell=\lceil\log_2 r\rceil$.

The initial objective is a constructive mechanism that uses the field representation in a way unavailable to a group-operation oracle. An eventual exponent claim would require total cold cost $r^{\alpha+o(1)}$ with $\alpha<1/2$, a separate memory bound, and explicit assumptions. No value of $\alpha$ is predicted here. A small-instance gain, if found, would be reported at its measured scope.

This follows the current user's request, rather than the older IC-first prioritization in the repository contracts. It does not close or change any existing IC goal.

## 2. Repository orientation and what was actually checked

The three repositories have complementary roles: `crypto` owns implementations and measurement infrastructure; `cryptanalysis` owns experiment protocols and independent checking; `crypto-autoresearcher` owns programme records and the cross-repository lead atlas. That allocation is documented in its [lab contract](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/docs/lab-contract.md).

The review used these `main` revisions:

| Repository | Revision |
| --- | --- |
| `aburan28/crypto` | `5cb553810e5bbfbd8691ec614ffcaacefc625757` |
| `aburan28/cryptanalysis` | `c5aa7b39bfa30e8cdbd46a158c7cbadaa8be3503` |
| `aburan28/crypto-autoresearcher` | `ab0609ebee3d17527a51667591bda56f7cdece31` |

All 147 lead rows and 52 known-result rows were materialized and their Git blob hashes checked against GitHub metadata. This is index coverage, not independent validation of 199 scientific claims. Relevant idea records, rejected/deferred indexes, source notes, contracts, and primary literature were read selectively. The source manifest records the indexed files.

The indexed corpus includes a historical quantum-resource lead, and the unfiltered lexical matcher returned it. That row is outside this workstream and supplies no proposed algorithm, dependency, or cost comparison. `atlas-match-classical.txt` makes its exclusion explicit while preserving the original matcher output and source manifest.

The live atlas contains 43 `closed_obstructed`, 18 `closed_known`, 5 `closed_dominated`, 6 `exhausted_at_scale`, 51 `open_next_step`, 16 `open_blocked`, and 8 `open_unexamined` entries. These are recorded dispositions, not new verdicts from this session.

**Coverage limits matter.** The atlas's dated review pins older revisions than the `main` revisions above. GitHub reports the three comparisons as 1,246, 891, and 678 commits ahead, respectively, and returns only 300 changed files in each comparison. Those counts describe ancestry, not numbers of new research results. They prevent a claim that every post-review change was examined. Root recursive-tree requests failed; an experiments directory listing reached GitHub's 1,000-entry cap. The semantic knowledge-search service was unavailable; directory reads, the repository's lexical atlas matcher, and targeted GitHub searches were the fallback. Unmerged branches and stored raw archives were not exhaustively audited.

Consequently, **“not found in this review” is not “never tried.”** An exhaustive internal or external novelty certificate is not delivered.

## 3. What the existing work prevents us from relabelling

| Prior family or record | Relevance to this plan |
| --- | --- |
| `LEAD-EXO-padic-jet-canonical-lift` | A prime-to-characteristic torsion lift followed by an additive logarithm is not a fresh mechanism. The proposed bit-count coefficient ring is a counting device, not a lift of the curve. |
| `LEAD-EXO-elliptic-net-eds`, IDEA-006 | Rewriting scalar multiplication as a nonlinear recurrence does not provide its inverse. Short linear annihilators and low displacement rank have existing scoped obstructions. |
| `LEAD-STR-endo-scalar-action-generic` | Known linear scalar actions and cheaper known-scalar multiplication do not supply an unknown scalar. |
| IDEA-050, spinor/matchgate addition transform | A basis change followed by Pfaffian or tensor contraction is already proposed. A new proposal must exhibit the extra identity and compare the actual operations. |
| IDEA-111, radical ladder branch quotient | Compact syntax, shared prefixes, and a smaller ideal are insufficient. The present output is one target's scalar, rather than an explicitly decoded representation of every branch. This changes the question but does not solve it. |
| IDEA-070, reverse automaton | A small state machine without a cheap constructor and scalar orientation is an occupied route. |
| IDEA-156, coefficient-conditioned source extraction | Calling an unavailable coefficient oracle an algorithm is an existing failure mode. The candidate must construct and evaluate the coefficient. |
| IDEA-379, Ax–Katz locator | Divisibility of a many-solution count does not decide existence. The direct scalar encoding below deliberately has at most one satisfying input; computing its count remains hard. |
| `LEAD-EXO-lossy-object-propagation` | Deterministic lossless group propagation and probabilistic projections are already distinguished. Neither is a license to assume cheap scalar-bit prediction. |

The prior-art links and interpretation limits are in `SOURCES.md`. Parent lead for this investigation: `LEAD-EXO-ideas-corpus-algebraic-transforms`. This planning report does not create a novelty-certified lead or alter any official hypothesis status.

Two scope distinctions guide the search. A lower bound on representing a full relation tensor is not automatically a lower bound on evaluating one target-conditioned functional. Conversely, a one-target formulation is not automatically easier: a point mass can have a tiny final representation while being expensive to construct. Also, generic-group lower bounds do not prove a lower bound for arbitrary algorithms on the actual coordinate bits. A model-specific lower bound needs its model's hypotheses. [Corrigan-Gibbs, Henzinger and Wu](https://eprint.iacr.org/2026/384) makes that distinction explicit.

## 4. The exact object to investigate

Use a deterministic, total Boolean circuit $C_{E,P}$ computing a canonical point encoding of $[b]P$ from the $\ell$ input bits of $b$. Enforce $b<r$. Every internal wire must be a deterministic function of those bits. Include the identity point, exceptional additions, field reduction, and canonical output encoding.

All variables are ordinary classical bits. "Parity" means their exact XOR. Where the literature uses "tensor contraction," it means summation and multiplication of finite arrays of constraint values on a classical computer. No quantum states, amplitudes, measurements, or quantum speedups enter this construction. The coefficient tags below are stored as finite bit vectors.

Let $F_Q(b)$ be 1 exactly when $b<r$ and $C_{E,P}(b)=Q$, and 0 otherwise. Since $P$ has order $r$ and $Q$ belongs to its subgroup, exactly one accepted input is $b=k$.

Work in the coefficient ring

$$
R=\mathbb F_2[\varepsilon_0,\ldots,\varepsilon_{\ell-1}]
  /(\varepsilon_i\varepsilon_j:\ 0\leq i,j<\ell).
$$

Define the tagged parity response

$$
Z_Q=\sum_{b\in\{0,1\}^{\ell}}F_Q(b)
             \prod_{j=0}^{\ell-1}(1+b_j\varepsilon_j).
$$

Then

$$
Z_Q=1+\sum_{j=0}^{\ell-1}k_j\varepsilon_j.
$$

The justification is elementary: every summand but the unique accepted input is zero, and every product of two tags vanishes. It is a correctness specification, not a new hardness reduction or speed result. Evaluating the displayed sum by enumerating $b$ costs order $r$ evaluations and is worse than rho.

The ring has only $\ell+1$ binary coefficients. Its multiplication is

$$
(a,u)(b,v)=(ab,av+bu),
$$

so a tagged operation costs $O(\ell)$ bit operations with a direct representation. Compact tags do not imply a compact contraction.

Attach weight $1+\varepsilon_j$ to the positive scalar-input literal, weight 1 to its negative literal, and weight 1 to internal wires. Count satisfying assignments of the exact circuit constraints in $R$. This is an instance of [algebraic model counting](https://arxiv.org/html/1211.4475), including its existing gradient-style semiring construction. It is **not** a novel algorithm merely because the weights are interpreted as scalar bits. Known reductions from counting to tensor contraction are also explicit prior art: [Dudek, Dueñas-Osorio and Vardi](https://arxiv.org/abs/1908.04381).

An arbitrary Boolean circuit cannot be evaluated bottom-up as a model count by simply replacing OR and AND with ring operations: sharing and overlapping assignments invalidate that shortcut. Use exact classical variable elimination over finite arrays of constraint values, a sound compiled counting circuit, or a separately proved rewrite system. If auxiliary variables have multiple satisfying extensions, parity can erase the unique scalar; unique-extension correctness is mandatory.

## 5. The missing operation, stated without an oracle

Search for an **explicit block identity for the tagged response** that uses the shared field arithmetic of successive elliptic additions and doublings to eliminate internal coordinate/carry variables before a large boundary object is built. It must preserve the constant coefficient and every scalar-bit coefficient, including on exceptional cases.

A candidate submission must specify:

1. The input block, all boundary variables, and exactly which target constraints are already pinned.
2. A finite rewriting procedure using public curve parameters and public target coordinates. It may depend on $Q$; it may not depend on $k$, planted scalar bits, an uncharged lookup table, or a previously solved target.
3. A proof of equality of the tagged contractions for every allowed boundary assignment, or an explicit narrower invariant closed under composition. A sample of final correct answers is insufficient.
4. The cost of constructing and applying the replacement, its encoded coefficient size, and its behavior when blocks compose. Numerical rank or the size of the final answer is insufficient.
5. A comparison with ordinary fixed-window multiplication, XOR elimination, decision diagrams, tensor factorization, and algebraic model counting. If those already implement the operation, classify it as an adaptation.

No such identity has been derived in this review. This is the central research debt. A statement that a fast parity evaluator exists would simply restate the desired attack.

The first concrete discovery task is to build exact one- and two-step scalar blocks, totalize their exceptional cases, and compare their tagged boundary contractions before and after coordinate elimination. Use existing XOR elimination and canonical Boolean simplification as controls. Candidate rules must exploit a demonstrable elliptic identity beyond those controls. The familiar simplification of two steps to a fixed-window step is a known positive control, not the sought advance.

## 6. Work sequence and decision points

| Stage | Work and required artifact | What determines the next action |
| --- | --- | --- |
| A: collision audit | Compare the exact proposed block procedure with IDEA-050/070/111/156/379, direct scalar-circuit work, AMC, and counting compilers. Complete the outstanding branch and post-atlas search. | A duplicated operation is credited and retained as a control. Only a distinct construction is considered for a novelty claim. |
| B: exact object construction | Register small public synthetic curve instances; implement a total deterministic scalar circuit and tagged evaluator in C++ or Rust. Verify unique extensions and agreement with an independent point implementation. | Any missing exceptional case or multiplicity invalidates the encoding; repair it before interpreting cancellation. |
| C: block discovery | Enumerate tiny block boundaries, record exact cancellations, propose rewrite rules, and verify them symbolically or exhaustively within their stated finite domain. Preserve failed rules and counterexamples. | An identity surviving composition becomes a candidate algorithm component. A small final response alone does not. |
| D: blind cost ladder | Freeze the procedure and seeds, then run fresh targets at increasing subgroup sizes. Charge compilation, search, specialization, contraction, recovery, checking, failed attempts, and memory. | Distinguish a local identity, a stage gain, a complete solver gain, and a null result. Do not infer asymptotics from a short ladder. |
| E: independent challenge | Independently reconstruct the identity, verify outputs and counters, and compare with matched rho and the strongest relevant compiler. | Only then consider a scoped algorithmic claim. Larger runs depend on a concrete surviving mechanism, not a renamed oracle. |

These are proposed stages, not approved experiment records or completed runs. The first implementation stage needs exact committed inputs and the repository's normal execution admission. The plan itself is ready for review.

### Initial measurement design

Use a discovery panel at subgroup bit sizes 8, 10, and 12, with four registered curves per size and exhaustive scalar truth. Select non-anomalous prime-field instances from the shared curve authority or register new ones with exact parameters and certified subgroup orders. Cover $k=0,1,r-1$, identity output, both point signs, and exceptional addition cases.

After freezing a rule, use six fresh curves at each of 12, 14, 16, and 18 subgroup bits, with eight independently selected targets per curve: 192 held-out target trials. Store the input manifest and its hash before execution. This is a proposed sample allocation, not a claim that those fixtures already exist. Treat special-$j$ and special-prime families as separate strata; report their own matched automorphism baselines.

Primary observables are actual primitive/bit-operation counts, intermediate representation sizes, peak live memory, rule applications, rejected rules, and exact output checks. Record wall time descriptively; a controlled performance claim requires the repository's placement and calibration conditions. Plot ordinary parity and tagged parity side by side, because cancellation of an untagged count may destroy every bit coefficient.

### Controls that could actually distinguish a mechanism

- A known injective affine Boolean map provides a positive control: XOR elimination should recover its input cheaply, and tags must preserve the result.
- A tiny enumerated random permutation has the same unique-preimage property. It demonstrates that the compact final response is not special to ECDLP. Charge its explicit table; it is an instrumentation control, not a fair asymptotic cost baseline.
- Same-size arithmetic controls replace selected local arithmetic relations, with unique-extension status checked separately. State their encoding differences. An invertible change of wire basis alone preserves the computation and is not a structure-destroying null.
- Run the same generic simplifier on the EC circuit and controls. Any advantage attributed to an elliptic rewrite must identify the equality the controls lack.
- Compare the complete candidate with same-target rho using negation and applicable automorphisms, and with existing exact counting/constraint tools on the identical circuit. Verify that a chosen tool supports characteristic-two/semiring semantics before using it as a parity reference.

## 7. Cost and falsification

Let $N$ be the number of local constraints. For a dense binary variable-elimination schedule whose largest union of participating indices has size $w$, a conservative time bound is $O(\ell N2^w)$ classical bit operations, plus circuit construction and schedule search. Record live storage explicitly. A small separator or low rank only helps if its representation is constructed and manipulated cheaply. Neither a quantum oracle nor the cost of simulating a quantum algorithm is an allowed resource model.

For a compressed procedure, report its actual arithmetic-circuit operations, coefficient storage, and compilation cost rather than substituting a rank for time. All curve-specific setup is charged to the first target. If setup is excluded in a secondary many-target experiment, disclose the reuse count and include preprocessing-rho as a comparison.

A counterexample to a rewrite rejects that rewrite. A procedure that needs hidden scalar data is circular. A speed claim based on post-solution simplification is invalid. A polynomial-size forward circuit, a rank-one final target slice, and a correct small scalar recovery establish no fast inversion bound. A computation that expands a square-root-size or larger table has not established the desired exponent change.

If the frozen rewrite grammar shows no advantage over its controls, record the exact blocks and sizes tested and change the construction under investigation. Do not repeatedly retune the same compiler and call it a new mechanism. That outcome would not rule out every target-conditioned algorithm. A timeout or exhausted memory is an operational limit, not a theorem.

## 8. Four proof-search audits

**Baseline reproduction.** Enumerating every canonical scalar reproduces the exact tagged response in order-$r$ work; ordinary BSGS/rho retain their square-root comparison. Tags alone do not improve either.

**Observation collision.** Every injective map has the same compact one-target response specification. Thus uniqueness, compact tags, or final rank cannot identify EC-specific tractability.

**Quantifier order.** A proposed solver is one public procedure working for every target in its stated curve/subgroup domain. It may specialize on $Q$. “For each $Q$, a small circuit exists” does not supply a uniform constructor and is insufficient.

**Method ceiling and nearby object.** Generic counting methods have no automatic sub-square-root bound on this circuit family. Apply the proposed elliptic rule to a nearby circuit where its algebraic identity is false. If the same argument still promises cheap arbitrary permutation inversion, its purported elliptic ingredient has not been identified.

Proof map for future work: unique canonical scalar representation; unique extension of circuit wires; tagged count identity; local rewrite soundness; closure under composition; full construction/evaluation cost. The first three are standard correctness obligations, not the claimed novelty. The last three are unsupplied. No Lean proof or formal verification is claimed in this planning task.

## 9. Current status and next action

Repository orientation and the indexed prior-work comparison are complete at the stated scope. Exhaustive literature/repository coverage is partial. The direct tagged-count specification is derived above and recognized as established model-counting machinery. A new EC-specific cancellation identity, executable candidate solver, scientific trials, independent review, and any advantage remain pending.

**The next substantive action is Stage B followed by the exact micro-block discovery of Stage C, with a written collision audit attached to every proposed rewrite.** The research deliverable is the first constructive EC-specific rule that survives those tests, or counterexamples explaining exactly why a tested rule fails. No ongoing background experiment is implied.

`dominated_by`: not applicable; no new attack result. `sota_delta`: no measured change. `novelty_status`: unverified; the counting wrapper is known and is not submitted as the novel contribution.

The diagram distinguishes known machinery, the missing operation, and later validation. No canonical attack-frontier graph is changed: this report promotes no result and changes no existing lead disposition.

\newpage

## Mechanism and validation dependencies

![Classical computation only. Known constructions are blue; the missing EC-specific operation is dashed amber. All downstream tests are pending. No measured speedup is depicted.](mechanism.pdf){width=82%}


\newpage

# Sources and provenance

This is a selective source review, not a claim to have read the entire ECDLP literature. `verified_by` for retrieved content means this Codex session read the indicated material; it does not mean the mathematical claim was independently proved or the experiment replayed.

**Classical-only source use.** The proposed method draws on classical arithmetic, Boolean constraints, algebraic model counting, and exact classical variable elimination. Quantum algorithms and simulation of quantum attacks are excluded. The full historical atlas manifest is preserved for provenance, including `LEAD-EXO-quantum-ecdlp-resources`; that row is outside the proposal. `atlas-match-classical.txt` removes that row from the original lexical hits. Matchgate/Pfaffian and tensor terminology appears in classical mathematical methods and prior-work comparisons here; it does not supply a quantum computation or a quantum speedup.

## Internal sources

The following paths are at `aburan28/crypto-autoresearcher`, commit `ab0609ebee3d17527a51667591bda56f7cdece31`, unless stated otherwise. All provenance in this section is `internal`.

| Source | What was used and its evidentiary limit |
| --- | --- |
| [Lead atlas README](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/knowledge/leads/ecdlp/README.md) and its 147 lead files | Cross-repository family map, recorded dispositions, evidence pointers and the warning that absence of a match proves nothing. The indexed files are not 147 independent replays. |
| [Review-state snapshot](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/knowledge/leads/ecdlp/REVIEW_STATE.json) | Historical review pins and tallies. Current main ancestry and live tallies differ; the dated empty-delta statement was not assumed current. |
| [Atlas review report](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/docs/reports/ecdlp-lead-atlas-20261024/README.md) | Explicit summary-depth limitations, source conflicts, and historical recommendations. Its IC-first ranking does not govern the current user's request. |
| [Known-results map](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/knowledge/frontiers/ecdlp/README.md) and 52 KR rows | Literature pointers and model scopes, indexed and matched locally. Underlying papers were read selectively, not all reverified. |
| [Idea registry](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/ideas/idea_registry.tsv), [deferred index](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/ideas/deferred/README.md), [rejected index](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/ideas/rejected/README.md) and `outputs/_blacklist_wrapped.txt` | Detection of prior formulations. A deferred or rejected proposal may have had no scientific execution; it must not be described as a measured failed algorithm. |
| [IDEA-050](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/ideas/ECDLP-IDEA-050_spinor_matchgate_addition_transform_hypothesis.md) | Existing matchgate/Pfaffian transform proposal. A new name for contraction is insufficient. |
| [IDEA-070](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/ideas/rejected/ECDLP-IDEA-070_p_kernel_reverse_automaton_hypothesis.md) | Exact reverse-automaton proposal and its constructor/orientation gap. |
| [IDEA-111](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/ideas/deferred/ECDLP-IDEA-111_radical_montgomery_ladder_branch_ideal_quotient_hypothesis.md) | Full branch-union quotient proposal; explicitly theorem-deferred and unrun. Its global representation obligations are distinguished from target-conditioned evaluation. |
| [IDEA-156](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/ideas/rejected/ECDLP-IDEA-156_combinatorial_nullstellensatz_source_self_reduction_hypothesis.md) | Coefficient-extraction oracle circularity. The plan must supply its evaluator rather than assume it. |
| [IDEA-379](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/ideas/rejected/ECDLP-IDEA-379_ax_katz_divisibility_source_locator_hypothesis.md) | Divisibility/existence distinction for many-solution fibres. Uniqueness changes the count's interpretation, not its computational difficulty. |
| [Projection panel IDEA-20260817-84755b](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/ledger/proposals/IDEA-20260817-84755b.yaml) and [tracked-object sourcing report](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/research/ecdlp_tracked_object_enumeration_20260905.md) | Existing deterministic/probabilistic distinctions and the prior example of a novelty conclusion overturned by a semantic match. Not empirical support for the proposed workstream. |
| [Inventor protocol](https://github.com/aburan28/crypto-autoresearcher/blob/ab0609ebee3d17527a51667591bda56f7cdece31/docs/inventor-protocol.md) | Baseline, collision, quantifier and method-ceiling audits; a list of rejected mechanisms is not an impossibility result. |
| [Prime-field breakthrough programme in crypto](https://github.com/aburan28/crypto/blob/5cb553810e5bbfbd8691ec614ffcaacefc625757/RESEARCH_PRIME_FIELD_BREAKTHROUGH_PROGRAM.md) and [prime-field implementation note](https://github.com/aburan28/crypto/blob/5cb553810e5bbfbd8691ec614ffcaacefc625757/RESEARCH_PRIME_FAST_ECDLP.md) | Existing enumerative IC, lattice and preprocessing-rho routes. These are prior internal analyses and measurements, not independent measurements from this session. |
| The three `AGENTS.md` files, root READMEs, and shared lab contract | Repository roles, artifact and evidence requirements, source-reading discipline. Current user direction overrides earlier IC prioritization. |

`atlas-match-direct.txt` records the repository tool's lexical match for `direct scalar Boolean circuit target-conditioned parity cancellation carries`. It returns known Boolean-system work, existing lossy-projection work and the algebraic-transform corpus among other entries. Its score is relevance, not a novelty probability. The first two invocation attempts failed on missing local import paths; materializing the repository dependency and using `PYTHONPATH=.` made the unchanged matcher run. No scientific computation was involved.

Targeted connected-GitHub searches also covered tensor/carry, inverse ladder, modular composition, interval products, Lattes maps, carry linearization, parity, coefficient extraction, target conditioning, Miller derivatives, and unique-witness/tagged-count terminology. Some broad tokenized searches were noisy. A search-rate limit was encountered; bounded successful searches followed later. These facts limit any absence claim.

## External primary sources

Provenance is `retrieved`, verified_by `Codex session, 2026-10-25`, at the reading depth indicated.

| Source | Material read and use |
| --- | --- |
| Kimmig, Van den Broeck and De Raedt, [Algebraic Model Counting](https://arxiv.org/html/1211.4475) | Definition 2, the GRAD semiring, and Section 3's soundness/compilation conditions. Establishes that sum-product tagging is prior art and that naive bottom-up evaluation on arbitrary shared Boolean circuits is unsound. |
| Maene and De Raedt, [The Gradient of Algebraic Model Counting](https://arxiv.org/abs/2502.18406), AAAI 2025 | Abstract and publication metadata. A further prior-art pointer for algebraic differentiation; no theorem from the unread body is relied upon. |
| Dudek, Dueñas-Osorio and Vardi, [Efficient Contraction of Large Tensor Networks for Weighted Model Counting through Graph Decompositions](https://arxiv.org/abs/1908.04381) | Abstract and introduction of the full PDF. Counting-to-tensor reduction and contraction-order optimization are established techniques, not an EC discovery. |
| Corrigan-Gibbs, Henzinger and Wu, [The Structured Generic-Group Model](https://eprint.iacr.org/2026/384), EUROCRYPT 2026 | Abstract and introduction/model description in the author-hosted full PDF. Its restricted-model lower bounds must not be applied to arbitrary concrete-coordinate computations without checking the model. |
| Lauter and Stange, [The elliptic curve discrete logarithm problem and equivalent hard problems for elliptic divisibility sequences](https://arxiv.org/abs/0803.0728) | Abstract, revision and publication metadata. EDS reformulations are an existing research family; no unpublished decoding consequence is inferred. |
| [Cartier–Miller coefficient-sum manuscript repository](https://github.com/bbrhuft/Cartier-Miller-evaluation-of-genus-one-coefficient-sums) | Current README and stated scope: a fixed characteristic-dependent coefficient cutoff, not arbitrary scalar-interval counting. The authors label it unrefereed and novelty unsettled. It is excluded as support for a new DLP algorithm; its proofs were not audited. |

The classic Galbraith–Gaudry survey was located, but its full PDF fetch was blocked; it is a further-reading pointer, not evidence of full literature coverage. Generic ECDLP, tensor methods and arithmetic circuits are broad literatures; the searches here cannot certify an original algorithm.

## Preserved limits and unchanged graphs

No prior raw experiment was replayed, no scientific trial was launched, no performance comparison was measured, and no new structural theorem was independently verified. The current draft does not satisfy the user's novelty criterion for an algorithm. The unsupplied operation and the remaining source coverage are stated in the plan rather than converted into an impossibility claim.

The lead and known-results maps, and the atlas report's disposition/frontier views, were checked for the proposed topic. This report changes none of their evidence or statuses, so their canonical graph sources and renderings remain unchanged. The new diagram depicts only this plan's dependency structure and marks the missing operation explicitly.
