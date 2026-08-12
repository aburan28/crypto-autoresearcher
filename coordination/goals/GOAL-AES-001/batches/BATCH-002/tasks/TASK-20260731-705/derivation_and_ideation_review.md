# Check (a) — derivation note and super-box ideation package (TASK-20260731-701)

**Independent validation, TASK-20260731-705. Verdict for check (a) only.**
This file carries ONE verdict. It says nothing about the harness repair
(check (b), `harness_repair_review.md`) or the gate run (check (c),
`gate_601b_review.md`), and those files say nothing about this one.

| field | value |
|---|---|
| Reviewed revision | `ebac9ba8a52b05bbd434edac715271e404d8e104` (snapshot, TASK-20260731-704) |
| Artifacts | `derivation_note_column_local_obstructions.md`, `verify_derivation.py`, `candidate_report.yaml` |
| Producer | TASK-20260731-701 (idea-generator) |
| **Verdict (a)** | **passed, with defects** |
| Promotion fitness (note only) | **FIT** as a `derivation`-tier knowledge item |
| Official state changed | none. No evidence strength assigned. |

---

## 0. Snapshot integrity (precondition)

Executed, not asserted:

- `git merge-base --is-ancestor ebac9ba8 HEAD` → reachable from HEAD.
- `git rev-parse ebac9ba8^` → `98ae8539c9cbb8c3a261ceab83536069c9947253`.
- `git diff --name-status 98ae8539 ebac9ba8` → exactly the 10 declared paths,
  all `A` (added), nothing else.
- SHA-256 of every committed blob recomputed with `git show ebac9ba8:<path>`
  and compared to `source_path_sha256`: **9/9 match**, including
  `gate_601b_impl.c = dc2bc3fe…` and `mutation_control_v2.py = d2b2a5dd…`
  which independently agree with the digests recorded inside
  `gate_601b_results.json` and `repair_receipt.json`.

Precondition satisfied. One defect noted: `commit_sha` and `parent_sha` in the
receipt are still `null` (D-705-6, low) — the receipt itself specifies they be
filled in a follow-on write after the commit, and that write did not happen.
The binding is nevertheless complete because the digests bind.

---

## 1. Self-containment — read as if BATCH-001 did not exist

**The argument closes without any BATCH-001 record.** I read §§0–7 treating
`EV-AES-001`, `TASK-20260731-604` and `aes_reduced.py` as unavailable and found
no step that depends on them:

- §1 states the field, the reduction polynomial `0x11B`, the matrix `M`, the
  `Inv(0)=0` convention, the bit-definition of `A`, the constant `0x63`, the
  difference convention and the definition of collinearity. Nothing is imported.
- §2.1 derives `ord(M) = 4` from the circulant → `F[y]/(y^4+1) = F[z]/(z^4)`
  isomorphism and the characteristic-2 Frobenius. Complete on the page.
- §2.4 derives the kernel dimensions from the ring structure and applies
  Burnside. Complete on the page, with an independent stratification
  cross-check also on the page.
- §3.1 is a two-case coordinate-wise argument. §3.2 is a hand-checkable
  counterexample with all three needed `L` values displayed.
- The only citations, §7, are explicitly labelled *provenance* and are used for
  history, not inference. §2.4's mention of `EV-AES-001` B-3 is a comparison of
  two numbers both derived in the note; deleting the mention loses nothing.
- Appendix A is explicitly declared non-load-bearing for either proposition.
  I confirm that: neither §2 nor §3 uses A.1/A.2/A.3.

The single external dependency is claim `C0` of the script, which the note
already declares optional (`SKIP` if unavailable). The *note* does not depend
on it; the note's §0.4/limitation 4 correctly describes it as the operational
pinning of the AES constants and correctly calls it weaker than a read
specification.

**Self-containment: YES.**

---

## 2. Re-execution of `verify_derivation.py` from committed source

Extracted with `git show ebac9ba8:…/verify_derivation.py` (digest
`9618f55f…`, matching the manifest) and run twice:

1. In a bare scratch directory: `SUMMARY 16 PASS, 0 FAIL, 1 SKIP of 17`,
   exit 0. `C0` skipped with *harness not found*.
2. With the committed BATCH-001 harness (`git show
   ebac9ba8:…/TASK-20260731-602/aes_reduced.py`) placed at the exact relative
   path the script computes: `SUMMARY 16 PASS, 0 FAIL, 1 SKIP`, exit 0.
   `C0` skipped with `AttributeError: 'NoneType' object has no attribute
   '__dict__'`.

Per-claim reproduction (my run, committed source):

| claim | reproduced | value observed |
|---|---|---|
| `C-TAB` | PASS | 65536/65536 table vs. reference multiplications; 255/255 inverses; `ginv(0)=0` |
| `C0` | **SKIP** | import failure, see §2.1 |
| `C1` | PASS | `ord(M)=4`; `M^2 = [[5,0,4,0],[0,5,0,4],[4,0,5,0],[0,4,0,5]]` |
| `C2` | PASS | `|GL(4,GF(2^8))| = 338947946628913982763966439819837440000`; ratio `1.180e-38` |
| `C3` | PASS | orbit `{(1,0,0,0),(2,1,1,3),(5,0,4,0),(e,9,d,b)}`, size 4 |
| `C4` | PASS | `q^4-1 = 4294967295`; bound `>= 1073741824` |
| `C5` | PASS | kernel dims `4,1,2,1`; Burnside `1073758335`; stratified `255+32640+1073725440` |
| `C6a` | PASS | 65280/65280 exhaustive, 255 of them at `x=0`, 0 failures |
| `C6b` | PASS | 4000/4000, seed 202608010001 |
| `C6c` | PASS | 4000/4000 with a zero coordinate, seed 202608010002 |
| `C7a` | PASS | 0/4000 survive `L`, seed 202608010003 |
| `C7b` | PASS | 0/4000 survive `S = L∘Inv`, seed 202608010004 |
| `C7c` | PASS | `L(v)=(7c,63,63,63)`, `L(w)=(5d,63,63,63)`, not collinear |
| `C8` | PASS | 64262 preserved / 508 degenerate / **0 broken** of 64770 |
| `C9` | PASS | 16 nonzero entries, values `{01,02,03}` |
| `C10` | PASS | subgroup order 255; `ord(02)=51`, `ord(03)=255` |
| `C11` | PASS | 1020 forward- and 1020 reverse-reachable → strongly connected |

**16 of 17 claims reproduce exactly. 0 FAIL. 1 SKIP.** My totals agree with the
coordinator-side corroboration recorded in the snapshot receipt (CORROB-704-1);
that corroboration is *not* what discharges the gate — this re-execution and
§3 are.

### 2.1 The `C0` SKIP is a defect in `verify_derivation.py`, not in the harness

Diagnosed by executing the import in isolation. Full traceback root cause:

```
File "/usr/lib/python3.11/dataclasses.py", line 712, in _is_type
    ns = sys.modules.get(cls.__module__).__dict__
AttributeError: 'NoneType' object has no attribute '__dict__'
```

`aes_reduced.py` uses `@dataclass(frozen=True)` at import time.
`dataclasses._is_type` looks the defining module up in `sys.modules`.
`verify_derivation.py:309-313` loads via `spec_from_file_location` /
`module_from_spec` / `exec_module` **without** inserting the module into
`sys.modules` first, so the lookup returns `None`. One line
(`sys.modules[spec.name] = mod` before `exec_module`) fixes it — I verified
that by doing exactly that in my own code (§3, V7). Note that
`mutation_control_v2.py`'s runner *does* register the module, i.e. BATCH-002
already contains the correct pattern elsewhere.

Recorded as **D-705-2 (low)**. Not repaired: repair is not this task's role.

---

## 3. Independent recomputation — my own method, not their script

Written from scratch (`indep_check.py`, validator-authored; no code, tables or
constants copied from `verify_derivation.py`; shift-and-add `gmul`, brute-force
inverse by search rather than log/antilog tables, and a different random seed).

| fact | note's value | my value | method |
|---|---|---|---|
| `ord(M)` in `GL(4,GF(2^8))` | 4 | **4** | brute-force power iteration on the matrix |
| `ord(M)` — second, independent method | 4 | **4** | order of `c(y)=(02,03,01,01)` in `F[y]/(y^4+1)` by polynomial multiplication with explicit `y^4 = 1` reduction |
| orbit of `e1` under `<M>` | 4 elements | **4**: `(01,00,00,00), (02,01,01,03), (05,00,04,00), (0e,09,0d,0b)` | direct iteration |
| `dim ker(M^e - I)`, `e=0..3` | 4,1,2,1 | **4,1,2,1** | my own Gaussian elimination over `GF(2^8)` (rank of `M^e - I`), *not* the ring-theoretic route the note derives it by |
| nonzero fixed vectors | 4294967295, 255, 65535, 255 | **identical** | `256^k - 1` from the ranks |
| lower bound `ceil((q^4-1)/4)` | 1073741824 | **1073741824** | direct |
| exact Burnside orbit count | 1073758335 | **1073758335** | Burnside from my own ranks |
| stratified cross-check | 255 + 32640 + 1073725440 | **identical** | computed from my fixed-point counts, not copied |
| `|GL(4,GF(2^8))|` | 338947946628913982763966439819837440000 | **identical**; four factors `4294967295, 4294967040, 4294901760, 4278190080` also identical | product formula |
| ratio `4/|GL|` | 1.18e-38 | **1.180e-38** | direct |
| `Inv(λv)=λ⁻¹Inv(v)` scalar form | holds | **0 failures / 65280 pairs, 0 of them at x=0** | exhaustive, inverse by search |
| same, vector level **including zero coordinates** | holds | **0 failures / 20000 seeded draws with zeros deliberately over-sampled** | seed 70505, my seed |
| `L` counterexample | `L(v)=(7c,63,63,63)`, `L(w)=(5d,63,63,63)`, not collinear | **identical**, collinearity search over all 255 scalars returns none | `L` rebuilt from the bit definition in §1 |
| collinearity failure under `L`, non-constant pairs | 0 survive | **0 / 4000 survive** (my seed 70506) | independent sampler |
| constant-vector family (Corollary 2.2) | 0 broken, 508 degenerate | **ok 64262, degenerate 508, broken 0** | exhaustive over `(a, λ)` |
| every entry of `M` nonzero; values `{01,02,03}` | yes | **yes** | direct |
| entries of `M` generate `GF(2^8)*` | order 255; `ord(02)=51`, `ord(03)=255` | **identical** | closure of the generated set |

**Every fact in both propositions recomputes independently. No discrepancy.**

### 3.1 `C0`'s intent, covered independently

I loaded the committed BATCH-001 harness with `sys.modules` registration and
compared it to *my own* constants (not the script's):

- `aes_reduced.AES_MIX` equals the note's `M`: **True**
- the harness S-box equals my `L(Inv(x))` for all 256 `x`: **True**
- the harness `GF.inv` equals my brute-force inverse for all 256 `x`: **True**
- multiplicative order of the *harness's* MixColumns matrix: **4**

As a further external anchor, my independently constructed S-box gives
`S(0x00)=0x63`, `S(0x01)=0x7c`, `S(0x53)=0xed`. Those are the standard AES
values as I recall them — flagged `unverified_from_memory`, because
`csrc.nist.gov` is unreachable under this network policy and I read no
specification. Two agreeing recollections would not be a citation either.

**C0's intent is discharged; the mechanised claim `C0` remains SKIP.**

---

## 4. Ruling on defect D-701-1 (the transcription gate)

The facts, kept separate:

1. The producer did **not** run the script and did **not** transcribe output.
   §6.2 of the note says so in terms and refuses to fabricate a transcript
   under AGENTS.md rule 9. That refusal is correct behaviour, not a defect.
2. The TASK-20260731-701 completion gate asked the **producer** to transcribe
   the invocation and output. On its literal text that gate item was **not
   met**, and TASK-20260731-704 was right not to waive it.
3. The dispatching session's run (16/0/1) is Coordinator-side corroboration of
   an artifact it was archiving. It is not independent validation and I do not
   rely on it.
4. This task re-executed the script from committed source (§2) and, more
   strongly, recomputed every numerical claim by an independent method (§3).

**Ruling: D-701-1 is DISCHARGED, by substitution and at a higher standard than
the gate asked for.** The gate's purpose was machine confirmation of the
derived numbers; that purpose is now served by an independent session that did
not author the note, which is strictly stronger than a producer transcript.
The gate's *letter* remains unmet and that should be recorded as such rather
than back-dated: the note's §6.2 line "machine recomputation pending" was
accurate when written and is now superseded by this report, not by an edit to
the note (records are immutable — the note must not be amended).

Residual: `C0` alone stays SKIP (D-705-2), covered by §3.1.

---

## 5. The two additions beyond BATCH-001

**Addition 1 — Corollary 2.2, the constant-vector family on which `L` DOES
preserve collinearity.** Correct, and I verified it exhaustively and
independently: over all `255 × 254 = 64770` pairs `(a, λ)` with `a ≠ 0`,
`λ ∉ {0,1}`, **0 broken**, 508 degenerate, 64262 preserved. The mathematics is
also transparent: `L` applied coordinate-wise to `(a,a,a,a)` yields
`(L(a),L(a),L(a),L(a))`, and any two nonzero constant vectors are collinear by
the scalar `L(b)/L(a)`. The degenerate count is exactly right: `L(a)=0` for
exactly one `a` (`A a = 0x63` has a unique solution since `A` is invertible),
and that `a` appears once as the source and 253 times as the image over the
`λ`-sweep, plus the symmetric bookkeeping — `508 = 2 × 254`. **This addition
is materially load-bearing**: without it Corollary 2.1 as stated ("does not
preserve collinearity") would be false as a universal, and the sampling choice
in `C7a`/`C7b` (non-constant vectors only) would be an unexplained exclusion.
The note states the reason for the exclusion at the point of the exclusion.
Correct, and an improvement on BATCH-001.

**Addition 2 — the scope limit that neither proposition says anything about
difference propagation through SubBytes (§3.5).** Correct, and correctly
placed. `S(x+d) + S(x)` is not a function of `d`, so a statement about
`Inv(λv)` — a statement about *values* — transfers to differences only under an
assumption the note does not make. §3.5 also states the dual limitation on
values (collinearity is destroyed by AddRoundKey), which is the right symmetric
caveat. **Does it properly bound the note's scope? Yes.** I attempted to find
a sentence elsewhere in the note that over-reads across this boundary and found
none: §2.6 confines its propagation claim to ARK and MC, §4 item 5 restates the
non-licence explicitly, and §5's ShiftRows remark forecloses the other obvious
over-reading (that Proposition 1 is a green light for column-local objects).

---

## 6. `proof_status` and scope honesty

`proof_status: derivation` is **honest**. Both propositions are complete
human-checkable arguments with machine-recomputed numerical conclusions and no
machine-checked formal proof; `proven` would overstate, `empirical_only` would
misdescribe (nothing here measures a cipher). The note's own gloss of the label
matches what I found.

The scope statements are honest. Specifically I confirm:

- "**no cryptanalytic claim about AES of any kind, at any round count**"
  (§0.2) — I found no distinguisher, key recovery, complexity claim or measured
  excess anywhere in the note.
- "**not a barrier statement about AES security**" (§0.2, §4 item 6,
  limitation 5) — correct, and the note is careful in the *other* direction
  too: §0.2 item 3 states that Proposition 1 restores column-local objects to
  status *open*, "which is strictly weaker than either 'closed' or
  'promising'". That is the right formulation and it is repeated in §2.7 and
  §4 item 4.
- No novelty claim (§0.4, limitation 3), with the network policy named. Correct
  and appropriately blunt. My own reaction — that both propositions look like
  standard folklore — is itself `unverified_from_memory` and settles nothing.

One over-strong sentence, minor: §2.4's "Nonconstant invariants therefore exist
in abundance — there are `1073758335` independent binary choices available".
The count is the number of orbits, and the note itself says so two lines later
and again in §2.7; the phrase "independent binary choices" is loose (it counts
`2^1073758335` invariants, not `1073758335` choices, and "independent" is doing
no work). Cosmetic; recorded as **D-705-3 (informational)**, not a correctness
defect.

**Promotion fitness verdict on the note as a standalone artifact: FIT** for
promotion at the `derivation` tier. It is self-contained (§1), every numerical
claim reproduces (§2) and independently recomputes (§3), its two additions are
correct (§5), and its scope statements are honest (§6). A promotion decision
belongs to TASK-20260731-706, not to me; I record fitness only.

---

## 7. Ideation package — `candidate_report.yaml`

### 7.1 Object-first discipline

All 8 objects (OBJ-701-1 … -8) name a concrete tracked object, a named byte set
and a named round count. Verified line by line. The byte set is a ShiftRows
diagonal (`{0,5,10,15}`-style) in every case where a byte set applies, i.e. the
objects are **super-box-level with ShiftRows inside the two-round super-box and
outside the tracked word**, not relabelled column-local objects. OBJ-701-8
explicitly moves to two diagonals. This is the correct response to the BATCH-001
column-local problem, and the companion note's §5 states the reason.

Zero candidates were admitted, so the per-candidate cost boundary, survival
depth and dedup obligations fall on objects rather than candidates; each object
carries them. `dominated_by: n/a` with a written justification (nothing is
claimed, so nothing can be dominated) and `sota_delta: 0 bits on every axis at
every round count 3–7`. Under `docs/inventor-protocol.md` a bare `null` would be
a fabrication; `n/a` with the reasoning spelled out is the correct value here.
**Accepted.**

### 7.2 Deduplication, per object

Each object is scored against all nine named families plus the corpus. My own
independent identification attempt agrees with the producer's on every object,
and — this matters — the producer **volunteers** the rediscoveries rather than
leaving them for me to find:

| object | producer's identification | my judgement |
|---|---|---|
| OBJ-701-1 projective class of a word | not an instance; adjacent to KN-LIT-7593 | agree; adjacency, not rediscovery |
| OBJ-701-2 subspace coset | subspace-trail-style | agree |
| OBJ-701-3 (probabilistic reading) | **truncated differential — rediscovery, recorded** | agree |
| OBJ-701-4 | **Demirci–Şelçuk multiset fingerprint — rediscovery, recorded** | agree |
| OBJ-701-5 | **Super-Sbox / rebound — rediscovery, recorded** | agree |
| OBJ-701-6 cycle structure | representation artifact, KN-LIT-7595 transported | agree; the report itself labels this closure weaker (corpus-relayed, not re-derived) |
| OBJ-701-7, -8 | OPEN, not examined | agree; correctly not proposed |

**Candidates judged to be a rediscovery presented as novel: NONE.** There is
nothing to name, because zero candidates were proposed and every rediscovery is
declared by the producer first. `PROP-701-I` itself is pre-labelled a probable
re-derivation of known subspace-trail limits at recall confidence LOW-MEDIUM,
`unverified_from_memory`. I cannot confirm or refute that recall — no primary
source is reachable — and my own recollection of a two-round subspace-trail
ceiling for AES is likewise **unverified-from-memory and settles nothing**.

### 7.3 `PROP-701-I` — is the proof complete?

I worked through all three steps. **The proof is complete and, as far as I can
check it, correct.** Step by step:

- **Step 1.** With ShiftRows offsets `(0,1,2,3)`, input word 1 contributes
  exactly one coordinate `i_j = (1-j) mod 4` to output word `j`. Correct.
  Because the other three input words are untouched and `π(a)=π(b)`, all four
  arguments of `F_j` coincide, so the two outputs must share a `π` value; they
  differ by `Δ_{i_j} m_{i_j}` after MixColumns. Every row index `i` is reached
  by choosing `j = (1-i) mod 4`. Correct.
- **Step 2.** `v = Δ_i m_i` has all four coordinates nonzero **because every
  entry of `M` is nonzero** — I verified that fact independently (§3). The
  re-application of Step 1 to the pair `(u, u+v)` is where **round-independence
  is consumed**: `u` and `u+v` are output words of one interface being fed as
  input words to the next, and the argument needs the *same* `π` there. The
  hyperplane constraint dissolves because `u_k = Σ_l M[k][l] y_l + (k_j)_k` with
  `M[k][l] ≠ 0` and `y_l` free for `l ≠ i`, so `u_k` sweeps all of `F`. Correct.
- **Step 3.** The reachable translations are the nodes reachable in the
  `(λ,k)` graph, which I verified strongly connected in my own recomputation
  (claim C11's content, `ord(0x03)=255`). Invariance translations form a group
  under addition, hence contain the `GF(2)`-span of `{λ m_k}`, which is the
  `F`-span of `{m_0,…,m_3}` = `F^4` since `M` is invertible. So `π` is constant.
  Correct.

I additionally ran the producer's own falsification gate for this proof — see
§7.4 — and the AES-shaped case confirms the engine exhaustively in the
scaled-down analogue.

**What the closure does NOT cover.** The report names four holes (OD-1
layer-dependent, OD-2 multi-word, OD-3 set-valued, OD-4 probabilistic /
bounded-branching) and ranks OD-1 first with a concrete next computation. All
four are real and correctly identified. Probing the two qualifiers the task
card singles out:

- **"round-independent"** is consumed exactly once, in Step 2's re-application,
  and that is precisely OD-1. The report's characterisation is right, though its
  phrasing ("iterates Steps 1-2 an unbounded number of times") is slightly
  misleading: the hypothesis is a single universally-quantified statement about
  `π` and `Φ`, and re-applying it costs no additional assumption — what it costs
  is that the *same* `π` must sit at the next layer. **D-705-4 (informational).**
- **"deterministic"** is consumed in the existence of the functions `F_j`. OD-4
  correctly notes that `B > 1` branching is untouched, and asks the right
  follow-up (does the group-growth argument lower-bound `B` for a given entropy
  loss?) — that is the form that would turn a qualitative closure into a cost
  inequality.
- **A hole the report does NOT name.** `π` is assumed to be *the same map at
  every word position* within a layer. A **word-position-dependent family**
  `π_0, π_1, π_2, π_3` is neither OD-1 (which is layer-dependence) nor OD-2
  (which is multi-word domain). Step 1 would then yield an invariance for
  `π_j` at output index `j` while the re-application in Step 2 needs a pair with
  equal `π_1` at an input index, and the indices do not line up. The proof does
  not transfer verbatim, and no replacement is offered because the case is not
  considered. Recorded as **D-705-5 (low)**: an unnamed gap in an otherwise
  carefully enumerated scope list. It narrows the closure; it does not
  invalidate any step.
- The hypothesis quantifies over **every state `s`**. An object required to
  propagate deterministically only on a structured subset of states (a coset, a
  δ-set) is outside the hypothesis. This is arguably adjacent to OD-3 but is not
  the same thing, and is not named. Folded into D-705-5.

**Is `NO_ADMISSIBLE_NEXT_MECHANISM` a closure or a fatigue report?** A
**closure**, at the `docs/inventor-protocol.md` §4 standard. A fatigue report's
content is a count of screened objects; this record's content is a proposition
with a proof, a named obstruction ("the interface `Φ = ARK·MC·SR` is not a byte
permutation; every MixColumns entry is nonzero and the entries generate
`GF(2^8)*`, so one collision grows into full translation invariance"), and
forward guidance naming the four classes a future object must inhabit. CLO-701-1
and CLO-701-2 meet the standard. CLO-701-3 does **not** re-derive anything and
the report says so itself, labelling it `prior-art closure, corpus-relayed, not
re-verified` — correctly weaker, correctly labelled. The record also explicitly
declines to claim "the super-box lane is mined", which is the premature-closure
failure the protocol forbids. **Not a fatigue report.**

### 7.4 GATE-701-C — I ran it, and it does not read as specified

The gate was `SPECIFIED, NOT RUN` (the producer had no execution tool, and
correctly reported no output). I implemented it myself from the written
specification (validator-authored `gate701c.py`: `GF(2^4)` with `x^4+x+1`,
4×4 circulant, the closure rule `u ↦ {u_j·m_j}` plus `GF(2)`-span, over all
65535 nonzero `Δ`) and ran all three matrices:

| matrix | prediction in the report | **my measured result** |
|---|---|---|
| AES-shaped `M4`, first row `(02,03,01,01)` | 65535/65535 close to dim 16 | **65535/65535 at dim 16 — PASS, as predicted** |
| `null_1` = identity (no MixColumns) | "0 of 65535 close to 16 (all stall at 4)" | **0/65535 reach 16 — stall confirmed — but at dimension 1, not 4** |
| `null_2` = circulant `(02,00,01,01)` with a zero entry | "a nonzero fraction stall below 16" | **65535/65535 close to dim 16 — NO STALL. Same reading as the AES-shaped matrix.** |

Two findings, of very different weight.

1. **The AES-shaped result confirms the engine of PROP-701-I exhaustively in
   the analogue.** This is the gate's main purpose and it passes, now with
   observed output rather than a prediction. It is independent corroboration of
   the proof I checked by hand in §7.3.
2. **`null_2` does not discriminate.** The gate carries a *pre-declared* VOID
   condition: "The gate is VOID … if EITHER null object below returns the same
   verdict as the AES-shaped matrix." On the instantiation the report names —
   first row `(02,00,01,01)` — that condition **fires**. Under the producer's
   own rule the gate as specified is VOID. The mathematical reason is
   instructive and is the general lesson: "every entry nonzero" is a
   *sufficient* hypothesis of Step 2, not a necessary one, so knocking it out
   does not have to change the conclusion. A null built by negating a
   sufficient hypothesis is not automatically a discriminating null.
   Recorded as **D-705-1 (medium)** — the most substantive defect I found in
   check (a).
   Mitigating: `null_1` *does* discriminate, sharply and in the right
   direction, and it is the one the report designates the sensitivity anchor
   ("control-of-the-control": if `null_1` does not stall, the run is void before
   the target is read). So the gate retains a working positive control.
3. `null_1`'s **predicted numeric reading is wrong**: the report says the span
   stalls at dimension 4 (the coordinate line `GF(2^4)·e_k`); the closure
   actually stalls at dimension **1**, because from `λ e_k` the rule returns
   `λ e_k` itself and never produces a second scalar. The containment claim is
   right, the achieved dimension is not. The qualitative verdict (stall, closure
   fails on the null) is unaffected. Folded into **D-705-1**.

**Can this gate's positive control discriminate against its own null object?**
Partly. Against `null_1`: **yes**, decisively (dim 16 vs dim 1), and the
discrimination is structural rather than an activity pattern — the gate never
touches the S-box, which is the direct and correct repair of BATCH-001 defect
I-3. Against `null_2` as instantiated: **no**. The report's claim that "the
three readings are qualitatively different, not different by a threshold" is
**falsified by measurement** for the third reading.

This defect sits in `candidate_report.yaml`, not in the derivation note, and
does not touch either proposition or the note's promotion fitness.

---

## 8. Defects from check (a)

| id | severity | statement |
|---|---|---|
| D-705-1 | medium | `GATE-701-C`'s `null_2` (circulant `(02,00,01,01)` over `GF(2^4)`) does not discriminate: I measured 65535/65535 closing to dimension 16, the same reading as the AES-shaped matrix, which fires the gate's own pre-declared VOID condition. `null_1`'s predicted stall dimension is 4 in the report and 1 in measurement. `null_1` does discriminate and the AES-shaped case passes. |
| D-705-2 | low | `verify_derivation.py` claim `C0` cannot import the BATCH-001 harness because the module is not registered in `sys.modules` before `exec_module`, so `@dataclass` resolution fails. Script defect, not a harness defect. `C0`'s intent covered independently in §3.1. |
| D-705-3 | informational | Note §2.4's phrase "1073758335 independent binary choices" is loose; the number is an orbit count, as the note itself states elsewhere. |
| D-705-4 | informational | `PROP-701-I`'s OD-1 scope text describes the argument as iterating "an unbounded number of times", which overstates the cost of re-application; the substantive point (layer-dependence breaks it) is correct. |
| D-705-5 | low | `PROP-701-I` does not name two scope holes: word-position-dependent families `π_0..π_3` within a layer, and restriction of the "for every state `s`" quantifier to a structured subset. Neither is OD-1..OD-5. |
| D-705-6 | low | The TASK-20260731-704 snapshot receipt still carries `commit_sha: null` and `parent_sha: null`; the follow-on write it prescribes did not occur. Digests bind regardless. |

None of these is an evidence-integrity failure and none is a fabrication.

---

## 9. Verdict for check (a)

**passed, with defects.**

- The derivation note is **self-contained**, both propositions **reproduce**
  (16/17 script claims, 0 FAIL) and **independently recompute** by my own
  methods with no discrepancy, both additions beyond BATCH-001 are **correct**
  and the second properly bounds the note's scope, `proof_status: derivation`
  is **honest**, and the scope statements are **honest**.
  **Fit for promotion to knowledge as a standalone artifact.**
- The ideation package meets the object-first, deduplication, closure and
  Pareto-honesty obligations; `NO_ADMISSIBLE_NEXT_MECHANISM` is a **closure**,
  not a fatigue report; `PROP-701-I`'s proof is **complete**, with two unnamed
  scope holes (D-705-5).
- The one substantive defect is **D-705-1**: the closure's own falsification
  gate has a non-discriminating second null, and by its own pre-declared rule
  would be VOID as specified. The gate's primary claim nevertheless verifies
  when I run it.

I change no official state, propose no hypothesis status, promote nothing, and
assign no evidence strength.
