# Formalization targets

One file per frozen formal task, consumed by
`autoresearch formal formalize --task-file <path>` and turned into a dispatch
queue stanza by `tools/formal_task.py`.

A target is a **pointer plus a claim, not an approval**. Writing one here
queues nothing and approves nothing; the Coordinator decides what runs, and a
machine-verified result is still pending semantic-fidelity review.

Every `claim` here is quoted or tightly paraphrased from a committed theory
note, and `source` names the note it came from. Do not write a claim that is
not traceable to one: a formalization of a claim nobody made proves nothing
about this program's research.

## What is here, in ascending difficulty

| target | kind | from | expectation |
| --- | --- | --- | --- |
| `ncp-affine-normal-form` | `formalize_claim` | THM-COMMUTATOR-KERNEL1 Lemma 1 | tractable — the pipeline smoke test |
| `ncp-reachability` | `formalize_claim` | THM-COMMUTATOR-KERNEL1 Lemma 2(b) | moderate |
| `ncp-commutator-ideal-refutation` | `formal_counterexample` | THM-COMMUTATOR-KERNEL1 Prop 1 | hard; a failure here is informative, not a defect |

## Semaev degree-fall attribution (RQ-DREG-bd6c86)

| target | kind | from | expectation |
| --- | --- | --- | --- |
| `semaev-frobenius-collapse` | `formalize_claim` | THM_SEMAEV_FALL1 Lemma 1 | tractable — the smoke test for this lane |
| `semaev-decomposition-certificate` | `formalize_claim` | THM_SEMAEV_FALL1 Lemma 3 | moderate; trivial mathematically, valuable operationally |
| `semaev-symmetrization-degree` | `formalize_claim` | THM_SEMAEV_FALL1 Lemma 2(b) | hard; may come back blocked on Mathlib's graded symmetric-polynomial support, which is a useful result about reach |

All three are **per-instance identities or decision procedures, never growth
statements**. `RQ-DREG-bd6c86` asks how the solving degree of the Weil-descended
Semaev systems grows; that is open, there is no proof to formalize, and a build
here is not evidence toward it. Read `THM_SEMAEV_FALL1` §4 before reviewing one:
the attribution procedure these lemmas support is sound and **not complete**, so
a failing check never certifies that a degree fall is unexplained.

The Huang–Kosters–Petit–Yeo last-fall-degree bound (`KN-LIT-7605`) is the real
theorem in this lane and is deliberately not specced: it needs Macaulay-matrix
and Gröbner machinery Mathlib does not carry.

All three NCP targets come from one note that was read end to end. Do not add targets by
skimming a note for a quotable sentence — the surrounding definitions are the
part the engine has to get right, and a claim detached from them formalizes
into something that is not the claim.

## Natural follow-ups, deliberately not specced yet

`THM_INCBARRIER1` §8 states three open gaps (G1, G2, G3) in precise form, and
G2 in particular — the worst-case chord constant, proved between 3/4 and 1 and
undetermined in between — is the shape `find_proof_gap` exists for. They are
not specced here because faithfully stating them needs §3–§5's definitions
read in full, and a paraphrase would be a different claim.
