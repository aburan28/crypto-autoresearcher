# Derivation note: the L5 measurement uses a rank LOWER bound where the argument requires an UPPER bound

Author: coordinator session, TASK-20260825-169adc, BATCH-4d5406, GOAL-ECQ-2298dc, 2026-08-25.
Status: **refutation artifact** under `docs/claims-and-verification.md` "Refutation artifacts",
tier **2 — derivation note** (a checkable argument, NOT a machine-verified proof, and NOT a
counterexample certificate). It is the artifact relied on by `DEC-20260825-a74c9e`.

**WHAT THIS NOTE IS ABOUT AND WHAT IT IS NOT ABOUT.** It refutes an INFERENCE RULE used at lane
L5 of `DEC-20260824-b7557b`. It does **not** refute the conclusion that lane drew. The arithmetic
Mordell-Weil rank over `Q(t)` of the Kloosterman surface may well be 0; nothing here says
otherwise. What is established is that the recorded measurement **cannot support that conclusion,
or any upper bound at all**, and therefore cannot support the object-class closure L5 asserts.

**IT IS ALSO NOT PROGRESS TOWARD RANK 32 OVER Q.** Nothing in this note produces a curve, a point,
a family, or a rank. It is an audit of a bound's direction. See §7.

---

## 1. The inference as recorded

`DEC-20260824-b7557b` lane L5, fields `quantity` and `value`, verbatim in substance:

> quantity: Arithmetic Mordell-Weil rank over Q(t), bounded ABOVE by the minimum specialisation
> rank (Silverman gives rank E_t(Q) >= rank E(Q(t)) for all but finitely many t), against the
> stated geometric rank.
>
> value: Geometric 15, arithmetic 0. Over 31 specialisations ... the **certified rank lower
> bounds** ranged 0 to 2 with MINIMUM 0 ... The 0 is an upper bound on the generic rank read off a
> 31-point sample, not a proof of generic rank 0.

Its source, `coordination/goals/GOAL-ECQ-2298dc/inputs/RETRIEVAL-elkies-rank17.md` addendum 2:

> **Method:** Silverman specialisation gives `rank E_t(Q) >= rank E(Q(t))` for all but finitely
> many t, so the MINIMUM specialisation rank bounds the generic rank from above. 31
> specialisations evaluated ...
>
> **Result:** rank lower bounds ranged **0 to 2**, minimum **0**. ... So the generic rank over
> Q(t) is at most 0 on this sample.

## 2. The derivation

Let `E/Q(t)` be non-isotrivial and let `s_t : E(Q(t)) -> E_t(Q)` be the specialisation
homomorphism. Silverman's specialisation theorem: `s_t` is injective for all but finitely many
`t in Q`. Hence for all admissible `t`,

    (A)   rank E(Q(t))  <=  rank E_t(Q).

For each `t`, let `l_t` and `u_t` be a certified LOWER and a certified UPPER bound on the
specialisation rank, so that

    (B)   l_t  <=  rank E_t(Q)  <=  u_t.

Combining (A) with the RIGHT half of (B) gives the usable statement

    (C)   rank E(Q(t))  <=  min over admissible t of  u_t.

**(C) consumes `u_t`. It cannot be run on `l_t`.** Combining (A) with the LEFT half of (B) gives

          rank E(Q(t))  <=  rank E_t(Q)     and     l_t <= rank E_t(Q),

two lower-bounding statements about the same unbounded quantity `rank E_t(Q)`. Their conjunction
has no consequence for `rank E(Q(t))` whatsoever. Concretely, `l_t = 0` for every `t` in any finite
sample is consistent with `rank E(Q(t)) = 15`: take any surface of arithmetic rank 15 whose
generators specialise, at every sampled `t`, to points outside whatever region the instrument
inspected. Nothing in `l_t = 0` excludes that.

**Therefore the sentence "the MINIMUM specialisation rank bounds the generic rank from above" is
true of `min u_t` and false of `min l_t`, and the recorded measurement produced `min l_t`.**
The decision's own hedge — "The 0 is an upper bound on the generic rank read off a 31-point sample"
— is itself the error rather than a caveat on it: the 0 is not an upper bound on anything.

## 3. The instrument produced `l_t`, by construction

The certifier used in this campaign exhibits a point set and certifies joint independence via the
`F_l`-rank of the reduction map over many good primes together with a torsion bound
(`DEC-20260824-5246b7`; `coordination/goals/GOAL-ECQ-2298dc/tasks/TASK-20260824-02c3e4/report.md`
sections 3-5). It contains no descent, no Selmer-group computation, and no analytic input. An
instrument of that design can only ever certify that the rank is **at least** the rank of the
exhibited independent set. Every number it reports is an `l_t`. The v2 run set records this
explicitly: `maximum certified rank lower bound 0` with `certificate_kind: none` on every part-C
row. So the direction error at §2 is not an accident of wording; the available instrument could
not have produced `u_t`.

## 4. Proves-too-much control, run-backed inside this same campaign

The inference rule of §1 is refuted by applying it to an object of known large rank.

- ICARM curve no. 302 carries a claimed rank `>= 31`, and this program independently certified 31
  jointly independent points on it in exact arithmetic (`RUN-ECQ-f5af06-v2-A-certify`; A-FULL
  `k = 31` of 31, `F_2`-rank 31 over 45 good primes, torsion bound 1). So `rank E(Q) >= 31` for
  that curve is established **by this program's own committed run**.
- Those 31 generators have x-numerators of about **33 decimal digits**
  (`DEC-20260824-b7557b` L1 `obstruction`).
- The only x-coordinate box this campaign ever froze reaches **8 decimal digits** for `w = 1`, and
  was exhausted at `95 899 629 / 95 899 629 = 100 percent` coverage with **0** rank-increasing hits
  (`RUN-ECQ-f5af06-v2-B-extension`).

Hence: a from-scratch application of "search the frozen box, certify what you find" to curve
no. 302 — that is, exactly the L5 procedure, run on a curve whose rank is known to this program to
be at least 31 — is **provably incapable of certifying rank above 0 over that box**, because every
one of the 31 generators lies outside it by about 25 decimal orders of magnitude. If the L5
inference rule were sound, it would conclude from that null that no. 302 has rank at most 0. Its
rank is at least 31.

The gap between `l` and the truth is therefore **at least 31 on a curve inside this campaign**.
This is the strongest checkable form the refutation admits here: a counterexample to the inference
rule, backed by committed run records, though not a counterexample certificate to L5's conclusion.

## 5. Three further independent defects in L5's basis

**D2 — the search bound is not recorded anywhere.** There is no committed run record for the 31
specialisations (`DEC-20260824-b7557b` L5 `basis_limitation`, stated by the decision itself). The
x-numerator bound, the denominators searched, the prime set, the torsion bound and the per-`t`
timings are therefore absent from committed state. **A null search result whose search bound is not
recorded is uninterpretable in principle**: its discriminating power is the probability that a
generator lies inside the inspected region, and that quantity cannot even be formed. Order of
magnitude, declared as illustration and NOT as measurement: the transcribed model's coefficients
have degree 8 in `t`, so a generic generator with x-coordinate of degree 4 to 8 in `t` specialises
at `t = 25` to an x-numerator of order `25^8 ~ 1.5e11`, i.e. 12 decimal digits — already past the
8-digit reach of the only box this campaign froze. The true degrees are unknown because the source
prints no generators (D3).

**D3 — the model fails this campaign's own admissibility criterion.** The campaign derived, and
recorded as a reusable technique, the selection criterion: *"a paper printing model AND generators
is safely transcribable; a paper printing model only is not"*
(`coordination/goals/GOAL-ECQ-2298dc/inputs/SCOPING-recomputation-lane.md`). The same campaign's
retrieval file records of the Kloosterman surface: *"No explicit generators."* The model was
obtained through tooling documented in that same file as silently dropping exponents (two reads of
one Nagao paper giving `9T + 211950` against `9T^6 + 211950`, and `396150T` against `396150T^2`),
and the file states the measurement *"should be re-run against a verified PDF before it is
cited."* It was cited. The campaign's own rule, applied to the campaign's own artifact, excludes
this model from transcription-safe use.

**D4 — scope, and an object that could not carry its own lane.** One surface supports a
class-level assertion ("*this is why 'find a surface of high geometric rank' is not a route to
32*"). Separately: the sampled surface has stated geometric rank **15**. Even under **zero**
descent loss it delivers 15, which is 17 short of the objective. **The one object measured could
not have carried the lane it was used to close**, in either direction.

## 6. The generalisation is contradicted by this campaign's own central object

L5's obstruction asserts the descent gap is "not small — it is total". Objects named in the same
decision contradict genericity of that:

- **The rank-17 elliptic K3 fibration** — the vehicle of the entire published record ladder. On
  the reading recorded in `SCOPING-recomputation-lane.md`: `R = 0`, `NS = U + MWL`, `rank NS >= 19`,
  arithmetic MW rank over `Q(t)` equal to **17**. Its geometric MW rank is then 17 or 18, so its
  descent gap is **0 or 1**. Not total; essentially absent.
- **Mestre / Kihara rank 14 and Nagao rank 13** are ARITHMETIC generic ranks over `Q(t)`, each
  carried by a surface of at least that geometric rank. Each is an object whose descent gap is
  bounded by (geometric rank minus 14, resp. 13).
- **Shioda's rank-68 surface**, whose Mordell-Weil group is defined over a field of degree
  829 440, is the opposite extreme and is a genuine instance of the obstruction — but it is a
  retrieved literature statement about one atypical highly symmetric object, not a measurement made
  here, and one extreme instance plus one defective instance do not establish a distribution.

The honest statement the evidence supports is therefore: **the geometric-to-arithmetic descent gap
is object-dependent and ranges from 0 to total.** That is precisely the reversal
`DEC-20260824-b7557b` already records in its own `obstruction.resource_check`: the right object is
`NS(X_Qbar)` **as a Galois module**, and a rational non-CM point on a moduli curve is a mechanism
that forces trivial Galois action. A decision cannot simultaneously hold that the gap is generic
and that a known mechanism selects objects where it vanishes.

## 7. What follows, and the boundary that does not move

Follows: L5's obstruction does not hold at the scope L5 asserts, and the lane returns to
**unmeasured** — not to promising.

Does not follow, and is stated so it is not inferred:

1. **No route to rank 32 over Q is opened.** The highest explicit geometric rank this program has
   retrieved is 15 (Kloosterman), 17 short of the objective even at zero descent loss. The
   surfaces that would matter — Euler characteristic `d >= 4`, where Shioda-Tate permits
   `rank MW <= 10d - 2 = 38` and so does not exclude 32 — are not in this program's hands. L5's
   real obstruction is **the same availability obstruction as L4**, not descent.
2. **Nothing here is progress toward C1**, partial credit toward it, or a reason to describe
   `GOAL-ECQ-2298dc` as advancing. C1 remains unmet and the goal remains `blocked`.
3. **The Shioda-Tate arithmetic checked, since it is load-bearing for point 1.** For an elliptic
   surface over `P^1` with `chi(O_X) = d`, `h^{1,1} = 10d` and `rank MW <= rho - 2 <= 10d - 2`.
   Anchored at both ends of what is independently known: `d = 1` gives 8, the `E_8` maximum for a
   rational elliptic surface; `d = 2` gives 18, the K3 maximum quoted in `DEC-20260824-b7557b` E4.
   Both agree, so `d = 3 -> 28` and `d = 4 -> 38` follow. The K3 ceiling that closes C2 is
   therefore correct **and is confined to `d = 2`**; it says nothing at `d >= 4`.
4. **Rank over `Q(t)` is not rank over `Q`.** It reaches `Q` only by Silverman specialisation, at
   the value actually attained.

## 8. Basis declaration

`proof_status: derivation`. §2 is a self-contained argument checkable by an independent reader.
§4 is a control backed by committed run records (`RUN-ECQ-f5af06-v2-A-certify`,
`RUN-ECQ-f5af06-v2-B-extension`) — whose figures are producer-reported and **not validated** by any
validator, red team, or Coordinator, exactly as `DEC-20260824-b7557b` limitations state; the §4
argument survives that, because it needs only that the 31 generators are large and the box is
small, and it degrades to a statement about the box's declared bounds even if the run figures are
wrong. §5 and §6 rest on committed input documents that are NOT evidence records and that no run
record backs. No claim here is `empirical_only`, and none is a machine-verified proof.
