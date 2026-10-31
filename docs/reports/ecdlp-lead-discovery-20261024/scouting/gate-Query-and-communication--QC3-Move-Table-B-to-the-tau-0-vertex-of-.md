# Novelty gate N1-N4: QC3 "Move Table B to the tau = 0 vertex of the generic time-space frontier"

Candidate: full m-fold signed sumset table (x-keyed), one lookup per walked target, small B, m = 3-5, aimed at B3
(LEAD-ICP-prime-ic-constant-engineering). Gate run 2026-10-25. All numbers below that are not quoted from a file
are labelled "my arithmetic" or "prediction". No outcome of any experiment is reported; none was run.

## 0. Verdict (details and evidence below)

verdict = advances_lead (lead: LEAD-ICP-prime-ic-constant-engineering, open_next_step), with these load-bearing limits:

1. The mathematics is not new. Every ingredient is recorded in the program or the literature:
   - the exponent law j/(2j-1) for a j-fold table at the optimal base, and the growth r^{1/(2(2j-1))} of IC/rho
     (j = 3: r^{1/10}): crypto `research/ic_triple_table_20260923/PREREGISTRATION.md` (Koblitz, derived and measured);
   - the generic collision floor S_3 >= (1/2) sqrt(r N) for any x-key-collision engine in exactly QC3's
     (representation, operation set) frame: IDEA-20260928-ce3ab0, refined and audited as H-PFDR-cf8ca6 (analyzed);
   - the BSGS limit and its measured toy-prime constants: KR-RHO-cd0049, LEAD-RHO-bsgs-family-memory (closed_known);
   - the repo's own mitm model N^{max(h, m-h+1)/m} with measured 0.67 / 0.75 / 0.60 at m = 3 / 4 / 5.
2. What is not recorded anywhere I could find (the residual novelty, and it is only an untried parameter point):
   a prime-field recipe with table arity j = m >= 3 (no scan of R - F_i), the base sized at the j-table optimum
   (B* = 22-24 at fp24), priced in GAE under ecbench with the section 5a band. Evidence for "untried":
   - Rust `ic.pipeline` `MitmOracle` holds a `PairTable` only, `m` in {2, 3}: "a table of pair sums probed once per
     target (m = 2) or once per R - P (m = 3)" (crypto src/cryptanalysis/ic_framework/plugins.rs L33, L1833-1870);
   - the Python engine rejects the vertex: solver.py "table_arity must be in [1, m - 1]", default (m+1)//2
     (tails.py default_table_arity);
   - the one Rust arity benchmark is j = 2 at fixed B = 64: research/ecbench_rootfinding_arity_20261013/REPORT.md
     (m3/m2 = 1.431345, interval 1.224624-1.716117, a measurement of pair table + scan at B = 64);
   - the planner rule "m = 2 beats m = 3 and root finding by 4-60x in S" (planner.rs L480) and the planner study
     varies base size, oracle, stop rule and target mode, never arity (research/ic_planner_validation_20261020);
   - the exact-ECCp-131 "three-point" oracle is pair table + one subtraction, "without materializing cubic storage"
     (research/eccp131_bsgs_ic_20261020/reports/run-20261022T0523Z/REPORT.md).
3. Prior art the candidate does not cite and the atlas does not index: `research/ic_triple_table_20260923/` and
   `research/ic_triple_counted_20260923/` (crypto repo, Koblitz tournament harness, callgrind instruction counts).
   It is a v = 3 table + one scanned summand (so (m, j) = (4, 3)), measured triple/scaled 1.493 [1.411, 1.575] at n23a1,
   0.589 [0.535, 0.643] at n37a0, 0.409 [0.337, 0.494] at n43a1 (gain grows with r), and its follow-up records that
   "below rho" was measured against a non-matched rho (control: IC arm above rho at all five cells, 1.19x-2.88x).
   `grep` of knowledge/leads/ecdlp for "triple" / "ic_triple" returns nothing: this is an atlas coverage gap.
   QC3 is therefore a prime-field port of an already-measured lever, at the j = m vertex instead of j = m - 1.
4. It stays inside SO-TABLE and SO-GEN and does not answer either obstruction (the candidate says so). It must not be
   written up as crossing rho, as an exponent move, or as "choose B optimally to cross rho" (LEAD-ICP-generic-table-decomposition forecloses).

Why advances_lead and not duplicate_of_lead: the nearest same-mechanism lead, LEAD-ICP-generic-table-decomposition
(closed_obstructed), is closed on the exponent / crossing-rho question and its Scope clause is "any generic
(enumeration/table) decomposition over F_p"; QC3 claims neither. The open sibling LEAD-ICP-prime-ic-constant-engineering
states "Each verified gain is an improvement over the current IC baseline under the owner's success criterion even
though the exponent is fixed", its forecloses list (batched inversion, Montgomery arithmetic, NFS-style filtering,
blocked pair-table build, automatic planner) does not mention table arity, and its next_action (validation gate, then
two-level batching) has no arity arm. The binary sibling LEAD-ICB-generic-table-oracle says the same:
"constant-factor engineering of this pipeline remains valid baseline work". Why not new: see N2/N3/N4.
Why not known_result: no KR row states the prime-field Table B arity ladder in GAE; the KR rows cover the limit
(BSGS) and the frontier, not this parameter point. If the orchestrator scores the idea rather than the experiment,
the honest label is "known mathematics, unmeasured parameter point".

Required corrections before this goes to design-experiment (details in section 6):
(a) cite and reuse the Koblitz triple-table instrument and its rho-control lesson; (b) restate "CGK frontier" as a
heuristic: CGK's theorem is for free offline advice about a fixed group, QC3 charges the table inside S, so the
binding recorded bound is the collision floor of IDEA-20260928-ce3ab0 / H-PFDR-cf8ca6; (c) report ratios to matched
rho AND bsgs.negation AND the collision floor (1/2) sqrt(rho_rel B r); (d) the fp20-fp28 band is below the size where
the Koblitz triple table lost (n23a1: base floor of 2 orbits) so check the early-stop / rank floor at m >= 3 first.

Housekeeping disclosure: my first loop wrote `atlas_1..4.txt` and `frontier_1..4.txt` into the shared directory
`scout/raw/` (a concurrent/previous gate's scratch, 23:39-00:03 timestamps) and overwrote files of those names there.
Nothing outside scout/ was touched. My authoritative raw outputs are in `scout/_qc3tau0_raw/` and pasted below.

## 1. N1 Atlas collision

Env: LEAD_ATLAS_CRYPTO, LEAD_ATLAS_CRYPTANALYSIS, LEAD_ATLAS_ECC_CHALLENGES exported as instructed; run from /Volumes/SSD990-2/crypto-autoresearcher.
Runs 1-3 are the three match_phrasings; run 4 is my own phrasing.

```
=== python3 tools/lead_atlas.py --match "prime-field index calculus with a full triple-sum table and walked targets at the generic time-space vertex"
   15  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   15  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   12  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
   12  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
   11  LEAD-ICB-multi-target-and-portfolio          closed_obstructed  Batch IC and IC/rho portfolios: amortising the set-up over many targets, restart portfolios
   11  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
   10  LEAD-ICP-extension-field-embedding           closed_obstructed  Embedding E(F_p) into E(F_{p^n}) to buy a subfield factor base
```

```
=== python3 tools/lead_atlas.py --match "use a table of all triple sums of factor-base points instead of pair sums to cut prime index calculus cost"
   20  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
   17  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   16  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
   15  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   13  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   12  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
   12  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
   12  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases
```

```
=== python3 tools/lead_atlas.py --match "meet-in-the-middle table decomposition at higher arity as a generic time/memory trade-off for the prime ladder"
   28  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7)
   21  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
   16  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
   15  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
   14  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   10  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
   10  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases
    9  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
```

```
=== python3 tools/lead_atlas.py --match "one-target prime-field index calculus with unknown-log factor base, signed m-fold sumset table and one lookup per walked target (baby-step giant-step with unknown baby logs)"
   29  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
   19  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   19  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
   17  LEAD-ICP-extension-field-embedding           closed_obstructed  Embedding E(F_p) into E(F_{p^n}) to buy a subfield factor base
   17  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   16  LEAD-EXO-split-jacobian-projection           closed_obstructed  Split-Jacobian projected smoothness and the pair (P,Q) as a genus-2 divisor
   16  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   16  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
```

### 1.1 Reading of the top 5 of every run (lead YAML opened: mechanism + obstruction + forecloses)

| run | rank | hit | disposition | same mechanism as QC3? |
|---|---|---|---|---|
| 1 | 1 | KR-IC-5931ee | known_result | literature row: naive Semaev IC over F_p no better than generic. Context, not a mechanism. |
| 1 | 2 | LEAD-ICP-retained-setup-online | closed_dominated | No. Many-target retained advice vs rho with an empty DP table; BL preprocessing rho wins. QC3 is one target, set-up charged. Its remark "orbit-folded m = 2 Koblitz IC is BSGS on the quotient and sits on the BL r/P law" is the m = 2 case of QC3's own limit statement. |
| 1 | 3 | KR-IC-a4dd54 | known_result | No (genus threshold). |
| 1 | 4 | LEAD-ICE-generic-oracle-arity-cost-floor | closed_obstructed | Partly: arity floor for ENUM/MITM/FREE oracles. Measured domain is binary curves of prime degree; "free oracle at m = 3 on ECC2K-130: 2^68.58 vs rho 2^60.81". Does not cover a prime-field toy-size constant. |
| 1 | 5 | LEAD-ICP-prime-ic-constant-engineering | open_next_step | The home lead (B3). Its forecloses do not include table arity. |
| 2 | 1 | LEAD-RHO-correlated-walks-shared-sums | closed_obstructed | No. Lexical collision on "pair table R_i + R_j steps": that lead shares sums across rho walks. QC3's sums are factor-base sums used as a lookup key and the target walk is one addition per trial (cost 1.096 GAE), not a shared-step scheme. Its obstruction (shared index sequence makes P_i - P_j invariant) does not apply because QC3 targets are not required to collide with each other. |
| 2 | 2 | KR-IC-5931ee | known_result | context |
| 2 | 3 | LEAD-ICP-prime-ic-constant-engineering | open_next_step | home lead |
| 2 | 4 | KR-IC-a4dd54 | known_result | no |
| 2 | 5 | LEAD-STR-class-representative-ic-selection | open_next_step | No. Choice of isogenous curve / isomorphic model; orthogonal and composable. |
| 3 | 1 | LEAD-ICP-generic-table-decomposition | closed_obstructed | YES, same mechanism family (below). |
| 3 | 2 | LEAD-ICB-generic-table-oracle | closed_obstructed | Same family on Koblitz (pair tables, compact-orbit 4-sum, MITM). |
| 3 | 3 | LEAD-ICE-generic-oracle-arity-cost-floor | closed_obstructed | as above |
| 3 | 4 | KR-RHO-cd0049 | known_result | The BSGS limit of QC3's family, measured. |
| 3 | 5 | LEAD-ICE-rootfind-pairtable-oracle | open_blocked | Same oracle family at m = 2 / 3 ("m = 3 is |F| lookups"): the j = 2 scan. Its next_action prices natives; no arity-j = m arm. |
| 4 | 1 | LEAD-ICP-retained-setup-online | closed_dominated | see run 1 |
| 4 | 2 | KR-IC-5931ee | known_result | context |
| 4 | 3 | LEAD-ICP-algebraic-membership-factor-base | closed_obstructed | No. QC3's base is an interval/random enumerated base; SO-ALGFB is not touched. |
| 4 | 4 | LEAD-ICP-extension-field-embedding | closed_obstructed | No. |
| 4 | 5 | LEAD-STR-class-representative-ic-selection | open_next_step | No. |

Also opened for context: LEAD-RHO-bsgs-family-memory (closed_known), LEAD-ICB-multi-target-and-portfolio, LEAD-ICP-full-width-arity-grid
(open_blocked, Python-engine arity m = 2..8 at 50-63 bits, default table arity, blocked on resources), LEAD-ICP-residual-partial-relations
(open_next_step, sibling B3 arm: large-prime residuals on the m = 2 engine), LEAD-ICP-coincidence-harvest-structured-base, LEAD-ICE-charged-toy-ic-exponent-vs-rho (B1, open_blocked).

### 1.2 Obstruction statements the candidate must stay inside (verbatim from the lead rows)

LEAD-ICP-generic-table-decomposition (closed_obstructed, theorem), mechanism: "Over F_p the roots of S_3/S_4 are exactly x(R -/+ F_i) matched against x(F_j +/- F_k), so the point-decomposition problem becomes a batched subtraction plus a table lookup (folded, walked targets; mitm tables of h-fold signed sums). With a factor base of size B and arity m this trades B^{m-1} advice for (m!/2^m) p / B^{m-1} work per relation, and was the hope for moving the Table B prime ladder toward rho."
obstruction.statement: "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). Measured on generated prime-order E/F_p, 12-32 bits: exhaustive IC exponent 0.99 (m = 2) and 1.01 (m = 3), mitm 0.67 / 0.75 / 0.60 at m = 3/4/5 (4/7 at m = 7) against rho 0.50 [0.48, 0.52]; Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4. Scope: any generic (enumeration/table) decomposition over F_p."
forecloses: "pair-table meet-in-the-middle decomposition beats rho at higher arity; faster S_3 root finding or batched subtraction makes prime IC sub-rho; choose the factor-base size B optimally to cross rho; free decomposition oracle at m = 2 or m = 3; generic collision floor for x-key relations".
revisit_when: "A non-generic decomposition oracle exists with per-attempt cost T_dec << p^{1/4} at arity m = 4 (an S_5 oracle at B ~ p^{1/5}), or a decomposition test sub-linear in |F|."

LEAD-ICB-generic-table-oracle (closed_obstructed, theorem), Scope: "all binary and Koblitz curves, one target, setup charged." revisit_when includes: "constant-factor engineering of this pipeline remains valid baseline work (LEAD-ICB-koblitz-setup-phase-cost)."

LEAD-ICE-generic-oracle-arity-cost-floor (closed_obstructed, cost_model), Scope: "oracles that do not read curve coordinates algebraically; the FREE control does have sub-VOW cells, so the obstruction is the oracle class, not IC."

LEAD-RHO-bsgs-family-memory (closed_known, cost_model): "bsgs.negation is the prime-toy ops leader at 1.100 [0.978, 1.225] x sqrt(pi/4) but needs 0.50 sqrt(r) table entries (rho 0.034); at log2 r = 256 that is 2^127 entries, so rho with DPs dominates at every cryptographic size (KR-RHO-7d93f6)." revisit_when: "A BSGS-type schedule with o(sqrt r) memory and BSGS-level operations".

LEAD-ICP-prime-ic-constant-engineering (open_next_step): mechanism "Each verified gain is an improvement over the current IC baseline under the owner's success criterion even though the exponent is fixed." next_action: "Put the eight Table B prime rows through the validation gate ..., then run the unimplemented two-level target batching ... as a paired ecbench arm against the current folded/walked m = 2 recipe at fp20-fp28." forecloses: batched inversion, Montgomery native arithmetic for the relation search, NFS-style relation filtering, blocked cache-aware pair table construction, automatic recipe planner.

### 1.3 What QC3 does that the foreclosure phrases do not cover

(i) Every phrase in LEAD-ICP-generic-table-decomposition.forecloses is about crossing rho or removing the exponent gap; QC3 asserts neither and states the gap still grows (N^{1/(2(2m-1))}).
(ii) The lead's measured mitm ladder used the engine's default table arity h = (m+1)//2 at |F| near the default size (README section 3), i.e. (m, j) = (3, 2), (4, 2), (5, 3). QC3 changes two things at once: j = m (no scan) and the base sized to the j-table optimum. Neither is a forecloses phrase. But the closed lead's own mechanism text covers "mitm tables of h-fold signed sums ... walked targets", so the mechanism family is the same. This is the reason the verdict is advances_lead (a new arm under the open constant-engineering lead) and not new.
(iii) A semantic match with a closed lead whose obstruction the candidate does not answer is a duplicate only if the candidate claims what the obstruction forecloses. QC3 disclaims it. If the write-up ever drifts to "pair-table / k-sum table beats rho at higher arity" or "optimal B crosses rho", the verdict flips to duplicate_of_lead (LEAD-ICP-generic-table-decomposition).

## 2. N2 Known results (tools/build_frontier_map.py --match, same four phrasings)

```
=== python3 tools/build_frontier_map.py --match "prime-field index calculus with a full triple-sum table and walked targets at the generic time-space vertex"
KR-IC-5931ee  score=15  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-a4dd54  score=12  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-9e610d  score=9  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-ae532f  score=9  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-RHO-cd0049  score=9  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-IC-46d822  score=8  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-RHO-38be82  score=7  [known_mechanism/reported]  Tag tracing and table-driven step shortcuts
    sources: KN-LIT-93696f, KN-LIT-20ef89
KR-RHO-ea34b8  score=7  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
```

```
=== python3 tools/build_frontier_map.py --match "use a table of all triple sums of factor-base points instead of pair sums to cut prime index calculus cost"
KR-IC-5931ee  score=17  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-a4dd54  score=15  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-RHO-cd0049  score=12  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-IC-9e610d  score=11  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-46d822  score=8  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-ae532f  score=8  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-IC-64659b  score=7  [known_bound/proven]  Diem: rigorous subexponential ECDLP for suitable n
    sources: KN-LIT-003, KN-LIT-65f76d
KR-IC-1fcdbc  score=6  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
```

```
=== python3 tools/build_frontier_map.py --match "meet-in-the-middle table decomposition at higher arity as a generic time/memory trade-off for the prime ladder"
KR-RHO-cd0049  score=15  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-IC-5931ee  score=8  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-a4dd54  score=7  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
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
```

```
=== python3 tools/build_frontier_map.py --match "one-target prime-field index calculus with unknown-log factor base, signed m-fold sumset table and one lookup per walked target (baby-step giant-step with unknown baby logs)"
KR-IC-5931ee  score=19  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-b0fcda  score=15  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-RHO-cd0049  score=14  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-IC-a4dd54  score=12  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-9e610d  score=9  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-ae532f  score=9  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-IC-46d822  score=8  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-49c882  score=8  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
```

### 2.1 Reading

| KR row | content (from KRMAP.md) | relation to QC3 |
|---|---|---|
| KR-IC-5931ee (known_negative/proven) | Naive Semaev IC over F_p cannot beat generic methods (Yokoyama-Yasuda-Takahashi-Kogure; PKM, APS, Kudo algebraic bases work only at small parameters) | QC3 is a naive-Semaev-type recipe, inside it. Context, not a collision. |
| KR-RHO-cd0049 (known_bound/measured) | negation BSGS at 1.160 [1.068, 1.248] x the generic floor, 0.5015 sqrt(r) table entries, 96 verified runs; vs rho 0.8250 [0.725, 0.945] of the walk's ops for 15.79x the table | QC3's m -> infinity limit ("BSGS with unknown-log baby steps, about 1.48 sqrt(rho_rel B r)") is a variant of this measured row; "BSGS beats rho on ops at toy sizes" is a KR row, not a QC3 finding. |
| KR-RHO-ea34b8 / KN-LIT-013 (known_bound/proven) | CGK S T^2 = Omega~(eps N); Bernstein-Lange l^{1/3} online after l^{2/3} tables meets it | The "frontier" in QC3's title. See 2.2 for why it is a heuristic here. |
| KR-RHO-7d93f6, KR-RHO-13bf67 | Dinur T^2 S = Theta~(C^2 N); Shoup Omega(sqrt N) | SO-GEN. |
| KR-IC-9e610d, KR-IC-ae532f | survey consensus; records | context |

No KR row states the prime Table B arity ladder in GAE or the j = m vertex. A KR hit therefore does not by itself make the candidate
a known_result; what is known is the family limit, the frontier and the exponent law. What is exactly new, stated narrowly:
a prime-field (m, j) = (m, m), m in {3, 4, 5}, B = the j-table optimum, arm in ic.pipeline units (GAE, section 5a band), paired against the incumbent
folded/walked m = 2 recipe. Everything else is recorded.

### 2.2 Citation check (load-bearing: Corrigan-Gibbs and Kogan)

- Retrieved this session: https://eprint.iacr.org/2017/1113 (WebFetch). Title "The Discrete-Logarithm Problem with Preprocessing", authors Henry Corrigan-Gibbs and Dmitry Kogan; the page states it is "a major revision of an IACR publication in EUROCRYPT 2018"; abstract states the generic-group bound ST^2 = Omega~(eps N) for S bits of advice, online time T, success probability eps, prime group order N, tight up to log factors. Provenance: retrieved.
- Applicability caveat (my reading, not a retrieved statement): the theorem is for advice about a fixed group (offline phase free), online time per instance. QC3 charges the table build inside S for a single instance, so CGK is not the binding bound for QC3's accounting; the binding generic bounds in that accounting are Shoup (T >~ sqrt N) and the program's own collision-counting floor S_3 >= (1/2) sqrt(r N) (IDEA-20260928-ce3ab0, derivation tier, "unreviewed"; refined as H-PFDR-cf8ca6, status analyzed, "never supported on current evidence"). Calling j = m "the tau = 0 vertex of the CGK frontier" is QC1 notation; the recorded objects are the two-term model (H-PFDR-064546) and the collision floor.
- Recalled (not re-retrieved): Shoup 1997 Omega(sqrt N) and Kuhn-Struik / Yun batch bound, as carried in KN-LIT-011, KR-RHO-46c2c6; BSGS as a textbook algorithm.

## 3. N3 Ledger dedup (grep of ledger/.index/{proposals,hypotheses}.jsonl only)

Index rows carry truncated title/claim/mechanism/statement; a lexical miss proves nothing. Scripts: scout/_qc3tau0_raw/ledger_grep.py, ledger_extra.py (raw output below).

### 3.1 Raw grep output, term set 1 (ALL-of patterns)
```

### triple-sum table: patterns=['triple|three-sum|3-sum|three-point|cubic', 'table|storage|lookup'] ALL
-- proposals: 10 hits
  IDEA-20260726-012  [|unverified]  Let k have characteristic different from 2, let F=k(t), and prescribe p_empty=1 and p_S=(t+1)/(t+d_S
  IDEA-20260816-a96623  [|proposed]  (A) Every downstream claim this campaign can make about the rotation-constant space rests on a weigh
  IDEA-20260816-d202cf  [|proposed]  (A) The obstruction predicate of IDEA-20260726-012 is defined relative to a CHOICE: H-PMA-001 freeze
  IDEA-20260829-172151  [|proposed]  (A) THE OBJECT. A census cell is a triple (curve family, instrument, scale) carrying a VERDICT. The 
  IDEA-20260829-bb55d5  [|proposed]  (A) THE OBSTRUCTION AS STATED, AND THE HIDDEN PREMISE IN IT. IDEA-20260805-3c957e is this lane's str
  IDEA-20260829-cb4fd5  [|proposed]  (A) THE FEASIBILITY TABLE IS ARITHMETIC AND IT IS AVAILABLE NOW. The Macaulay column count at degree
  IDEA-20260829-ecd69d  [|proposed]  (A) THE ARCHIVED NUMBER NOBODY DERIVED. EV-MLKEM-005 observation 6 records that the Algorithm-18 int
  IDEA-20260904-7582ba  [|proposed]  (A) THE CENSUS QUESTION, POSED PRECISELY. IDEA-20260904-982159 exhibits an ECDLP resource that this 
  IDEA-20261003-849551  [|proposed]  A Jacobian point stores 3 field elements. An affine point stores 2. Three exceeds two by 1, and the 
  IDEA-20261007-469116  [|proposed]  On E: y^2 = x^3 + 2x + 3 over F_23, let B be the first 9 affine points of E(F_{23^3}) in lexicograph
-- hypotheses: 4 hits
  H-BINSTD-9bde6e  [BINSTD|approved]  SETTING. Standardized binary ECDLP population of RQ-BINSTD-b6f698. Comparator: matched van Oorschot-
  H-ECDLP-752c8c  [ECDLP|proposed]  Source proposal IDEA-20260829-cb4fd5 (RQ-SBRG-f31cb2, class tooling). (A) THE FEASIBILITY TABLE IS A
  H-ECDLP-9d5e78  [ECDLP|analyzed]  In the exact m=3, two-way split, x-coordinate MITM implementation frozen by EXP-SEMAEV-f48dd1, Arm B
  H-SIG-e7ff26  [SIG|proposed]  For the boolean chained Semaev system (m = 3, t = 3, 2n variables, n quadratics and n cubics) at any

### table arity: patterns=['table[_ -]?arity|tail arity|arity of the (pair|table)|h-fold|h = ?\\(m\\+1\\)'] ALL
-- proposals: 0 hits
-- hypotheses: 1 hits
  H-PFDR-2765d2  [PFDR|specified]  On prime-order ordinary curves E/F_p with log2 p in 20..32, generated by generate_prime_order_curve(

### full sumset one lookup: patterns=['sumset|full m-fold|m-fold sum|all .{0,20}-fold|signed sums of'] ALL
-- proposals: 10 hits
  IDEA-20260731-012  [|adaptation]  Let E/F_p carry a prime-order subgroup G of order N, let F be a factor base of size B = N^beta, and 
  IDEA-20260829-390ccc  [|proposed]  CONDITIONAL THEOREM CANDIDATE, stated for falsification. Let G = <P> have prime order N, let D subse
  IDEA-20260830-c5c614  [|proposed]  (A) WHAT IS ALREADY CLOSED, SO THAT THIS IS NOT MISTAKEN FOR IT. KN-FIND-007 fixes the mean per-targ
  IDEA-20260905-5a1ea2  [|proposed]  (A) THE OBJECT. For a factor base F of size m inside a prime-order subgroup G of E(F_p), let H_F(x) 
  IDEA-20260930-14c753  [|proposed]  Representation class R1 of RQ-ECDLP-623a32 (x-coordinate). The attack stage is relation collection's
  IDEA-20260930-4ebd85  [|proposed]  For a frozen explicit point set B of size m on the prime-order subgroup of a toy binary Koblitz curv
  IDEA-20261002-cad44c  [|proposed]  Any Couveignes factor base built from F_2-rational points of a commutative algebraic group of dimens
  IDEA-20261006-5bfbcf  [|proposed]  Representation R1, attack stage relation yield. On E: y^2 = x^3 + x + 4 over F_61, let F be the four
  IDEA-20261009-0bb2cf  [|proposed]  On every available curve with certified generators (rank 5-29 from the literature plus the rank-30/3
  IDEA-20261018-5fa71b  [|proposed]  BRIDGE. c(R) = h-sum count vector of a base, mu its mean, Delta = Var/mu. (I1) PFDR kappa_h (IDEA-20
-- hypotheses: 10 hits
  H-CERTBIN-0c5608  [CERTBIN|approved]  The written counts are 6154284 and 20708500. The written ceiling mantissas are 254535220 and 8564834
  H-CERTBIN-a916e0  [CERTBIN|approved]  Representation class R1 (x-coordinate). Let p <= min(1, C(B+m-1, m)/r). For L independent uniform ta
  H-ECDLP-3165ff  [ECDLP|proposed]  SCOPE: EXPLICIT reusable precomputations for the target-independent part of a chained point-decompos
  H-ECDLP-8a1942  [ECDLP|proposed]  The solving degree d_solve of a decomposition system is defined by the degree at which the Macaulay 
  H-FROB-24c252  [FROB|approved]  6725 is 58811 below 65536. 39201 is 26335 below 65536. The cube of 6725 is 304142328125, which is 28
  H-FROB-66d9ae  [FROB|approved]  CLAIM (structural certificate / column pricing; NO ATTACK). Setting: any Couveignes factor base F wh
  H-ICEX-c273c2  [ICEX|proposed]  THE DECOMPOSITION PROBABILITY IS NOT A PROBABILITY TO BE ESTIMATED. For a factor base V of size B, i
  H-LHW-e54b1b  [LHW|approved]  CLAIM (heuristic_validation / integer sumset instrument; NO ATTACK; NO EXPONENT MOVE). Let W = W(m,w
  H-PFDR-1b2386  [PFDR|proposed]  (A) WHAT IS ALREADY CLOSED, SO THIS IS NOT MISTAKEN FOR IT. The mean per-target decomposition yield 
  H-PFDR-2765d2  [PFDR|specified]  On prime-order ordinary curves E/F_p with log2 p in 20..32, generated by generate_prime_order_curve(

### time-space / CGK: patterns=['corrigan|s\\*t\\^?2|s ?t\\^2|time-space|time/memory|time–memory|time-memory'] ALL
-- proposals: 11 hits
  IDEA-20260808-06aae4  [|proposed]  Demirci-Selcuk meet-in-the-middle attacks buy time with a precomputed table of delta-set multisets w
  IDEA-20260828-411711  [|proposed]  IDEA-20260805-cdc87d derives a closed-form, calibration-free crossover formula for the classical enu
  IDEA-20260901-949d55  [|proposed]  FIVE SEPARABLE CLAIMS. (A) THE OBJECT. The birthday phase of a chosen-prefix collision does not seek
  IDEA-20260904-d84512  [|unverified]  (A) THE EXACT CLAIM. Fix E/F_p with G = <P> of prime order N = Theta(p). For a set V of x-coordinate
  IDEA-20260906-44daf9  [|proposed]  For a specified synthetic nonce-leakage channel, a hybrid solver can improve the time-memory-sample 
  IDEA-20260906-e5e51c  [|proposed]  (A) THE ASYMMETRY, STATED PRECISELY. Consider a population of N distinct FIPS 203 ML-KEM-1024 public
  IDEA-20260920-a92b0f  [|proposed]  (A) THE MODEL DISTINCTION THE NOTE DOES NOT DRAW, AND IT IS THE WHOLE ANSWER. Open statement S1 asks
  IDEA-20260923-9e4b71  [|proposed]  (A) THE MODEL SHIFT. RQ-ECDLP-78dbc5 asks for fewer stored entries at fixed online cost in a charged
  IDEA-20260930-39ad61  [|proposed]  CEILING FIRST. No per-target exponent moves. The per-target online cost of the one-table-per-class a
  IDEA-20261018-49fdf7  [ICPERF|proposed]  Every recorded pair-table, k-sum and 6-sum design at ECC2K-130 and every n=85,89 rung is a non-adapt
  IDEA-20261018-4c28fc  [ICPERF|proposed]  Preprocessing rho at equal or smaller advice is faster online than compact-orbit IC at n=73 and n=83
-- hypotheses: 7 hits
  H-ECDLP-77caa5  [ECDLP|specified]  Fix E/F_p with G = <P> of prime order N. For a set V of x-coordinates with |V| = D, let Tab_V be the
  H-ECDLP-9a1388  [ECDLP|specified]  Fix the integer pair (n, M) = (16, 4) before any cost is evaluated. Stage 0 asserts only the charged
  H-FROB-cd38a5  [FROB|approved]  TEST BOUNDARY. One isogeny class of abelian surfaces over F_2. The Frobenius polynomial is P(T) = T^
  H-ICEX-a91960  [ICEX|proposed]  (A) THE MODEL, AS THE CORPUS CARRIES IT. KN-LIT-013 (Corrigan-Gibbs and Kogan, filed) records that a
  H-MLKEM-6111bf  [MLKEM|specified]  Fix the exact count identity of IDEA-20260828-411711 before any later-stage claim. Stage 0 asserts o
  H-SCURVE-d83a28  [SCURVE|specified]  Fix the exact 2-adic identity of IDEA-20260829-96bd39 before any ascending 2-isogeny is walked. Stag
  H-SSI-8ff06b  [SSI|proposed]  SCOPE: classical costs only; the one published time-memory curve of the 2026 p^{1/3+o(1)} supersingu

### bsgs + index calculus: patterns=['bsgs|baby-step|baby step', 'index calculus|\\bic\\b|factor base|factor-base'] ALL
-- proposals: 2 hits
  IDEA-20261015-29fdc8  [|proposed]  (A) On pair 46, w acts on G as lambda = 2/v mod N (v*w = pi+1, pi = 1 on G). The x-map R of w permut
  IDEA-20261015-7a3c9e  [|proposed]  For the repository's folded pair-state index calculus (a table of #states folded pair sums of base r
-- hypotheses: 0 hits

### walked targets: patterns=['walk(ed)?\\b.{0,40}target|target.{0,40}walk', 'table|lookup|pair'] ALL
-- proposals: 2 hits
  IDEA-20260906-a3d6ae  [|proposed]  (A) SETTING (U > 1, one table, one group). Targets Q_1..Q_U are processed sequentially (or in rounds
  IDEA-20261015-7a3c9e  [|proposed]  For the repository's folded pair-state index calculus (a table of #states folded pair sums of base r
-- hypotheses: 1 hits
  H-ECDLP-32fad8  [ECDLP|specified]  (A) SETTING (U > 1, one table, one group). Targets Q_1..Q_U are processed sequentially; target u run

### arity planner: patterns=['planner|arity', 'table b|prime|mitm'] ALL
-- proposals: 35 hits
  IDEA-20260726-003  [|unverified]  For toy prime-field curves with a frozen factor base and decomposition arity m, the Semaev fiber S_{
  IDEA-20260727-003  [|known]  For prime-field Semaev index calculus with factor base size B = N^beta and decomposition arity m, th
  IDEA-20260727-006  [|adaptation]  For prime-field Semaev index calculus with an interval (or any Fourier-accessible) factor base F = {
  IDEA-20260727-007  [|known]  Granting the yield heuristic, prime-field Semaev index calculus at arity m = 5 with factor base B = 
  IDEA-20260731-007  [|unverified]  For prime-field Semaev index calculus at arity m>=4 with factor-base size B=N^beta, the decompositio
  IDEA-20260731-012  [|adaptation]  Let E/F_p carry a prime-order subgroup G of order N, let F be a factor base of size B = N^beta, and 
  IDEA-20260802-003  [|unverified]  TWO CLAIMS, ONE NEGATIVE AND ONE MEASURED, AND THEY ARE STATED SEPARATELY BECAUSE THEY HAVE DIFFEREN
  IDEA-20260807-32f96d  [|proposed]  FINDING-PF-IC-001's cost model is total ~ ell^{(1+gamma)/m}, DECREASING in m, and dismisses large m 
  IDEA-20260807-569c82  [|proposed]  (A) THE ORACLE. PAIR(h_1, h_2) returns the pairing value of two handles from G, in mu_N inside F_{p^
  IDEA-20260807-e57607  [|proposed]  (A) WHY THIS IS THE ONLY EXPONENT-RELEVANT QUESTION IN L4, DERIVED. For prime-field point decomposit
  IDEA-20260808-093497  [|proposed]  (A) THE OBJECT. Fix E/F_p, a target R with x-coordinate x_R, an arity m >= 2, and a factor base V su
  IDEA-20260808-812554  [|proposed]  Write T_solve = B^{(m-1)sigma} for the cost of finding all m-decompositions of one target over a siz
  IDEA-20260813-a46301  [|unverified]  For an HQC instance with quasi-cyclic parity-check structure over R = F_2[X]/(X^n - 1) (n prime), a 
  IDEA-20260815-416f41  [|proposed]  DEC-20260810-2f86db rejects the generic-fibre Frobenius cycle-type census as a probe of relation rat
  IDEA-20260816-c9565d  [|proposed]  (A) THE PROBLEM. This program has recorded coverage excesses for structured factor bases of 1.0012, 
  IDEA-20260829-267a06  [|proposed]  Grover-Prange against quasi-cyclic syndrome decoding spends essentially all of its per-iteration cos
  IDEA-20260829-c705b4  [|proposed]  THE OBSERVATION FIRST, BECAUSE IT IS A FACT ABOUT COMMITTED RECORDS AND NOT A HYPOTHESIS. Every unco
  IDEA-20260830-f2e5b7  [|proposed]  (A) THE OMITTED CHANNEL, STATED AS A SPECIFIC DEFECT IN A LIVE PROPOSAL. At arity m = 2 over a prime
  IDEA-20260901-f375a9  [|proposed]  Four statements. P1 and P2 are derivations, C is the collapse they force, and M is the measurement. 
  IDEA-20260902-2327a5  [|proposed]  Setting: E/F_p ordinary, p > 3, G a subgroup of prime order N, factor base V a set of B on-curve x-c
  IDEA-20260902-a0ed78  [|proposed]  Setting: E/F_p ordinary, G = E(F_p) of prime order N (or the prime-order subgroup; nothing below dep
  IDEA-20260903-cf63ad  [|proposed]  Setting. E/F_p short Weierstrass y^2 = f(x), p > 3, arity m = 3, chained t = 3 tree as in GOAL-DREG-
  IDEA-20260905-24d827  [|proposed]  SCOPE: ordinary prime-field short-Weierstrass curves, p in 2^12..2^32, decomposition arity m in {2,3
  IDEA-20260905-df55e9  [|proposed]  A certificate that binds the polynomial presentation, named degree invariant, admissible parameter d
  IDEA-20260906-1f6bfe  [|proposed]  (A) THE QUESTION THIS INSTRUMENT DECIDES. For the decomposition-count vector c_D(r) of a size-B base
  IDEA-20260906-6da433  [|proposed]  SETTING as in IDEA-20260906-a77711 (E/F_q, n odd prime, G of prime order N not in a proper subfield,
  IDEA-20260906-b26c06  [|proposed]  SETTING. E/F_p short Weierstrass of prime order N, factor base D of B x-classes (point set W = D and
  IDEA-20260922-faa8d2  [|proposed]  SCOPE: symmetrized descended pdp over F_{2^n}, n prime, factor base a subspace V of dimension l; ari
  IDEA-20260926-1db0e8  [|proposed]  SEAM AND WHY THIS IS NOT IDEA-20260922-c2bbe6. HOLD-Q returned c2bbe6 (the elliptic single-large-pri
  IDEA-20260926-80209d  [|proposed]  CEILING FIRST. A control fixture for RQ-BINSTD-b6f698's table (owner by the R2 rule); no arity, no o
  IDEA-20261007-560bcb  [SSI|proposed]  Suppose TrapCurveGen outputs a supersingular curve E, a complete evaluable witness W for End(E), a p
  IDEA-20261010-066c44  [|proposed]  Conditional, exponent-relevant. At prime n<=13, enumeration-certified UNSAT chained-S_3 systems (t=m
  IDEA-20261016-6ad2a5  [|proposed]  Depends on IDEA-20261016-bf8f49 (S2 and its same-sign analogue). Take an arm with lifts having B not
  IDEA-20261016-b428b9  [|proposed]  For each accepted lift E=(A,B) with its two points compute r_lb (points plus any found), r_ub = dim 
  IDEA-20261018-9fc21f  [|proposed]  BRIDGE of H-SEMBIN-83a856 (supported), IDEA-20261017-3db2a8, EXP-PFDR-ca5e01, EV-RELN-335cd2, IDEA-2
-- hypotheses: 29 hits
  H-BINSTD-4c31d1  [BINSTD|analyzed]  SETTING. Binary curves E_{a,b}: y^2+xy=x^3+a x^2+b over one fixed F_{2^n} (n prime, 17<=n<=41) with 
  H-BINSTD-daf992  [BINSTD|approved]  SETTING. Binary curves E_{a,b}: y^2+xy=x^3+a x^2+b over one fixed F_{2^n} (n prime, 17<=n<=41) with 
  H-DS-001  [DS|analyzed]  For prime-field Semaev index calculus at arity m in {4,5} with factor-base size B in {64,128,256} on
  H-DTREE-001  [DTREE|inconclusive]  For toy prime-field curves at 16, 20, and 24 bits with standard factor base B = ceil(sqrt(N)) and ar
  H-ECDLP-15d016  [ECDLP|specified]  Fix the one-step next-feature split of a parity feature on a prime-order additive group before any p
  H-ECDLP-29f047  [ECDLP|proposed]  SCOPE: the frozen toy Semaev point-decomposition systems already used in this program's DREG lane, a
  H-ECDLP-60de36  [ECDLP|rejected_scoped]  For prime p = 3 mod 4 with 2^L | p+1 and target curve y^2 = x^3 - 3x + b, encoding the factor-base x
  H-ECDLP-84ca6a  [ECDLP|proposed]  Source proposal IDEA-20260808-b3c97b (RQ-INSTR-f8faa0, class tooling). SCOPE: this program's own evi
  H-ECDLP-a6d66b  [ECDLP|proposed]  FIELD CORRECTION, RECORDED FIRST BECAUSE IT CHANGES WHAT THIS RECORD IS. The dispatching handoff TAS
  H-ECDLP-b657e1  [ECDLP|specified]  Fix the closed-form representation-multiplicity identities of IDEA-20260806-20f6ab before any factor
  H-EQD-001  [EQD|analyzed]  THE CLAIM IS STATED AT LIMB L2 EXACTLY AS experiments/EXP-EQD-001/specification.yaml DEFINES IT, AND
  H-EQIC-70a21a  [EQIC|proposed]  SCOPE. Prime fields F_p with p = 1 mod 3 at field_bits in {12, 16, 20}; curves E/F_p with j = 0, i.e
  H-FIB-001  [FIB|approved]  For toy prime-field curves at 16 and 20 bits with frozen factor base B = ceil(sqrt(N)) and decomposi
  H-ICEX-87ad66  [ICEX|proposed]  SCOPE FIELD. Prime-field ECDLP by Semaev point-decomposition index calculus over E/F_p with a prime-
  H-ICEX-9e54c2  [ICEX|specified]  FOR EVERY FIXED ARITY m >= 2, EVERY LINEAR-ALGEBRA EXPONENT omega IN THE DECLARED RANGE, AND EVERY F
  H-ICEX-fe2944  [ICEX|proposed]  In the index-calculus pipeline as this program actually implements it, at summation arity m in {2, 3
  H-MTBK-001  [MTBK|proposed]  For toy prime-field curves with factor base F of size B ~ p^b (b in {0.4, 0.5, 0.6}) and Semaev deco
  H-MTIC-001  [MTIC|approved]  For toy prime-field curves at 16, 20, and 24 bits with factor base B = ceil(sqrt(N)) and decompositi
  H-PFDR-064546  [PFDR|proposed]  (A) THE ACCOUNTING. Let G have prime order N, the factor base have size B, D be the cost in group op
  H-PFDR-0cc7e8  [PFDR|specified]  On the committed mitm rows of the crypto_autoresearcher.index_calculus engine (results/sweep-minfill
  H-PFDR-9aadc0  [PFDR|specified]  SETTING. E/F_p short Weierstrass, p > 3, arity m = 3, chained t = 3 tree over F_p with no Weil desce
  H-PFDR-cb9606  [PFDR|proposed]  (A) THE OMITTED CHANNEL, AS A SPECIFIC DEFECT IN A SIBLING RECORD OF THIS BATCH. At arity m = 2 over
  H-PFDR-cf8ca6  [PFDR|analyzed]  On the crypto_autoresearcher.index_calculus mitm engine, prime-order ordinary curves E/F_p with log2
  H-RELN-10ad6b  [RELN|proposed]  For prime-order short-Weierstrass curves E/F_p with the negation-closed x-interval factor base of no
  H-RELN-41562a  [RELN|proposed]  On prime-order short-Weierstrass curves E/F_p with N = #E(F_p) prime and near 2^14, 2^16, 2^18 and 2
  H-RELN-dee9ec  [RELN|specified]  On the complete frozen9-rung prime-order ordinary-curve panel with m=3, two auxiliary cardinality se
  H-SEMBIN-2d7708  [SEMBIN|specified]  Semaev's Assumption 1 (d_F4 <= 4 for the chained-S_3 Boolean system, for every 2 <= t <= m) is FALSE
  H-SMTH-001  [SMTH|specified]  HEUR-DS-1, STATED AS ITS OWN FALSIFIABLE HYPOTHESIS AND SEPARATED FROM THE ALGORITHMIC CLAIM OF H-DS
  H-SUBRES-001  [SUBRES|weakened]  In the serial-S3 split of the m = 5 Semaev summation relation with a 2 | 3 arity split over a balanc

### optimal B / factor base size: patterns=['optimal|optimi[sz]e|model optimum|choose', 'factor.base size|\\bB\\b|\\|f\\|', 'mitm|pair.table|table'] ALL
-- proposals: 0 hits
-- hypotheses: 0 hits

### pair table m=2 prime: patterns=['pair.table|pair table', 'prime|fp'] ALL
-- proposals: 0 hits
-- hypotheses: 0 hits

### gae constant table b: patterns=['table b', 'constant|gae|engineering'] ALL
-- proposals: 0 hits
-- hypotheses: 0 hits
```

### 3.2 Raw grep output, term set 2
```

### term 'bsgs': 14 hits
  IDEA-20260801-003 [adaptation] On GOAL-ECDLP-001, every hypothesis that claims a sub-rho result must first pass a closed-form targe
  IDEA-20260802-002 [adaptation] An attack family on the ECDLP can be indexed by its TRACKED OBJECT, and that index can be made measu
  IDEA-20260805-2afd22 [unverified] GOAL-SDEG-001's title and objective are "certificate-backed", and its single completion criterion is
  IDEA-20260815-f81c17 [proposed] Every comparison in this campaign names rho and BSGS as the baselines. BSGS is faster in group opera
  IDEA-20260816-3fc7b2 [proposed] (A) Sparse secrets exist in FHE parameter sets because they make bootstrapping affordable, so any pr
  IDEA-20261006-12280d [proposed] In the generic group Z/251Z, with handles that hide the integer representative, 64 planted targets, 
  IDEA-20261006-b6b4ce [proposed] On the first ordinary prime-field curve E with a rational 2-torsion point, prime p in [211, 500), j 
  IDEA-20261015-29fdc8 [proposed] (A) On pair 46, w acts on G as lambda = 2/v mod N (v*w = pi+1, pi = 1 on G). The x-map R of w permut
  IDEA-20261015-7a3c9e [proposed] For the repository's folded pair-state index calculus (a table of #states folded pair sums of base r
  H-BND-3b83a3 [analyzed] On the two toy standing challenges at epoch 1, the best already-measured alternative beats or trades
  H-ECDLP-3ac227 [proposed] SCOPE. A measurement of where baby-step giant-step stops being a usable second baseline under an ENF
  H-ECDLP-74960f [proposed] Test all original witness, distribution, cover and census predictions with exact finite interfaces a
  H-ECDLP-9890e8 [specified] Fix the exact crossover-order identities of IDEA-20260808-2fabbc before any signed-y cascade, any Bo
  H-GRUMPY-62b749 [approved] CLAIM (heuristic_validation / generic-group instrument; NO ATTACK; NO EXPONENT). LET l∈{101,257} (pr

### term 'mitm': 63 hits
  IDEA-20260725-001 [methodological] Wiener-style full-cost accounting applied to classical supersingular path-finding (MITM vs low-memor
  IDEA-20260731-007 [unverified] For prime-field Semaev index calculus at arity m>=4 with factor-base size B=N^beta, the decompositio
  IDEA-20260805-c60813 [unverified] EVERY ATTEMPT UNDER THIS GOAL HAS STAYED INSIDE MEET-IN-THE-MIDDLE AND CLAW. EXP-SSIQ-4de240, EXP-SS
  IDEA-20260807-bbdcf3 [proposed] (A) THE TWO NUMBERS, AND WHY THE GAP CUTS BOTH WAYS. For an ordinary E/F_p with Frobenius trace t, d
  IDEA-20260808-06aae4 [proposed] Demirci-Selcuk meet-in-the-middle attacks buy time with a precomputed table of delta-set multisets w
  IDEA-20260808-24c61b [proposed] Write k in base B with m = log_B N digits, so Q = sum_j [d_j B^{j-1}] P with d_j in [0,B). ECDLP is 
  IDEA-20260808-3f8a2b [proposed] The x-oracle MITM (Arm B) reduces the total field-operation cost to find a target number of relation
  IDEA-20260808-4f3ef4 [structurally_distinct_control] In the existing toy m=3 Semaev/MITM setup, replacing the right-half x(P2+P3) keys with deterministic
  IDEA-20260808-778f82 [proposed] DERIVED THIS SESSION. A meet-in-the-middle on the oil-vector search needs the quadratic map to SPLIT
  IDEA-20260808-7c4e9d [proposed] The true-null control experiment suggested by the red team ("Arm D: Random-from-F_p MITM") has alrea
  IDEA-20260808-a3f7c1 [proposed] (A) THE OBSTRUCTION THIS AVOIDS. H-XOR-d1a480 (rejected_scoped per DEC-20260808-6a7ac4) showed that 
  IDEA-20260808-c5f9a2 [proposed] (A) THE OBSTRUCTION THIS AVOIDS. H-XOR-d1a480 (rejected_scoped per DEC-20260808-6a7ac4) shows that c
  IDEA-20260815-88658a [proposed] GOAL-KEX-001 proposes a constructive turn: build a key-exchange candidate whose flatness assumptions
  IDEA-20260815-e94ea3 [proposed] The published algorithm builds a keyed table and does claw finding, giving memory essentially equal 
  IDEA-20260821-e46061 [proposed] A meet-in-the-middle ("splice-and-cut") chunk-separation instrument, restricted to Round 1 (the firs
  IDEA-20260821-ea35d1 [proposed] Construction R1-SEP10, defined exactly as: MD4 Round 1 (steps 1-16, word k used at step k+1); FREE W
  IDEA-20260828-0155e5 [proposed] Build and EXECUTE, to a certified key recovery, a Demirci-Selcuk-style meet-in-the-middle (DS-MITM) 
  IDEA-20260828-4d7330 [proposed] (A) H-MDFIVE-bf7767's HEUR-H1, H-MDFIVE-0ca596's HEUR-H1, and IDEA-20260828-69bde4's H1 each state a
  IDEA-20260828-55a0de [proposed] (A) THE GAP. Of the 25 filed RQ-MLKEM-003 proposals, every "dual"-attack record (5a4409, 0eb075, ba5
  IDEA-20260828-69bde4 [proposed] For MD4 and MD5, under the standard splice-and-cut architecture (one chunk computed forward from the
  IDEA-20260828-c65b10 [proposed] IDEA-20260805-72ec9a correctly identifies that REF-B does not yet exist as a frozen, measured artifa
  IDEA-20260901-1ddfd4 [proposed] (A) THE LOWER BOUND, RIGOROUS WITHIN THE FAMILY. Fix a dimension g and let A be a superspecial princ
  IDEA-20260901-7d0bfd [proposed] FIVE SEPARABLE CLAIMS. (A) OBJECT AND COST. The SHA-1 disturbance vector (DV) is a codeword of the l
  IDEA-20260901-871141 [proposed] (A) THE SHAPE NOBODY HAS USED. CSIDH key recovery, in the vectorization formulation, is: given E_0 a
  IDEA-20260901-ac7566 [proposed] FIVE SEPARABLE CLAIMS. (A) A DISTINCT OBJECT. Every SHA-1 preimage result in this corpus (KN-LIT-421
  IDEA-20260901-e4184f [proposed] Five statements. A is the construction, B is the covolume identity that is the whole content, C is t
  IDEA-20260904-7caed1 [proposed] (A) THE LAW, STATED ONCE AND THEN APPLIED. Let a search problem be presented as a composition struct
  IDEA-20260922-845a77 [proposed] Search heuristic 3 (agents/idea-generator.md) asks, for any bottleneck search, whether the target sp
  IDEA-20260922-faa8d2 [proposed] SCOPE: symmetrized descended pdp over F_{2^n}, n prime, factor base a subspace V of dimension l; ari
  IDEA-20260926-d3c5a5 [proposed] CEILING FIRST. No exponent moves and nothing here bears on ECC2K-130 except negatively. Representati

### term 'pair table': 3 hits
  IDEA-20261018-49fdf7 [proposed] Every recorded pair-table, k-sum and 6-sum design at ECC2K-130 and every n=85,89 rung is a non-adapt
  H-KIC-c9c760 [proposed] On the fixedN19base/eight publiccases, orbit-canonical x lookup with exact witness transport lowers 
  H-RELN-6d1a05 [specified] For the exact nine-curve,54-instance interval-chart pair-table protocol, calibration-selected public

### term 'two-term': 6 hits
  IDEA-20260829-b5a2c8 [proposed] (A) THE ACCOUNTING. Let G have prime order N, let the factor base have size B, let D be the cost in 
  IDEA-20260830-3c0861 [proposed] (A) THE GATE, STATED PRECISELY AND FOR THE FIRST TIME AT THE ARITY THAT MATTERS. The two-term point-
  IDEA-20260830-4ab603 [proposed] (A) THE COUPLING THAT THE TWO-TERM MODEL LEAVES OUT. In the charge T(B) = m!*N*D/(2^m*B^{m-1}) + c_L
  H-ECDLP-4ce467 [proposed] THE ARTIFACT UNDER AUDIT is the two-term point-decomposition cost model used by three committed prop
  H-ICEX-6f3e4b [proposed] (A) THE COUPLING THE TWO-TERM MODEL LEAVES OUT. In a charge of the form T(B) = m! N D / (2^m B^{m-1}
  H-PFDR-064546 [proposed] (A) THE ACCOUNTING. Let G have prime order N, the factor base have size B, D be the cost in group op

### term 'family optimum': 1 hits
  IDEA-20260926-20ba8f [proposed] Representation class R1 of RQ-ECDLP-623a32 (x-coordinate subspace base at the cap locus); the attack

### term 'arity ladder': 7 hits
  IDEA-20260803-e2f5bd [proposed] IDEA-20260801-021 PROVES |F_p| <= 3 d_p FOR A DEGREE-d_p ALGEBRAIC PREDICATE AND STOPS. IDEA-2026080
  IDEA-20260803-fa9839 [proposed] THE CENTRAL COMPARISON THIS PROGRAM EXISTS TO DECIDE HAS NEVER BEEN WRITTEN DOWN AS A FORMULA, AND I
  IDEA-20260808-2ef5c8 [proposed] IDEA-20260803-fa9839 charges T = m! N D_trial / B^{m-1} + c_LA B^2 and derives "beats rho iff D_tria
  IDEA-20260828-5f259f [proposed] IDEA-20260805-4bd60c already defines and derives forced structural values for a graded nonlinearity 
  H-AES-5823dd [specified] Fix the exact count identity of IDEA-20260828-5f259f before any later-stage claim. Stage 0 asserts o
  H-ECDLP-b657e1 [specified] Fix the closed-form representation-multiplicity identities of IDEA-20260806-20f6ab before any factor
  H-ICEX-9e54c2 [specified] FOR EVERY FIXED ARITY m >= 2, EVERY LINEAR-ALGEBRA EXPONENT omega IN THE DECLARED RANGE, AND EVERY F

### term 'tail/h-fold': 7 hits
  IDEA-20260808-4854f8 [proposed] Published DFRs combine a per-coordinate tail probability p across coordinates by a union bound or an
  IDEA-20260808-b16d04 [unverified] Conditionally on H1-H5, a fixed public target-independent signed-y antisymmetric partition with root
  IDEA-20260831-ae480e [unverified] PART 1 (a premise-check this session already performed by direct source retrieval, not assumption): 
  H-BINSTD-ecd982 [approved] The restart lengths begin 1, 1, 2, 1, 1, 2, 4, 1, 1, 2, 1, 1, 2, 4, 8. Their sum is 32. The block en
  H-GRUMPY-1ead49 [approved] In the generic prime-order group written as Z/l, the set C_n of targets solved by any schedule in th
  H-ICPERF-604887 [approved] The ten costs are four 2s, three 4s, two 8s and one 16. Their sum is 52 and their sum of squares is 
  H-PFDR-2765d2 [specified] On prime-order ordinary curves E/F_p with log2 p in 20..32, generated by generate_prime_order_curve(
```

### 3.3 Hits that may be the same object (id + first 100 characters of claim)

| id | status | claim (100 chars) | same object as QC3? |
|---|---|---|---|
| IDEA-20260928-ce3ab0 | proposed | "REPRESENTATION CLASS AND STAGE: R1 of RQ-ECDLP-623a32 (the point is keyed by x in F_p, and its sign by a stored y-bit)." Title: the generic collision floor, S >= (1/2) sqrt(r N) | Same (R1, Sigma) frame; gives the lower bound QC3's family approaches. Not the recipe. OPENED (record 1). |
| H-PFDR-cf8ca6 | analyzed | "the generic collision floor (1/2)*sqrt(r*N) REFINED to its aggregate, premise-audited" (supersedes H-PFDR-0cc7e8) | Tests the floor on committed mitm rows (default |F| per arity, h = (m+1)//2). OPENED head only (record 3). |
| H-PFDR-064546 | proposed | "(A) THE ACCOUNTING. Let G have prime order N, the factor base have size B, D be the cost in group operations of one m-decomposition attempt" | The two-term model T(B) = m! N D/(2^m B^{m-1}) + c_LA B^2, B* = Theta((N D)^{1/(m+1)}); m = 2 free-oracle floor N^{2/3} at N^{1/3} memory. That is the (2, 2) exponent 2/3 of QC3. Table build is not charged there. OPENED (record 2). |
| H-PFDR-0cc7e8 | specified | "On the committed mitm rows of the crypto_autoresearcher.index_calculus engine (results/sweep-minfill-20260926, sweep-arity..." | Predecessor of cf8ca6. Not opened. |
| H-PFDR-2765d2, H-PFDR-4765e4 | specified | "the mitm engine's table is the x-keyed signed h-fold sumset of the base and its search computes x(R_t - H - s F_j)" (mechanism, index) | Names the same table object (x-keyed signed h-fold sumset, h <= m-1) and the same search; census of coincidences, not a QC3 recipe. |
| IDEA-20260830-4ab603 / H-ICEX-6f3e4b | proposed | "THE FREE DECOMPOSITION ORACLE IS NOT A BOUNDARY LIFT, IT IS A MEMORY PURCHASE, AND ITS PRICE IS EXACTLY B^2" | Records that the m = 2 pair table is a memory purchase of B^2. Same lesson at j = 2. |
| IDEA-20261015-7a3c9e | proposed | "Orbit-folded m=2 Koblitz index calculus is baby-step giant-step on the quotient and sits on the Bernstein-Lange r/P law" | Records that the m = 2 folded/walked recipe is BSGS-like. QC3 generalises to j >= 3. |
| IDEA-20260808-812554, H-ICEX-9e54c2 | proposed / specified | "The sigma-threshold ..."; "The arity threshold - the fully charged point-decomposition IC versus rho comparison is a closed-form function of arity m" | Closed-form arity thresholds; same obstruction (lead LEAD-ICE-generic-oracle-arity-cost-floor). |
| IDEA-20260807-32f96d | proposed | "Arity m >= 4 has ZERO measured cost cells anywhere in the corpus" | Superseded by the Python arity sweeps (m up to 7). |
| IDEA-20260904-d84512, H-ECDLP-77caa5 | unverified / specified | "ADVICE LENGTH UNDER A CHARGED DECOMPRESSION TIME ... the generic frontier S*T^2 = Theta~(N)"; "Advice exponent gamma_C ... indistinguishable from 0" | Same frontier cited as QC3's ingredient, different object (compressed log tables). |
| IDEA-20261018-49fdf7 | proposed | "Every recorded pair-table, k-sum and 6-sum design at ECC2K-130 and every n=85,89 rung is a non-adaptive table-lookup algorithm with advice below sqrt(N)" | Closes pair-table / k-sum engineering formally on the binary side (DKM 2025/783). Context for SO-TABLE; QC3 is prime-field constants. |
| IDEA-20260731-012 | adaptation | "Large-prime variation for prime-field ECDLP ... near-miss harvest over a shifted (m-1)-sumset" | Different (large primes); composable with QC3 (sibling lead LEAD-ICP-residual-partial-relations). |

No ledger record in the index proposes a table of ALL m-fold sums with a single lookup per walked target on a prime field, nor an arity dimension for the Table B planner. Experiments index not searched (outside the stated scope).

### 3.4 Full records opened (3 of 3 allowed, by exact path)

1. ledger/proposals/IDEA-20260928-ce3ab0.yaml (claim and mechanism sections). Content that decides the gate:
   - "OBJECT FRAME. Representation: R1, the x-coordinate key, 2:1 on points. Operation set Sigma: translation by the signed factor-base elements (+-F_a), plus the target generation aP+bQ ... Trichotomy: PARTIAL-ACTION (Class I)". This is QC3's pair verbatim.
   - Lemma (derivation tier, unreviewed): E[r] <= 4 S^2/N, so S >= (1/2) sqrt(r N); with r ~ c_m |F| = c_m N^beta the floor is N^{(1+beta)/2}. "At beta = 1/m the floor exponent is (m+1)/(2m) ... the mitm engine is exponent-optimal among generic single-instance engines at odd m." (my arithmetic: at beta = 1/(2j-1) the floor is N^{j/(2j-1)}, which is QC3's exponent m/(2m-1) at j = m; so QC3's optimum sits ON the recorded floor exponent.)
   - (C2) "mitm at odd m = 2h-1 sits at T = N^{(h-1)/m}, precomputation N^{h/m} and S = N^{h/m}. BL reaches the same T and precomputation with S = N^{1/m}, so mitm index calculus is Pareto-dominated by BL in this model at every odd m."
2. ledger/hypotheses/H-PFDR-064546.yaml (statement, assumptions). T(B) = m! N D/(2^m B^{m-1}) + c_LA B^2, B* = Theta((N D)^{1/(m+1)}), T* = Theta((N D)^{2/(m+1)}), memory Theta(B*); m = 2 free-oracle floor N^{2/3} at N^{1/3} memory, "Pareto-dominated by Pollard rho on BOTH axes"; the linear-algebra exponent 3/2 moves it to N^{3/5}. Table construction is outside this model; QC3 charges it (c_tab = 1 GAE per key, H9).
3. ledger/hypotheses/H-PFDR-cf8ca6.yaml (header, first 60 lines only): refines the floor to an aggregate form, "ceiling analyzed, never supported, on current evidence".

Decision from the ledger: the object (R1 x-key, Sigma = +-F translations, partial-action) and the cost accounting are recorded; the recipe at j = m, B at the j-table optimum is not. Consistent with advances_lead, not new.

## 4. N4 Notation change (IC / factor-base / representation candidate)

(representation, operation set) pair as stated by QC3: (R1: x-key, with stored y-bit, of the full <= m-fold signed sumset of a small factor base; Sigma = translation by factor-base elements, plus the walked-target step R <- R + G, the latter an addition performed on actual points).
- This is not a new arithmetic. It is the pair recorded in IDEA-20260928-ce3ab0 ("Representation: R1 ... Operation set Sigma: translation by the signed factor-base elements"), IDEA-20260928-4e2be7 and H-PFDR-4765e4/2765d2 ("Representation R1 x-key with stored y-bit; operation set Sigma = translation by +-F_a; partial-action class (Class I)"). QC3 changes the table arity inside that pair, not the pair.
- Not a rigidity result in new notation:
  - IDEA-20260806-c5d183 (full translation action => constant or injective): QC3 does not propagate the lossy key under full translation. The walk carries the point; x(.) is applied only at lookup, so QC3 is in the partial-action class that c5d183 leaves open and that the object-frame doc names as the index-calculus class. No restatement.
  - IDEA-20260901-863e36 (projection paired with an operation set; block systems of <Sigma>): QC3's Gamma is {+-1} (negation fold), the already-recorded quotient. Nothing new.
  - KN-OPEN-020 (bounded-degree algebraic factor bases scoped out): QC3's base is an enumerated interval/random abscissa set with a hash table; it neither contradicts nor advances KN-OPEN-020. It is not in the open class (high-degree / implicit / target-dependent).
  - KN-FIND-ffe1df Theorem C (an exactly sum-compatible bucket index is a surjective homomorphism, impossible for prime N, 1 < M < N): irrelevant, QC3 uses no sum-compatible filter; the group law is the combining rule and the y-bit resolves the 2-valued x-key branching.
- QC1's "(m, j)" and "tau" coordinates are bookkeeping for the table arity j and the number of enumerated summands m - j (tau = 0 means none). They are not a new representation. Mapping to recorded notation: j = h (README section 3 / tails.py), m - j - 1 = fixed points, "scan" = the one S_3 solve per target; the engine's allowed range is h in [1, m-1], so j = m is exactly the case the Python engine excludes.
- Conclusion: N4 passes only in the sense that QC3 claims no rigidity result and contradicts none. It does not pass as "new notation for something unrecorded": the object frame is the recorded one.

## 5. Arithmetic cross-check of the candidate's stated model (my arithmetic, not a measurement; sizes in units of sqrt(r) as in LEADERBOARD Table B)

Inputs taken from the candidate (H7-H9): hit probability per walked target 2K/r, K = table keys; c_tab = 1; c_w = 1.096; relations rho_rel*B with rho_rel in [0.667, 1]; r = 2^23.4 (fp24 row; incumbent S = 14, matched rho 1.04 in LEADERBOARD.md L56).
- Incumbent m = 2, B = 111 abscissae (222 points, LEADERBOARD L157): K = B^2 + B = 12,432 keys (matches the candidate's 12.4k). S = K + rho_rel B 1.096 r / (2K) gives 14.6 sqrt(r) at rho_rel = 0.667, 16.8 at 0.8, 20.0 at 1.0, against the table's 14 (candidate: 14.71 vs 14.79 measured; its rho_rel is evidently near 0.67). The model reproduces the incumbent row to about 4% at rho_rel = 0.667.
- QC3 m = 3: counting signed multisets of size <= 3 folded by negation, K = 8,107 at B = 22 and 10,412 at B = 24 (the candidate states 7.6k-9.8k; my count is 4-6% above its upper end, immaterial). S = 5.7 / 6.4 / 7.4 sqrt(r) at B = 22 for rho_rel = 0.667 / 0.8 / 1.0 and 5.9 / 6.5 / 7.3 at B = 24: inside the candidate's 5.8-7.4 band. The recorded collision floor (1/2) sqrt(rho_rel B r) is 1.9-2.5 sqrt(r) there, so the predicted S is about 3x the floor: consistent with it, not a violation.
- These are PREDICTIONS of a model, not outcomes. The model has never been run at j = m on a prime field in this program.

## 6. Recommended edits to the candidate before it is filed (does not change the verdict)

1. Add to the citation list and the dedup text: IDEA-20260928-ce3ab0 and H-PFDR-cf8ca6 (collision floor, same object frame); research/ic_triple_table_20260923 and research/ic_triple_counted_20260923 (Koblitz triple table, same r^{1/10} law, measured); LEAD-ICP-generic-table-decomposition's measured mitm exponents (0.67 / 0.75 / 0.60) as the h = (m+1)//2 baseline QC3 is compared with.
2. State the novelty narrowly: "port of an already-measured table-arity lever to the prime Table B recipe at the j = m vertex, with the base re-sized". Drop "never run" unless qualified by "on a prime field, in ic.pipeline, with j = m".
3. Import the Koblitz lesson: gains must be scored against a matched rho with the IC arm's own canonicalisation (ic_triple_counted section 3), and the smallest cell lost to a base-size floor. Check the rank/early-stop floor at m >= 3 with B = 13-22 before any panel.
4. Replace "CGK frontier" by "two-term model + collision floor" in the mechanism; keep CGK only as the reason SO-TABLE applies.
5. Report the ratio to the collision floor (1/2) sqrt(rho_rel B r) per row alongside matched rho and bsgs.negation, so "BSGS relabelling" is excluded by construction.
6. Pre-state disposition if the ordering predicted by H7-H9 holds: the result is a constant on B3 (tier I) and does not change LEAD-ICP-generic-table-decomposition, LEAD-ICE-generic-oracle-arity-cost-floor or any SO.
