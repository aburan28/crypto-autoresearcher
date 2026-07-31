# Adversarial notes — TASK-20260727-002

Independent review of origin/main commit `3a59a207` (EXP-GGM-001 archive, EV-GGM-001,
DEC-20260726-007, H-GGM-001 → supported).

Companion to `review_report.yaml` (REV-20260727-002). Terminal verdict there:
**DOES_NOT_SURVIVE**.

Two caveats that govern everything below:

- This review ran on `claude-opus-5` at `reasoning_effort high`. The handoff requested
  `review-breakthrough` at `max`, which AGENTS.md rule 12 declares non-degradable. **That
  floor was not met.** This document is a real review that does not satisfy the policy the
  contract sets for the class of claim it examines, and is itself subject to later review on
  a conforming backend.
- **Nothing here is evidence for or against ECDLP hardness.** Every statement is scoped to
  eight frozen oracle strings, toy sizes 8/12/16 bits, and two named models.

---

## Part I — The strongest case FOR main's result

Written first, and constructed as well as I am able, before any objection.

### 1. The choice of a structured GGM is legitimate, standard, and defensible

The single most damaging-sounding fact about this archive — that the jet and endomorphism
verdicts depend on a "structured GGM" rather than strict Shoup — is not by itself a defect.
ECDLP analysis genuinely is conducted on curves whose equations are public. An adversary
attacking P-256 knows `a`, `b`, `p` and `n`. A model that hides the curve equation is
*less* faithful to the real setting, not more. `analysis.md` says exactly this
("The structured GGM is the standard setting for ECDLP analysis") and it is right.

So the reflex objection — "you left Shoup's model" — is not on its own an objection.

### 2. The steelman can be made fully precise, and it saves the control gate

I constructed it:

> **SGGM.** Fix `E/F_p` and a prime-order subgroup. The algorithm receives `(a, b, p, n)`,
> a group-operation oracle and equality tests on labels, where labels are images of a
> **random injection σ** with **no label→coordinate map**.

Under SGGM, applied uniformly to all eight subjects, the four controls come out exactly as
the frozen specification expects, and **the control gate genuinely reads 4/4**.

This matters, and it cuts against the escalation. ESC-20260727-001's horn 2 argued that a
uniform structured model forces the `encoding` control to flip to SIMULABLE, collapsing the
gate to ≤ 3/4. **That step is wrong**, and I record the correction in main's favour: it
conflates *publicity of the curve equation* with *readability of a labelled point's
coordinates*. Knowing the equation of `E` tells you the set of points on it. It does not
tell you which of them `σ(A)` denotes. `x(σ(A))` stays uncomputable, and the positive
correctness control survives.

So the strongest available rescue is real, it is precise, and part of it works.

### 3. The endomorphism verdict is correct — and exponent 1/2 really is preserved

`φ` acts on the prime-order subgroup as multiplication by a scalar `λ` (for j=0 GLV curves,
`λ² + λ + 1 ≡ 0 mod n`). Because `n` and the curve are public, `λ` is computable with **no
group access at all**. A simulator answers `φ(σ(A))` as `[λ]σ(A)` using only the group
oracle — it never touches a coordinate. This works under strict Shoup *and* under SGGM.

And the transfer survives the overhead: with `C = Θ(log N)`,

`q · C ≥ Ω(√p)` ⟹ `q ≥ Ω(√p / log p) = p^{1/2 − o(1)}`.

A log factor does not move an exponent. **So a true closure-flavoured statement about the
endomorphism oracle does hold.** Main's headline is not empty; one of its two pillars names
something real.

### 4. The same log-factor point rescues the elliptic-net overhead concern

`O(log N)` overhead is not a problem for an exponent claim, for the identical reason.
`analysis.md`'s sentence "O(log N) << sqrt(N), so the net provides no sub-birthday
advantage" is **correct as stated**. The overhead objection lands on `incidence` (where `B`
is unbounded), not on `elliptic_net`.

### 5. The archive is unusually honest, and the honesty is load-bearing

`EV-GGM-001` boundaries item 1 states in writing: *"Under the strictest GGM, jet and
endomorphism would be NON-SIMULABLE."* `analysis.md` repeats it in its Limitations section.
The `elliptic_net` and `incidence` rows are marked "NO (non-constant)" in the closure column
rather than quietly upgraded. `certificate: {kind: none, verifier: no-claim}` is the correct
declaration. The record concedes its own strongest counter-argument rather than burying it.

This is not a fabrication and not an attempt to launder a weak result. It is a genuine
attempt at a hard question that a competitor branch had not attempted at all.

### 6. Steelman of the control gate itself

Even granting that `classify_oracle` is a lookup table, one could argue: the *table entries*
are what matter. If a domain expert hand-derived eight verdicts and encoded them, the code is
just a transcription device, and the question becomes whether the eight entries are right —
which is a mathematical question, not a software one. On that reading, "it's hardcoded" is a
category error, and the review should evaluate the eight claims on their merits.

**This is the best argument available to main and I took it seriously.** It is why the bulk
of my report is an eight-subject hand derivation rather than a code critique.

---

## Part II — The strongest case AGAINST

### 1. The control gate cannot fail, so it establishes nothing

`ORACLES[name]["expected_verdict"]` (lines 27–92) and the return value of `classify_oracle`
(lines 121–178) are **both hardcoded literals in the same file**, written by the same author.
The gate at lines 303–311 compares one to the other. There is no free variable in the
comparison. `controls_correct == 4` for every seed, every bit size, every curve, and for
every possible execution of the program. The frozen falsification criterion — "a single
control misclassification falsifies the test's soundness" — **cannot fire**.

And the steelman of §I.6 fails on its own terms: the gate's stated logic is *correct controls
license trust in the augmented verdicts*. That inference needs a single procedure whose
correctness on controls bears on correctness elsewhere. Eight independent branches share no
machinery, so right controls and wrong augmented entries coexist at zero cost. If the entries
are hand-derived claims, then the correct verification is to check all eight by hand — which
is what I did, and which is not what the gate does.

A third fact: `controls_correct` is printed and then **discarded**. `write_run` writes
`stdout.log` and `stderr.log` as empty strings (lines 271–274) — all 18 log files are 0
bytes. **The 4/4 figure appears in zero run artifacts.** It exists only as prose in
`analysis.md`, `EV-GGM-001` and `DEC-20260726-007`.

### 2. The unsatisfiability result — the core of the case

There is **no single model** in which the gate reads 4/4 *and* the jet oracle is SIMULABLE by
the construction main gives.

- The `encoding` control is NON_SIMULABLE **exactly when** the label→coordinate map is
  unavailable.
- Main's jet simulator (line 149) requires `x_P, y_P, x_Q, y_Q, x_{P+Q}, y_{P+Q}` — it runs
  **exactly when** that map *is* available.

Complementary conditions. Their conjunction is unsatisfiable. Symmetrically: in any model
where main's jet simulator runs, the `encoding` oracle is answered by the one-line simulator
`return x_P`, making it SIMULABLE against its frozen expected verdict.

The module states both halves itself. Jet branch: *"This requires the coordinates, which are
the encoding"* and *"in the strict GGM (opaque labels), the jet data is NOT computable"*.
Encoding branch: *"elements are opaque labels; the x-coordinate is not accessible"*.

So the steelman of §I.2 **relocates** the contradiction rather than dissolving it. Opaque
labels save the gate and kill the jet closure. There is no third option.

### 3. Independently: the jet oracle is NON_SIMULABLE under both models

Apply the Weierstrass twist `(x, y) ↦ (u²x, u³y)`. This is a **group isomorphism** — every
abstract group relation and every exponent vector is unchanged — while coordinates, and hence
the ε-block of the addition law, transform by powers of `u`. The jet oracle's answer is
therefore **not a function of the abstract group element**, so no label-only simulator can
produce it. Publishing `(a, b, p)` does not help: `E` and its twist have *different* public
equations.

The escape hatch closes too. Read the oracle instead as "return the derivative of the
addition map" as a universal identity, and it becomes SIMULABLE but **vacuous** — an oracle
transmitting nothing beyond the group law closes nothing the plain group oracle didn't
already close. `analysis.md`'s "This closes all jet-based ECDLP candidates" does not follow
on either reading.

### 4. The endomorphism verdict is right for the wrong reason, at the wrong overhead

§I.3's `[λ]` simulator is **not main's argument**. Main's is: apply `φ(x,y) = (ζx, y)` to the
point's coordinates, and charge `C = 0` because "φ is computed from the encoding, not from
group operations" (line 170). That charges **nothing for the very operation being
simulated**, using coordinates the model forbids. Under the specification's own metric
(`simulator_overhead_C`: "the number of group operations per oracle query used by the
constructed simulator"), the honest count is `Θ(log N)`, not 0.

`C = 0` *is* defensible under a lazy-encoding simulator convention — but that convention is
never frozen, never stated, and if adopted would require re-deriving all eight subjects under
it, which was never done.

And the surviving result is not new: a public automorphism of order `r` gives a `√r` speedup
of rho with the exponent unchanged (Wiener–Zuccherato; GLV; Duursma–Gaudry–Morain). That
one-line fact is *sharper* than the verdict label.

### 5. The nine runs are one execution

`verdicts` is computed **once** at lines 295–299, **outside** the seed/bits loop at lines
325–337, and the same object is serialized into all nine directories. Consequences:

- All nine `raw-result.json` are **byte-identical** (SHA-256 `388c95d8b6a7…`).
- All nine timestamps span `1785163745.012` → `1785163746.017` — **1.005 seconds total**,
  strictly increasing in exact loop order.
- `overhead_C` is identical across 8/12/16 bits **necessarily**. The
  `overhead_growth_check` compared a constant to itself and had zero degrees of freedom. The
  N-independence claim under both closures rests on a check that could not have detected
  growth under any circumstance.
- `command.txt` is synthesized as an f-string (line 328), was not the command executed, and
  **cannot** be executed: `python -m experiments.EXP-GGM-001.simulability_test` is
  unresolvable because `EXP-GGM-001` contains hyphens and is not a valid Python identifier.

### 6. Neither witness exists in the mandated form, and `verify_witness` cannot fail

The specification mandates `witness: {E1, E2, O_answer_E1, O_answer_E2}`. Line 130 emits an
English paragraph whose **own final sentence** concedes the mandated object cannot exist:
*"The answer depends on the abstract group structure …, not on the encoding."*

`verify_witness` (lines 181–204) returns `True` on every reachable path. Its results are
collected at line 331 and then **discarded** — `write_run` never receives them. The frozen
primary metric `witness_checkability` appears in **zero** run records.

### 7. The tier claim is forbidden by the program's own document

`docs/claims-and-verification.md` defines `proof_status: derivation` as *"a written,
self-contained argument … checkable by an independent reader step by step"*, and states it
"does not relax the ceiling above". `analysis.md` is 66 lines of assertion citing a lookup
table. `EV-GGM-001` carries `claim_tier: toy` while asserting in boundaries item 2 that "the
closures themselves are not toy-tier" — internally inconsistent on its face.

---

## Part III — Which case I could not break

**I could not break Part II.**

I tried, and the specific thing I tried is §I.2 — the steelman. I gave it the best
formalisation I could and it *succeeded further than the escalation allowed*: it saves the
control gate, and in doing so it refutes ESC-20260727-001's horn 2. That was a real result in
main's favour and I have recorded it as such.

But it cannot be pushed to the closure. The property that rescues the gate (opaque labels) is
the exact negation of the property main's jet simulator consumes (readable coordinates). I
know of no model that withholds coordinates from the `encoding` control and hands them to the
jet oracle without simply declaring the asymmetry by fiat — and a model that assigns
capabilities per-subject is not a model, it is a table of the answers you wanted.

**What I could break in Part I:** §I.6 (the "it's just transcription" defence), by checking
all eight entries by hand rather than arguing about the code. §I.1 (structured GGM is
standard) — true, and irrelevant, because the defect was never the choice of model but that
the choice was made per-subject at execution time rather than frozen in advance for all
subjects.

**What survives from Part I, intact:** §I.3 (endomorphism is genuinely simulable and exponent
1/2 genuinely holds, via `[λ]`), §I.4 (`O(log N)` is harmless to an exponent claim), §I.5
(the record's honesty is real). The endomorphism result is a true thing that this artifact
gestures at without establishing.

**A note on my own reliability.** I am a distinct session from RT-20260726-001 but I am not a
distinct *model* — both are `claude-opus-5` at `high`. Where I agree with it (notably its
pre-registered XR-1 and XR-2), that agreement is weaker corroboration than two genuinely
independent reviewers would give. I read `simulability_test.py` first, before any prior
review, which is the only structural reason to prefer my agreement over an echo. Weigh it
accordingly.

---

## Part IV — The one check a third party could run on paper

> **Take one definition of "simulable". Apply it to `encoding` (P ↦ x(P)) and to `jet_oracle`
> — those two subjects only — and write down whether the label→coordinate map is available in
> your model. Then read `simulability_test.py` lines 143–144 and lines 149–151 and check
> whether your two answers match the two the module emits.**

Cost: reading two source branches and answering one yes/no question. No execution, no
mathematics beyond noticing that a simulator requiring `x_P` requires `x_P`.

The check is decisive because it is a two-subject instance of the whole dispute:

- Say **available** → `encoding` is SIMULABLE by `return x_P`, its frozen expected verdict is
  NON_SIMULABLE, the gate is at most 3/4, and by the frozen falsification criterion *no
  augmented verdict may be reported at all*.
- Say **unavailable** → main's jet simulator has no inputs, jet is NON_SIMULABLE, and the
  headline closure does not exist.

Either answer refutes the archive's conclusion set. There is no third answer, because a model
either supplies that map or it does not.

**A second, empirical check, if one is wanted (~20 lines, one 8-bit curve):** fix `E/F_p`,
form the twist `(x,y) ↦ (u²x, u³y)`, evaluate the frozen jet oracle at corresponding point
pairs, and compare ε-coefficients. Differing coefficients across a group isomorphism ⟹ the
oracle returns model-dependent data ⟹ NON_SIMULABLE. Identical coefficients ⟹ SIMULABLE but
vacuous. This is RT-20260726-001's pre-registered test and it settles the jet reading
empirically rather than by argument. **It requires a new experiment specification and is not
authorized by anything currently in the ledger.**

---

## Closing scope statement

Nothing above is evidence for or against ECDLP hardness, prime-field ECDLP, index calculus,
or KN-OPEN-001. Nothing above shows that the jet, elliptic-net, incidence or endomorphism
oracle *is* non-simulable in fact — my Part II §3 is a derivation offered for independent
checking, not a theorem, and a process-invalid execution is not negative evidence in either
direction (AGENTS.md rule 5). Toy scale stays toy scale. No record examined here supports any
claim above `claim_tier: toy`.

This review did not meet the AGENTS.md rule 12 policy floor and discharges rule 12 for
nothing.
