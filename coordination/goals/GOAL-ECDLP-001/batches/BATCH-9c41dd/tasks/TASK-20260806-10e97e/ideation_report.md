# Ideation report — TASK-20260806-10e97e

Five proposals filed. Nothing here is a measurement, a status change, or an
approval. Every number below is either derived in the cited proposal or read from
a committed artifact I can name by path. Primary sources are unreachable from
this environment, so **every proposal carries `novelty_status: unverified`** and
none is dismissed as known either.

Prerequisite: `duplication_audit.md` in this directory. Coverage achieved
**262/262** files in `ledger/proposals/` and **64/64** proposals in the seven
target questions (34 RQ-ECDLP-002 + 30 satellites), plus the 47 ECDLP entries of
the pre-ledger catalogue `ideas/catalogue-20260805/`. Nine candidates were
generated and dropped because the audit found them already held; each drop is
recorded there with the record that holds it.

---

## 1. The five proposals

| id | question | class | what it decides | compute |
|---|---|---|---|---|
| `IDEA-20260806-3b91c7` | RQ-ECDLP-002 | cost-model | The comparator is off this corpus's own recorded frontier: at memory `N^sigma` on a fixed curve the achievable generic online time is `N^{(1-sigma)/2}`, so every threshold in the ECDLP/ICEX lanes is too generous by `N^{sigma/2}` — at `B = N^{1/(m+1)}` the bar moves from `N^{1/2}` to `N^{1/2 − 1/(2(m+1))}`, i.e. 25.6 bits at `m=4`, `N = 2^256` | **zero** (+ optional toy sweep) |
| `IDEA-20260806-9d47e2` | RQ-MONO-001 | cost-model | Cashes `KN-FIND-c41ea9`'s complete-splitting theorem as a cost identity: `D_trial` for enumerate-and-test is exactly `m−1` group additions, not a Gröbner solve — pinning the free parameter the ICEX threshold turns on, and labelling every committed SDEG/DREG/SIG cell by formulation | **zero** (+ fixture reproduction) |
| `IDEA-20260806-7ea402` | RQ-SDEG-001 | cost-model | Gröbner cost is quantized in whole degrees, so a rank deficit costs exactly zero unless it moves `d_solve`; the jump factor at the decisive cell `n=12, D=6` is `1.731` at `omega=2`, and the 7,110 deficit's own rank effect is a 4.5% **saving** | **zero** (+ toy ladder) |
| `IDEA-20260806-c5d183` | RQ-ECDLP-002 | mechanism | No lossy ECDLP object propagates deterministically under the full translation action (five-line orbit argument), forcing a three-class index set for `KN-OPEN-019` and a forced value of **zero** for `IDEA-20260802-002`'s stated success cell | **zero** (+ toy verification) |
| `IDEA-20260806-20f6ab` | RQ-ECDLP-002 | algorithm | **Explicitly subpolynomial, and the title says so.** Prices the partial-relation/large-prime escape that catalogue A1-1 closes by argument: it is worth exactly `C(m, m/2)` — `2^{29.16}` at the coverage-optimal `m=32`, `N^{o(1)}`, hence **zero exponent**, and at most ~1 bit end-to-end after the Amdahl ceiling | low |

All five are zero- or low-compute by construction. That is deliberate and follows
`analysis/SSI-ECDLP-SYNTHESIS-20260803.md` §5: this program's binding constraint
is not compute but the absence of written-down cost models against which
measurements could be ranked.

## 2. Ranking by expected information gain per unit cost

**1. `IDEA-20260806-3b91c7` — the memory-matched baseline.** Highest, and it is
not close. Cost is one afternoon of exact arithmetic. Information gain is a
*multiplier on every other result in the goal*: it changes the number that every
ECDLP and ICEX candidate must beat, in a stated direction (harder), by a stated
amount (`N^{sigma/2}`, 25.6 bits at `m=4`), and it supplies a missing row for a
Pareto table the lane has never built. It is also the only proposal in this batch
whose central claim is pinned between two committed statements — it must land
**exactly on** `KN-TECH-005`'s recorded lower bound `S·T² = Ω̃(n)`, and both
"below" and "above" are reachable failures. Crucially it makes this program's
positive claims *harder*, which is the direction a correction should point when
the author has no stake in it.

**2. `IDEA-20260806-9d47e2` — cashing complete splitting as a cost identity.**
Second because it is the batch's actual deadlock exit and costs a reading pass.
`GOAL-ICEX-001` blocks on SDEG/MONO/RELN packages; SDEG/DREG/SIG block on a
semi-regularity model; MONO is paused. This record says the corpus has *already
proved* the thing ICEX needs — `D_trial` is `m−1` group additions in the
enumerate formulation — and that the three blocked goals have been measuring a
different formulation's `D_trial` without labelling it. The deliverable (an E/S
label plus membership-predicate type per committed cell) is pure reading and
ranks three goals instead of blocking them. It is second rather than first only
because its value is contingent on what the labelling pass finds, whereas
3b91c7's arithmetic is unconditional.

**3. `IDEA-20260806-7ea402` — cost quantization of the rank deficit.** Third.
Same deadlock, narrower scope, and its most valuable branch (the committed
artifacts do not contain the third input needed to compute `sol(D)`) is a finding
about archiving rather than about mathematics. But the arithmetic is free, the
exact jump table `J(12,5)=2.505, J(12,6)=1.731, J(12,7)=1.322` is computable
today, and the sign result — that the celebrated 7,110 deficit is, absent a
threshold crossing, a **4.5% cost saving** — is a direct, checkable contradiction
of the reading three goals carry.

**4. `IDEA-20260806-c5d183` — the additive-compatibility trichotomy.** Fourth.
The theorem is almost certainly folklore (I say so in the record, and put my
prior at 0.60 that a reviewer finds it stated), and it moves nothing. Its value
is entirely structural: `KN-OPEN-019` currently has no index set, every saturation
conclusion this program has reached is therefore a statement about its search,
and a three-element index set with an exhaustiveness argument *over hypotheses*
is what `docs/inventor-protocol.md` §4 asks for. It also forces the value of an
already-committed proposal's primary metric before that meter is built, which is
the cheapest kind of pre-registration available.

**5. `IDEA-20260806-20f6ab` — the price of the large-prime escape.** Last, and
deliberately so. It is a subpolynomial result; the title, the
`target_complexity` block and the `sota_delta` all say so, and after the Amdahl
ceiling it is worth at most about one bit end to end. It earns its place because
it converts catalogue A1-1's *argument* into a *number* — the escape is worth
exactly `C(m, m/2)` and no more — which upgrades a screened mechanism to a named
obstruction at the §4 closure standard, and because it directly answers
`IDEA-20260803-fa9839`'s explicitly weakest link `HEUR-AT-3`. Its one route to
something exponent-relevant (recursive representation compounding) is counted
exactly at toy scale rather than estimated.

## 3. Test this one first, and this is the cheapest valid discriminator

**Test `IDEA-20260806-3b91c7`, Stage 0, and inside Stage 0 run the `sigma = 0`
calibration before anything else.**

The single cheapest falsification is one line of arithmetic:

> Derive the chain-table triple and evaluate `sigma + 2·tau_on`. It must equal
> **1** identically. Then set `S = 1` and check that the formula returns
> online time `Θ(sqrt(N))` and a correction of **exactly zero**.

Why this is the right first test, and why it is *valid* rather than merely cheap:

- **It is calibrated on an edge where the answer is known for free, and where
  there is provably no hidden cost to find.** At `S = 1` the construction *is*
  Pollard rho, and rho's position — `0.886·sqrt(N)` at `O(1)` memory — is this
  corpus's own standing convention. An instrument built to find hidden memory
  costs will find them everywhere unless it returns **zero** correction at the
  one point that has none. A sign error, an off-by-one in the stopping rule, or a
  double-counted offline term all surface immediately as a nonzero correction at
  `sigma = 0`. This is the specific defect `ideas/catalogue-20260805/SCREENING.md`
  §2 records the whole screening exercise as having: *"No lens-calibration
  control was run… no entry known to be sound was passed through the three lenses
  to confirm they can return 'not refuted'."* This test is that control, applied
  to my own instrument, first.
- **It is two-sided, and both sides are reachable.** `sigma + 2·tau_on < 1`
  contradicts a committed theorem (`KN-TECH-005`) and means my derivation is
  wrong. `> 1` means the construction is off-frontier and the headline collapses.
  Neither branch is an outcome I can talk my way out of.
- **It is upstream of everything else in the batch.** If it fails, three of the
  five proposals lose a term they cite (7ea402, 9d47e2 and 20f6ab each carry a
  memory-matched clause), and none of the toy compute in the batch should be
  spent.
- **It costs zero compute, no dependency, and about an hour.** SageMath is
  absent, `numpy` is not needed, and no ECDLP is solved.

The cheapest falsification of the *second*-ranked proposal, for comparison, is
the committed-fixture reproduction: rebuild `KN-FIND-c41ea9`'s `m=4`, `F_211`
census and check 193/193 complete splittings with root sets exactly
`{x(±P1±P2±P3)}`. That is also a known-answer edge, and it is why 9d47e2 ranks
where it does.

## 4. Honest accounting (`docs/inventor-protocol.md` §5)

**Objects considered.** (i) The cost point as an exponent **triple**
`(sigma, tau_on, tau_off)` — 3b91c7. (ii) The **degree-graded solve indicator**
`sol(D)` and its integer `d_solve` — 7ea402. (iii) The **propagation type**
`(H, b, coordinate_dependence)` of a projection — c5d183. (iv) The
**representation multiplicity** `rho_rep` of a single decomposition — 20f6ab.
(v) The **charged per-attempt cost `D_trial` indexed by formulation** — 9d47e2.
Considered and rejected before drafting, with reasons in `duplication_audit.md`
§4: the second moment / additive energy of a factor base (held by
`IDEA-20260805-a25f11`); free-collision supply as coverage's complement (A1-6);
enumeration dependency as a sumset (A1-6); the coupon-collector correction
(A1-8, `IDEA-20260805-061f97`); the quadratic-character chord word (**killed by
the `KN-FIND-c41ea9` screen, not merely duplicated**); degree-`d` fibrations as
collision compressors (`IDEA-20260802-005`); base change to `F_{p^n}` (A4-4);
the generic-transport null (`IDEA-20260731-011`); the structured-GGM `delta`-mass
screen (A3-1, and blocked at source); and the CM/norm-form lens, which was worked
through, found to reproduce A1-2's meet-in-the-middle exponent exactly, and
carried only as forward guidance inside `c5d183`.

**Depth of verified structure.** **Zero.** No experiment was run, no cell was
measured, and no proposal in this batch has been executed. Every exponent,
identity, jump factor and bit count stated in the five records is a
*pre-registered prediction to be verified*, several of them arithmetic identities
that can fail. Where a record re-derives an established result through a new lens
— c5d183's orbit argument, 20f6ab's balancing, 9d47e2's cost corollary — that is
recorded as exactly that, and each says so in its own `novelty_status` and
`honest_prior_of_survival`.

**`dominated_by`.** Every frontier row this corpus holds was checked, per
proposal, and none was left as an unchecked `null`. Rows checked: Pollard rho
(`0.886·sqrt(N)` time, `O(1)` memory, linear parallel speedup); BSGS
(`N^{1/2}`, `N^{1/2}`); the automorphism-quotient rho variant `sqrt(N/|Aut|)`;
the multi-target floor `sqrt(T·N)` (`IDEA-20260731-013`, `KN-LIT-013`); the
preprocessing frontier `S·T² = Ω̃(N)` (`KN-TECH-005`); prime-field index
calculus, which has no known advantage (`KN-OPEN-001`, and `EV-IC-002` retracted
this program's only support verdict); and, for records that cite it, the
memory-matched baseline `sqrt(N/S)` derived in `3b91c7` itself. Verdicts:
`c5d183` and `7ea402` — `n/a (no algorithmic result claimed)`, written only after
the row-by-row check; `20f6ab` — **dominated by Pollard rho on every axis**
(2^189.4 vs 2^128 time at `m=4`, `N=2^256`; `N^{1/2}` vs `O(1)` memory);
`9d47e2` — the *formulation* it costs is dominated by rho by 64 bits and by the
memory-matched baseline by 128 bits, the record itself occupies no point;
`3b91c7` — its construction's **total** cost is dominated by rho at every
`sigma > 0` and ties at `sigma = 0`, and it **sits on** the preprocessing
frontier, where it cannot be improved without contradicting a committed theorem.

**`sota_delta`, quantitatively.** **Zero on every ECDLP attack axis, for all
five.** No solve, no relation at scale, no certificate, and nothing faster than
`0.886·sqrt(N)`. The non-zero deltas, all on comparators and accounting:
the baseline online-time exponent at memory `N^sigma` moves `1/2 → (1−sigma)/2`,
tightening the index-calculus bar by `1/(2(m+1))` = 32.0/25.6/21.3/18.3/16.0 bits
at `m = 3..7` and `N = 2^256`, plus a forced cap `B ≤ N^{1/3}` and a
re-verdict of BSGS as dominated by `N^{1/4}` at its own memory (3b91c7);
`D_trial` pinned at `m−1` group additions against a degree-`2^{m−2}`
root-find, three to four orders of magnitude, plus an E/S label per committed
cell (9d47e2); an exact jump table with `J(12,6) = 1.731` and a **4.5% cost
saving** where three goals read an obstruction, and a one-bit deliverable
replacing a three-significant-figure one (7ea402); one object cell proved empty
and a three-element index set with an exhaustiveness argument over hypotheses,
plus a forced zero for `IDEA-20260802-002`'s success cell (c5d183); and the
large-prime escape priced at exactly `C(m, m/2)` = 2/6/20/70/252/924/3432 at
`m = 2..14 even`, `2^{29.16}` at the coverage-optimal `m = 32`, `N^{o(1)}` hence
**no exponent**, halved to 14.6 bits after re-optimising `B` and capped at about
1 bit end-to-end by the Amdahl ceiling (20f6ab).

**Enumerated closures, each with its mechanism, each *proposed* and none
established.**
1. *Lossy + fully-deterministic ECDLP objects.* Obstruction: a factor of a
   transitive action is transitive, so a projection commuting with all
   translations of a prime-order group has image of size 1 or `N`. Forward
   guidance: three surviving classes (partial-action, branching,
   coordinate-dependent) with their cost obligations — `C(B+m−1,m)/N`,
   `log(budget)/log(b)`, `c·sqrt(N)/C_sim`. Nearby object where it must fail:
   composite order, where `Z/(ab) → Z/a` is lossy and deterministic
   (Pohlig–Hellman). `c5d183`.
2. *The partial-relation / large-prime escape over a prime field.* Obstruction:
   the rejection cost `R_w` per acceptance and the representation multiplicity
   `C(m, m/2)` per solution cancel exactly at `R_w = C(m, m/2)` and not beyond.
   Forward guidance: a-priori window restriction (which is
   constrained decomposition at half arity, i.e. `KN-OPEN-001` recursively), and
   any representation lever on the **linear-algebra** stage, which nobody has
   attempted. `20f6ab`.
3. *Summation polynomials as the binding object in prime-field decomposition.*
   Obstruction: on the factor-base locus the fibre's roots are group sums, so the
   algebra is redundant in the enumerate formulation; in the solve formulation
   the binding object is the membership predicate, bounded by
   `|F| ≤ 3 d_p` (`IDEA-20260801-021`). Forward guidance: the **partial locus**
   (one free coordinate), where complete splitting does not apply and which is
   genuinely open. `9d47e2`.

None of these is a claim that a direction is impossible, none rests on the object
enumeration being complete, and this session declined to generate nothing.

**Open directions for the next session.**
(a) Whether index calculus's own memory can be traded down the way the baseline's
can — the relation matrix is not obviously chainable and nobody has tried
(`3b91c7` forward guidance).
(b) The **partial locus** of the summation cover, where complete splitting is
silent and large-prime variants operate (`9d47e2`).
(c) Whether `d_solve` for a *prime-field* decomposition system is reachable at
all — the question ICEX actually needs and that no committed cell answers
(`7ea402`).
(d) A representation-style lever on the **linear-algebra** stage, where the
Amdahl ceiling says the remaining factor lives (`20f6ab`).
(e) Populating `c5d183`'s three classes: Class II objects with amortized
branching below the survival-depth bound, and Class III objects surviving
`KN-FIND-002`'s simulability screen at non-constant overhead — the only cell
where a sub-1/2 prime-field exponent can live.
(f) Two audit debts this session incurred and did not discharge: re-run the
`preprocessing|advice|precomputation` grep over `knowledge/` **uncapped** (it hit
40 files), and open `EV-SIG-008` and `EV-DREG-008` **at source** rather than
through `analysis/SSI-ECDLP-SYNTHESIS-20260803.md`.

## 5. What this session did not do

It ran no experiment, changed no status, approved nothing, promoted nothing to
`knowledge/`, and committed nothing. It resolves no open problem: `KN-OPEN-001`,
`-005`, `-009`, `-019` and `-020` are exactly where they were, and `c5d183`
supplies `KN-OPEN-019` with a candidate index set rather than a resolution. It
adjudicates novelty in neither direction, for any proposal. It advances no
exponent: `sota_delta` is zero on every ECDLP attack axis for all five records,
`dominated_by` is explicit in each, and Pollard rho at `0.886·sqrt(N)` remains
the baseline that nothing here claims to beat.

One identifier caveat, restated because it is a live risk: `tools/allocate_id.py`
could not be executed (no Bash tool). All five tokens were chosen **without
scanning committed state** and then verified free by a repository-wide grep
returning 0 matches. **The Coordinator must run
`python3 tools/allocate_id.py --check` on all five before the snapshot commit**;
on collision, supersede under a new id rather than rename (`AGENTS.md` rule 15).
