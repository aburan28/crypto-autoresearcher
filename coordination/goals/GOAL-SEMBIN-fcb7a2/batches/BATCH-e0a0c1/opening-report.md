# BATCH-e0a0c1 — opening report

**Goal** GOAL-SEMBIN-fcb7a2 · **Decision** DEC-20260916-441cd5 · **Round** REVIEW-SEMBIN-20260916-e0a0c1
**Opened** 2026-09-16 · **Lane** second, concurrent with BATCH-cbb416 · **Cards** 7, every one at `maximum_runs: 0`

> **Readers of this batch's two producer tasks must not read this file.** It is in their
> `blind_from` list, because it restates the Coordinator's expected answers.

## The one fact that shapes this lane

`EXP-SEMBIN-4fa22c` measures the **fake** first fall degree `d'_F`. Every route from that
quantity to any statement of Nagao's runs through 2015/984's **Lemma 4**, `d_F ≤ d'_F`.

That paper does not prove Lemma 4. It derives it from its Lemma 3, attributes Lemma 3 to
`[11]` = Nagao 2013/549, and says so in one sentence:

> Proof of this Lemma is complicated and not constructive.
> — `inputs/NAGAO-2015-984/paper_fulltext.md` :507

And this program has already verified, by exhaustive two-polynomial search over F_2, that
Lemma 4's **literal** form — with the field equations *outside* the fake system — is **false**.

So the campaign is about to spend compute on a quantity whose only bridge to its target is a
lemma with no proof in the paper that asserts it, no reader in this program before 2026-09-13,
and one form already known false. The contract *consumes* Lemma 4 rather than testing it, so
the run cannot discover this. A read can, and costs no compute.

## Why a second lane instead of two more cards

`BATCH-cbb416` declares `max_concurrent: 1` because its executing producer is a
degree-by-degree GF(2) rank computation under a 10 GB resident-set watchdog. Two readers of
frozen PDF text cost that measurement nothing — but folding them into that queue would either
stack them behind the executor for no reason, or force its concurrency up and put readers in
the same slot pool as the measurement. `BATCH-51e2aa` in the sibling campaign recorded what
that costs: a Macaulay2 phase drove the load average to 4.55 and a review joint had to be split
out to keep a timing clean.

The goal head anticipated this and authorised it in advance: item (2) "needs no compute and
competes with the batch for nothing, so it may run concurrently in a separate lane rather than
waiting behind it."

## The two reads

| Task | Source | Joints |
|---|---|---|
| `TASK-20260916-9da6e0` | Nagao 2013/549 (frozen, sha256 verifies) | J-1 which statement, J-2 is it proved, J-3 does it give Lemma 4's inside form |
| `TASK-20260916-64a93b` | Semaev 2015/310 (frozen) | J-4 statement versus argument |

Both carry the **J-5 proves-too-much control** and both run in independent sessions, mutually
blind, on disjoint joints. They run in parallel because neither answer is an input to the other.

### The trap the first read is built around

2013/549 **has its own Lemma 3**, at `paper_fulltext.md` :1081, and it is an unrelated
weight-degree statement about monomials. A reader who greps for "Lemma 3" in the upstream paper
will find it, and will report on the wrong statement confidently. The card therefore requires
matching on **content**, not number.

### The control that makes J-3 falsifiable

The program's own exhaustive counterexample supplies a known-false object. If a reader's
reconstruction of Lemma 4 from the upstream lemma **also** goes through with the field
equations outside, the reconstruction is wrong somewhere — and locating that is worth more than
the reconstruction. This is "controls before belief" applied to an argument rather than a
measurement.

## The prior is committed before either reader runs

At `coordination/review/sembin-20260916-e0a0c1/read-plan.yaml`: six numbered predictions with
confidences and falsification conditions.

This campaign has a decisive precedent. On 2026-09-16 a blind read of Nagao's Proposition 5
**overturned** the Coordinator's reading of it, and the goal's objective changed as a result
(`CORR-20260916-96f47d`, `DEC-20260916-88ac73`). It was informative *because* the expectation
was written down first. "The reader agreed with us" and "the reader agreed with what we had
already written down" are different findings, and only a pre-recorded prior separates them.

Two things about that prior are worth stating here:

- **P-4 is where the Coordinator expects to lose**, and says so. A reader who finds the upstream
  lemma unproved or insufficient for the inside form produces the most valuable outcome
  available in this lane, because the contract would have to record its Lemma 4 dependency as
  weaker. Confirmation leaves the campaign exactly where it stands.
- **P-3 is recorded because it was already wrong.** The Coordinator's first reading was that
  2015/984 had silently dropped a locality hypothesis when restating the lemma — which would
  have been a serious finding. The definition at 2013/549 :180 refuted that within minutes.
  A prior listing only the beliefs that survived the Coordinator's own checking overstates how
  well calibrated the Coordinator was, and the closing ruling has to score calibration honestly.

## The blind, and what it is worth

Neither reader may open the read plan, the opening decision, this report, the checkpoint, or its
sibling's directory. The limit is declared rather than hidden: **the J-1 answer is a lemma
number in a public paper**, derivable in minutes by grep, so the blind buys real independence on
J-2, J-3 and J-4 and much less on J-1.

That candour is not free-floating. `CORR-20260916-292e53` records this campaign paying for a
protective document that quoted the very value it was written to protect. The response is to
state what a blind is worth rather than to claim a clean one.

## Two binding modes, on purpose

| Archive | Mode | Why |
|---|---|---|
| `TASK-20260916-b88c5a` (control plane) | `content_at_commit` | The goal head and the queue legitimately change after the archive. Binding them at HEAD reports every later rerank as corruption — the failure `CORR-20260915-654160` records. |
| `TASK-20260916-92128f` (reader packages) | `content_first` | A filed report never legitimately changes. `content_first` verifies at HEAD, so it is the mode that **catches** an in-place edit — which the sibling campaign has suffered twice (`CORR-20260916-5166fe`, `CORR-20260916-2e9bc3`). |

Choose the mode by asking what the archive is protecting.

## What this lane cannot reach

- **It cannot refute Proposition 5.** DC-1 is untouched by either read.
- **It cannot move `H-SEMBIN-a7e721`.** The hypothesis predicts a measurable separation; nothing
  here measures anything.
- **It cannot discharge a completion criterion.** All four need a committed decision on run or
  read evidence, and a report is not a decision. Criterion 4 remains the only one met.
- **It cannot settle anything about the first revision of 2013/549.** Only the last of two
  revisions is served, that is what the program froze, and this environment cannot fetch an
  unserved revision. Both readers are told to report that limit rather than reason about a
  version they cannot open.
- **If a reader finds the upstream lemma unproved or insufficient**, the claim that follows — a
  published subexponential ECDLP bound resting on an unsupported lemma — is a contradiction of
  established evidence under core rule 12 and needs `review-breakthrough` at **max**. That tier
  is undegradable and cannot be served here. The finding is then recorded at its narrowest
  supported scope and the **claim** stays un-promoted while the campaign stays **active**. A
  limit on the claim, never on the campaign — and never a reason to soften a finding so that a
  servable tier will carry it.

## Inference

Every card sets `fallback_allowed: true` with a stated reason rather than inheriting `false`
from the `AGENTS.md` template — right for the contract, wrong for this machine, which holds no
API credentials for any adapter backend. `model_verified` is `false` throughout and recorded as
**not obtained** rather than as met. Both reader cards set
`independent_session_required: true`. The queue renders with no `inference_advisories` entry.
