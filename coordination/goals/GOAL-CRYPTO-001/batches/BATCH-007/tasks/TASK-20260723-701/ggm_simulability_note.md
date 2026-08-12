# KN-OPEN-005 GGM simulability screen

## Verdict and boundary

`NO_DISTINCT_UNAUDITED_FAMILY`.

No family ID is assigned. The checked corpus contains no remaining
prime-field representation family with an exact public oracle and a
target-conditioned transcript that is both outside the prior simulation
screens and useful for relations below the birthday bound. This is a
zero-compute corpus and theorem screen, not a universal lower bound.

No empirical work, standardized-curve execution, key recovery, attack
software, or breakthrough claim is present.

## What would count as a non-simulable transcript

Let \(H=\langle P\rangle\) have prime order \(N\), and let
\(Q=[k]P\). A generic algorithm's handles represent affine forms

\[
L_i(k)=a_i+b_i k\pmod N.
\]

Fix all side information explicitly granted to the base simulator. Choose
\(k_0\ne k_1\) for which every equality and inequality among the queried
\(L_i(k_j)\) agrees. Before a generic collision, the two base transcripts are
then isomorphic by renaming opaque handles. If an augmented oracle returns
\(Z_j\) on the same formal query sequence, a sufficient explicit
non-simulability certificate is:

1. the relabelling isomorphism preserves all side information granted to the
   base simulator;
2. a public verifier \(V\) has
   \[
   \left|\Pr[V(Z_0)=1]-\Pr[V(Z_1)=1]\right|
     \ge \epsilon,
   \qquad \epsilon\ge 1/\operatorname{poly}(\log N);
   \]
3. this gap is asymptotically larger than the generic collision term
   \(O((q+1)^2/N)\) when the simulator is limited to \(O(1)\) additional
   group queries and \(O(\operatorname{poly}(\log N))\) public arithmetic per
   augmented answer; and
4. \(Z_j\) contains an exact target-conditioned signed occurrence relation,
   or a certified miss, for both known-log relation targets and the identical
   operation on a fresh scalar-blind masked target \(Q+[t]P\).

For deterministic outputs, different verified outputs give
\(\epsilon=1\). Conditions 1--3 distinguish the augmentation from an exact
constant-overhead generic simulator. Condition 4 distinguishes a useful
representation from the trivial fact that concrete curve coordinates are not
opaque generic labels.

A raw \(x\)-coordinate, a universal identity, an aggregate count, a predicate
on a supplied tuple, or an existence bit without exact source replay fails
condition 4. Likewise, a source tuple, scalar, coordinate dictionary, or
target-fitted advice supplied as input is circular rather than
non-simulability evidence.

This criterion discriminates two explanations before any experiment:

- If every answer factors through admitted public equations, public query
  coordinates, and the simulator's formal expressions and equality pattern,
  an exact simulator exists and the generic square-root barrier remains.
- If a verified source-bearing output has the transcript gap above, the
  frozen augmentation is not exactly \(O(1)\)-overhead simulable. It would
  still need complete cost, rank, factor-log, and blind-descent review.

## Why the suggested jet families are not remaining families

### Higher-order public-equation jets

`THM-JETBARRIER1` T2/T4 already covers every finite jet order on a variety
given by public equations. At smooth points, formal smoothness supplies the
lift. At singular points, the fiber is defined by public Hasse--Schmidt
equations. Thus the answer is public algebra with zero additional group-oracle
queries. This includes a fixed public algebraic constraint by adjoining its
equations to the public variety.

It therefore fails the transcript-gap clause: after all admitted public data
and formal generic expressions are fixed, no hidden-\(k\) output remains.
Calling this family “higher order” does not make it unaudited.

### Constrained additive lifts

`FINDING-PF-IC-001` P1547 and
`p1547_prime_to_p_jet_coordinate_gate.md` already give the all-order
prime-to-\(p\) screen. The reduction kernel of a finite nilpotent lift has a
filtration by characteristic-\(p\) tangent modules. For
\(\ell=\lvert H\rvert\ne p\), multiplication by \(\ell\) is invertible on
every layer. Hence an additive map

\[
J:H\longrightarrow M,\qquad J([n]R)=[n]J(R),
\]

into a native finite, formal, Witt, crystalline, or additive arithmetic-jet
target is zero. Higher order does not create an \(\ell\)-primary channel.

A “nonadditive constrained invariant” is named only as a logical residual.
No public operation, output type, lift-invariance theorem, source inverse, or
transcript distribution is supplied. It is therefore not a family that can be
screened under the explicit criterion.

### Hasse-jet multiplicity codes

`ECDLP-IDEA-268` already records the decisive interface: local decoding needs
random access to source-sensitive value-and-Hasse-derivative symbols. Public
endpoint data do not provide that word. Supplying it or its point lift assumes
the missing source oracle. Without it there is no augmented transcript.

## Other residuals do not instantiate a family

1. **Composite-handle coordinate oracle.** `THM-JETBARRIER1` T6 identifies
   this as the seam where one restores the concrete curve encoding of
   arbitrary group elements. Its raw outputs are non-generic, but no
   target-conditioned exact source relation or sub-birthday path follows.
2. **GGM meta-completeness (G1).** A maximal language of simulable
   augmentations remains open model theory. It is not a representation oracle
   with an ECDLP transcript.
3. **Weil-restriction/descent publicness (G2).** This concerns extension-field
   descent. A prime field has no proper subfield for that construction, so it
   is outside the present prime-field scope.
4. **Arbitrary nonadditive point invariant.** This remains a placeholder until
   an exact, target-uniform operation is written. Missing mathematics cannot
   receive a favorable simulator or cost score.

Elliptic nets, incidence reporters, EQJ, TTN, first-order free jets, and their
named variants were excluded at handoff and were not reopened.

## Cheapest decisive gate

For any future exact family, apply the
`NS-TX-PRIME-001` symbolic relabelled-transcript-pair gate:

1. freeze the oracle, inputs, coefficient provenance, side information, and
   formal query sequence;
2. prove the collision-free two-world base transcripts are relabelling
   isomorphic;
3. derive the augmented outputs and verified probability gap;
4. reject a raw-coordinate-only gap;
5. require exact signed source replay for known-log and fresh masked targets;
6. charge setup, misses, output, rank failures, factor-log solve, blind
   descent, verification, bit work, traffic, and peak memory.

The gate passes only if the verified transcript gap exceeds
\(O((q+1)^2/N)\), replay is exact, certificate failures are zero by
construction, the complete fresh-target exponent is at most \(0.25\), and
complete work and memory exponents satisfy

\[
\tau\le 0.25,\qquad \lambda\le 0.45,\qquad \mu\le 0.45.
\]

The two outcomes have fixed meanings. A public/formal factorization produces
an exact simulator and barrier-side disposition. A source-bearing gap produces
only an unfiled theorem candidate for independent review; it is not
breakthrough evidence.

This is the cheapest valid discriminator because the current residuals lack
an oracle, not measurements. A fixture cannot define a missing transcript.

## Pollard-rho comparison and cost boundary

Pollard rho uses expected \(N^{1/2+o(1)}\) group operations and
\(N^{o(1)}\) serial memory. Shoup's bound gives
\(\Omega(N^{1/2})\) work to an \(O(1)\)-overhead simulable augmentation.

No family is proposed here, so no construction, relation-density, rank,
factor-log, descent, output, or memory exponent is assigned zero. There is no
candidate \(\lambda\) or \(\mu\) to compare favorably with rho. Even raw
non-simulability would not establish an advantage without the complete
\(\lambda,\mu,\tau\) ledger above.

## Falsification and limits

This checked-corpus disposition is falsified by an exact, mechanism-distinct
prime-field family that passes the transcript criterion and deduplication.
That event would authorize independent theorem review only. Conversely, an
exact simulator, a raw-coordinate-only gap, hidden source advice, missing
fresh-target replay, or an incomplete cost ledger leaves the disposition
unchanged.

The corpus search is not an exhaustive external-literature review, so
`novelty_status` is `unverified`. The result does not close every imaginable
augmentation, concrete coordinate-sensitive algorithm, extension-field
descent model, or nonadditive invariant. It changes no proposal, hypothesis,
evidence, decision, or goal status.

## Ranking rationale and handoff

The no-family disposition has better information gain per cost than renaming
higher-order or constrained jets: their public-equation and additive-target
forms already have theorem screens. The remaining seams do not instantiate an
oracle. I would test `NS-TX-PRIME-001` first for any future exact family,
because its symbolic two-world transcript pair is the cheapest valid
simulability discriminator. Until such a family exists, `KN-OPEN-004` or
`KN-OPEN-006` offers a more concrete theorem target than another
representation-name audit.

Return this note and `ggm_screen_report.yaml` to the Coordinator for
`TASK-20260723-702` snapshot archival and subsequent independent
`TASK-20260723-703` review. Do not file a proposal, open an experiment, or
change official research state.
