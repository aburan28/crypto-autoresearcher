# VAL-BATCH-001 — independent validation of the GOAL-SSIQ-001 BATCH-001 producer packages

**Task:** TASK-20260805-89a2e7 · **Role:** validator · **Goal:** GOAL-SSIQ-001 · **Batch:** BATCH-001
**Reviewed (both snapshot-frozen, read from the committed tree):**

- `coordination/goals/GOAL-SSIQ-001/batches/BATCH-001/tasks/TASK-20260805-85af9d/` — exponent-budget re-derivation, frozen at commit `50596409` by `archives/TASK-20260805-750709-receipt.yaml`
- `coordination/goals/GOAL-SSIQ-001/batches/BATCH-001/tasks/TASK-20260805-87e568/` — L1/L4 method-ceiling audit, frozen at commit `7ec7f730` by `archives/TASK-20260805-3494ac-receipt.yaml`

**Validation performed at** `HEAD = 1a7436cff73206c8ff339ea189639c54cf0f648f`, working tree clean
(`git status --porcelain` empty). No repository file was modified by this task other than this
report. No ledger record, no raw artifact, and no record status was touched.

**OVERALL VERDICT: ADMIT-WITH-CONDITIONS** (conditions = findings V4, V6, V9, V12; none of them
is a soundness defect in the two load-bearing results, all of them are scope- or
precision-conditions on how those results may be transcribed into the ledger).

---

## 0. Inference and independence cap — stated first, because it bounds everything below

| field | value |
|---|---|
| `requested_policy` | `review-adversarial` |
| adapter binding | `python3 -m orchestration.adapter resolve --role validator --independent-session` → `review-adversarial -> anthropic:claude-opus-5 (effort=xhigh)` |
| `resolved_model_id` | `claude-opus-5` (runtime self-report; **`model_verified: false`** — `doctor --probe` not run, this task is zero-compute) |
| `reasoning_effort` | not assertable under this binding; the policy's `xhigh` requirement was **not** verified as applied |
| `fallback_used` | **true** |
| `fallback_reason` | Subagent frontmatter cannot express a policy (CLAUDE.md, "Model policy note"); this session runs `model: inherit`, so the alias fell back to the session model rather than being launched with the resolved environment. |
| `independent_session` | true |
| `independence_kind` | **SESSION only, not MODEL** |

**The cap, stated plainly.** Both producers ran on `claude-opus-5` (their own reports record this,
with the adapter's table answer `anthropic:claude-sonnet-5` recorded alongside because the two
disagree). This validation also ran on `claude-opus-5`. Producer and validator are therefore the
**same model in different sessions**. A systematic error shared by the model — e.g. a
mis-remembered form of the Deuring/Eichler embedding count — would not be caught by this pass,
because both sides would make it. **Evidence built on this batch may not exceed `preliminary`.**
This is the same cap that held `EV-SSI-005` at `preliminary` and it was recorded at batch open
(`BATCH-001-OPENING.md` §5), so it is not a surprise.

**Mitigation actually applied against that cap.** Wherever a load-bearing step rested on model
recall rather than on text, I fetched a primary source this session and quote it (see §4.3 and
§5). That converts the two most correlated steps — D1's ingredients (c) and (e) — from
"two sessions of one model agree" into "anchored to fetched text". It does not remove the cap.

---

## 1. Receipt verification (content-first) — **BOTH PASS**

Method: for each declared path, `git show <commit>:<path> | sha256sum` recomputed and compared
against the declared `path_sha256`; commit reachability and parent checked with
`git merge-base --is-ancestor` and `git log -1 --format=%P`; changed-path set from
`git show --name-only --format=''`. Hashes were **additionally** recomputed at `HEAD` to prove
the frozen artifacts have not drifted since the snapshot.

### 1.1 `TASK-20260805-750709` (freezes the TASK-20260805-85af9d package) — **PASS**

| check | result |
|---|---|
| commit `5059640927b6067277d10e50f73e3a436ba198c9` reachable from `HEAD` | **YES** |
| declared parent `d8701af525b7f39a90509c715ccadf96083ad150` | **matches actual parent** |
| changed-path set == declared set (6 paths) | **EQUAL**, no scope expansion |
| `path_sha256` of all 6 paths recomputed at the commit | **6/6 MATCH** |
| same 6 hashes recomputed at `HEAD` | **6/6 IDENTICAL** — no post-snapshot drift |
| commit message names the task and the source task | yes |

`commit_sha: null` inside the receipt file is correct by construction (the receipt is committed
inside the commit it describes) and the sha is carried in `dispatch_queue.json`
`tasks[].archive.commit_sha`, which is where I verified it. The receipt's own hash is absent from
its internal `path_sha256` for the same reason and is present in the queue's archive block, where
it also matches.

### 1.2 `TASK-20260805-3494ac` (freezes the TASK-20260805-87e568 package) — **PASS**

| check | result |
|---|---|
| commit `7ec7f730fe9988d6aa7154cb40eb49f3b81ee48b` reachable from `HEAD` | **YES** |
| declared parent `a191407f09a7198046e2f2e268bfc331ce12dd42` | **matches actual parent** |
| changed-path set == declared set (5 paths) | **EQUAL**, no scope expansion |
| `path_sha256` of all 5 paths recomputed at the commit | **5/5 MATCH** |
| same 5 hashes recomputed at `HEAD` | **5/5 IDENTICAL** |

### 1.3 The frozen input is also unchanged

`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` has blob sha `f8c3a690…` at `HEAD`, at
`50596409`, and at the producers' execution commit `d8701af5` — identical. Its content sha256 is
`ca34a0f784351992df72458b2410ed92a137a1811d5401a24810121116c7a9cf`, exactly the value both
producers recorded. The object I re-extracted from is byte-identical to the object they read.

> **Receipt verdict: both snapshots are admissible frozen objects. Content-verified, not merely
> reachability-verified.** Neither receipt asserts anything mathematical, and both say so.

---

## 2. Per-locator re-extraction — **45/45 verbatim, 45/45 support what they are claimed to support, 0 mismatches**

I re-extracted every entry of `line_locators.yaml` independently: parse the YAML, normalise
whitespace, and require the quotation to be a substring of the *declared* line of the frozen
file (with a ±3-line fallback search that was never needed). This is the mechanical half. The
**second and load-bearing half** — does the quoted sentence establish the `what_it_establishes`
attached to it — I did by reading the surrounding proof for each entry; the result column below
records that judgement, not the substring test.

Legend: **V** = verbatim at the declared line; **S** = supports its `what_it_establishes` as
written; a superscript marks a note in §2.1.

| # | factor | line | quotation (head) | V | S |
|---|---|---|---|---|---|
| 1 | HEAD | 19 | `**Theorem 1.1.** Assuming Heuristic 1, there is a La…` | ✓ | ✓ |
| 2 | HEAD | 13 | `The impact on concrete parameter sets remains to be …` | ✓ | ✓ |
| 3 | HEAD | 39 | `However, its memory cost is essentially as high as t…` | ✓ | ✓ |
| 4 | HEAD | 39 | `While the new algorithm improves the asymptotic cost…` | ✓ | ✓ |
| 5 | HEAD | 69 | `**Heuristic 1.** Let p be a prime number, and let E/…` | ✓ | ✓ ᴬ |
| 6 | F1 | 81 | `**Theorem 1.5 ([4]).** Let E be a supersingular elli…` | ✓ | ✓ |
| 7 | F1 | 177 | `From Theorem 1.5, we have that deg(φ) ≤ (p/2)^{1/3}.…` | ✓ | ✓ (locator correction is right: 177 opens the proof of **Lemma 3.4**; the proof of Thm 1.1 begins at 193) |
| 8 | F1 | 61 | `However, a recent result [4] proves that there alway…` | ✓ | ✓ |
| 9 | F1 | 266 | `[4] Yves Aubry, Roger Oyono, and Christelle Vincent.…` | ✓ | ✓ |
| 10 | F2 | 167 | `1. X ← B^{1/2} · (p/2)^{1/6};…` | ✓ | ✓ |
| 11 | F2 | 160 | `**Lemma 3.4.** Suppose that the smallest isogeny E →…` | ✓ | ✓ ᴮ |
| 12 | F2 | 177 | `Let k be the largest index such that Π_{i=1}^k ℓ_i ≤…` | ✓ | ✓ |
| 13 | F2 | 181 | `deg(η) = deg(φ)/deg(ψ) ≤ ℓ_{k+1}(p/2)^{1/3}/X ≤ B(p/…` | ✓ | ✓ (the `X=(B·D)^{1/2}` reading is correct — re-derived independently in §3.2) |
| 14 | F2 | 177 | `Note that by minimality of φ, it must have cyclic ke…` | ✓ | ✓ |
| 15 | F2 | 183 | `Let χ = η̂^{(p)}. The codomain of η is E^{(p)}, so t…` | ✓ | ✓ |
| 16 | F2 | 87 | `and to Andrea Basso for suggesting a tighter choice …` | ✓ | ✓ |
| 17 | F3 | 131 | `**Definition 3.1.** Let E be an elliptic curve, and …` | ✓ | ✓ |
| 18 | F3 | 133 | `**Lemma 3.2.** For any X > B > 0, we have #L(E, X, B…` | ✓ | ✓ (the "Lemma 3.2 not 3.3" and "≤ not =" corrections are both right) |
| 19 | F3 | 135 | `*Proof.* For any x < X, the number I(x) of isogenies…` | ✓ | ✓ |
| 20 | F3 | 154 | `**Lemma 3.3.** Algorithm 2 terminates in time Ψ(X, B…` | ✓ | ✓ |
| 21 | F3 | 156 | `From Lemma 3.2, the size of the table L is at most Ψ…` | ✓ | ✓ |
| 22 | F3 | 158 | `The cost of computing the list is thus at most #L · …` | ✓ | ✓ |
| 23 | F3 | 216 | `Ψ(X, B) = Xw^{−w(1+o(1))} = p^{1/6+o(1)}p^{o(1)} = p…` | ✓ | ✓ ᶜ |
| 24 | F3 | 218 | `We deduce that each attempt costs Ψ(X, B)X^{1+o(1)}B…` | ✓ | ✓ |
| 25 | F3 | 226 | `The size of the tables constructed in Algorithm 2 is…` | ✓ | ✓ ᴰ |
| 26 | F3 | 228 | `M = Ψ(X, B)X.…` | ✓ | ✓ |
| 27 | F3 | 230 | `This is derived like the upper bound from Lemma 3.2,…` | ✓ | ✓ ᴰ |
| 28 | F4 | 187 | `**Lemma 3.5.** Suppose that E is a uniformly random …` | ✓ | ✓ |
| 29 | F4 | 189 | `*Proof.* By Lemma 3.4, the algorithm succeeds when t…` | ✓ | ✓ |
| 30 | F4 | 210 | `By Lemma 3.5, and thanks to Heuristic 1, the success…` | ✓ | ✓ |
| 31 | F4 | 212 | `P0 = √log(p/2)^{−√log(p/2)(1+o(1))} = p^{−log(√log(p…` | ✓ | ✓ (re-derived: `u=√log(p/2)`, `u^{-u}=p^{-o(1)}`) |
| 32 | F4 | 218 | `We deduce that each attempt costs Ψ(X, B)X^{1+o(1)}B…` | ✓ | ✓ |
| 33 | F4 | 191 | `**Remark 1.** Lemma 3.5 is a simple lower bound on t…` | ✓ | ✓ |
| 34 | F4 | 77 | `**Theorem 1.4 ([10]).** Let X, B > 0, and u = log X …` | ✓ | ✓ |
| 35 | F5 | 193 | `It repeatedly calls Algorithm 2 on uniformly random …` | ✓ | ✓ |
| 36 | F5 | 200 | `1. B ← e^{(1/3)√log(p/2)}; Note that in practice, on…` | ✓ | ✓ |
| 37 | F5 | 214 | `Writing w = log(X)/log(B) = (1/2 log B + 1/6 log(p/2…` | ✓ | ✓ |
| 38 | F6 | 193 | `We fix the length n of the random walk to ensure tha…` | ✓ | ✓ |
| 39 | F6 | 202 | `3. ω ← a non-backtracking random walk φ : E → E′ of …` | ✓ | ✓ |
| 40 | F7 | 171 | `5. if (E′)^{(p)} is the key of an entry ((E′)^{(p)},…` | ✓ | ✓ |
| 41 | F7 | 185 | `We have proved that both (E′, ψ) and (E′^{(p)}, χ) a…` | ✓ | ✓ |
| 42 | F7 | 39 | `the algorithm essentially resolves a claw-finding pr…` | ✓ | ✓ |
| 43 | F7 | 39 | `The time-memory tradeoff of van Oorschot–Wiener [43]…` | ✓ | ✓ |
| 44 | F8 | 156 | `Computing the polynomial Φ_ℓ(j(E′), x) ∈ F_{p^2}[x] …` | ✓ | ✓ |
| 45 | F8 | 156 | `We do not presently investigate the best possible ex…` | ✓ | ✓ ᴱ |

**MISMATCH COUNT: 0.** No fabricated line number, no fabricated quotation, no lemma
misnamed in the locator file, no reference misprinted.

### 2.1 Notes on the five entries where the *interpretation* needs a word (none is a mismatch)

- **ᴬ (#5).** "The whole `p^{1/3+o(1)}` tier is conditional on this and on nothing weaker" is
  correct for **Theorem 1.1**. Corollary 1.2 additionally routes through `[35, Thm 1]` and
  `[35, Prop 8.5]`; the package does flag those separately as CITED-NOT-VERIFIED and assigns them
  no exponent, so nothing downstream is affected.
- **ᴮ (#11).** "The opening reading's attribution of the split bound to *Lemma 3.4* points at a
  sentence that does not carry it" is literally true of the **statement** of Lemma 3.4; the bound
  lives in its **proof** (lines 177–181), which the package says in the same breath. The
  correction is right but is a precision correction, not a substantive error in the opening
  reading.
- **ᶜ (#23).** "`Ψ(X,B)` is strictly below `X` while still `X^{1+o(1)}`" is loose notation:
  `Ψ = X·w^{−w(1+o(1))}` is `X^{1−o(1)}`, i.e. *smaller* than `X` by a superpolynomial factor.
  The p-exponent claim actually used (`Ψ = p^{1/6+o(1)}`) is correct and nothing depends on the
  notation.
- **ᴰ (#25, #27).** These carry the §4.1 **lower** bound on the table size, and the
  `what_it_establishes` says it "pins `q = 2` two-sidedly for the full list". The lower bound is
  *asserted* inside a section the source itself frames as a rough estimate under optimistic
  assumptions (line 43: *"these estimates make optimistic assumptions … should not be interpreted
  as accurate predictions"*; line 226: *"Let us estimate a lower bound … under the assumption that
  the bound … in Lemma 3.5 is tight"*). The `provenance` field is honest ("lower: §4.1 only"), but
  "pins two-sidedly" is a stronger word than "asserted in a rough-estimation section". → **Finding
  V6.**
- **ᴱ (#45).** The `what_it_establishes` cites the source calling the unoptimised `O(1)`
  "critical for practice". That phrase is on line 156 but **outside the quoted slice**. It is on
  the declared line, so it is not a fabrication; the slice alone does not carry it.

### 2.2 The eight `checked_and_absent` negative claims — **all 8 independently re-run and confirmed**

I re-ran every declared search on the frozen file. `1/4`: 0 hits. `minkowski` (case-insensitive):
0 hits. `lower bound`: exactly 2 hits, lines 191 (a bound on a **probability**) and 226 (a bound
on **concrete cost**) — neither bounds a degree from below, as claimed. `optimal`: exactly 3 hits,
lines 191, 200, 230, none asserting optimality of `(p/2)^{1/3}` or of `p^{1/3+o(1)}`. `kani`: 0
hits. `precomput`: 1 hit, line 200, about the parameter `B`. `subfield|locus|rational subgraph`:
only inside reference title [15]. No `Õ(p^{1/4})` figure anywhere.
**One under-enumeration, cosmetic:** the `Delfs` search reports line 51 only; line 53 also
mentions Delfs–Galbraith (*"reused in [40] to accelerate the Delfs–Galbraith algorithm, although
still within the p^{1/2}·(log p)^{O(1)} asymptotic"*). That extra hit **strengthens** the stated
consequence rather than weakening it. → **Finding V11** (cosmetic).

Also cosmetic: `line_locators.yaml` and `task_report.yaml` record `total_lines: 351`; the file has
350 newline-terminated lines plus a trailing empty line. No locator is affected.

---

## 3. Independent re-derivation of the exponent composition and the 1/4 conditions

**I derived the following from the frozen text before opening `target_conditions.md`.** The
producer's file is compared against it in §3.5.

### 3.1 Setup (symbols mine, values from the text)

`D = p^d` the structural degree bound on the minimal `E → E^{(p)}` (line 81: `d = 1/3`);
`B = p^β` the smoothness bound; `X` the per-side degree bound; `#L` the table cardinality.

### 3.2 The split constraint forces `X`

Greedy prefix cut with all primes `≤ B` gives `deg ψ ≤ X` by construction and
`deg η = deg φ / deg ψ ≤ ℓ_{k+1}·D / X ≤ B·D / X`. Requiring the second half to also fit under
`X`:

```
B·D/X ≤ X  ⟺  X ≥ (B·D)^{1/2},   and the text takes the minimum,  X = (B·D)^{1/2}.
```

So **`X² = B·D` exactly**. This is my own derivation of line 181 read right-to-left, and it
agrees with the package.

### 3.3 Composition

`#L ≤ Ψ(X,B)·X·(log X + 2)`; with `β = o(1)`, `Ψ(X,B) = X·w^{−w(1+o(1))} = X·p^{−o(1)}`, so
`#L = X^{2+o(1)} = (B·D)^{1+o(1)} = D·p^{o(1)}`. Per-attempt cost = `#L·(B+log p)^{O(1)}` (build
dominates search, line 158) `= D·p^{o(1)}`. Success probability `P0 = u^{−u(1+o(1))}` with
`u = log(p/2)/(3 log B) = √log(p/2)` at the chosen `B`, so `P0 = p^{−o(1)}` and `P0^{−1} = p^{o(1)}`.

```
TIME   = per-attempt × P0^{-1} = D·p^{o(1)}      → exponent d
MEMORY = #L                    = D·p^{o(1)}      → exponent d
```

I also checked the two neighbouring regimes to confirm `β = o(1)` is not a free knob: at `β > 0`
constant, `Ψ ≍ X` and the cost becomes `p^{β+d} > p^d`; at `B = (log p)^C`, `u ≈ log p/(3C loglog p)`
and `P0^{−1} = p^{1/(3C)}`, giving `p^{d + 1/(3C)} > p^d`. **`B` cannot lower the exponent in
either direction.** (This corroborates F5's exponent-0 classification with an argument the
package states only qualitatively.)

### 3.4 My independent 1/4 conditions

With `T = c·q·d/k + r` (`c` = collision cost exponent in the per-side cardinality, `q` =
cardinality exponent in the per-side degree bound, `k` = split arity, `r` = exponent of `P0^{−1}`),
source values `(d,k,q,c,r) = (1/3,2,2,1,0)` reproduce `T = 1/3`, `M = 1/3`:

| factor | value needed for `T = 1/4`, others fixed | my verdict |
|---|---|---|
| `d` | **1/4** | admissible as an equation; `X → p^{1/8}`, `#L → p^{1/4}`, memory also `1/4` |
| `q` | **3/2** (`δ = 1/2`) | admissible as an equation |
| `k` | **8/3** | not an integer; `k=3 → 2/9`, `k=4 → 1/6` **but only if `c=1` at that arity** |
| `c` | **3/4** | **INADMISSIBLE alone**: `M = q·d/k = 1/3 > T = 1/4` is impossible |
| `r` | **−1/12** ⟹ `P0 = p^{1/12} > 1` | **NO SOLUTION EXISTS** |

Whole-target statement: the product `c·q·d/k` must be multiplied by `3/4` (equivalently `k` by
`4/3`), and that movement cannot be placed on `r`.

I re-verified every rational in the producer's joint table in exact arithmetic:
row 1 `(1/4,2,2,1) → 1/4`; row 2 `(1/3,2,3/2,1) → 1/4`; row 3 `(1/3,8/3,2,1) → 1/4`;
row 4 `(3/8,3,2,1) → 1/4`; row 5 `(1/2,4,2,1) → 1/4`; row 6 `(1/3,2,7/4,6/7) → T=1/4, M=7/24`
(inadmissible, correctly labelled); row 7 `(5/16,2,2,4/5) → T=1/4, M=5/16` (inadmissible,
correctly labelled). Also `T − M = (c−1)qd/k + r` ✓, and the vOW reading `c = 3/2` from
`√(N³/w)` ✓. The §4 exchange-rate algebra `T = (2−δ+e)/6`, `T=1/4 ⟺ e = δ − 1/2` ✓, with the
unaligned null `e = 2δ → T = (2+δ)/6` ✓ and the aligned null `e = δ → T = 1/3` for every `δ` ✓.

### 3.5 **AGREEMENT / DISAGREEMENT: my derivation AGREES with `target_conditions.md` on every
exponent, every condition, and every row of the joint table.** Two differences, both stated
rather than reconciled silently:

1. **`Y = (B·D)^{1/k}` is the wrong closed form for `k ≥ 3`.** The same greedy-cut argument gives
   pieces in `(Y/B, Y]`, so `(Y/B)^{k−1}·Y ≥ D`, i.e. `Y = (B^{k−1}·D)^{1/k}`. For `k = 2` the two
   agree. Since `B = p^{o(1)}`, **the p-exponent `d/k` the package uses is unaffected**, and no
   condition changes. Precision defect only. → **Finding V5.**
2. **The naive `k`-way collision cost is `c = k − 1`, not `c = 1`, and the package does not say
   so.** With `k` pieces the `k−1` intermediate curves are unknown, so the natural algorithm
   enumerates from every endpoint of one list: time `= (per-side cardinality)^{k−1}`, giving
   `T = 2d(k−1)/k` — `4/9` at `k=3`, `1/2` at `k=4`, i.e. **monotonically worse** than the
   incumbent `1/3`. The package correctly refuses to assume `c = 1` at `k ≥ 3` ("assuming `c = 1`
   there would be assuming the question") but leaves the *known baseline* unstated, which is what
   makes rows 4–5 read as cheap. → **Finding V4.**

---

## 4. **D1 — the gating check.** Verdict: **D1 SURVIVES.**

`L1_ceiling_audit.md` §6 derives: `#{E : δ_E ≤ T} ≪ Σ_{n≤T}(np)^{1/2+o(1)} ≪ T^{3/2}p^{1/2+o(1)}`,
hence `fraction(T) ≪ T^{3/2}p^{−1/2+o(1)}`; at `T = p^{1/4}` this is `p^{−1/8+o(1)}`, which is not
`p^{−o(1)}`, killing L1's second disjunct. The producer pre-committed the reversion
(disjunct 2 → UNRESOLVED) if a validator finds D1 unsound.

### 4.1 I re-derived D1 from scratch before reading §6, and obtained the same bound

Sketch of my independent route: an isogeny `φ : E → E^{(p)}` of degree `n` gives
`ψ = φ̂∘F ∈ End(E)` with `nrd(ψ) = np`; `p` is inert or ramified in any imaginary quadratic field
embedding in `B_{p,∞}`, so `p | trd(ψ)`, and `nrd ≥ trd²/4` forces `trd(ψ) = 0` as soon as
`np < p²/4`, i.e. `n < p/4`. Then `ψ² = −np` and `Z[√(−np)] ↪ End(E)`. The number of
supersingular curves admitting such an embedding is at most the number of embeddings, which is
the Hurwitz-type sum `Σ_{f² | 4np} h(−4np/f²)`. Summing over `n ≤ T` and dividing by the total
curve count `p/12 + O(1)` gives exactly `fraction(T) ≪ T^{3/2}p^{−1/2+o(1)}`.

Exponent arithmetic re-checked: `Σ_{n≤T} n^{1/2} ≍ T^{3/2}` ✓; at `T = p^{1/4}`,
`p^{3/8−1/2} = p^{−1/8}` ✓; the threshold `3θ/2 − 1/2 ≥ −o(1) ⟺ θ ≥ 1/3` ✓; vacuity at
`θ = 1/3` ✓. §6.4's method ceiling `total ≫ p^θ·p^{1/2−3θ/2} = p^{1/2−θ/2}` ✓, returning `p^{1/3}`
at `θ=1/3` and `p^{3/8}` at `θ=1/4`, with the inequality direction correct (an *upper* bound on
the fraction gives a *lower* bound on the attempt count).

### 4.2 Ingredient (c) — the question the producer asked me to settle: `n^{o(1)}` or `n^{1/2}`?

> **Determination: `n^{o(1)}`. The correction is harmless and D1's exponent stands.**

The orders between `Z[√(−np)]` and the maximal order are indexed by conductors `f` with
`f² | 4np`, and the total (not-necessarily-optimal) embedding count is
`Σ_{f² | 4np} h(−4np/f²)`. Bounding each term by (d):

```
Σ_{f²|4np} h(−4np/f²)  ≪  (4np)^{1/2} log(np) · Σ_{f²|4np} 1/f
                       ≤  (4np)^{1/2} log(np) · σ(4np)/(4np)
                       =  (np)^{1/2} · log(np) · O(log log np)  =  (np)^{1/2+o(1)}.
```

The sum is dominated by `f = 1`; the divisor sum `Σ 1/f` is `O(log log)`, not a power of `n`. The
feared `n^{1/2}` would require the *largest* admissible conductor to dominate, and it cannot —
when `f` is large the class number it carries is correspondingly small. Note also that the
producer's own phrasing of (c) uses `H(4np)`, the **Hurwitz** class number, which already sums
over the intermediate orders by definition; (d) applies to `H` unchanged.

**Primary-source anchor fetched this session** (against the shared-model correlation risk):
Eisenträger–Hallgren–Leonardi–Morrison–Park, arXiv:2004.11495v2 (ar5iv rendering, sha256
`d2c3720759f8900a0d2b8714ca232bf91d63cd2d94a9555e3d09937dc837bcaa`), **Theorem 3.9 and its
proof**, verbatim: *"if `E` is a supersingular elliptic curve defined over `F_{p²}` with
`j`-invariant `j` … and `ℓ < p/4` is also a prime, then `E` is `ℓ`-isogenous to `E^{(p)}` if and
only if `Z[√(−ℓp)]` embeds into `End(E)` [9, Lemma 6]"*, together with
`|Emb_{O_K}(F_{p²})| ≫ √(ℓp)/log log(ℓp)` and a fibre bound `≤ (ℓ+1)·6` for `(E,f) ↦ j(E)`. That
is D1's ingredients (a)+(b) as an *iff* from published text, and the count `(ℓp)^{1/2±o(1)}`
matching (c)+(d) in **both** directions at prime `n = ℓ`. The same passage records that
*"In [9, Section 7], an upper bound is given for `S^p`"* — i.e. the upper-bound direction D1 needs
is a known computation, not an invention.

### 4.3 Ingredients (a), (d), (e)

- **(a) — verified verbatim from the re-fetched AOV §3** (byte-identical HTML, §5): *"since `p` is
  either inert or ramified in any imaginary quadratic field that embeds into `B_{p,∞}`, an element
  of `B_{p,∞}` of norm divisible by `p` must also have trace divisible by `p`. Combining this with
  the inequality (1), we thus have that if `α` is inseparable with `nrd(α) < p²/4`, then
  `trd(α) = 0`."* The producer's condition `n < p/4` is exactly `np < p²/4`. ✓
- **(d) `h(D) ≪ |D|^{1/2} log|D|` — CORRECT, and unconditional**: Dirichlet's class number formula
  `h(D) = w√|D|·L(1,χ_D)/(2π)` with the classical `L(1,χ_D) ≪ log|D|`. **I did not fetch a text
  for this**; it is textbook and uncontroversial, but I record that this one ingredient rests on
  standard theory rather than on an artifact retrieved this session. → **Finding V9.**
- **(e) `#{supersingular j-invariants} = p/12 + O(1)` — verified verbatim from a fetched primary
  source.** The Delfs–Galbraith preprint body (`dg_ar5iv`, hash matches the producer's log
  exactly) states `#S_{p²} = ⌊p/12⌋ + {0 if p≡1, 1 if p≡5,7, 2 if p≡11 (mod 12)}`. ✓

### 4.4 Two consistency checks D1 passes that the audit did not claim

- **At `T = 1`** D1 gives `#{E : δ_E = 1} ≪ p^{1/2+o(1)}` — matching the known size `≍ p^{1/2}` of
  the `F_p` locus, which the very same fetched Delfs–Galbraith text states independently
  (*"we expect to select a vertex in the subset of `j ∈ F_p` with probability approximately
  `p^{1/2}/p = 1/p^{1/2}`"*). D1 is therefore tight at the **bottom** end as well as vacuous
  exactly at the top end (`T = (p/2)^{1/3}`), which the audit did notice. A counting bound that is
  simultaneously tight at `T=1` and vacuous at `T=p^{1/3}` is behaving correctly across its whole
  range.
- **The `§6.4` conditionality flag can be discharged.** §6.4 was flagged as resting on the goal
  record's *unverified opening reading* of the exponent budget. The sibling task's corrected
  identity is `T = d` with `X² = B·D` (which I re-derived independently in §3), so the step
  "one attempt at threshold `p^θ` costs `X² ≈ p^θ`" survives the correction unchanged. The flag is
  satisfied, not merely outstanding.

### 4.5 D1 verdict and its consequence

> **D1 SURVIVES independent re-derivation. Ingredient (c) contributes `(np)^{o(1)}`, not `n^{1/2}`.
> The pre-committed reversion is NOT triggered: L1 disjunct 2 remains CLOSED.** Its status stays
> `proof_status: derivation` — a checkable argument, now with (a) and (e) anchored to fetched
> primary text, (c) anchored to a published statement of the same correspondence and count, and
> (d) resting on classical theory. It is not a cited theorem and not machine-checked.

Residual risks I could **not** eliminate and that any downstream record must carry: the fibre and
`|Aut|` weightings (`E` and `E^{(p)}` share an order, `|Aut| ∈ {2,4,6}`) are bounded factors that I
checked are `p^{o(1)}` but did not enumerate case by case; and the whole check was performed by
the same model as the producer (§0).

---

## 5. Re-fetch comparison — 14 of the 17 logged retrievals re-run

Method identical in spirit to the log's (`curl -sS -L --max-time`, system CA bundle, TLS never
disabled, `HTTPS_PROXY` never unset). Live web content is not immutable, so a hash difference is
scored on **content**, not on bytes.

| id | URL | logged sha256 (head) | re-fetch sha256 (head) | verdict |
|---|---|---|---|---|
| `aov_abs` | `arxiv.org/abs/2607.14624` | `09768304a2cb8d6e` | `09768304a2cb8d6e` | **IDENTICAL** |
| `aov_html` | `arxiv.org/html/2607.14624v1` | `eec18aefad605f87` | `eec18aefad605f87` | **IDENTICAL** — the body the whole L1 audit rests on |
| `aov_pdf` | `arxiv.org/pdf/2607.14624v1` | `6f556abbe4b3c3b6` | `6f556abbe4b3c3b6` | **IDENTICAL** (still not text-extractable here — see below) |
| `dg_doi` | `doi.org/10.1007/s10623-014-0010-1` | `32ed63159c77e21e` (3 038 B challenge) | `0482489d380afbf9` (295 066 B article page) | **DIFFERENT — my session was NOT bot-challenged.** Infrastructure difference, in the producer's favour: see §5.2 |
| `dg_springer` | `link.springer.com/article/…` | `32ed63159c77e21e` | `4dd81862187e62bf` (295 068 B) | **DIFFERENT** — same reason |
| `dg_springer_pdf` | `link.springer.com/content/pdf/…` | `32ed63159c77e21e` | `baa1a18489f771eb` (295 033 B, still HTML not PDF) | **DIFFERENT** — same reason; still no PDF body |
| `dg_crossref` | `api.crossref.org/works/…` | `f3f5bed003713 0e6` | `f3f5bed0037130e6` | **IDENTICAL** |
| `dg_arxiv_abs` | `arxiv.org/abs/1310.7789` | `cad7092ad9f577b6` | `cad7092ad9f577b6` | **IDENTICAL** |
| `dg_arxiv_api` | `export.arxiv.org/api/query?id_list=1310.7789` | `2a5de4f2d2c6d824` | `2a5de4f2d2c6d824` | **IDENTICAL** |
| `dg_s2` | Semantic Scholar Graph, DOI query | `a332a01cd4b8bbf0` | `a332a01cd4b8bbf0` | **IDENTICAL** |
| `dg_unpaywall` | `api.unpaywall.org/v2/…` | `ab83a1d1a1656ee5` | `ab83a1d1a1656ee5` | **IDENTICAL** |
| `dg_openalex` | `api.openalex.org/works/doi:…` | `5e1a153a2ab82b63` | `9ae1723180c8a1b1` | **DIFFERENT BYTES, IDENTICAL CONTENT** on every load-bearing field: `is_oa:false`, `oa_status:"closed"`, `oa_url:null`, `any_repository_has_fulltext:false`, no `abstract_inverted_index`, single publisher location. Differs in `updated_date` (2026-08-04) and `cited_by_count` — volatile fields |
| `dg_ar5iv` | `ar5iv.labs.arxiv.org/html/1310.7789` | `6761f976e2f6a17b` | `6761f976e2f6a17b` | **IDENTICAL** — the preprint body all §3 quotations rest on |
| `sccs_abs` | `eprint.iacr.org/2021/1488` | `08edb71a330b7912` | `08edb71a330b7912` | **IDENTICAL** |
| `dg_core` | CORE search | HTTP 429, empty body | not re-run | log's `e3b0c442…` is the canonical empty-string hash and is correctly annotated as such |
| `sccs_search`, `dg_galbraith_home` | — | — | not re-run | routing/negative entries, nothing rests on them |

### 5.1 Quotation re-verification from the re-fetched bodies

Using the producer's *corrected* extraction discipline (replace `<math>` by its `alttext`, strip
tags, **then** unescape), I re-extracted and compared every load-bearing quotation:

- **AOV Remark 4.3 — the quotation that carries L1 disjunct 1: VERBATIM CORRECT, all inequality
  signs present.** My extraction independently reproduces `θ ≥ 2/3`, `D ≤ Cp^θ`, `θ < 2/3`,
  `D_1 > Cp^θ`, `|t_{12}| ≤ D_1/2`, `D_1D_2 − t_{12}² ≥ 3D_1²/4 > (3C²/4)p^{2θ}`, and
  `if η < 1/3, then for any constant C' > 0 there exists a prime p and a supersingular elliptic
  curve E … with an isogeny E ⟶ E^{(p)} of degree at least C'p^η`. **The MathML-unescaping bug the
  producer caught mid-task did not survive into the frozen package** — the frozen quotation is the
  corrected one.
- **AOV §5.1 — the rank-3 statement: VERBATIM CORRECT**, including `R` rank 3 via `[AV]`, the
  bijection `φ ↦ φ̂∘F`, `Q' = Q/(4p)`, `discriminant p/4`, `N_1` the least degree, and
  `p/4 ≤ N_1N_2N_3 ≤ p/2`. The producer's `[…]` elisions skip only the Gram matrix and equation (7).
- **AOV §2.2 (Gross lattice, Hermite bound), Prop 3.1, Prop 4.1, Thm 4.2 and its Cassels proof,
  §6.2 data (`⌊∛(p/2)⌋ − δ(p) ≤ 4` / `≤ 5`, `p = 234,959`, Conjectures 6.3 and 6.8), §1 and §2.2
  `F_p`-locus `δ_E = 1`, and the `p = 22,273` non-realisable Gram matrix: ALL VERBATIM CORRECT**,
  and each is attributed to the right section.
- **Delfs–Galbraith preprint body: VERBATIM CORRECT** for *"By the birthday paradox, the heuristic
  running time of the algorithm is `Õ(p^{1/4})` binary operations"*, *"high-storage
  bi-directional-search algorithm … given as Algorithm 1"*, *"This step should require `Õ(p^{1/2})`
  steps"*, *"which only requires `Õ(p^{1/4})` steps"*, *"The second stage has no effect on the
  asymptotic running time"*, and *"probability approximately `p^{1/2}/p = 1/p^{1/2}`"*. I also
  re-checked the memory claim: no space bound is attached to the `F_p` algorithm anywhere in the
  preprint body; the only cost-sense occurrences are the abstract's `Õ(p^{1/2})` space for the
  `F_{p²}` MITM, "large storage" about `[Gal99]`, "lower storage version", "high-storage", and
  "little storage" for the descent. **Producer's §3.3 confirmed.** (Their "exactly five relevant
  occurrences" counts cost-sense hits; a raw grep over the ar5iv page returns far more, all
  boilerplate or "vector space".)

### 5.2 The one place where my re-fetch **improves on** the producer's outcome

SpringerLink served me the **published article landing page** (295 KB) where it served the
producer a 3 038-byte "Client Challenge". The published abstract, from the publisher's own site,
reads in the load-bearing part: *"It takes an expected Õ(p^{1/2}) bit operations, and also
Õ(p^{1/2}) space, by performing a 'meet-in-the-middle' breadth-first search in the isogeny graph.
… We give an algorithm to construct isogenies between supersingular curves over F_p that works in
Õ(p^{1/4}) bit operations."*

This is **word-for-word the abstract the producer relayed through Semantic Scholar**, now
first-party. Consequences: (i) `dg_s2` was a faithful relay; (ii) the RC4 mechanism the producer
established (arXiv *metadata* abstract vs the paper's own text, with the published version siding
with the paper's text) is **confirmed at the publisher**; (iii) the published **body** remains
unobtained — the landing page is metadata plus references, and the PDF route still returns HTML.
The producer's HEADLINE ("published body NOT obtained; published abstract obtained") is therefore
still exactly right; only the *route* to the abstract improved. Nothing in either deliverable
needs to change, and I record this as an infrastructure difference (AGENTS.md rule 5), not as a
defect. → **Finding V10** (a cheap, now-demonstrated route for a follow-up session).

I confirm independently that **no PDF text extractor is available** (`pdftotext` absent;
`import pypdf` dies in `pyo3_runtime`; `fitz`, `pdfminer`, `pikepdf` absent), so the producer's
anomaly A2 is real and the AOV audit does rest on one rendering of the paper. Note the log says
"pypdf … absent"; it is in fact *installed but non-functional*. Cosmetic.

---

## 6. Overclaim-drift check — **no drift found**

I searched both packages specifically for the five failure modes named in the task card.

1. **Any sentence reading as though a `p^{1/4}` algorithm exists, is likely, or is near:** none
   found. Both packages open with an explicit denial (`exponent_budget.md` §0,
   `target_conditions.md` §0 and §7, `lever_additions.md` preamble, `L1_ceiling_audit.md` VERDICT
   block and §10.1). `target_conditions.md` §3.3 volunteers evidence *against* convenience
   ("integer split arities skip over 1/4"). The nearest thing to an enthusiastic sentence is
   "**Row 4 and row 5 are the structurally interesting ones**", and it is hedged in the same
   paragraph by naming the unestablished assumption. → covered by **Finding V4**, not overclaim.
2. **Unconditional quotation of the `p^{1/3+o(1)}` tier:** none found. Every restatement I could
   locate carries the conditional-on-Heuristic-1 qualifier, and `exponent_budget.md` §0 fixes four
   qualifiers (conditional / memory = time / superpolynomial `o(1)` / expected-not-worst-case) with
   locators, which `target_conditions.md` §0 inherits by reference.
3. **`F_p` figure used as evidence about `F_{p²}`:** none found, in either direction. The
   prohibition is restated three times in `L4_baseline_acquisition.md` (headline, §5, §7) and the
   deliverable draws the *opposite* inference from its own material — that the `p^{1/4}` phase is
   asymptotically free in Delfs–Galbraith's own accounting.
4. **Memory dropped beside a time exponent:** none found. `exponent_budget.md` §3.3 and
   `target_conditions.md` §6 carry `M` beside `T` throughout, including the explicit statement that
   no route in the table gives `p^{1/4}` time at polynomial memory. `L4` records the `F_p`
   algorithm's memory as **unstated by the source** rather than assuming a value in either
   direction — which is the correct handling.
5. **A citation treated as verified when it is not:** none found. Seven external dependencies are
   marked CITED-NOT-VERIFIED in the first package with the reference text printed exactly as the
   source prints it (I checked all seven against lines 262–344 of the frozen file); the second
   package discloses eight further AOV-inherited dependencies as unfetched and flags `[AV]` as the
   most load-bearing of them.

**Null-object / controls-before-belief (inventor-protocol §3):** both packages run the control
rather than asserting a signal. `target_conditions.md` §4.1 and `lever_additions.md` A4 compute the
**two nulls of L2's own instrument** (independent membership `e = 2δ → T = (2+δ)/6`, worse than
baseline; aligned membership `e = δ → T = 1/3`, exact break-even for every `δ`) and state that a
measured `e ≈ δ` *is the null*, not a finding. I re-derived both and they are correct. This is the
right shape: the quantity that must decay is named, and the value it takes when the effect is
absent is pre-registered. `L1_ceiling_audit.md` §7 N4 runs the structural null object (a generic
supersingular target): the trace-zero reduction is unavailable, the governing lattice is rank 4,
and the exponent becomes `1/2` — the method **distinguishes** the structured object from the
structure-free surrogate, which is a passing control rather than a decorative one.

---

## 7. Premature-closure check — the symmetric failure

**The producer's claim that the goal record's named obstruction is a category error twice over is
CORRECT, and I verified both halves independently.**

1. **Direction.** Minkowski's convex-body theorem, Hermite's constant and Cassels' Theorem III are
   **upper** bounds on a lattice minimum given its determinant. They cannot force a floor: for any
   fixed determinant there are lattices of arbitrarily small minimum. Confirmed at the source —
   AOV Theorem 4.2's proof is literally an application of Cassels' Theorem III to get
   `f(u) ≤ ∛(2 Discr f)`, an upper bound. A "Minkowski-type **lower** bound" does not exist as a
   theorem shape.
2. **Rank.** I recomputed the rank-4 determinant myself from the frozen text's own statement
   (line 244): `det(P, Nrd) = [O:P]²·det(O, Nrd) = p⁴·(p²/16)`, and dividing a rank-4 form by `p`
   divides its determinant by `p⁴`, so `det(P, Nrd/p) = p²/16`. Hermite then gives
   `λ₁ ≤ γ₄·det^{1/4} = √2·(p²/16)^{1/4} = p^{1/2}/√2` — **exponent 1/2, strictly weaker than the
   known 1/3**. Confirmed.

**The rank-3 replacement does do the work claimed of it.** From the re-fetched AOV §5.1: `R` has
rank 3 (via the bijection `φ ↦ φ̂∘F` onto inseparable endomorphisms and the rank-3-ness of the
trace-zero inseparable sublattice), its degree form is `Q' = Q/(4p)` of discriminant `p/4`, and
`N_1 = δ_E`. Hermite in rank 3 with `γ₃ = 2^{1/3}` gives
`N_1 ≤ 2^{1/3}(p/4)^{1/3} = (p/2)^{1/3}` — **reproducing Theorem 1.5's constant exactly, not just
its exponent**. The rank drop from 4 to 3 is bought by the arithmetic constraint `p | trd`
(AOV §3, quoted in §4.3 above), which exists precisely because the target is the Frobenius
conjugate. So the exponent `1/3` is `1/rank` on a lattice of discriminant `≍ p`, and the audit's
one-line summary of itself is accurate.

**Does "CLOSED" rest on a genuine lower bound?** Split by disjunct:

- **Disjunct 1** rests on cited unconditional primary text (AOV Remark 4.3), re-fetched and
  re-read here. I re-checked the refutation logic: assuming `δ_E ≤ Cp^{1/4}` universally and taking
  `η = 0.3`, Remark 4.3 supplies witnesses with `δ_E ≥ C'p^{0.3}` for every `C'`; Theorem 4.2 forces
  the witness `p` to grow with `C'`, so `p^{0.05} ≤ C/C'` eventually fails. Contradiction. The
  quantifier structure is an infinitely-often statement about the **extremal** curve, and the audit
  states that explicitly rather than inflating it to `∀p ∃E`. ✓ *(Minor arithmetic slip in AOV
  itself, not in the audit: with `C = √(4C'/3)` the derived constant is `3C²/16 = C'/4`, so the
  printed conclusion should read `≥ (C'/4)p^η`. Immaterial — `C'` is universally quantified.)*
- **Disjunct 2** rests on D1, which is a **population** statement, and that is the correct shape:
  the audit demonstrates (via AOV §1 and §2.2, re-verified) that `δ_E = 1` exactly on the `F_p`
  locus, so **no per-curve floor exists at any positive exponent** and a universal lower bound is
  impossible in principle. The audit's §8 quantifier table draws precisely this distinction and
  warns that `(iii-a)` and `(iii-b)` are both "lower-bound shaped" yet point in opposite directions.
  **This is the opposite of "it looks saturated".**

**No premature closure found**, with one scope condition: L1's own wording admits "another
cheaply-recognisable auxiliary target", and case **N5** (oriented curves, prescribed-torsion
targets, higher-dimensional targets) is explicitly **NOT COVERED**. The audit says so in its
verdict scope line and in §12 R3/R5. A ledger transcription that writes "L1 CLOSED" without the
scope would overstate it. → **Finding V12.**

The audit also refuses to convert its method ceiling into a hardness claim (§10.3: D1 bounds a
*method*, not the supersingular isogeny problem; treating it otherwise would be the
"saturated framework mistaken for a saturated problem" failure). That refusal is correct and is
the single most important sentence in the package.

---

## 8. Numbered findings — each states what would resolve it

Severity: **BLOCKING** (must be resolved before the ledger archive) · **CONDITION** (must travel
with the record) · **NOTE** (record-hygiene).

**V1 — CONDITION. Independence is session-only; the batch's evidence ceiling is `preliminary`.**
Both producers and this validator resolve to `claude-opus-5`; `review-adversarial` binds to
`anthropic:claude-opus-5 (effort=xhigh)` but this subagent runs `model: inherit`, so `xhigh` was
neither applied nor verifiable and `fallback_used: true`. A shared systematic error would not be
caught. *Resolves when:* a second backend resolves (`orchestration.adapter doctor --probe`) and D1
in particular is re-checked by a genuinely different model; until then, no record built on this
batch may exceed `preliminary`, and this cap must appear in the record itself, not only here.

**V2 — NOTE. `model_verified: false` across all three tasks.** No `doctor --probe` was run by
anyone (correctly, since all three tasks are zero-compute). *Resolves when:* a probe is run in a
session that is permitted network calls for that purpose, and the identifier is recorded as
probe-verified.

**V3 — CONDITION. D1 is a derivation, not a theorem, and must be transcribed as one.**
It survives (§4), and its ingredients are now anchored: (a) and (e) to fetched primary text, (c) to
a published statement of the same correspondence and count magnitude, (d) to classical theory.
It remains `proof_status: derivation` under `docs/claims-and-verification.md`. *Resolves when:* the
count is checked against a cited theorem statement of the Deuring/Eichler optimal-embedding number
(e.g. via Charles–Goren–Lauter §7, which EHL+20 names as containing the matching upper bound), or
the derivation is routed to a human referee.

**V4 — CONDITION. The `k ≥ 3` rows are not free, and the known baseline moves the wrong way.**
`target_conditions.md` §3.3/§5 rows 3–5 and `lever_additions.md` A1 all price a deeper split at
`c = 1`, which the package correctly declines to assume — but does not state that the *naive*
`k`-way collision costs `c = k − 1`, giving `T = 2d(k−1)/k` = `4/9` at `k=3` and `1/2` at `k=4`,
i.e. **worse than the incumbent**. Calling rows 4–5 "the structurally interesting ones" without
that number risks a reader treating a `k`-split as cheap. *Resolves when:* the naive baseline
`c = k−1` is recorded beside those rows (a one-line addition in a superseding record; the frozen
artifact must not be edited), so that A1's requirement (ii) reads as "beat `c = k−1`", not as
"establish `c = 1`".

**V5 — NOTE. `Y = (B·D)^{1/k}` should be `Y = (B^{k−1}·D)^{1/k}` for `k ≥ 3`.** The greedy-cut
argument gives pieces in `(Y/B, Y]`. Agrees at `k = 2`; the p-exponent `d/k` is unaffected because
`B = p^{o(1)}`, so **no condition in the package changes**. *Resolves when:* the closed form is
corrected in whatever record inherits it.

**V6 — CONDITION. "`q = 2` is pinned two-sidedly" overstates the status of the lower half.**
The matching lower bound is asserted in §4.1, a section the source frames as a rough estimate under
optimistic assumptions (lines 43, 226, 240), and rests on the unproved-here count "the number of
isogenies of degree `d` is at least `d`". The upper half (Lemma 3.2) is proved, modulo the cited
`[2, Lemma 5.7]`. *Resolves when:* the record says "upper bound proved (on a cited count); lower
bound asserted in the source's rough-cost section", which the package's own `provenance` field
already says — the `what_it_establishes` prose is what needs to match it.

**V7 — NOTE. Locator #45's `what_it_establishes` quotes a phrase from outside its slice.**
"critical for a practical deployment" is on line 156 but not inside the quoted text.
*Resolves when:* the slice is extended, or the claim is attributed to the line rather than to the
quotation.

**V8 — NOTE. `total_lines: 351` vs 350 newline-terminated lines**, and the `Delfs` absence-search
enumerates line 51 but not line 53 (the extra hit strengthens the stated consequence).
*Resolves when:* corrected in a superseding record; no locator or conclusion is affected.

**V9 — CONDITION. Ingredient (d) is the one D1 ingredient with no artifact.** `h(D) ≪ |D|^{1/2}
log|D|` is Dirichlet's formula plus `L(1,χ) ≪ log|D|`; unconditional and uncontroversial, but I
verified it from standard theory, not from a text fetched this session — which under V1 means one
model's recall. *Resolves when:* a citation with a locator is attached (any analytic number theory
text; the effective statement is classical).

**V10 — NOTE. The Springer bot-challenge is intermittent, and the published landing page IS
reachable.** My re-fetch returned the article page and its publisher-side abstract, confirming the
relayed abstract word-for-word and confirming the RC4 mechanism first-party. The published **body**
is still not obtained. *Resolves when:* a follow-up session retries the Springer route (now
demonstrated to work at least sometimes) and, if the body is still withheld, tries Delfs' thesis —
the route the producer already named.

**V11 — NOTE. The producer's log entry for `dg_core` and the "pypdf absent" phrasing.** The 429
zero-byte entry is correctly hashed and correctly annotated as an unresolved route rather than a
negative result. `pypdf` is installed but non-functional (`pyo3_runtime.PanicException`), which I
reproduced; "absent" understates the diagnosis slightly. *Resolves when:* the environment gains a
working PDF text extractor — which would also let the AOV audit rest on two independent renderings
instead of one (producer anomaly A2), and would let `[AV]` (arXiv:2602.05284, which I confirmed is
fetchable in one call, HTML sha256 `5bc2b950b5d256fcf18d6af47f2083c741e5f55aa9cf964fa93ca60d77152c81`,
**contents not verified by me**) be checked — it is the load-bearing unfetched dependency behind
AOV §5.1.

**V12 — CONDITION (the most important one for the ledger). "L1 CLOSED" must be written with its
scope attached.** The verdict is: disjunct 1 closed by cited primary text; disjunct 2 closed by a
surviving derivation; **scoped to the target `E^{(p)}` and small-degree-modified neighbours; case
N5 (structurally different auxiliary targets) NOT COVERED**, and L1's own wording admits exactly
that substitution. *Resolves when:* the goal record and any checkpoint state the verdict as
"CLOSED (scoped), N5 open, revisit condition R3" rather than "L1 CLOSED", and carry the audit's own
§10.3 disclaimer that D1 is a ceiling on a method and asserts nothing about the hardness of the
supersingular isogeny problem.

---

## 9. Terminal verdict

> ## **ADMIT-WITH-CONDITIONS**

Both snapshot receipts are content-verified. All 45 locators re-extract verbatim from the
byte-identical frozen source and all 45 support what they are claimed to support. My independent
re-derivation of the exponent composition and of the conditions for total exponent `1/4` **agrees
with the producer's on every value**, with two precision differences recorded rather than
reconciled (V4, V5). **D1 survives independent re-derivation** — ingredient (c) contributes
`(np)^{o(1)}`, decisively not `n^{1/2}` — so the pre-committed reversion is not triggered and L1
disjunct 2 stays CLOSED; disjunct 1 stays CLOSED on re-fetched, byte-identical primary text whose
inequality signs I confirmed survive the producer's mid-task extraction bug. Fourteen of seventeen
logged retrievals re-fetched; every hash that matters is byte-identical, and the three that differ
differ in the producer's favour or in volatile metadata only. No overclaim drift and no premature
closure detected; the null-object controls are present and correctly computed on both sides.

The conditions are V4, V6, V9 and V12: they concern how these results are **transcribed**, not
whether they hold. And V1 binds everything — this is one model checking itself in a second
session, so nothing in this batch may be promoted above `preliminary`.

**What a passed validation does and does not mean.** It means these two packages are admissible
evidence. It does **not** support any ECDLP or isogeny claim, does not demonstrate a speedup, does
not assert that a `p^{1/4}` algorithm exists or is near, and does not authorise any promotion. The
lever verdict recorded here is an inventor-protocol §8 audit verdict; only the Coordinator may move
a record status.

---

### Artifact paths

- this report: `/home/user/crypto-autoresearcher/coordination/goals/GOAL-SSIQ-001/batches/BATCH-001/reviews/VAL-BATCH-001.md`
- validated: `/home/user/crypto-autoresearcher/coordination/goals/GOAL-SSIQ-001/batches/BATCH-001/tasks/TASK-20260805-85af9d/{exponent_budget.md,line_locators.yaml,target_conditions.md,lever_additions.md,task_report.yaml}`
- validated: `/home/user/crypto-autoresearcher/coordination/goals/GOAL-SSIQ-001/batches/BATCH-001/tasks/TASK-20260805-87e568/{L1_ceiling_audit.md,L4_baseline_acquisition.md,source_access_log.yaml,task_report.yaml}`
- receipts: `/home/user/crypto-autoresearcher/coordination/goals/GOAL-SSIQ-001/batches/BATCH-001/archives/{TASK-20260805-750709-receipt.yaml,TASK-20260805-3494ac-receipt.yaml}`
- frozen source: `/home/user/crypto-autoresearcher/inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` (sha256 `ca34a0f7…16c7a9cf`)
- sources re-fetched this session (hashes in §5): arXiv:2607.14624v1 (abs/html/pdf), arXiv:1310.7789 (abs/api/ar5iv), Springer/DOI/Crossref/Unpaywall/OpenAlex/Semantic-Scholar for `10.1007/s10623-014-0010-1`, eprint.iacr.org/2021/1488, and — added by this validation — arXiv:2004.11495v2 via ar5iv (sha256 `d2c3720759f8900a0d2b8714ca232bf91d63cd2d94a9555e3d09937dc837bcaa`) and arXiv:2602.05284 (fetched, contents not verified).
