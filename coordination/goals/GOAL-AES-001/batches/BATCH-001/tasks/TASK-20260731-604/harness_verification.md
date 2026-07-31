# CHECK (a) — Harness integrity verification

Task: TASK-20260731-604 (validator, independent session, review-adversarial)
Reviewed: TASK-20260731-602 artifacts as committed in snapshot `0185c0ff`
Verdict: **passed**, with four recorded defects (all latent or declared; none
contaminates the committed result)

Nothing in this file is a statement about AES. It is a statement about an
instrument. No official state is changed and no evidence strength is assigned.

---

## 0. Snapshot verification (gate: must pass before any finding is recorded)

```
$ git log -1 --format='%H parent=%P' 0185c0ff
0185c0ff2d3878101d8f6cf5bdef48906ffb197b parent=0137a051eb5828789eb267fa83c8278086578d4c
$ git merge-base --is-ancestor 0185c0ff HEAD  ->  REACHABLE
$ git diff-tree --no-commit-id --name-status -r 0185c0ff
A  .../TASK-20260731-603/snapshot-receipt.json
A  .../TASK-20260731-601/baseline_map.md
A  .../TASK-20260731-601/candidate_report.yaml
A  .../TASK-20260731-602/aes_reduced.py
A  .../TASK-20260731-602/run_record.md
A  .../TASK-20260731-602/vector_check_receipt.json
```

Recomputed SHA-256 of each blob **as read out of the commit** (`git show 0185c0ff:<path> | sha256sum`):

| path | recomputed | matches `source_path_sha256` |
|---|---|---|
| `TASK-20260731-601/baseline_map.md` | `ba3419c6…8ecf6` | yes |
| `TASK-20260731-601/candidate_report.yaml` | `eeb15ffa…2eaea` | yes |
| `TASK-20260731-602/aes_reduced.py` | `2c76f3e5…babb447` | yes |
| `TASK-20260731-602/vector_check_receipt.json` | `48e355d7…3b453` | yes |
| `TASK-20260731-602/run_record.md` | `709db346…d74de` | yes |

Commit changes exactly the six declared paths and nothing else; the message
names TASK-20260731-601, -602, -603 and GOAL-AES-001; `record_ids` is empty as
required for a snapshot; the amendment rode in its own isolated commit
`0137a051`, which is the snapshot's parent, exactly as `declared_scope_extension.resolution`
states. `git status --porcelain coordination/goals/GOAL-AES-001` is empty.

The module hash in the receipt (`2c76f3e5db83ec2500ce1010a392a135869d8b9dd1a534af817e06f15babb447`)
equals the committed blob's hash and equals `MODULE_SHA256` computed by the
module at load time from the file I extracted. **No drift between receipt and
committed code.**

Additionally, the driver source embedded verbatim in `run_record.md` (the single
fenced `python` block, 38877 bytes) hashes to
`675ff4d568c03f6b12aa5d8931c6185ec7c5b08344ef826616fd9580d4c84a6d`, which is
exactly the `artifact_hashes.check_driver_sha256` recorded in the receipt. The
driver is therefore recoverable and verifiable, not merely asserted. I extracted
it and executed it (§4, §5).

**Verdict: snapshot verified. Proceeding.**

---

## 1. Independent randomized differential test (my seed, my driver)

I did not use the executor's driver or seeds for this check. Validator seed
`60420260731777`, `random.Random`, fresh key/plaintext draws.

```
$ python3 val_diff.py
validator seed: 60420260731777
module sha256 as loaded: 2c76f3e5db83ec2500ce1010a392a135869d8b9dd1a534af817e06f15babb447
[1] pycryptodome enc+dec comparisons: 9000, mismatches: 0
[2] openssl CLI enc+dec block comparisons: 1440, mismatches: 0
```

- 1500 fresh (key, plaintext) pairs per key size at 128/192/256, each checked in
  **both** directions: `aes_reduced.encrypt_block` vs `pycryptodome`, and
  `aes_reduced.decrypt_block` vs `pycryptodome.decrypt` with round-trip to the
  original plaintext. 9000 comparisons, 0 mismatches.
- 12 fresh keys per key size, 20 blocks each, through the **openssl CLI**
  (`openssl enc -aes-N-ecb -K <hex> -nopad -e` and `-d`), 1440 block
  comparisons, 0 mismatches, all exit status 0.

Tool versions I resolved myself: Python 3.11.15, pycryptodome 3.23.0,
OpenSSL 3.0.13 30 Jan 2024 — identical to the versions recorded in the receipt.

### Per-vector known-answer reproduction

| key size | direction | `aes_reduced` | pycryptodome | openssl CLI | three-way |
|---|---|---|---|---|---|
| 128 | enc | `69c4e0d86a7b0430d8cdb78070b4c55a` | same | same | **AGREE** |
| 192 | enc | `dda97ca4864cdfe06eaf70a0ec0d7191` | same | same | **AGREE** |
| 256 | enc | `8ea2b7ca516745bfeafc49904b496089` | same | same | **AGREE** |
| 128/192/256 | dec | round-trips to plaintext on all 4500 cases | same | same | **AGREE** |

These three ciphertexts also match the FIPS-197 Appendix C values as *I* recall
them. **That agreement is `unverified_from_memory` on my side too** — csrc.nist.gov
is unreachable from this session, I read no specification document, and my recall
carries exactly the same status as the executor's. It is recorded as
corroboration between two independent recollections, which is weaker than a read
source and must not be represented as one. The load-bearing fact is the
three-way *implementation* agreement, not the recalled constant.

**Vectors not reproduced: none. Vectors not checked: the NIST CAVP/AESAVS
response files** (not present locally, csrc.nist.gov unreachable) — correctly
listed in the receipt's `checks_not_run`, and I confirm I could not run them
either.

---

## 2. Backend independence — explicit verdict: **PASS (verified by construction, not by assertion)**

The receipt asserts that `aes_reduced.py` never calls a reference
implementation. I tested this rather than reading it. I installed an import
guard that raises on `Crypto`, `Cryptodome`, `cryptography`, `subprocess`, `ctypes`
and `ssl`, and only then imported and ran the module:

```
$ python3 val_indep.py
with Crypto/subprocess/ctypes imports BLOCKED, AES-128 ct = 69c4e0d86a7b0430d8cdb78070b4c55a
stdlib-only modules actually imported by aes_reduced: ['dataclasses', 'hashlib', 'random', 'typing']
```

It produces the correct AES ciphertext with every reference backend and every
subprocess escape hatch unavailable. An AST scan of the committed file lists all
imports as `__future__, dataclasses, hashlib, json, random, sys, typing`
(`json`/`sys` only inside the `__main__` demo). The only occurrence of the string
"openssl" in the file is in a docstring.

The two references are also independent **of each other**: pycryptodome is an
in-process C/Python library, openssl is a separate process invoked via the CLI
with its own EVP implementation. Two checks against the same backend would not
count; these are not the same backend.

---

## 3. Reduced-round convention — explicit verdict: **documented, and internally consistent with the code**

I did not verify this by reading the prose. I **wrote my own reduced-round AES
from the prose** (C1/C2/C3 as stated in the module docstring and `run_record.md`
§4), deliberately structured differently: S-box built via a log/antilog table
rather than by `GF.inv` exponentiation, MixColumns written out per-row with
`xtime` rather than as a matrix product, Rcon as a literal list rather than a
computed power. I anchored my implementation as genuine AES at `r = Nr` against
both backends, then compared it to the committed code across the whole reduced
range.

```
anchor 128-bit r=Nr: validator impl == pycryptodome == openssl : True
anchor 192-bit r=Nr: validator impl == pycryptodome == openssl : True
anchor 256-bit r=Nr: validator impl == pycryptodome == openssl : True
--- reduced-round agreement: validator prose-derived impl vs committed aes_reduced.py ---
reduced-round cases agreeing: 468, disagreeing: 0
```

468 cases = 3 key sizes × (r = 0…Nr) × {`final_mix_columns` False, True} × 6
random (key, plaintext) draws. **Zero disagreements.** An independently written
implementation of the *documented* convention computes exactly what the
committed code computes, at every reduced round count, under both variants.

Direct checks of each numbered convention against the code:

| claim | check | result |
|---|---|---|
| C1 | `rounds=Nr, final_mix_columns=False` is FIPS-197 | `is_fips197 == True`, matches both backends, all 3 key sizes |
| C1 | the alternative variant is *not* AES | `final_mix_columns=True` gives a different ciphertext and `is_fips197 == False` |
| C1 | final round really drops MixColumns | `trace()` emits no `r{Nr}.mix` label but does emit `r{Nr-1}.mix` |
| C2 | initial AddRoundKey is whitening, not a round | `AES(k, rounds=0).encrypt_block(p) == p XOR RK[0]` exactly, all 3 key sizes |
| C3 | untruncated schedule indexed 0..r | `AES(k, rounds=r).round_keys == AES(k).round_keys[:r+1]` for every `r` in 0..Nr, all 3 key sizes |
| C3 | no renumbering when extending past Nr | `AES(k, rounds=Nr+2).round_keys[:Nr+1] == full schedule`; `is_fips197 == False` |
| — | decryption inverts at every reduced round count | true for every `r` in 0..Nr, all 3 key sizes |
| — | partial-evaluation levels chain correctly | `encrypt_partial(0→2)` then `(2→5)` equals `encrypt_block` at `rounds=5` |

**Verdict: the convention is documented explicitly, and what the code computes
matches the documentation, verified against an independently authored
implementation of that documentation.**

### Is the reduced-round path constrained, or is the checking circular?

The task asked me to say plainly which. My answer is: **partly circular, but not
wholly, and the two parts must not be conflated.**

Decompose the reduced-round cipher into (i) its *components* — S-box, ShiftRows
offsets, MixColumns matrix, key schedule — and (ii) its *round-structure
convention* — C1/C2/C3.

- **Components are externally pinned, and this genuinely constrains the reduced-round
  path.** The reduced cipher uses byte-identical components to the full cipher
  (I verified `round_keys` prefixing and shared `Components` directly). Any error
  in a component would show up at `r = Nr`, where three independent
  implementations agree over 10440 of my own comparisons. This is not circular.
- **The round-structure convention is not externally referenced at all, and cannot
  be.** No available tool implements `r < Nr` AES. The receipt's own
  `reduced_round_convention` flat-checks are, in part, the implementation checked
  against itself — `C2_rounds0_is_pure_whitening` and
  `C4_distinct_ciphertext_per_round_count` are definitional/near-tautological
  and constrain nothing beyond internal coherence. My 468-case comparison
  removes the *prose-versus-code* circularity (a second author's implementation
  of the same written spec agrees), but it cannot remove the fact that the
  convention itself is a **choice**, not a verified fact.

The correct characterisation is therefore: at `r < Nr` this is not a *correctness*
question that could be right or wrong against a reference — it is a *definitional*
question. What remains genuinely unverified is whether the adopted convention is
the one the literature uses. The module says so, in the right words, and marks
its recollection `UNVERIFIED-FROM-MEMORY`. My own recollection agrees with the
module's and is **equally unverified** — I read no source. Two agreeing
recollections are not a citation.

This matters concretely and only at one point: any future comparison of a
reduced-round measurement against a recalled literature number silently assumes
the two use the same convention. The producer states this obligation
explicitly. It is the correct statement of the limitation, and the
snapshot's `producer_stated_principal_limitation` and the coordinator note both
render it accurately. **The instrument is externally verified precisely where the
research is not happening — that framing in the commit message is accurate and I
confirm it.**

---

## 4. The mutation control and its claimed false-green fix — the highest-value check

### 4.1 The reported control reproduces exactly

I extracted the archived driver (hash-verified, §0), pointed `MODULE_DIR` at the
committed module, and re-ran `check_detection_power` myself:

| mutant | status | KAT flagged | random pairs flagged | detected |
|---|---|---|---|---|
| `sbox_transpose_0x53_0x54` | applied | 2 / 4 | 152 / 200 | true |
| `shiftrows_offsets_swapped` | applied | 4 / 4 | 200 / 200 | true |
| `rcon_off_by_one` | applied | 4 / 4 | 200 / 200 | true |

verdict: `pass`. These are the exact numbers in `run_record.md` §4.3, including
the 2/4 and 152/200 figures. **All three mutants take the `applied` code path**
— i.e. each was detected by a real comparison against pycryptodome and against
the recalled vectors, not by any import-time exception. The committed green
result is therefore not contaminated by the historical bug.

### 4.2 The fix is genuine for the failure mode it was introduced to address

I reconstructed the original false-green shape: a module that raises a
*non-*`AssertionError` at import (`AttributeError: 'NoneType' object has no
attribute '__dict__'`, the exact exception the executor reports).

```
--- B. import raises AttributeError (the original false-green shape): verdict=FAIL
     sbox_transpose_0x53_0x54   | status: driver_import_error | detected: False
     shiftrows_offsets_swapped  | status: driver_import_error | detected: False
     rcon_off_by_one            | status: driver_import_error | detected: False
```

The control returns `FAIL`, not `pass`, and each row is `detected: False`. **The
fix is real.** Registering the module in `sys.modules` before `exec_module` and
routing non-assertion exceptions to `driver_import_error` with `detected: false`
both behave as documented.

### 4.3 DEFECT H-1 — a residual, narrower false-green path remains

The task asked whether the current scoring *cannot* credit an import error as a
detection. Precisely: it mostly cannot, but there is one remaining exception
class where it still can.

`except AssertionError` is scored `rejected_by_module_self_check`,
`detected: True`. I injected an import-time `AssertionError` **unrelated to the
mutation**:

```
--- C. import raises AssertionError unrelated to the fault: verdict=pass
     sbox_transpose_0x53_0x54   | status: rejected_by_module_self_check | detected: True
     shiftrows_offsets_swapped  | status: rejected_by_module_self_check | detected: True
     rcon_off_by_one            | status: rejected_by_module_self_check | detected: True
```

The control returns `pass` on three mutants none of which was compared against
anything. The failure class has been narrowed from *all* import exceptions to
*`AssertionError` only*, but not eliminated. The driver does not check that the
`AssertionError` originated in the module's own consistency check, nor that it is
related to the injected fault.

Severity: **latent, not realized.** This path is not exercised by the committed
run (§4.1 — all three mutants imported cleanly). The design intent is defensible:
`aes_reduced.py` contains exactly one import-time assertion
(`assert mat_mul(AES_MIX, AES_INV_MIX) == IDENTITY_MIX`), which a MixColumns
mutant would legitimately trip. But the rule as written is broader than the
intent. Recommended repair (for the Coordinator to schedule, not for me to make):
require the assertion text to match the module's own self-check, or drop the
self-check detection path entirely and require every mutant to be caught by a
comparison.

### 4.4 DEFECT H-2 — the self-check detection path silently vanishes under `python3 -O`

```
under -O:      inconsistent MixColumns matrices imported WITHOUT AssertionError (self-check stripped)
without -O:    AssertionError raised -> AES MixColumns matrices inconsistent
```

`assert` statements are removed under `-O`, so a module with provably
inconsistent MixColumns/inverse-MixColumns matrices imports cleanly. Impact is
limited — such a mutant would still be caught by the differential comparison —
but a check whose behaviour depends on an interpreter flag is not a check. Minor.

### 4.5 Control-of-the-control: the mutation control is not trivially always-green

A control that reports "detected" for everything proves nothing. I built a
**semantics-preserving no-op mutant** (rewrote the S-box construction as a list
comprehension plus `tuple()`, changing the source text but not the cipher):

```
--- D. no-op mutant (semantics unchanged): random pairs flagged = 0/200
       -> would be scored detected=False   (correct answer: False)
```

Correct. The control discriminates rather than always firing.

### 4.6 DEFECT H-3 — the mutation control has zero coverage of the reduced-round path

All three mutants are scored by comparison **at full rounds** against
pycryptodome. No mutant perturbs the round-structure logic — e.g. flipping
`_is_final_round`, off-by-one in the `encrypt_partial` level range, or a
round-key index shift at `r < Nr`. Some such mutants would be invisible at
`r = Nr` by construction and are exactly the bugs that would silently corrupt
every later cryptanalytic measurement. The receipt's detection-power claim is
therefore scoped to the full-round path only, and should be read that way. This
is a coverage gap, not an error: nothing false is asserted.

---

## 5. Determinism and receipt-versus-code agreement — explicit verdicts

I ran the archived driver twice, from scratch, in a clean directory:

```
committed results_digest : f78e55e4b7d6df30f41ce4aa613f8621ca9ecdd21f9ab9f3027b87c96dacaf1a
my run1 results_digest   : f78e55e4b7d6df30f41ce4aa613f8621ca9ecdd21f9ab9f3027b87c96dacaf1a  True
my run2 results_digest   : f78e55e4b7d6df30f41ce4aa613f8621ca9ecdd21f9ab9f3027b87c96dacaf1a  True
run1 == run2             : True
```

**Determinism verdict: PASS.** The digest over every ciphertext/plaintext
produced, in execution order, reproduces bit-for-bit in a different session, in
a different directory, on a different day, from the committed seeds
(`20260731602`, `…001`–`…005`). Seeds are recorded, are the only randomness
source, and are honoured.

**Receipt-versus-code verdict: PASS, byte-identical.** I diffed my recomputed
receipt against the committed one field by field, excluding only genuinely
volatile fields (timestamps, wall clock, git state, environment, tool versions,
command list, artifact paths, prior-run digest). The structural diff reported
exactly one difference:

```
only in committed: /verdicts/determinism_rerun_digest_matches
```

which is present only because that verdict is emitted when a prior digest is
supplied for comparison. Every other value — all nine section verdicts, the
per-vector outputs, the 3072 openssl and 12000 pycryptodome comparison counts,
the null-object control ciphertexts and component fingerprints, the mutation
table, the reduced-round per-round-count ciphertext fingerprints — recomputed
identically. **The receipt describes what the code actually computes. There is no
drift and no unreproduced entry.**

### Null-object controls in the receipt

Present and substantive: random S-box (data path only, and with key schedule),
two distinct seeds, random MixColumns, identity variants. Each records
`differs_from_aes`, `invertible`, `is_fips197_flag_false`, a component SHA-256
fingerprint, and its seeded provenance. I confirmed the seeds and the resulting
ciphertexts recompute. These are genuine null objects of the same shape, and the
module's `.provenance` chain makes a control run reconstructible from the
receipt.

### Checks correctly recorded as not run

Five, all accurate and all verified by me as genuinely unavailable here: NIST
CAVP/AESAVS files, the FIPS-197 document text, an AES-NI C cross-check (declared
out of deliverable scope), **a reduced-round cross-check against an external
reference** (impossible — no such tool exists), and non-ECB modes. Nothing is
reported as passing that was not executed. `checks_not_run` is honest and
complete as far as I can determine.

---

## 6. Verdict

**CHECK (a): passed.**

Every claim in `vector_check_receipt.json` that I could re-execute, I
re-executed, and it reproduced. Full-round AES is pinned by three independent
implementations under my own seeds; backend independence is verified by
construction rather than by assertion; the reduced-round convention is documented
and matches the code, verified against an independently authored implementation
of the documentation; determinism reproduces exactly; the receipt is byte-faithful
to what the code computes; and the executor's self-reported false-green fix is
genuine for the failure mode it addresses.

Defects recorded (none contaminates the committed result):

- **H-1** (medium, latent): the mutation control still credits *any* import-time
  `AssertionError` as a detection. Narrowed from the original bug, not
  eliminated. Not exercised by the committed run.
- **H-2** (low): the self-check detection path is stripped under `python3 -O`.
- **H-3** (medium, coverage): no mutant probes reduced-round round-structure
  logic, so the measured detection power does not extend to the path this
  campaign will actually use.
- **H-4** (declared, not a producer fault): the reduced-round path has no
  external reference and cannot obtain one. The producer states this as its
  principal limitation and is correct to. My independent reimplementation
  strengthens the prose-to-code binding but cannot supply an external reference.

This verdict says the instrument is admissible as a reproducibility floor. It
says nothing about AES, supports no cryptanalytic claim, and carries no
implication for CHECK (b), which is reported separately and reached a different
conclusion.
