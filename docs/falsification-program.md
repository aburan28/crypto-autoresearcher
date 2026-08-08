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

## The two rules that make a falsification admissible

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

**2. Evidence only.** Every probe files evidence. None edits a finding, changes
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
11–103, all controls clean. `EV-FALSIFY-440677`. This is a non-refutation, not
a proof: the recorded proof sketch still argues "generic" and still concludes
"every", and uniform sampling would miss an exceptional locus of density below
~1/300.

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

### F-1b — KN-FIND-a1f3c2 over special families, and m ≥ 6 (D1)

F-1 sampled curves uniformly, which is the wrong sampler for an exceptional
locus. Re-run over families *enumerated as families*: j=0 and j=1728, CM by
small discriminant, full rational 2-torsion (`f` split), anomalous
(`#E = p`), supersingular, and curves with `j` in a prime subfield. Extend to
m=6 (degree 16), where the "independence of the quadratic extensions" step has
most to strain against. Same admissible-shape test, same null object.
**Refuted if** any enumerated family yields an inadmissible shape.
**Note:** a clean result here still does not repair the quantifier gap in the
recorded proof; it only removes the places a counterexample was most likely.

### F-5 — KN-FIND-c7d31e end-to-end cost (D4)

The speedup counts sweep work only. Re-cost with target generation and linear
algebra included. **Refuted if** the end-to-end advantage at realistic
relation counts falls below the quoted `(m+1)/2`. **Null:** set the sweep cost
to zero and confirm the model then reproduces exactly `(m+1)/2`, which
localises any discrepancy to the omitted terms.

### F-6 — KN-FIND-e7a3b1, "all six standard analytic methods are closed" (D5)

The corpus's own closure standard (`docs/inventor-protocol.md`) requires a
named obstruction, an argument, and forward guidance; a count of
screened-and-rejected approaches is a fatigue report whose honest status is
`unverified`, and that rule explicitly binds the program's own standing
closures. Audit each of the six against it. **Refuted if** any is supported
only by "we tried it and it did not work". Same audit for KN-FIND-7e4b90
(`proved_negative`, "blocked for ordinary prime-field ECDLP") and for
KN-OPEN-009's closure by KN-FIND-a1f3c2 — F-1 leaves that closure resting on an
argument whose quantifier step is unrepaired.

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

### F-8 — KN-FIND-9d2f56 / ff4a46, Betti-Yield "exact condition" (D1)

An exact-condition claim is an iff and fails if either direction fails.
Construct toy complexes on both sides of the stated threshold and check both
directions independently. **Refuted if** a complex satisfies one side and not
the other. Note that KN-FIND-ff4a46 is a *wording repair* of KN-FIND-9d2f56
carrying `confidence: proved`; a repair inherits the proof status of what it
repaired, and KN-FIND-9d2f56 is confirmed above as one of the nine D6 records
whose `proof_refs` name only itself.

### F-10 — Reproduce the corpus's own reported numbers (D2, highest yield per hour)

For every finding carrying a table, re-run the measurement from its recorded
parameters and compare. F-2 and F-3 both began here and both found the defect
in the first table they touched. This is the single highest-yield item in the
program and needs no new mathematics.

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
