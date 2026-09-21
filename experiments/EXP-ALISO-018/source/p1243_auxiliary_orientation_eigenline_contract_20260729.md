# Experiment Contract: Orientation-Labeled Auxiliary Principalization

Date: 2026-07-29

## Hypothesis

Let `eta:E0->E1` commute with an effective quadratic orientation and let the
auxiliary prime `delta` split in that orientation.  The two orientation
eigenvalues label the two rational cyclic order-`delta` subgroups on both
curves.  Selecting the same eigenvalue on `E0` and `E1` therefore selects
compatible type-`(1,delta)` principalization lines without evaluating
`eta` on `delta`-torsion or enumerating all `delta+1` target lines.

## Null hypothesis

The public eigenvalue label is not unique on an endpoint, the endpoint label
sets differ, or the same-label target subgroup does not contain the
transported source subgroup.

## Claim status

`RESTRICTED THEOREM / TOY-EVIDENCE / MODEL-BOUND / NO END-TO-END RECOVERY`

## Parameters

- public ordinary fixture `E0/GF(29)` with `j(E0)=5`;
- its unique rational ascending degree-`2` isogeny `eta:E0->E1`;
- auxiliary prime `delta=7`;
- full torsion field `GF(29^24)`;
- Frobenius as the effective orientation;
- seeds `20260729`, `20260730`, and `20260731`.

The degree-`2` map is hidden from branch selection.  It may be used only
after selection to audit the commutative square.

## Metrics

- number of public rational degree-`7` directions on each endpoint;
- Frobenius eigenvalue attached to each direction;
- equality and distinctness of endpoint eigenvalue sets;
- number of same-label target candidates;
- transported-line containment after the audit map is revealed;
- source and target theta principalization factor counts;
- field degree, wall time, and peak RSS.

## Positive controls

- Both endpoint direction sets have exactly two distinct eigenvalues.
- Selecting the least eigenvalue gives exactly one direction per endpoint.
- Both selected graph gluings kill all `16` product `2`-torsion points.
- After selection, the hidden degree-`2` map transports the selected source
  line into the selected target line.
- Conjugating the orientation generator coherently at both endpoints relabels
  the directions and preserves compatibility.

## Negative controls

- Swapping to the other target eigenvalue does not contain the transported
  source line.
- A scalar that is not a Frobenius eigenvalue selects no rational direction.
- Replacing the target label by the wrong endpoint label fails the
  compatibility audit.
- Conjugating the orientation generator only at the target swaps the numeric
  labels and fails compatibility.

## Success criterion

All exact gates and negative controls pass on all three seeds; the public
selection is seed-stable; and an independent verifier reconstructs every
curve, line, eigenvalue, theta quotient, hash, and compatibility audit.

## Falsification criterion

Any label is ambiguous, endpoint eigenvalue sets differ, the same-label
square fails, a wrong-label control passes, or a hash or replay check fails.

## Reproduction command

```bash
env HOME=/private/tmp/p1243-sage-home TMPDIR=/private/tmp \
  sage experiments/ecdlp_isogeny/p1243_auxiliary_orientation_eigenline.sage.py
```
