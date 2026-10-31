# Gate N1-N4: QC1 (tau, mu) admission region for IC decomposition oracles, find-one vs list-all

Gate run 2026-10-25 by the N1-N4 gate subagent. Read-only on the repositories; everything below is under
`/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/`.
Environment for the tools: `LEAD_ATLAS_CRYPTO`, `LEAD_ATLAS_CRYPTANALYSIS`, `LEAD_ATLAS_ECC_CHALLENGES` exported as instructed; run from `/Volumes/SSD990-2/crypto-autoresearcher`.

## VERDICT (summary)

**duplicate_of_lead**, nearest lead `LEAD-ICE-generic-oracle-arity-cost-floor` (closed_obstructed; its `forecloses` list contains the phrase
"arity threshold for point-decomposition index calculus"), with the same object already filed in the ledger as
`IDEA-20260803-fa9839` / `H-ICEX-9e54c2` (specified) / `EXP-ICEX-146ff5` (approved_execution_withheld). QC1 states that it "escapes nothing itself", so it does not answer
the obstruction of that lead; the strict rule makes it a duplicate. Residual increment (an arithmetic reconciliation of two thresholds the corpus already holds in different normalisations; it changes no disposition) is described in section "Residual delta" at the end.

---------------------------------------------------------------------------------------------------

## RAW --match OUTPUTS (verbatim; saved copies: atlas_run_{1..4}.txt, frontier_run_{1..4}.txt in this directory)

Default `--limit` was used (8 rows per run). Run 4 is my own extra phrasing.

### lead_atlas.py --match, run 1
```
=== ATLAS RUN 1: per-attempt oracle exponent tau and table exponent mu escape region for an index-calculus decomposition oracle ===
   17  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   12  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
   10  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
    9  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    9  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
    9  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
    9  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7)
    9  LEAD-ICP-gfp5-oa-sdhp-jv                     open_next_step     Joux-Vitse oracle-assisted static DH and (n-1)-point decomposition on E(F_{p^5}), p = 2^64 - 2^32 + 1
```

### lead_atlas.py --match, run 2
```
=== ATLAS RUN 2: how fast must a point decomposition oracle be per attempt to beat Pollard rho ===
   18  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
   18  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   15  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
   14  KR-RHO-e7f98e                                known_result       GPU Pollard rho: academic state of the art is thin
   14  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
   13  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
   13  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7)
   12  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves
```

### lead_atlas.py --match, run 3
```
=== ATLAS RUN 3: decomposition oracle that is not a generic time/memory trade-off obeying S*T^2 >~ N ===
   14  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
   12  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   11  LEAD-EXO-augmented-oracle-ggm                closed_obstructed  Augmented oracles (x-, y-, full-point, halving, endomorphism-image, incidence) and GGM simulability
   11  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7)
   10  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
   10  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
   10  LEAD-STR-endo-scalar-action-generic          closed_obstructed  Endomorphism-augmented generic and witness-lattice attacks on a prime-order subgroup
    9  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
```

### lead_atlas.py --match, run 4
```
=== ATLAS RUN 4: admission region time-space generic-group lower bound index calculus factor base size relations ===
   19  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   16  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   15  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   15  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
   15  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   14  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
   14  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
   13  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
```

### build_frontier_map.py --match, run 1
```
=== FRONTIER MAP RUN 1: per-attempt oracle exponent tau and table exponent mu escape region for an index-calculus decomposition oracle ===
KR-RHO-cd0049  score=7  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-5765d2  score=6  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-8b9daa  score=6  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-081a58  score=5  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-955fd6  score=5  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-1fcdbc  score=4  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-5a43e5  score=4  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
```

### build_frontier_map.py --match, run 2
```
=== FRONTIER MAP RUN 2: how fast must a point decomposition oracle be per attempt to beat Pollard rho ===
KR-RHO-e7f98e  score=14  [record/reported]  GPU Pollard rho: academic state of the art is thin
    sources: KN-LIT-c75942, KN-LIT-2b1b99, KN-LIT-34a845, KN-LIT-74dfa6, KN-LIT-2c4f3d, KN-LIT-a4b3d8
KR-RHO-6654ba  score=12  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-RHO-cd0049  score=12  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-IC-1fcdbc  score=11  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-5765d2  score=11  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-955fd6  score=10  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-RHO-1c2928  score=10  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-13bf67  score=9  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
```

### build_frontier_map.py --match, run 3
```
=== FRONTIER MAP RUN 3: decomposition oracle that is not a generic time/memory trade-off obeying S*T^2 >~ N ===
KR-IC-081a58  score=6  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-8b9daa  score=6  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-955fd6  score=6  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-1fcdbc  score=4  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-a4dd54  score=4  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-f3da82  score=4  [known_mechanism/reported]  F4 trace reuse across many similar systems
    sources: KN-LIT-c137bd
```

### build_frontier_map.py --match, run 4
```
=== FRONTIER MAP RUN 4: admission region time-space generic-group lower bound index calculus factor base size relations ===
KR-IC-5931ee  score=19  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-b0fcda  score=15  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-a4dd54  score=12  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-46d822  score=8  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-49c882  score=8  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-5a43e5  score=8  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-73db3f  score=8  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-9e610d  score=8  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
```

---------------------------------------------------------------------------------------------------

## N1 Atlas collision

Lead YAMLs opened and read (mechanism + obstruction + forecloses): ICE-generic-oracle-arity-cost-floor, ICP-generic-table-decomposition,
ICB-generic-table-oracle, ICE-rootfind-pairtable-oracle, ICE-gpu-rootfind-oracle, ICB-prime-degree-algebraic-decomposition,
ICE-charged-toy-ic-exponent-vs-rho, EXO-augmented-oracle-ggm, RHO-generic-sqrt-lower-bound, ICP-algebraic-membership-factor-base,
ICP-isogeny-transported-relation-yield, STR-class-representative-ic-selection, plus (not in the top 5, but the candidate places
built oracles against them) ICE-sat-xor-pdp-oracle, ICB-decomposition-encoding-and-sat, ICE-prime-field-semaev-solving-degree,
ICP-coppersmith-smallroot-semaev, ICE-hybrid-guess-determine-l7, ICP-full-width-arity-grid, EXO-methodology-instruments.
KR rows among the top 5 (handled in N2): KR-RHO-e7f98e, KR-IC-5931ee, KR-IC-b0fcda.

### Top hits per run, with decision

| run:rank | lead | disposition | same mechanism as QC1? |
|---|---|---|---|
| 1:1, 2:2, 3:2 | LEAD-ICE-rootfind-pairtable-oracle | open_blocked | No. Constant-factor oracle (batched root finding / pair table) that "moves the constant, never the p/|F| exponent". QC1 would be an instrument that classifies it (outside R_m), not a rival. |
| 1:2, 2:3, 3:5 | LEAD-ICB-generic-table-oracle | closed_obstructed | Same wall, binary side. QC1's generic corollary is this obstruction restated in (tau, mu). |
| 1:3, 2:5 | LEAD-ICE-gpu-rootfind-oracle | open_blocked | No. GPU constant for the relation phase. |
| 1:4 | LEAD-ICB-prime-degree-algebraic-decomposition | open_blocked | Partly: its mechanism already states the threshold "Relation collection beats rho only if a failed attempt costs 2^{alpha l} with alpha < m/2 - 1". That is QC1's find-one tau-only boundary (m >= 4) in binary coordinates. |
| 1:5 | LEAD-ICE-charged-toy-ic-exponent-vs-rho | open_blocked | No (it is the consumer). QC1 proposes to change its next step; see below. |
| 2:1, 3:1 | LEAD-ICE-generic-oracle-arity-cost-floor | closed_obstructed | **Yes, nearest.** See quote below. |
| 3:3 | LEAD-EXO-augmented-oracle-ggm | closed_obstructed | Related to the corollary (SO-GEN / GGM-simulable oracles); QC1 adds nothing to its obstruction. |
| 3:4 | LEAD-ICP-generic-table-decomposition | closed_obstructed | **Yes (prime side).** Its `revisit_when` is a one-point instance of QC1's region. |
| 4:2 | LEAD-ICP-isogeny-transported-relation-yield | open_blocked | No (yield by base stratum). |
| 4:4 | LEAD-ICP-algebraic-membership-factor-base | closed_obstructed | Not the same mechanism. QC1 uses its consequence (tau >= m for a grid indicator oracle, SO-ALGFB) as an input, does not escape it. |
| 4:5 | LEAD-STR-class-representative-ic-selection | open_next_step | No. |

### The nearest lead, quoted (Scope clause included)

LEAD-ICE-generic-oracle-arity-cost-floor, `mechanism`: "Treat the oracle as an abstract m-SUM search or charge it nothing, and ask whether any arity
m or base size puts point-decomposition IC below rho. The product law relations x targets x oracle = m 2^n is independent of dim V, and the store any
sub-rho cell needs costs as much as rho's whole walk."

`obstruction.statement` (kind cost_model): "For oracles of class ENUM, MITM and MITM_CAPPED on binary curves of prime degree n, the replicated v2 cost
model has zero in-domain sub-rho cells (EV-SEMBIN-b6d042); on ECC2K-130 a free oracle at m = 3 still costs 2^68.58 against rho's 2^60.81 (KN-FIND-aa2efc);
in-model, structured generic-group bounds (CHW 2026/384) and non-adaptive time-space bounds (DKM 2025/783) give the same wall. **Scope: oracles that do
not read curve coordinates algebraically;** the FREE control does have sub-VOW cells, so the obstruction is the oracle class, not IC."

`forecloses`: free decomposition oracle lifts IC below rho; **arity threshold for point-decomposition index calculus**; generic m-SUM decomposition
oracle; larger arity m makes enumeration IC beat rho; multi-target amortisation rescues exhaustive-solver IC.
`ledger_refs` include IDEA-20260803-fa9839, IDEA-20260830-4ab603, H-ICEX-6f3e4b, H-ICEX-9e54c2.

### The prime-field lead, quoted

LEAD-ICP-generic-table-decomposition `obstruction.statement` (kind theorem): "Any decomposition oracle that enumerates or table-looks-up factor-base
elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the
two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). Measured on generated prime-order E/F_p, 12-32 bits:
exhaustive IC exponent 0.99 (m = 2) and 1.01 (m = 3), mitm 0.67 / 0.75 / 0.60 at m = 3/4/5 (4/7 at m = 7) against rho 0.50 [0.48, 0.52]; Table B gap to
matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4. **Scope: any generic (enumeration/table) decomposition over F_p.**"
`revisit_when`: "A non-generic decomposition oracle exists with per-attempt cost T_dec << p^{1/4} at arity m = 4 (an S_5 oracle at B ~ p^{1/5}), or a
decomposition test sub-linear in |F|." This is QC1's R_4 boundary (tau < 1 at beta -> 1/4 gives T < N^{1/4}) already written as a revisit condition.
Evidence row: crypto `RESEARCH_PRIME_FIELD_BREAKTHROUGH_PROGRAM.md` sections 1 and 2.4 ("S*T^2 table and arity-vs-linear-algebra optimum; first arity that
could beat rho is m = 4").

### The binary threshold, quoted

LEAD-ICB-decomposition-encoding-and-sat `obstruction.statement` (kind measured, closed_obstructed): "Every SAT or enumeration method measured has
per-attempt UNSAT cost 2^{alpha l} with alpha ~ m (WDSat 2.9985 bits per unit l at m = 3, reproducing 2^{3l}/3!; alpha 4.09-4.33 at m = 4, l = 3..5),
while beating rho needs alpha < m/2 - 1; at m = 3, 4 the measured families extrapolate 50-150 bits above budget at n = 131."
These are the same numbers QC1 lists as its "WDSat at m = 3 (R_3 empty) and m = 4 (4.09-4.33 vs < 1)" placement. The m = 3 cell of the open SAT lead
(LEAD-ICE-sat-xor-pdp-oracle, "fit alpha(m) at m in {3,4,5}") is therefore already measured (2.9985) in a closed lead, and independently closed by the
free-oracle floor at m = 3 (KN-FIND-aa2efc, 2^68.58 vs 2^60.81). Dropping m = 3 from that fit is sensible but changes no disposition.

### Standing obstructions: does QC1 escape any?

QC1 says "escapes nothing itself; it certifies when an oracle has escaped". Checked against: SO-TABLE (LEAD-ICP-generic-table-decomposition,
LEAD-ICB-generic-table-oracle: both quoted above/below), SO-GEN (LEAD-RHO-generic-sqrt-lower-bound: "any generic algorithm needs Omega(sqrt r) group
operations for a prime-order-r group ... **Scope: all generic algorithms, any field, any r.**"), SO-ALGFB (LEAD-ICP-algebraic-membership-factor-base:
"membership polynomial prod(x - v) of degree B ... **Scope: prime-order E/F_p, any base of size B.**"). QC1 does not claim an oracle outside these;
it prices where one would have to lie. The obstruction of LEAD-ICE-generic-oracle-arity-cost-floor therefore stands unanswered, and QC1's output is a
quantitative restatement of the complement of its Scope clause.
LEAD-ICB-generic-table-oracle `obstruction.statement`, for the record: "Every oracle built from group operations and membership tests makes IC a
generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply ... **Scope: all binary and Koblitz curves,
one target, setup charged.**"

### Effect on open leads (the "advances_lead" test)

* LEAD-ICE-charged-toy-ic-exponent-vs-rho (open_blocked). QC1 would rewrite its next step to "admit only a backend whose derived (tau, mu) lies inside
  R_m" and record the arm-M verdict as implied by R_5 plus the CRT ceiling audit. The ledger already carries the machinery: `IDEA-20261018-ac3694`
  names the approved backend with an "admission-refusing driver" (EXP-ICEX-153c34), `H-ICEX-6ca21f` (approved) is the ceiling audit QC1 cites, and the
  lead's own `forecloses` contains "go/no-go on optimistic handed-over inputs" (IDEA-20260815-47638d). I did not open the EXP-ICEX-153c34 specification
  (record budget), so I cannot say whether its admission rule already equals the tau-only boundary. QC1's contribution to this lead is a relabelling of a
  threshold the program already uses, not a new discriminator.
* LEAD-ICE-sat-xor-pdp-oracle (open_next_step). Increment is "drop m = 3": see above, already measured and already closed elsewhere.
* LEAD-ICB-prime-degree-algebraic-decomposition (open_blocked). Already states alpha < m/2 - 1.
So `advances_lead` is not earned: no open lead gets a next step it could not already write from its own text and the ledger.

### What QC1 does that the `forecloses` phrases do not cover (the honest delta)

1. **Find-one vs list-all semantics: both halves are already in the corpus, in different normalisations; the only increment is that they disagree for m >= 5.**
   * List-all side (prime field). The two-term model of IDEA-20260803-fa9839 (`T = m! N D / B^(m-1) + c_LA B^2`, threshold `d < (m-3)/4`) charges
     m! N / B^m trials per relation, which is < 1 once B^m > N; that is only meaningful if one attempt returns all ~pi = B^m/N decompositions. The record
     itself names the relevant mechanism, though as a missing ingredient rather than as a semantics switch: "it requires the relation-search term itself to be
     cheaper than m! N / B^(m-1) trials, which ... can only come from harvesting more than one usable relation per trial", and its observation-collision list
     includes "harvest-all multi-relation yield". The threshold table itself (`arity_threshold_table`, d_max = (m-3)/4) is not split by that distinction.
   * Find-one side (binary). LEAD-ICB-decomposition-encoding-and-sat (closed) and LEAD-ICB-prime-degree-algebraic-decomposition (open_blocked) state the
     threshold as `alpha < m/2 - 1`, which is QC1's find-one tau-only boundary for m >= 4. (My earlier index regex for "harvest-all / more than one relation /
     relations per trial" came back empty only because the index text fields are truncated; the phrase is in the opened fa9839 record.)
   * What QC1 adds: noticing that these two thresholds, written in B-exponent form `m/2 - 1` (find-one) and `m - 3` (list-all), differ for m >= 5, so that the
     prime-field N-unit windows of section 2.4 / fa9839 for m >= 5 are list-all values. I re-derived the region analytically and checked it (see "Independent
     re-check"): find-one tau-only boundary is `tau < min(m/2-1, m-3)`, i.e. in N-units `d < 1/2 - 1/m` for m >= 4 (m = 5: 0.30, m = 6: 0.333, m = 8: 0.375),
     against `(m-3)/4` (m = 5: 0.50, m = 6: 0.75, m = 8: 1.25). For m = 4 both give N^{1/4}; for m <= 3 both are empty. This is a normalisation reconciliation
     plus two numbers per m, an annotation for the closed lead, not a new lead.
2. **The mu (table) axis for m > 2.** IDEA-20260830-4ab603 / H-ICEX-6f3e4b has the D-versus-space coupling at m = 2 only. QC1's `tau + mu < m - 1` is the three-term
   exponent algebra max(relations, mu*beta, 2*beta) < 1/2 solved for all m. It is arithmetic in the cost model, not a lower bound.
3. **m = 3 tie.** Find-one boundary is tau = 0 at m = 3, not m/2 - 1 = 0.5. Irrelevant in practice: measured alpha(m=3) is 2.9985.
Everything else in QC1 (generic corollary, tau + mu = m generic splits, predicted mitm exponents, placement table) is already in the corpus; see N2/N3.

---------------------------------------------------------------------------------------------------

## N2 Known results (build_frontier_map.py --match; raw output pasted above)

Hits and their relation to QC1:
* KR-RHO-13bf67 (Shoup/Nechaev generic lower bound, textbook_fact/proven): QC1's "generic corollary" (an oracle built from group operations and
  membership tests cannot lie in R_m) is this, applied to a cost model. Known result. Also appears in run 2 and the CGK row below.
* KR-RHO-7d93f6 (Dinur, T^2 S = Theta~(C^2 N) for many collisions) and KR-RHO-cd0049 (measured negation-map BSGS vs floor): time-space background, not the region.
* KR-IC-5931ee (Naive Semaev IC over prime fields cannot beat generic methods, known_negative/proven, score 19 in run 4): the headline conclusion for
  every generic-oracle cell of QC1's placement table.
* KR-IC-5765d2 (SAT/XOR for point decomposition), KR-IC-1fcdbc (char-2 summation slower than rho), KR-IC-955fd6, KR-IC-8b9daa, KR-IC-081a58,
  KR-IC-46d822 (Gaudry q^{2-2/n}), KR-IC-a4dd54, KR-IC-5a43e5, KR-IC-b0fcda, KR-IC-9e610d (Galbraith-Gaudry survey consensus): context.
* KR-RHO-e7f98e (run 2, rank 4: GPU Pollard rho, academic state of the art is thin), KR-RHO-6654ba (point halving as a rho step): rho-engineering rows, not the same object.
* Not in any KR row: the tau/mu escape region itself, the find-one/list-all split. The balance of relation cost against linear algebra to read off a per-attempt
  oracle threshold is the standard IC cost analysis (recalled: Diem, Compositio 2011; Galbraith-Gaudry 2016 survey = KR-IC-9e610d), so the region is a
  re-reading of known cost analysis plus the Shoup/CGK lower bounds. Verdict for N2: **known_result for the generic corollary and the two-term balance; the
  find-one/list-all reconciliation has no KR hit; it is the only part I cannot place in the literature (recalled, not searched beyond the abstracts below).**

### Citation provenance (this gate)

| citation | provenance | note |
|---|---|---|
| Corrigan-Gibbs, Kogan, ePrint 2017/1113 (EUROCRYPT 2018) | **retrieved** this session (WebFetch eprint.iacr.org/2017/1113) | Abstract confirms generic DL with S-bit advice, time T, success eps: "ST^2 = Omega~(eps N)" for prime order N. |
| Corrigan-Gibbs, Henzinger, Wu, "The Structured Generic-Group Model", ePrint 2026/384 (EUROCRYPT 2026) | **retrieved** (abstract only; WebFetch eprint.iacr.org/2026/384) | Abstract: DL algorithm exploiting structure in at most a delta fraction takes time ~ min(sqrt q, 1/delta); also states lower bounds for "elliptic-curve points". NOTE: the program's own audit (crypto `research/lit2026_w3_ggm_audit_20261011/README.md`, "Limits") says the EC section "could not be extracted" from the copy it read; the live abstract says EC-point bounds are proved. Theorem numbers in QC1 are as quoted from that README and were not re-read here. |
| Shoup, EUROCRYPT 1997, LNCS 1233:256-266 | recalled (also KR-RHO-13bf67 in the program's map) | not re-fetched |
| De-Trevisan-Tulsiani CRYPTO 2010; Golovnev-Guo-Horel-Park-Vaikuntanathan STOC 2020 (arXiv 1907.08355) | recalled | I find no step of QC1's region derivation that uses them: the region is cost-model arithmetic. The statement "must beat random-function inversion of F^m -> G by B^{1+eps}" is asserted in the candidate, not derived; I did not verify it. |
| Dinur-Keller-Marmor ePrint 2025/783 (non-adaptive S*T >~ N) | as summarised in the program's audit README (read), not fetched | |

---------------------------------------------------------------------------------------------------

## N3 Ledger (grep of `ledger/.index/{proposals,hypotheses,experiments}.jsonl`; index claim/mechanism fields are truncated, so this is a lower bound on overlap)

Key terms used: "per-attempt", "admission/admissible", "S*T^2" variants, "time-space/time-memory", "oracle ... exponent", "list-all/find-one", "T_dec",
"Corrigan/CGK/Shoup", "decomposition oracle", "arity threshold", "function inversion / 3SUM-indexing / Golovnev / De Trevisan / Yao".

Records that may be the same object (id, status, first ~100 chars of claim/title):

| id | status | claim (first 100 chars) |
|---|---|---|
| IDEA-20260803-fa9839 | proposed | "The arity threshold - write down, and validate against a known exponent, exactly how cheap the decomposition oracle must be for point-decomposition index calculus to beat rho at each arity m" |
| H-ICEX-9e54c2 | specified | "FOR EVERY FIXED ARITY m >= 2, EVERY LINEAR-ALGEBRA EXPONENT omega IN THE DECLARED RANGE, AND EVERY FAMILY OF FACTOR BASES OF SIZE B(N) IN A GROUP OF PRIME ORDER N, the fully charged cost of point-dec..." |
| EXP-ICEX-146ff5 | approved_execution_withheld | "The arity threshold - a fully charged, calibration-gated closed-form comparison of point-decomposition index calculus against matched Pollard rho and BSGS, emi..." |
| H-ICEX-71bce3 | proposed | "The comparison this question exists to decide - when point-decomposition index calculus beats Pollard rho - can be written in closed form with zero compute, and the resulting model is FALSIFIABLE aga..." |
| IDEA-20260830-4ab603 / H-ICEX-6f3e4b | proposed | "THE FREE DECOMPOSITION ORACLE IS NOT A BOUNDARY LIFT, IT IS A MEMORY PURCHASE, AND ITS PRICE IS EXACTLY B^2" (D and space are coupled, m = 2; T*S never below Theta(N)) |
| IDEA-20260727-003 | proposed (novelty_status known) | "Free-oracle admissibility frontier - measuring the relation-count and linear-algebra floor that any prime-field index calculus must clear before a decomposition cost is charged" |
| EXP-ICEX-60c93c | draft | "Emit the two-regime alpha(theta, m) table with its identity gate and its exhibited identifiability collision in exact rational arithmetic..." (**unread**; "two-regime" may already be a pi < 1 / pi > 1 split) |
| IDEA-20260920-a92b0f | proposed | "S1 ANSWERED IN BOTH DIRECTIONS: P*T = Omega(n) is FALSE in the non-uniform generic group model Corrigan-Gibbs-Kogan actually use..." (CGK model distinction) |
| IDEA-20261018-49fdf7 | proposed | "Formal frame for closing pair-table and k-sum work: structured-GGM and non-adaptive time-space bounds" (the SGGM/DKM ingredient of QC1, applied to the same designs) |
| H-ICEX-a91960 | proposed | "PREPROCESSING MOVES THE PER-TARGET EXPONENT ONLY BECAUSE THE OFFLINE PHASE IS FREE ... KN-LIT-013 (Corrigan-Gibbs and Kogan, filed)" |
| IDEA-20260904-d84512 / H-ECDLP-77caa5 | unverified / specified | "ADVICE LENGTH UNDER A CHARGED DECOMPRESSION TIME ... the generic frontier S*T^2 = Theta~(N)" (x-coordinate tables) |
| IDEA-20260926-d1adfc, -dacb83, -9cc043, -89886c | proposed | "CEILING FIRST ..." per-attempt decomposition-oracle cost-column records (R1, Class I) |
| H-SEMBIN-8e7ae3 | specified | "...an m-summand index calculus whose decomposition oracle is a generic m-SUM search cannot fall below the van Oorschot-Wiener rho baseline at any summand c..." |
| H-ECDLP-c3d48a | specified | "Stage 0 windowed-tree threshold identities - m=3 empty admissible band - before any small-root lattice" (same "empty at m = 3" statement for the lattice route) |
| IDEA-20260815-47638d, IDEA-20260815-0253b6 | proposed | go/no-go on optimistic inputs; reachability audit of admissible deferred-lane ranges (same instrument spirit) |

Opened in full (3 records, as allowed): IDEA-20260803-fa9839 (read to the end of `predictions`/`minimal_test`), IDEA-20260830-4ab603 (claim, mechanism head),
IDEA-20260727-003 (claim and mechanism).

Decision from those three:
* **IDEA-20260803-fa9839** is the same object. Its claim: "WRITING D_trial = N^d, THIS BEATS RHO IF AND ONLY IF d < (m-3)/4 ... at m <= 3 no admissible
  D_trial >= 1 satisfies it WITHIN THIS MODEL; at m = 4 the decomposition oracle must run below N^(1/4); at m = 5, below N^(1/2)." Its deliverable is a
  machine-readable `arity_threshold_table` d_max(m) = (m-3)/4 with the m <= 3 rows INFEASIBLE-WITHIN-MODEL, "for each deferred measurement ... a verdict
  rather than a datum". That is QC1's list-all region (tau-only), its m <= 3 emptiness, and its use as a screen for deferred measurements. The record
  also states "The model can never establish a prime-field ADVANTAGE, only a threshold and a set of no-go readings" (QC1's tier X, 0 bits).
  My check: fa9839's d_max(m) equals QC1's list-all `tau_max/4` for every m = 2..8 (table in the re-check output).
* **IDEA-20260830-4ab603** is the mu-coupling at m = 2 ("T * S never falls below Theta(N)" along the interpolation). QC1 extends to all m.
* **IDEA-20260727-003** (novelty known) is the free-oracle admissibility frontier ("the admissible region ... installed as a cheap precheck that every
  future proposal in this ledger must pass"). Same instrument idea and wording, tau = -infinity slice.

Whether any of these was ever executed: EXP-ICEX-146ff5 is `approved_execution_withheld`, EXP-ICEX-349205 `review_required`, EXP-ICEX-60c93c `draft`
(from the experiments index). I did not look for an evidence record.

---------------------------------------------------------------------------------------------------

## N4 Notation check (representation, operation set)

QC1's pair: (x-coordinate label in F_p of factor-base points, any presentation of F; Sigma = translation by factor-base elements; object = partial inverse of
the m-fold addition map F^m -> G). Trichotomy class: partial-action (index calculus, Class I of IDEA-20260806-c5d183).
* This is exactly the pair every recorded IC proposal already declares ("Representation R1; Sigma = translation by factor-base elements (Class I,
  partial-action)", e.g. IDEA-20260926-d1adfc, -dacb83, -9cc043, IDEA-20261017-4b1672). No new representation, no new operation set, no new tracked object.
* It is not a restatement of the rigidity results in new notation: c5d183 (constant-or-injective under full translation), 863e36 (projection paired with
  Sigma, block systems of <Sigma>), KN-FIND-ffe1df Theorem C (exact sum-compatible bucket index is a surjective homomorphism, impossible for prime N) all concern
  what a lossy projection can do. QC1 proposes no projection; it is a cost column over the Class I object ("TRICHOTOMY and LOSSY-PROJECTION TEST: not applicable
  to a cost column", the same disposition IDEA-20260926-dacb83 records). So N4 does not turn this into a rigidity duplicate; it also shows there is no new
  arithmetic here.
* KN-OPEN-020: QC1 does not name which open class (high-degree, implicit-membership, target-dependent) a qualifying oracle belongs to; it declares itself an
  instrument. Its G1 row (tau >= m for a Groebner-on-grid-indicator oracle) is inside the scoped-out bounded-degree class (SO-ALGFB), consistent with
  KN-OPEN-020's "bounded-degree theorem must remain a scoped negative".
N4 result: no notation-level novelty.

---------------------------------------------------------------------------------------------------

## Independent re-check of the region lemma (this gate; not a reproduction of the candidate's script)

Script: `qc/qc1_gate_recheck.py`, output `qc/qc1_gate_recheck.out` (python3 -I; seed 20261025). Model as stated by the candidate: B = N^beta,
pi = B^m/N, relations ~ B, LA ~ B^2, table build ~ B^mu, per-attempt cost B^tau; sub-rho iff max(rel, mu*beta, 2*beta) < 1/2 for some beta.
Analytic derivation (mine): find-one with m*beta < 1 needs beta > 1/(2(m-1-tau)) together with beta < min(1/m, 1/4, 1/(2mu)), giving
tau < min(m/2-1, m-3) and tau + mu < m-1; the m*beta >= 1 branch gives tau < m/2-1, mu < m/2, m > 4, which is contained in the first set. List-all with
LA < 1/2 forces beta < 1/4 and exponent 1 + beta(1+tau-m) < 1/2, i.e. tau < m-3.
Numerics: 4000 random (m in 2..9, tau, mu in [0,m]) points per semantics, grid over beta (40001 points): **0 disagreements** between grid and closed form for
both find-one and list-all. So the lemma is correct *as a statement about the stated cost model*. It rests on H1 (mean yield B^m/N, KN-FIND-007), H2 (LA = B^2,
omega = 2) and on relations = B; a smaller omega or a rank-lenient solve would change every boundary.
N-unit thresholds (per-attempt oracle cost N^d): list-all (m-3)/4 equals fa9839's d_max at every m; find-one is 1/2 - 1/m for m >= 4.
Generic-split check: QC1's (m-j, j) formula reproduces the program's recorded model column 2/3, 3/4, 3/5, 4/7 at (m, j) = (3,2), (4,2), (5,3), (7,4)
(0.6667, 0.7500, 0.6000, 0.5715). The program's README (`src/crypto_autoresearcher/index_calculus/README.md`, "model" column: 2/3, 3/4, 3/5; "4/7 at m = 7")
already carries these predictions, so "predictions match the fitted exponents" is not a new corollary. Caveat on this check: the j per m is read from the README's
table sizes (m = 5: 4.5e5 entries at |F| = 87 is about 87^3/1.5, so j = 3), not independently derived.

I did not verify the placement-table numbers (SDEG tau 3.99/3.24, G1 "A*L^5 = 1,041-8,438 x T", lattice reach 1/80 vs 1/6); they rest on records I did not open.

---------------------------------------------------------------------------------------------------

## Residual delta, and what I would do with it

* Verdict stays duplicate_of_lead. The correct filing is an annotation, not a lead: attach to `LEAD-ICE-generic-oracle-arity-cost-floor` (as evidence for its
  "arity threshold" forecloses phrase) the reconciliation of the program's two normalisations of the same threshold: binary `alpha < m/2 - 1` (find-one) and
  prime `d < (m-3)/4` (list-all, fa9839 / section 2.4) coincide at m = 4 and differ for m >= 5; the find-one prime windows are N^{0.30} (m = 5) and
  N^{0.333} (m = 6). Checkable in seconds from `qc/qc1_gate_recheck.py`. Nothing else in QC1 is an increment.
* Open question I could not close: whether EXP-ICEX-60c93c ("two-regime alpha(theta, m) table", draft) or EXP-ICEX-146ff5 already contain the pi < 1 / pi > 1 split.
  Paths: `/Volumes/SSD990-2/crypto-autoresearcher/experiments/EXP-ICEX-60c93c/specification.yaml`, `.../EXP-ICEX-146ff5/specification.yaml`. I stayed within the 3-record limit and did not
  open them. If they do, even the residual delta is a duplicate.
* The "external ingredient" (CGK, Shoup, SGGM, DKM) is already in the program (lit2026_w3 audit, IDEA-20261018-49fdf7, KN-LIT-013, KR-RHO-13bf67). Yao/DTT/3SUM-indexing
  is cited but not used in any derivation step I can see; nothing in the corpus grep (ledger index, atlas, research docs) mentions 3SUM-indexing or Golovnev et al.
  in an IC context, so connecting the m-SUM-with-advice bound B^{tau+mu} >~ B^m to the region would be a new (unproved here) step, not part of QC1 as written.
* Caveats: lexical greps over truncated index fields cannot prove absence; the ledger proposals directory was not scanned (only `.index` and three opened records).
