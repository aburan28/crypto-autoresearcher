# BATCH-029 snapshot: an error in my own approval, found by the executor

## What the executor caught (OBS-1)

`A1-PLATEAU` fired: D8 = 0.0043859313845401315, above the frozen plateau edge
0.003214927 and **2.75x the one-sample critical value** 0.001593354. Under the
calibration the contract adopted, the separation did NOT decay under an 8x null.

But the executor also reported, unprompted, that **D8 is LESS THAN the
unequal-size two-sample critical value 0.004780061 that the contract itself
names.** So the claim -- made in the contract's own reasoning and REPEATED BY ME
IN THE APPROVAL RECORD -- that a PLATEAU outcome "rejects under BOTH
calibrations" is NOT exact. It fails throughout the interval
[0.003214927, 0.004780061), and this run's value falls inside it.

I wrote in APPROVAL-EXP-SMTH-e932e8.yaml:

> "ARM 1 IS CALIBRATION-ROBUST BY CONSTRUCTION, which is the property that makes
> it decisive. At m8 the one-sample critical value is 0.001593 and the
> unequal-size two-sample value is 0.004780, so PLATEAU rejects under BOTH
> readings and DECAY not-rejects under BOTH."

Both numbers are right there in my own sentence and I did not notice that the
plateau EDGE sits below the two-sample CRITICAL VALUE, leaving a band where the
label fires and the two-sample test does not reject. I approved a
robustness claim I had the arithmetic to falsify in front of me.

## What the executor did about it, which was exactly right

Applied the frozen band as written, labelled the outcome A1-PLATEAU, reported
the raw quantity and the gap explicitly, adjusted nothing, reached for no
tiebreaker, re-scored nothing, and referred adjudication to the Reviewer and
Coordinator. That is the behaviour the pre-registration exists to produce: a
producer that finds its own contract imprecise reports the imprecision rather
than resolving it in whichever direction the numbers happen to favour.

## What this does and does not mean

IT DOES NOT MEAN ARM 1 IS VOID. Under the calibration the contract DECIDED IN
ADVANCE -- one-sample, chosen deliberately as the stricter reading, on the stated
ground that the treatment arm is exhaustive and only the null is random -- D8
exceeds the critical value by 2.75x and the outcome is a rejection. The
contract's chosen framing is unambiguous and this run rejects under it.

WHAT IS DAMAGED IS THE ROBUSTNESS CLAIM, not the result. The reviewers must rule
on whether the one-sample framing is correct, because for this value it now
matters -- which is precisely the question BATCH-028 left open and which ARM 1
was supposed to make moot. It did not make it moot.

## My probe, for the record

My coordinator-side probe read D8 = 0.003633; this run read 0.0043859. Both land
in PLATEAU, but they are NOT the same number and my probe was not reproducing
the contract's arm -- different null construction. That is a further reason the
probe carries no weight, and it is disclosed here as it was in the approval.

## Also in the package

ARM 2 returned A2-SUPPORT-NOT-DETECTED and the executor applied the
pre-committed interpretation without prompting: this does NOT clear the support
mismatch, it is an upper bound on the projection's blindness. The forbidden words
were not used. OBS-3 records a real tension for the reviewers -- the treatment
rejects against the uniform null and does not reject against its own
support-matched null, while the two nulls are indistinguishable at this n -- and
the executor offered no mechanism, which was correct.

INTEG-A passed: the treatment N-sequence reproduces BATCH-028's recorded digest
bit-exactly, so the treatment arm is provably the same fixed object.

THE APPROVAL GATE FIRED AND IS RECORDED. All three hashes agreed, the check ran
before the driver was written, and the counterfactual is stated in the manifest.
That gate is the whole reason BATCH-029 exists.
