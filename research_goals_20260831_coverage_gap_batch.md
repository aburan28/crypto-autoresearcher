# Research Goals 2026-08-31 — Coverage-gap intake: auxiliary-input DLP, and five corrections to an external audit

**Date anchor:** 2026-08-31

**Status:** Planning record. One `draft` goal, one research question, six
proposals. **Nothing here is evidence.** No experiment was run, no hypothesis
status changed, and no decision record was written.

**Input document:** *"ECDLP Auto-Researcher: Coverage Gap Analysis Against the
Full Published Attack Surface"* (PDF, 13 pages), supplied by the user on
2026-08-31. It is an EXTERNAL audit of this repository conducted from the
public GitHub landing page. Its own Caveats section states the limitation that
turns out to govern the whole document: *"I could not open
classify_research_submission.py, individual submissions/, or per-experiment
contract.md bodies, so I do not assert their internal contents beyond what the
README states."*

That caveat is honest and it is load-bearing. **Five of the input document's six
triage calls are wrong**, and they are wrong in one direction: it reports as
ABSENT or THIN work this program has already done, in several cases already
closed. This batch records the corrections against verified ledger state, then
opens a goal on the one residue that survives them.

Companion precedents: `research_goals_20260809_deployment_gap_batch.md`,
`research_goals_20260809_hash_symmetric_factoring_batch.md`,
`research_goals_20260804_five_primitive_batch.md`.

---

## 1. What the input document recommended, and what the ledger actually holds

The input document ranks five weak-coverage areas by "yield per unit
engineering effort" and recommends a three-stage program against them. Every
row below was checked against the working tree at
`aa1d1ad8c` before any record in this batch was written.

| # | Input document's area | Its triage | **Verified ledger state** | Verdict |
|---|---|---|---|---|
| 1 | HNP / lattice + Fourier nonce leakage | **ABSENT**, "highest yield", "the single largest gap" | `GOAL-ECDSA-001` (`draft`) + `RQ-ECDSA-87625f` (`active`) + **24 proposals**. The goal's own objective is to *"assemble the lattice-with-predicate and Fourier/Bleichenbacher results into a single Pareto frontier over (leaked bits, error rate, samples, time, memory, curve size)"* and to *"state where the 1-bit boundary sits at 256 bits"*. | **WRONG.** The document's top recommendation is an existing goal, framed the same way. |
| 2 | Generic-rho engineering | **THIN**, "rho only as baseline" | `H-RHO-bc6ea6` (`specified`) states exactly the negation-map question: *"the negation-quotient Pollard rho walk does NOT achieve its naive sqrt(2) gain, and the shortfall is a measurable function of the fruitless-cycle escape rule"*. 140 files across `ledger/`, `experiments/` and `knowledge/` touch negation map or fruitless cycles (57 / 75 / 8). Grumpy giants filed as `KN-LIT-7291`. | **UNDERSTATED.** The gap is execution, not conception: the hypothesis is specified and unrun. |
| 3 | Cheon auxiliary-input DLP | **ABSENT**, "the repo entirely lacks", "orthogonal to everything gated" | 17 ledger files. `DEC-20260802-204` reclassified an internally-generated route (APR-206) as *"a rediscovery of Cheon's discrete logarithm with auxiliary input algorithm"*; `DEC-20260802-206` retains it as `known_prior_art_baseline`; `DEC-20260802-208` files the primary source. **But: zero goals, zero questions, zero hypotheses, zero experiments.** | **WRONG on absence, RIGHT on the residue.** See §2. |
| 4 | Multi-target / batch / preprocessing DLP | **ABSENT** | `GOAL-ECDLP-001` requires *"complete preprocessing, relation collection, linear algebra, target descent, verification, memory, and multi-target accounting against Pollard rho and BSGS"* of every candidate; `CTRL-E2` adds *"the exhaustive-table and N^(1/3) preprocessing-frontier multi-target baselines in closed form"*. | **WRONG.** It is a standing accounting requirement on every candidate. |
| 5 | Automorphism-rho (GLV/GLS) | **THIN/ABSENT** | `GOAL-ENDO-001` is built on it, measuring *"whether endomorphism-ring depth, j-invariant special structure, or CM discriminant size changes anything beyond the known sqrt(\|Aut\|) automorphism-quotient constant"*. Plus `H-ENDO-001`, `H-JINV-0e8819`, `H-JINV-db2776`. | **WRONG.** It is an entire campaign, with the automorphism-vs-endomorphism distinction the document urges already load-bearing in the objective. |
| 6 | Elliptic nets / EDS | **THIN**; recommends "a single discriminating experiment to confirm the null and close it" | **Already done and closed.** `H-NET-001` is `rejected_scoped` on `EV-NET-001` (`EXP-NET-001`, `RUN-NET-001-a`): charged k-recovery exponent measured at 1.97–2.80 against a promotion gate of <0.49; net-relation rank per field op 0.024–0.046 against a 2x gate; sieve/BSGS op ratio *growing* with size, 24.2 → 38.6 → 134.7. | **WRONG.** The recommended experiment has been run, with controls, and the null confirmed. |

**Cross-cutting quantum note.** The document urges refreshing this program's
quantum resource figures to 2026 numbers and suggests the Dallaire-Demers
*"Brace for impact"* graded secp\*k1 ladder as an external calibration ladder.
Both are already here: `KN-LIT-1351` is that paper, and the 2026 figures the
document cites already appear across `IDEA-20260813-a46301`,
`IDEA-20260813-319645`, `IDEA-20260818-e0ce51` and `EV-CRYPTO-013`.

### Reproducing the checks

Rows 1, 2, 5 and 6 reproduce at any commit, since this batch adds nothing to
those areas. Row 3's two counts are of state *before* this batch, so they must
be run against the base commit — this batch's own records would otherwise be
counted.

```sh
grep -rl RQ-ECDSA-87625f ledger/proposals/ ledger/ideas/ | wc -l   # 24  (row 1)
grep -E '^\s+status:' ledger/H-NET-001.yaml                        # rejected_scoped (row 6)
grep -rilE 'negation.map|fruitless' ledger/ experiments/ knowledge/ | wc -l  # 140 (row 2)

# row 3 -- counts of state BEFORE this batch, from the base commit
git grep -ril cheon aa1d1ad8c -- ledger/ | wc -l                    # 17
git grep -ril cheon aa1d1ad8c -- ledger/goals/ ledger/questions/ | wc -l   # 0
```

### Why the document went wrong, and what it should be trusted on

The failure is structural, not careless: it audited a 7,427-commit research
program through a README. Absence of evidence on a landing page became evidence
of absence in a triage table. The rank ordering it produced is therefore
**inverted relative to marginal value** — it ranks first the area with a goal
and 24 proposals, and ranks fifth an area this program has already closed with
measurements.

What it should be trusted on, and what this batch takes from it:

- **Its literature map is dense and useful**, and several of its references are
  not in `knowledge/`. Those are pointers worth filing regardless of the triage
  errors — but they are `recalled` provenance here, see §5.
- **Its "provably dead" section agrees with this program's own findings** on
  xedni, canonical-height lifting, and F_p Semaev tuning for a rho win. That
  agreement is worth something precisely because it was reached independently.
- **Its correction to its own prior context on the automorphism-vs-endomorphism
  distinction is correct** — a curve automorphism of order m gives a `sqrt(m)`
  rho factor, a GLV/GLS endomorphism acting as `[λ]` on the prime-order subgroup
  gives none. This program already holds that (`GOAL-ENDO-001`), so it is a
  confirmation rather than a contribution, but an independent one.
- **Row 3's residue is real.** See §2.

---

## 2. What survives: the auxiliary-input lane, on the side the gate does not cover

The document called Cheon "absent". It is not — but the reason it is not is more
interesting than either the claim or the correction, and it leaves a genuine
lane open.

This program met Cheon's algorithm **from the inside**. BATCH-032 generated
APR-206, an "augmented-input" route with a balanced `N^{1/4}` row, and the
coordinator correctly recognized it as a rediscovery rather than a result. The
decision that closed it (`DEC-20260802-204`) turned on one sentence:

> Reject any ordinary-ECDLP improvement claim because acquisition of the
> auxiliary point `A=[x^d]P` from ordinary input `P,Q=[x]P` remains
> unestablished below rho-scale work.

That gate is correct and this batch does not reopen it. But note exactly what it
is a statement about: **acquisition**. It says the attack cannot manufacture its
own inputs. It says nothing whatever about the setting where the inputs are
**published as protocol parameters** — q-SDH, Boneh–Boyen signatures, and
powers-of-tau style structured reference strings hand over `[x]P, [x²]P, …,
[x^q]P` by design.

So the lane splits cleanly, and only one half was ever closed:

| | acquisition cost | status here |
|---|---|---|
| **Ordinary ECDLP input** | rho-scale, unestablished below | **closed** by `DEC-20260802-204` |
| **Protocol-published powers** | zero, by construction | **never examined** |

And on the open half, the decisive question is not algorithmic at all. It is
arithmetic, finite, and cheap: Cheon's cost `O(√(r/d) + √d)` is controlled
entirely by which divisors `r±1` actually has. The `r^{1/4}` headline describes
a *hypothetical* divisor near `√r`. A real curve gets whatever divisors it
happens to get — and nobody choosing P-256 was choosing the factorization of
`r−1`.

**Nobody in this program has computed that factorization.** It is one afternoon
of integer factorization with certificates, it has a definite answer, and the
answer is decisive in both directions:

- **No useful divisor on any standardized order** → the entire attack class is
  inert at deployed parameters *regardless of protocol*, and the lane closes on
  a certificate rather than an opinion.
- **A divisor near `√r` on a deployed curve** → that curve is named, and the
  goal's pause conditions send it to independent validation *before* anything
  else happens.

This is the shape the `research_goals_20260809` batch selected for and named:
**a security property living in a finite, enumerable object**. It is why this is
the one row of the six that gets a goal.

---

## 3. Records opened

All identifiers minted with `tools/allocate_id.py --next` and each verified free
with `--check` before use (AGENTS.md rule 14). No token was chosen by scanning
committed state.

| Record | ID | Status |
|---|---|---|
| Goal | `GOAL-AUXIN-a93442` | `draft` |
| Question | `RQ-AUXIN-f8d8c0` | `active` |
| Proposals | `IDEA-20260831-df4197`, `-ccb587`, `-bd0356`, `-3db9a0`, `-cc73da`, `-ecdd8c` | filed |

The goal is deliberately narrow. It is **not** "do Cheon"; it is "decide whether
Cheon reaches anything at deployed parameters, cheapest question first, and
close the lane if it does not."

### The six proposals, in dependency order

**1. `IDEA-20260831-df4197` — the divisor census.** *(measurement, priority high)*
Factor `r−1` and `r+1` for a frozen list of standardized orders; enumerate the
divisor lattice; evaluate `√((r±1)/d) + √d` at every divisor; report the best
achievable exponent `E(r)` per curve against the rho baseline of 0.5 at
identical accounting. Certificates on every factorization, independently
recomputed. Controls: a planted-divisor synthetic order must return `E ≈ 0.25`
(if the pipeline misses a divisor that was deliberately planted, no negative
result about any real curve may be reported); a safe prime must return
`E ≈ 0.5`. **No heuristic at any point** — this is why it is sequenced first and
alone. Its `next_action` in the goal is to run it *before* the rest of the goal
is opened.

**2. `IDEA-20260831-ccb587` — the protocol supply audit.** *(audit, priority high)*
Which deployed instantiations actually publish `[x^i]P`, for which `i`, and how
many — read off primary specifications, one citation per row, `UNDETERMINED`
where parameters are not publicly pinned and never estimated. The critical
detail the row must not fudge: releasing `[x]P … [x^q]P` for small `q` does
**not** supply `[x^d]P` for `d ≈ √r`, which is astronomically larger than any
real SRS publishes. The expected answer is no across the board, and the audit's
job is to record that comparison explicitly rather than to report two numbers
side by side. Null object: plain ECDSA/Ed25519 signing, which releases no powers
and must come back empty.

**3. `IDEA-20260831-bd0356` — mechanism reproduction.** *(mechanism, priority medium)*
Run Cheon at toy scale on planted-divisor curves, with a **matched no-divisor
control of identical bit size** and a certificate on every recovered scalar. The
pair is the claim: a positive alone could be a harness leaking its own setup, a
negative alone could be a broken solver. This program has cited Cheon's cost in
three committed decisions and has never executed it — an inherited number the
inventor protocol says to reproduce before building on. Note the run controls
explicitly forbid the failure the validator currently flags on four `EXP-ISOU`
runs: *a run claiming a discrete log without a verified certificate is invalid.*

**4. `IDEA-20260831-3db9a0` — the honest cost frontier.** *(cost-model, priority medium)*
The `r^{1/4}` figure is a **time** exponent; the naive form buys it with `√d`
memory, which at the balanced divisor is `r^{1/4}` memory — *the same exponent*.
`DEC-20260802-204` records the balanced row and the distinguished-point
low-memory variant as separate dispositions: two points on a tradeoff curve,
cited as though they were one result. Sweep both, measure peak memory rather
than modelling it, and emit a Pareto frontier with `dominated_by` filled per
row. This copies the method `GOAL-ECDSA-001` already applies in the adjacent
lane.

**5. `IDEA-20260831-cc73da` — the gate as a theorem target.** *(theory, priority medium)*
`DEC-20260802-204`'s gate says acquisition "remains **unestablished**" below
rho-scale work. That is the absence of a known method, not a lower bound — and
this program has been citing it as a boundary ever since. Is it provable in the
generic group model? Carries a full `proof_search_map`: the `d = 1` baseline the
argument must reproduce as *achievable*; the linear-target nearby-object control
(`[ax+b]P`) it must **fail** to prove hard, or it proves too much and is void;
and the Schwartz–Zippel union bound at degree `d ≈ √r`, which is where the
natural argument most plausibly dies. **Either outcome is worth having, and the
second is worth more** — a gate cited in three decisions and never proved is
exactly what the discipline suite exists to surface. Literature check first:
`DEC-20260802-208` already lists nonlinear-target generic hardness as
`known_prior_art_area`, so this may already be a corollary, and a citation is a
success for this idea rather than a failure of it.

**6. `IDEA-20260831-ecdd8c` — the SafeCurves audit row.** *(tooling, priority low)*
Twenty `GOAL-SCURVE-*` audits already reproduce eleven published criteria and
then measure "prioritized additional parameter-level weakness diagnostics". The
divisor census is exactly such a diagnostic. Wiring it in makes it durable —
computed by machinery that keeps running rather than by a document that goes
stale. The design problem, built into the row rather than papered over: a curve
failing the embedding-degree criterion **is weak**; a curve whose `r−1` has a
convenient divisor **is not**, unless it is used in a protocol that publishes
auxiliary powers. So the tooling emits the arithmetic value and its
protocol-conditionality clause **as one unit**, with a test asserting neither can
be emitted without the other. Gated on idea 1 passing its controls first: wiring
an uncontrolled computation into twenty audits propagates an error twenty times.

---

## 4. What was deliberately NOT opened

No goal was opened for rows 1, 2, 4, 5 or 6 of §1. Opening one would duplicate
existing state, and a duplicate goal in a 103-goal ledger is worse than no goal
— it splits a lane across two records that then drift.

What those rows warrant instead is a `next_action`, which is the coordinator's
call and not this batch's:

- **Row 2 is the strongest of them.** `H-RHO-bc6ea6` is `specified` and unrun.
  The input document's actual contribution here is a concrete target the
  hypothesis does not name: the Bos–Kleinjung–Lenstra measured negation-map
  ceiling of **1.29×** against the √2 usually quoted. That is a number to
  reproduce against, and it belongs in the experiment contract when
  `H-RHO-bc6ea6` is designed.
- **Row 1** is a `draft` goal with 24 proposals awaiting selection, not a gap.
- **Row 6 is closed.** `H-NET-001` is `rejected_scoped`. The input document's
  Stage-3 recommendation is complete.

The input document's "do not fund" list — further F_p Semaev tuning for a rho
win, xedni, canonical-height lifting, pairing inversion, first-fall-degree over
F_p — agrees with this program's existing findings and changes nothing. It is
recorded here as independent concurrence, not as a new constraint.

---

## 5. Provenance, stated plainly

**Every literature reference reaching this batch through the input document is
`recalled` provenance.** No agent in this program opened Cheon (EUROCRYPT 2006 /
J. Cryptology 2010), Kozaki–Kutsuma–Matsuo (Pairing 2007), Brown–Gallant
(ePrint 2004/306), Kim–Cheon, or Sakemi et al. this session. They are recorded
as pointers, hedged and marked, per the "Citation provenance" rules in
`templates/research-records.md`: *a recalled citation is a pointer, never a
citation.* None of them supports anything, and `RQ-AUXIN-f8d8c0` carries a
constraint gating experiment **design** on filing the primary sources — with one
exception, stated deliberately: **the divisor census (idea 1) depends on no
citation at all.** It needs only the cost expression, which is already filed as
prior art by `DEC-20260802-208` with a primary source. That is why it can run
first.

The Sakemi et al. figures the document reports (a 128-bit-order DLPwAI in ~45
hours on one PC; 1314 core-days at 160-bit order) are **not verified by this
program** and are explicitly barred from use as a comparison target in
`IDEA-20260831-bd0356` until read and filed.

By contrast, every claim in §1 and §2 about **this repository's own state** is
`internal` provenance and was read directly in the working tree this session.
The commands that reproduce them are in §1.

**Nothing in this batch is a security claim.** Idea 1 reports factorizations, not
difficulty; a divisor of the right size is a *necessary* condition and is barred
from being reported as a vulnerability. Idea 2 reads specifications. Idea 3
reproduces known prior art at toy scale and claims no novelty. Idea 5 is a proof
attempt whose most likely outcome is a citation.

---

## 6. Validation

`tools/validate_ledger.py` reports **the same 4 errors before and after this
batch** — four `EXP-ISOU-2ac81f` run manifests that claim a discrete log without
`certificate.verified: true`. They are pre-existing on `main`, unrelated to this
work, and untouched by it. **No new validation error was introduced** by the
eight records added here.

That pre-existing failure is worth naming rather than stepping around, because
it is the exact failure mode `IDEA-20260831-bd0356` is written to avoid, and
because it is live on `main` right now:

```
experiments/EXP-ISOU-2ac81f/runs/RUN-ISOU-{20bit,24bit}-{A,B}/manifest.yaml:
  run claims a discrete_log but certificate.verified is not true
```

Fixing it is out of scope for this batch and belongs to whichever campaign owns
`EXP-ISOU-2ac81f`.
