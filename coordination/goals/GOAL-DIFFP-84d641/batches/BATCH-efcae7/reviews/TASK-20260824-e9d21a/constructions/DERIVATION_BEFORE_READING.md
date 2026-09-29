# INDEPENDENT DERIVATION -- written BEFORE opening
# coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-efcae7/tasks/TASK-20260824-9a489e
# Sources used so far: harness/diffpath/{pathobj,adjudicator,primitives}.py,
# harness/diffpath/controlpower.py (lines 230-460, 1075-1200), review-plan.yaml,
# assignment, task card, handoff, AGENTS.md. NOTHING from the producer directory.
# Timestamp of writing: before any read under tasks/TASK-20260824-9a489e.

## (1) J11 -- the SHA-1 flag confound, derived from the committed code alone

serialize() puts ("in_linearized_code", bool) in the key for every sha1 object.
plant_from_pair sets it = P.sha1_in_linearized_code(full_dv).
P.sha1_in_linearized_code(w) == (sha1_expand(w[:16], len(w)) == w).
perturb_message_difference() RECOMPUTES it on the perturbed dv.

The expansion is GF(2)-linear. Write dv' = dv XOR e, e = indicator of the k
flipped bit positions. Then
   expand(dv'[:16]) = expand(dv[:16]) XOR expand(e[:16]).
If the source is in code, expand(dv[:16]) = dv, so
   in_code(dv')  <=>  dv XOR expand(e[:16]) == dv XOR e  <=>  expand(e[:16]) == e
i.e. IFF THE PERTURBATION VECTOR IS ITSELF A CODEWORD.

DERIVED PREDICTION (mine, before reading):
 P-RT-1  For a source with in_linearized_code True, the flag moves at EVERY
         k >= 1 unless e is a nonzero codeword. e has weight <= 16 for
         k in {1,2,4,8,16}. A nonzero seed expands to a tail that cannot be
         all-zero (the kernel of seed -> tail is trivial: run the recursion
         backwards from t=31 down and every seed word is forced to 0), so any
         codeword with support inside the 16 seed words is impossible, and any
         codeword at all has tail weight bounded below by the code's minimum
         distance, which is far above 16 for the 80-word SHA-1 expansion code.
         THEREFORE: the flag moves on essentially every k >= 1 draw, INCLUDING
         k = 1, and for the deterministic draw (positions = range(k), all inside
         word 0, e[:16] != 0 with an all-zero tail) it moves with CERTAINTY.
 P-RT-2  CONSEQUENCE. The confound is TOTAL, not partial. On sha1 the family-(d)
         perturbation moves TWO key components at once -- message_difference and
         in_linearized_code -- at every k. So "family (d) probes the message
         difference" is FALSE ON SHA-1 as a matter of the key's structure, and a
         per-k report will show the flag co-moving at every k rather than only at
         large k.
 P-RT-3  It does NOT bite on md5 (no flag in the md5 key) and does NOT bite on a
         source whose in_linearized_code is already False (family (c) draws):
         there the flag stays False and the perturbation is clean.
 P-RT-4  SUSPECTED DEFECT, independent of the above: plant_from_pair computes the
         flag on the FULL 80-word dv while perturb_message_difference recomputes
         it on obj.dv, which is the step_range SLICE. If any sha1 census entry has
         step_range != (0,79) the two are computed on different objects and the
         recomputation is not the committed predicate applied to the same thing.
         TO BE CHECKED against the census.

## (2) J13 -- was the detection verdict guaranteed in advance?

Row of interest: drop_set = {"message_difference"}.
Key components after projection: primitive, length, step_delta,
[signed_representation if E4 not in gens], [block_index if E6 not in gens],
[step_start if E1 not in gens], and for sha1 in_linearized_code.

PERTURBATION_DECLARATION holds fixed: step_delta, step_delta_signed, block_index,
step_range, conditions, cv/m/mp, primitive, length, and (sha1) dv_seed_window.
It recomputes delta_m_signed (md5, NOT a key component) and in_linearized_code
(sha1, A KEY COMPONENT).

DERIVED PREDICTION (mine, before reading):
 P-RT-5  MD5. After dropping message_difference EVERY remaining key component is
         held fixed by the perturbation, and orbit minimisation cannot separate
         them because it is applied to both draw and source over the same variant
         list. So the ablated canonical form of the draw EQUALS that of its own
         source entry, at every k, for every draw. Every md5 family-(d) draw
         adjudicates strict MEMBER against the message_difference-blind
         adjudicator. THE DETECTION VERDICT FOR THAT ROW IS GUARANTEED IN ADVANCE
         ON MD5 BY THE CONSTRUCTION. It is a restatement, not a power result.
 P-RT-6  SHA-1. in_linearized_code survives the projection and (P-RT-1) moves at
         every k >= 1, so the ablated adjudicator STILL REJECTS every sha1
         family-(d) draw. The sha1 arm contributes ZERO members at k >= 1 to that
         row. So on sha1 the answer to J13's question -- "could an adjudicator
         that drops message_difference still reject a family-(d) draw?" -- is
         YES, and it does so through a CORRELATED KEY COMPONENT (the flag), which
         means family (d) does not isolate the message difference on sha1 at all.
 P-RT-7  THE SPLIT IS THE FINDING. The row's DETECTED verdict is carried entirely
         by the md5 arm, where it is a tautology, while the sha1 arm shows the
         opposite thing. Neither a clean power result nor a clean tautology.

## (3) J8 -- object I expect to survive the strengthened suite

O-E (plan candidate v), instantiated: an adjudicator whose serialised key drops
message_difference FOR SHA-1 ONLY and keeps it for md5.
 P-RT-8  It passes CTL-PLANT (a coarser key can only add members, and recall is a
         member test), passes CTL-NULL (a) (md5 sighted), passes (b) and (c)
         (step_delta separates random draws from the census), and passes
         CTL-NULL-D (md5 by message_difference, sha1 by the flag). Yet it is blind
         to the primary datum of a differential characteristic on half the census.
 P-RT-9  WHERE THE SURVIVAL HAPPENS: at DETECTION_RULE in controlpower.py, which
         reads ONLY CTL-NULL-D's PRIMARY arm (Row.record -> self.nulld, populated
         only by family_d_primary with arm="primary"). The one arm that isolates
         the message difference from the flag -- perturb_by_codeword, which by
         GF(2)-linearity keeps the flag True while changing dv -- is a SUB-ARM
         reported beside the battery and is NEVER carried into the battery's
         detection rule. An instrument that fails the sub-arm still passes the
         suite as the battery scores it.
 P-RT-10 NEW, not on the floor list: the DETERMINISTIC draw uses
         positions = range(k), so for k <= 32 it only ever flips bits of WORD 0 of
         the message difference. An instrument blind to words 1..15 (md5) or
         1..79 (sha1) is invisible to the deterministic arm entirely; only the
         seeded draws can reach it. That is a property of how the flipped
         positions are chosen, i.e. exactly J11's one-thing-at-a-time mutation.
