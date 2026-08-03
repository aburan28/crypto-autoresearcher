# Theory note: source provenance is advice, not a point invariant

## Candidate mechanism

The predecessor assigned one public unary feature to each D2 point. Its x-only
signal vanished once the random label respected the same point-negation fibers.
This successor asks a different question: does the *construction history* of a
D2 point predict the complementary construction history in a D2+D2 witness?

Source provenance is not intrinsic to a group element. A D2 point can have many
factor-pair witnesses, and a fixed-curve compiler may retain one or more of
them as advice. The experiment therefore charges the witness and tag explicitly
and tests two public symmetry-bound witness policies.

## Exact null lemma

Let `I` index D2 points, let `nu:I->I` be point negation, let `m(i)` be exact
unordered factor-pair multiplicity, and let `tau:I->[r]` be an inversion-
invariant candidate tag. Partition the `nu`-orbits by orbit size, `m(i)`, and
selected-witness class, then permute complete tag records within each part. The
resulting `tau_pi` preserves:

- `tau_pi(i)=tau_pi(nu(i))`;
- the global tag histogram;
- the occupied-tag count;
- the tag histogram within every multiplicity stratum;
- the tag histogram within every selected-witness class;
- the factor base, D2 support, D4 relation, and target schedule.

This is a finite combinatorial fact, not a randomness claim. Randomness enters
only through the disclosed choice of within-stratum permutation. A null with no
effective movement has no power and cannot support promotion.

V2 also uses a distinct compositional null: permute complete public source
records among sign fibers and recompute tags. This null preserves source
composition but does not condition on the candidate's resulting tag histogram.
The two nulls answer different questions and neither substitutes for the other.

## Same-outer-schedule obstruction

Suppose the candidate and materialized D4 baseline inspect the same ordered
factor points, compute the same complements `Y_j=Q-f_j`, and stop at the same
first supported complement. Materialized D4 performs one exact dictionary
lookup after each outer EC subtraction. A route-and-verify source compiler does
the same outer subtraction and then performs nonnegative inner work, including
at least one EC addition on a successful route. Therefore

`T_source(Q) >= T_materialized_D4(Q)`

in online group additions for this interface.

This is a restricted theorem, not a general barrier. Its escape routes are an
outer-factor router, batch sharing across targets, an exact algebraic translator
that changes the primitive cost model, or route construction that supports a
different query schedule. V2 therefore separates a structural source signal
from a useful-compiler signal; the current inner scanner has no honest path to
strict materialized-D4 online dominance.

## Semantic sufficiency of D2 values

If two provenance states have the same semantic D2 point `a`, then for every
target `Y` their exact complement set is the same set of witnesses of `Y-a`.
Alternate provenance can help implement or compress that lookup, but it cannot
be credited as additional semantic support. V2 records every D2 witness and
the all-witness tag multiset while using one symmetry-bound witness in advice.

## What a positive result would mean

If the candidate beats every effective matched shuffle, the evidence would
show that the selected source construction aligns with the inverse addition
relation beyond occupancy, inversion symmetry, and D2 multiplicity. It would
justify testing richer multi-witness or batched source states.

It would not show:

- a sub-square-root ECDLP algorithm;
- an asymptotic exponent improvement;
- an efficient relation generator at cryptographic sizes;
- rank or sparse-linear-algebra savings;
- a deployment-relevant break.

Those claims require replicated scaling plus the full relation, rank, linear
algebra, and individual-log pipeline.

## Necessary inequalities

For candidate advice `S_c`, exact-D2 advice `S_2`, materialized-D4 advice `S_4`,
candidate supported online work `T_c`, exact-D2 work `T_2`, materialized work
`T_4`, and equal-advice BSGS work `T_b`, a practical source compiler needs to
improve the lower envelope of these comparators. A first diagnostic is

`S_c*T_c^2 < S_2*T_2^2`.

Strict joint dominance would require

`S_c < S_4`, `T_c < T_4`, `T_c < T_2`, and `T_c < T_b`.

The same-outer-schedule theorem prevents the current scanner from satisfying
the materialized online inequality. Beating both nulls without the comparator
envelope is evidence of structure but not a useful fixed-curve compiler. Using
enough advice to make BSGS constant-time also precludes an online win.

## Proof track

- Characterize factor-base families for which source tags reduce conditional
  right-tag entropy after D2 multiplicity is conditioned out.
- Bound route triples and exact candidate reads from that entropy or a stronger
  expansion parameter.
- Determine whether the same structure survives multiple D2 witness policies.

## Disproof track

- Show that tag-shuffled routes have the same distribution conditional on
  multiplicity and inversion orbit.
- Exhibit source tags whose apparent gain is entirely canonical-witness bias.
- Show that any entropy gain is paid back by tag buckets, route triples, or
  candidate verification.
- Compare the resulting `S*T^2` diagnostic with the generic preprocessing
  scale without treating it as a universal lower-bound proof.
