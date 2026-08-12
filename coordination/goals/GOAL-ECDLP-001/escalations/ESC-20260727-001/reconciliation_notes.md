# ESC-20260727-001 — reconciliation notes

Companion to `ruling.yaml`. Where the ruling states dispositions, this file shows the working:
what was read, what was checked against what, and where the argument could fail.

**Scope.** Nothing here is evidence for or against ECDLP hardness. No experiment was run or
re-run. No implementation was read. Every claim below is traceable to a committed artifact.

---

## 1. First, a correction to the escalation's own premise

The escalation listed as verified fact: *"In the run manifests, inference.policy,
requested_policy, resolved_model_id, fallback_used, validity, git_commit, and dirty_tree are all
null."*

For the two manifests I was given, that is **not so**. `RUN-GGM-s1-b8` and `RUN-GGM-s1-b16` both
record:

| field | value |
|---|---|
| `code.commit` | `7ec5251ff6c23cbc26ada90ecb0fced928f84b85` |
| `code.dirty` | `false` |
| `inference.requested_policy` | `coordinator-ultra-code` |
| `inference.resolved_model_id` | `fireworks-ai/accounts/fireworks/models/glm-5p2` |
| `inference.fallback_used` | `true` |
| `result.valid` | `true` |
| `status` | `completed_valid` |
| `certificate` | `kind: none, verified: true, verifier: no-claim` |

That is substantially compliant with the artifact policy, and `certificate: none` is the
*correct* declaration for a measurement run claiming no solve. I am recording this prominently
because a ruling resting on a false premise would be worthless, and because it would be unjust
to the co-driver to let "no provenance at all" stand in the record when the provenance is
largely there and is honest about the fallback.

What is genuinely missing on those two runs: `adapter_version` is null, `dependencies` is `{}`,
`artifacts` is `{}` (though the sibling log files exist per `COMMIT_PATHS.txt`), the fallback has
no `authorization_ref`, and `EV-GGM-001.run_ids` is `[]` despite the record asserting nine runs.
Seven manifests I have not seen. TASK-20260727-001 exists to settle all of that properly.

---

## 2. The substantive core, in one page

Both of our independent reviews were written **before** this execution existed and without
either session seeing the other's output. RT-20260726-001 OBJ-01 posed a dilemma and predicted
that no single definition of "simulable" could both pass the control gate and yield the four
expected SIMULABLE verdicts. Falsification route XR-1 specified the check: *write the module's
operative predicate as one sentence and apply it to all eight subjects by hand.*

main's `raw-result.json` lets us do exactly that, using its own words.

**Under strict Shoup**, main classifies the `encoding` control NON_SIMULABLE because
"in the generic group model, elements are opaque labels; the x-coordinate is not accessible
without breaking the encoding abstraction."

**Under the structured GGM**, main classifies `jet_oracle` SIMULABLE — while stating in the same
field: *"This requires the coordinates, which are the encoding"* and *"in the strict GGM (opaque
labels), the jet data is NOT computable."* And `endomorphism_oracle` SIMULABLE — while stating:
*"in the strictest Shoup GGM (opaque labels), phi cannot be applied to a label, making it
NON-SIMULABLE."*

So the run applies one model to the controls and a different model to the subjects the
controls are supposed to license. Fix either model and apply it uniformly:

- **Strict Shoup throughout** → jet and endomorphism are NON-SIMULABLE *by main's own written
  reasoning*. Both headline closures disappear.
- **Structured GGM throughout** → coordinates are available from the encoding plus the public
  curve for *every* subject, so `x(P)` is equally a deterministic function of available data and
  the `encoding` control must come out SIMULABLE. Its frozen `expected_verdict` is
  NON-SIMULABLE and it is the positive correctness control, so the gate falls to at most 3/4 and
  the frozen `falsification_criterion` declares the test unsound — no augmented verdict may be
  reported at all.

The reported 4/4 is an artifact of the split. This is checkable on paper, needs no
re-execution, and was predicted in advance.

**Is this decisive against the co-driver's mathematics?** No, and I want to be exact about
that. It is decisive against the *claim as recorded*. It is entirely possible that a properly
frozen structured GGM, with all eight subjects re-derived under it and a control set rebuilt to
suit, yields a defensible result — perhaps even the same verdicts for jet and endomorphism, with
a re-purposed encoding control. That would be a genuine contribution. What cannot survive is the
current combination: a gate scored under one model licensing verdicts reached under another.

Also note H-GGM-001's own `assumptions` item 5 requires the model variant be *"fixed consistently
across all oracles and controls."* The execution violated an assumption of the hypothesis it
reports as supported. That is not a subtle reading; it is the assumption's plain text.

---

## 3. Three further predictions that landed

**Static overhead count (XR-2).** Predicted: *"Identical integers at all three sizes for every
subject confirm that C is a static source-text count that cannot vary with N."* Observed:
`jet=1, endomorphism=0, pure_generic=1, public_curve=0` at both 8 and 16 bits, `null` elsewhere.
The N-independence claim on which both closures rest is supported by a check that could not have
failed.

**Discrete-log witness (BO-3 / OBJ-05).** Predicted: the mandated witness cannot exist, so the
control will pass by assertion. Observed: main's `witness` field for `discrete_log` is prose
restating Shoup's bound, exhibits no encoding pair, and ends by saying the answer "depends on the
abstract group structure ... not on the encoding" — which is precisely why the mandated
encoding-pair witness is unconstructible. The control scored correct without producing the
certificate its specification requires.

**Tier escalation (OBJ-02).** Predicted: the frozen `scale_independence_note` would force the
analyst into a supra-toy assertion that `docs/claims-and-verification.md` forbids. Observed:
`EV-GGM-001` carries `claim_tier: toy` and `proof_status: derivation` while its own `boundaries`
and the decision context assert the closures are "not toy-tier." The record contradicts itself
exactly where OBJ-02 said it would. The honest form — `claim_tier: toy` **and**
`proof_status: derivation` together, closure language dropped — was available and is still
available.

---

## 4. One arithmetic point, stated carefully

`analysis.md` says the `O(log N)` and `O(B^m)` overheads are "still << sqrt(N), so no
sub-birthday advantage exists." For `O(log N)` that is correct. For `O(B^m)` it depends on `B`,
which the frozen specification never bounds — the omission RT-20260726-001 OBJ-08 flagged. Under
this program's own convention `B = ceil(sqrt(N))` (H-STR-002 `test_boundary.parameters`), `B^2`
is of order `N`, which is far *greater* than `sqrt(N)`, not far less. So that sentence is either
false or vacuous depending on a parameter nobody fixed.

To be clear about direction: this does **not** mean the incidence oracle confers a sub-birthday
advantage. Nothing suggests it does. It means the stated reason for concluding it doesn't is
unsound as written, and the oracle's own cost is one of the things the specification never
pinned down.

---

## 5. Where my own argument could fail

Listing this because a ruling that cannot be wrong is worth as little as an experiment that
cannot fail — the defect this campaign has now found three times.

1. **I read two manifests of nine.** If the other seven differ materially, parts of §1 and §3
   change. TASK-20260727-001 settles it.
2. **I did not read `simulability_test.py`.** If the module's operative predicate differs from
   the prose rationales in `raw-result.json`, my horn argument targets the wrong object. The
   rationales are the module's own output, so this seems unlikely, but it is unverified.
3. **The structured GGM might be formalizable in a way that saves the gate.** If someone defines
   it so that the curve equation is public but the *point encoding* remains opaque, jet and
   endomorphism might separate from `x(P)` after all. I could not construct such a definition —
   jet data is a function of coordinates, and coordinates are the encoding — but I would not
   call that impossible, and it is exactly what an independent reviewer should attack.
4. **My reading of horn 2 assumes the encoding control means what the specification says it
   means.** A v2 could legitimately re-purpose that control. Then horn 2 dissolves and the
   question becomes what the new control set proves.

This is why recommendation F1 is an independent rule-12 review of main's execution rather than
acceptance of this ruling. My analysis should be checked by someone who did not write it.

---

## 6. The pattern worth more than this dispute

Three consecutive designs in this program shipped a headline criterion that could not fail:

| where | criterion that could not fail |
|---|---|
| EXP-IC-001 (REV-20260726-003 BO-5) | tautological `S*T^2` success conjunct |
| EXP-GGM-001 (REV-20260726-005 BO-2/BO-7, RT OBJ-04) | 4/4 control gate passed by a content-free classifier; and now, in execution, a growth check comparing a constant to itself |
| the archive rule itself (BATCH-006 close-out) | the post-commit verifier checks only paths the archive itself declared, so a batch's own dispatch queue was invisible to it |

And now a fourth instance of the same family: an execution that could not produce a costly
negative, because the gate that was supposed to stop it was scored under a different model than
the verdicts it licensed.

The common shape is a check whose scope is set by the same artifact it is meant to police. The
durable fixes are cheap and structural, not clever: freeze the definition before the subjects;
seal expected verdicts away from the implementer; require every gate to have a control on both
sides of every axis; make each archive claim the queue that governs it; and route every claim
that crosses a tier boundary to a non-originating reviewer *before* it is archived, not after
it is disputed.

If this escalation produces only one durable change, that should be it — not a verdict about
jets.

---

## 7. What is owed to the co-driver's work

It executed, it kept complete run directories with logs and environment, it recorded its
fallback honestly without claiming equivalence, it wrote a real human-readable analysis (which
our branch does not have for this question), and it stated its most damaging boundary in its own
evidence record: *"Under the strictest GGM, jet and endomorphism would be NON-SIMULABLE."*
That sentence is the reason this ruling could be written from main's own artifacts, and putting
it there was the right call.

The failure is procedural, and it is a failure the harness invited: nothing mechanically
prevented an unapproved specification from being executed and archived as a closure result. That
gap belongs to the system, not to the agent that walked through it.
