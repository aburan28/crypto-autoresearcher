# RED-TEAM REPORT — H-DREG-001 n=17 audit (TASK-20260720-DREG-AUDIT)

Role: Red Team. I attack the *interpretation* of the certified n=17 result and recommend
(not decide) a verdict. Receipt integrity is not my job — the Validator's
`VAL-20260720-DREG-AUDIT` already recomputed every hash and reconciled every metric
(`receipt_integrity: verified`, six checks pass, no material defect). I take the numbers
as clean and ask only what they are allowed to mean.

All quantitative claims below are grounded in: `ledger/EV-DREG-001.yaml`,
`ledger/EV-DREG-002.yaml`, `ledger/EV-DREG-003.yaml`, `ledger/EV-SIG-003.yaml`,
`ledger/EV-SIG-004.yaml`, `ledger/H-DREG-001.yaml`, `ledger/H-SIG-001.yaml`, the
`VAL-20260720-DREG-AUDIT` report in this directory, and raw run receipts under
`experiments/EXP-SIG-005/runs/` (a residual_6 measurement not yet certified into a
ledger EV file — see §4).

---

## 1. Summary + recommended verdict

**Recommended verdict: `inconclusive` (trending `weakened`; an explicit KILL is NOT yet
earned).**

The tempting "tracks the null / no speedup / scoped KILL" reading is the better-supported
*direction*, but it does not clear the KILL bar, and its single strongest talking point
("relative deficit → 0") is its weakest logically. The opposite "lurking speedup" reading
has no positive quantitative support along the n-axis, but is not dead along the *degree*
axis, which is barely probed. The decisive observable — the rank deficit (and, ideally,
whether d_reg is reached) at **D = 6 at a standard, on-lattice size (n = 12)** — is
unmeasured; the only D = 6 residual point that exists is at **n = 9, the documented
anomalous size**, and it shows the two relevant observables *disagreeing*.

Evidential bar for each candidate verdict, and why only `inconclusive` is currently
justified:

| Verdict | Bar it requires | Met? |
|---|---|---|
| `supported_scoped` | A positive, replicated, *growing* invariant: deficit super-linear in n (CI excludes exponent 1 from below) **or** `d_reg(sem) < d_reg(null)` on some measured cell **or** a degree-concentrated deficit that lowers a *measured* d_reg. | **No.** No measured super-linear n-growth; no d_reg measured anywhere; degree axis has one point, at the anomalous size. |
| `rejected_scoped` (KILL) | H-DREG-001's own KILL clause: `d_reg(sem)` tracks the null within CIs at a reachable n (requires an actual d_reg measurement) **or** the deficit demonstrably asymptotically irrelevant to the first-fall degree. | **No.** d_reg is *not reached at D = 5* for either arm (sem 125,099 < nrows 132,719; null 126,922 < 132,719), so the KILL clause is not evaluable. Declaring KILL now converts a fixed-degree D = 5 proxy into a d_reg result — forbidden by AGENTS rule 6 and the d_reg-not-reached caveat. |
| `weakened` | The sub-rho scenario has lost its best evidence and the burden has shifted to a specific, still-open mechanism. | **Defensible in spirit** — see §2–§4 — but premature to stamp before the one cheap degree-axis cell at standard size is run. |
| `inconclusive` (current) | Decisive observable unmeasured; existing cells under-determine the sign of the effect. | **Yes — the honest label.** |

Net: recommend the Coordinator **hold `inconclusive`**, record that the evidence has
shifted the burden toward the KILL side along the n-axis while the degree axis remains
open, and gate any status change on the single measurement named in §4/§6.

---

## 2. Attack on the "tracks-null / no-speedup" reading

### Steelman (the seductive KILL)
1. Relative deficit `deficit/rank` is **monotone decreasing**: 4.71% / 2.70% / 1.46% /
   1.39% at n = 12/15/17/18 (recomputed exact by the Validator).
2. Absolute increments **decelerate**: +540 (12→15), then small moves (−39, +176).
3. On the mod-3 lattice the within-wall series was already decelerating (+540 then +137
   at n = 12→15→18, `EV-DREG-001`).
4. The D4 syzygy law is only **linear**: residual = 2n/3 + 1 and deficit_4 = 8n/3,
   confirmed with zero seed variance through **n = 24** (`EV-SIG-004` + the confirmed
   n=24 point). Linear structure is asymptotically negligible against a rank that grows
   like C(2n, ≤5) ~ n^5.
5. residual_5 increments decelerate: 344 → 878 → 1158 at n = 9/12/15, increments
   +534 then +280.
   ⇒ structure asymptotically negligible ⇒ sub-rho scenario dead ⇒ scoped KILL.

### Break

**B1 — "Relative deficit → 0" is nearly a tautology and is the *wrong* invariant.**
The Macaulay column count grows like C(nb, ≤5) with nb = 2n, i.e. ~ n^5. *Any* deficit
that grows slower than n^5 — including a deficit growing linearly, quadratically, or
even quartically in n — forces `deficit/rank → 0`. So relative shrinkage is compatible
with a polynomial-in-n deficit, which is exactly the kind of structure a sub-rho scenario
could ride. Meanwhile the **absolute** deficit is net-growing (1,322 → 1,999) and, on the
mod-3 lattice, **monotone increasing** (1,322 → 1,862 → 1,999). The invariant that
matters for d_reg is not a ratio against a quintically-growing denominator; it is whether
the extra-syzygy content is enough to move the *first-fall degree*. The KILL's headline
plank is its logically weakest.

**B2 — Four points, and the one that creates the "non-monotonicity" is OFF the syzygy
lattice.** Residues mod 3: n = 12 ≡ 0, 15 ≡ 0, 18 ≡ 0, but **n = 17 ≡ 2**. Every SIG
cascade law is stated for n ≡ 0 mod 3 (counts 8n/3, 2n/3+1 are integers only then); the
whole SIG measurement ladder is n ∈ {9,12,15,18,21,24}. **n = 17 is the single DREG point
that lies off the lattice on which the deficit-generating syzygy family is defined.** The
−39 "dip" that makes the series "non-monotone" and licenses the deceleration read sits
*exactly* at that off-lattice point. Comparing n = 17 to n = 15 and n = 18 as if they lie
on one smooth curve is comparing an off-lattice residue class to on-lattice points. Drop
n = 17 and the on-lattice subsequence 1,322 / 1,862 / 1,999 is monotone increasing. The
"non-monotone deceleration" is, to first order, a mod-3 commensurability artifact — not a
law about the deficit.

**B3 — The parity precedent is direct evidence that this system class produces
integer-scale n-residue anomalies.** `EV-SIG-004` documents an exactly-**+1** rank defect
of the early-break reduction at n = 9/15/21 (n/3 odd) and 0 at n = 12/18 (n/3 even) — an
unexplained n/3-parity effect. Caveat, stated plainly: that +1 is an *instrument
reduction* artifact (corrected under canonical `full_reduce` in `EV-SIG-004`), **not** the
Macaulay deficit itself, and n = 17 is not divisible by 3 so it has no defined value of
that specific defect. But the precedent still bites: it establishes that n-mod-3 structure
produces integer-level anomalies in *this exact system family*, so treating a ~39-unit
wiggle at an off-lattice n as signal (in either direction) is unsupported.

**B4 — The residual_5 "deceleration" leans on the anomalous n = 9 point.** The +534→+280
deceleration uses the n = 9 → n = 12 increment, and n = 9 is the *documented anomalous
size*: residual_4 = 24 (vs the law's 2n/3+1 = 7) and deficit_4 = 41 (vs 8n/3 = 24), both
replicated on 3 seeds (`EV-SIG-004`). On the lattice you have only one clean interval
(n = 12 → 15, +280): a single increment cannot establish deceleration.

**B5 — Deceleration ≠ boundedness ≠ irrelevance to d_reg.** Even a strictly decelerating
but *unbounded* deficit (∝ n, or n log n) keeps supplying extra low-degree syzygies and
can keep lowering the first-fall degree relative to a semi-regular null. The KILL requires
the deficit to be asymptotically irrelevant to d_reg, which is a claim about d_reg — and
**d_reg is not measured**: at n = 17, D = 5, *neither* arm reaches full row rank (row
deficits 7,620 for sem, 5,797 for null). The entire ladder is a fixed-degree D = 5 proxy
that sits *below* d_reg. Reading "no super-linear growth of a D = 5 proxy" as "no d_reg
effect" is precisely the inference AGENTS rule 6 (negative evidence closes only the exact
tested scope) forbids.

**Verdict of §2:** tracks-null is the better-supported direction but does **not** clear
the KILL bar; its strongest-sounding evidence (relative → 0, the n=17 non-monotonicity) is
either tautological or an off-lattice artifact.

---

## 3. Attack on the "lurking speedup" reading

### Steelman (a real speedup hiding past the wall)
1. The **absolute** deficit is net-growing (1,322 → 1,999) and monotone increasing on the
   mod-3 lattice.
2. `EV-DREG-002` states explicitly that a phase transition at n ≥ 21 **cannot be
   excluded** from four points.
3. The cascade is **much larger in the degree direction**: residual_5 ≈ hundreds–thousands
   vs residual_4 ≈ 9–15; and residual_6 = 2,615 ≫ residual_5 = 344 at n = 9 (raw
   `EXP-SIG-005` run h). The birth law (a new non-rewritable component at every degree)
   holds at D = 6.
4. d_reg is unmeasured and could be lower for the Semaev arm.
5. Independent structural signature: sem Macaulay column support shrinks 84.2 → 82.2 →
   81.9 → 80.8% (n = 12/15/17/18) while the null stays at 100% (`EV-DREG-001`,
   `EV-DREG-002`) — the ideal is genuinely non-generic.

### Break

**B6 — The confirmed LINEAR D4 law is a hard constraint against fast n-growth.** residual =
2n/3 + 1 and deficit_4 = 8n/3, now confirmed through **n = 24** with zero within-size seed
variance over 3–5 seeds/size across n = 12..24 (`EV-SIG-004` + n=24 confirmation). A linear
law that survives eight sizes is not a small-sample coincidence; the D4 cascade demonstrably
does not accelerate in n.

**B7 — No measured syzygy quantity grows super-linearly in n.** residual_5 decelerates
(+534 → +280); deficit_5 grows sub-quintically; the whole point of B1 is that relative
deficit → 0. The n-axis speedup case has *zero* positive quantitative support.

**B8 — The degree-direction growth reads the WRONG observable.** residual_D is a
syzygy-module dimension, and `EV-SIG-003` proved rank-wise that **residual ≠ deficit**:
at n = 12 residual_5 = 878 but deficit_5 = 1,321 (the residual is a strict *component* of
the deficit, not the deficit). Syzygy-module dimensions inflate combinatorially with the
ambient monomial count as D rises, so "residual_6 ≫ residual_5" is expected regardless of
any d_reg effect. The quantity that actually maps to rank / d_reg is the *deficit*, and at
the one place we can watch it climb the degree axis — n = 9, from raw `EXP-SIG-005` run h —
the **deficit turns over**: deficit_4 = 41, deficit_5 = 909, **deficit_6 = 776** (909 → 776
is a same-instrument, same-n *decline*). The system approaches column-rank saturation at
D = 6 (rank 27,292 of 29,332 columns) and its shortfall below semi-regular *shrinks*. So
the "cascade explodes in degree" story inflates the residual while the d_reg-relevant
deficit is turning over. (Caveat: single point, anomalous size — see §4.)

**B9 — "Cannot be excluded" is not "is indicated."** The phase-transition escape is
unfalsified, not evidenced. Every measured law — linear D4, decelerating D5,
relative-deficit → 0, and (at n = 9) a deficit that turns over at D6 — points away from a
resumed climb. Invoking n ≥ 21 is an appeal to the unmeasured.

**Verdict of §3:** the speedup reading has no positive n-axis support; its only live hope
is the degree axis, and the single degree-axis probe we have *undercuts* it — but that
undercut rests on one anomalous size, so it does not close the question either.

---

## 4. The degree axis and the decisive missing measurement

**Why this is the real crux.** d_reg is the smallest degree D at which the Macaulay matrix
first becomes solvable (Hilbert-series first fall). The direction of the effect matters and
is worth stating precisely: extra non-Koszul syzygies at degree ≤ D are exactly what the
rank deficit counts, and they pull the *first fall* to a lower degree — i.e. a deficit that
is **concentrated in, and growing along, the top degree** could lower d_reg **even if the
per-n growth is slow**. So the hypothesis is genuinely alive on the degree axis in a way it
is not on the n axis. The slow-in-n / fast-in-D structure (residual_4 linear-small;
residual_5 hundreds–thousands; residual_6 = 2,615 at n = 9) is precisely the profile that
*would* matter if it were the deficit and if it persisted at standard sizes.

**What the evidence actually establishes on the degree axis — and what it does not:**

- The only complete degree column is at **n = 9** (raw `EXP-SIG-005` run h, not yet in a
  ledger EV file): residual_4 = 24, residual_5 = 344, residual_6 = 2,615 (birth law
  residual_6 > 0 holds); and the *deficits* are 41 / 909 / 776.
- Three problems with leaning on it:
  1. **n = 9 is the documented anomalous size** (residual_4 = 24 vs law 7; deficit_4 = 41
     vs 24). The one degree column we have is the *least* representative size in the ladder.
  2. **residual ≠ deficit** (`EV-SIG-003`). The fast-growing object (residual_D) is a
     component of, not equal to, the d_reg-relevant object (deficit_D).
  3. At n = 9 the two observables **disagree**: residual_6 is large and growing in D, but
     deficit_6 (776) is *below* deficit_5 (909). The pro-speedup signal (residual) and the
     anti-speedup signal (deficit turnover) point opposite ways, and the deficit is the one
     that maps to d_reg.
- **residual_6 / deficit_6 at a standard size does not exist.** `EXP-SIG-005` runs g
  (n = 12) and j (n = 18) reached only D5 / D4 respectively and were stopped before the
  expensive D6 stage; no `EV-SIG-005.yaml` is filed yet. So the degree axis is probed at
  exactly one size, and it is the wrong one.
- **No d_reg is measured anywhere.** Every cell (DREG and SIG) sits below full row rank at
  its top degree. The ladder is entirely fixed-degree.

**Conclusion:** the current evidence does **not** rule out a degree-concentrated,
d_reg-lowering effect — it barely probes it, at the anomalous size, with the pro/anti
observables in conflict. This is the specific reason a KILL is unearned.

**The single measurement that would most change the verdict:**

> **D = 6 at n = 12 (standard, on-lattice), both arms — specifically the rank *deficit*
> (deficit_6, not just residual_6) and whether full row rank / first fall is reached.**

Concretely: finish `EXP-SIG-005` run g's censored D6 stage to get residual_6/deficit_6 at
n = 12, and — higher value — run the **DREG block-m4ri D = 6 rank deficit at n = 12** on
H-DREG-001's own instrument and success metric (the prediction explicitly covers D ≤ 6).

Why this one, ranked against the alternatives the task named:
- **residual_6 at n = 12** tests whether the n = 9 degree column (24/344/2,615;
  41/909/776 turnover) is a size-9 artifact or a real degree law, at a non-anomalous size.
  This is the direct falsifier of the degree-axis speedup.
- **DREG D = 6 deficit at n = 12** is strictly more decisive: it is measured on the exact
  H-DREG-001 instrument and metric, and it is the first genuine chance to see whether
  **d_reg is reached at D = 6** (full row rank) — the first actual d_reg datum in the whole
  program. If deficit_6(n=12) > deficit_5 = 1,321 and rising, the degree route is alive and
  the verdict must stay open (or reopen toward supported). If deficit_6(n=12) < deficit_5
  (turnover, as at n = 9 but now at a standard size), the degree route is closing and a
  KILL becomes defensible.
- **The n = 21 D = 5 deficit** (costed at 7–9 h) mostly tests the n-axis phase transition —
  which the linear D4 law and decelerating D5 already constrain — and stays *below* d_reg
  (still fixed-degree). Lower information per compute-hour than a D = 6 standard-size cell.

---

## 5. Scope and caveats (what none of this is allowed to claim)

- **Toy scale.** DREG: n ≤ 18 measured past-wall only at n = 17/18, D = 5, single seed
  (2026), single target, ti = 0, m = 3, t = 3, one curve family. SIG cascade: n ≤ 24 at
  D ≤ 4; D = 5 at n ≤ 15; D = 6 at **n = 9 only**. AGENTS rule 7: none of this is
  crypto-scale validation.
- **Fixed-degree, not d_reg.** The certified 1,823 at n = 17 is a rank deficit at a *fixed
  degree D = 5*, with both arms below full row rank (Validator check 4). It is **not** a
  measured solving-degree difference. `d_reg(sem) < d_reg(null)` and `gap(n) = d_reg − d_ff`
  are *not evaluable* from any current cell. d_ff has only 2 resolved samples (values 3, 2)
  at n = 12; the hypothesis's own gap(n) metric is unmeasured.
- **residual_6 is uncertified.** residual_6 = 2,615 is a raw `EXP-SIG-005` run-h receipt
  with no `EV-SIG-005.yaml` and no Validator sign-off; it is one size, and that size is
  documented anomalous. Treat it as provisional, not as ledger evidence.
- **mod-3 commensurability confound.** The deficit-generating syzygy family lives on
  n ≡ 0 mod 3; n = 17 ≡ 2 is off-lattice. Any cross-n comparison that routes through n = 17
  is confounded and must not be read as a smooth trend.
- **AGENTS discipline.** Rule 5: the cancelled NULL-B parent and every censored D6 stage
  are infrastructure censoring, not evidence either way. Rule 6: a KILL here would be "no
  sub-rho signal at n ≤ 24, D ≤ 5, seed family 2026," never a theorem. Rule 7: toy ≠
  crypto-scale. Only the Coordinator sets status.

---

## 6. Falsification routes / next measurements, ranked by information gain

1. **[Highest] D = 6 at n = 12, standard size, both arms.** DREG block-m4ri rank deficit
   (Does deficit_6 exceed deficit_5 = 1,322? Is full row rank / first fall reached — the
   first d_reg datum?) *and* finish the censored SIG-005 run-g D6 stage
   (residual_6/deficit_6 at n = 12). First test of the degree axis at a non-anomalous size;
   first possible d_reg point. Decides supported-vs-KILL more than anything else.
2. **D = 6 at n = 15, standard.** Second on-lattice degree-axis point; confirms or refutes
   any turnover seen at n = 12. Expensive on the SIG instrument (pre-measured ~547k × ~768k
   per `EXP-SIG-005` spec); the DREG instrument may be the cheaper route.
3. **n = 21 and n = 24 D = 5 deficit (DREG).** Tests the n-axis phase transition
   `EV-DREG-002` flags. Lower marginal information: the linear D4 law + decelerating D5
   already predict continued deceleration, so this is mostly confirmatory; n = 21 costed
   7–9 h.
4. **Replicate the deficit series across ≥ 3 curves / additional seeds at fixed n
   (12, 15).** DREG is currently single-seed (2026); the −39 dip at n = 17 has no error bar.
   Tests whether the deficit and the dip are instance-stable or noise.
5. **Direct d_ff / d_reg first-fall ladder at n = 12, 15 with ≥ 8 targets.** Measures the
   hypothesis's own gap(n) = d_reg − d_ff object rather than a fixed-degree proxy; currently
   only 2 d_ff samples exist. Slow, but it is the only route to the metric the success
   clause is actually written in.

---

### One-line recommendation

**Verdict: `inconclusive` (trending `weakened`; KILL not earned) — the n-axis speedup case
is quantitatively empty, but d_reg is unmeasured and the degree axis is probed only at the
anomalous n = 9, so a scoped KILL would over-read a fixed-degree D = 5 proxy.**

**Highest-value next measurement: the D = 6 rank *deficit* at n = 12 (standard size) on the
DREG block-m4ri instrument — the first non-anomalous test of the degree axis and the first
chance at an actual d_reg point.**
