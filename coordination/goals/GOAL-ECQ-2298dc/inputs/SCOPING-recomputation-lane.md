# Scoping verdict: the recomputation lane does NOT reach rank 32, even on complete success

Author: orchestrating session, from a scoping task run 2026-08-24.
Status: input to GOAL-ECQ-2298dc. Not an evidence record.

## The finding that settles the campaign, independent of every cost estimate

A successful recomputation of Elkies' K3 delivers **rank 17 over Q(t)** -- his 2006
starting line. Reaching 32 from there is `17 + 15`, a specialisation sieve this
campaign has already recorded as not plausible with its resources. **The lane does
not reach the objective even on complete success.** That is a cleaner closure than
"too expensive" and it does not depend on any cost figure being right.

## My premise for the lane was INVERTED

The published construction runs **family -> Shimura curve**, not point -> family.
arXiv:0802.1301 is titled *Shimura curve computations via K3 surfaces of
Neron-Severi rank at least 19*: the K3s are the INSTRUMENT and the curve equations
are the PRODUCT. So `u^2 = 16t^6 - 19t^4 + 88t^2 - 48` is the **output** of the
object we lack, not an input to it. There is no published map in the direction I
proposed. Every published D=6 family (Besser-Livne, Baba-Granath) is **level 1**;
the target needs level 79, and `X_0^6(79)` has genus 13 with its degree-80 cover of
`X(6)`, its universal family, and the map all unpublished.

## Elkies-Kumar was my conflation, confirmed

arXiv:1209.3527 computes **Hilbert modular surfaces** -- real multiplication, not
quaternionic. It does not apply to `X(6,79)`. What is genuinely shared is only the
generic 2-neighbour fibration-hopping machinery.

## A theorem that closes my own "reachable adjacent record" recommendation

I had proposed generic rank >= 19 over Q(t) as the nearest reachable record.
**It is unreachable via elliptic K3 surfaces, by a proven ceiling**: rho <= h^{1,1}
= 20 caps MW at 18 over C, and 0709.2908 states there is no elliptic K3 of MW rank
18 over Q, so 17 is the maximum over Q and the rank-18 record over Q(T) already
requires quadratic base change out of the K3 category. C2 needs elliptic surfaces
of Euler characteristic >= 3 -- a different object class whose descent behaviour is
unstudied here. **Recording this prevents a batch being spent on it.**

Also: the publicly available ceiling for an EXPLICIT family is **14** (Mestre or
Kihara). Every rung from 15 to 18 is Elkies' and none of those models is published.

## The Shimura curve equation, VERIFIED by exact arithmetic rather than fetch-counting

At `t = 14/13` the right-hand side is `258052096/4826809`, and `258052096 = 16064^2`
exactly with `16064 = 2^6 * 251`. So `u = 2^6 * 251 / 13^3` exactly, matching the
paper's stated orbit. The second orbit checks too: at `t = 2`, RHS = 1024 = 32^2.
**A dropped exponent would destroy the perfect-square property and the stated
factorisation simultaneously.** Five reads plus this check: verified.

## The transcription protocol that eliminates the exponent hazard by construction

> **Require that the paper's own generators satisfy the transcribed model
> identically. A single dropped exponent breaks the identity with probability
> essentially 1.**

Demonstrated three times in this campaign now: the rank-28 curve via its listed
point, the Shimura curve via its listed orbit, and #302 via all 31 witnesses. It
also yields a SELECTION CRITERION this program did not have: a paper printing
model + generators is safely transcribable; a paper printing model only is not.

## Object-level re-reading of the Kloosterman measurement

Geometric rank 15 / arithmetic 0 is not a nuisance result -- it identifies that the
WRONG OBJECT was being tracked. `NS(X_Qbar)` as an ABSTRACT lattice discards the
Galois action, which is exactly the datum arithmetic rank depends on. The correct
object is `NS(X_Qbar)` **as a Galois module**. Under that reading the Shimura curve
stops looking incidental: with `R = 0`, `NS = U + MWL`, and rank 17 over Q(t)
requires Galois to act trivially on the whole rank-19 lattice; a rational non-CM
point on `X(6,79)/<w_474>` is what buys that triviality. **The Shimura curve is the
descent bookkeeping.** That is a reusable statement, not a rationalisation.

## Tooling, better than assumed but with the decisive gap

OSCAR (Julia, open source, no licence) ships `elliptic_surface`, `kodaira_neron_model`,
`trivial_lattice`, `mordell_weil_sublattice`, **`two_neighbor_step`**,
`elliptic_parameter`, plus Hecke's `primitive_embeddings` for Kneser-Nishiyama
enumeration. So steps 0, 2 and 3 all fit on this hardware in hours to days.

**The gap:** OSCAR requires the generic fibre AND the Mordell-Weil generators as
INPUT -- it is a verification and transformation tool, not a discovery tool.
**Nothing public implements "lattice data -> explicit Weierstrass family over a
one-dimensional moduli curve"** -- Elkies' p-adic-Newton + LLL moduli deformation.
That is the whole of step 1, its cost is `p^d` in an unmeasured free-parameter
count `d`, and it must be written from a 2007 lecture-note sketch.

## Verdict

Rank >= 32 over Q needs either the author's cooperation or compute and expertise
this program does not have. **The highest-value action is emailing Elkies** -- the
formulas existed in 2006, he offered to post them, and Dujella's "personal
communication" citations show he shares on request. That is a human action this
program cannot take.

The mathematics is NOT declared closed. What is closed, each with a named
obstruction: C2 via elliptic K3s (proven ceiling); reconstruction from the moduli
point (level-79 structure unpublished); high-geometric-rank substitution (descent,
measured here).

---

# Addendum: Kihara rank-14 is PAYWALLED, and the substitute lane closes too

The scoping named Kihara, *On an elliptic curve over Q(t) of rank >= 14*,
Proc. Japan Acad. Ser. A 77 (2001) 50-51, DOI 10.3792/pjaa.77.50, as the best
remaining substitute and listed it as Open Access. **That listing is wrong.**

- The Project Euclid `.full` page shows title, author and abstract only, then
  login and subscription prompts. Verbatim: access "requires either an
  institutional subscription or individual purchase".
- The direct download endpoint returns a **PDF encrypted with the Standard
  security handler** (`/Encrypt` present, `/Filter /Standard`). Its streams are
  not zlib-readable; 32 FlateDecode streams decompress to nothing without the
  decryption key.

**I did not attempt to decrypt it, and the cached copy was deleted.** The paper
is paywalled copyrighted work; circumventing an access control to read it is not
something this program will do to complete a task, and whether an empty-password
trick would succeed technically is beside the point.

## Consequence

The substitute lane is blocked by access, not by mathematics. Standing:

- Kihara rank 14 over Q(t): **paywalled**, model and generators unread.
- Mestre rank 14: citation **unknown**, never retrieved.
- Nagao rank 13 over Q(T): access status **contradictory** in retrieval; and it
  is the paper whose exponents this program's tooling has already mangled twice.
- Kloosterman geometric 15: **measured arithmetic rank 0**, dead as a vehicle.

So this program still holds **no verified explicit high-rank family over Q(t)**,
and the cheapest route to one now runs through a library subscription rather
than through any computation.

None of this moves the objective. Even a clean rank-14 family sits **18 rungs
below rank 32** and four below the Q(t) record.
