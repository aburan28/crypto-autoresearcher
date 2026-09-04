# Coordinator rulings — backlog design, wave 1

Design-time rulings on questions the designing coordinators escalated rather
than deciding silently. Each was verified against the primary record before
ruling; none is a rubber stamp. These bind the approval decision that will
follow; they are not themselves approvals.

## R1. Question reassignment for the Shor-on-ECDLP cost assembly — CONFIRMED

`IDEA-20260815-1570fe` carries `question_id: RQ-QALG-457b41`. The designing
coordinator filed `H-ICEX-4b2e19` under `RQ-QRE-6dba8c` instead and disclosed
the move. Verified and confirmed:

- `RQ-QALG-457b41` has `curve_families: []`, `field_types: [module lattices
  over cyclotomic polynomial rings (Module-LWE, Module-SVP)]` and `bit_sizes:
  [ML-KEM-512, ML-KEM-768, ML-KEM-1024]`. Its constraints forbid a cost figure
  transferring in or out. An ECDLP quantum cost assembly cannot be filed there.
- `RQ-QRE-6dba8c` scope reads: "RSA-2048 factoring and 256-bit prime-field
  ECDLP under Shor's algorithm; surface-code fault tolerance". That is exactly
  this pipeline.

The immutable proposal is untouched and the mismatch is disclosed in the
hypothesis and the contract. Correct handling.

## R2. EXP-ICEX-b8c865 stays HARD-BLOCKED at approval — UPHELD

`RQ-QRE-6dba8c` constraint 1: "No pipeline output is recorded before at least
two primary resource-estimation papers are filed as KN-LIT entries with their
input tables extracted."

Verified against the four cited entries. Only `KN-LIT-099` qualifies (68 lines,
full simulation table). The other three do not, on their own testimony:

- `KN-LIT-1460`, `KN-LIT-1463`: "No abstract was extractable from the first two
  pages of the local PDF; contribution recorded from the title only."
- `KN-LIT-1882`: bulk-seeded 2026-07-24, "parsed heuristically and may be
  incomplete or mis-segmented; claims are relayed from the paper's abstract
  without independent verification."

`b8c865` produces a pipeline output, so constraint 1 binds. It stays blocked
until a second primary paper is filed with its input table extracted. The
coordinator also records that its dominant term is unevaluable regardless,
since KN-LIT-099 carries no error-correction layer and states no per-run
success probability — so unblocking the constraint alone would not make the
experiment runnable.

## R3. EXP-ICEX-640aef is NOT blocked by that constraint — RULED

The coordinator flagged this as a judgement call rather than deciding. Ruling:
constraint 1 governs a *pipeline output*. `640aef` records no pipeline output.
It reproduces one source's closed forms against that same source's own data
points, which constraint 2 contemplates as a distinct activity: "Reproduction
is scored against the paper's own inputs, and a reproduction gap is reported
with its magnitude rather than tuned away."

A reproduction that consumes exactly one paper cannot require two papers to be
filed. Constraint 1 does not bind it. `640aef` may proceed to approval on its
own merits.

Note its design is deliberately null: it predicts sensitivity to code distance,
cycle time, error rate, distillation and connectivity is EXACTLY ZERO, because
the closed forms contain none of those. The ranking is empty by construction.
That is a real result about what the source can and cannot support, not a
failed experiment, and the approval decision should read it that way.

## Corpus-integrity observation, not a ruling

All four entries above carry `citation_verified: read`, including the three
whose own body text says the contribution was taken from the title only or
relayed without verification. The flag and the body disagree. Records are
immutable so nothing is edited here, but `citation_verified: read` cannot be
relied on as evidence that a source was actually read, and any gate that tests
it is weaker than it appears. Worth a superseding correction and a check of
whatever else that flag gates.

---

# Wave 2 rulings

## R4. EXP-ECDLP-fa2ed6 Arm S (supersingular positive control) — PERMITTED as a control

The designing coordinator stopped rather than deciding, correctly. Ruling:
the supersingular arm may run AS A CONTROL. It may not produce any claim about
supersingular curves.

`RQ-ECDLP-912694` constraint 1 reads "Ordinary curves only; supersingular and
extension-field-only maps are out of scope." Read alone that forbids the arm.
It is not alone. Constraint 4 of the same question reads "Exception cells are
controls and cannot be used as unqualified falsification evidence" — the
question explicitly contemplates cells outside its scope serving as controls,
and bounds what may be concluded from them rather than forbidding them. Its own
`scope.curve_families` confirms the reading: the third entry is
"extension-field special-j controls where the named automorphism is not
F_p-rational", an out-of-family object admitted precisely because it is a
control.

So constraint 1 bounds the CLAIM SPACE, not the control space. A control is not
a claim: running a supersingular curve to show the instrument can return
delta != 1 asserts nothing about supersingular curves, it establishes that the
measurement is capable of a negative at all.

The alternative is worse and is the reason this matters. Without the arm,
"delta = 1 identically for ordinary curves" is measured by an instrument never
shown able to return anything else, which makes it an unfalsifiable constant
rather than a result. That is the vacuous-instrument failure mode, and
GOAL-ENDO-001 completion criterion C4 forbids it in terms: "Every instrument
used to support any conclusion has passed both directions of its
RQ-INSTR-f8faa0 control: it detects a planted signal and it rejects a matched
null."

Binding conditions on the arm:
1. It is labelled a control everywhere it appears, in the contract and in any
   evidence record that cites it.
2. No record may state a result about supersingular curves from it. Its only
   admissible reading is instrument dynamic range.
3. The ordinary-curve conclusion remains scoped to ordinary curves, and cites
   the arm only as evidence that the instrument could have returned otherwise.
4. If the arm does NOT return delta != 1, that is an instrument failure and
   triggers pause condition P1, not a finding about curves.

The coordinator's fallback — stop at S0 and report DERIVATION-ONLY with the
ordinary arm "unfalsified, never a verified negative" — was the right design
for a refusal, and stands as the behaviour if the arm cannot be run for some
other reason.

## R5. Approval-time flags carried forward from wave 2

Not rulings — open items the designing coordinators surfaced that the approval
decision must resolve. Recorded here so they are not lost between design and
approval.

1. **P1 is inherited, not native (EXP-ECDLP-fa2ed6).** Ruling R4's binding
   condition 4 routes a control failure to pause condition P1, which belongs to
   GOAL-ENDO-001. The contract's question, RQ-ECDLP-912694, has no pause
   conditions of its own — verified: the record has no `pause_conditions` key
   and no pause/goal keys at all. So if this contract is ever dispatched under a
   goal other than GOAL-ENDO-001, BC4's stop has no home and must be given one
   before approval. The designing coordinator recorded this in a
   `citation_scope_note` rather than letting the contract imply the question
   imposes P1, which is right.

2. **Label collision on "R4" (H-ECDLP-66d6fc).** That hypothesis already uses
   R1-R4 for its own four statements, and its own R4 is an unrelated
   ramified-prime scope asymmetry. Ruling R4 is always written "ruling R4" in
   the records; the hypothesis statements were deliberately NOT renumbered
   because the paired contract references them. Read carefully at approval.

3. **Two distinct failure paths must not be collapsed (EXP-ECDLP-fa2ed6).** A
   control that RUNS and returns delta = 1 is an instrument failure under P1,
   and the ordinary enumeration becomes `attempted_and_inconclusive`. A control
   that NEVER RAN is a derivation-only stop, and the ordinary arm is
   `unfalsified` with the arm withdrawn. Both refuse a verified negative, but
   they are different dispositions and an executor could easily merge them.

4. **Unverifiable input dependency (EXP-ECDLP-797b5c).** It consumes post-merge
   NFS matrices at three sizes for two problems that it does not produce, and
   their existence was not verified. Recorded as a blocking precondition: if
   they do not exist the contract cannot run, and that is an infrastructure
   stop, never a result.

## The recurring failure mode this run has now found four times

Four independent designing coordinators, working from different batches with no
contact, each found a pre-registered discriminator that could not fire:

- the pfdr-battery-20260904 round's null band, width zero by construction
  (box(E2) equalled the realised support at every s);
- IDEA-20260829-66a876's factor-4 band over a 6-bit ladder, against a
  hypothesis that moves the ratio by 2x across that span;
- IDEA-20260901-a31b94's time-axis dominance, identically zero on the whole
  range [0, 1/3] its own input is asserted over;
- IDEA-20260830-3c0861's incumbent sign-valued gate, width zero at n = 2.

This is not four coincidences. Pre-registering a band without computing what
the alternative hypothesis actually does to it produces a discriminator that
looks rigorous and cannot fail. Every contract in this backlog now carries a
band-non-degeneracy check, several of them blocking before execution. That
check should become standing practice at approval, not a per-batch nicety.

---

# Wave 3 findings

## The rho baseline constant is ambiguous by sqrt(2), and every ECDLP comparison rests on it

Two knowledge entries contradict each other about what 0.886 means. Verified
verbatim:

- `KN-TECH-006` line 7: "expected ~0.886*sqrt(n) group operations serial";
  line 20: "Negation and other cheap automorphisms give a FURTHER
  constant-factor speedup."
- `KN-TECH-018` lines 25-26: charges against KN-TECH-006 that the convention
  "0.886*sqrt(n) with negation" ALREADY INCLUDES the sqrt(2) negation factor.

These cannot both hold. sqrt(pi/4) = 0.8862 is the plain birthday constant with
no automorphism factor in it; with negation the constant would be
0.8862/sqrt(2) = 0.6266. So KN-TECH-006's reading is the arithmetically
consistent one and KN-TECH-018's "already includes" is wrong — but neither
entry is edited here, because records are immutable and because the point is
not to pick by argument.

Why this is not a footnote: Pollard rho is the baseline that EVERY ECDLP claim
in this program is compared against, and this program has never measured its
constant (that gap is what IDEA-20260815-3c9919 exists to close). A sqrt(2)
ambiguity in the baseline is a sqrt(2) ambiguity in every advantage claim made
against it. Two designs now settle it empirically rather than by citation:
`EXP-ICEX-91952c` fits c over four sizes with a negation-class plant whose
forced value is exactly the 0.8862 -> 0.6267 drop, and `EXP-ICEX-c156e2` runs
rho to completion on the same instances as the competitor. Neither may quote
either entry as authority.

A related mis-citation, also verified: `IDEA-20260811-9e8791` attributes a
"sqrt(6) = 2.449 band" to KN-TECH-018. That entry states a sqrt(|Aut|) speedup
(sqrt(2) for negation, ~sqrt(2m) for order-m). sqrt(6) is a reading at
|Aut| = 6 and is recorded as a reading, not as the entry's content.

## Ten degenerate discriminators now, and six were in one batch

measurement-2 found SIX of its twelve designs unable to fire as stated. With
the four already recorded that is ten across this run. The six:

- a fingerprint injective in BOTH arms, so the statistic is 0 either way and
  the 0.05 threshold is identically zero over the whole declared range;
- a residue vector whose components are exact deterministic functions of one
  field element, so the "effective independent count" is 1 by construction and
  no alternative can move it;
- "run the same monomial order twice" as a null, which a deterministic Groebner
  engine makes width-zero by definition;
- syzygy counts recorded verbatim as functions of n alone, so between-curve
  variance is zero by construction and the curve-count formula is vacuous;
- a zero-success discriminator at T=50 where a true p=0.01 target shows zero
  successes 60.5% of the time, so it cannot separate a hard stratum from a
  uniform population;
- a twist-side character constant +1 on the whole subgroup away from 2-torsion,
  giving defect and null both 0.000 by construction; and separately, in the
  same design, a 0.15-bit decision rule against a statistic whose entire range
  at the cell of interest is 0.037 bits.

Each was repaired with a computed replacement, not a loosened threshold. Two
were declared UNDERPOWERED at reachable scale rather than shrunk: the
cryptographically interesting B = p^(1/2) cell needs about N = 1.1e8 against
the declared 1e7, and that is written into the contract.

The pattern is now unambiguous. A pre-registered band is worthless until
someone computes what the alternative hypothesis does to the statistic across
the declared range. This must be a standing approval gate.

## Layout facts worth propagating

- `RQ-SIG-001`, `H-SIG-001` and `DEC-20260717-002` live at the repository root
  of `ledger/`, not under `ledger/questions/`. Same legacy layout as
  `RQ-DREG-001`. The validator indexes 103 such frozen root-level records, so
  these are not missing.
- Goals may be sharded: `ledger/goals/GOAL-X/goal.yaml`. Two agents have now
  been misled by a files-only listing.

Open question for the validator, raised by measurement-2 and not yet checked:
whether `validate_ledger.py` resolves a `question_id` pointing at a legacy
root-level path.

## R6. EXP-PFDR-9187e7 stays BLOCKED — UPHELD

`RQ-ICEX-001` constraint 1, verbatim: "Blocked until GOAL-SDEG-001,
GOAL-MONO-001, and GOAL-RELN-001 each have a committed protocol or scoped
measurement decision."

Verified: GOAL-SDEG-001 `active`, GOAL-RELN-001 `active`, **GOAL-MONO-001
`paused`**. A paused goal has not produced a committed protocol or a scoped
measurement decision, so the condition is not discharged and the block stands.
The contract may not be approved until it is. Lifting it requires either the
missing protocol/decision or a versioned `protocol_amendment` to the question —
not a coordinator's say-so at approval time.

## R7. EXP-PFDR-ccae87's supersingular control is REFUSED — and this is NOT R4

Ruling R4 permitted a supersingular arm as a control under RQ-ECDLP-912694.
This one is refused under RQ-JINV-8fc13a, and the difference is textual, not a
change of mind.

R4 turned on RQ-ECDLP-912694 constraint 4, "Exception cells are controls and
cannot be used as unqualified falsification evidence" — the question itself
contemplating out-of-scope cells as controls and bounding what they may
conclude. RQ-JINV-8fc13a has no such clause. What it has instead is a scope
that ENUMERATES its permitted null objects as a curve family in its own right:
"matched random-curve null objects at the same p", alongside toy ordinary
prime-field curves and CM curves including j=0 and j=1728. Supersingular is not
among them. A question that lists its own nulls has already answered which
out-of-family objects it admits, and reading a further one in would be
substituting my judgement for the question's.

So the arm is refused. The designing coordinator's fallback stands and was
correctly built: the request was declared non-blocking, the k=1
embedding-degree control carries the instrument-validation load alone, and the
report must say so explicitly.

If the supersingular control is genuinely needed here, that is a scope
amendment to RQ-JINV-8fc13a — a separate, versioned act — not something to
route in through a contract.

## R8. My own handoff mislabelled the field for part of mechanism-2 — CORRECTION

The handoffs describe all 131 as "untested prime-field ECDLP proposals". For
this batch that is wrong, and the designing coordinator caught it. Verified by
direct read: IDEA-20260829-57b1eb and IDEA-20260829-fa8235 both concern
ordinary binary curves over F_{2^n} with Weil descent to GF(2);
IDEA-20260828-d91efa is boolean/GF(2) descent (its text uses "boolean" five
times).

The error is mine: the worklist filter selected on ECDLP-relevant vocabulary
and I labelled the whole set prime-field without checking each record's actual
field. The coordinator wrote each scope statement to the ACTUAL field rather
than to my label, which is the right resolution — the contract is bound by the
object it studies, not by the handoff's summary of it.

No other batch is known to be affected, but the same filter produced all
thirteen handoffs, so field labels elsewhere in this backlog should be read as
provisional and checked per record at approval.

---

# Wave 4: the degeneracy found inside a repair

The 33rd degenerate discriminator of this run is the most instructive, because
it was in a FIX, not in a source proposal.

algorithm-1 had wrongly reported GOAL-MONO-001 as having no ledger record and
was sent back. Its own diagnosis of the error, now written into
H-ECDLP-a0d3ea: an absence claim requires a check that could have found the
thing, and a listing that cannot show directories cannot support "no record
exists". That is the second time this layout caught an agent despite an
explicit warning in the brief.

Reading the record then falsified the repair itself. The goal's `next_action`
points at DEC-20260810-2f86db, which rests on EV-MONO-a0a89c OBS-5. Verified
here by direct read: OBS-5 records "SPLITS COMPLETELY" with "193/193 split" at
m=4 over F_211, establishing unconditionally that on the factor-base locus
every root of S_m lies in F_p.

The consequence is fatal to the repaired design. A true factor-base member
forces every character in the C_2^{m-2} tower trivial, so the filter can never
reject one. Sensitivity is forced to exactly 1.000 and the selectivity lift to
~2^{m-2}. The repaired band — null [0.97, 1.03] against a hypothesised >= 1.30
with a planted 1.50 — was built to detect an alternative that is a COMMITTED
THEOREM. Running it would have re-measured OBS-5 at experiment cost and
reported a known result as a finding.

The second repair splits along the line OBS-5 actually draws:
- member side -> forced-value instrument checks, explicitly not evidence;
- NON-member false-positive rate -> primary metric, since it is the one
  quantity OBS-5 does not settle (predicted 2^-(m-2) = 0.250 at m=4; s.e.
  0.0014 at 100k candidates makes a +/-0.010 band ~7 sigma);
- charged operation ratio -> decisional, because a perfectly sensitive filter
  whose ceiling is removing a 1-2^{-(m-2)} fraction can still fail to pay.

Both degeneracies are retained in the contract's `band_non_degeneracy` rather
than dropped, so the history is auditable.

## What this says about the band-non-degeneracy check

Thirty-three failures across thirteen batches, at least four of them forced by
algebra rather than by parameter choice, and now one inside a repair written by
an agent that had already internalised the rule. The check is not a nicety to
apply once at design time. It has to be re-run against every revision, and it
has to be run against the CORRECTED design, not only the original.

A standing prohibition verified verbatim in GOAL-MONO-001 is also now carried
into the contract with its scope made explicit, so a reviewer need not guess:
"DO NOT COMMISSION AN m >= 4 CENSUS IN THAT INSTRUMENT'S FORM, EVER" targets a
census that samples the base uniformly and reads Frobenius cycle type. The
contract does neither — it fixes m-2 coordinates at factor-base elements and
reports a rate and an operation count — and an invalidation rule forbids drift
into the banned form.
