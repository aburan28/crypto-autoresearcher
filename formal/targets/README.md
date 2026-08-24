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

All three come from one note that was read end to end. Do not add targets by
skimming a note for a quotable sentence — the surrounding definitions are the
part the engine has to get right, and a claim detached from them formalizes
into something that is not the claim.

## Natural follow-ups, deliberately not specced yet

`THM_INCBARRIER1` §8 states three open gaps (G1, G2, G3) in precise form, and
G2 in particular — the worst-case chord constant, proved between 3/4 and 1 and
undetermined in between — is the shape `find_proof_gap` exists for. They are
not specced here because faithfully stating them needs §3–§5's definitions
read in full, and a paraphrase would be a different claim.
