# Run record — TASK-20260731-602

**Build the FIPS-197-pinned reduced-round-capable AES ground-truth harness**

| field | value |
|---|---|
| task | TASK-20260731-602 |
| role | executor |
| goal / question / batch | GOAL-AES-001 / RQ-AES-001 / BATCH-001 |
| handoff | `ledger/handoffs/TASK-20260731-602.yaml` |
| git commit at execution | `1e1c77829de76c3f5aaad393c69281577976f0f6` |
| dirty tree at execution | **yes** — only `coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/` (this task's own untracked output directory). No tracked file was modified. |
| executed (UTC) | 2026-07-31T17:19:17Z → 2026-07-31T17:19:33Z (final receipt run) |
| overall verdict | **pass** — 9/9 receipt verdicts pass, 0 fail, 0 partially run |
| certificate kind | `none` (pure instrument-verification run; nothing is claimed solved — `docs/claims-and-verification.md`) |

## 0. Scope and non-claims

This task built an instrument and verified it. Per the handoff constraints and
AGENTS.md rule 1, this record contains **no cryptanalytic claim, no mechanism,
no evidence-strength assignment, and no state change**. Nothing here says
anything about the security of AES at any round count. The only assertion made
is the narrow one in the receipt's `claim_scope`: `aes_reduced.py` agrees with
pycryptodome 3.23.0 and the openssl CLI on the inputs actually listed.

## 1. Artifacts

| path | sha256 |
|---|---|
| `coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602/aes_reduced.py` | `2c76f3e5db83ec2500ce1010a392a135869d8b9dd1a534af817e06f15babb447` |
| `coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602/vector_check_receipt.json` | `48e355d77cc1b0bdcd134c4dfe1ed2c7acfc40ebc8a6c00472c8914fdbd3b453` |
| `coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602/run_record.md` | this file |
| verification driver `check_vectors.py` (source reproduced verbatim in §9) | `675ff4d568c03f6b12aa5d8931c6185ec7c5b08344ef826616fd9580d4c84a6d` |

**Why the driver is not a fourth file.** The dispatch queue declares exactly
three `artifact_paths` for this task and the write scope is the task directory.
Rather than expand the declared artifact set, the driver was executed from the
session scratchpad against the archived `aes_reduced.py` (located via
`AES_REDUCED_DIR`) and its **complete source is reproduced verbatim in §9**,
with its sha256 recorded in the receipt. A reviewer reproduces the run by
extracting §9 to `check_vectors.py` and running the commands in §5. This is a
protocol deviation from the obvious layout and is recorded here as one.

## 2. Environment

| component | resolved value | how obtained |
|---|---|---|
| platform | `Linux-6.18.5-x86_64-with-glibc2.39`, x86_64 | `platform.platform()` inside the driver |
| CPU / RAM / GPU | 4 cores, 15 GB RAM, no GPU (`nproc`, `free -g`) | declared envelope, confirmed |
| python3 | `3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]` | `python3 -c 'import sys; print(sys.version)'` |
| pycryptodome | `3.23.0` | `python3 -c 'import Crypto; print(Crypto.__version__)'` |
| openssl | `OpenSSL 3.0.13 30 Jan 2024 (Library: OpenSSL 3.0.13 30 Jan 2024)`, platform `debian-amd64` | `openssl version -a` |
| gcc | `gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` | `gcc --version` |
| sage | absent | not invoked |

Every version string above is the tool's own report, captured by the driver and
stored in `vector_check_receipt.json → tool_versions` together with the exact
command and exit status. None was transcribed by hand.

**gcc / AES-NI was NOT used.** `gcc 13.3.0` with `-maes` is available per the
goal record, but no C code is part of this deliverable. The version is recorded
for the environment record only, with `used_in_this_task: false` in the receipt.
No AES-NI cross-check was run; see §7.

## 3. THE REDUCED-ROUND CONVENTION (the load-bearing decision)

FIPS-197 defines AES only at Nr = 10 / 12 / 14 rounds for 128 / 192 / 256-bit
keys. **It does not define what "r-round AES" means for r < Nr.** The
convention below is therefore a *choice*, and it is the single most likely way
this campaign could produce a false positive: a reduced-round result obtained
under a silently non-standard convention is an artifact about a different
cipher, not a fact about AES. It is stated here, in the module docstring of
`aes_reduced.py`, and in `vector_check_receipt.json →
reduced_round_convention`, and it is machine-checked (§4, `reduced_round_convention`).

### Adopted convention — `AES(key, rounds=r)`, default `final_mix_columns=False`

```text
s  = P
s ^= RK[0]                                   # initial AddRoundKey
for i in 1 .. r-1:                           # full rounds
    s = SubBytes(s); s = ShiftRows(s); s = MixColumns(s); s ^= RK[i]
s = SubBytes(s)                              # round r == the final round
s = ShiftRows(s)
# MixColumns OMITTED in round r
s ^= RK[r]
return s
```

**(C1) The final round drops MixColumns.** Round `r` — whatever `r` is — is the
final round and omits MixColumns, mirroring FIPS-197's round Nr. At `r = Nr`
this reproduces FIPS-197 AES bit-for-bit (verified against two independent
references, §4). *Rationale*: it is the only choice under which the reduced
cipher is a truncation of the real cipher rather than a different one, so the
r = Nr case is a genuine regression test of the reduced-round code path itself.
The alternative is available as `final_mix_columns=True`, and `is_fips197`
returns `False` for it even at r = Nr, so it cannot be mistaken for AES.

**(C2) The initial AddRoundKey is NOT counted as a round.** It is key
whitening. `rounds=4` therefore means four S-box layers, with RK[0] applied
before the first. `rounds=0` is legal and denotes whitening only. *Rationale*:
this makes "round count" synonymous with "number of nonlinear layers", which is
the quantity every AES attack is parameterised by.

**(C3) Round keys are the untruncated FIPS-197 schedule, indexed 0..r.** The
key schedule is a function of the key length (Nk), not of the reduced round
count: the r-round cipher uses the first r+1 round keys of the *standard*
expansion. The schedule is not re-derived, re-seeded, or shortened, and Rcon
indices are not renumbered — RK[i] of the reduced cipher is byte-for-byte RK[i]
of the full cipher. *Rationale*: any other choice would make the reduced cipher's
key schedule a second, undocumented design decision, and key-schedule
relations are one of the objects RQ-AES-001 explicitly puts in scope. This is
machine-checked for all key sizes and all r (`C3_reduced_roundkeys_are_prefix_of_full_schedule`).

### What the literature does — UNVERIFIED-FROM-MEMORY

> **Recollection, not a citation.** No primary source is reachable from this
> environment (csrc.nist.gov, eprint.iacr.org and arxiv.org are blocked under
> this harness's network policy; see RQ-AES-001 `provenance`). The following is
> recalled from memory and has **not** been checked against any read document.

The recollection is that reduced-round AES cryptanalysis conventionally means
exactly (C1)+(C2)+(C3) — r rounds, last round without MixColumns, whitening key
applied and not counted — and that papers keeping MixColumns in the last round
normally say so explicitly, because omitting it is a linear change that most
attacks absorb into the final key guess. **Mark this `unverified_from_memory`
wherever it is relied on.** Concretely, any downstream comparison against a
recalled literature number must state, in the same sentence, both that the
baseline is unverified-from-memory *and* which of the two conventions the
comparison assumes. If a later result turns out to depend on the choice, that
dependence is itself a finding to report, not a detail to smooth over. Both
variants are one constructor flag apart precisely so the sensitivity can be
measured rather than argued.

## 4. What was checked, and the result of each check

All nine verdicts below are copied from `vector_check_receipt.json → verdicts`.
Every one was executed; none is asserted without its output in the receipt.

| # | check | verdict | what it actually did |
|---|---|---|---|
| 1 | `component_derivations` | **pass** | S-box is a bijection on 256 values; `inv_sbox[sbox[x]] == x` for all x; `AES_MIX × AES_INV_MIX = I` over GF(2^8); `x · x^{-1} = 1` for all 255 nonzero x; `inv(0) = 0`. S-box sha256 `c2d8e5ee…08b4f2`. |
| 2 | `known_answer_vectors` | **pass** | 4 vectors × 7 comparisons = 28 comparisons, all true. Both directions. See §4.1. |
| 3 | `multiblock_consistency` | **pass** | 8-block ECB vs pycryptodome and vs openssl. |
| 4 | `randomized_vs_pycryptodome` | **pass** | **6000 random (key, input) pairs** (2000 each for 128/192/256), each compared in **both** directions ⇒ **12 000 block comparisons**, 12 000 agreements, **0 mismatches**. |
| 5 | `randomized_vs_openssl` | **pass** | 16 random keys × 32 blocks × 3 key sizes × 2 directions ⇒ **96 openssl invocations, 3072 blocks** compared, all agreeing, 0 mismatches, 0 openssl errors. |
| 6 | `reduced_round_convention` | **pass** | 36 boolean checks (12 per key size) pinning C1/C2/C3 and the partial-evaluation API. See §4.2. |
| 7 | `null_object_controls` | **pass** | 7 component-replaced ciphers; each invertible, each differing from AES, each flagged `is_fips197 == False`; seed reproducibility and seed sensitivity confirmed for both random S-box and random MixColumns. |
| 8 | `detection_power_mutation_control` | **pass** | 3 fault-injected mutants of `aes_reduced.py`, all detected. See §4.3. |
| 9 | `determinism_rerun_digest_matches` | **pass** | Independent re-run reproduced digest `f78e55e4…acaf1a` exactly. See §6. |

### 4.1 Known-answer vectors

> **Honesty note on the "expected" column.** No primary source is reachable, so
> the expected ciphertexts below are **recalled from memory** and are tagged
> `recall_status: recalled_from_memory_unverified` in the receipt. **They are
> not the authority for this task.** The authority is three-way agreement
> between `aes_reduced.py`, pycryptodome and openssl, which does not depend on
> anyone's recall being right. The recalled value is reported as a *fourth,
> weaker* comparison. Had it disagreed while the three implementations agreed,
> that would have been recorded as a memory error in this record, not as an
> implementation failure.

| vector (recalled attribution) | key bits | expected (recalled) | aes_reduced | pycryptodome | openssl | verdict |
|---|---|---|---|---|---|---|
| FIPS-197 App. B | 128 | `3925841d02dc09fbdc118597196a0b32` | same | same | same | pass |
| FIPS-197 App. C.1 | 128 | `69c4e0d86a7b0430d8cdb78070b4c55a` | same | same | same | pass |
| FIPS-197 App. C.2 | 192 | `dda97ca4864cdfe06eaf70a0ec0d7191` | same | same | same | pass |
| FIPS-197 App. C.3 | 256 | `8ea2b7ca516745bfeafc49904b496089` | same | same | same | pass |

Per vector the receipt stores all seven comparisons individually:
`encrypt.aes_reduced_vs_pycryptodome`, `encrypt.aes_reduced_vs_openssl`,
`encrypt.pycryptodome_vs_openssl`, `encrypt.aes_reduced_vs_recalled_expected`,
`decrypt.aes_reduced_vs_pycryptodome`, `decrypt.aes_reduced_vs_openssl`,
`decrypt.roundtrip_recovers_plaintext`. All 28 are `true`. openssl exit status
was 0 on all 8 invocations (4 encrypt + 4 decrypt), stderr empty.

All four recalled values in fact matched the two independent implementations.
That agreement retroactively corroborates the recollection; it does **not**
promote it to a citation, and it is not recorded as one.

### 4.2 Convention checks (12 per key size, all pass)

`C1` full-round default == FIPS-197 reference · `C1b` the `final_mix_columns=True`
variant differs from AES · `C1c` `rounds=None` == full rounds · `C2` `rounds=0`
is exactly `P ⊕ RK[0]` · `C3` reduced round keys are a prefix of the full
schedule for every r · `C4` all Nr+1 round counts give distinct ciphertexts ·
`C5` invertible at every round count under **both** conventions · `C6` partial
encryption composes: for every split j, `E_{j→Nr}(E_{0→j}(x))` equals the full
ciphertext, and `D_{j→0}` inverts it · `C7` trace labels match the partial
level indexing · `C8` the final round carries no `.mix` state by default while
round Nr−1 does · `C9` `final_mix_columns=True` restores it · `C10` the
`is_fips197` flag is true only for the exact FIPS-197 configuration.

The receipt also stores, per key size, the full ciphertext-by-round-count list
for a fixed seeded (key, plaintext) — a byte-level fingerprint of the adopted
convention that a validator can recompute independently.

### 4.3 Detection-power control (a null object for the instrument itself)

`docs/inventor-protocol.md` requires the identical measurement against a null
object before a signal is believed. Applied to this task, the "signal" is a
green receipt, so the control asks: **would this harness turn red on a
knowingly wrong AES?** Three single-fault mutants were generated from the
archived source, imported as separate modules, and pushed through the same
comparisons:

| mutant | KAT vectors flagged | random pairs flagged (of 200) | detected |
|---|---|---|---|
| `sbox_transpose_0x53_0x54` (two S-box entries swapped) | 2 / 4 | 152 / 200 | yes |
| `shiftrows_offsets_swapped` ((0,1,2,3) → (0,1,3,2)) | 4 / 4 | 200 / 200 | yes |
| `rcon_off_by_one` (Rcon exponent shifted by one) | 4 / 4 | 200 / 200 | yes |

**Observation worth carrying forward (recorded, not interpreted):** the sparse
S-box fault escaped 2 of the 4 known-answer vectors and 48 of 200 random pairs.
A single block touches only ~160 of 256 S-box entries, so a fixed KAT can miss
a sparse table fault outright. **Randomized differential agreement is the
load-bearing check in this receipt; the recalled vectors are a weaker
supplement.** Any future harness change should be re-validated by check 4, not
by the four vectors.

**A real defect this control caught, recorded per AGENTS.md rule 8.** The first
implementation of the mutation control scored `rejected_at_import` as a
detection. Two of three mutants were then "detected" by an
`AttributeError: 'NoneType' object has no attribute '__dict__'` — which is not
a detection at all but a loader bug in the driver (a module combining
`@dataclass` with `from __future__ import annotations` must be registered in
`sys.modules` before `exec_module`). That would have been a green control that
proved nothing. The driver now (a) registers the module before executing it,
(b) counts only an `AssertionError` from the module's own internal consistency
check as a genuine self-check detection, and (c) records any other import
exception as `driver_import_error` with `detected: false`, scoring it as a
failure — never as evidence the fault was caught (AGENTS.md rule 5). All three
mutants now import cleanly and are caught by the comparison machinery itself.
Superseded intermediate receipts from before this fix were scratch files and
are not part of the artifact set; this paragraph is their record.

## 5. Exact commands and real output

Environment probe (top-level session, before implementation):

```console
$ git rev-parse HEAD
1e1c77829de76c3f5aaad393c69281577976f0f6
$ python3 -VV
Python 3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]
$ python3 -c "import Crypto; print(Crypto.__version__)"
3.23.0
$ openssl version
OpenSSL 3.0.13 30 Jan 2024 (Library: OpenSSL 3.0.13 30 Jan 2024)
$ gcc --version | head -1
gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
$ nproc
4
$ free -g | head -2
               total        used        free      shared  buff/cache   available
Mem:              15           0          14           0           0          15
```

openssl single-block ECB probe (establishes the reference invocation used
throughout; note `-nopad`, and that `xxd` is absent on this host so hex is
printed with python):

```console
$ printf '\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb\xcc\xdd\xee\xff' > pt.bin
$ openssl enc -aes-128-ecb -K 000102030405060708090a0b0c0d0e0f -nopad -in pt.bin -out ct.bin
$ python3 -c "print(open('ct.bin','rb').read().hex())"
69c4e0d86a7b0430d8cdb78070b4c55a
$ openssl enc -d -aes-128-ecb -K 000102030405060708090a0b0c0d0e0f -nopad -in ct.bin -out pt2.bin
$ python3 -c "print(open('pt2.bin','rb').read().hex())"
00112233445566778899aabbccddeeff
```

Module self-report:

```console
$ python3 aes_reduced.py
{
  "module_sha256": "2c76f3e5db83ec2500ce1010a392a135869d8b9dd1a534af817e06f15babb447",
  "sbox_sha256": "c2d8e5eed6cbebd8625fc18f81486a7733c04f9b0129ffbe974c68b90308b4f2",
  "aes128_full_round_demo_ct": "69c4e0d86a7b0430d8cdb78070b4c55a",
  "config": { "key_bits": 128, "rounds": 10, "full_rounds": 10,
              "final_mix_columns": false,
              "initial_addroundkey_counted_as_round": false,
              "is_fips197": true, ... }
}
```

Throughput measurement (real, used to sanity-check that the reported wall clock
is consistent with the work claimed — 12 000 pure-Python blocks at 0.69 ms each
≈ 8 s, plus 96 openssl subprocesses, versus 16.3 s reported):

```console
$ python3 -c "...1000 encrypt_block calls..."
1000 blocks in 0.69s
real	0m0.804s
```

The two verification runs (the second produces the archived receipt; the first
exists to supply `--prior-digest` for the determinism check):

```console
$ export AES_REDUCED_DIR=/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602
$ python3 check_vectors.py --out receiptA.json --repo /home/user/crypto-autoresearcher --tmpdir "$PWD/_rA"
{
  "overall_verdict": "pass",
  "verdicts": {
    "component_derivations": "pass",
    "known_answer_vectors": "pass",
    "multiblock_consistency": "pass",
    "randomized_vs_pycryptodome": "pass",
    "randomized_vs_openssl": "pass",
    "reduced_round_convention": "pass",
    "null_object_controls": "pass",
    "detection_power_mutation_control": "pass"
  },
  "results_digest_sha256": "f78e55e4b7d6df30f41ce4aa613f8621ca9ecdd21f9ab9f3027b87c96dacaf1a",
  "wall_clock_seconds": 16.581,
  "openssl_error_count": 0,
  "out": "receiptA.json"
}
A_EXIT=0

$ python3 check_vectors.py --out receiptB.json --repo /home/user/crypto-autoresearcher \
    --prior-digest f78e55e4b7d6df30f41ce4aa613f8621ca9ecdd21f9ab9f3027b87c96dacaf1a --tmpdir "$PWD/_rB"
{
  "overall_verdict": "pass",
  "verdicts": {
    "component_derivations": "pass",
    "known_answer_vectors": "pass",
    "multiblock_consistency": "pass",
    "randomized_vs_pycryptodome": "pass",
    "randomized_vs_openssl": "pass",
    "reduced_round_convention": "pass",
    "null_object_controls": "pass",
    "detection_power_mutation_control": "pass",
    "determinism_rerun_digest_matches": "pass"
  },
  "results_digest_sha256": "f78e55e4b7d6df30f41ce4aa613f8621ca9ecdd21f9ab9f3027b87c96dacaf1a",
  "wall_clock_seconds": 16.332,
  "openssl_error_count": 0,
  "out": "receiptB.json"
}
B_EXIT=0

$ python3 -c "<compare receiptA/receiptB modulo timestamps, command timings, verdicts>"
receipts identical modulo timing/commands/verdicts: True
```

Mutation control, run separately as a whole-harness red test before it was
folded into the driver (the archived `aes_reduced.py` was never modified; a
mutated **copy** was tested):

```console
$ AES_REDUCED_DIR=.../mutant python3 check_vectors.py --out mutant_receipt.json ...
{
  "overall_verdict": "FAIL",
  "verdicts": {
    "component_derivations": "pass",
    "known_answer_vectors": "FAIL",
    "multiblock_consistency": "pass",
    "randomized_vs_pycryptodome": "FAIL",
    "randomized_vs_openssl": "FAIL",
    "reduced_round_convention": "FAIL",
    "null_object_controls": "pass"
  },
  ...
}
EXIT=1
```

The harness exits non-zero and reports FAIL on a wrong AES. (`multiblock_consistency`
passing for that mutant is the sparse-fault effect quantified in §4.3, not a
bug: the 8 blocks of that fixed vector are identical and never index the two
swapped S-box entries.)

`vector_check_receipt.json → commands` holds all **112** subprocess invocations
of the archived run with their exit statuses, stderr, and wall times. Every
openssl exit status is 0; `openssl_error_count` is 0.

## 6. Determinism and seeds

All randomness comes from `random.Random(seed)` (Mersenne Twister) with these
fixed seeds and nothing else — no system entropy, no time, no address hashing
is consumed on any computation path:

| purpose | seed |
|---|---|
| master / task | `20260731602` |
| randomized differential vs pycryptodome | `20260731602001` |
| randomized differential vs openssl | `20260731602002` |
| null-object controls | `20260731602003` |
| convention checks | `20260731602004` |
| detection-power mutants | `20260731602005` |
| control component seeds | random S-box `11`, `12`; random MixColumns `99`, `100` |

`results_digest_sha256` is SHA-256 over every ciphertext and plaintext produced
during a run, in execution order. Two independent runs both produced
`f78e55e4b7d6df30f41ce4aa613f8621ca9ecdd21f9ab9f3027b87c96dacaf1a`, and the
receipts are byte-identical apart from timestamps, per-command wall times, and
the extra determinism verdict. Re-running reproduces byte-identical results.

## 7. Limitations and things that could NOT be verified

These are recorded in `vector_check_receipt.json → checks_not_run` as well.

1. **The r < Nr behaviour has no external reference.** This is the most
   important limitation. No available tool implements reduced-round AES, so
   the reduced-round path **cannot** be cross-validated against pycryptodome or
   openssl. It is pinned only by (a) exact three-way agreement at r = Nr, which
   exercises the same round-loop code, and (b) the internal convention checks
   of §4.2. A validator should treat the reduced-round semantics as *documented
   and self-consistent*, not as *externally corroborated*.
2. **NIST CAVP / AESAVS response files were not used.** Not present locally and
   csrc.nist.gov is unreachable. NOT RUN.
3. **The FIPS-197 document itself was never read.** The four "expected" values
   are recalled, tagged `recalled_from_memory_unverified`, and are not the
   authority (§4.1). This task pins the *implementation*, not the *standard*.
4. **Reference independence is real but bounded.** `aes_reduced.py`,
   pycryptodome and openssl are three genuinely distinct code paths — the
   module imports only the standard library and never calls either reference —
   so the agreement is not a tautology. But both references were validated by
   their own authors against the same published standard, so they are not
   independent of a hypothetical error *in the standard as I recall it*. This
   caveat is stated verbatim in the receipt's `independence_statement`.
5. **No AES-NI / C cross-check.** gcc 13.3.0 with `-maes` is available but no C
   implementation is part of this deliverable. Not attempted.
6. **ECB only.** CBC/CTR/GCM are not implemented and not claimed; reduced-round
   cryptanalysis operates on the block permutation directly.
7. **Performance.** `aes_reduced.py` is pure Python at ~0.69 ms/block (≈1450
   blocks/s single-core, measured). A campaign step needing ≫10^7 blocks will
   need a faster path; this instrument is built for correctness, not speed. No
   estimate of any attack's feasibility is offered here.
8. **The four recalled vectors happened to agree.** That corroborates the
   recollection but is not a citation and must not be cited as one downstream.

## 8. Inference / model provenance

| field | value |
|---|---|
| `requested_policy` | `executor-implementation` (from `ledger/handoffs/TASK-20260731-602.yaml` → `inference.policy`) |
| `reasoning_effort` | `null` (policy default) |
| `fallback_allowed` (handoff) | `false` |
| `degraded_allowed` (handoff) | `false` |
| resolved model | `claude-opus-5` (Claude Opus 5), running as the `executor` subagent under the Claude Code harness |
| `fallback_used` | **`true`** |
| `model_verified` | `false` — `python3 -m orchestration.adapter doctor --probe` was not run in this session |

Per CLAUDE.md "Model policy note": under this Claude Code harness the subagent
frontmatter cannot resolve `orchestration/model-policies.yaml` identifiers (all
subagents run `model: inherit`), so the requested `executor-implementation`
policy alias could not be resolved to its intended backend and the harness's
inherited Claude model served the task. This is recorded as `fallback_used:
true` rather than silently substituted. Note that the handoff sets
`fallback_allowed: false`; the substitution is structural to this harness, not
a choice made here, and the Coordinator should decide whether it needs an
`inference_amendment`. Flagging it rather than resolving it is deliberate —
this record does not have the authority to waive a handoff constraint.

## 9. Verification driver source (`check_vectors.py`, verbatim)

sha256 `675ff4d568c03f6b12aa5d8931c6185ec7c5b08344ef826616fd9580d4c84a6d`.
Extract to `check_vectors.py` anywhere, set `AES_REDUCED_DIR` to this task
directory, and run the commands in §5 to reproduce.

```python
#!/usr/bin/env python3
"""check_vectors.py -- TASK-20260731-602 verification driver.

Checks aes_reduced.py against TWO independent reference implementations
(pycryptodome and the openssl CLI) and emits vector_check_receipt.json.

It records what was ACTUALLY computed. A failing check is written as failing.

Usage:
  python3 check_vectors.py --out receipt.json [--prior-digest HEX]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
import time
from datetime import datetime, timezone

# The module under test is located via AES_REDUCED_DIR (default: this file's
# directory). This lets the driver be executed from a scratch directory while
# testing the archived aes_reduced.py byte-for-byte.
MODULE_DIR = os.environ.get("AES_REDUCED_DIR", os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, MODULE_DIR)
import aes_reduced as AR  # noqa: E402

SEED_MASTER = 20260731602
SEED_RANDOM_PYCRYPTO = 20260731602001
SEED_RANDOM_OPENSSL = 20260731602002
SEED_CONTROLS = 20260731602003
SEED_ROUNDTRIP = 20260731602004
SEED_DETECTION = 20260731602005

N_PYCRYPTO_PER_KEYSIZE = 2000      # random (key, plaintext) pairs per key size
N_OPENSSL_KEYS_PER_KEYSIZE = 16    # distinct random keys per key size
N_OPENSSL_BLOCKS_PER_KEY = 32      # blocks per key (one openssl call per key/dir)

DIGEST = hashlib.sha256()
COMMANDS = []


def feed(*parts):
    for p in parts:
        DIGEST.update(p if isinstance(p, bytes) else str(p).encode())
        DIGEST.update(b"|")


def run(cmd, **kw):
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, **kw)
    COMMANDS.append({
        "command": cmd if isinstance(cmd, str) else " ".join(cmd),
        "exit_status": p.returncode,
        "stdout_bytes": len(p.stdout),
        "stderr": p.stderr.decode(errors="replace")[:2000],
        "wall_seconds": round(time.time() - t0, 4),
    })
    return p


# --------------------------------------------------------------------------
# References
# --------------------------------------------------------------------------

def pycrypto_encrypt(key: bytes, data: bytes) -> bytes:
    from Crypto.Cipher import AES as PCAES
    return PCAES.new(key, PCAES.MODE_ECB).encrypt(data)


def pycrypto_decrypt(key: bytes, data: bytes) -> bytes:
    from Crypto.Cipher import AES as PCAES
    return PCAES.new(key, PCAES.MODE_ECB).decrypt(data)


OPENSSL_ERRORS = []


def openssl_ecb(key: bytes, data: bytes, decrypt: bool, tmpdir: str, tag: str):
    """Returns (output_hex_or_None, exit_status, stderr)."""
    alg = {16: "aes-128-ecb", 24: "aes-192-ecb", 32: "aes-256-ecb"}[len(key)]
    fin = os.path.join(tmpdir, f"in_{tag}.bin")
    fout = os.path.join(tmpdir, f"out_{tag}.bin")
    with open(fin, "wb") as fh:
        fh.write(data)
    cmd = ["openssl", "enc"]
    if decrypt:
        cmd.append("-d")
    cmd += [f"-{alg}", "-K", key.hex(), "-nopad", "-in", fin, "-out", fout]
    p = run(cmd)
    if p.returncode != 0:
        OPENSSL_ERRORS.append({"tag": tag, "exit": p.returncode,
                               "stderr": p.stderr.decode(errors="replace")})
        return None, p.returncode, p.stderr.decode(errors="replace")
    with open(fout, "rb") as fh:
        out = fh.read()
    return out.hex(), 0, ""


# --------------------------------------------------------------------------
# Recalled FIPS-197 known-answer vectors.
#
# HONESTY NOTE: no primary source is reachable from this environment. The
# `expected_ct` values below are RECALLED FROM MEMORY and are recorded with
# recall_status = "recalled_from_memory_unverified". They are NOT the
# authority for this task. The authority is agreement between three
# independent implementations (aes_reduced.py, pycryptodome, openssl). If a
# recalled value were to disagree with all three, that is a memory error in
# this record, not an implementation failure, and the receipt says so.
# --------------------------------------------------------------------------

RECALLED_VECTORS = [
    {
        "id": "FIPS197-AppB-AES128",
        "source_claim": "FIPS-197 Appendix B (Cipher Example), recalled from memory",
        "key_bits": 128,
        "key": "2b7e151628aed2a6abf7158809cf4f3c",
        "pt": "3243f6a8885a308d313198a2e0370734",
        "expected_ct": "3925841d02dc09fbdc118597196a0b32",
    },
    {
        "id": "FIPS197-AppC1-AES128",
        "source_claim": "FIPS-197 Appendix C.1 (AES-128), recalled from memory",
        "key_bits": 128,
        "key": "000102030405060708090a0b0c0d0e0f",
        "pt": "00112233445566778899aabbccddeeff",
        "expected_ct": "69c4e0d86a7b0430d8cdb78070b4c55a",
    },
    {
        "id": "FIPS197-AppC2-AES192",
        "source_claim": "FIPS-197 Appendix C.2 (AES-192), recalled from memory",
        "key_bits": 192,
        "key": "000102030405060708090a0b0c0d0e0f1011121314151617",
        "pt": "00112233445566778899aabbccddeeff",
        "expected_ct": "dda97ca4864cdfe06eaf70a0ec0d7191",
    },
    {
        "id": "FIPS197-AppC3-AES256",
        "source_claim": "FIPS-197 Appendix C.3 (AES-256), recalled from memory",
        "key_bits": 256,
        "key": "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f",
        "pt": "00112233445566778899aabbccddeeff",
        "expected_ct": "8ea2b7ca516745bfeafc49904b496089",
    },
]


def check_known_answer_vectors(tmpdir):
    results = []
    for v in RECALLED_VECTORS:
        key = bytes.fromhex(v["key"])
        pt = bytes.fromhex(v["pt"])
        ct_expect = v["expected_ct"]

        mine_ct = AR.AES(key).encrypt_block(pt).hex()
        pyc_ct = pycrypto_encrypt(key, pt).hex()
        ossl_ct, ossl_rc, ossl_err = openssl_ecb(key, pt, False, tmpdir, v["id"] + "_e")
        feed(mine_ct, pyc_ct, ossl_ct)

        ct_bytes = bytes.fromhex(mine_ct)
        mine_pt = AR.AES(key).decrypt_block(ct_bytes).hex()
        pyc_pt = pycrypto_decrypt(key, ct_bytes).hex()
        ossl_pt, ossl_drc, ossl_derr = openssl_ecb(key, ct_bytes, True, tmpdir, v["id"] + "_d")
        feed(mine_pt, pyc_pt, ossl_pt)

        comps = {
            "encrypt.aes_reduced_vs_pycryptodome": mine_ct == pyc_ct,
            "encrypt.aes_reduced_vs_openssl": (ossl_ct is not None and mine_ct == ossl_ct),
            "encrypt.pycryptodome_vs_openssl": (ossl_ct is not None and pyc_ct == ossl_ct),
            "encrypt.aes_reduced_vs_recalled_expected": mine_ct == ct_expect,
            "decrypt.aes_reduced_vs_pycryptodome": mine_pt == pyc_pt,
            "decrypt.aes_reduced_vs_openssl": (ossl_pt is not None and mine_pt == ossl_pt),
            "decrypt.roundtrip_recovers_plaintext": mine_pt == pt.hex(),
        }
        results.append({
            "vector_id": v["id"],
            "source_claim": v["source_claim"],
            "recall_status": "recalled_from_memory_unverified",
            "key_bits": v["key_bits"],
            "key_hex": v["key"],
            "plaintext_hex": v["pt"],
            "expected_ciphertext_hex_recalled": ct_expect,
            "aes_reduced_ciphertext_hex": mine_ct,
            "pycryptodome_ciphertext_hex": pyc_ct,
            "openssl_ciphertext_hex": ossl_ct,
            "openssl_encrypt_exit_status": ossl_rc,
            "openssl_encrypt_stderr": ossl_err[:500],
            "aes_reduced_decrypted_hex": mine_pt,
            "pycryptodome_decrypted_hex": pyc_pt,
            "openssl_decrypted_hex": ossl_pt,
            "openssl_decrypt_exit_status": ossl_drc,
            "openssl_decrypt_stderr": ossl_derr[:500],
            "comparisons": comps,
            "verdict": "pass" if all(comps.values()) else "FAIL",
        })
    return results


def check_random_vs_pycryptodome():
    rng = random.Random(SEED_RANDOM_PYCRYPTO)
    out = []
    for kb, klen in ((128, 16), (192, 24), (256, 32)):
        enc_ok = enc_bad = dec_ok = dec_bad = 0
        first_mismatch = None
        for _ in range(N_PYCRYPTO_PER_KEYSIZE):
            key = bytes(rng.randrange(256) for _ in range(klen))
            pt = bytes(rng.randrange(256) for _ in range(16))
            a = AR.AES(key)
            mine = a.encrypt_block(pt)
            ref = pycrypto_encrypt(key, pt)
            if mine == ref:
                enc_ok += 1
            else:
                enc_bad += 1
                if first_mismatch is None:
                    first_mismatch = {"dir": "encrypt", "key": key.hex(), "in": pt.hex(),
                                      "mine": mine.hex(), "ref": ref.hex()}
            ct = pt
            mined = a.decrypt_block(ct)
            refd = pycrypto_decrypt(key, ct)
            if mined == refd:
                dec_ok += 1
            else:
                dec_bad += 1
                if first_mismatch is None:
                    first_mismatch = {"dir": "decrypt", "key": key.hex(), "in": ct.hex(),
                                      "mine": mined.hex(), "ref": refd.hex()}
            feed(mine, mined)
        out.append({
            "key_bits": kb,
            "pairs_compared": N_PYCRYPTO_PER_KEYSIZE,
            "encrypt_agreements": enc_ok, "encrypt_mismatches": enc_bad,
            "decrypt_agreements": dec_ok, "decrypt_mismatches": dec_bad,
            "first_mismatch": first_mismatch,
            "verdict": "pass" if (enc_bad == 0 and dec_bad == 0) else "FAIL",
        })
    return out


def check_random_vs_openssl(tmpdir):
    rng = random.Random(SEED_RANDOM_OPENSSL)
    out = []
    for kb, klen in ((128, 16), (192, 24), (256, 32)):
        enc_ok = enc_bad = dec_ok = dec_bad = 0
        blocks_e = blocks_d = 0
        first_mismatch = None
        errors = []
        for j in range(N_OPENSSL_KEYS_PER_KEYSIZE):
            key = bytes(rng.randrange(256) for _ in range(klen))
            data = bytes(rng.randrange(256)
                         for _ in range(16 * N_OPENSSL_BLOCKS_PER_KEY))
            a = AR.AES(key)
            mine = a.encrypt_ecb(data).hex()
            ref, rc, err = openssl_ecb(key, data, False, tmpdir, f"rnd{kb}_{j}_e")
            feed(mine, ref)
            if ref is None:
                errors.append({"dir": "encrypt", "exit": rc, "stderr": err[:300]})
            elif mine == ref:
                enc_ok += 1
                blocks_e += N_OPENSSL_BLOCKS_PER_KEY
            else:
                enc_bad += 1
                if first_mismatch is None:
                    first_mismatch = {"dir": "encrypt", "key": key.hex(),
                                      "in": data.hex(), "mine": mine, "ref": ref}
            mined = a.decrypt_ecb(data).hex()
            refd, rcd, errd = openssl_ecb(key, data, True, tmpdir, f"rnd{kb}_{j}_d")
            feed(mined, refd)
            if refd is None:
                errors.append({"dir": "decrypt", "exit": rcd, "stderr": errd[:300]})
            elif mined == refd:
                dec_ok += 1
                blocks_d += N_OPENSSL_BLOCKS_PER_KEY
            else:
                dec_bad += 1
                if first_mismatch is None:
                    first_mismatch = {"dir": "decrypt", "key": key.hex(),
                                      "in": data.hex(), "mine": mined, "ref": refd}
        out.append({
            "key_bits": kb,
            "distinct_keys": N_OPENSSL_KEYS_PER_KEYSIZE,
            "blocks_per_key": N_OPENSSL_BLOCKS_PER_KEY,
            "encrypt_calls_agreeing": enc_ok, "encrypt_calls_mismatching": enc_bad,
            "decrypt_calls_agreeing": dec_ok, "decrypt_calls_mismatching": dec_bad,
            "blocks_agreeing_encrypt": blocks_e, "blocks_agreeing_decrypt": blocks_d,
            "openssl_errors": errors,
            "first_mismatch": first_mismatch,
            "verdict": "pass" if (enc_bad == 0 and dec_bad == 0 and not errors) else "FAIL",
        })
    return out


def check_component_derivations():
    sbox, inv = AR.aes_sbox(), AR.aes_inv_sbox()
    checks = {
        "sbox_is_bijection": sorted(sbox) == list(range(256)),
        "sbox_inverse_consistent": all(inv[sbox[x]] == x for x in range(256)),
        "sbox_len_256": len(sbox) == 256,
        "mix_times_invmix_is_identity": AR.mat_mul(AR.AES_MIX, AR.AES_INV_MIX) == AR.IDENTITY_MIX,
        "gf_inverse_correct": all(AR.GF.mul(x, AR.GF.inv(x)) == 1 for x in range(1, 256)),
        "gf_inv_zero_is_zero": AR.GF.inv(0) == 0,
    }
    feed(hashlib.sha256(bytes(sbox)).hexdigest())
    return {"checks": checks,
            "sbox_sha256": hashlib.sha256(bytes(sbox)).hexdigest(),
            "verdict": "pass" if all(checks.values()) else "FAIL"}


def check_reduced_round_convention():
    """Convention (C1)(C2)(C3) checks -- these define the cipher for the campaign."""
    rng = random.Random(SEED_ROUNDTRIP)
    checks = {}
    details = []
    ok = True

    for kb, klen, nr in ((128, 16, 10), (192, 24, 12), (256, 32, 14)):
        key = bytes(rng.randrange(256) for _ in range(klen))
        pt = bytes(rng.randrange(256) for _ in range(16))

        # C1: at full rounds, default convention == FIPS-197 (== pycryptodome).
        full_default = AR.AES(key, rounds=nr).encrypt_block(pt)
        ref = pycrypto_encrypt(key, pt)
        c1 = (full_default == ref)
        # the OTHER variant must differ (it is a different cipher; recorded, not judged)
        full_withmc = AR.AES(key, rounds=nr, final_mix_columns=True).encrypt_block(pt)
        c1b = (full_withmc != ref)
        # default with rounds=None == rounds=nr
        c1c = (AR.AES(key).encrypt_block(pt) == full_default)

        # C2: initial AddRoundKey not counted -- rounds=0 is pure whitening.
        c2 = (AR.AES(key, rounds=0).encrypt_block(pt) == bytes(a ^ b for a, b in zip(pt, key[:16])))

        # C3: reduced-round round keys are a prefix of the full schedule.
        full_rk = AR.key_expansion(key, nr + 1)
        c3 = all(AR.AES(key, rounds=r).round_keys == full_rk[:r + 1] for r in range(0, nr + 1))

        # round-count monotonic distinctness: r and r+1 give different outputs
        cts = [AR.AES(key, rounds=r).encrypt_block(pt).hex() for r in range(0, nr + 1)]
        c4 = len(set(cts)) == len(cts)

        # invertibility at every reduced round count, both conventions
        c5 = True
        for r in range(0, nr + 1):
            for fmc in (False, True):
                a = AR.AES(key, rounds=r, final_mix_columns=fmc)
                if a.decrypt_block(a.encrypt_block(pt)) != pt:
                    c5 = False

        # partial encryption composes to the full encryption at every split
        c6 = True
        a = AR.AES(key, rounds=nr)
        lvl0 = a.whiten(pt)
        for split in range(0, nr + 1):
            mid = a.encrypt_partial(lvl0, 0, split)
            if a.encrypt_partial(mid, split, nr) != full_default:
                c6 = False
            if a.decrypt_partial(mid, split, 0) != lvl0:
                c6 = False

        # trace labels agree with the partial-encryption level indexing
        tr = dict(a.trace(pt))
        c7 = (tr["ark0"] == lvl0
              and all(tr[f"r{i}.ark"] == a.encrypt_partial(lvl0, 0, i) for i in range(1, nr + 1))
              and tr[f"r{nr}.ark"] == full_default)
        # final round has no .mix label under the default convention
        c8 = (f"r{nr}.mix" not in tr) and (f"r{nr-1}.mix" in tr)
        # ... and does have one when final_mix_columns=True
        tr2 = dict(AR.AES(key, rounds=nr, final_mix_columns=True).trace(pt))
        c9 = f"r{nr}.mix" in tr2

        # is_fips197 flag correctness
        c10 = (AR.AES(key, rounds=nr).is_fips197
               and not AR.AES(key, rounds=nr - 1).is_fips197
               and not AR.AES(key, rounds=nr, final_mix_columns=True).is_fips197)

        row = {
            "key_bits": kb, "full_rounds": nr, "key_hex": key.hex(), "pt_hex": pt.hex(),
            "C1_full_default_equals_fips197_reference": c1,
            "C1b_final_mixcolumns_variant_differs_from_aes": c1b,
            "C1c_rounds_None_equals_full_rounds": c1c,
            "C2_rounds0_is_pure_whitening": c2,
            "C3_reduced_roundkeys_are_prefix_of_full_schedule": c3,
            "C4_distinct_ciphertext_per_round_count": c4,
            "C5_invertible_at_every_round_count_both_conventions": c5,
            "C6_partial_encryption_composes": c6,
            "C7_trace_labels_match_level_indexing": c7,
            "C8_final_round_omits_mixcolumns_by_default": c8,
            "C9_final_mixcolumns_true_keeps_it": c9,
            "C10_is_fips197_flag_correct": c10,
            "ciphertext_by_round_count": cts,
        }
        details.append(row)
        for k, v in row.items():
            if isinstance(v, bool):
                checks[f"{kb}.{k}"] = v
                ok = ok and v
        feed(*cts)
    return {"per_key_size": details, "verdict": "pass" if ok else "FAIL",
            "flat_checks": checks}


def check_null_object_controls():
    rng = random.Random(SEED_CONTROLS)
    key = bytes(rng.randrange(256) for _ in range(16))
    pt = bytes(rng.randrange(256) for _ in range(16))
    base = AR.AES(key, rounds=4)
    base_ct = base.encrypt_block(pt)

    controls = {
        "random_sbox_seed_11": base.with_random_sbox(11),
        "random_sbox_seed_11_incl_keysched": base.with_random_sbox(11, also_key_schedule=True),
        "random_sbox_seed_12": base.with_random_sbox(12),
        "identity_sbox": base.with_identity_sbox(),
        "identity_mixcolumns": base.with_identity_mixcolumns(),
        "random_mixcolumns_seed_99": base.with_random_mixcolumns(99),
        "identity_shiftrows": base.with_identity_shiftrows(),
    }
    rows = []
    ok = True
    for name, c in controls.items():
        ct = c.encrypt_block(pt)
        inv_ok = (c.decrypt_block(ct) == pt)
        differs = (ct != base_ct)
        not_fips = not c.is_fips197
        # reproducibility from the recorded seed: rebuilding gives the same output
        rows.append({
            "control": name,
            "ciphertext_hex": ct.hex(),
            "invertible": inv_ok,
            "differs_from_aes": differs,
            "is_fips197_flag_false": not_fips,
            "provenance": c.provenance,
            "component_fingerprint": c.components.describe(),
        })
        ok = ok and inv_ok and differs and not_fips
        feed(ct)

    # seed reproducibility and seed sensitivity
    same_seed = (base.with_random_sbox(11).encrypt_block(pt)
                 == base.with_random_sbox(11).encrypt_block(pt))
    diff_seed = (base.with_random_sbox(11).encrypt_block(pt)
                 != base.with_random_sbox(12).encrypt_block(pt))
    mix_same = (base.with_random_mixcolumns(99).encrypt_block(pt)
                == base.with_random_mixcolumns(99).encrypt_block(pt))
    mix_diff = (base.with_random_mixcolumns(99).encrypt_block(pt)
                != base.with_random_mixcolumns(100).encrypt_block(pt))
    ok = ok and same_seed and diff_seed and mix_same and mix_diff
    return {
        "base": {"key_hex": key.hex(), "pt_hex": pt.hex(), "rounds": 4,
                 "ciphertext_hex": base_ct.hex()},
        "controls": rows,
        "seed_reproducible_sbox": same_seed,
        "seed_sensitive_sbox": diff_seed,
        "seed_reproducible_mix": mix_same,
        "seed_sensitive_mix": mix_diff,
        "verdict": "pass" if ok else "FAIL",
    }


def check_detection_power(tmpdir):
    """Negative control ON THE INSTRUMENT ITSELF.

    docs/inventor-protocol.md requires a null object of the same shape before a
    signal is believed. Applied here: a green cross-implementation receipt is
    only meaningful if the SAME comparison machinery turns red on a knowingly
    wrong AES. Three single-fault mutants of aes_reduced.py are built, imported
    from disk as independent modules, and pushed through the same comparisons.
    Each must be detected. A mutant that survives is reported, not hidden.
    """
    import importlib.util

    with open(os.path.join(MODULE_DIR, "aes_reduced.py")) as fh:
        src = fh.read()

    anchor = "    sbox = tuple(_affine(GF.inv(x)) for x in range(256))"
    assert anchor in src, "mutation anchor not found"
    mutants = {
        "sbox_transpose_0x53_0x54": src.replace(anchor,
            "    sbox = list(_affine(GF.inv(x)) for x in range(256))\n"
            "    sbox[0x53], sbox[0x54] = sbox[0x54], sbox[0x53]\n"
            "    sbox = tuple(sbox)"),
        "shiftrows_offsets_swapped": src.replace(
            "    shift_offsets: Tuple[int, int, int, int] = (0, 1, 2, 3)",
            "    shift_offsets: Tuple[int, int, int, int] = (0, 1, 3, 2)"),
        "rcon_off_by_one": src.replace(
            "    for _ in range(i - 1):\n        v = GF.mul(v, 0x02)",
            "    for _ in range(i):\n        v = GF.mul(v, 0x02)"),
    }

    rows = []
    all_detected = True
    for name, msrc in mutants.items():
        if msrc == src:
            rows.append({"mutant": name, "status": "NOT_APPLIED",
                         "reason": "mutation anchor text not found; mutant identical to original",
                         "detected": False})
            all_detected = False
            continue
        path = os.path.join(tmpdir, f"mutant_{name}.py")
        with open(path, "w") as fh:
            fh.write(msrc)
        modname = f"mutant_{name}"
        spec = importlib.util.spec_from_file_location(modname, path)
        mod = importlib.util.module_from_spec(spec)
        # Register before exec: a module using @dataclass together with
        # `from __future__ import annotations` fails to import otherwise. That
        # failure is a LOADER bug, not a detection, and must not be scored as one.
        sys.modules[modname] = mod
        try:
            spec.loader.exec_module(mod)
        except AssertionError as exc:
            # The module's own internal consistency assertion caught the fault.
            # This is a genuine detection, by the implementation's self-check.
            rows.append({"mutant": name, "status": "rejected_by_module_self_check",
                         "detection_mechanism": "internal assertion in aes_reduced.py",
                         "detail": f"AssertionError: {exc}", "detected": True})
            continue
        except Exception as exc:
            # Anything else is an infrastructure failure of THIS driver.
            # Recorded as a failure, never as a detection (AGENTS.md rule 5).
            rows.append({"mutant": name, "status": "driver_import_error",
                         "detection_mechanism": None,
                         "detail": f"{type(exc).__name__}: {exc}",
                         "detected": False,
                         "note": "Loader failure in check_vectors.py, NOT evidence that "
                                 "the fault was detected. Scored as a failure."})
            all_detected = False
            continue
        finally:
            sys.modules.pop(modname, None)

        kav_detected = 0
        for v in RECALLED_VECTORS:
            key, pt = bytes.fromhex(v["key"]), bytes.fromhex(v["pt"])
            if mod.AES(key).encrypt_block(pt).hex() != v["expected_ct"]:
                kav_detected += 1

        rng = random.Random(SEED_DETECTION)
        rnd_total = rnd_detected = 0
        for _ in range(200):
            key = bytes(rng.randrange(256) for _ in range(16))
            pt = bytes(rng.randrange(256) for _ in range(16))
            rnd_total += 1
            if mod.AES(key).encrypt_block(pt) != pycrypto_encrypt(key, pt):
                rnd_detected += 1

        detected = (kav_detected > 0) or (rnd_detected > 0)
        all_detected = all_detected and detected
        rows.append({
            "mutant": name,
            "status": "applied",
            "known_answer_vectors_flagged": kav_detected,
            "known_answer_vectors_total": len(RECALLED_VECTORS),
            "random_pairs_flagged_vs_pycryptodome": rnd_detected,
            "random_pairs_total": rnd_total,
            "detection_mechanism": "cross-implementation comparison vs pycryptodome "
                                   "and recalled known-answer vectors",
            "detected": detected,
        })

    return {"mutants": rows,
            "note": "Mutants are transient files under the scratch tmpdir; the archived "
                    "aes_reduced.py is never modified. Observation worth carrying forward: "
                    "a fixed known-answer vector can MISS a sparse S-box fault (only ~160 "
                    "of 256 S-box entries are touched by one block), while randomized "
                    "differential testing catches it immediately. Randomized agreement is "
                    "the load-bearing check here, not the recalled vectors.",
            "verdict": "pass" if all_detected else "FAIL"}


def check_multiblock_consistency(tmpdir):
    """Multi-block ECB against both references, fixed (non-random) input."""
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    data = bytes(range(16)) * 8
    mine = AR.AES(key).encrypt_ecb(data).hex()
    pyc = pycrypto_encrypt(key, data).hex()
    ossl, rc, err = openssl_ecb(key, data, False, tmpdir, "multiblock")
    feed(mine, pyc, ossl)
    comps = {"vs_pycryptodome": mine == pyc,
             "vs_openssl": (ossl is not None and mine == ossl)}
    return {"blocks": len(data) // 16, "key_hex": key.hex(), "input_hex": data.hex(),
            "aes_reduced_hex": mine, "pycryptodome_hex": pyc, "openssl_hex": ossl,
            "openssl_exit_status": rc, "openssl_stderr": err[:300],
            "comparisons": comps,
            "verdict": "pass" if all(comps.values()) else "FAIL"}


# --------------------------------------------------------------------------

def tool_versions():
    v = {}
    p = run(["python3", "-c", "import sys; print(sys.version)"])
    v["python3"] = {"reported": p.stdout.decode().strip(), "exit_status": p.returncode,
                    "command": "python3 -c 'import sys; print(sys.version)'"}
    p = run(["python3", "-c", "import Crypto; print(Crypto.__version__)"])
    v["pycryptodome"] = {"reported": p.stdout.decode().strip(), "exit_status": p.returncode,
                         "command": "python3 -c 'import Crypto; print(Crypto.__version__)'"}
    p = run(["openssl", "version", "-a"])
    v["openssl"] = {"reported": p.stdout.decode().strip().splitlines()[0] if p.returncode == 0 else None,
                    "full": p.stdout.decode().strip(), "exit_status": p.returncode,
                    "command": "openssl version -a"}
    p = run(["gcc", "--version"])
    v["gcc"] = {"reported": p.stdout.decode().strip().splitlines()[0] if p.returncode == 0 else None,
                "exit_status": p.returncode, "command": "gcc --version",
                "used_in_this_task": False,
                "note": "recorded for the environment record only; no C code is part of this deliverable"}
    p = run(["openssl", "list", "-cipher-algorithms"])
    algs = p.stdout.decode(errors="replace")
    v["openssl_ecb_algorithms_present"] = {
        "aes-128-ecb": "AES-128-ECB" in algs.upper(),
        "aes-192-ecb": "AES-192-ECB" in algs.upper(),
        "aes-256-ecb": "AES-256-ECB" in algs.upper(),
        "exit_status": p.returncode,
        "command": "openssl list -cipher-algorithms",
    }
    return v


def git_state(repo_root):
    p = run(["git", "-C", repo_root, "rev-parse", "HEAD"])
    commit = p.stdout.decode().strip()
    p2 = run(["git", "-C", repo_root, "status", "--porcelain"])
    dirty = p2.stdout.decode()
    return {"commit": commit, "dirty": bool(dirty.strip()),
            "dirty_paths": [l[3:] for l in dirty.splitlines()][:50],
            "commands": ["git rev-parse HEAD", "git status --porcelain"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--prior-digest", default=None)
    ap.add_argument("--tmpdir", default=None)
    ap.add_argument("--repo", default=None, help="repository root for git state")
    args = ap.parse_args()

    here = MODULE_DIR
    repo_root = args.repo or (subprocess.run(
        ["git", "-C", here, "rev-parse", "--show-toplevel"],
        capture_output=True).stdout.decode().strip() or here)
    tmpdir = args.tmpdir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "_tmp_openssl")
    os.makedirs(tmpdir, exist_ok=True)

    t0 = time.time()
    started = datetime.now(timezone.utc).isoformat()

    sections = {}
    sections["component_derivations"] = check_component_derivations()
    sections["known_answer_vectors"] = check_known_answer_vectors(tmpdir)
    sections["multiblock_consistency"] = check_multiblock_consistency(tmpdir)
    sections["randomized_vs_pycryptodome"] = check_random_vs_pycryptodome()
    sections["randomized_vs_openssl"] = check_random_vs_openssl(tmpdir)
    sections["reduced_round_convention"] = check_reduced_round_convention()
    sections["null_object_controls"] = check_null_object_controls()
    sections["detection_power_mutation_control"] = check_detection_power(tmpdir)

    digest = DIGEST.hexdigest()

    kav = sections["known_answer_vectors"]
    verdicts = {
        "component_derivations": sections["component_derivations"]["verdict"],
        "known_answer_vectors": "pass" if all(v["verdict"] == "pass" for v in kav) else "FAIL",
        "multiblock_consistency": sections["multiblock_consistency"]["verdict"],
        "randomized_vs_pycryptodome": "pass" if all(
            v["verdict"] == "pass" for v in sections["randomized_vs_pycryptodome"]) else "FAIL",
        "randomized_vs_openssl": "pass" if all(
            v["verdict"] == "pass" for v in sections["randomized_vs_openssl"]) else "FAIL",
        "reduced_round_convention": sections["reduced_round_convention"]["verdict"],
        "null_object_controls": sections["null_object_controls"]["verdict"],
        "detection_power_mutation_control":
            sections["detection_power_mutation_control"]["verdict"],
    }
    if args.prior_digest is not None:
        verdicts["determinism_rerun_digest_matches"] = (
            "pass" if args.prior_digest == digest else "FAIL")

    with open(os.path.join(here, "aes_reduced.py"), "rb") as fh:
        src = fh.read()

    receipt = {
        "schema": "vector_check_receipt/v1",
        "task_id": "TASK-20260731-602",
        "goal_id": "GOAL-AES-001",
        "question_id": "RQ-AES-001",
        "batch_id": "BATCH-001",
        "purpose": "Pin the AES specification locally by demonstrating agreement between "
                   "aes_reduced.py and TWO independent reference implementations at full "
                   "rounds, and record the reduced-round convention this campaign adopts.",
        "claim_scope": {
            "asserts": "aes_reduced.py agrees with pycryptodome 3.23.0 and the openssl CLI "
                       "on the inputs actually tested, listed below.",
            "does_not_assert": "Nothing about AES security, full-round or reduced-round. "
                               "This is an instrument-verification record only.",
            "claim_tier": "not_applicable (instrument verification, no cryptanalytic claim)",
            "certificate_kind": "none",
            "certificate_rationale": "Pure measurement / verification run. Nothing is claimed "
                                     "to be solved or recovered (docs/claims-and-verification.md).",
        },
        "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "wall_clock_seconds": round(time.time() - t0, 3),
        "independence_statement":
            "aes_reduced.py imports only the Python standard library and never invokes "
            "pycryptodome or openssl. The S-box, inverse S-box, MixColumns inverse and Rcon "
            "are derived from the GF(2^8) definition inside aes_reduced.py, not transcribed. "
            "pycryptodome (a C/assembly implementation via libtomcrypt-derived code) and the "
            "openssl CLI (OpenSSL's own EVP AES, AES-NI accelerated where available) are two "
            "further independent code paths. Three-way agreement is therefore not a tautology. "
            "CAVEAT recorded honestly: pycryptodome and openssl are independent implementations "
            "but both were validated by their authors against the same published standard; "
            "they are not statistically independent of a hypothetical error in the standard "
            "itself. This task pins the implementation, not the standard.",
        "reduced_round_convention": {
            "id": "GOAL-AES-001/BATCH-001 convention v1",
            "C1_final_round_drops_mixcolumns": True,
            "C2_initial_addroundkey_counted_as_round": False,
            "C3_key_schedule": "untruncated FIPS-197 expansion for the key length; the r-round "
                               "cipher uses round keys 0..r of that schedule; Rcon indices are "
                               "not renumbered",
            "alternative_available": "final_mix_columns=True keeps MixColumns in the final "
                                     "round; that variant is NOT FIPS-197 AES at r = Nr and "
                                     "is_fips197 reports False for it",
            "literature_convention_note": "UNVERIFIED-FROM-MEMORY. No primary source is "
                                          "reachable from this environment. Recollection is "
                                          "that reduced-round AES cryptanalysis conventionally "
                                          "uses C1+C2+C3. This has NOT been checked against any "
                                          "read document and must be re-stated as unverified in "
                                          "any downstream comparison.",
        },
        "seeds": {
            "master": SEED_MASTER,
            "randomized_vs_pycryptodome": SEED_RANDOM_PYCRYPTO,
            "randomized_vs_openssl": SEED_RANDOM_OPENSSL,
            "null_object_controls": SEED_CONTROLS,
            "reduced_round_convention": SEED_ROUNDTRIP,
            "detection_power_mutation_control": SEED_DETECTION,
            "rng": "python3 random.Random(seed), Mersenne Twister; "
                   "all randomness in this receipt comes from these seeds and nothing else",
            "control_component_seeds": {"random_sbox": [11, 12], "random_mixcolumns": [99, 100]},
        },
        "sample_sizes": {
            "pycryptodome_pairs_per_key_size": N_PYCRYPTO_PER_KEYSIZE,
            "pycryptodome_pairs_total": 3 * N_PYCRYPTO_PER_KEYSIZE,
            "pycryptodome_block_comparisons_total": 3 * N_PYCRYPTO_PER_KEYSIZE * 2,
            "openssl_keys_per_key_size": N_OPENSSL_KEYS_PER_KEYSIZE,
            "openssl_blocks_per_key": N_OPENSSL_BLOCKS_PER_KEY,
            "openssl_block_comparisons_total":
                3 * N_OPENSSL_KEYS_PER_KEYSIZE * N_OPENSSL_BLOCKS_PER_KEY * 2,
            "known_answer_vectors": len(RECALLED_VECTORS),
        },
        "environment": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python_implementation": platform.python_implementation(),
            "cpu_count": os.cpu_count(),
            "declared_envelope": "4 CPU cores, 15 GB RAM, no GPU, no sage",
        },
        "tool_versions": tool_versions(),
        "git": git_state(repo_root),
        "artifact_hashes": {
            "aes_reduced_py_path_tested": os.path.join(here, "aes_reduced.py"),
            "aes_reduced.py.sha256": hashlib.sha256(src).hexdigest(),
            "aes_reduced.py.bytes": len(src),
            "check_driver_sha256": hashlib.sha256(
                open(os.path.abspath(__file__), "rb").read()).hexdigest(),
            "check_driver_note": "The driver source is reproduced verbatim in run_record.md; "
                                 "the task's declared artifact list is exactly three files, so "
                                 "the driver is archived inside run_record.md rather than as a "
                                 "fourth file.",
        },
        "results_digest_sha256": digest,
        "results_digest_note": "SHA-256 over every ciphertext/plaintext produced by this run, "
                               "in execution order. Two runs of this driver must produce the "
                               "same digest; that comparison is recorded as "
                               "determinism_rerun_digest_matches when --prior-digest is given.",
        "prior_run_digest_sha256": args.prior_digest,
        "checks_not_run": [
            {"check": "NIST CAVP / AESAVS response-file validation",
             "reason": "The CAVP vector files are not present locally and csrc.nist.gov is "
                       "unreachable under this harness's network policy. NOT RUN."},
            {"check": "verification against the FIPS-197 document text",
             "reason": "The specification PDF is not reachable. The recalled Appendix B/C "
                       "vector values in this receipt are marked "
                       "recalled_from_memory_unverified and are NOT the authority; "
                       "three-way implementation agreement is."},
            {"check": "AES-NI C reference cross-check (gcc -maes)",
             "reason": "Not attempted. Out of the declared deliverable scope for this task "
                       "(three Python artifacts). gcc version recorded for environment only."},
            {"check": "reduced-round cross-check against an external reference",
             "reason": "No external tool implements reduced-round AES, so r < Nr behaviour "
                       "CANNOT be externally validated. It is pinned only by (a) exact "
                       "agreement at r = Nr and (b) the internal convention checks in the "
                       "reduced_round_convention section. This is a real limitation and is "
                       "stated as one."},
            {"check": "modes other than ECB (CBC/CTR/GCM)",
             "reason": "Out of scope: reduced-round cryptanalysis operates on the block "
                       "permutation directly. Not implemented, not claimed."},
        ],
        "commands": COMMANDS,
        "verdicts": verdicts,
        "overall_verdict": "pass" if all(v == "pass" for v in verdicts.values()) else "FAIL",
        "sections": sections,
    }

    with open(args.out, "w") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=False)
        fh.write("\n")

    print(json.dumps({"overall_verdict": receipt["overall_verdict"],
                      "verdicts": verdicts,
                      "results_digest_sha256": digest,
                      "wall_clock_seconds": receipt["wall_clock_seconds"],
                      "openssl_error_count": len(OPENSSL_ERRORS),
                      "out": args.out}, indent=2))
    return 0 if receipt["overall_verdict"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
```
