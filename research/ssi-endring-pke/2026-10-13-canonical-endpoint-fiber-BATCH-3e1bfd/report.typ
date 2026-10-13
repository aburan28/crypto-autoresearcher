#set page(paper: "a4", margin: (x: 16mm, y: 14mm), numbering: "1")
#set text(font: "DejaVu Sans", size: 8.8pt, fill: rgb("172033"))
#set par(justify: true, leading: 0.58em)
#set heading(numbering: "1.", outlined: true)
#show heading.where(level: 1): it => block(above: 0.9em, below: 0.42em)[#set text(size: 14pt, weight: "bold", fill: rgb("173f68")); #it.body]
#show heading.where(level: 2): it => block(above: 0.7em, below: 0.3em)[#set text(size: 10.8pt, weight: "bold", fill: rgb("244a7c")); #it.body]

#align(center)[
  #text(size: 20pt, weight: "bold", fill: rgb("173f68"))[CEFC-PKE endpoint-fiber search]
  #v(3pt)
  #text(size: 12pt)[Candidate and adversarial evaluation]
  #v(4pt)
  #text(size: 8.5pt, fill: rgb("526174"))[GOAL-SSI-2fa82a · BATCH-3e1bfd · TASK-20261013-c6961f · 2026-10-13]
]

= Result

This round did *not* produce a complete or secure public-key encryption scheme. It produced one conditional interface, CEFC-PKE, and independently evaluated it under O1–O6. No concrete nontrivial edge label, exact key/endpoint distribution, polynomial complete-ring endpoint evaluator, or attacker-to-complete-EndRing extractor was supplied. The raw XOR syntax is also IND-CCA2-insecure: one related-ciphertext query recovers the challenge message.

The composed result is *zero survivors*. O1 is open; O2 is contradicted for the submitted complete-and-efficient construction claim; O3–O6 are open. Novelty, IND-CPA security, a complete-EndRing reduction, QPT/QROM security, and NIST Category 5 are not established. Scientific, implementation, formalizer, benchmark, and parameter-selection runs were zero.

#figure(image("flow.svg", width: 100%), caption: [CEFC-PKE's intended flow. Blue arrows are declared or conditional operations; dashed red arrows are missing algorithms or reductions; orange is the worked raw-CCA break.])

= Frozen method and candidate

The opening admitted one mechanism: can public walk sampling, endpoint-fiber invariance, complete-EndRing-assisted endpoint evaluation, and attacker-to-complete-EndRing extraction coexist in one exact interface? J1 owned O1/O2 and executable syntax; J2 owned O3/O4 and ring necessity; blind J3 owned O5/O6, raw security, novelty, QPT/QROM, and Category 5. Composition copied verdicts without voting.

For a public curve E and sampled admissible walk w, define the endpoint F_E(w)=C and the proposed label sum I_E(w)=sum EdgeLabel(e). The required fiber theorem says equal endpoints imply equal label sums. A complete evaluable basis W_E of End(E) is intended to compute that value from C through RingPotential. Encryption emits (C, m xor H_pad(pp,E,C,I_E(w),|m|)). This is a typed conditional relation, not an instantiated algorithm.

If sender and recipient obtain the same encoded potential, XOR cancellation recovers the actual message. A value constant on every endpoint fiber also factors set-theoretically through the endpoint. Those definitional consequences do not establish that a nontrivial label exists, that a complete ring efficiently evaluates it, or that a complete ring is necessary.

= Construction and correctness review

== J1 — exact distributions and algorithms

J1 stopped at the first gate. TrapCurveGen_ER and its public marginal are undefined; WalkSample is abstract; EdgeLabel, CompleteEvalBasis, and RingPotential are absent; encodings, retries, bit lengths, and costs are open. The sender cannot compute its value and the recipient cannot compute the same value from W_E and C. O1 remains open and O2 is contradicted for the submitted claim that the construction is complete and efficient. This is not a nonexistence theorem.

== J2 — fibers and complete-ring necessity

For same-length walks containing distinct subpaths P and Q between the same vertices, unequal branch sums create equal endpoints but different sender values. The packet supplies neither a concrete collision nor a theorem excluding all such collisions because the sampler and label are uninstantiated.

The public coboundary EdgeLabel(U to V)=h(V)-h(U) is a decisive control: its sum telescopes to h(C)-h(E), giving perfect fiber invariance with no secret. Hence invariance alone cannot establish complete-ring necessity.

Decryption observes W_E only through D_E(C)=RingPotential(pp,E,W_E,C). No theorem excludes a public endpoint computation, exact-path trapdoor, one evaluator, finite torsion action, cache, compressed witness, or opaque decoder. O3 and O4 remain open.

= Security review

The required reduction inputs an exact-distribution EndRing challenge E, simulates the byte-identical PKE game for a successful adversary, and outputs a verifier-accepted complete evaluable saturated rank-four basis with an explicit QPT/QROM success loss. No such extractor exists. The available arrow complete EndRing → RingPotential → decrypt is reverse functionality, not security. A newly named endpoint-potential game is not EndRing hardness.

The raw syntax also breaks under CCA. Given challenge (C,v), query the distinct ciphertext (C,v xor Delta). Decryption reuses the same endpoint potential and pad, returning m_b xor Delta; undoing Delta reveals m_b. One decryption query, zero random-oracle queries, and advantage 1/2 suffice. This result is scoped to the frozen unauthenticated XOR syntax.

= Obligation and gate ledger

#table(
  columns: (0.38fr, 0.24fr, 0.38fr),
  inset: 4.2pt,
  stroke: rgb("cbd5e1"),
  [*Gate*], [*Status*], [*Decisive boundary*],
  [O1 distribution], [open], [No exact key/endpoint law],
  [O2 algorithms], [contradicted], [Honest algorithms stop at absent calls],
  [O3 correctness], [open], [No concrete fiber/failure theorem],
  [O4 ring necessity], [open], [Smaller endpoint decoders not excluded],
  [O5 reduction], [open], [No attacker-to-ring extractor or loss],
  [O6 full view], [open], [Adaptive, repeated, auxiliary, and costs incomplete],
  [Raw IND-CCA2], [contradicted], [One related-ciphertext query],
  [Novelty / QPT / Cat-5], [not established], [No source, theorem, parameter, or resource case],
)

= Category-5, novelty, and scope boundary

No parameter set was selected. There is no completed classical or quantum attack portfolio, reduction loss, memory/data/preprocessing accounting, qubit/depth/gate estimate, smaller-witness cost, or measured implementation resource. No current normative NIST Category-5 source was inspected inside the frozen scope. Field size or nominal bit count cannot replace those obligations.

No external primary-source novelty search occurred. Internal comparisons distinguish CEFC-PKE from earlier repository directions, but internal nonduplication is not a literature novelty result.

The automated independence checker exited 2 because the standalone review plan lacks the nested review_plan block expected by the tool. That administrative defect is preserved and not called a pass. Reviewer attestations report no sibling-review reads.

The result applies only to CEFC-PKE as frozen. It does not establish universal nonexistence of a conservative edge label, complete-ring endpoint evaluator, EndRing PKE, or CCA transform. No automatic successor is authorized. A later separately ranked packet must first supply an exact real key/walk law, a concrete nontrivial EdgeLabel/RingPotential pair, an executable honest trace, and a proved fiber theorem.

= Evidence map

- Opening: TASK-20261013-6b28a0 and DEC-20261013-c399a4.
- Producer: TASK-20261013-64d436, frozen by TASK-20261013-fc14f6.
- J1: TASK-20261013-47054b, hash 47713e6e…84f79.
- J2: TASK-20261013-414c2f, hash ad3b5228…7e8e3.
- Blind J3: TASK-20261013-883a47, hash d42d55d5…9ad36.
- Composition: TASK-20261013-474c15, hash f8e548a2…530c85.
- Review custody: EV-SSI-a6d309 and DEC-20261013-e28a61.
