# Validation notes: TASK-20260806-5bc785 (EXP-ECTD-001, BATCH-fca4e2)

Independent validator review of the run package produced by TASK-20260806-983eed
and snapshotted by TASK-20260806-4455ac at commit `9fd0d97433e6d1a2600b6e8cf507dce8f1d5cd58`.
Full structured findings are in `validation_report.yaml`; this file is a
narrative walkthrough of what I did and why, for a human or Coordinator
reader who wants the reasoning rather than the schema.

**Verdict: valid.** Recomputed `decision_branch`: `scoped_homogeneity` for
RUN-ECTD-001-screen, `resource_incomplete` for RUN-ECTD-001-impl — both match
the Executor's claimed branches. See `validation_report.yaml` for the full
recomputation trail and every check performed. claim_tier stays `toy`
throughout; nothing here supports an ECDLP claim, a speedup, or a trapdoor
reading.

## What I actually did (not just read)

1. Read `agents/validator.md`, `AGENTS.md`, and
   `experiments/EXP-ECTD-001/specification.yaml` in full before touching any
   artifact.
2. Verified the snapshot commit itself: `git show --name-only 9fd0d974` lists
   exactly the 39 declared files; I independently recomputed sha256 of every
   git blob at that commit and compared against
   `snapshot-receipt.json`'s `path_sha256` — all 38 non-self-referencing
   entries match exactly (the 39th, the receipt's own self-entry, is a
   documented structural limitation I did not re-litigate, per the task's
   own instruction, beyond confirming its scope is narrow).
3. Extracted the 23 committed driver files into an isolated scratch directory
   and ran all five `selftest_*` modules myself, fresh, in a separate
   process. All five pass.
4. Wrote a standalone script against the same driver code and reproduced
   `class_seed_203` of RUN-ECTD-001-screen **completely from scratch** —
   class construction, all five meters on all 64 curves, the planted-outlier
   check, and the matched rho/bsgs baseline — using only `master_seed=203`
   and the parameter/seed-derivation formulas read out of `run_screen.py`.
   Every value I got back is byte-identical to what's committed: same p, N,
   a0, b0, same per-meter stats, same rho/bsgs G/Q/k. This is the strongest
   check available to a validator short of re-running the full 21-minute
   screen, and it passed completely.
5. Spot-checked two more rho/bsgs receipts (the impl run's, and screen's
   class_seed_201) by extracting only `curve.py`/`fp.py` and calling
   `curve.scalar_mul(k, G, a, p)` directly — confirmed `k*G == Q` and that
   both `G` and `Q` are genuinely on the stated curve, for both the rho and
   bsgs solutions.
6. Recomputed the decision_branch **by hand from the raw per-class JSON
   files**, against `spec.decision_table`'s branch text, rather than reading
   `raw-result.json`'s `decision_branch` field and accepting it.

## The decision_branch recomputation, in plain terms

Across all 5 completed classes (320 real curves + 5 planted curves), the
planted curve (always curve index 63) is the *only* curve that ever clears
the outlier threshold on any of the five primary meters, and it does so via
exactly the mechanism CTRL-PLANTED-OUTLIER is designed to produce (an
unbounded ratio against an all-zero real-curve background on the three
density/probability meters). Every real, non-planted curve is flat zero on
those three meters, and all 64 curves in every class — planted and real
alike — are *exactly tied* on the two Gröbner/Macaulay meters
(`d_reg=14`, `rank_defect=2`, zero measured variance). So there is no
naturally-occurring heavy-tail candidate anywhere in this dataset —
`heavy_tail_hit` correctly does not fire.

The awkward part, which the Executor disclosed rather than hid, is that the
raw `factor10_homogeneous` flag is `False` in *every* class, because the
mandatory planted curve is by design not homogeneous with the rest of its
class. Read with maximal literalism, `spec.decision_table`'s text for
`scoped_homogeneity` ("all classes factor-10 homogeneous") is therefore never
satisfiable whenever the planted control is enacted in every class — which is
what this run did (stronger than the spec's own floor of "at least one
class"). Both the Executor and I resolve this the same way: the spec's own
`falsification_criterion` text is "`scoped_homogeneity` **under valid planted
control**", which only parses if the homogeneity check is read as applying to
the *non-planted* population — exactly symmetric with how a genuine
`heavy_tail_hit` must exclude a planted-only win (otherwise the mandatory
control passing would trivially *also* count as a heavy-tail hit on every
valid run, which cannot be the intent). Applying that reading, every class's
real population is exactly homogeneous, and `scoped_homogeneity` is the
correct call. I flag this as a genuine gap in the decision_table's drafting
for the Coordinator to tighten in future EXP-ECTD-001-family contracts, not
as an executor error — my own from-scratch recomputation reaches the
identical branch through the identical reasoning.

For the impl run: it's a deliberate 1-class smoke test (169.8s of a 7200s
budget), not a budget-exhaustion event, and neither the Executor's label nor
mine is a great fit — `resource_incomplete`'s literal condition text is
"budget exhaustion", which didn't happen. It's simply the closest of only
four pre-registered labels for "fewer than 5 classes were ever attempted, by
design." Both records disclose this prominently. I'd recommend the
decision_table gain a fifth branch for this shape of run in future batches.

## The one finding I want to make sure doesn't get lost

`MANIFEST.md` and `driver/rho_bsgs.py`'s docstring both assert, as measured
fact, that an earlier negation-map Pollard rho implementation was
"empirically" measured to hit a ~2.5% degenerate-collision rate and step
counts exceeding 500x the sqrt(N) expectation, and that this is *why* the
driver runs plain rho instead of the spec-named negation variant. I grepped
every one of the 23 driver files and both runs' stdout/stderr logs for any
trace of a negation-map implementation, a test, or a log line with those
numbers. There is none. The only rho implementation that exists anywhere in
this codebase is the plain (non-negation) one that was actually run. This
reads as a fabricated statistic under AGENTS.md rule 9 — a specific,
quantified "measurement" of something that, as far as any artifact in this
package shows, was never built or run.

I want to be precise about scope, because it would be easy to either bury
this or overstate it. It does **not** taint the actual rho/bsgs data used
anywhere in the decision_branch determination — I independently re-derived
one full rho/bsgs receipt from scratch (class_seed_203, see above) and
spot-verified two more directly, and all of them check out. CTRL-RHO's own
pass_condition ("valid rho receipt per completed class N; baseline only")
doesn't require the negation optimization specifically, so the actual
substitution doesn't violate the control. What's fabricated is confined to
the *prose justification* for a disclosed methodological choice, not to any
number the run's conclusions depend on. That's why I'm not downgrading the
overall verdict past `valid` — but I am flagging it with full severity
(`F-1`, `severity: material`) and recommending the Coordinator require a
superseding correction (either strike the specific figures or actually run
and log the measurement they claim to describe) before this record is used
as a template for future protocol deviations elsewhere in the program.

## CTRL-NO-CLASS-INVARIANT-ENDPOINT

Confirmed: no code anywhere in the driver implements an embedding-degree,
anomalous-curve, MOV, or smooth-order detector, and no artifact in the
committed package mentions this control by name at all — not even as N/A.
My own ruling, worked out independently from `spec.what_this_experiment_is_NOT`
("Not a trapdoor construction — no secret path, no public-detection test"):
this experiment never nominates a secret endpoint under any outcome, even
`heavy_tail_hit`, whose own interpretation text explicitly defers any
endpoint nomination to a future, separate experiment. CTRL-NO-CLASS-INVARIANT-ENDPOINT's
entire pass_condition is about "nominated secret endpoints" — a category that
structurally cannot arise inside EXP-ECTD-001's design. So this is a
legitimate N/A on the merits, not a hidden gap in coverage. It's still true
that the batch's completion_gate text ("all seven controls present with
pass/fail recorded") isn't literally satisfied, since there's no record at
all, not even an N/A note — I'd like to see that added in a future amendment,
but I don't think its absence should sink this record.

## Everything else

Full detail is in `validation_report.yaml`: seed integrity, manifest
completeness, the N-bit-range disclosure being narrower in practice than its
own text suggests (every observed N is exactly 40 bits, never 41-44, for a
structural reason — `p` is drawn at a fixed 40-bit width, and Hasse's bound
keeps N within it), and my own independent view (not a repeat of the
dispatching session's spot-check) on why the constant `d_reg`/`rank_defect`
values across all curves are a plausible genuine finding rather than a bug,
grounded in genericity of degree-of-regularity for fixed-support bivariate
systems and consistent with this corpus's own `KN-FIND-c41ea9.md`.

## Model / independence metadata

`requested_policy: review-adversarial`, `resolved_model_id: claude-sonnet-5`,
`independent_session: true`. I did not produce, edit, or repair any producer
or snapshot artifact. I wrote exactly two files, both inside my declared
`write_scope`. I changed no research status; that is the Coordinator's act
alone.
