# Citation re-read notes — EXP-BINSTD-38e4ad Stage 0

Task: `TASK-20261001-b78ef3`. HOLD-S. Observations/documentation only.
No deployed-curve break claim. No fixed-target orbit-clause satisfiability claim.

Re-read in full (claim sections and mechanism) of the three title-only citations
named by IDEA-20260922-2a3771 / HOLD-S review Step 1. Distinctions vs the
HOLD-S-corrected H1 (soundness null under a77711 A1/A2) are recorded below.

## IDEA-20260904-3c7a91

- **Title/claim axis:** PDP CNF-XOR model admits no above-leaf pruning; conflict
  count ≈ 2^{m l}/|G|; solver engineering cannot move the search exponent.
- **Object:** leaf-completeness / unit-propagation structure of the descended
  Semaev CNF, independent of Frobenius.
- **Distinction vs corrected H1:** 3c7a91 is about *solver pruning of one PDP
  instance*. Corrected H1 is about whether *coordinate squaring is a symmetry of
  one fixed-target solution set* (it is not: A1 maps solutions to the conjugate
  instance). No shared claim that orbit clauses on one CNF are
  satisfiability-preserving. Citation is background on leaf enumeration, not a
  soundness warrant for fixed-target Frobenius clauses.

## IDEA-20260915-eee7e4

- **Title/claim axis:** Side-constrained core — add `x_i ∈ x(E)` per block to
  shrink leaves from |V|^m to |V ∩ x(E)|^m ≈ 2^{m(l-1)} without losing
  E-decompositions (constant-factor, no exponent move).
- **Object:** E-membership / twist-side filter on the factor-base alphabet.
- **Distinction vs corrected H1:** eee7e4 is a *sound* local alphabet filter
  (side bit). Corrected H1 rejects treating Frobenius orbit equivalence as a
  *sound filter on one fixed R*. H2 in this packet (membership orbit-collapse on
  a tau-stable V) is preprocessing-only counting, not the eee7e4 solver-side
  constraint. Do not conflate E-side blocking clauses with tau-orbit clauses.

## IDEA-20260920-b9f0c5

- **Title/claim axis:** WDSat conflict audit on Frobenius-invariant factor bases
  at n=41 (cheap) / n=43 (decisive) vs null 2^{m l}/m!; basis-blind vs first
  pruning.
- **Object:** Whether an *invariant V* prunes SAT search on one fixed R,
  residual after a77711 closed invariant-ring rewriting.
- **Distinction vs corrected H1:** b9f0c5 *assumes* the factor base is
  tau-stable and asks a *search* question (conflicts vs orbit-naive null). This
  packet's corrected H1 asks the prior *soundness* question (A1/A2) at n=17 via
  exhaustive group-arithmetic census — not WDSat. Stage 1 primary instrument is
  the census; SAT is out of Stage 1 scope. b9f0c5 does not license fixed-target
  orbit-equivalence CNF clauses.

## Summary

| Citation   | Lives in                          | Supports fixed-target orbit CNF? |
|------------|-----------------------------------|----------------------------------|
| 3c7a91     | leaf-completeness / no pruning    | No                               |
| eee7e4     | E-side alphabet filter            | No                               |
| b9f0c5     | WDSat on invariant V vs null      | No (different question)          |
| corrected H1 | a77711 A1/A2 soundness census   | Explicitly under test as UNSOUND |

`citation_reread_complete: true`
