# Refreshed duplication, knowledge, and proof/control audit

## Scope and provenance

This audit is the Coordinator pre-dispatch gate for `IDEA-20260806-9c2f80`.
It was refreshed on 2026-08-09 in the isolated worktree
`/Volumes/SSD990/crypto-autoresearcher/.worktrees/ssi-cost-source-20260809` at
commit `0ca9d65e67baf87ebe1754973c213c100928dbab`. `origin/main` was fetched
and resolved to `48bb882e71c12595fc7830faeb091567733561bd`; `git ls-remote
--heads origin` was also checked before any new identifiers were allocated.

The prior audit remains immutable at
`coordination/goals/GOAL-SSI-001/batches/BATCH-b3c87f/tasks/TASK-20260806-fd3518/duplication_audit.md`.
This document is an additive refresh, not a replacement or correction of that
record.

## Corpus and remote checks

The refresh searched the current committed tree with `rg` over `ledger`,
`knowledge`, `ideas`, `coordination`, and `experiments` for:

* `resolution fiber`, `random-advice`, `p-only advice`, `p-dependent
  preprocessing`, `preprocessing frontier`, `changed quantifier`, and `A_p`;
* the exact candidate identifier and its nearest-neighbour identifiers; and
* generic SSI terms `non-uniform advice`, `advice.*OneEnd`,
  `preprocessing.*OneEnd`, and `p-only structure`.

The remote-head check found no branch named for this candidate or for an SSI
advice/preprocessing successor. This is a collision check, not proof that a
remote branch has no semantically related work.

## Findings

### Exact and adjacent SSI records

No committed `knowledge/` finding or literature item supplies the exact
classical object in this proposal: a per-prime, instance-independent advice
string `A_p`, a size axis `S`, a per-instance query-time axis `T`, and the
resolution fiber `R(a)` for the OneEnd problem. The two generic knowledge
records returned by the broad non-uniform search (`KN-LIT-5621` and
`KN-LIT-5232`) concern non-uniform certificates, not supersingular
endomorphism computation; they are not treated as support or novelty evidence.

The following adjacent committed records were re-read or re-targeted:

| record | overlap | disposition |
| --- | --- | --- |
| `IDEA-20260805-250e50` | A degree-threshold screen and the same possible `1/5` branch | Distinct: its `gamma` is a per-query time exponent and it has no advice/memory axis; the current record prices the p-only table that a “free” screen would require. |
| `IDEA-20260805-bc8246` | A memory-sensitive cost functional | Distinct: `w` is working memory for one execution, while `S` is immutable advice written before instances and amortized across them. |
| `ideas/catalogue-20260805/B1-9` | A per-vertex j-only filter | Distinct: the filter is recomputed at each vertex and has no p-only advice quantifier. |
| `ideas/catalogue-20260806-mlkem-aes-ssi-ssiq/S2-4` | Multi-target amortization and an explicit reference to this candidate | Not a duplicate: S2-4 is a quantum pooled-collimation experiment tracking a difference lattice and shared coset states; it has no classical advice string, preprocessing table, or `(S,T)` frontier. |
| `ideas/catalogue-20260806-mlkem-aes-ssi-ssiq/S1.md`, `Q3.md` | Several non-uniformity or reusable-structure references | These entries explicitly route a p-only reusable object to `IDEA-20260806-9c2f80`; they do not instantiate its classical OneEnd frontier. |
| `IDEA-20260806-d5a34e`, `IDEA-20260806-94676a` | Later proposals cite the candidate as a boundary or neighbour | They do not replace the candidate's tracked object or supply a competing `(S,T)` construction. |

The new S2 catalogue references are a useful collision audit result: they
confirm that the advice axis is visible elsewhere in the corpus, but also
record the mechanism-level separation. The candidate remains `unverified`,
not “novel” in the literature.

### Proof-search-map gate

The proposal contains all four required Section 8 audits, and the refresh
checked them against the current bytes:

1. **Exact baseline reproduction:** `S=0` returns the incumbent
   `p^{1/3+o(1)}` row and `S=p^{1/2}` is the stated MITM/Delfs–Galbraith
   balance embedding.
2. **Observation collision:** Construction A at `sigma=4/5` and Construction B
   at `theta=1/5` both produce `(S,T)=(p^{4/5},p^{1/5})`; the record explains
   that B's stored curves already carry the orders, so this is a notation
   collision, not a second mechanism.
3. **Quantifier order:** the incumbent is `forall p forall E`; the candidate is
   `forall p exists A_p independent of E forall E`, with advice size `S` and
   query time `T(S)`.
4. **Method ceiling and nearby object:** the strongest permitted statement is
   only for the named closed list, never all advice strings; the oriented,
   CSIDH-shaped control is required to avoid an object-insensitive flat result.

The proof map is therefore sufficient for dispatch of a bounded accounting
experiment. It is not a proof of the proposed frontier, and H-ADV-3 remains a
load-bearing conjecture.

### Matched controls gate

The proposal has the required matched null/control package:

* a random-advice null with the same size/access/query budget, hash-committed
  before treatment rows, forced to return the incumbent row;
* a shuffled-fiber control, forced to remove the speedup if the instrument is
  measuring orders rather than set membership;
* symbolic `S=0` and `S=p` known-answer gates;
* at least three interior sigma points and a monotonicity check; and
* a nearby oriented/CSIDH-shaped control that must not reproduce the same
  frontier.

The initial bounded experiment deliberately stops before the optional toy
graph arm. It can therefore make no statement about H-ADV-1. H-ADV-2
(order-to-curve preprocessing) and H-ADV-3 (the fiber bound) remain explicitly
unvalidated assumptions and are reported as such.

## Coordinator decision at this gate

**PASS for a design-and-review batch; no mathematical result.** The candidate
is sufficiently differentiated from the committed SSI corpus to freeze its
Stage 0/1 accounting contract. The contract must remain derivation-only:
no isogeny implementation, no attack run, no exponent transition, no security
claim, and no assertion that the closed-list frontier is a lower bound over all
advice.

The next gate is an independent Validator and Red Team review after a snapshot
commit. Only a later Coordinator ledger archive may set the experiment to
approved/frozen/execution-authorized. A random-advice null failure, an `S=0`
gate failure, or a construction below `1/3` at `sigma <= 2/3` must terminate
the package or escalate to the required breakthrough review; none is observed
in this audit because no treatment has run.

## Sources checked

* `ledger/proposals/IDEA-20260806-9c2f80.yaml`
* `coordination/goals/GOAL-SSI-001/batches/BATCH-b3c87f/tasks/TASK-20260806-fd3518/duplication_audit.md`
* `ideas/catalogue-20260805/`
* `ideas/catalogue-20260806-mlkem-aes-ssi-ssiq/S1.md`
* `ideas/catalogue-20260806-mlkem-aes-ssi-ssiq/S2.md`
* `ideas/catalogue-20260806-mlkem-aes-ssi-ssiq/Q3.md`
* `ledger/goals/GOAL-SSI-001/goal.yaml`
* `ledger/decisions/DEC-20260805-596d71.yaml`
* `ledger/decisions/DEC-20260809-ea08ae.yaml`

