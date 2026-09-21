# Classic McEliece parameter sets — transcription

**Task:** TASK-20260803-f3aece · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-001
**Question:** RQ-MCE-e65b3c · **Date:** 2026-08-03
**Role:** executor · `requested_policy: executor-implementation` ·
`resolved_model_id: claude-opus-5` · `fallback_used: true`

> **This document transcribes. It assesses nothing.** No statement here says or
> implies that any parameter set is secure, adequate, threatened, or adequate
> against any attack. Where the sources make security *claims*, those claims are
> reproduced as claims of the source, attributed, and left unevaluated.

---

## 0. Sources, and which fact came from which

Every number below is traceable to one of these four documents. All were
fetched 2026-08-03; URLs, HTTP statuses, byte counts and sha256 are in
`source_access_log.yaml`. **No number in this document is recalled from
training data.** No `[RECALLED-NOT-READ]` marker was required, because no
recalled number was used.

| Key | Document | Role here |
|---|---|---|
| **SPEC** | `mceliece-spec-20221023.pdf` — *"Classic McEliece: conservative code-based cryptography: cryptosystem specification"*, 23 October 2022, 16 pp. sha256 `dcc68788…` | (m, n, t); the definition `k = n − mt`; size formulas; ℓ = 256 |
| **IMPL** | `mceliece-impl-20221023.pdf` — *"…guide for implementors"*, 19 pp. sha256 `86225992…` | Table 1: numeric key / ciphertext / session-key sizes in bytes |
| **SEC** | `mceliece-security-20221023.pdf` — *"…guide for security reviewers"*, 36 pp. sha256 `db17ef08…` | The submission's claimed NIST "categories" |
| **PC** | `mceliece-pc-20221023.pdf` — *"…what plaintext confirmation means"*, 1 p. sha256 `9894108c…` | What the `pc` variants change |

The specification is the primary document by the designers' own designation:
`spec.html` (v2026.06.13) states *"The official definition of Classic McEliece
is the cryptosystem specification"*, linking SPEC. SPEC itself contains **no**
security categories and **no** numeric byte sizes. The round-4 submission
overview delegates those explicitly — *"Expected strength (2.B.4) for each
parameter set — See the separate 'guide for security reviewers' document"* and
*"Detailed performance analysis (2.B.2) — See the separate 'guide for
implementors' document"* — so SEC and IMPL are the specification's own
designated sources for them, not substitutes chosen by me.

---

## 1. The parameters, transcribed

SPEC §7 *"Selected parameter sets"* defines **ten** sets. It is running prose,
not a table, so table-extraction damage does not arise; both extractors
(pypdf 6.14.2 and pdfminer.six 20260107) returned identical text.

Verbatim form of each entry, e.g. §7.7:

> *"7.7 Parameter set mceliece6960119 — KEM with m = 13, n = 6960, t = 119.
> Field polynomials f(z) = z^13 + z^4 + z^3 + z + 1 and F(y) = y^119 + y^8 + 1."*

The `f` sets are the same (m, n, t) plus *"Semi-systematic parameters
(µ, ν) = (32, 64)"* (SPEC §7.2, §7.4, §7.6, §7.8, §7.10). (µ, ν) does not
enter n, k or t.

| Parameter set | m | n | t | source |
|---|---:|---:|---:|---|
| mceliece348864 | 12 | 3488 | 64 | SPEC §7.1 |
| mceliece348864f | 12 | 3488 | 64 | SPEC §7.2 |
| mceliece460896 | 13 | 4608 | 96 | SPEC §7.3 |
| mceliece460896f | 13 | 4608 | 96 | SPEC §7.4 |
| mceliece6688128 | 13 | 6688 | 128 | SPEC §7.5 |
| mceliece6688128f | 13 | 6688 | 128 | SPEC §7.6 |
| mceliece6960119 | 13 | 6960 | 119 | SPEC §7.7 |
| mceliece6960119f | 13 | 6960 | 119 | SPEC §7.8 |
| mceliece8192128 | 13 | 8192 | 128 | SPEC §7.9 |
| mceliece8192128f | 13 | 8192 | 128 | SPEC §7.10 |

`k` is **not** listed in §7. It is defined in SPEC §3, verbatim:

> *"A positive integer t ≥ 2 with mt < n. This also defines a parameter
> k = n − mt."*

So `k` below is computed from the specification's own definition, not
transcribed and not recalled.

---

## 2. THE RATE, with the arithmetic shown

Named duty 1. `k = n − mt`; rate `R = k/n`, given as an exact rational in
lowest terms and as a decimal. The `f` variants share their base set's row.

| Parameter set | n | m·t | k = n − mt | k/n exact | k/n decimal |
|---|---:|---:|---:|---:|---:|
| mceliece348864(f) | 3488 | 12·64 = 768 | 3488 − 768 = **2720** | **85/109** | **0.779817** |
| mceliece460896(f) | 4608 | 13·96 = 1248 | 4608 − 1248 = **3360** | **35/48** | **0.729167** |
| mceliece6688128(f) | 6688 | 13·128 = 1664 | 6688 − 1664 = **5024** | **157/209** | **0.751196** |
| mceliece6960119(f) | 6960 | 13·119 = 1547 | 6960 − 1547 = **5413** | **5413/6960** | **0.777730** |
| mceliece8192128(f) | 8192 | 13·128 = 1664 | 8192 − 1664 = **6528** | **51/64** | **0.796875** |

Reduction of each fraction, so a reader need not redo it:

- 2720/3488: gcd 32 → **85/109**. (85·32 = 2720; 109·32 = 3488.)
- 3360/4608: gcd 96 → **35/48**. (35·96 = 3360; 48·96 = 4608.)
- 5024/6688: gcd 32 → **157/209**. (157·32 = 5024; 209·32 = 6688.)
- 5413/6960: gcd 1 → **5413/6960** already in lowest terms
  (6960 = 2^4·3·5·29 = 16·3·5·29; **5413 is prime**, so it shares no factor
  with 6960 and the fraction cannot be reduced).
- 6528/8192: gcd 128 → **51/64**. (51·128 = 6528; 64·128 = 8192.)

Decimals are truncated/rounded to 6 places; the exact rational is authoritative.

**Self-check, and one error it caught — recorded, not quietly fixed.** Every
reduction above was re-verified with an independent `math.gcd` and
`fractions.Fraction` computation after this section was first drafted. The
five rates and five gcds were confirmed. The check *did* catch one error, in my
own prose rather than in the transcription: the first draft justified
5413/6960's irreducibility by asserting "5413 = 7·773", which is false
(7·773 = 5411). 5413 is in fact **prime**, so the conclusion — gcd 1, fraction
irreducible, rate 5413/6960 — was correct while the stated reason was not. The
line is corrected above. Recorded here under AGENTS.md rule 8 rather than
silently repaired, because a reviewer is entitled to know which claims in this
document survived a check and which were produced by one. **No transcribed
value from any source was affected.**

**Range of the five rates: 0.729167 … 0.796875.** The lowest is
mceliece460896, the highest mceliece8192128. Note the rates are **not**
monotone in the security category: 348864 (category 1) has rate 0.7798, higher
than 6688128 (category 5) at 0.7512.

Restricted to the sets ISO standardized (see `standardization_status.md`;
348864 is **not** among them), the range is **0.729167 … 0.796875** — the same
endpoints, since both extremes are ISO sets.

> Stated flatly, with no interpretation attached: these are the rates. This
> document does **not** compare them to any attack threshold. That comparison
> belongs to the task that transcribes the attack side (TASK-20260803-292b99)
> and to the Coordinator, not to this transcription.

---

## 3. Claimed security categories

Source: **SEC**, in the discussion following its Table 1. Verbatim:

> *"Since the underlying facts have not changed, the submission continues to
> assign its selected parameter sets to "categories" 1, 3, 5, 5, 5
> respectively. As before, these assignments are based on counting realistic
> costs for memory."*

and immediately after:

> *"If NIST instead decides to make "category" assignments on the basis of bit
> operations with free memory access, then the correct assignments will instead
> be 1, 2, 4, 4, 5. This does not reflect any instability in the Classic
> McEliece security estimates: the submission has always been careful to
> distinguish between these two different types of accounting for the costs of
> attacks."*

**Resolving "respectively".** The sentence gives five numbers without naming
the sets. The referent ordering is fixed by SEC's Table 1 immediately above it,
whose rows run 348864, 460896, 6688128, 6960119, 8192128. That ordering is
independently corroborated by two explicit sentences in the same document:

- *"the submission has always assigned this parameter set to NIST's "Category 5"
  (AES-256)"* — said of **6960119** (4th position → 5 ✓).
- *"One can object to the assignment of 460896 to "Category 3" (AES-192)…"* —
  **460896** named with its category (2nd position → 3 ✓).

Two of the five positions are thus pinned by name, both consistent. The mapping
is not a guess about word order.

| Parameter set | Category **as claimed by the submission** (realistic memory cost) | Category **the same document says would be correct** under free-memory bit-operation accounting |
|---|:---:|:---:|
| mceliece348864(f) | 1 | 1 |
| mceliece460896(f) | 3 | 2 |
| mceliece6688128(f) | 5 | 4 |
| mceliece6960119(f) | 5 | 4 |
| mceliece8192128(f) | 5 | 5 |

Three caveats, all from the source itself, none of them mine:

1. These are the **submission's own assignments**, not a NIST determination.
   SEC presents them as what "the submission … assign[s]".
2. The two columns are the same submission's numbers under two different cost
   models it explicitly distinguishes. Quoting only one column misrepresents
   the source.
3. SEC states the accounting basis is *"counting realistic costs for memory"* —
   which is precisely the charging question GOAL-MCE-001's second completion
   criterion is about. Recorded; **not** adjudicated here.

SEC's Table 1 (Esser–Bellini estimator output, three memory models per set) was
read and is available at `mceliece-security-20221023.pdf` p.10. It is **not**
transcribed into this document: it is attack-cost estimation, outside this
task's transcription scope, and it belongs with the ISD-baseline work rather
than with the parameter table. Its existence and location are noted so the
next task does not have to rediscover it.

---

## 4. Key and ciphertext sizes

Source: **IMPL** Table 1, p.6, captioned *"Sizes of inputs and outputs to the
complete cryptographic functions. All sizes are expressed in bytes."*

This **is** a real PDF table and therefore the extraction-damage risk case. It
was read with both extractors: pypdf renders it row-major, pdfminer.six renders
it column-major, and the two reconstruct to the same 10×4 array. No
`[EXTRACTION-DAMAGED]` marker is set — see §5 for the arithmetic check that
independently confirms it.

| Parameter set | Public key | Private key | Ciphertext | Session key |
|---|---:|---:|---:|---:|
| mceliece348864 | 261120 | 6492 | 96 | 32 |
| mceliece348864f | 261120 | 6492 | 96 | 32 |
| mceliece460896 | 524160 | 13608 | 156 | 32 |
| mceliece460896f | 524160 | 13608 | 156 | 32 |
| mceliece6688128 | 1044992 | 13932 | 208 | 32 |
| mceliece6688128f | 1044992 | 13932 | 208 | 32 |
| mceliece6960119 | 1047319 | 13948 | 194 | 32 |
| mceliece6960119f | 1047319 | 13948 | 194 | 32 |
| mceliece8192128 | 1357824 | 14120 | 208 | 32 |
| mceliece8192128f | 1357824 | 14120 | 208 | 32 |

All values in **bytes**, per the table's own caption.

IMPL adds, verbatim: *"It is possible to compress the private key down to 40
bytes (or 32 bytes for non-f parameter sets) with uncompression less expensive
than key generation."* So the private-key column is the uncompressed
representation.

---

## 5. Cross-check: the two transcriptions verify each other

This is the strongest integrity control available here and it costs nothing, so
it was run. SPEC §6.2 gives the size formulas verbatim:

> *"The public key T, which is an mt × k matrix, is represented in a row-major
> fashion. Each row of T is represented as a ⌈k/8⌉-byte string, and the public
> key is represented as the mt⌈k/8⌉-byte concatenation of these strings."*

> *"The ciphertext is represented as the next ⌈mt/8⌉ bytes."*

Feeding the §7 triples through those formulas must reproduce IMPL Table 1 — two
independently-extracted documents, one arithmetic bridge. Result:

| Set | mt·⌈k/8⌉ computed | IMPL pk | ⌈mt/8⌉ computed | IMPL ct | |
|---|---:|---:|---:|---:|:--:|
| mceliece348864 | 768·340 = 261120 | 261120 | 96 | 96 | MATCH |
| mceliece460896 | 1248·420 = 524160 | 524160 | 156 | 156 | MATCH |
| mceliece6688128 | 1664·628 = 1044992 | 1044992 | 208 | 208 | MATCH |
| mceliece6960119 | 1547·677 = 1047319 | 1047319 | 194 | 194 | MATCH |
| mceliece8192128 | 1664·816 = 1357824 | 1357824 | 208 | 208 | MATCH |

**10/10 match** (5 sizes × pk and ct). Note 6960119 is the discriminating case:
it is the only set where both ceilings bite (k = 5413, ⌈5413/8⌉ = 677 not
676.625; mt = 1547, ⌈1547/8⌉ = 194 not 193.375), and it still matches exactly.
A transcription error in m, n, t, or in the size table would have to be a
conspiracy of two compensating errors to survive this.

Reproduce with: `python3` on the script recorded in the run notes —
`k = n - m*t; pk = m*t*ceil(k/8); ct = ceil(m*t/8)`.

---

## 6. The `pc` parameter sets

The ISO list (see `standardization_status.md`) names `pc` and `pcf` sets that do
**not** appear in SPEC §7. They are defined by **PC**, a one-page delta document
whose opening states verbatim:

> *"For continuity, this document defines exactly the same KEM as the round-3
> Classic McEliece submission. This definition is presented as a list of changes
> to the separate 'cryptosystem specification' document."*

PC changes Encap/Decap to add a plaintext-confirmation hash `C1 = H(2,e)` and
redefines the ciphertext encoding:

> *"A ciphertext C has two components: C0 ∈ F2^mt and C1 ∈ F2^ℓ. The ciphertext
> is represented as the concatenation of the ⌈mt/8⌉-byte string representing C0
> and the ⌈ℓ/8⌉-byte string representing C1."*

with ℓ = 256 (SPEC §6.1, verbatim: *"The integer ℓ is 256."*).

Consequences, stated precisely:

- **PC introduces no new (m, n, t).** It is a delta on the same parameter
  space. So `mceliece460896pc` has m = 13, n = 4608, t = 96, and **the same rate
  35/48** as `mceliece460896`. **The rate table in §2 covers the pc variants
  unchanged.** This is the load-bearing point for GOAL-MCE-001.
- **Public keys are unchanged** — PC does not touch key representation.
- **Ciphertexts grow by exactly ⌈256/8⌉ = 32 bytes.**

| pc set | ciphertext, bytes | provenance |
|---|---:|---|
| mceliece348864pc(f) | 96 + 32 = 128 | **computed** from PC + SPEC §6.1 |
| mceliece460896pc(f) | 156 + 32 = 188 | **computed** from PC + SPEC §6.1 |
| mceliece6688128pc(f) | 208 + 32 = 240 | **computed** from PC + SPEC §6.1 |
| mceliece6960119pc(f) | 194 + 32 = 226 | **computed** from PC + SPEC §6.1 |
| mceliece8192128pc(f) | 208 + 32 = 240 | **computed** from PC + SPEC §6.1 |

> These five ciphertext sizes are **computed from the sources' formulas, not
> transcribed from any table**, and are marked as such. I found no numeric size
> table for the pc variants in any document fetched. A reviewer wanting a
> transcribed pc size table should treat it as **not obtained**.

---

## 7. What was NOT obtained

| Item | Status |
|---|---|
| pc-variant private-key sizes | **not obtained** — no table found in the fetched documents; PC does not state them and IMPL Table 1 covers only the ten non-pc sets |
| A numeric pc size table of any kind | **not obtained** — see §6 |
| Per-set category assignment for `f` / `pc` variants as *distinct* entries | **not obtained as such.** SEC assigns five categories to five *sizes*. The f and pc variants share (m, n, t) with their base set, but SEC does not enumerate them separately, and I do not extend its claim on their behalf. |
| ISO's own text for any parameter or category | **not obtained** — iso.org returned 403 twice; see `standardization_status.md` |
| Category assignment by NIST (as opposed to by the submission) | **not obtained**, and per NIST IR 8545 there is no NIST standard for this algorithm to carry one |

---

## 8. Marker summary

- `[RECALLED-NOT-READ]` markers set: **0**. No number in this document came
  from recall. Every figure traces to a fetched document with a recorded
  sha256, or is arithmetic on such figures with the arithmetic shown.
- `[EXTRACTION-DAMAGED]` markers set: **0**. The only real table (IMPL Table 1)
  survived dual-extractor agreement *and* the §5 arithmetic reconstruction;
  SPEC §7 is prose and agreed character-for-character across extractors.
- Values labelled **computed** rather than transcribed: the `k` column, the
  whole of §2, the §5 check column, and the pc ciphertext sizes in §6. Each is
  computed from a formula quoted verbatim from the source.
