# Falsification program for the knowledge corpus

Adopted 2026-08-08 under `RQ-FALSIFY-a2c501`. Worked examples and the shared
instrument: `experiments/EXP-FALSIFY-d770c1/`.

The corpus is not evidence. It is a set of claims that have so far survived
whatever was pointed at them, and for most of them nothing has been pointed at
them at all. This document says what to point, and in what order.

## Why this exists

Of the 58 records in `knowledge/findings/`, 24 carry `proof_status: derivation`.
Several of those carry `confidence: proved` with `evidence_level: theorem`.

No computer-algebra system is installed in this harness — no sympy, numpy,
scipy, sage, pari, cypari2, flint or galois. Confirm before assuming otherwise:

```sh
python3 -c "import importlib
for m in ['sympy','numpy','sage','cypari2','flint','galois']:
    try: importlib.import_module(m); print(m,'present')
    except Exception: print(m,'MISSING')"
```

So no derivation-tier finding in this corpus has been checked by any process
independent of the reasoning that wrote it. The ledger records a great deal of
independent *review* — a second agent reading an argument — and no independent
*execution* of the arithmetic that argument asserts. Those are different
guarantees. Review catches a wrong step someone can see; execution catches a
wrong step nobody can see. This program supplies the second.

Standard-library integer arithmetic is exact, which is the whole opportunity:
the claims are arithmetic, and the tests below cost minutes.

## The three rules that make a falsification admissible

**1. No refutation without a passing null control.** A probe that has not been
shown to stay silent on an object where the claim is TRUE by construction
reports nothing at all. This is not a formality. `RUN-FALSIFY-d770c1-001`
recorded a first, uncontrolled probe reporting a 28% violation rate against
KN-FIND-a1f3c2 — including factorisation shapes `[1,7]`, `[3,5]`, `[8]` that
are impossible for the asserted group. It looked decisive, quantitative and
publishable. Every violation was an artifact of a silent degree drop inside the
probe's own resultant. The null object was clean throughout, which is exactly
what localised the fault to the probe instead of the finding.

A falsification harness without null objects is capable of refuting a correct
theorem convincingly. Premature refutation is a failure mode symmetric with
premature closure, and this program is the thing most likely to commit it.

**2. Establish the record is current before probing it.** The corpus is
versioned by supersession, never by edit, so *a finding's own file is not the
current state of its claim.* Run the checker, which covers all three mechanisms:

```sh
python3 experiments/EXP-FALSIFY-d770c1/falsify/check_currency.py KN-FIND-xxxxxx
```

**Four** mechanisms are in use and **a check on any one has silent false
negatives** (`EV-FALSIFY-f367ec`, `EV-FALSIFY-2feed0`):

| Mechanism | Example | Trap |
|---|---|---|
| `superseded_by` | 52 of 58 findings | **5 findings lack the field entirely**; `.get()` returns the same as for a current record |
| `status:` + `withdrawn_by:` | KN-FIND-031, withdrawn | its `superseded_by` is null, so a supersession check calls it current |
| a record in `ledger/corrections/` | KN-FIND-a1f3c2 | nothing is written back into the finding |
| **a repair filed as a sibling finding** | `ff4a46` repairs `9d2f56` | not in `ledger/corrections/`; **0 of 7 targets link back** |

This rule exists because F-1 broke it. `EV-FALSIFY-440677` reported the
generic-vs-every gap in KN-FIND-a1f3c2's proof sketch as an *unrepaired* defect.
`CORR-20260807-652652` had recorded the same defect the day before, more sharply
— it names the omitted load-bearing step (σ_all must be the *whole* kernel, i.e.
the 2^(m-2) signed sums pairwise distinct at the generic point) and observes that
the independence assertion is the very statement it is offered as a reason for —
and it *supplies the missing proof* as Lemma 3.2. Withdrawn in
`CORR-20260808-3d4031`. A probe that skips this check may not assert that any
defect is unrepaired.

**And sweep `coordination/` for prior reasoning.** The checker reports it as an
*advisory* signal: those are working notes, not records, so a hit never makes a
finding stale — it means someone may already have thought about this. F-3
reported a finite-size-artifact diagnosis as this program's own; `BATCH-086/
TASK-20260804-112/diagonal_analysis.md` had made the same argument four days
earlier. Narrowed in `CORR-20260808-733115`. **Twice now** a "finding" of this
program was already in the repository — that is a pattern, not bad luck.

A clean result is not proof a record is current. It proves the three *known*
mechanisms are clean, which is the most a mechanical check can say.

**3. Evidence only.** Every probe files evidence. None edits a finding, changes
a hypothesis status, or supersedes a record — only the Coordinator may
(AGENTS.md rule 1), corrections supersede rather than overwrite (rule 4), and a
result contradicting a `proved`/`theorem` record needs independent
`review-adversarial` review by someone who did not originate it (rule 12).

## Defect classes, ranked by how cheaply they are caught

| Class | Signature in the record | Decisive test |
|---|---|---|
| **D1 Quantifier drift** | argument says "for generic parameters", claim says "for EVERY" | direct counterexample search over enumerated special families |
| **D2 Estimand drift** | derived quantity, plus a table exceeding it, plus a named mechanism for the gap | measure both estimands separately; null object without the mechanism |
| **D3 Unidentifiable fit** | an exponent fitted over a sub-decade range with no reported scatter | replicate at fixed parameter; compare within-point scatter to the across-point effect; fit the same exponent to a structureless null |
| **D4 Toy-to-crypto carry** | a constant measured at toy scale quoted at N=2^256 | vary the parameter the extrapolation holds fixed; if the constant moves, it is not a constant |
| **D5 Fatigue closure** | "all standard approaches are closed", "no exceptional locus", from a screening count | apply the corpus's own closure standard: named obstruction, argument, forward guidance — else `unverified` |
| **D6 Self-referential proof** | `proof_refs` points at the finding's own file | check whether any artifact outside the record supports it |
| **D7 Caveat loss on promotion** | a record promoted from a task/lemma document, whose source states limits the record omits | diff the record against its source for vacuity notes, non-claims and scope lines |
| **D8 Counted agreement** | confidence asserts N "independent" analyses agree | check their dates, campaigns and framing — same-day same-campaign agreement is one analysis reported N ways until shown otherwise |

D6 is worth a single mechanical sweep before anything else. Parse the
front-matter as YAML — a regex over the raw text silently misses flow-style
lists (`proof_refs: [path]`) and reports a clean corpus:

```sh
python3 - <<'PY'
import glob, re, os, yaml
for p in sorted(glob.glob('knowledge/findings/*.md')):
    m = re.match(r'^---\n(.*?)\n---\n', open(p).read(), re.S)
    if not m: continue
    fm = yaml.safe_load(m.group(1)) or {}
    refs = fm.get('proof_refs') or []
    if isinstance(refs, str): refs = [refs]
    if refs and all(os.path.basename(str(r)) == os.path.basename(p) for r in refs):
        print(f"{os.path.basename(p):<22} confidence={fm.get('confidence')}")
PY
```

**Executed 2026-08-08 — 9 findings, 4 of them `confidence: proved`:**

| Finding | confidence | proof_status |
|---|---|---|
| KN-FIND-9d2f56 | proved | derivation |
| KN-FIND-b7e091 | proved | derivation |
| KN-FIND-c7d31e | proved | derivation |
| KN-FIND-c93d45 | proved | derivation |
| KN-FIND-7e4b90 | proved_negative | derivation |
| KN-FIND-e7a3b1 | proved_negative | derivation |
| KN-FIND-3a7d42 | conditional_proof | derivation |
| KN-FIND-5c1a03 | multiple_independent_analyses | derivation |
| KN-FIND-a1f3c2 | derivation | derivation |

For each of these, the entire evidentiary basis for a `proved` label is the
record's own prose. That is not a defect on its own — a correct derivation is
correct however it is filed — but it does mean the `proof_refs` field carries no
information for these nine, and a reader who treats a populated `proof_refs` as
external corroboration is misled. Two of the nine have since been probed
directly: KN-FIND-a1f3c2 survived (F-1), KN-FIND-c7d31e's theorem survived while
its verification did not (F-2). Seven remain unprobed.

## Executed

### F-1 — KN-FIND-a1f3c2, Semaev monodromy `C_2^(m-2)` universally (D1)

`C_2^(m-2)` acting simply transitively on `2^(m-2)` sheets is a regular cover,
so every unramified specialisation factors into factors of EQUAL degree, and
every non-identity element has order 2. Admissible shapes are exactly
`[1]*2^(m-2)` and `[2]*2^(m-3)`. One `[1,3]`, `[3,5]`, `[8]` or `[1,1,2]`
refutes the claim.

Null object: minimal polynomial of `±s_1 ± … ± s_k`, `s_i² = d_i`, whose Galois
group embeds in `C_2^k` by construction. Positive control: `S_m` vanishes on
genuine relations.

**Outcome — claim survives.** 0/906 violations at m=4, 0/368 at m=5, primes
11–103, all controls clean. `EV-FALSIFY-440677`. A non-refutation, not a proof:
uniform sampling would miss an exceptional locus of density below ~1/300.

**Partly withdrawn — `CORR-20260808-3d4031`.** This record also claimed the
proof sketch's generic-vs-every gap was *unrepaired*. It was not:
`CORR-20260807-652652` had already identified it and supplied the missing step
(Lemma 3.2, `papers/semaev-conservation-specialization/paper.tex`), and
`KN-FIND-a8990a` Theorem A now derives (Z/2)^(m-2) with arithmetic = geometric
monodromy in every characteristic via Artin's theorem. What the run does
contribute is **independent corroboration**: a8990a's finite-scale dichotomy
("totally split, or 2^(m-3) quadratics, never anything else") is exactly the
admissible-shape test, and this run confirms it on 1,274 specializations with a
separate implementation and its own null object, against a8990a's own 241,643.
That matters because a8990a states plainly that rule 12 is not met for it.

### F-2 — KN-FIND-c7d31e, BKK Speedup Theorem (D2)

**Outcome — theorem survives, verification table refuted.** The identity
`γ_m = (m+1)/2^m` reproduces to |error| ≤ 0.0011. But per-decomposition
retention on a real curve at p=1009 is 0.5000 against a theoretical 0.5000,
error 0.0000, at every B — the elliptic-curve group law contributes *nothing*,
so the recorded "EC group law gives ~0.1 bonus" is false. The reported table is
a per-TARGET rate, which runs 0.61 → 1.000 as B goes 10 → 40 at fixed m, and a
curve-free null object brackets every reported value at multiplicity 1–2.
`EV-FALSIFY-2a5e46`.

### F-4 — KN-FIND-2a8b7e, geometrically growing BKK speedup (D4)

The finding fits `γ_m ≈ 0.86·0.68^(m-2)` across four rows, concludes
`speedup ≈ 1.72·1.36^(m-2)` "geometrically growing", and extrapolates
m=6 → 5.9x, m=7 → 8.0x, m=8 → 10.9x. Its four rows are measured at
**B = 54, 18, 12, 10** — B falls as m rises.

**Outcome — growth law refuted, confounded with B.** Holding B fixed, the
per-step ratio the finding fits at a constant 0.68 becomes 0.754 / 0.829 /
**1.096** (B=12), 0.893 / 1.280 / 1.127 (B=18), 1.004 / 1.290 / 1.002 (B=24) —
rising toward and past 1.0, not decaying. Mechanism: mean multiplicity rises
1.10 → 95.04 at B=24 and per-target success saturates at exactly 1.0000, so
shrinking B as m grows is what keeps the quantity off its ceiling.

The resulting geometric law also contradicts `KN-FIND-c7d31e`'s **proved linear**
`(m+1)/2` — ratio 1.27 at m=4 rising to 2.42 at m=8, diverging without bound —
while that finding states it "provides the combinatorial foundation for the
empirical improvements in KN-FIND-2a8b7e". At most one can hold.
`EV-FALSIFY-67150b`.

### F-9 — corpus-wide contradiction sweep (D3)

**Outcome — executed, two groups returned.** A mechanical sweep for quantities
quoted at more than one value returned `C(p)` (→ F-3) and `speedup` (→ F-4).
Both pointers led to real defects. The sweep's regex is deliberately crude and
its recall is a floor, not an estimate: it groups by the symbol immediately
preceding a numeral, so a quantity named differently in two records is invisible
to it. Two hits from one crude pass is a lower bound on what a careful pass
would find.

### F-10b — corpus currency and metadata exposure (D6-adjacent)

Found while applying rule 2 to the next F-10 target. Two integrity defects,
neither touching any mathematical claim, both cheap to fix. `EV-FALSIFY-f367ec`.

**Currency is marked three incompatible ways** (table under rule 2), and five
findings — `010`, `011`, `4e7a92`, `720727`, `d1c853` — carry no `superseded_by`
field *at all*, three of them no status field either. Field-absent and
explicitly-null are different facts; collapsing them is the bug.

**`KN-FIND-528ca0` has no YAML front matter** — the only one of 58 — so it is
absent from `knowledge/INDEX.md` entirely (the index names 57 of 58). Its
headline content is a **scope correction**: the theorem holds for *indefinite*
quaternion algebras and explicitly does NOT apply to HAWK's totally definite
algebra. A restriction on where a theorem applies is the thing most worth
surfacing to a later reader, and it is exactly what no metadata reader or
`search_knowledge` query can currently see.

**Separately**: CLAUDE.md says generated artifacts "are never committed" and
`knowledge/INDEX.md` is gitignored. The path *is* in `.gitignore` (line 134) but
the file is **still tracked** — `.gitignore` does not apply to tracked files and
`git rm --cached` was never run. Rebuilding the index still dirties a tracked
file on every branch, which is the conflict the documented fix says it removed.

### F-7 — KN-FIND-982fdf, C_t-minimality clauses (d) and (e) (D7)

The first clauses in this program to be **decided** rather than sampled.
Definition 3 (in the *lemma document*, not the finding) makes the order-based
class finite — every prefix/suffix of the ordered x-values — so (d) and (e) are
decidable on a fixed curve. `EV-FALSIFY-246cd8`.

**Outcome — both clauses hold, exhaustively.** 72 curves, p ∈ 11–53, whole class
enumerated: clause (d) holds every time, with exactly **two** identifying
oracles (C_t and its complement), never a third. Zero violations. Clause (e)
holds too — *and* holds for **40/40 random 1-bit oracles**, so standing alone it
distinguishes C_t from nothing.

**The defect is D7, caveat loss on promotion.** `ct_minimality_lemma.md` says
exactly that: clause (e) is "true but **vacuous** unless combined with Lemma 4"
— the word appears **4 times** — and it records an explicit non-claim, "minimal
does *not* hold among all 1-bit oracles". The knowledge record carries
**neither**: "vacuous" appears **zero** times in KN-FIND-982fdf. The source is
more careful than the record promoted from it, and the record is what gets cited.

Rule 2 was load-bearing here: the finding never defines "order-based", so
without the `coordination/` sweep this probe would have reported the definition
missing — which would have been wrong.

*Not tested*: clauses (a), (b), (c). **(b), non-simulability, is the substantive
one** and no enumeration over one curve can decide it. The corollary's weight
rests on (b), which is untouched here.

*Third probe defect, recorded not hidden*: the antichain check first compared
sets by **inclusion** and reported `False` on all 72 curves. The claim is about
the pointwise **information** order. Under the right order it holds everywhere.
F-1's degree drop, F-10d's naive aggregation, and this — three times the
instrument was wrong and the claim was right.

### F-6 — KN-FIND-e7a3b1, "all standard analytic approaches are closed" (D5)

Audited against the corpus's **own** closure standard, which
`docs/inventor-protocol.md` explicitly applies to "the program's own standing
saturation conclusions". `EV-FALSIFY-89e414`.

**Outcome — not a fatigue report; the universal is unestablished.**

- **(a) named obstruction — passes, well.** Each approach carries a specific
  obstruction, plus a unifying one: `DL_G` is not algebraic in *j* over F_p, so
  a method must want algebraic structure the DL lacks, or be computational not
  information-theoretic, or want non-abelian structure `E(F_p) ≅ Z/N` lacks.
- **(c) forward guidance — passes.** Hecke characters for CM curves are named as
  the surviving route, with their limitation; H-PSEUDO is declared *open*, not
  dead.
- **(b) argument — passes for the eight, fails for the universal.** The
  three-way taxonomy is *asserted* exhaustive over analytic methods, never
  argued. Enumerating members of an unbounded class and concluding "all" is
  exactly the inference this standard exists to catch.

Two subsidiary defects: the title says **six**, the table has **eight** data
rows; and the "DL random permutation" row is closed on `C ~ p^0.079`, the
exponent now under correction (`CORR-20260808-733115`).

*Not established*: that any closed approach works. No attempt was made to
construct a method evading the taxonomy, which is what a real refutation needs.
The objection is that the record asserts exhaustiveness rather than arguing it.

### F-6b — KN-FIND-7e4b90, "blocked for ordinary prime-field ECDLP" (D5)

**Outcome — mathematics sound, closure incomplete, and it is the one that
matters most.** `EV-FALSIFY-e58e4e`.

(a) and (b) pass: the obstruction is structural and specific — Wesolowski needs
`End(E)` a rank-4 definite quaternion algebra with 4D-LLL short vectors of norm
`O(p^{1/3})`; ordinary prime-field curves have a rank-2 commutative imaginary
quadratic order, so the lattice is 2D with shortest vector `O(√N)`, which *is*
Pollard rho.

It is arguably **understated**: the record says `|D| ~ p^{2/3}` with class number
1 is "not the case for generic curves", but class number 1 is not a genericity
condition — Baker–Heegner–Stark leaves finitely many such orders, max `|D| = 163`,
so that case is impossible for *every* curve once p ≳ 2082. Flagged for a
reviewer, not asserted.

**(c) fails: zero statements of what remains open** — no successor, no revisit
condition, no remaining uncertainty. AGENTS.md's integrity section asks for
evidence, budget, test boundary, remaining uncertainty, and a concrete successor
or revisit condition; this supplies three of five.

Why it matters beyond its size: Wesolowski is the program's **canonical
exemplar** (`docs/target-result-profile.md`). A record titled *blocked*, tagged
`blocked`, closing the transfer of the program's own stated target, with no
revisit condition and self-referential `proof_refs`, is the highest-consequence
shape a closure can take here. And the successor already exists unnamed:
**GOAL-SSI-001**, "Supersingular-isogeny cryptanalysis after the SIDH break" —
exactly where the quaternion structure *does* occur. The scope line correctly
excludes supersingular curves; the title does not, and one sentence would stop a
later reader concluding the route is dead in this program. It is not.

*Not established*: that the transfer is possible. No route past the rank-2
obstruction was sought — that would be the real test, and it was not run.

### F-10d — KN-FIND-a8990a, Semaev cover structure (D2 reproduction)

**Outcome — verifies in every particular checked.** `EV-FALSIFY-66f32d`. The
headline "241643 good specializations with zero exceptions" recomputes exactly
from the archived artifact: 16,737 (C2_C4 sampled) + 224,906 (C6 exhaustive).
Zero exceptions verified rather than accepted — `mixed_patterns = 0`,
`max_factor_degree_seen = 2`, `one_pattern_per_class = True` everywhere. Both
null-control rates match: NULL-A rejects at **86.31%**, NULL-B at **51.09%**
against the quoted "86% and 51%".

*Checker's own near-error, recorded:* naively summing all blocks gives 257,750
and looks like a 16,107 discrepancy. C5 tests a **different** consequence
(factor-base locus splitting), so excluding it is correct. The record's
arithmetic was right and the first pass of this check was wrong.

This is the best-made record met under this question: it self-declares
`confidence: derivation` not `proved`, states plainly that rule 12 is unmet and
novelty unadjudicated, ships executable code beside the claim, and reports nulls
its own instrument rejects at 86%. `RUN-FALSIFY-d770c1-001` independently
corroborates the same dichotomy on 1,274 specialisations with no shared code —
which matters precisely because rule 12 is unmet. The remaining gap is the one
the record names itself: a reviewer reading Theorem A and Lemma 3.2, not more
finite-scale checks.

### F-10c — KN-FIND-030, ID-allocation concurrency (D1, in a contract document)

**Outcome — finding upheld, its fix overstated where it was written down.**
`EV-FALSIFY-896f80`. KN-FIND-030 is accurate about both collisions and its
remedy works. But **AGENTS.md rule 14** says a random token "scans no state and
so **cannot converge**" — a universal negative about a randomised algorithm, and
false. `allocate_id.py`'s own docstring states it correctly ("collide only by
drawing the same value out of 16**6").

*Corrected in `CORR-20260808-438ecd`*: this entry originally said CLAUDE.md
"repeats it verbatim". It does not — `grep -c` returns **0**. CLAUDE.md says the
tool "draws a token **without scanning state**, then `--check` it before use",
which is accurate and names the mitigation in the same sentence. **One** document
overstates the fix, not two.

The margin nobody had written down: namespace 16⁶ per family, **1,275** random
tokens in use, worst family 181, so P(next collides) ≈ **1.08e-05**. Within one
family the birthday probability is 2.93% at N=1,000 and 52.5% at N=5,000. Dated
families reset daily and are safe; the undated ones — `KN-LIT-`, `KN-TECH-`,
`BATCH-`, per-area `EXP-`/`EV-` — accumulate forever, and `KN-LIT-` sits beside
7,832 literature files.

Controls passed: `--check` returns "REFUSE: taken" on an occupied id and "OK" on
a free one; 100 `--next` draws gave 0 occupied. So mint-then-check catches
collisions against *committed* state within one worktree — and cannot catch two
worktrees minting concurrently, which is precisely the case rule 14 calls
impossible. Small is not the same claim as cannot.

### F-10a — KN-FIND-ac28ed, exact-arithmetic K* corrections (D2)

A *correction* record carrying `confidence: proved`. Its dangerous failure mode
is not a wrong correction but an **incomplete audit** — a third bad cell nobody
caught. All 18 cells of the BATCH-121 table recomputed in exact rationals, plus
an IEEE-double recomputation as a cause control.

**Outcome — verifies completely, the first such record in this program.** Three
cells disagree with the committed tables and collapse to exactly the **two**
distinct corrections it names (`K*(std)` is m-independent, so its one error
appears once per table). No third exists. The stated cause is confirmed rather
than assumed: float reproduces the committed 2001 and 126 exactly, and a
representability control shows every disagreement sits at t=0.9 while all three
binary-exact t=0.5 cells (134, 100, 80) were committed correctly.

One **minor traceability defect**: it attributes the K* formulas to
KN-FIND-c7d31e, which contains zero occurrences of "K*". They are in
`BATCH-121/tasks/TASK-20260805-005` §B.2–B.3. `EV-FALSIFY-e983ed`.

### F-3 — KN-FIND-d4f820 / e7a3b1 / 4c9e71, the constant `C(p)` (D3)

Three live findings, none superseded, record `p^0.055`, `p^0.079`, and
`O(1) ≈ 4` for the same quantity.

**Outcome — exponents withdrawn.** Within-prime spread at p=1009 is 1.494×,
exceeding the entire across-prime variation of 1.213×; the fit moves from
`p^0.032` to `p^0.097` on resampling; and a structureless random subset fits
`p^0.069`, inside the claimed range. Unrecorded real signal: the factor base's
constant sits a stable 1.300× above the random null at every prime.
`EV-FALSIFY-40291d`.

## Pre-registered, not yet executed

Each states the target, the defect class, the decisive observation, and the
null object. Written before execution so the outcome cannot be chosen after.

### F-7 — GGM simulability claims, KN-FIND-002 / b7e091 / 982fdf (D1, D6)

These assert closure of oracle *classes* — "GGM-simulable with O(1) overhead",
"the minimal non-simulable order-based identifier". Class-level claims are
universal claims. Enumerate all order-based 1-bit oracles on a toy curve by
brute force and check the asserted minimality and uniqueness clauses
exhaustively rather than by argument. KN-FIND-982fdf's clauses (c), (d), (e)
are finite statements at toy scale and are therefore decidable, not merely
arguable. **Refuted if** an enumerated oracle is a strict predecessor the
argument says cannot exist. **Null:** run the same enumeration against a
deliberately non-minimal oracle and confirm the checker flags it.

### F-8a — repairs filed as sibling findings (D7-adjacent)

Found while applying rule 2 to F-8's target. A finding can be repaired by
**another finding** rather than by a `ledger/corrections/` record, and that link
is one-directional in **every** instance: 7 relationships, target links back in
**0**. `KN-FIND-012` is targeted by *three* repairs (013, 014, 031) plus three
corrections — six documents amend it, and it points at none.
`EV-FALSIFY-2feed0`.

This program walked into it: `ac28ed` repairs `c7d31e`, and F-2 probed `c7d31e`
without having read `ac28ed`. The cost was a **missing cross-reference, not a
wrong claim** — ac28ed corrects the K\* cells and downgrades the β-transfer
label, a different matter from F-2's estimand mismatch, and it states it makes
"no claim that the BKK speedup theorem is invalidated". `EV-FALSIFY-2a5e46`
stands as written.

Why the asymmetry bites: rule 4 means the corpus is *read forward* from an old
record to its repairs, and immutability guarantees the stale record stays put to
be found first. `check_currency.py` now covers all four mechanisms.

### F-10g — KN-FIND-015 and KN-FIND-013 (D2) — **F-10 complete**

`EV-FALSIFY-f14d8c`. The last two table-bearing findings.

**`KN-FIND-015`: derived arithmetic consistent, 12 of 12.** Carrier gaps
4.29/8.69/14.12 vs recorded 4.3/8.7/14.1; MATZOV-2022 6.29/10.29/16.02 vs
6.3/10.3/16.0; primal_bdd below NIST 2.80/6.04/1.28 vs 2.8/6.0/1.3; and
primal_bdd beats dual_hybrid+fft in all three sets as stated.

*Its measurements are not verifiable here* — lattice-estimator at the pinned
commit isn't installed and can't be fetched. That's an environment limit, not a
criticism: the pinning is exactly what makes reproduction possible elsewhere.

**`KN-FIND-013`: an inconsistency I can exhibit but not resolve.** Its crossover
Δ (9.5/14.4/14.8) is correctly *not* the simple NIST−baseline gap
(3.5/11.9/12.3) — HEUR-S1 routes Δ through R inside a log. But the implied rate,
gap÷Δ, is **0.37 / 0.83 / 0.83** CC bits per Δ bit. The 768 and 1024 rows agree
to two decimals; **Kyber-512 differs by 2.2×**.

**RESOLVED — `CORR-20260808-65a36f`, and 013 is correct.** The recommended
follow-up was run. The Case A model is in
`BATCH-004/tasks/TASK-20260731-010/validation_notes.md`:
`cost(Δ) = log2(2^Tsample + 2^(second_term+Δ))`. Solving `cost(Δ) = NIST`
reproduces **9.4555 / 14.3597 / 14.7598** — every value to four decimals.

The Kyber-512 anomaly is a **genuine regime difference**. Only the *second* term
takes +Δ, so Δ moves the total only as it lifts that term past Tsample. The gap
`Tsample − second_term` is **6.10** bits at Kyber-512 versus **2.17 / 2.11** at
768/1024 — so far more of Δ is absorbed at 512. And the two sets with nearly
equal gaps have nearly equal rates (0.83, 0.83), which is the consistency check
the original observation was missing.

*My error*: I declared it unresolvable while naming the search that resolved it.
One grep away. Same shape as `CORR-20260808-733115` — a conclusion drawn from the
record in hand rather than from the repository.

*Both records scope themselves well*: 015 labels its own level "estimate level
(not a cryptanalytic certificate)"; 013 labels its result "(conditional)" and
calls 012's ~84-bit figure "an *upper reference*, not a measured error". Their
shared baseline column matches exactly.

### F-10f — the ML-KEM cluster: 012 / 014 / 031 (D2 reproduction)

**First probe outside ECDLP** — which matters, because a defect pattern found
only in one domain may belong to that domain's authors rather than the corpus.
`EV-FALSIFY-432634`.

**Three records, three exact reproductions** from the archived vendor data.
`KN-FIND-012`: all six table entries — 1802, −35.7045, and Pgood
6668/11964/17823 **exactly**, not approximately. `KN-FIND-014`: all five aligned
entries — 2223 / 3988 / 0 / gap 421. `KN-FIND-031` (withdrawn, but "not retracted
as arithmetic"): the floor is **1.786031e-11 = 1/(4000·241³)** to full precision,
so −35.70 is exactly the sampling resolution limit, as it claims.

**The linkage defect, now with a number.** 012 references neither 014 nor 031,
both of which amend it. A reader of 012 **as written** computes the T-gap as
6668 − 1802 = **4866**. The correct aligned value is 2223 − 1802 = **421** — an
**11.57× overstatement**, obtained from a current, unsuperseded record. Sharpest
instance of the F-8a defect and the only one that can be quantified.

*Small imprecision in 014*, for accuracy not substance: its summary says the gap
"was overstated by factor 3". The **scale** factor is exactly 3 (verified); the
quantity its own table calls **T-gap** moves 11.57×, since subtracting a fixed
1802 doesn't scale linearly. It understates its own correction.

*Worth saying*: `KN-FIND-012` is the most carefully scoped record met under this
question — `provisional`, self-tagged `contested`, four explicit non-claims
including "Not a key-recovery break of ML-KEM / FIPS 203". Its qualitative
conclusion survives alignment intact: the aligned fraction inside is still 0.

*Not established*: anything about ML-KEM or Kyber security. The vendor `.out`
files are taken as given. **013 and 015 were currency-checked but not
reproduced** — they remain open.

### F-10e — KN-FIND-5c1a03, "three completely independent analyses" (D8)

**Outcome — the characterisation stands; the independence claim does not.**
`EV-FALSIFY-d07ef4`.

The record carries `confidence: multiple_independent_analyses` and asserts
"three completely independent analyses". Its three legs — `e7a3b1` (analytic),
`9d2f56` (combinatorial), `7e4b90` (algebraic) — **all carry `added:
2026-08-04`, as does 5c1a03 itself.** One campaign, one window, one framing,
each leg derivation-tier with no external verification.

This is the corpus's *own* quorum principle, outside its stated domain: "Three
aliases that all fall back to one backend produce correlated judgements;
counting them three times is not independent agreement."

**And all three legs have since been qualified**, each by a separate probe here:
e7a3b1's universal is unestablished (F-6); 9d2f56's "exact condition" — the very
form 5c1a03 cites — was withdrawn by ff4a46 (F-8); 7e4b90's closure supplies
three of five required elements (F-6b). A convergence inherits its legs.

**Bonus — the corpus corroborates F-6 against itself.** F-6 found e7a3b1's title
says "all six" while its table has **8** rows, and could not say which was
intended. 5c1a03 calls the same leg "**8** character-sum proof methods". Written
the same day, saying eight. The table is right; the title is the error.

*Not disputed*: the characterisation itself — minimal algebraic structure vs
richer structure — which is plausible and was not evaluated. Same-day filing
doesn't prove the analyses weren't separate, only that the record claims
independence while offering no evidence of it. Correlated is not wrong.

New defect class **D8, counted agreement**: a confidence label that counts
agreeing analyses must show they could have disagreed.

### F-1c — m = 6, the last untested structural case (D1)

**Outcome — holds, on a thin sample.** `RUN-FALSIFY-d770c1-007`. At m=6 the
cover has degree 16, so admissible shapes are `[1]*16` and `[2]*8` only.
Construction is `S_6 = Res_X(S_5(x1..x4,X), S_3(x5,x6,X))` — three nested
resultant levels, full nominal degree asserted at each.

**0 violations in 17 usable specialisations**, all `[2]*8`. Controls re-run
rather than inherited (new code, three places for the RUN-001 fault to hide):
positive **30/0**, null object **0/162**.

**Honest limits.** n=17 is thin; a locus of density below ~1/17 would be
invisible. And **no `[1]*16` was observed** — under Chebotarev the identity class
has density 1/16, so seeing none in 17 draws is unremarkable (p ≈ 0.33) but
leaves that class *unconfirmed* at m=6.

*Probe starvation, recorded*: the first version yielded **1 usable specialisation
in 97** and was **not reported**. Cause: a degree drop whenever an interpolation
node collides with a fixed parameter, and m=6 has 17×9 nodes. Choosing nodes
clear of the parameters fixed it — raising yield without weakening the test,
since every degree assertion stays in force.

### F-5 — end-to-end BKK cost (D4) — **BLOCKED ON UPSTREAM, not skipped**

`EV-FALSIFY-4144a5`. The record F-5 would audit, `EV-SEMAEV-7f7d22`, **does not
exist** — it is a *reserved* identifier. `DEC-20260806-08b9ed` says it "remains
correctly reserved and bound by BATCH-122". No decision treats it as evidence.

And F-5's thesis is **already on the record**: `KN-FIND-ac28ed` (2026-08-06,
before F-5 was written) requires that it "be pre-registered against exact
rational arithmetic with the linear-algebra and memory terms included" and
downgrades the β-transfer's "provable" label to a model assumption. Running a
cost model now would pre-empt a scheduled pre-registration and repeat the
already-recorded-diagnosis error of `CORR-20260808-733115`.

*Almost filed and wrong*: "five records cite evidence that doesn't exist" reads
as decisions resting on nothing. Checking them refutes it — they say *reserved*.
Sixth would-be false finding, caught by checking.

### Correction to a figure this program kept citing

"259 pre-existing validator errors" has been used here as shorthand for corpus
disorder. It is not. The count is 256 and the composition is what matters: 56
missing-field, 45 missing run artifact, 33 run missing-field, 19 evidence→unknown
run, 17 certificate-kind, 11 expected-`run`-key. That is **legacy schema debt in
run manifests**, which `validate_ledger.py`'s own comments put at ~680
pre-current-schema manifests.

The dangling references are mostly a **file-format mismatch**: 32 unknown-ref
errors name 12 ids, and `RUN-YIELD-004/-005/-006`, `RUN-OIFP-001` all *exist*
with `manifest.**json**` where `check_run()` globs only `manifest.**yaml**`.
RUN-OIFP-001 even ships command.txt, environment.json and both logs — a complete
package in the wrong serialisation.

Not harmless, though: a run whose manifest the validator cannot read is a run
whose controls and certificate discipline go **unchecked** — which matters for
exactly the reasons this program exists.

### F-1b — special families, re-scoped then run (D1)

**Outcome — 0 violations on every family, and F-1b was mostly redundant.**
`EV-FALSIFY-4e9c78`. Closed as pre-registered.

Re-scoped twice. Its original motivation was voided by `CORR-20260808-3d4031`.
Then a draft of this probe was about to assert that no run had tested special
families — **checked before writing, and false**: a8990a's run enumerates
j=0 (both congruence classes), j=1728 (both, one supersingular), and 4
full-2-torsion curves. A deliberate family design, not a uniform sample.

Genuinely uncovered: **anomalous curves** (#E = p). An exhaustive (a,b) scan
over p ∈ 11–47 found 339. Result: **0 violations**, at m=4 and m=5, on all six
families — anomalous, supersingular, j=0, j=1728, full-2-torsion, generic-j.

**The anomalous result is the interesting one, and it is negative.** Anomalous
curves are exactly where prime-field ECDLP is broken outright by the
Smart/Satoh-Araki/Semaev lift. If any family carried an exceptional monodromy
locus, that was the candidate. Their factorisation behaviour is indistinguishable
from generic. The monodromy carries **no** signal about the one prime-field
family whose ECDLP is known to be easy — which closes an obvious place to look.

*Controls not re-run*: instrument unchanged from `RUN-FALSIFY-d770c1-001`, whose
null object and positive control established it. Stated so "controls passed" is
not claimed for a run that didn't execute them. *Remaining*: m ≥ 6.

### F-8 — KN-FIND-9d2f56 / ff4a46, Betti-Yield "exact condition" (D1)

**Outcome — the pre-registered test is MOOT, and the real defect is linkage.**
`EV-FALSIFY-0ed0d9`.

F-8 was written to test an "exact condition" claim as an iff. That premise no
longer holds: `ff4a46` has already narrowed it to a **necessary condition only**
and explicitly disclaims sufficiency. There is no iff left to falsify —
recorded as *moot*, not skipped.

**Rule 2 saved this probe a fourth time.** 9d2f56's disjunction
(`β₁ ≥ Ω(√N)` OR `⟨r₂⟩ = o(1)`) and its "equivalently … requires yield above the
random baseline" *look* contradictory. They are not: `o(1)` **is** the negligible
level, so "not o(1)" is "above the baseline" once the baseline is the
pseudorandom AT-heuristic yield — exactly the identification ff4a46 makes.

**The surviving defect is sharp.** ff4a46 says in terms "This record supersedes
KN-FIND-9d2f56's wording". Yet 9d2f56 records `superseded_by: **null**`, contains
**zero** references to ff4a46, and its **title still reads** "H-PSEUDO is the
exact condition for sub-rho combinatorial ECDLP" — the precise formulation
ff4a46 warns "can be read as claiming H-PSEUDO is a *sufficient* condition". A
reader landing there gets the withdrawn claim under a `proved` label, with the
correction unreachable.

ff4a46 carries a machine-readable `repair_target` field — used by **1 of 58**
records and read by no tool.

*Not established*: anything about the theorem's truth, or about whether sub-rho
is achievable — ff4a46 declines that question and so does this. Nor that
`superseded_by` is the right field: this is a *partial* supersession (wording
withdrawn, theorem preserved) the schema may not model.

An exact-condition claim is an iff and fails if either direction fails.
Construct toy complexes on both sides of the stated threshold and check both
directions independently. **Refuted if** a complex satisfies one side and not
the other. Note that KN-FIND-ff4a46 is a *wording repair* of KN-FIND-9d2f56
carrying `confidence: proved`; a repair inherits the proof status of what it
repaired, and KN-FIND-9d2f56 is confirmed above as one of the nine D6 records
whose `proof_refs` name only itself.

### F-10 — Reproduce the corpus's own reported numbers (D2, highest yield per hour)

For every finding carrying a table, re-run the measurement from its recorded
parameters and compare. F-2, F-3 and F-4 all began here.

**COMPLETE — all 17 reproduced or accounted for.** Original inventory: Five are done — `c7d31e`,
`2a8b7e`, `d4f820`/`e7a3b1`/`4c9e71` (as F-2, F-4, F-3) and `ac28ed` (F-10a).
Twelve remain, largest first: `a8990a` (10 rows), `012` (6), `029` (5), `030`
(5), `528ca0` (5), `014` (4), `031` (4), `ff4a46` (4), `013` (3), `015` (3),
`5c1a03` (3), `93d1aa`.

Reproduce with `falsify/run_kstar.py` as the pattern for closed-form tables and
`falsify/probes.py` for measured ones. Note that four of the five done so far
were defective; do not read that base rate into the remaining twelve, since the
five were chosen by the F-9 sweep and by claim strength, not at random.

## Priority

1. **F-10** — mechanical, no new mathematics. Every defect found so far surfaced
   from re-running a recorded table. F-9 is done and fed F-3 and F-4; a second,
   less crude pass over quantity names is still worth one hour.
2. **F-6** — applies a rule the corpus already adopted to closures that predate
   it; a wrong closure suppresses a live research lane, which is the costliest
   error class here.
3. **F-1b, F-7, F-8** — exhaustive enumeration against class-level and
   universal claims.
4. **F-4, F-5** — cost-model audits of the crypto-scale figures.

## Reporting standard

Every probe reports its null-control outcome next to its measurement, states the
scope it tested, and says which of these it found: the claim survived, the claim
was refuted within scope, the claim's *support* was refuted while the claim
stands (F-2, F-3), or the design could not resolve the question. The last is a
real outcome and is not a failure of the probe.

A finding that survives is not thereby promoted. Nothing in this program raises
a confidence level; it can only lower one, or leave it where it was.
