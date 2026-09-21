# Validator notes — TASK-20260803-90327f

**What I recomputed, and how.** Independent session. I did not produce the
package under review and did not run, import, or repair any of its files.
Every number below came out of a script I wrote, against a clone of the
estimator I made myself.

Reviewed object: snapshot commit `7afc38466bb697ac309a89a49e92f396393a5e73`,
parent `072629728d35a5a432cf080851b28a0c07844f99`, six declared paths.

> All figures here are **cost-model estimates**, never measurements. No ML-KEM
> break is claimed or implied, and a charge that *raises* an estimated attack
> cost is not a security proof. AGENTS.md rule 12 is UNMET and UNWAIVED;
> nothing here touches EV-MLKEM-011, EV-MLKEM-013, EV-MLKEM-017, KN-FIND-012 or
> KN-FIND-014.

---

## 0. Instrument set up from scratch

```
git clone https://github.com/malb/lattice-estimator <scratch>/le
git -C <scratch>/le checkout 3e48ef421ec256afddb3e7d2249a77eab6e9ba12
git -C <scratch>/le rev-parse HEAD
  -> 3e48ef421ec256afddb3e7d2249a77eab6e9ba12
  (Sat Jun 27 10:55:47 2026 +0100, "Merge pull request #218 ...")
```

Integrity of the reviewed bytes, checked before reading them: `sha256sum` on
all six declared paths reproduces the six `path_sha256` values recorded in the
archive block, and the four `artifact_sha256` entries inside `receipt.json`
agree as well. `git diff HEAD` is clean on all five producer artifacts. The
only working-tree change under BATCH-010 is `dispatch_queue.json` — Coordinator
bookkeeping (task states, archive hashes), not producer content.

## 1. Known-answer control — I ran it, I did not copy it

```
$ PYTHONPATH=<repo>/tools/sage_free_estimator/shim:<scratch>/le \
    python3 tools/sage_free_estimator/known_answer_control.py
set             log2(rop)          reference      delta  beta   eta      d
Kyber512   140.1994731076     140.1994731076   0.00e+00   389   422   1005
Kyber768   200.9587149141     200.9587149141   0.00e+00   606   640   1420
Kyber1024  270.7236234535     (no reference)         --   855   889   1867

PASS: every reference value reproduced exactly (delta 0.0) against
lattice-estimator 3e48ef421ec2.
[VALIDATOR control exit code: 0]
```

Claim C1 **reproduced**, including all nine β/η/d values.

## 2. Independent re-derivation of β, η, d, and the cost decomposition

My script calls `primal_bdd(p, red_cost_model=RC.MATZOV)` and then re-derives
both cost terms from the reduction model rather than reading the estimator's
own fields:

| set | β/η/d | log2 rop | red+svp−rop | log2 MATZOV(β,d) vs red | log2 [MATZOV(η+1,η+1)+babai(d−η)] vs svp |
|---|---|---:|---:|---:|---:|
| Kyber-512 | 389/422/1005 | 140.1994731076 | `0.0` | Δ `0.000e+00` | Δ `0.000e+00` |
| Kyber-768 | 606/640/1420 | 200.9587149141 | `0.0` | Δ `0.000e+00` | Δ `0.000e+00` |
| Kyber-1024 | 855/889/1867 | 270.7236234535 | `0.0` | Δ `0.000e+00` | Δ `0.000e+00` |

Terms: red 139.1087303309 / 199.9092057208 / 269.8125061574; svp
139.2848445191 / 200.0065813127 / 269.6289031804.

Margins against the cutoffs 143 / 207 / 272: **+2.800527 / +6.041285 /
+1.276377**. Reproduced.

## 3. THE LOAD-BEARING CHECK — the sieve dimension

**Finding: the producer is right, and it is right for the reason it gives.**

I read all five cited lines in my own clone. Every one is a verbatim match:

- `lwe_primal.py:465` — `bkz_cost = costf(red_cost_model, beta, d)`
- `lwe_primal.py:482` — `eta = svp_dim if params._homogeneous else svp_dim - 1`
- `lwe_primal.py:488` — `svp_cost = costf(red_cost_model, svp_dim, svp_dim)`,
  directly under the comment `# we make one svp call on a lattice of rank eta + 1`
- `lwe_primal.py:490` — `svp_cost["rop"] += PrimalHybrid.babai_cost(d - eta)["rop"]`
- `reduction.py:800` — `beta_ = beta - self.d4f(beta)`, with the gate count at
  `:808` being `C * 2 ** (a*beta_ + b)`

The step that actually makes the d4f claim binding is the inheritance, and the
producer states it without showing it, so I checked it programmatically:

```
type(RC.MATZOV).__mro__  ->  MATZOV -> GJ21 -> Kyber -> ReductionCost -> object
'__call__' in MATZOV.__dict__ : False
'__call__' in GJ21.__dict__   : False
'__call__' in Kyber.__dict__  : True
RC.MATZOV.nn                  : 'list_decoding-classical'
```

So `RC.MATZOV(β, d)` really does execute the `reduction.py:800` path and really
does sieve in the d4f-reduced dimension. **Confirmed.**

I also checked the "single final call" part, which the producer asserts but
does not quantify. Inside `Kyber.__call__`, `svp_calls = C·max(d − β, 1)`:

| set | BKZ term: C·(d−β) sieve calls | SVP term: C·max(0,1) |
|---|---:|---:|
| Kyber-512 | 3319.53 | 5.3888 |
| Kyber-768 | 4386.52 | 5.3888 |
| Kyber-1024 | 5453.51 | 5.3888 |

The final call is invoked as `costf(model, svp_dim, svp_dim)`, so `d − β = 0`
and the multiplier collapses to `C` — one sieve. The producer's description is
accurate.

Dimensions:

| set | β | η+1 | d4f(β) | d4f(η+1) | BKZ sieve dim | SVP sieve dim | peak |
|---|---:|---:|---:|---:|---:|---:|:--|
| Kyber-512 | 389 | 423 | 35.802619 | 37.915470 | 353.197381 | **385.084530** | SVP |
| Kyber-768 | 606 | 641 | 48.847070 | 50.867988 | 557.152930 | **590.132012** | SVP |
| Kyber-1024 | 855 | 890 | 62.855627 | 64.764670 | 792.144373 | **825.235330** | SVP |

η+1 > β on all three (423>389, 641>606, 890>855) and the reduced SVP dimension
exceeds the reduced BKZ dimension on all three. **Claim C4 reproduced.** The
producer's 385.08 / 590.13 / 825.24 are correct, so c\* is computed against the
right dimension.

Had the BKZ sieve been taken as peak instead, c\* would be 0.03425604 /
0.04843445 / 0.00733552 — **+8.25% / +5.55% / +3.98%**. The report's "a few
percent" is right. Not a sign change anywhere.

### Two things I checked that the package does not

**(a) Applying d4f to *memory* is the conservative branch.** d4f is a runtime
trick; using it for the memory dimension too is a modelling choice. It lowers
log2 M and therefore *raises* c\*, i.e. it works **against** the producer's own
headline:

| convention | log2 M_peak (Z_q) | c\* |
|---|---|---|
| with d4f (producer) | 88.4941 / 131.6573 / 180.9250 | 0.03164649 / 0.04588645 / 0.00705473 |
| without d4f (raw η+1) | 96.4970 / 142.3317 / 194.4727 | 0.02902190 / 0.04244512 / 0.00656327 |

**(b) A floor/no-floor wrinkle, immaterial.** `reduction.py:800` uses unfloored
`β − d4f(β)` for the runtime model, which is what the producer used for memory;
the estimator's own vector-count sites (`:846`, `:854`, `:903`, `:936`) use
floored `β − floor(d4f(β))`. Under the floored convention c\* = 0.03157749 /
0.04582302 / 0.00704849 — within 0.2%.

## 4. Memory unit — recomputed in every convention

Chain confirmed: `M_vec = 2^(0.2075n)`, `M_zq = n·M_vec`,
`M_bits = 12·n·M_vec` with q = 3329, log2 q = 11.700873, ceil = 12.

The instrument citation checks out. `estimator/lwe_dual.py` contains
`cost["mem"] += sieve_dim * N` under the comment *"Add the memory cost of
storing the `N` dual vectors, using `sieve_dim` many coefficients (mod q) to
represent them … so this is really an upper bound here"*, and the docstring
entry *"``mem``: memory requirement in integers mod q"*. Both are verbatim.

| set | log2 M vectors | log2 M Z_q | log2 M bits | c\* vec | c\* Z_q | c\* bits |
|---|---:|---:|---:|---:|---:|---:|
| Kyber-512 | 79.905040 | **88.494071** | 92.079034 | 0.03504819 | **0.03164649** | 0.03041438 |
| Kyber-768 | 122.452392 | **131.657286** | 135.242249 | 0.04933579 | **0.04588645** | 0.04467010 |
| Kyber-1024 | 171.236331 | **180.924993** | 184.509955 | 0.00745389 | **0.00705473** | 0.00691766 |

BKZ-sieve memory in Z_q, for reference: 81.752787 / 124.731163 / 173.999577 —
matches the producer.

**Unit sensitivity, refined.** The spread is **15.24% / 10.44% / 7.75%**
relative to the smaller value (13.22% / 9.46% / 7.19% relative to the larger).
So "~15%" is the **maximum over the three sets**, not a uniform figure — correct
as an upper bound, overstated as a general claim (defect D7). Direction is
conservative: it overstates the sensitivity.

The substantive point — no order-of-magnitude unit slip — is confirmed, and it
is **structural rather than lucky**: the three units differ only by the additive
terms log2(n) ≈ 8.6–9.7 bits and log2(12) = 3.585 bits, against a base 0.2075·n
of 73–171 bits. The ratio max/min log2 M is 1.152356 / 1.104448 / 1.077516, and
since c\* ≡ margin / log2 M, c\* moves by exactly that ratio and no more. An
order-of-magnitude unit error is arithmetically impossible in this chain.

I also tried to validate the chain numerically against the estimator's own
`mem` output. `dual_hybrid(Kyber512, RC.MATZOV)` returns `mem` = 2^140.5106 at
β = 408, while n·2^(0.2075n) at n = 408 is 2^93.3324. These *should not* agree —
the dual attack requests N ≫ 2^(0.2075·sieve_dim) vectors for distinguishing, so
its `mem` is `sieve_dim · N` with N set by the distinguisher, not by the sieve
database. What the comparison does establish is the **unit**: `mem` is
(dimension) × (number of vectors) in Z_q elements, exactly the producer's chain.
I record it so the check is not silently dropped; no inconsistency is asserted.

## 5. c\*, both models, and the c = 1/3 margins

Model A closed form c\* = margin / log2 M_peak reproduces to 8 dp. Model B I
re-derived with my own 300-iteration bisection of
`cost(c) = red·M_bkz^c + svp·M_svp^c`:

| set | c\* Model A | c\* Model B (my bisection) | Δ vs producer | cost(c\*_B) |
|---|---:|---:|---:|---:|
| Kyber-512 | 0.03164649 | 0.03277120 | 4.70e-09 | 143.0000000000 |
| Kyber-768 | 0.04588645 | 0.04701194 | 3.92e-09 | 207.0000000000 |
| Kyber-1024 | 0.00705473 | 0.00720010 | 1.86e-10 | 272.0000000000 |

Structural check passes: c\*_B > c\*_A on all three, as it must, since
M_bkz < M_peak makes Model B the cheaper charge at any c.

Margins at c = 1/3, cross-checked two independent ways
(`cutoff − (log2 rop + log2M/3)` and `m0 − log2M/3`):

| set | Model A | Model B |
|---|---:|---:|
| Kyber-512 | **−26.6975** | −26.0295 |
| Kyber-768 | **−37.8445** | −37.1417 |
| Kyber-1024 | **−59.0320** | −58.2350 |

**Claims C2, C3, C6 reproduced.**

Then I diffed *everything* stored under the Z_q unit in `results.json` — five
named charges × two charge models × three sets, plus c\* and the four
access-fraction rows per set — against my own recomputation:

```
MAX |validator - producer| over every stored Z_q charged-cost,
margin, c* and f-sensitivity entry:   0.000e+00
```

H9 sensitivity independently reproduced: f = 2^−10 → 0.144648 / 0.121841 /
0.062326; 2^−20 → 0.257650 / 0.197796 / 0.117598; 2^−30 → 0.370652 / 0.273751 /
0.172869.

Derived ratios also check: (1/3)/c\* = 10.53 / 7.26 / 47.25; (1/2)/c\* = 15.80 /
10.90 / 70.87; 2^m0 = 6.967× / 65.858× / 2.422×; per-access charge log2M/3 =
29.50 / 43.89 / 60.31 and log2M/2 = 44.25 / 65.83 / 90.46.

## 6. The 0.2075 constant

```
log2(sqrt(4/3))        = 0.20751874963942182
|0.2075 - closed form| = 1.874964e-05
```

Producer's reported 1.875e-05 is correct to the digits given. The literal
`0.2075` appears at `reduction.py:415`, `:854`, `:936` as claimed.
**Claim C7 reproduced.** BDGL16 primary text: not retrieved by the producer, not
retrieved by me — recorded as unable_to_check.

## 7. Controls: eight reported, four that can actually fail

All eight reproduce. But four are algebraic identities of the definitions:

| control | can it fail? | why |
|---|---|---|
| CTRL-0 known-answer | **yes** | genuine external reference |
| CTRL-1 decomposition | **yes** | genuine re-derivation from the reduction model |
| CTRL-2 baseline | **yes** | genuine comparison to an archived value |
| CTRL-3 0.2075 closed form | **yes** | genuine numeric identity check |
| CTRL-4 unit scaling | no | c\* ≡ m0/log2M in every unit, so the ratio is forced |
| CTRL-5 null object | no | charge term is c·log2M, and c·0 = 0 identically |
| CTRL-6 closed form vs bisection | barely | bisects the *same* closed form; tests the routine |
| CTRL-7 monotonicity | no | margin(c) is affine with slope −log2M < 0 |

That is defect D1. The four substantive controls are strong; presenting all
eight as equal standing inflates the count.

**On CTRL-5 and the inventor protocol (defect D3).** The report calls CTRL-5
"the inventor-protocol control-before-belief check". It is not a null object of
the same shape — it sets the signal to zero by hand. A real null of the same
shape would be the identical pipeline on a parameter set with no undercut (c\*
must fail to exist), or on an attack whose memory is polynomial rather than
exponential in the sieve dimension (c\* must blow up). Neither was run.

Being fair about what §3 is aimed at: this derivation is deterministic
arithmetic with no sampling, no seed, and no estimator of a random quantity, so
the statistical-artifact failure mode is not the binding risk. And the package
*does* supply the decay statement §3 asks for — the H9 table shows c\* rising
monotonically as the access fraction f (the parameter that would destroy the
result) shrinks, and every heuristic carries a `direction_if_wrong`. The defect
is the claim made *for* CTRL-5, not an absence of directional reasoning.

**Defect D2** is adjacent and worse: H8 (the NIST cutoff is not itself
re-charged) lists `validated_by: [CTRL-5_null_object_zero_memory]`. CTRL-5 zeroes
the *attack's* memory; H8 is about the *reference computation's* memory. CTRL-5
says nothing about it. H8's own status is `unvalidated`, so the file contradicts
itself.

## 8. The check H12 records as `falsified_by: n/a`

H12's `direction_if_wrong` claims that a cheaper attack would raise c\*. That is
falsifiable and the falsifier was cheap, so I ran it (Kyber-512, RC.MATZOV):

```
primal_usvp     log2 rop = 143.771733
primal_bdd      log2 rop = 140.199473
dual            UNAVAILABLE: AttributeError: '_RealField' object has no attribute 'pi'
dual_hybrid     log2 rop = 145.528285   mem log2 = 140.5106
primal_hybrid   UNAVAILABLE: ZeroDivisionError

CHEAPEST SERVED: primal_bdd at log2 rop 140.199473
```

Two results:

1. **primal_bdd is the cheapest attack this harness serves and runs.** The
   baseline stands. The check resolves in the producer's favour — it just was
   not in the package (defect D5).
2. **The harness cannot serve `dual` or `primal_hybrid` either** (defect D4).
   The `dual` failure traces to `estimator/prob.py:213`,
   `amplify_sigma` → `RDF.pi()`, which the shim's `_RealField` does not
   implement. `primal_hybrid` raises `ZeroDivisionError`. Both fail loudly
   rather than returning a wrong cost, which is the shim's stated design and is
   the safe behaviour — but H12, report §7 item 4, `results.json.status_note`
   and `tools/sage_free_estimator/README.md`'s "Scope and limits" all name
   Arora–Gröbner as *the* limitation. The served set is narrower than advertised,
   and it is narrower in the direction that understates how large the undercut
   might be. Root cause is in `tools/sage_free_estimator/shim` — committed at
   `defd0373`, outside this package and outside my write scope. I did not touch
   it.

**Answer to the question asked about H12's `n/a`:** split the heuristic. The
pure scope declaration ("every number here concerns primal_bdd under
RC.MATZOV") genuinely is not a claim about the world, needs no falsifier, and is
verifiable by inspection — I verified it; the script calls nothing else. For
that half, `n/a` is correct and should not be repaired into a fake falsifier.
But H12 also asserts a *fact about the instrument*, which I partially falsified,
and its `direction_if_wrong` states a claim whose falsifier was available and
unrun. So: **acceptable as a scope statement, a gap as written.** Not a
fabrication, not grounds for INADMISSIBLE — a five-minute check would have
closed it.

## 9. Overclaim check

I looked for both failure directions and found neither.

- **No break.** The derivation moves estimated cost *up*. `certificate.kind` is
  `none` with the right reason. Nothing computes or approaches a solve.
- **No security proof.** The harder direction, handled explicitly and in the
  right words: *"a memory charge that RAISES the estimated attack cost above a
  NIST cutoff is not a proof of security — it is a statement about one cost
  model, at one parameter set, under the heuristics in heuristics.yaml."* That
  sentence is in the report, the script docstring and `results.json`.
- **No status change**, no promotion request, no heuristic declared validated.
- **No best-attack claim** — correct in substance, though the stated reason is
  incomplete (D4).

The one sentence I would tighten is §7's "the undercut … does not survive any of
the memory charges examined here" (defect D8). It is true for the examined
c-values, but true *because* H9 charges every MATZOV gate as one memory access;
the package's own table shows Kyber-512's c\* reaching 0.370652 > 1/3 at
f = 2^−30, where the undercut would survive a 3D charge. H9 is disclosed
prominently in §5, so this is precision, not misrepresentation — but §7 is the
paragraph a downstream record will quote.

**Residual risk worth naming.** c\* being one to two orders of magnitude below
1/3 is a striking number that will read as "ML-KEM's NIST margin is comfortable
once memory is priced". It supports no such thing. It says that *at the
free-memory optimum* — not the operating point a memory-charged attacker would
choose (H10) — a surcharge of 7× / 66× / 2.4× per charged operation closes the
gap, *under* the assumption that every MATZOV gate is a memory access (H9),
against a cutoff held fixed on an argument not verified against NIST text (H8,
H11), for the one attack this harness serves and runs (H12, D4). Drop those four
qualifiers and the result is overstated.

## 10. What I could not check

- The NIST cutoffs 143 / 207 / 272 (H11) — no NIST or FIPS 203 text is readable
  under this program's network policy, exactly as EV-MLKEM-015 recorded. A
  one-bit cutoff error moves c\* by 0.0113 / 0.0076 / 0.0055 — which is 78% of
  Kyber-1024's entire c\*. The producer says so too; it is the honest reason not
  to read 0.00705 as three significant figures.
- BDGL16 as primary source for 0.2075 (H4). What *is* verified: the instrument's
  literal and the closed form.
- Whether a memory-aware attacker's true optimum is materially cheaper (H10) —
  RC.MATZOV supplies no lower-memory sieve model, so it is not computable here.
- Whether any attack *outside* this harness beats primal_bdd. I checked only
  what the harness serves and runs.
- Model B under the vectors and bits units — I re-bisected Model B only in the
  headline Z_q unit. Low risk: Model A's unit scaling is an exact identity and
  brackets it.
- The estimator itself. My independence is at the artifact level; I used the
  same instrument at the same pin as the producer, which is exactly what the
  known-answer control makes admissible. A defect in lattice-estimator 3e48ef4,
  or in the shim on a path the control does not cover, is invisible to both of
  us. **D4 is one instance of that class surfacing.**

## 11. Verdict

**ADMISSIBLE_WITH_DEFECTS.**

Every quantitative claim in the task card reproduced independently, at exact
equality or print-rounding residuals. The load-bearing sieve-dimension claim is
confirmed against the pinned source, line by line, including the inheritance
step the producer asserted without showing. The memory unit chain is consistent,
correctly sourced, and its bounded sensitivity is structural rather than
coincidental. The package does not overclaim in either direction.

The eight defects are documentation, control-framing and scope-completeness
defects. **None of them changes a number.** D2 (H8's misattributed control) and
D4 (the incomplete served-attack scope statement) are the two worth correcting
in a successor record, because both could mislead a later reader about how much
has actually been checked.

A passed validation means this receipt is admissible evidence. It does not
support any ML-KEM claim, does not demonstrate a speedup, does not validate any
heuristic, and does not authorize promotion. AGENTS.md rule 12 remains UNMET and
UNWAIVED, and this review — `review-adversarial`, not `review-breakthrough` at
`max` — cannot clear anything that rule 12 governs.

---

Requested policy `review-adversarial`, `xhigh`, independent session. Resolved
model `claude-opus-5`, `fallback_used: true` (the policy alias routes to a
GPT-5.6-family model this harness cannot resolve; `.claude/agents/` runs
`model: inherit`). Not probe-verified. I did not commit, stage, push, or edit
anything outside
`coordination/goals/GOAL-MLKEM-003/batches/BATCH-010/tasks/TASK-20260803-90327f/`.
